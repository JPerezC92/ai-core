"""Unit tests for domain identity guards covering pull-request and remote identity."""

from __future__ import annotations

from dataclasses import replace

from verified_pr_cleanup_pkg.domain.guards import (
    SshRemote,
    github_repository_from_url,
    parse_ssh_remote,
    pull_request_identity_error,
)
from verified_pr_cleanup_pkg.domain._test_support import CleanupTestData as Data

REMOTE_PATH = f"{Data.OWNER}/{Data.REPOSITORY}"
SSH_ALIAS_HOST = "github.com-personal"
SSH_FOLDER_ALIAS_HOST = "work-account"
ACCEPTED_GITHUB_REMOTE_URLS = (
    f"https://github.com/{REMOTE_PATH}",
    f"https://github.com/{REMOTE_PATH}.git",
    f"git@github.com:{REMOTE_PATH}",
    f"git@github.com:{REMOTE_PATH}.git",
    f"ssh://git@github.com/{REMOTE_PATH}.git",
)
REJECTED_GITHUB_REMOTE_URLS = (
    f"https://github.com.evil/{REMOTE_PATH}.git",
    f"git@github.com.evil:{REMOTE_PATH}.git",
    f"git@{SSH_ALIAS_HOST}:{REMOTE_PATH}.git",
    f"ssh://git@{SSH_ALIAS_HOST}/{REMOTE_PATH}.git",
    f"git@{SSH_FOLDER_ALIAS_HOST}:{REMOTE_PATH}.git",
    f"https://{SSH_ALIAS_HOST}/{REMOTE_PATH}.git",
    f"git@github.com-:{REMOTE_PATH}.git",
    f"git@github.com:{Data.OWNER}",
    "git@github.com:",
    f"git@github.com:{REMOTE_PATH}.git?redirect=evil",
    f"git@github.com:{REMOTE_PATH}.git#fragment",
    f"https://git@github.com/{REMOTE_PATH}.git",
    f"https://github.com:443/{REMOTE_PATH}.git",
    f"ssh://git@github.com:443/{REMOTE_PATH}.git",
    f"ssh://git:token@github.com/{REMOTE_PATH}.git",
    f"ssh://other@github.com/{REMOTE_PATH}.git",
    f"ssh://github.com/{REMOTE_PATH}.git",
    f"ssh://git@github.com/{REMOTE_PATH}.git?redirect=evil",
    f"ssh://git@github.com/{REMOTE_PATH}.git#fragment",
)
ACCEPTED_SSH_REMOTES = (
    (f"git@{SSH_ALIAS_HOST}:{REMOTE_PATH}.git", SshRemote(SSH_ALIAS_HOST, "git", Data.OWNER, Data.REPOSITORY)),
    (f"ssh://git@{SSH_ALIAS_HOST}/{REMOTE_PATH}.git", SshRemote(SSH_ALIAS_HOST, "git", Data.OWNER, Data.REPOSITORY)),
    (f"git@{SSH_FOLDER_ALIAS_HOST}:{REMOTE_PATH}", SshRemote(SSH_FOLDER_ALIAS_HOST, "git", Data.OWNER, Data.REPOSITORY)),
    (f"ssh://other@{SSH_FOLDER_ALIAS_HOST}/{REMOTE_PATH}.git", SshRemote(SSH_FOLDER_ALIAS_HOST, "other", Data.OWNER, Data.REPOSITORY)),
)
REJECTED_SSH_REMOTES = (
    f"{SSH_ALIAS_HOST}:{REMOTE_PATH}",
    f"git@{SSH_ALIAS_HOST}:{Data.OWNER}",
    f"git@{SSH_ALIAS_HOST}:",
    f"git@-oProxyCommand=evil:{REMOTE_PATH}.git",
    f"git@*:{REMOTE_PATH}.git",
    f"git@{SSH_ALIAS_HOST}:{REMOTE_PATH}.git?redirect=evil",
    f"git@{SSH_ALIAS_HOST}:{REMOTE_PATH}.git#fragment",
    f"git@{SSH_ALIAS_HOST}:token@{REMOTE_PATH}.git",
    f"ssh://{SSH_ALIAS_HOST}/{REMOTE_PATH}.git",
    f"ssh://git:token@{SSH_ALIAS_HOST}/{REMOTE_PATH}.git",
    f"ssh://git@{SSH_ALIAS_HOST}:22/{REMOTE_PATH}.git",
    f"ssh://git@{SSH_ALIAS_HOST}/{REMOTE_PATH}.git/extra",
    f"ssh://git@-oProxyCommand=evil/{REMOTE_PATH}.git",
    f"ssh://git@{SSH_ALIAS_HOST}/{REMOTE_PATH}.git?redirect=evil",
    f"ssh://git@{SSH_ALIAS_HOST}/{REMOTE_PATH}.git#fragment",
)


def test_remote_identity_accepts_exact_github_https_and_ssh_remotes() -> None:
    """Accept exact github.com remotes only; aliases remain unresolved domain data."""
    expected = Data.repository()
    assert all(github_repository_from_url(url) == expected for url in ACCEPTED_GITHUB_REMOTE_URLS)


def test_remote_identity_rejects_alias_lookalike_credential_and_port_remotes() -> None:
    """Refuse SSH aliases, spoofed hosts, credentials, ports, extra segments, and queries."""
    assert all(github_repository_from_url(url) is None for url in REJECTED_GITHUB_REMOTE_URLS)


def test_ssh_parser_returns_host_and_repository_parts_without_host_policy() -> None:
    """Parse scp-style and ssh URL aliases into host, user, owner, and repository."""
    assert all(parse_ssh_remote(url) == expected for url, expected in ACCEPTED_SSH_REMOTES)
    assert all(parse_ssh_remote(url) is None for url in REJECTED_SSH_REMOTES)


def test_pr_identity_requires_canonical_url_and_exact_repository_number() -> None:
    """Accept the exact PR identity and reject adversarial URL/repository bindings."""
    repository = Data.repository()
    pull_request = Data.create()
    assert pull_request_identity_error(
        pull_request, Data.PR_NUMBER, repository, Data.BASE_BRANCH
    ) is None
    for url in Data.INVALID_PR_URLS:
        invalid = replace(pull_request, url=url)
        assert pull_request_identity_error(
            invalid, Data.PR_NUMBER, repository, Data.BASE_BRANCH
        ) is not None


def test_pr_identity_rejects_wrong_number_repository_base_and_merge_state() -> None:
    """Refuse mismatched PR number, head repository, base, and merged predicate."""
    repository = Data.repository()
    pull_request = Data.create()
    invalid_records = (
        (pull_request, Data.PR_NUMBER + 1, repository, Data.BASE_BRANCH),
        (replace(pull_request, head_repository=Data.OTHER_REPOSITORY), Data.PR_NUMBER, repository, Data.BASE_BRANCH),
        (replace(pull_request, base_branch=Data.WRONG_BASE_BRANCH), Data.PR_NUMBER, repository, Data.BASE_BRANCH),
        (replace(pull_request, state=Data.OPEN_PR_STATE), Data.PR_NUMBER, repository, Data.BASE_BRANCH),
    )
    for candidate, number, expected_repository, base_branch in invalid_records:
        assert pull_request_identity_error(candidate, number, expected_repository, base_branch) is not None
