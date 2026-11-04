"""Application layer: pre-close readiness validation use case."""

from __future__ import annotations

from incident_workflow_pkg.domain.entities import Problem
from incident_workflow_pkg.domain.rules import (
    evaluate_pre_close,
)
from incident_workflow_pkg.domain.value_objects import (
    CloseOutSnapshot,
    ModeFindings,
)

__all__ = ["ValidatePreClose"]


class ValidatePreClose:
    """Pre-close readiness use case for the working and durable ticket set."""

    def execute(
        self,
        snapshot: CloseOutSnapshot,
        register_rows: list[Problem],
    ) -> ModeFindings:
        """Evaluate pre-collapse readiness from an already-loaded snapshot."""
        return {
            "violations": evaluate_pre_close(snapshot, register_rows),
            "warnings": [],
        }
