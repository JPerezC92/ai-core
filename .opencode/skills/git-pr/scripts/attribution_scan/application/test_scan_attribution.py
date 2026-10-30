"""Test attribution scanning outcomes for decoded inputs without filesystem IO."""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPTS))

from attribution_testkit import (  # noqa: E402
    make_complete_snapshot,
    make_malformed_policy,
    make_malformed_snapshot,
)
from attribution_scan.application.scan_attribution import execute  # noqa: E402
from attribution_scan.domain.records import (  # noqa: E402
    AttributionPolicy,
    PolicyValidationError,
    ScanInput,
    SnapshotValidationError,
)


def create_policy() -> AttributionPolicy:
    """Build synthetic validation data without reading the approved policy."""
    return {
        "schema": 1,
        "self_excluded_file": "policy.json",
        "markers": ["Synthetic attribution:"],
        "identities": ["Synthetic author"],
    }


def create(
    *, malformed_snapshot: bool = False, malformed_policy: bool = False
) -> ScanInput:
    """Build a decoded-input command through IO-free shared factories."""
    policy = create_policy()
    return ScanInput(
        snapshot_value=(
            make_malformed_snapshot() if malformed_snapshot else make_complete_snapshot()
        ),
        policy_value=make_malformed_policy(policy) if malformed_policy else policy,
    )


def test_malformed_snapshot_returns_typed_error_with_original_message() -> None:
    result = execute(create(malformed_snapshot=True))

    assert isinstance(result, SnapshotValidationError)
    assert result.code == "SNAPSHOT_INVALID"
    assert result.message == "snapshot pr_number must be a positive integer"


def test_malformed_policy_returns_typed_error_with_original_message() -> None:
    result = execute(create(malformed_policy=True))

    assert isinstance(result, PolicyValidationError)
    assert result.code == "POLICY_INVALID"
    assert result.message == "policy markers must be a non-empty string list"


def test_snapshot_validation_precedes_policy_validation() -> None:
    result = execute(create(malformed_snapshot=True, malformed_policy=True))

    assert isinstance(result, SnapshotValidationError)
    assert result.code == "SNAPSHOT_INVALID"
    assert result.message == "snapshot pr_number must be a positive integer"


def test_complete_clean_inputs_return_scan_metadata_without_matches() -> None:
    result = execute(create())

    assert not isinstance(result, (PolicyValidationError, SnapshotValidationError))
    assert result == {
        "pr_number": 80,
        "head_sha": "a" * 40,
        "base": "origin/main",
        "matches": [],
        "exclusions": [],
    }
