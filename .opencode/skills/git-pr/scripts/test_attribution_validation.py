"""Unit tests for attribution snapshot, policy, and path validation."""

from __future__ import annotations

import pytest

from attribution_testkit import (
    invalid_paths,
    load_approved_policy,
    make_complete_snapshot,
    make_invalid_path_snapshot,
    make_malformed_policy,
    make_malformed_snapshot,
    make_snapshot_without_changed_files,
)
from scan_attribution import (
    PolicyValidationError,
    SnapshotValidationError,
    scan_attribution,
)


POLICY = load_approved_policy()


def test_snapshot_requires_at_least_one_changed_file_body() -> None:
    with pytest.raises(SnapshotValidationError):
        scan_attribution(make_snapshot_without_changed_files(), POLICY)


@pytest.mark.parametrize("path", invalid_paths())
def test_snapshot_rejects_empty_absolute_and_traversal_paths(path: str) -> None:
    with pytest.raises(SnapshotValidationError):
        scan_attribution(make_invalid_path_snapshot(path), POLICY)


def test_malformed_snapshot_is_rejected() -> None:
    with pytest.raises(SnapshotValidationError):
        scan_attribution(make_malformed_snapshot(), POLICY)


def test_malformed_policy_is_rejected() -> None:
    invalid_policy = make_malformed_policy(POLICY, "identities")
    with pytest.raises(PolicyValidationError):
        scan_attribution(make_complete_snapshot(), invalid_policy)
