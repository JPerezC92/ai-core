"""Specify structural body evidence checks, not evidence-truth certification."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pr_review.application.validate_final_body import execute
from pr_review.domain.records import ReviewPreparationError
from pr_review.test_support import (
    BodyDefect, create_body, create_draft, create_invalid_body, create_metadata,
    FindingStatus, create_findings_body, create_initial_review_body,
    create_pipe_item_body,
)


def test_unchanged_remote_accepts_body_only_candidate_without_rewriting_it() -> None:
    body = create_body()
    result = execute(baseline=create_metadata(), current=create_metadata(), body=body)
    assert not isinstance(result, ReviewPreparationError)
    assert result.body == body


def test_title_wrapper_is_never_an_upload_candidate() -> None:
    result = execute(baseline=create_metadata(), current=create_metadata(), body=create_draft())
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "BODY_INVALID"


@pytest.mark.parametrize("defect", ["missing-row", "duplicate-row", "unchecked", "wrong-head", "changed-item"])
def test_structurally_invalid_passing_evidence_is_rejected(defect: BodyDefect) -> None:
    body = create_invalid_body(defect)
    result = execute(baseline=create_metadata(), current=create_metadata(), body=body)
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "BODY_INVALID"


@pytest.mark.parametrize("status", ["FIXED", "REJECTED"])
def test_completed_review_accepts_closed_canonical_findings(status: FindingStatus) -> None:
    baseline = create_metadata(body=create_initial_review_body())
    body = create_findings_body(status)
    result = execute(baseline=baseline, current=baseline, body=body)
    assert not isinstance(result, ReviewPreparationError)
    assert result.body == body


@pytest.mark.parametrize("status", ["OPEN", "IN PROGRESS", "DEFERRED"])
def test_pass_body_rejects_unresolved_finding_rows(status: FindingStatus) -> None:
    baseline = create_metadata(body=create_initial_review_body())
    result = execute(baseline=baseline, current=baseline, body=create_findings_body(status))
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "BODY_INVALID"


def test_escaped_table_pipe_matches_literal_checkbox_without_rewriting_body() -> None:
    body = create_pipe_item_body()
    baseline = create_metadata(body=body)
    result = execute(baseline=baseline, current=baseline, body=body)
    assert not isinstance(result, ReviewPreparationError)
    assert result.body == body


def test_escaped_pipe_does_not_allow_a_genuinely_different_evidence_key() -> None:
    baseline = create_metadata(body=create_pipe_item_body())
    result = execute(baseline=baseline, current=baseline, body=create_pipe_item_body(mismatched=True))
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "BODY_INVALID"
