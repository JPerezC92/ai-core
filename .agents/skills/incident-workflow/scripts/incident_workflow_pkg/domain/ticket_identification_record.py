"""Record for the identification fields parsed from a ``ticket_<id>.md`` record."""

from __future__ import annotations

from typing import TypedDict


class TicketIdentification(TypedDict):
    """The identification fields parsed from a ``ticket_<id>.md`` record."""

    symptom_ids: list[str]
    known_problem_ids: list[str]
    identification_verdict: str
