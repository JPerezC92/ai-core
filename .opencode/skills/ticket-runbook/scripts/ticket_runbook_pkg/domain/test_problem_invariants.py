"""Unit tests that invalid register cells never become a Problem."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2]))
from ticket_runbook_pkg.domain._test_support import _ProblemData  # noqa: E402
from ticket_runbook_pkg.domain.entities import Problem  # noqa: E402
from ticket_runbook_pkg.domain.errors import (  # noqa: E402
    CODE_INVALID_ALLOW_EXACT,
    CODE_INVALID_LIFECYCLE,
    CODE_INVALID_STATUS,
    CODE_INVALID_TEAM,
    CODE_MISSING_SYMPTOM,
    DomainError,
)


class ProblemInvariantTests:
    @pytest.mark.parametrize(
        ("overrides", "code"),
        [
            ({"team": _ProblemData.INVALID_TEAM}, CODE_INVALID_TEAM),
            ({"lifecycle": _ProblemData.INVALID_LIFECYCLE}, CODE_INVALID_LIFECYCLE),
            (
                {"allow_exact": _ProblemData.INVALID_ALLOW_EXACT},
                CODE_INVALID_ALLOW_EXACT,
            ),
            ({"status": _ProblemData.INVALID_STATUS}, CODE_INVALID_STATUS),
            ({"symptom": _ProblemData.NO_SYMPTOM}, CODE_MISSING_SYMPTOM),
        ],
    )
    def test_invalid_cell_returns_domain_error(
        self, overrides: dict[str, str], code: str
    ) -> None:
        result = Problem.create(**_ProblemData.create(**overrides))
        assert isinstance(result, DomainError)
        assert result.code == code
