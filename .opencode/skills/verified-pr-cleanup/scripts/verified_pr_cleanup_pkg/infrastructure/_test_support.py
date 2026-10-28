"""Shared isolated Git fixtures and exact read-only argv policies for adapter tests."""

from __future__ import annotations

import json
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import pytest

from verified_pr_cleanup_pkg.domain._test_support import CleanupTestData as Data
from verified_pr_cleanup_pkg.domain.guards import is_full_oid, is_safe_remote_name


@dataclass(frozen=True)
class GitRepositoryFixture:
    """Commit and remote identities created inside one isolated tmp_path."""

    local: Path
    bare: Path
    base_oid: str
    head_oid: str | None = None
    merge_oid: str | None = None


def _run_git(cwd: Path | None, *arguments: str) -> bytes:
    """Mutate or inspect only the temporary test repository during fixture setup."""
    completed = subprocess.run(
        ["git", *arguments], cwd=cwd, capture_output=True, check=False, shell=False
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr.decode("utf-8", errors="replace"))
    return completed.stdout


def _base_repository(root: Path) -> GitRepositoryFixture:
    """Create a base commit and matching temporary bare remote."""
    local = root / Data.GIT_LOCAL_DIR
    bare = root / Data.GIT_BARE_DIR
    _run_git(None, "init", "--bare", str(bare))
    _run_git(None, "init", str(local))
    _run_git(local, "config", "user.name", Data.GIT_USER_NAME)
    _run_git(local, "config", "user.email", Data.GIT_USER_EMAIL)
    _run_git(local, "checkout", "-b", Data.BASE_BRANCH)
    (local / Data.BASE_FILE).write_text(Data.BASE_CONTENT, encoding="utf-8")
    _run_git(local, "add", Data.BASE_FILE)
    _run_git(local, "commit", "-m", Data.BASE_COMMIT_LABEL)
    _run_git(local, "remote", "add", Data.REMOTE_NAME, str(bare))
    _run_git(local, "push", "--set-upstream", Data.REMOTE_NAME, Data.BASE_BRANCH)
    oid = _run_git(local, "rev-parse", "HEAD").decode("ascii").strip()
    return GitRepositoryFixture(local, bare, oid)


def create_inventory_fixture(root: Path) -> GitRepositoryFixture:
    """Create a repo for read-only remote/ref/object and worktree inventory tests."""
    return _base_repository(root)


def create_nested_branch_fixture(root: Path) -> GitRepositoryFixture:
    """Add a ref nested below the PR head name to prove exact-ref lookup."""
    fixture = _base_repository(root)
    _run_git(fixture.local, "branch", nested_branch_name())
    return fixture


def nested_branch_name() -> str:
    """Return one branch name nested below the PR head branch name."""
    return f"{Data.HEAD_BRANCH}/nested"


def create_linked_worktree_fixture(root: Path) -> GitRepositoryFixture:
    """Add one linked worktree that has the PR head branch checked out."""
    fixture = _base_repository(root)
    linked = root / Data.LINKED_WORKTREE_PATH
    _run_git(fixture.local, "worktree", "add", "-b", Data.HEAD_BRANCH, str(linked))
    return fixture


def create_parity_fixture(root: Path, parity_matches: bool) -> GitRepositoryFixture:
    """Create divergent local base/head commits for changed-path parity tests."""
    fixture = _base_repository(root)
    local = fixture.local
    _run_git(local, "checkout", "-b", Data.HEAD_BRANCH)
    (local / Data.PARITY_PATH).write_text(
        Data.PARITY_HEAD_CONTENT, encoding="utf-8"
    )
    _run_git(local, "add", Data.PARITY_PATH)
    _run_git(local, "commit", "-m", Data.FEATURE_COMMIT_LABEL)
    head_oid = _run_git(local, "rev-parse", "HEAD").decode("ascii").strip()
    _run_git(local, "checkout", Data.BASE_BRANCH)
    base_content = (
        Data.PARITY_HEAD_CONTENT
        if parity_matches
        else Data.PARITY_BASE_MISMATCH_CONTENT
    )
    (local / Data.PARITY_PATH).write_text(base_content, encoding="utf-8")
    (local / Data.PARITY_UNRELATED_PATH).write_text(
        Data.PARITY_UNRELATED_CONTENT, encoding="utf-8"
    )
    _run_git(local, "add", Data.PARITY_PATH, Data.PARITY_UNRELATED_PATH)
    _run_git(local, "commit", "-m", Data.PARITY_COMMIT_LABEL)
    base_oid = _run_git(local, "rev-parse", "HEAD").decode("ascii").strip()
    return GitRepositoryFixture(local, fixture.bare, base_oid, head_oid)


