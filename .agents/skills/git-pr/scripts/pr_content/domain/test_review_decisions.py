"""Specify supplied decision shape and context checks without authentication claims."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pr_content.domain.review_decisions import parse_decisions
from pr_content.domain.records import ReviewPreparationError
from pr_content.test_support import DecisionDefect, create_invalid_decisions, create_metadata, create_review_decisions
from pr_content.test_support import create_followup_decisions, create_invalid_followup_decisions


def test_explicit_bound_decision_provenance_is_structurally_accepted() -> None:
    result = parse_decisions(create_review_decisions("na"), create_metadata())
    assert not isinstance(result, ReviewPreparationError)


@pytest.mark.parametrize("defect", ["head", "provenance"])
def test_unbound_or_incomplete_decisions_return_typed_failure(defect: DecisionDefect) -> None:
    result = parse_decisions(create_invalid_decisions(defect), create_metadata())
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "DECISIONS_INVALID"


def test_independent_followup_decision_retains_destination_and_provenance() -> None:
    supplied = create_followup_decisions()
    result = parse_decisions(supplied, create_metadata())
    assert not isinstance(result, ReviewPreparationError)
    assert len(result.debt) == len(supplied["debt"])
    for parsed, original in zip(result.debt, supplied["debt"]):
        assert parsed.target == original["target"]
        assert parsed.destination == original["destination"]
        assert parsed.evidence == original["evidence"]


def test_independent_followup_requires_supplied_provenance() -> None:
    result = parse_decisions(create_invalid_followup_decisions("provenance"), create_metadata())
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "DECISIONS_INVALID"
