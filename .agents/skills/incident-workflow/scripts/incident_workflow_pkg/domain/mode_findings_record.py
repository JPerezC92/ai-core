"""Record for the findings returned by one validation mode."""

from __future__ import annotations

from typing import TypedDict


class ModeFindings(TypedDict):
    """Findings returned by one validation mode: blocking violations and warnings."""

    violations: list[str]
    warnings: list[str]