def create_e2e_fixture(
    root: Path, pr_state: str
) -> tuple[GitRepositoryFixture, dict[str, object]]:
    """Create a merged local/bare repo and matching fake GitHub PR response."""
    fixture = _base_repository(root)
    _run_git(fixture.local, "checkout", "-b", Data.HEAD_BRANCH)
    (fixture.local / Data.FEATURE_FILE).write_text(Data.FEATURE_CONTENT, encoding="utf-8")
    _run_git(fixture.local, "add", Data.FEATURE_FILE)
    _run_git(fixture.local, "commit", "-m", Data.FEATURE_COMMIT_LABEL)
    head_oid = _run_git(fixture.local, "rev-parse", "HEAD").decode("ascii").strip()
    _run_git(fixture.local, "checkout", Data.BASE_BRANCH)
    _run_git(
        fixture.local, "merge", "--no-ff", Data.HEAD_BRANCH,
        "-m", Data.E2E_MERGE_COMMIT_LABEL,
    )
    merge_oid = _run_git(fixture.local, "rev-parse", "HEAD").decode("ascii").strip()
    _run_git(
        fixture.local, "push", Data.REMOTE_NAME, Data.BASE_BRANCH, Data.HEAD_BRANCH
    )
    set_fixture_remote(fixture.local, Data.GITHUB_REMOTE_URL)
    payload = Data.github_payload(
        head_oid=head_oid, merge_commit_oid=merge_oid, state=pr_state
    )
    return GitRepositoryFixture(fixture.local, fixture.bare, merge_oid, head_oid, merge_oid), payload


def set_fixture_remote(local: Path, remote_url: str) -> None:
    """Change only the remote URL in an isolated temporary repository."""
    _run_git(local, "remote", "set-url", Data.REMOTE_NAME, remote_url)


def install_fake_process_boundaries(
    monkeypatch: pytest.MonkeyPatch,
    bare_remote: Path,
    github_payload: dict[str, object],
    github_exit_code: int = 0,
) -> list[tuple[str, ...]]:
    """Keep concrete adapters while redirecting GitHub and remote reads to local fakes."""
    original_run = subprocess.run
    original_which = shutil.which
    git_executable = original_which("git")
    if git_executable is None:
        raise AssertionError("Git executable is required by the isolated test fixture")
    observed_git_argv: list[tuple[str, ...]] = []

    def controlled_which(command: str) -> str | None:
        return Data.GH_FAKE_EXECUTABLE if command == "gh" else original_which(command)

    def controlled_run(
        arguments: Sequence[str],
        cwd: Path | None = None,
        capture_output: bool = False,
        check: bool = False,
        shell: bool = False,
        timeout: float | None = None,
        env: Mapping[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        command = list(arguments)
        if command[0] == git_executable:
            git_argv = tuple(command[1:])
            observed_git_argv.append(git_argv)
            if env is None or env.get("GIT_OPTIONAL_LOCKS") != "0":
                raise AssertionError(
                    "Git invocation must pass GIT_OPTIONAL_LOCKS=0 in env."
                )
            if (
                len(git_argv) >= 4
                and git_argv[:2] == ("ls-remote", "--refs")
                and git_argv[2] == Data.REMOTE_NAME
            ):
                command[3] = str(bare_remote)
            return original_run(
                command, cwd=cwd, capture_output=capture_output, check=check,
                shell=shell, timeout=timeout, env=env,
            )
        if command[0] == Data.GH_FAKE_EXECUTABLE:
            return subprocess.CompletedProcess(
                command, github_exit_code, json.dumps(github_payload).encode("utf-8"),
                Data.GH_FAKE_STDERR,
            )
        raise AssertionError("unexpected process boundary")

    monkeypatch.setattr(shutil, "which", controlled_which)
    monkeypatch.setattr(subprocess, "run", controlled_run)
    return observed_git_argv


def is_allowed_read_only_git_argv(arguments: tuple[str, ...]) -> bool:
    """Accept only exact read-only Git command shapes used by the validator."""
    if len(arguments) == 4 and arguments[:3] == ("remote", "get-url", "--all"):
        return is_safe_remote_name(arguments[3])
    if len(arguments) == 5 and arguments[:4] == ("remote", "get-url", "--push", "--all"):
        return is_safe_remote_name(arguments[4])
    if len(arguments) == 4 and arguments[:2] == ("ls-remote", "--refs"):
        return is_safe_remote_name(arguments[2]) and arguments[3].startswith("refs/heads/")
    if len(arguments) == 2 and arguments[0] == "check-ref-format":
        return arguments[1].startswith("refs/heads/")
    if (
        len(arguments) == 3
        and arguments[:2]
        == ("for-each-ref", "--format=%(refname)%09%(objectname)")
    ):
        return arguments[2].startswith("refs/heads/")
    if len(arguments) == 4 and arguments[:3] == ("rev-parse", "--verify", "--quiet"):
        return arguments[3].endswith("^{commit}") and is_full_oid(
            arguments[3].removesuffix("^{commit}")
        )
    if len(arguments) == 4 and arguments[:2] == ("merge-base", "--is-ancestor"):
        return is_full_oid(arguments[2]) and is_full_oid(arguments[3])
    if len(arguments) == 3 and arguments[0] == "merge-base":
        return is_full_oid(arguments[1]) and is_full_oid(arguments[2])
    if len(arguments) == 5 and arguments[:3] == ("diff", "--name-only", "-z"):
        return is_full_oid(arguments[3]) and is_full_oid(arguments[4])
    if len(arguments) >= 8 and arguments[:4] == (
        "--literal-pathspecs", "diff", "--quiet", "--exit-code",
    ):
        return (
            is_full_oid(arguments[4]) and is_full_oid(arguments[5])
            and arguments[6] == "--" and all(path for path in arguments[7:])
        )
    if arguments == ("worktree", "list", "--porcelain"):
        return True
    return False
