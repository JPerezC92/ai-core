"""Unit tests for Problem.is_incident."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))
from ticket_runbook_pkg.domain._test_support import _ProblemData  # noqa: E402


class ProblemIncidentTests:
    def test_incident_team_is_incident(self) -> None:
        assert _ProblemData.entity().is_incident is True

    def test_dev_team_is_not_incident(self) -> None:
        assert _ProblemData.entity(team=_ProblemData.TEAM_DEV).is_incident is False
