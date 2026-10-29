"""Value-object domain records for ticket-runbook header, identification, close-out, and findings."""

from __future__ import annotations

from typing import Optional, TypedDict


class AnalysisHeader(TypedDict):
    """The seven required YAML frontmatter fields for ``analysis/state.md``."""

    Phase: str
    SLA_due: str
    Updated: str
    Hypotheses_outstanding: str
    Query_budget: str
    Identification_verdict: str
    Same_query_reruns: str


class TicketIdentification(TypedDict):
    """The identification fields parsed from a ``ticket_<id>.md`` record."""

    symptom_ids: list[str]
    known_problem_ids: list[str]
    identification_verdict: str


class CloseOutSnapshot(TypedDict):
    """Filesystem values required to evaluate pre-close and close-out sets."""

    ticket_file_names: list[str]
    ticket_content: Optional[str]
    working_analysis_files: list[str]
    analysis_contents: dict[str, str]
    response_draft_present: bool
    screenshots_dir_present: bool
    validations_dir_present: bool
    missing_image_paths: list[str]
    missing_ticket_paths: list[str]
    unsafe_ticket_paths: list[str]


class ModeFindings(TypedDict):
    """Findings returned by one validation mode: blocking violations and warnings."""

    violations: list[str]
    warnings: list[str]
