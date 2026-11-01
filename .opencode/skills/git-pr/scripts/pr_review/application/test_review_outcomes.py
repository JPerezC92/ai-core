"""Specify existing release outcomes with explicit owner-supplied decisions."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pr_review.application.validate_final_body import execute
from pr_review.domain.records import ReviewPreparationError
from pr_review.test_support import (
    OutcomeKind, create_initial_review_body, create_metadata, create_outcome_body, create_review_decisions,
    FollowupDefect, create_followup_body, create_followup_decisions, create_invalid_followup_decisions,
)


@pytest.mark.parametrize("kind", ["na", "advisory", "debt"])
def test_completed_outcome_accepts_explicit_bound_decisions(kind: OutcomeKind) -> None:
    baseline = create_metadata(body=create_initial_review_body())
    body = create_outcome_body(kind)
    result = execute(baseline=baseline, current=baseline, body=body,
                     decisions=create_review_decisions(kind))
    assert not isinstance(result, ReviewPreparationError)
    assert result.body == body


@pytest.mark.parametrize("kind", ["na", "advisory", "debt"])
def test_outcome_without_required_decision_is_rejected(kind: OutcomeKind) -> None:
    baseline = create_metadata(body=create_initial_review_body())
    result = execute(baseline=baseline, current=baseline, body=create_outcome_body(kind),
                     decisions=create_review_decisions())
    assert isinstance(result, ReviewPreparationError)


def test_deferred_finding_requires_debt_authority_not_release_acceptance_alone() -> None:
    baseline = create_metadata(body=create_initial_review_body())
    result = execute(baseline=baseline, current=baseline, body=create_outcome_body("debt"),
                     decisions=create_review_decisions("advisory"))
    assert isinstance(result, ReviewPreparationError)


@pytest.mark.parametrize("advisory", [False, True])
def test_independently_authorized_followup_preserves_completed_outcome(advisory: bool) -> None:
    baseline = create_metadata(body=create_initial_review_body())
    body = create_followup_body(advisory=advisory)
    result = execute(baseline=baseline, current=baseline, body=body,
                     decisions=create_followup_decisions(advisory=advisory))
    assert not isinstance(result, ReviewPreparationError)
    assert result.body == body


@pytest.mark.parametrize("defect", ["missing", "target", "destination", "provenance"])
def test_followup_without_matching_complete_authority_is_rejected(defect: FollowupDefect) -> None:
    baseline = create_metadata(body=create_initial_review_body())
    result = execute(baseline=baseline, current=baseline, body=create_followup_body(),
                     decisions=create_invalid_followup_decisions(defect))
    assert isinstance(result, ReviewPreparationError)
