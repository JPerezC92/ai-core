"""Unit tests for Problem.is_matchable."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))
from ticket_runbook_pkg.domain._test_support import _ProblemData  # noqa: E402


class ProblemMatchableTests:
    def test_candidate_active_mitigated_are_matchable(self) -> None:
        assert _ProblemData.entity(
            lifecycle=_ProblemData.LIFECYCLE_CANDIDATE
        ).is_matchable is True
        assert _ProblemData.entity().is_matchable is True
        assert _ProblemData.entity(
            lifecycle=_ProblemData.LIFECYCLE_MITIGATED
        ).is_matchable is True

    def test_resolved_and_retired_are_not_matchable(self) -> None:
        assert _ProblemData.entity(
            lifecycle=_ProblemData.LIFECYCLE_RESOLVED
        ).is_matchable is False
        assert _ProblemData.entity(
            lifecycle=_ProblemData.LIFECYCLE_RETIRED
        ).is_matchable is False
