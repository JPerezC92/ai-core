"""Integration tests for remote, ref, and object read-only inventory."""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Callable, Mapping
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

SSH_ALIAS_HOST = "github.com-personal"
REMOTE_PATH = f"{Data.OWNER}/{Data.REPOSITORY}"
ALIAS_REMOTE_URLS = (
    f"git@{SSH_ALIAS_HOST}:{REMOTE_PATH}.git",
    f"ssh://git@{SSH_ALIAS_HOST}/{REMOTE_PATH}.git",
)
GITHUB_SSH_CONFIG = b"hostname github.com\nuser git\nport 22\n"


def _fake_remote_git(url: str) -> Callable[..., bytes]:
    """Return a `_git` double reporting the supplied fetch and push URL."""

    def fake_git(*arguments: str, cwd: Path | None = None) -> bytes:
        if arguments[:2] == ("remote", "get-url"):
            return f"{url}\n".encode("utf-8")
        raise AssertionError(f"unexpected git arguments: {arguments}")

    return fake_git


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


def test_remote_identity_accepts_exact_https_without_any_ssh_expansion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resolve an exact github.com HTTPS remote without invoking ssh."""
    git = GitCli.__new__(GitCli)
    monkeypatch.setattr(git, "_git", _fake_remote_git(Data.GITHUB_REMOTE_URL))
    monkeypatch.setattr(git, "_ssh", lambda *arguments: pytest.fail("ssh must not run"))
    assert git.remote_identity(Data.REMOTE_NAME) == Data.repository()


@pytest.mark.parametrize("alias_url", ALIAS_REMOTE_URLS)
def test_remote_identity_resolves_any_ssh_alias_name_through_local_config(
    alias_url: str, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Resolve scp and ssh alias forms through `ssh -G` without a network connection."""
    git = GitCli.__new__(GitCli)
    observed_ssh: list[tuple[str, ...]] = []

    def fake_ssh(*arguments: str) -> bytes:
        observed_ssh.append(arguments)
        return GITHUB_SSH_CONFIG

    monkeypatch.setattr(git, "_git", _fake_remote_git(alias_url))
    monkeypatch.setattr(git, "_ssh", fake_ssh)
    assert git.remote_identity(Data.REMOTE_NAME) == Data.repository()
    assert observed_ssh == [("-G", SSH_ALIAS_HOST), ("-G", SSH_ALIAS_HOST)]


