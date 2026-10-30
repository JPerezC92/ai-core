"""Structure and placeholder tests for ODD feature documents."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from feature_testkit import make_feature  # noqa: E402
from feature_validation.domain.rules import validate_feature  # noqa: E402


def test_valid_document_has_no_findings() -> None:
    assert validate_feature(make_feature()) == []


@pytest.mark.parametrize("field", ("status", "owner", "created"))
def test_missing_required_header_is_rejected(field: str) -> None:
    options = {
        "status": {"include_status": False},
        "owner": {"include_owner": False},
        "created": {"include_created": False},
    }
    findings = validate_feature(make_feature(**options[field]))
    assert any(f"header must include {field.title()}" in finding for finding in findings)


@pytest.mark.parametrize(
    ("heading", "expected"),
    (("specs_heading", "## Specs"), ("tasks_heading", "## Tasks"), ("log_heading", "## Log")),
)
def test_missing_required_section_is_rejected(heading: str, expected: str) -> None:
    findings = validate_feature(make_feature(**{heading: "## Missing"}))
    assert any(expected in finding for finding in findings)


def test_missing_l1_is_rejected() -> None:
    findings = validate_feature(make_feature(log_entries=("- L2 — later",)))
    assert any("L1" in finding for finding in findings)


def test_missing_spec_entry_is_rejected() -> None:
    findings = validate_feature(make_feature(spec_entries=("- a requirement",)))
    assert any("S#" in finding for finding in findings)


def test_invalid_task_structure_is_rejected() -> None:
    findings = validate_feature(make_feature(task_entries=("- T1 | S1 | route | commit: pending",)))
    assert any("Tasks entry" in finding for finding in findings)


def test_invalid_task_status_is_rejected() -> None:
    findings = validate_feature(
        make_feature(task_entries=("- T1 | S1 | route | blocked | commit: pending",))
    )
    assert any("open|in progress|done" in finding for finding in findings)


def test_multiple_spec_references_are_accepted() -> None:
    document = make_feature(task_entries=("- T1 | S1, S2 | route | open | commit: pending",))
    assert validate_feature(document) == []
