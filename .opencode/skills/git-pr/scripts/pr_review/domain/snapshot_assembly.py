"""Reconcile supplied complete scanner snapshots to exact owner-supplied paths."""

from attribution_scan.domain.records import Snapshot, SnapshotValidationError
from attribution_scan.domain.validation import validate_snapshot

from .records import LocalInventory, ReviewPreparationError


def validate_local_inventory(value: object) -> LocalInventory | ReviewPreparationError:
    """Validate unknown inventory and nested content through the scanner boundary."""
    error = ReviewPreparationError("SNAPSHOT_INVALID", "local immutable inventory required")
    keys = {"schema", "pr_number", "head_sha", "base", "commit_messages", "changed_files"}
    if not isinstance(value, dict) or set(value) != keys:
        return error
    commits = value["commit_messages"]
    if not isinstance(commits, list) or any(not isinstance(commit, dict) or commit.get("surface") != "commit-message" for commit in commits):
        return error
    validated = validate_snapshot({
        "schema": value["schema"], "pr_number": value["pr_number"],
        "head_sha": value["head_sha"], "base": value["base"],
        "artifacts": [
            {"surface": "pr-title", "source": "local title validation boundary", "content": ""},
            {"surface": "pr-body", "source": "local body validation boundary", "content": ""},
            *commits,
        ],
        "changed_files": value["changed_files"],
    })
    if isinstance(validated, SnapshotValidationError):
        return ReviewPreparationError("SNAPSHOT_INVALID", validated.message)
    return LocalInventory(
        schema=validated["schema"], pr_number=validated["pr_number"],
        head_sha=validated["head_sha"], base=validated["base"],
        commit_messages=validated["artifacts"][2:], changed_files=validated["changed_files"],
    )


def assemble_snapshot(collected: object, exact_paths: object) -> Snapshot | ReviewPreparationError:
    """Validate scanner shape and exact inventory, retaining deleted-file entries."""
    snapshot = validate_snapshot(collected)
    if isinstance(snapshot, SnapshotValidationError):
        return ReviewPreparationError("SNAPSHOT_INVALID", snapshot.message)
    if not isinstance(exact_paths, list) or not all(isinstance(path, str) for path in exact_paths):
        return ReviewPreparationError("SNAPSHOT_PATHS_MISMATCH", "path inventory must be a string list")
    paths = [entry["path"] for entry in snapshot["changed_files"]]
    if len(set(paths)) != len(paths) or len(set(exact_paths)) != len(exact_paths) or set(paths) != set(exact_paths):
        return ReviewPreparationError("SNAPSHOT_PATHS_MISMATCH", "snapshot paths must equal the exact diff inventory")
    return snapshot
