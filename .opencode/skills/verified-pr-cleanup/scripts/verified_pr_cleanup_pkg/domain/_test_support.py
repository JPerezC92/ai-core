"""Shared deterministic data and argv policies for isolated preflight tests."""

from __future__ import annotations

from typing import cast

from verified_pr_cleanup_pkg.domain.models import (
    PullRequest,
    RepositoryIdentity,
    Worktree,
)


class CleanupTestData:
    """Factory for domain values and fake GitHub payloads used by T2 tests."""

    OWNER = "aicore"
    REPOSITORY = "toolbox"
    GITHUB_REMOTE_URL = f"https://github.com/{OWNER}/{REPOSITORY}.git"
    GH_FAKE_EXECUTABLE = "gh-fake"
    GH_FAKE_STDERR = b"fake GitHub CLI response"
    GIT_EXECUTABLE_STUB = "git-fake"
    BASE_BRANCH = "main"
    MERGED_PR_STATE = "MERGED"
    HEAD_BRANCH = "feature/cleanup"
    PR_NUMBER = 37
    OBSERVED_AT = "2026-10-28T12:00:00+00:00"
    HEAD_OID = "a" * 40
    DIVERGENT_OID = "f" * 40
    MERGE_OID = "b" * 40
    BASE_OID = "c" * 40
    MERGE_BASE_OID = "d" * 40
    REMOTE_NAME = "origin"
    GIT_LOCAL_DIR = "local"
    GIT_BARE_DIR = "remote.git"
    GIT_USER_NAME = "Cleanup Test"
    GIT_USER_EMAIL = "cleanup@example.invalid"
    BASE_FILE = "README.md"
    BASE_CONTENT = "base fixture\n"
    BASE_COMMIT_LABEL = "base"
    FEATURE_COMMIT_LABEL = "feature"
    PARITY_COMMIT_LABEL = "squash-equivalent base"
    E2E_MERGE_COMMIT_LABEL = "merge feature"
    PARITY_PATH = "target.txt"
    PARITY_HEAD_CONTENT = "same final content\n"
    PARITY_BASE_MISMATCH_CONTENT = "different result\n"
    PARITY_UNRELATED_PATH = "unrelated.txt"
    PARITY_UNRELATED_CONTENT = "only on base\n"
    FEATURE_FILE = "feature.txt"
    FEATURE_CONTENT = "merged change\n"
    MAGIC_PATHSPEC = ":(exclude)secret"
    OUTPUT_FILE_OPTION = "--output=sentinel"
    EXTRA_DIFF_OPTION = "--stat"
    INVALID_OID = "short"
    OTHER_REPOSITORY = "other/toolbox"
    WRONG_BASE_BRANCH = "release"
    CHANGED_HEAD_BRANCH = "feature/other"
    INVALID_HEAD_BRANCH = "feature bad"
    LINKED_WORKTREE_PATH = "linked"
    LINKED_WORKTREE_BRANCH = "topic"
    OPEN_PR_STATE = "OPEN"
    GITHUB_FAILURE_EXIT_CODE = 1
    WRONG_PR_NUMBER = PR_NUMBER + 1
    INVALID_PR_URLS = (
        "https://github.com.evil/aicore/toolbox/pull/37",
        "https://github.com/aicore-other/toolbox/pull/37",
        "https://github.com/aicore/toolbox-extra/pull/37",
        "https://github.com/aicore/toolbox/pull/38",
        "https://github.com/aicore/toolbox/pull/037",
        "https://github.com/AICore/toolbox/pull/37",
        "https://github.com/aicore/Toolbox/pull/37",
        "https://github.com/aicore/toolbox/pull/37/files",
        "https://github.com/aicore/toolbox/pull/37?redirect=evil",
        "https://github.com@evil/aicore/toolbox/pull/37",
        "https://github.com:443/aicore/toolbox/pull/37",
        "http://github.com/aicore/toolbox/pull/37",
    )
    MALFORMED_GITHUB_PAYLOAD_FIELDS = (
        ("mergeCommit", "not-an-object"),
        ("headRepository", []),
        ("headRepositoryOwner", []),
        ("headRefName", 12),
        ("mergedAt", 12),
    )
    INVALID_GITHUB_PR_NUMBERS = (0, -1, True, "37")

    @classmethod
    def create(cls, **overrides: object) -> PullRequest:
        """Create one deterministic PR record with caller overrides."""
        values: dict[str, object] = {
            "number": cls.PR_NUMBER,
            "state": cls.MERGED_PR_STATE,
            "merged_at": "2026-10-28T12:00:00Z",
            "merge_commit_oid": cls.MERGE_OID,
            "head_branch": cls.HEAD_BRANCH,
            "head_oid": cls.HEAD_OID,
            "head_repository": f"{cls.OWNER}/{cls.REPOSITORY}",
            "head_owner": cls.OWNER,
            "base_branch": cls.BASE_BRANCH,
            "url": cls.pr_url(),
        }
        values.update(overrides)
        return PullRequest(
            cast(int, values["number"]), cast(str, values["state"]),
            cast(str | None, values["merged_at"]), cast(str | None, values["merge_commit_oid"]),
            cast(str, values["head_branch"]), cast(str, values["head_oid"]),
            cast(str, values["head_repository"]), cast(str, values["head_owner"]),
            cast(str, values["base_branch"]), cast(str, values["url"]),
        )

    @classmethod
    def repository(cls) -> RepositoryIdentity:
        """Return the configured GitHub repository identity."""
        return RepositoryIdentity(cls.OWNER, cls.REPOSITORY)

    @classmethod
    def pr_url(cls) -> str:
        """Return the canonical URL for the default PR number."""
        return f"https://github.com/{cls.OWNER}/{cls.REPOSITORY}/pull/{cls.PR_NUMBER}"

    @classmethod
    def worktree(
        cls,
        path: str = "worktree",
        branch: str | None = BASE_BRANCH,
    ) -> Worktree:
        """Create one linked-worktree occupancy value."""
        return Worktree(path, branch)

    @classmethod
    def github_payload(cls, **overrides: object) -> dict[str, object]:
        """Create a complete fake `gh pr view --json` payload."""
        pull_request = cls.create(**overrides)
        merged = pull_request.state.upper() == cls.MERGED_PR_STATE
        merge_commit_oid = pull_request.merge_commit_oid if merged else None
        return {
            "number": pull_request.number,
            "state": pull_request.state,
            "mergedAt": pull_request.merged_at if merged else None,
            "mergeCommit": (
                {"oid": merge_commit_oid} if merge_commit_oid is not None else None
            ),
            "headRefName": pull_request.head_branch,
            "headRefOid": pull_request.head_oid,
            "headRepository": {"nameWithOwner": pull_request.head_repository},
            "headRepositoryOwner": {"login": pull_request.head_owner},
            "baseRefName": pull_request.base_branch,
            "url": pull_request.url,
        }
