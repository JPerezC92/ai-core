"""Specify local inventory collection that delegates assembly to the existing operation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Literal, TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pr_review.application.collect_local_inventory import execute
from pr_review.domain.records import ReviewPreparationError
from pr_review.test_support import (
    create_body, create_local_draft, create_local_snapshot, create_paths, create_snapshot,
)

HEAD_REVISION = "HEAD"
ANCESTOR_COMMIT = "b" * 40
RESOLVED_BASE_COMMIT = "c" * 40
InventoryDefect = Literal[
    "empty-range", "unresolved-base", "unresolved-head", "merge-base-unresolved",
    "no-paths", "path-set-mismatch",
]


class CollectionRequest(TypedDict):
    """Carry the typed command inputs every collection case shares."""

    pr_number: int
    base: str
    draft: str
    body: str


def create_request() -> CollectionRequest:
    """Build the command inputs from the shared review fixtures."""
    snapshot = create_snapshot()
    return {
        "pr_number": snapshot["pr_number"], "base": snapshot["base"],
        "draft": create_local_draft(), "body": create_body(),
    }


class RecordingReader:
    """Stand in for the Git port and record the ranges the operation requests."""

    def __init__(
        self,
        *,
        revisions: dict[str, str | None],
        merge_base: str | None,
        commits: list[str],
        changed_paths: list[str],
        deleted_paths: list[str],
        messages: dict[str, str],
        bodies: dict[str, str],
    ) -> None:
        self._revisions = revisions
        self._merge_base = merge_base
        self._commits = commits
        self._changed_paths = changed_paths
        self._deleted_paths = deleted_paths
        self._messages = messages
        self._bodies = bodies
        self.commit_ranges: list[tuple[str, str]] = []
        self.path_ranges: list[tuple[str, str]] = []
        self.merge_base_arguments: list[tuple[str, str]] = []

    def resolve_commit(self, revision: str) -> str | None:
        """Return the configured object id for a revision, or its configured absence."""
        return self._revisions[revision]

    def merge_base(self, first: str, second: str) -> str | None:
        """Return the configured common ancestor and record the supplied endpoints."""
        self.merge_base_arguments.append((first, second))
        return self._merge_base

    def list_commits(self, ancestor: str, head: str) -> list[str]:
        """Return the configured commit inventory and record the requested endpoints."""
        self.commit_ranges.append((ancestor, head))
        return list(self._commits)

    def read_message(self, commit: str) -> str:
        """Return the configured message for one commit."""
        return self._messages[commit]

    def list_changed_paths(self, ancestor: str, head: str) -> list[str]:
        """Return the configured exact path inventory and record the requested endpoints."""
        self.path_ranges.append((ancestor, head))
        return list(self._changed_paths)

    def list_deleted_paths(self, ancestor: str, head: str) -> list[str]:
        """Return the configured deleted-path inventory."""
        return list(self._deleted_paths)

    def read_file(self, commit: str, path: str) -> str:
        """Return the configured body; a deleted path stays absent on purpose."""
        return self._bodies[path]


def create_reader(defect: InventoryDefect | None = None) -> RecordingReader:
    """Build the port double from the shared fixtures, applying one named defect."""
    snapshot = create_snapshot()
    head = snapshot["head_sha"]
    base = snapshot["base"]
    changed_paths = create_paths()
    commit = snapshot["artifacts"][2]
    revisions: dict[str, str | None] = {HEAD_REVISION: head, base: RESOLVED_BASE_COMMIT}
    commits = [head]
    merge_base: str | None = ANCESTOR_COMMIT
    deleted_paths = [changed_paths[1]]
    messages = {commit["source"]: commit["content"]}
    bodies = {changed_paths[0]: snapshot["changed_files"][0]["content"]}
    if defect == "empty-range":
        commits = []
    elif defect == "unresolved-head":
        revisions[HEAD_REVISION] = None
    elif defect == "unresolved-base":
        revisions[base] = None
    elif defect == "merge-base-unresolved":
        merge_base = None
    elif defect == "no-paths":
        changed_paths = []
    elif defect == "path-set-mismatch":
        deleted_paths = ["src/unlisted.py"]
    return RecordingReader(
        revisions=revisions, merge_base=merge_base, commits=commits, changed_paths=changed_paths,
        deleted_paths=deleted_paths, messages=messages, bodies=bodies,
    )


class LocalInventoryCollectionTests:
    """Assemble the existing local snapshot from injected Git-derived values."""

    def test_collection_produces_the_local_snapshot_and_retains_the_deleted_path(self) -> None:
        reader = create_reader()
        result = execute(**create_request(), reader=reader)
        assert result == create_local_snapshot()
        head = create_snapshot()["head_sha"]
        assert reader.merge_base_arguments == [(RESOLVED_BASE_COMMIT, head)]
        expected_range = (ANCESTOR_COMMIT, head)
        assert reader.commit_ranges == [expected_range]
        assert reader.path_ranges == [expected_range]


class LocalInventoryRejectionTests:
    """Return a typed business rejection instead of an assembled snapshot."""

    def test_empty_commit_range_is_rejected(self) -> None:
        result = execute(**create_request(), reader=create_reader("empty-range"))
        assert isinstance(result, ReviewPreparationError)
        assert result.code == "GIT_COMMIT_RANGE_EMPTY"

    def test_unresolved_head_is_rejected(self) -> None:
        result = execute(**create_request(), reader=create_reader("unresolved-head"))
        assert isinstance(result, ReviewPreparationError)
        assert result.code == "GIT_REVISION_UNRESOLVED"

    def test_unresolved_base_ref_is_rejected(self) -> None:
        result = execute(**create_request(), reader=create_reader("unresolved-base"))
        assert isinstance(result, ReviewPreparationError)
        assert result.code == "GIT_REVISION_UNRESOLVED"

    def test_unresolved_merge_base_is_rejected(self) -> None:
        result = execute(**create_request(), reader=create_reader("merge-base-unresolved"))
        assert isinstance(result, ReviewPreparationError)
        assert result.code == "GIT_MERGE_BASE_UNRESOLVED"

    def test_empty_changed_path_list_is_rejected(self) -> None:
        result = execute(**create_request(), reader=create_reader("no-paths"))
        assert isinstance(result, ReviewPreparationError)
        assert result.code == "GIT_PATHS_EMPTY"

    def test_deleted_path_outside_the_changed_inventory_is_rejected(self) -> None:
        result = execute(**create_request(), reader=create_reader("path-set-mismatch"))
        assert isinstance(result, ReviewPreparationError)
        assert result.code == "SNAPSHOT_PATHS_MISMATCH"
