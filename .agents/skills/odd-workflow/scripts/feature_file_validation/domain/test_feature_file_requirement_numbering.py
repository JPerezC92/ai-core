"""Test that requirement numbers run consecutively from one without duplicates."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from feature_file_validation.domain._test_support import (  # noqa: E402
    make_feature_file,
    make_requirement,
)
from feature_file_validation.domain.rules import validate_feature_file  # noqa: E402


def test_gap_in_requirement_numbers_is_reported() -> None:
    entries = (make_requirement(1), make_requirement(3, ticked=False))

    findings = validate_feature_file(make_feature_file(requirement_entries=entries))

    assert any(
        finding.startswith("feature-file-requirement-numbering:") for finding in findings
    )


def test_duplicate_requirement_number_is_reported() -> None:
    entries = (make_requirement(1), make_requirement(1, ticked=False))

    findings = validate_feature_file(make_feature_file(requirement_entries=entries))

    assert any(
        finding.startswith("feature-file-requirement-numbering:") for finding in findings
    )


def test_consecutive_requirement_numbers_are_accepted() -> None:
    findings = validate_feature_file(make_feature_file())

    assert not any(
        finding.startswith("feature-file-requirement-numbering:") for finding in findings
    )
