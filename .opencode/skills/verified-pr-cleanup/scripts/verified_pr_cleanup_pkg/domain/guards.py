"""Pure identity guards for preflight evidence."""

from __future__ import annotations

import re
from urllib.parse import urlsplit

from verified_pr_cleanup_pkg.domain.models import PullRequest, RepositoryIdentity

OID_PATTERN = re.compile(r"^(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})$")
REMOTE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
GITHUB_OWNER_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
GITHUB_REPOSITORY_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def is_full_oid(value: str) -> bool:
    """Return True only for a full SHA-1 or SHA-256 object identifier."""
    return OID_PATTERN.fullmatch(value) is not None


def is_safe_remote_name(value: str) -> bool:
    """Reject option-like and ambiguous remote names."""
    return REMOTE_NAME_PATTERN.fullmatch(value) is not None and value not in {".", ".."} and ".." not in value


def github_repository_from_url(value: str) -> RepositoryIdentity | None:
    """Map credential-free github.com HTTPS/SSH remotes to repository identity."""
    owner: str
    repository: str
    if value.startswith("git@github.com:"):
        path = value.removeprefix("git@github.com:")
        if any(marker in path for marker in (":", "?", "#")):
            return None
        owner, separator, repository = path.partition("/")
        if not separator:
            return None
    else:
        parsed = urlsplit(value)
        try:
            port = parsed.port
        except ValueError:
            return None
        if (
            parsed.scheme not in {"https", "ssh"}
            or parsed.hostname != "github.com"
            or port is not None
            or parsed.query
            or parsed.fragment
            or parsed.password is not None
            or (parsed.scheme == "https" and parsed.username is not None)
            or (parsed.scheme == "ssh" and parsed.username != "git")
        ):
            return None
        segments = parsed.path.removeprefix("/").split("/")
        if len(segments) != 2:
            return None
        owner, repository = segments
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
