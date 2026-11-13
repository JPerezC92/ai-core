"""Record for the required YAML frontmatter fields of ``analysis/state.md``."""

from __future__ import annotations

from typing import TypedDict


class AnalysisHeader(TypedDict):
    """The seven required YAML frontmatter fields for ``analysis/state.md``."""

    Phase: str
    SLA_due: str
    Updated: str
    Hypotheses_outstanding: str
    Query_budget: str
    Identification_verdict: str
    Same_query_reruns: str
