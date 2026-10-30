"""Unit tests for Problem.activate."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))
from ticket_runbook_pkg.domain._test_support import _ProblemData  # noqa: E402
from ticket_runbook_pkg.domain.entities import (  # noqa: E402
    AllowExact,
    Lifecycle,
    Problem,
)
from ticket_runbook_pkg.domain.errors import (  # noqa: E402
    CODE_ILLEGAL_TRANSITION,
    DomainError,
)


class ProblemActivateTests:
    def test_candidate_returns_new_active_problem_without_mutating_original(
        self,
    ) -> None:
        old = _ProblemData.entity(
            lifecycle=_ProblemData.LIFECYCLE_CANDIDATE,
            allow_exact=_ProblemData.ALLOW_EXACT_NO,
        )
        new = old.activate()
        assert isinstance(new, Problem)
        assert new.id == old.id
        assert new.lifecycle is Lifecycle.ACTIVE
        assert new.allow_exact is AllowExact.YES
        assert old.lifecycle is Lifecycle.CANDIDATE
        assert old.allow_exact is AllowExact.NO
        assert old is not new

    @pytest.mark.parametrize(
        "lifecycle",
        [
            _ProblemData.LIFECYCLE,
            _ProblemData.LIFECYCLE_MITIGATED,
            _ProblemData.LIFECYCLE_RESOLVED,
            _ProblemData.LIFECYCLE_RETIRED,
        ],
    )
    def test_non_candidate_returns_illegal_transition(
        self, lifecycle: str
    ) -> None:
        problem = _ProblemData.entity(lifecycle=lifecycle)
        original = problem.lifecycle
        result = problem.activate()
        assert isinstance(result, DomainError)
        assert result.code == CODE_ILLEGAL_TRANSITION
        assert result.message == problem.id
        assert problem.lifecycle is original
