"""Integration tests for linked-worktree branch-occupancy inventory."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from verified_pr_cleanup_pkg.domain._test_support import CleanupTestData as Data
from verified_pr_cleanup_pkg.domain.models import BoundaryFailure
from verified_pr_cleanup_pkg.infrastructure._test_support import (
    create_linked_worktree_fixture,
    is_allowed_read_only_git_argv,
)
from verified_pr_cleanup_pkg.infrastructure.git_cli import GitCli


def test_worktree_inventory_reports_every_checked_out_branch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Read the checked-out branch of each linked worktree in an isolated repository."""
    fixture = create_linked_worktree_fixture(tmp_path)
    monkeypatch.chdir(fixture.local)
    git = GitCli()
    original_run = git._run
    commands: list[tuple[str, ...]] = []

    def recording_run(
        arguments: tuple[str, ...], cwd: Path | None = None
    ) -> subprocess.CompletedProcess[bytes]:
        commands.append(arguments)
        return original_run(arguments, cwd)

    monkeypatch.setattr(git, "_run", recording_run)
    worktrees = git.inspect_worktrees()
    assert {worktree.branch for worktree in worktrees} == {
        Data.BASE_BRANCH, Data.HEAD_BRANCH,
    }
    assert all(worktree.path for worktree in worktrees)
    assert all(is_allowed_read_only_git_argv(arguments) for arguments in commands)


def test_duplicate_worktree_paths_become_boundary_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reject an ambiguous inventory that lists the same worktree path twice."""
    git = GitCli.__new__(GitCli)
    git._executable = Data.GIT_EXECUTABLE_STUB

    def fake_git(*arguments: str, cwd: Path | None = None) -> bytes:
        return (
            f"worktree {Data.GIT_LOCAL_DIR}\n\nworktree {Data.GIT_LOCAL_DIR}\n"
        ).encode("utf-8")

    monkeypatch.setattr(git, "_git", fake_git)
    with pytest.raises(BoundaryFailure, match="duplicate paths"):
        git.inspect_worktrees()
