"""Factories for attribution scanner test data and policy-derived test lines."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Literal

from attribution_scan.domain.records import (
    Artifact,
    AttributionPolicy,
    ChangedFile,
    PolicyValidationError,
    Snapshot,
)
from attribution_scan.domain.validation import validate_policy


def load_approved_policy() -> AttributionPolicy | PolicyValidationError:
    """Load the checked-in policy as a test input, returning the validation result.

    File decoding stays in this factory; the validation itself stays IO-free, and a
    rejected policy is returned as a business-error value for callers to assert on.
    """
    policy_path = (
        Path(__file__).resolve().parent.parent
        / "references"
        / "_attribution-patterns.json"
    )
    return validate_policy(json.loads(policy_path.read_text(encoding="utf-8")))


def make_attribution_line(
    policy: AttributionPolicy,
    marker_index: int = 0,
    identity_index: int = 0,
) -> str:
    """Build a matching line from approved values without embedding policy text."""
    marker = policy["markers"][marker_index]
    identity = policy["identities"][identity_index]
    return f"{marker} {identity}"


def make_ordinary_identity_mention(policy: AttributionPolicy) -> str:
    """Build prose mentioning a policy identity without an attribution marker."""
    return f"Documentation mentions {policy['identities'][0]} here."


def make_multiline_matching_contents(policy: AttributionPolicy) -> tuple[str, str]:
    """Build artifact and file bodies with a matching line at known positions."""
    line = make_attribution_line(policy).swapcase()
    artifact_content = f"intro\n\n{line}"
    file_content = f"first\n{line}"
    return artifact_content, file_content


def make_changed_file(path: str = "README.md", content: str = "") -> ChangedFile:
    """Build one typed changed-file entry for a scanner snapshot."""
    return {"path": path, "content": content}


def make_changed_files(*entries: ChangedFile) -> list[ChangedFile]:
    """Collect changed-file entries without inline snapshot payloads in tests."""
    return list(entries)


def make_snapshot(
    *,
    changed_files: Sequence[ChangedFile] | None = None,
    artifact_content: tuple[str, str] | None = None,
) -> Snapshot:
    """Build a typed baseline snapshot for scanner tests."""
    artifacts: list[Artifact] = [
        {"surface": "pr-title", "source": "PR #80 title", "content": "Routine update"},
        {"surface": "pr-body", "source": "PR #80 body", "content": ""},
        {"surface": "commit-message", "source": "a" * 40, "content": "Routine update"},
    ]
    if artifact_content is not None:
        target_surface, content = artifact_content
        for artifact in artifacts:
            if artifact["surface"] == target_surface:
                artifact["content"] = content
                break

    snapshot: Snapshot = {
        "schema": 1,
        "pr_number": 80,
        "head_sha": "a" * 40,
        "base": "origin/main",
        "artifacts": artifacts,
        "changed_files": list(changed_files) if changed_files is not None else [],
    }
    return snapshot


def make_complete_snapshot() -> Snapshot:
    """Return a valid snapshot with one empty changed-file body."""
    return make_snapshot(changed_files=make_changed_files(make_changed_file()))


def make_snapshot_with_artifact_content(
    surface: Literal["pr-title", "pr-body", "commit-message"],
    content: str,
    *,
    changed_files: Sequence[ChangedFile] | None = None,
) -> Snapshot:
    """Build a snapshot with one selected artifact body replaced."""
    return make_snapshot(
        changed_files=changed_files,
        artifact_content=(surface, content),
    )


def make_snapshot_without_changed_files() -> Snapshot:
    """Build a structurally valid snapshot missing the required file body."""
    return make_snapshot(changed_files=())


def make_malformed_snapshot() -> dict[str, object]:
    """Build an intentionally malformed JSON object for input-validation checks."""
    return {"schema": 1}


def make_malformed_surface_snapshot() -> dict[str, object]:
    """Build a malformed JSON object with an unhashable artifact surface."""
    snapshot: dict[str, object] = dict(
        make_snapshot(changed_files=make_changed_files(make_changed_file()))
    )
    artifacts = snapshot["artifacts"]
    assert isinstance(artifacts, list)
    first_artifact: object = artifacts[0]
    assert isinstance(first_artifact, dict)
    first_artifact["surface"] = []
    return snapshot


def make_malformed_policy(
    policy: AttributionPolicy,
    empty_field: Literal["markers", "identities"] = "markers",
) -> dict[str, object]:
    """Build a malformed JSON policy object with one required list emptied."""
    malformed_policy: dict[str, object] = dict(policy)
    malformed_policy[empty_field] = []
    return malformed_policy


def invalid_paths() -> tuple[str, ...]:
    """Return empty, traversing, and absolute paths rejected by validation."""
    return ("", "../outside.py", "src/../../outside.py", "/absolute.py", r"C:\absolute.py")


def make_invalid_path_snapshot(path: str) -> Snapshot:
    """Build a complete snapshot carrying the requested invalid changed-file path."""
    return make_snapshot(
        changed_files=make_changed_files(make_changed_file(path=path))
    )


def write_json(path: Path, value: object) -> Path:
    """Write one JSON test input under the caller's temporary directory."""
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path
