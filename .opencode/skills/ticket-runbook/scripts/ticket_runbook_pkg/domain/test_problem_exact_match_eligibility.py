"""Unit tests for Problem.is_exact_match_eligible."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))
from ticket_runbook_pkg.domain._test_support import _ProblemData  # noqa: E402


class ProblemExactMatchEligibilityTests:
    def test_active_allow_exact_is_exact_match_eligible(self) -> None:
        assert _ProblemData.entity().is_exact_match_eligible is True

    def test_active_without_allow_exact_is_not_exact_match_eligible(self) -> None:
        assert _ProblemData.entity(
            allow_exact=_ProblemData.ALLOW_EXACT_NO
        ).is_exact_match_eligible is False

    def test_non_active_allow_exact_is_not_exact_match_eligible(self) -> None:
        assert _ProblemData.entity(
            lifecycle=_ProblemData.LIFECYCLE_CANDIDATE
        ).is_exact_match_eligible is False
