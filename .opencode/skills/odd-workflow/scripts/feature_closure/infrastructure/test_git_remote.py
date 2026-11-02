"""Specify remote branch presence mapping for the Git ls-remote adapter."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPTS))

from feature_closure.infrastructure import git_remote  # noqa: E402
from feature_closure.infrastructure.git_remote import (  # noqa: E402
    GitBoundaryError,
    GitRemoteBranchProbe,
)
from feature_closure.test_support import (  # noqa: E402
    GIT_LIVE_BRANCH,
    GIT_PREFIX_BRANCH,
    GIT_REMOTE_NAME,
    GIT_UNKNOWN_REMOTE,
    RemoteRepositoryFixture,
    create_remote_repository,
    isolate_fixture_environment,
)


@pytest.fixture()
def remote_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> RemoteRepositoryFixture:
    """Expose one isolated local remote under machine-independent Git configuration."""
    isolate_fixture_environment(monkeypatch)
    return create_remote_repository(tmp_path / "closure")


class RemoteBranchPresenceTests:
    """Map an advertised, deleted, or unmatched remote ref to a domain presence value."""

    def test_probe_reports_a_branch_the_remote_still_advertises(
        self, remote_repository: RemoteRepositoryFixture
    ) -> None:
        probe = GitRemoteBranchProbe()

        assert probe.exists(remote_repository["remote_uri"], GIT_LIVE_BRANCH) is True

    def test_probe_reports_a_deleted_branch_as_absent(
        self, remote_repository: RemoteRepositoryFixture
    ) -> None:
        probe = GitRemoteBranchProbe()

        assert probe.exists(remote_repository["remote_uri"], remote_repository["removed_branch"]) is False

    def test_probe_queries_the_exact_ref_rather_than_a_prefix(
        self, remote_repository: RemoteRepositoryFixture
    ) -> None:
        probe = GitRemoteBranchProbe()

        assert probe.exists(remote_repository["remote_uri"], GIT_PREFIX_BRANCH) is False


class RemoteBoundaryFailureTests:
    """Report an unusable remote or missing executable as a boundary failure, never as absence."""

    def test_probe_reports_an_unknown_remote_as_a_boundary_failure(
        self, remote_repository: RemoteRepositoryFixture
    ) -> None:
        probe = GitRemoteBranchProbe()

        with pytest.raises(GitBoundaryError):
            probe.exists(GIT_UNKNOWN_REMOTE, GIT_LIVE_BRANCH)

    def test_probe_reports_a_missing_git_executable_as_a_boundary_failure(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(git_remote.shutil, "which", lambda name: None)

        with pytest.raises(GitBoundaryError):
            GitRemoteBranchProbe().exists(GIT_REMOTE_NAME, GIT_LIVE_BRANCH)
