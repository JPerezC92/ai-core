"""Validate and scan immutable PR snapshots for approved attribution lines."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import TypedDict, cast


class AttributionPolicy(TypedDict):
    """The validated markers and identities used by the scanner."""

    schema: int
    self_excluded_file: str
    markers: list[str]
    identities: list[str]


class Artifact(TypedDict):
    """One complete PR or commit-message artifact."""

    surface: str
    source: str
    content: str


class ChangedFile(TypedDict):
    """One changed-file body in the immutable snapshot."""

    path: str
    content: str


class Snapshot(TypedDict):
    """The complete PR content snapshot evaluated by the scanner."""

    schema: int
    pr_number: int
    head_sha: str
    base: str
    artifacts: list[Artifact]
    changed_files: list[ChangedFile]


class Match(TypedDict):
    """A line-level attribution finding without source-text disclosure."""

    surface: str
    source: str | None
    path: str | None
    line: int
    marker: str
    identity: str


class Exclusion(TypedDict):
    """The one policy-file exclusion applied to changed-file bodies."""

    path: str
    reason: str


class ScanResult(TypedDict):
    """Deterministic scan metadata, findings, and applied exclusions."""

    pr_number: int
    head_sha: str
    base: str
    matches: list[Match]
    exclusions: list[Exclusion]


class PolicyValidationError(ValueError):
    """Raised when the supplied attribution policy is malformed."""


class SnapshotValidationError(ValueError):
    """Raised when the supplied PR snapshot is incomplete or malformed."""


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


def validate_policy(value: object) -> AttributionPolicy:
    """Validate a decoded policy without performing filesystem access."""
    if not isinstance(value, dict):
        raise PolicyValidationError("policy must be a JSON object")
    if type(value.get("schema")) is not int or value.get("schema") != 1:
        raise PolicyValidationError("policy schema must be 1")
    excluded = value.get("self_excluded_file")
    markers = value.get("markers")
    identities = value.get("identities")
    if not isinstance(excluded, str) or not excluded:
        raise PolicyValidationError("policy self_excluded_file must be a non-empty string")
    for name, entries in (("markers", markers), ("identities", identities)):
        if not _is_string_list(entries) or not entries:
            raise PolicyValidationError(f"policy {name} must be a non-empty string list")
        if any(not entry or entry != entry.strip() for entry in entries):
            raise PolicyValidationError(f"policy {name} entries must be non-empty and trimmed")
        normalized = [entry.casefold() for entry in entries]
        if len(set(normalized)) != len(normalized):
            raise PolicyValidationError(f"policy {name} entries must be unique ignoring case")
    return cast(AttributionPolicy, value)


def validate_snapshot(value: object) -> Snapshot:
    """Validate snapshot completeness and shape without performing IO."""
    if not isinstance(value, dict):
        raise SnapshotValidationError("snapshot must be a JSON object")
    if type(value.get("schema")) is not int or value.get("schema") != 1:
        raise SnapshotValidationError("snapshot schema must be 1")
    pr_number = value.get("pr_number")
    if type(pr_number) is not int or pr_number < 1:
        raise SnapshotValidationError("snapshot pr_number must be a positive integer")
    head_sha = value.get("head_sha")
    if not isinstance(head_sha, str) or re.fullmatch(r"[0-9a-fA-F]{7,64}", head_sha) is None:
        raise SnapshotValidationError("snapshot head_sha must contain 7 to 64 hexadecimal characters")
    base = value.get("base")
    if not isinstance(base, str) or not base.strip():
        raise SnapshotValidationError("snapshot base must be a non-empty string")

    artifacts = value.get("artifacts")
    if not isinstance(artifacts, list):
        raise SnapshotValidationError("snapshot artifacts must be a list")
    surfaces: dict[str, int] = {"pr-title": 0, "pr-body": 0, "commit-message": 0}
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise SnapshotValidationError("each artifact must be a JSON object")
        surface = artifact.get("surface")
        source = artifact.get("source")
        content = artifact.get("content")
        if not isinstance(surface, str) or surface not in surfaces:
            raise SnapshotValidationError("artifact surface must be pr-title, pr-body, or commit-message")
        if not isinstance(source, str) or not source.strip():
            raise SnapshotValidationError("artifact source must be a non-empty string")
        if not isinstance(content, str):
            raise SnapshotValidationError("artifact content must be a string")
        surfaces[cast(str, surface)] += 1
    if surfaces["pr-title"] != 1 or surfaces["pr-body"] != 1 or surfaces["commit-message"] < 1:
        raise SnapshotValidationError("snapshot requires one PR title, one PR body, and at least one commit message")

    changed_files = value.get("changed_files")
    if not isinstance(changed_files, list):
        raise SnapshotValidationError("snapshot changed_files must be a list")
    if not changed_files:
        raise SnapshotValidationError("snapshot requires at least one changed-file body")
    for changed_file in changed_files:
        if not isinstance(changed_file, dict):
            raise SnapshotValidationError("each changed file must be a JSON object")
        path = changed_file.get("path")
        content = changed_file.get("content")
        if not isinstance(path, str) or not path or not _is_root_relative_path(path):
            raise SnapshotValidationError(
                "changed-file path must be a non-empty root-relative path without parent traversal"
            )
        if not isinstance(content, str):
            raise SnapshotValidationError("changed-file content must be a string")
    return cast(Snapshot, value)


def _scan_content(
    content: str,
    surface: str,
    source: str | None,
    path: str | None,
    policy: AttributionPolicy,
) -> list[Match]:
    matches: list[Match] = []
    markers = [(item, item.casefold()) for item in policy["markers"]]
    identities = [(item, item.casefold()) for item in policy["identities"]]
    for line_number, raw_line in enumerate(content.splitlines(), start=1):
        normalized_line = raw_line.strip().casefold()
        matching_markers = [item for item in markers if normalized_line.startswith(item[1])]
        matching_identities = [item for item in identities if item[1] in normalized_line]
        for marker, _ in matching_markers:
            for identity, _ in matching_identities:
                matches.append(
                    {
                        "surface": surface,
                        "source": source,
                        "path": path,
                        "line": line_number,
                        "marker": marker,
                        "identity": identity,
                    }
                )
    return matches


def scan_attribution(snapshot_value: object, policy_value: object) -> ScanResult:
    """Return every approved same-line marker/identity match in a snapshot."""
    snapshot = validate_snapshot(snapshot_value)
    policy = validate_policy(policy_value)
    matches: list[Match] = []
    exclusions: list[Exclusion] = []
    for artifact in snapshot["artifacts"]:
        matches.extend(
            _scan_content(
                artifact["content"], artifact["surface"], artifact["source"], None, policy
            )
        )
    for changed_file in snapshot["changed_files"]:
        if changed_file["path"].replace("\\", "/") == policy["self_excluded_file"].replace("\\", "/"):
            exclusions.append(
                {"path": changed_file["path"], "reason": "policy self-exclusion"}
            )
            continue
        matches.extend(
            _scan_content(
                changed_file["content"], "changed-file", None, changed_file["path"], policy
            )
        )
    return {
        "pr_number": snapshot["pr_number"],
        "head_sha": snapshot["head_sha"],
        "base": snapshot["base"],
        "matches": matches,
        "exclusions": exclusions,
    }


def main(argv: list[str] | None = None) -> int:
    """Read CLI inputs, serialize the scan, and return the documented status."""
    parser = argparse.ArgumentParser(description="Scan a complete PR snapshot for approved attribution lines.")
    parser.add_argument("--policy", required=True, help="path to the approved attribution policy JSON")
    parser.add_argument("--snapshot", required=True, help="path to the immutable PR snapshot JSON")
    arguments = parser.parse_args(argv)
    try:
        policy_value = json.loads(Path(arguments.policy).read_text(encoding="utf-8"))
        snapshot_value = json.loads(Path(arguments.snapshot).read_text(encoding="utf-8"))
        result = scan_attribution(snapshot_value, policy_value)
    except OSError:
        print(json.dumps({"error": "unable to read input file"}, sort_keys=True))
        return 2
    except UnicodeError:
        print(json.dumps({"error": "input is not valid UTF-8"}, sort_keys=True))
        return 2
    except json.JSONDecodeError:
        print(json.dumps({"error": "input is not valid JSON"}, sort_keys=True))
        return 2
    except (PolicyValidationError, SnapshotValidationError) as error:
        print(json.dumps({"error": str(error)}, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 1 if result["matches"] else 0


if __name__ == "__main__":
    sys.exit(main())
