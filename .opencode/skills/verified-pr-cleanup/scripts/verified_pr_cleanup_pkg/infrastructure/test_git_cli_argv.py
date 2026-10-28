"""Unit tests for exact read-only Git argv shapes and command subcommands."""

from __future__ import annotations

from verified_pr_cleanup_pkg.domain._test_support import CleanupTestData as Data
from verified_pr_cleanup_pkg.infrastructure._test_support import is_allowed_read_only_git_argv


def test_diff_allowlist_requires_full_revisions_and_literal_pathspec_form() -> None:
    """Reject output options and extra arguments while accepting exact parity forms."""
    assert is_allowed_read_only_git_argv((
        "diff", "--name-only", "-z", Data.MERGE_BASE_OID, Data.HEAD_OID,
    ))
    assert is_allowed_read_only_git_argv((
        "--literal-pathspecs", "diff", "--quiet", "--exit-code",
        Data.BASE_OID, Data.HEAD_OID, "--", Data.MAGIC_PATHSPEC,
    ))
    rejected = (
        ("diff", "--name-only", "-z", Data.OUTPUT_FILE_OPTION, Data.HEAD_OID),
        ("diff", "--name-only", "-z", Data.BASE_OID, Data.HEAD_OID, Data.EXTRA_DIFF_OPTION),
        ("diff", "--name-only", "-z", Data.INVALID_OID, Data.HEAD_OID),
        ("diff", "--name-only", "-z", Data.BASE_OID, Data.INVALID_OID),
        ("diff", "--quiet", "--exit-code", Data.BASE_OID, Data.HEAD_OID, "--", Data.PARITY_PATH),
        ("--literal-pathspecs", "diff", "--quiet", "--exit-code", Data.INVALID_OID, Data.HEAD_OID, "--", Data.PARITY_PATH),
        ("--literal-pathspecs", "diff", "--quiet", "--exit-code", Data.BASE_OID, Data.INVALID_OID, "--", Data.PARITY_PATH),
        ("--literal-pathspecs", "diff", "--quiet", "--exit-code", Data.BASE_OID, Data.HEAD_OID, Data.OUTPUT_FILE_OPTION, "--", Data.PARITY_PATH),
        ("--literal-pathspecs", "diff", "--quiet", "--exit-code", Data.BASE_OID, Data.HEAD_OID, "--"),
        ("--literal-pathspecs", "diff", "--quiet", "--exit-code", Data.BASE_OID, Data.HEAD_OID, Data.PARITY_PATH),
        ("--literal-pathspecs", "diff", "--quiet", "--exit-code", Data.BASE_OID, Data.HEAD_OID, "--stat", "--", Data.PARITY_PATH),
    )
    assert all(not is_allowed_read_only_git_argv(arguments) for arguments in rejected)


def test_literal_diff_allowlist_rejects_bare_or_empty_pathspec_separator() -> None:
    """Require at least one non-empty literal path after the parity separator."""
    bare = (
        "--literal-pathspecs", "diff", "--quiet", "--exit-code",
        Data.BASE_OID, Data.HEAD_OID, "--",
    )
    assert not is_allowed_read_only_git_argv(bare)
    assert not is_allowed_read_only_git_argv(bare + ("",))
    assert is_allowed_read_only_git_argv(bare + (Data.PARITY_PATH,))


def test_remote_and_worktree_allowlist_excludes_mutating_subcommands() -> None:
    """Allow only URL/ref reads and worktree listing; every mutation is rejected."""
    assert is_allowed_read_only_git_argv(("remote", "get-url", "--all", Data.REMOTE_NAME))
    assert is_allowed_read_only_git_argv(("remote", "get-url", "--push", "--all", Data.REMOTE_NAME))
    assert is_allowed_read_only_git_argv(("worktree", "list", "--porcelain"))
    rejected = (
        ("remote", "remove", Data.REMOTE_NAME),
        ("remote", "add", Data.REMOTE_NAME, Data.GITHUB_REMOTE_URL),
        ("remote", "rename", Data.REMOTE_NAME, Data.GIT_LOCAL_DIR),
        ("remote", "prune", Data.REMOTE_NAME),
        ("remote", "set-url", Data.REMOTE_NAME, Data.GITHUB_REMOTE_URL),
        ("worktree", "add", Data.GIT_LOCAL_DIR),
        ("worktree", "remove", Data.GIT_LOCAL_DIR),
        ("worktree", "move", Data.GIT_LOCAL_DIR, Data.GIT_BARE_DIR),
        ("worktree", "lock", Data.GIT_LOCAL_DIR),
        ("worktree", "unlock", Data.GIT_LOCAL_DIR),
        ("worktree", "prune"),
        ("worktree", "repair", Data.GIT_LOCAL_DIR),
    )
    assert all(not is_allowed_read_only_git_argv(arguments) for arguments in rejected)
