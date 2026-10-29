"""Identity-bearing domain model for the ticket-runbook problem register."""

from __future__ import annotations

from typing import TypedDict


class ProblemRow(TypedDict):
    """One parsed row of the ``knowledge/problems.md`` register."""

    id: str
    date: str
    team: str
    symptom: str
    system: str
    module: str
    problem: str
    discriminators: str
    exclusions: str
    evidence: str
    root_cause: str
    lifecycle: str
    allow_exact: str
    status: str
