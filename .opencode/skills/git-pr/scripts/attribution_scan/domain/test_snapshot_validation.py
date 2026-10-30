"""Test snapshot completeness and changed-file path validation as returned errors."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPTS))

from attribution_testkit import (  # noqa: E402
    invalid_paths,
    make_invalid_path_snapshot,
    make_malformed_snapshot,
    make_snapshot_without_changed_files,
)
from attribution_scan.domain.records import SnapshotValidationError  # noqa: E402
from attribution_scan.domain.validation import validate_snapshot  # noqa: E402


def test_snapshot_requires_at_least_one_changed_file_body() -> None:
    result = validate_snapshot(make_snapshot_without_changed_files())

    assert isinstance(result, SnapshotValidationError)
    assert result.code == "SNAPSHOT_INVALID"
    assert result.message == "snapshot requires at least one changed-file body"


@pytest.mark.parametrize("path", invalid_paths())
def test_snapshot_rejects_empty_absolute_and_traversal_paths(path: str) -> None:
    result = validate_snapshot(make_invalid_path_snapshot(path))

    assert isinstance(result, SnapshotValidationError)
    assert result.code == "SNAPSHOT_INVALID"
    assert result.message == (
        "changed-file path must be a non-empty root-relative path without parent traversal"
    )


def test_malformed_snapshot_is_rejected() -> None:
    result = validate_snapshot(make_malformed_snapshot())

    assert isinstance(result, SnapshotValidationError)
    assert result.code == "SNAPSHOT_INVALID"
    assert result.message == "snapshot pr_number must be a positive integer"
