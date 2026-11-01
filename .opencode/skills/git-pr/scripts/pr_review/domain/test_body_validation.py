"""Specify title-wrapper extraction without rewriting unrelated Markdown."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pr_review.domain.body_validation import extract_body
from pr_review.domain.records import ReviewPreparationError
from pr_review.test_support import create_body, create_draft


def test_extracts_only_body_preserving_every_body_byte() -> None:
    assert extract_body(create_draft()) == create_body()


def test_body_only_input_is_not_silently_treated_as_a_creation_draft() -> None:
    result = extract_body(create_body())
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "DRAFT_INVALID"
