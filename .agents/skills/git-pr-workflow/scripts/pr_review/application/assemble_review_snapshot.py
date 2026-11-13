"""Prepare a complete scanner-compatible snapshot from already collected inputs."""

from attribution_scan.domain.records import Snapshot

from pr_review.domain.records import ReviewPreparationError
from pr_review.domain.snapshot_assembly import assemble_snapshot


def execute(*, collected: object, exact_paths: object) -> Snapshot | ReviewPreparationError:
    """Reconcile supplied data without collecting Git or GitHub state."""
    return assemble_snapshot(collected, exact_paths)