@pytest.mark.parametrize(
    "config",
    (
        b"hostname github.com.evil\nuser git\n",
        b"hostname github.com\nuser other\n",
        b"hostname github.com\n",
        b"user git\n",
        b"hostname github.com\nhostname github.com.evil\nuser git\n",
    ),
)
def test_remote_identity_rejects_aliases_not_resolving_to_github(
    config: bytes, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fail closed unless expansion yields canonical github.com and the git user."""
    git = GitCli.__new__(GitCli)
    monkeypatch.setattr(git, "_git", _fake_remote_git(ALIAS_REMOTE_URLS[0]))
    monkeypatch.setattr(git, "_ssh", lambda *arguments: config)
    with pytest.raises(BoundaryFailure, match="SSH"):
        git.remote_identity(Data.REMOTE_NAME)


def test_remote_identity_rejects_non_git_alias_user_before_expansion(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Refuse an SSH alias carrying a non-git user without running ssh."""
    git = GitCli.__new__(GitCli)
    monkeypatch.setattr(
        git, "_git",
        _fake_remote_git(f"ssh://other@{SSH_ALIAS_HOST}/{REMOTE_PATH}.git"),
    )
    monkeypatch.setattr(git, "_ssh", lambda *arguments: pytest.fail("ssh must not run"))
    with pytest.raises(BoundaryFailure, match="not a recognised GitHub remote"):
        git.remote_identity(Data.REMOTE_NAME)


def test_ssh_expansion_uses_the_configured_ssh_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Run Git's configured SSH command with each leading tilde expanded, without a shell."""
    git = GitCli.__new__(GitCli)
    observed: list[tuple[str, tuple[str, ...]]] = []

    def fake_run(
        arguments: tuple[str, ...], cwd: Path | None = None
    ) -> subprocess.CompletedProcess[bytes]:
        assert arguments == ("config", "--get", "core.sshcommand")
        return subprocess.CompletedProcess(
            list(arguments), 0, b"ssh -i ~/.ssh/key -F ~/.ssh/config\n", b""
        )

    def fake_run_process(
        executable: str,
        arguments: tuple[str, ...],
        cwd: Path | None = None,
        environment: Mapping[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        observed.append((executable, arguments))
        return subprocess.CompletedProcess(
            [executable, *arguments], 0, GITHUB_SSH_CONFIG, b""
        )

    monkeypatch.setattr(git, "_run", fake_run)
    monkeypatch.setattr(git, "_run_process", fake_run_process)
    assert git._ssh("-G", SSH_ALIAS_HOST) == GITHUB_SSH_CONFIG
    assert observed == [(
        "ssh",
        (
            "-i", os.path.expanduser("~/.ssh/key"),
            "-F", os.path.expanduser("~/.ssh/config"),
            "-G", SSH_ALIAS_HOST,
        ),
    )]


def test_ssh_expansion_falls_back_to_path_ssh_without_a_configured_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Use the PATH SSH executable when Git reports no core.sshcommand."""
    git = GitCli.__new__(GitCli)
    observed: list[tuple[str, tuple[str, ...]]] = []

    def fake_run(
        arguments: tuple[str, ...], cwd: Path | None = None
    ) -> subprocess.CompletedProcess[bytes]:
        assert arguments == ("config", "--get", "core.sshcommand")
        return subprocess.CompletedProcess(list(arguments), 1, b"", b"")

    def fake_run_process(
        executable: str,
        arguments: tuple[str, ...],
        cwd: Path | None = None,
        environment: Mapping[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        observed.append((executable, arguments))
        return subprocess.CompletedProcess(
            [executable, *arguments], 0, GITHUB_SSH_CONFIG, b""
        )

    monkeypatch.setattr(git, "_run", fake_run)
    monkeypatch.setattr(git, "_run_process", fake_run_process)
    monkeypatch.setattr(shutil, "which", lambda command: Data.GIT_EXECUTABLE_STUB)
    assert git._ssh("-G", SSH_ALIAS_HOST) == GITHUB_SSH_CONFIG
    assert observed == [(Data.GIT_EXECUTABLE_STUB, ("-G", SSH_ALIAS_HOST))]


def test_ssh_expansion_fails_closed_without_an_ssh_executable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Raise a boundary failure instead of guessing when no SSH command is available."""
    git = GitCli.__new__(GitCli)
    monkeypatch.setattr(
        git, "_run",
        lambda arguments, cwd=None: subprocess.CompletedProcess(
            list(arguments), 1, b"", b""
        ),
    )
    monkeypatch.setattr(shutil, "which", lambda command: None)
    with pytest.raises(BoundaryFailure, match="SSH executable was not found"):
        git._ssh("-G", SSH_ALIAS_HOST)


def test_ssh_expansion_fails_closed_when_the_configured_command_cannot_be_read(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fail closed when Git cannot report core.sshcommand for a non-absence reason."""
    git = GitCli.__new__(GitCli)
    monkeypatch.setattr(
        git, "_run",
        lambda arguments, cwd=None: subprocess.CompletedProcess(
            list(arguments), 128, b"", b"fatal"
        ),
    )

    def fail_run_process(*arguments: object) -> subprocess.CompletedProcess[bytes]:
        pytest.fail("ssh must not run")

    monkeypatch.setattr(git, "_run_process", fail_run_process)
    with pytest.raises(BoundaryFailure, match="SSH"):
        git._ssh("-G", SSH_ALIAS_HOST)


@pytest.mark.parametrize(
    "configured",
    (
        b"\n",
        b"   ",
        b"\xff\xfe",
        b"ssh -i 'unterminated\n",
    ),
)
def test_ssh_expansion_rejects_empty_or_malformed_configured_commands(
    configured: bytes, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Refuse an empty, non-UTF-8, or unparsable configured SSH command."""
    git = GitCli.__new__(GitCli)
    monkeypatch.setattr(
        git, "_run",
        lambda arguments, cwd=None: subprocess.CompletedProcess(
            list(arguments), 0, configured, b""
        ),
    )
    with pytest.raises(BoundaryFailure, match="SSH"):
        git._ssh("-G", SSH_ALIAS_HOST)


def test_ssh_expansion_fails_closed_on_a_failed_process(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Raise a boundary failure when the resolved ssh cannot expand the configuration."""
    git = GitCli.__new__(GitCli)
    monkeypatch.setattr(
        git, "_run",
        lambda arguments, cwd=None: subprocess.CompletedProcess(
            list(arguments), 1, b"", b""
        ),
    )
    monkeypatch.setattr(shutil, "which", lambda command: Data.GIT_EXECUTABLE_STUB)

    def fake_run_process(
        executable: str,
        arguments: tuple[str, ...],
        cwd: Path | None = None,
        environment: Mapping[str, str] | None = None,
    ) -> subprocess.CompletedProcess[bytes]:
        return subprocess.CompletedProcess([executable, *arguments], 255, b"", b"error")

    monkeypatch.setattr(git, "_run_process", fake_run_process)
    with pytest.raises(BoundaryFailure, match="SSH configuration expansion failed"):
        git._ssh("-G", SSH_ALIAS_HOST)
