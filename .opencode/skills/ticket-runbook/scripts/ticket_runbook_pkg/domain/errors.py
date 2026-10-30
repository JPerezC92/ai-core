"""Typed ticket-runbook domain errors returned as values."""

from __future__ import annotations

from dataclasses import dataclass

CODE_INVALID_TEAM = "invalid_team"
CODE_INVALID_LIFECYCLE = "invalid_lifecycle"
CODE_INVALID_ALLOW_EXACT = "invalid_allow_exact"
CODE_INVALID_STATUS = "invalid_status"
CODE_MISSING_SYMPTOM = "missing_symptom_reference"
CODE_ILLEGAL_TRANSITION = "illegal_transition"


@dataclass(frozen=True)
class DomainError:
    """A business failure carried as a value with a stable code and a message."""

    code: str
    message: str
