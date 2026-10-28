"""Integration tests for remote, ref, and object read-only inventory."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from verified_pr_cleanup_pkg.domain._test_support import CleanupTestData as Data
from verified_pr_cleanup_pkg.domain.models import BoundaryFailure
from verified_pr_cleanup_pkg.infrastructure._test_support import (
    create_inventory_fixture,
    create_nested_branch_fixture,
    is_allowed_read_only_git_argv,
    nested_branch_name,
    set_fixture_remote,
)
from verified_pr_cleanup_pkg.infrastructure.git_cli import GitCli


def test_remote_ref_and_object_inventory_maps_from_isolated_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Read repository identity, refs, and commit presence from a temporary Git repo."""
    fixture = create_inventory_fixture(tmp_path)
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
    set_fixture_remote(fixture.local, Data.GITHUB_REMOTE_URL)
    assert git.remote_identity(Data.REMOTE_NAME) == Data.repository()
    set_fixture_remote(fixture.local, str(fixture.bare))

    assert git.remote_branch_oid(Data.REMOTE_NAME, Data.BASE_BRANCH) == fixture.base_oid
    assert git.local_branch_oid(Data.BASE_BRANCH) == fixture.base_oid
    assert git.local_branch_oid(Data.HEAD_BRANCH) is None
    assert git.object_exists(fixture.base_oid)
    assert not git.object_exists(Data.MERGE_OID)
    assert all(is_allowed_read_only_git_argv(arguments) for arguments in commands)


def test_line_inventory_accepts_ls_remote_tab_and_rejects_other_controls() -> None:
    """Keep strict line records while allowing the mandatory ls-remote TAB separator."""
    git = GitCli.__new__(GitCli)
    record = f"{Data.HEAD_OID}\trefs/heads/{Data.HEAD_BRANCH}"
    assert git._lines(f"{record}\n".encode("utf-8")) == [record]
    malformed_outputs = (
        f"{record}\x0brefs/heads/{Data.BASE_BRANCH}\n",
        f"{record}\n\n",
        "\n",
        f"{record}\r\n",
    )
    for malformed in malformed_outputs:
        with pytest.raises(BoundaryFailure, match="malformed line-delimited output"):
            git._lines(malformed.encode("utf-8"))


def test_local_branch_oid_ignores_refs_nested_below_the_requested_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resolve only the exact requested ref; a nested ref never satisfies it."""
    fixture = create_nested_branch_fixture(tmp_path)
    monkeypatch.chdir(fixture.local)
    git = GitCli()
    assert git.local_branch_oid(Data.HEAD_BRANCH) is None
    assert git.local_branch_oid(nested_branch_name()) == fixture.base_oid
    assert git.local_branch_oid(Data.BASE_BRANCH) == fixture.base_oid


@pytest.mark.parametrize(
    "record",
    (
        f"refs/heads/{Data.BASE_BRANCH}",
        f"refs/heads/{Data.BASE_BRANCH}\t{Data.INVALID_OID}",
        f"refs/heads/{Data.BASE_BRANCH}\t{Data.BASE_OID}\t{Data.BASE_OID}",
        f"refs/tags/{Data.BASE_BRANCH}\t{Data.BASE_OID}",
        f"refs/heads/{Data.BASE_BRANCH}\t{Data.BASE_OID}\n"
        f"refs/heads/{Data.BASE_BRANCH}\t{Data.DIVERGENT_OID}",
    ),
)
def test_local_branch_oid_rejects_malformed_or_ambiguous_ref_records(
    record: str, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fail closed unless the lookup returns exactly one branch ref/object pair."""
    git = GitCli.__new__(GitCli)

    def fake_run(
        arguments: tuple[str, ...], cwd: Path | None = None
    ) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess(
            list(arguments), 0, f"{record}\n".encode("utf-8"), b""
        )

    monkeypatch.setattr(git, "_run", fake_run)
    with pytest.raises(BoundaryFailure, match="Local branch ref"):
        git.local_branch_oid(Data.BASE_BRANCH)
