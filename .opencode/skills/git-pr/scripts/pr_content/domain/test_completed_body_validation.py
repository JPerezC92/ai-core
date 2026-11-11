"""Specify malformed completed-body rejection without boundary exceptions."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pr_content.domain.body_validation import validate_body
from pr_content.domain.records import ReviewPreparationError
from pr_content.test_support import create_metadata, create_truncated_evidence_body


def test_heading_without_section_content_returns_error_instead_of_index_error() -> None:
    result = validate_body(create_truncated_evidence_body(), create_metadata())
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "BODY_INVALID"
