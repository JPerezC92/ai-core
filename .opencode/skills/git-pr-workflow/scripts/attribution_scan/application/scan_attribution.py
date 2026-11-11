"""Execute the attribution scan over decoded snapshot and policy inputs."""

from attribution_scan.domain.matching import scan_validated_snapshot
from attribution_scan.domain.records import (
    PolicyValidationError,
    ScanInput,
    ScanResult,
    SnapshotValidationError,
)
from attribution_scan.domain.validation import validate_policy, validate_snapshot


def execute(command: ScanInput) -> ScanResult | PolicyValidationError | SnapshotValidationError:
    """Validate the snapshot before the policy, then scan the validated snapshot."""
    snapshot = validate_snapshot(command.snapshot_value)
    if isinstance(snapshot, SnapshotValidationError):
        return snapshot
    policy = validate_policy(command.policy_value)
    if isinstance(policy, PolicyValidationError):
        return policy
    return scan_validated_snapshot(snapshot, policy)
