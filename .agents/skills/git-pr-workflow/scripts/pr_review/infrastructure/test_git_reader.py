"""Specify local Git inventory reads through argv-only commands with no GitHub access."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pr_review.infrastructure import git_reader
from pr_review.infrastructure.git_reader import GitBoundaryError, GitReader, parse_status_entries
from pr_review.test_support import (
    GIT_METACHARACTER_PATH, GIT_RENAMED_FROM_PATH, GIT_RENAMED_TO_PATH, GIT_SIDE_EFFECT_NAME,
    GIT_SOURCE_PATH, GitOrphanFixture, GitRepositoryFixture, create_committed_repository,
    create_orphan_repository, create_truncated_status_payload, isolate_fixture_environment,
)


@pytest.fixture()
def committed_repository(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> GitRepositoryFixture:
    """Expose one isolated repository read under machine-independent Git configuration."""
    isolate_fixture_environment(monkeypatch)
    return create_committed_repository(tmp_path / "repository")


class GitReaderMappingTests:
    """Map real repository output into domain values without leaking raw records."""

    def test_reader_maps_commits_messages_and_a_deleted_path(self, committed_repository: GitRepositoryFixture) -> None:
        reader = GitReader(cwd=committed_repository["directory"])
        base = committed_repository["base"]
        head = committed_repository["head"]
        assert reader.resolve_commit("HEAD") == head
        assert reader.merge_base(base, head) == base
        assert reader.list_commits(base, head) == [head]
        assert reader.read_message(head) == committed_repository["message"]
        assert reader.list_changed_paths(base, head) == committed_repository["changed_paths"]
        assert reader.list_deleted_paths(base, head) == committed_repository["deleted_paths"]
        assert reader.read_file(head, GIT_SOURCE_PATH) == committed_repository["bodies"][GIT_SOURCE_PATH]

    def test_reader_maps_a_rename_to_its_destination_path(
        self, committed_repository: GitRepositoryFixture
    ) -> None:
        reader = GitReader(cwd=committed_repository["directory"])
        base = committed_repository["base"]
        head = committed_repository["head"]
        assert GIT_RENAMED_FROM_PATH not in reader.list_changed_paths(base, head)
        assert GIT_RENAMED_TO_PATH in reader.list_changed_paths(base, head)
        assert GIT_RENAMED_TO_PATH not in reader.list_deleted_paths(base, head)
        assert reader.read_file(head, GIT_RENAMED_TO_PATH) == committed_repository["bodies"][GIT_RENAMED_TO_PATH]

    def test_reader_reports_an_unresolvable_revision_as_absence(
        self, committed_repository: GitRepositoryFixture
    ) -> None:
        reader = GitReader(cwd=committed_repository["directory"])
        assert reader.resolve_commit("refs/heads/unresolved") is None


class GitReaderMergeBaseTests:
    """Report an absent common ancestor as absence rather than a resolved revision."""

    def test_reader_reports_a_disjoint_history_as_no_common_ancestor(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        isolate_fixture_environment(monkeypatch)
        orphan: GitOrphanFixture = create_orphan_repository(tmp_path / "orphan-repository")
        reader = GitReader(cwd=orphan["directory"])
        assert reader.resolve_commit(orphan["orphan_head"]) == orphan["orphan_head"]
        assert reader.merge_base(orphan["base"], orphan["orphan_head"]) is None


class GitReaderShellSafetyTests:
    """Read every committed path through argv, so no metacharacter becomes a command."""

    def test_reader_reads_a_metacharacter_path_without_a_side_effect(
        self, committed_repository: GitRepositoryFixture
    ) -> None:
        reader = GitReader(cwd=committed_repository["directory"])
        body = reader.read_file(committed_repository["head"], GIT_METACHARACTER_PATH)
        assert body == committed_repository["bodies"][GIT_METACHARACTER_PATH]
        assert not (Path(committed_repository["directory"]) / GIT_SIDE_EFFECT_NAME).exists()


class StatusEntryParsingTests:
    """Reject a truncated name-status payload instead of returning a partial path."""

    def test_truncated_rename_payload_is_a_boundary_failure(self) -> None:
        with pytest.raises(GitBoundaryError):
            parse_status_entries(create_truncated_status_payload())


class GitReaderFailureTests:
    """Report an unavailable or failing Git process as a boundary failure, never a business value."""

    def test_reader_reports_a_missing_git_executable_as_a_boundary_failure(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(git_reader.shutil, "which", lambda name: None)
        reader = GitReader()
        with pytest.raises(GitBoundaryError):
            reader.resolve_commit("HEAD")

    def test_reader_reports_a_missing_range_as_a_boundary_failure(
        self, committed_repository: GitRepositoryFixture
    ) -> None:
        reader = GitReader(cwd=committed_repository["directory"])
        with pytest.raises(GitBoundaryError):
            reader.list_commits(committed_repository["base"], "refs/heads/unresolved")
