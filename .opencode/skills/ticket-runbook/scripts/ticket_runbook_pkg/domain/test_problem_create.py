"""Unit tests for valid Problem.create identity and read-only accessors."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))
from ticket_runbook_pkg.domain._test_support import _ProblemData  # noqa: E402
from ticket_runbook_pkg.domain.entities import (  # noqa: E402
    AllowExact,
    Lifecycle,
    Problem,
    Status,
    Team,
)


class ProblemCreateTests:
    def test_valid_cells_return_problem_with_identity(self) -> None:
        result = Problem.create(**_ProblemData.create())
        assert isinstance(result, Problem)
        assert result.id == _ProblemData.ID
        assert result.team is Team.INCIDENT
        assert result.lifecycle is Lifecycle.ACTIVE
        assert result.allow_exact is AllowExact.YES
        assert result.status is Status.OPEN
        assert result.symptom == _ProblemData.SYMPTOM

    def test_identity_accessor_has_no_setter(self) -> None:
        result = Problem.create(**_ProblemData.create())
        assert isinstance(result, Problem)
        assert type(result).id.fset is None
