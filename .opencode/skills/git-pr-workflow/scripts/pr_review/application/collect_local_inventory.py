"""Collect local Git inventory and delegate assembly to the existing snapshot operation."""

from __future__ import annotations

from attribution_scan.domain.records import Artifact, ChangedFile, Snapshot

from pr_review.application.prepare_local_snapshot import execute as prepare_snapshot
from pr_review.domain.ports import GitInventoryPort
from pr_review.domain.records import LocalInventory, ReviewPreparationError

HEAD_REVISION = "HEAD"


def execute(
    *, pr_number: int, base: str, draft: str, body: str, reader: GitInventoryPort
) -> Snapshot | ReviewPreparationError:
    """Assemble the local snapshot from local prose and read-only Git inventory."""
    head = reader.resolve_commit(HEAD_REVISION)
    if head is None:
        return ReviewPreparationError("GIT_REVISION_UNRESOLVED", "HEAD must resolve to a commit")
    resolved_base = reader.resolve_commit(base)
    if resolved_base is None:
        return ReviewPreparationError("GIT_REVISION_UNRESOLVED", f"base ref must resolve to a commit: {base}")
    ancestor = reader.merge_base(resolved_base, head)
    if ancestor is None:
        return ReviewPreparationError("GIT_MERGE_BASE_UNRESOLVED", "base ref and HEAD share no common ancestor")
    commits = reader.list_commits(ancestor, head)
    if not commits:
        return ReviewPreparationError("GIT_COMMIT_RANGE_EMPTY", "the commit range between base and HEAD is empty")
    paths = reader.list_changed_paths(ancestor, head)
    if not paths:
        return ReviewPreparationError("GIT_PATHS_EMPTY", "the commit range changes no path")
    deleted = set(reader.list_deleted_paths(ancestor, head))
    if not deleted <= set(paths):
        return ReviewPreparationError(
            "SNAPSHOT_PATHS_MISMATCH", "deleted paths must belong to the changed path inventory"
        )
    changed_files: list[ChangedFile] = [
        {"path": path, "content": "" if path in deleted else reader.read_file(head, path)}
        for path in paths
    ]
    commit_messages: list[Artifact] = [
        {"surface": "commit-message", "source": commit, "content": reader.read_message(commit)}
        for commit in commits
    ]
    inventory = LocalInventory(
        schema=1, pr_number=pr_number, head_sha=head, base=base,
        commit_messages=commit_messages, changed_files=changed_files,
    )
    return prepare_snapshot(draft=draft, body=body, inventory=inventory, exact_paths=list(paths))
