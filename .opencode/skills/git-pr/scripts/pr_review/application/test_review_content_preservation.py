"""Specify protected baseline prose, test-item and finding-history preservation."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pr_review.application.validate_final_body import execute
from pr_review.domain.records import ReviewPreparationError
from pr_review.test_support import (
    HistoryChange, ProtectedChange, create_body, create_changed_history,
    create_findings_body, create_initial_review_body, create_metadata,
    create_protected_content_change,
)


def test_join_adds_evidence_and_ticks_without_changing_unrelated_prose() -> None:
    baseline = create_metadata(body=create_initial_review_body())
    body = create_body()
    result = execute(baseline=baseline, current=baseline, body=body)
    assert not isinstance(result, ReviewPreparationError)
    assert result.body == body


@pytest.mark.parametrize("change", ["summary", "item"])
def test_join_rejects_unauthorized_prose_or_test_item_change(change: ProtectedChange) -> None:
    baseline = create_metadata(body=create_initial_review_body())
    result = execute(baseline=baseline, current=baseline, body=create_protected_content_change(change))
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "BODY_INVALID"


@pytest.mark.parametrize("change", ["removed", "renumbered", "severity"])
def test_join_preserves_existing_finding_identity_and_severity(change: HistoryChange) -> None:
    baseline = create_metadata(body=create_findings_body())
    result = execute(baseline=baseline, current=baseline, body=create_changed_history(change))
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "BODY_INVALID"
