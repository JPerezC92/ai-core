"""Specify every documented metadata rejection returns one typed failure code."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pr_content.domain.records import METADATA_FIELDS, ReviewPreparationError, parse_metadata
from pr_content.test_support import MetadataDefect, create_invalid_metadata, create_metadata


def test_documented_seven_field_metadata_parses_successfully() -> None:
    result = parse_metadata(create_metadata())
    assert not isinstance(result, ReviewPreparationError)
    assert sorted(result) == sorted(METADATA_FIELDS)


@pytest.mark.parametrize(
    "defect",
    [
        "non-object", "zero-number", "negative-number", "string-number",
        "short-head", "non-hex-head", "long-head", "not-open-state",
        "blank-base", "blank-head-ref", "blank-title",
        "non-string-title", "non-string-base", "non-string-head-ref",
        "non-string-state", "non-string-body",
        "missing-field",
    ],
)
def test_documented_metadata_rejection_returns_typed_failure(defect: MetadataDefect) -> None:
    result = parse_metadata(create_invalid_metadata(defect))
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "METADATA_INVALID"
