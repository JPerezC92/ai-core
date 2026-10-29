"""Pure identity guards for preflight evidence."""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlsplit

from verified_pr_cleanup_pkg.domain.models import PullRequest, RepositoryIdentity

GITHUB_HOST = "github.com"
GITHUB_SSH_USER = "git"
OID_PATTERN = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")
REMOTE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
GITHUB_OWNER_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
GITHUB_REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
SSH_ALIAS_HOST_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,252}$")
SCP_STYLE_REMOTE_PATTERN = re.compile(
    r"^(?P<user>[^:/@\\]+)@(?P<host>[^:/@\\]+):(?P<path>.+)$"
)


@dataclass(frozen=True)
class SshRemote:
    """One parsed SSH remote before any host-policy decision."""

    host: str
    user: str
    owner: str
    repository: str


def is_full_oid(value: str) -> bool:
    """Return True only for a full SHA-1 or SHA-256 object identifier."""
    return OID_PATTERN.fullmatch(value) is not None


def is_safe_remote_name(value: str) -> bool:
    """Reject option-like and ambiguous remote names."""
    return REMOTE_NAME_PATTERN.fullmatch(value) is not None and value not in {".", ".."} and ".." not in value


def is_safe_ssh_alias_host(value: str) -> bool:
    """Reject option-like, wildcard, or malformed SSH host aliases."""
    return SSH_ALIAS_HOST_PATTERN.fullmatch(value) is not None


def _repository_identity(owner: str, repository: str) -> RepositoryIdentity | None:
    """Validate one owner/repository pair and strip one trailing .git suffix."""
    if repository.endswith(".git"):
        repository = repository[:-4]
    if (
        GITHUB_OWNER_PATTERN.fullmatch(owner) is None
        or GITHUB_REPOSITORY_PATTERN.fullmatch(repository) is None
        or owner in {".", ".."}
        or repository in {".", ".."}
        or ".." in repository
    ):
        return None
    return RepositoryIdentity(owner=owner, name=repository)


def parse_ssh_remote(value: str) -> SshRemote | None:
    """Parse scp-style or ssh URL forms into host, user, owner, and repository."""
    scp_style = SCP_STYLE_REMOTE_PATTERN.fullmatch(value)
    if scp_style is not None:
        host = scp_style.group("host")
        if not is_safe_ssh_alias_host(host):
            return None
        path = scp_style.group("path")
        if any(marker in path for marker in (":", "?", "#")):
            return None
        owner, separator, repository = path.partition("/")
        if not separator:
            return None
        identity = _repository_identity(owner, repository)
        if identity is None:
            return None
        return SshRemote(host, scp_style.group("user"), identity.owner, identity.name)
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if parsed.scheme != "ssh":
        return None
    try:
        port = parsed.port
    except ValueError:
        return None
    host = parsed.hostname
    user = parsed.username
    if (
        host is None
        or user is None
        or not is_safe_ssh_alias_host(host)
        or port is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        return None
    segments = parsed.path.removeprefix("/").split("/")
    if len(segments) != 2:
        return None
    identity = _repository_identity(segments[0], segments[1])
    if identity is None:
        return None
    return SshRemote(host, user, identity.owner, identity.name)


def github_repository_from_url(value: str) -> RepositoryIdentity | None:
    """Map only exact github.com HTTPS/SSH remotes; SSH aliases need host resolution."""
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if parsed.scheme == "https":
        try:
            port = parsed.port
        except ValueError:
            return None
        if (
            parsed.hostname != GITHUB_HOST
            or port is not None
            or parsed.username is not None
            or parsed.password is not None
            or parsed.query
            or parsed.fragment
        ):
            return None
        segments = parsed.path.removeprefix("/").split("/")
        if len(segments) != 2:
            return None
        return _repository_identity(segments[0], segments[1])
    ssh_remote = parse_ssh_remote(value)
    if (
        ssh_remote is None
        or ssh_remote.host.casefold() != GITHUB_HOST
        or ssh_remote.user != GITHUB_SSH_USER
    ):
        return None
    return RepositoryIdentity(owner=ssh_remote.owner, name=ssh_remote.repository)


def pull_request_identity_error(
    pull_request: PullRequest,
    requested_number: int,
    repository: RepositoryIdentity,
    base_branch: str,
) -> str | None:
    """Return a canonical URL, repository, PR, branch, or merge-state discrepancy."""
    if pull_request.number != requested_number:
        return "GitHub returned a different pull-request number."
    if pull_request.state.upper() != "MERGED" or not pull_request.merged_at:
        return "The pull request is not verifiably MERGED."
    if not is_full_oid(pull_request.head_oid):
        return "The live pull-request head OID is missing or invalid."
    if not pull_request.merge_commit_oid or not is_full_oid(pull_request.merge_commit_oid):
        return "The live pull-request merge commit OID is missing or invalid."
    if (
        pull_request.head_repository.casefold() != repository.full_name.casefold()
        or pull_request.head_owner.casefold() != repository.owner.casefold()
    ):
        return "The pull-request head repository does not match the configured repository."
    if pull_request.base_branch != base_branch:
        return "The pull-request base branch does not match the configured base."
    if not pull_request.head_branch or any(
        ord(character) < 32 or ord(character) == 127 for character in pull_request.head_branch
    ):
        return "The live pull-request head branch is empty or contains controls."
    parsed = urlsplit(pull_request.url)
    try:
        port = parsed.port
    except ValueError:
        return "The pull-request URL has an invalid authority."
    segments = parsed.path.split("/")
    if (
        parsed.scheme != "https"
        or parsed.netloc != "github.com"
        or parsed.hostname != "github.com"
        or port is not None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or len(segments) != 5
        or segments[0] != ""
        or segments[1] != repository.owner
        or segments[2] != repository.name
        or segments[3] != "pull"
        or segments[4] != str(requested_number)
    ):
        return "The PR URL is not the canonical URL for the requested repository and PR number."
    return None
