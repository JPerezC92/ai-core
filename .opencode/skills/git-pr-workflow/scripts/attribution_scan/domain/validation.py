"""Validate decoded attribution inputs with returned business-error values."""

import re
from pathlib import PurePosixPath, PureWindowsPath
from typing import cast

from .records import (
    AttributionPolicy,
    PolicyValidationError,
    Snapshot,
    SnapshotValidationError,
)


def _is_string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _is_root_relative_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    windows_path = PureWindowsPath(path)
    return (
        not PurePosixPath(normalized).is_absolute()
        and not windows_path.is_absolute()
        and not windows_path.drive
        and ".." not in normalized.split("/")
    )


def validate_policy(value: object) -> AttributionPolicy | PolicyValidationError:
    """Validate a decoded policy without performing filesystem access."""
    if not isinstance(value, dict):
        return PolicyValidationError("policy must be a JSON object")
    if type(value.get("schema")) is not int or value.get("schema") != 1:
        return PolicyValidationError("policy schema must be 1")
    excluded = value.get("self_excluded_file")
    markers = value.get("markers")
    identities = value.get("identities")
    if not isinstance(excluded, str) or not excluded:
        return PolicyValidationError("policy self_excluded_file must be a non-empty string")
    for name, entries in (("markers", markers), ("identities", identities)):
        if not _is_string_list(entries) or not entries:
            return PolicyValidationError(f"policy {name} must be a non-empty string list")
        if any(not entry or entry != entry.strip() for entry in entries):
            return PolicyValidationError(f"policy {name} entries must be non-empty and trimmed")
        normalized = [entry.casefold() for entry in entries]
        if len(set(normalized)) != len(normalized):
            return PolicyValidationError(f"policy {name} entries must be unique ignoring case")
    return cast(AttributionPolicy, value)


def validate_snapshot(value: object) -> Snapshot | SnapshotValidationError:
    """Validate snapshot completeness and shape without performing IO."""
    if not isinstance(value, dict):
        return SnapshotValidationError("snapshot must be a JSON object")
    if type(value.get("schema")) is not int or value.get("schema") != 1:
        return SnapshotValidationError("snapshot schema must be 1")
    pr_number = value.get("pr_number")
    if type(pr_number) is not int or pr_number < 1:
        return SnapshotValidationError("snapshot pr_number must be a positive integer")
    head_sha = value.get("head_sha")
    if not isinstance(head_sha, str) or re.fullmatch(r"[0-9a-fA-F]{7,64}", head_sha) is None:
        return SnapshotValidationError("snapshot head_sha must contain 7 to 64 hexadecimal characters")
    base = value.get("base")
    if not isinstance(base, str) or not base.strip():
        return SnapshotValidationError("snapshot base must be a non-empty string")

    artifacts = value.get("artifacts")
    if not isinstance(artifacts, list):
        return SnapshotValidationError("snapshot artifacts must be a list")
    surfaces: dict[str, int] = {"pr-title": 0, "pr-body": 0, "commit-message": 0}
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            return SnapshotValidationError("each artifact must be a JSON object")
        surface = artifact.get("surface")
        source = artifact.get("source")
        content = artifact.get("content")
        if not isinstance(surface, str) or surface not in surfaces:
            return SnapshotValidationError("artifact surface must be pr-title, pr-body, or commit-message")
        if not isinstance(source, str) or not source.strip():
            return SnapshotValidationError("artifact source must be a non-empty string")
        if not isinstance(content, str):
            return SnapshotValidationError("artifact content must be a string")
        surfaces[cast(str, surface)] += 1
    if surfaces["pr-title"] != 1 or surfaces["pr-body"] != 1 or surfaces["commit-message"] < 1:
        return SnapshotValidationError("snapshot requires one PR title, one PR body, and at least one commit message")

    changed_files = value.get("changed_files")
    if not isinstance(changed_files, list):
        return SnapshotValidationError("snapshot changed_files must be a list")
    if not changed_files:
        return SnapshotValidationError("snapshot requires at least one changed-file body")
    for changed_file in changed_files:
        if not isinstance(changed_file, dict):
            return SnapshotValidationError("each changed file must be a JSON object")
        path = changed_file.get("path")
        content = changed_file.get("content")
        if not isinstance(path, str) or not path or not _is_root_relative_path(path):
            return SnapshotValidationError(
                "changed-file path must be a non-empty root-relative path without parent traversal"
            )
        if not isinstance(content, str):
            return SnapshotValidationError("changed-file content must be a string")
    return cast(Snapshot, value)
