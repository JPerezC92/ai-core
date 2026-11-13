"""Integration coverage for loading the relocated diagnostic problem register."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))
from _incident_workflow_testkit import _register, _row  # noqa: E402
from incident_workflow_pkg.entry import load_register_rows  # noqa: E402


@pytest.fixture
def populated_register() -> str:
    """Build a valid incident register through the shared register factories."""
    return _register(
        _row(
            id="P-001",
            date="2026-01-01",
            team="incident",
            symptom="S-05",
            system="fixture-system",
            module="fixture-module",
            problem="fixture problem",
            discriminators="host=fixture",
            exclusions="host=excluded",
            evidence="log:42",
            root_cause="fixture cause",
            lifecycle="active",
            allow_exact="yes",
            status="open",
        )
    )


def test_load_register_rows_reads_relocated_register(
    tmp_path: Path, populated_register: str
) -> None:
    register_path = tmp_path / ".aicore" / "core" / "knowledge" / "diagnostics" / "problems.md"
    register_path.parent.mkdir(parents=True)
    register_path.write_text(populated_register, encoding="utf-8")

    rows = load_register_rows(tmp_path)

    assert len(rows) == 1
    assert rows[0].id == "P-001"
    assert rows[0].symptom == "S-05"
    assert rows[0].system == "fixture-system"
    assert rows[0].is_exact_match_eligible


def test_load_register_rows_empty_relocated_register(tmp_path: Path) -> None:
    register_path = tmp_path / ".aicore" / "core" / "knowledge" / "diagnostics" / "problems.md"
    register_path.parent.mkdir(parents=True)
    register_path.write_text(_register(), encoding="utf-8")

    assert load_register_rows(tmp_path) == []


def test_load_register_rows_missing_register(tmp_path: Path) -> None:
    assert load_register_rows(tmp_path) == []
