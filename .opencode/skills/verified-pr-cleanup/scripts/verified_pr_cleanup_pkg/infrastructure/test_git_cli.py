"""Integration tests for Herald changed-path parity and literal pathspec handling."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from verified_pr_cleanup_pkg.domain._test_support import CleanupTestData as Data
from verified_pr_cleanup_pkg.infrastructure._test_support import create_parity_fixture
from verified_pr_cleanup_pkg.infrastructure.git_cli import GitCli


@pytest.mark.parametrize("parity_matches", (True, False))
def test_herald_changed_path_proof_compares_only_head_changed_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, parity_matches: bool
) -> None:
    """Accept parity on head-changed paths despite unrelated base-tree differences."""
    fixture = create_parity_fixture(tmp_path, parity_matches)
    monkeypatch.chdir(fixture.local)
    assert fixture.head_oid is not None
    git = GitCli()
    merge_base = git.merge_base(fixture.base_oid, fixture.head_oid)
    changed_paths = git.changed_paths(merge_base, fixture.head_oid)
    assert changed_paths == (Data.PARITY_PATH,)
    assert git.paths_match(fixture.base_oid, fixture.head_oid, changed_paths) is parity_matches


def test_magic_pathspec_is_sent_as_a_literal_herald_parity_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Pass magic-looking filenames with Git literal-pathspec mode enabled."""
    git = GitCli.__new__(GitCli)
    git._executable = Data.GIT_EXECUTABLE_STUB
    captured: list[tuple[str, ...]] = []

    def fake_run(
        arguments: tuple[str, ...], cwd: Path | None = None
    ) -> subprocess.CompletedProcess[bytes]:
        captured.append(arguments)
        return subprocess.CompletedProcess([Data.GIT_EXECUTABLE_STUB], 0, b"", b"")

    monkeypatch.setattr(git, "_run", fake_run)
    assert git.paths_match(Data.BASE_OID, Data.HEAD_OID, (Data.MAGIC_PATHSPEC,))
    assert captured == [(
        "--literal-pathspecs", "diff", "--quiet", "--exit-code",
        Data.BASE_OID, Data.HEAD_OID, "--", Data.MAGIC_PATHSPEC,
    )]
