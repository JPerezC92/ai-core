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


def test_ascending_log_identifiers_are_accepted() -> None:
    document = make_feature(log_entries=("- L1 — original request", "- L2 — later request"))
    assert validate_feature(document) == []


def test_descending_log_identifiers_are_rejected() -> None:
    findings = validate_feature(
        make_feature(
            log_entries=("- L1 — original request", "- L3 — third", "- L2 — second")
        )
    )
    assert findings == ["Log entry identifiers must ascend strictly: L2 follows L3"]


def test_multiple_descending_log_identifiers_report_only_the_first_inversion() -> None:
    findings = validate_feature(
        make_feature(
            log_entries=("- L1 — a", "- L4 — b", "- L3 — c", "- L2 — d")
        )
    )
    assert findings == ["Log entry identifiers must ascend strictly: L3 follows L4"]


def test_repeated_log_identifier_is_rejected() -> None:
    findings = validate_feature(
        make_feature(
            log_entries=("- L1 — original request", "- L2 — later", "- L2 — repeated")
        )
    )
    assert findings == [
        "Log entry identifiers must ascend strictly: L2 follows L2",
        "Log entry identifier must be unique: L2 appears more than once",
    ]


def test_malformed_log_identifier_is_reported_not_raised() -> None:
    findings = validate_feature(
        make_feature(log_entries=("- L1 — a", "- L" + "9" * 5000 + " — huge"))
    )
    assert findings == [
        f"Log entry identifier is not a valid L number: - L{'9' * 5000} — huge"
    ]


def test_fenced_log_block_is_not_parsed_as_log_entries() -> None:
    document = make_feature(
        log_entries=(
            "- L1 — original request",
            "```markdown",
            "- L0 — sample line",
            "```",
        )
    )
    assert validate_feature(document) == []


def test_first_log_identifier_must_be_l1() -> None:
    findings = validate_feature(make_feature(log_entries=("- L2 — later",)))
    assert any("first Log entry must be L1" in finding for finding in findings)


def test_empty_log_section_reports_only_the_missing_l1_finding() -> None:
    findings = validate_feature(make_feature(log_entries=()))
    assert findings == ["Log needs an L1 entry"]


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
