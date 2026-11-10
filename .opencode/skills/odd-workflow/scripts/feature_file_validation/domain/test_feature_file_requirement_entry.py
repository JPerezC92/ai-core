"""Test the requirement line shape and the exclusion of indented sublist lines."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from feature_file_validation.domain._test_support import (  # noqa: E402
    make_feature_file,
    make_indented_sublist,
    make_malformed_requirement,
    make_requirement,
    make_requirement_with_uppercase_tick,
    make_requirement_without_number,
)
from feature_file_validation.domain.rules import validate_feature_file  # noqa: E402


def test_requirement_line_without_the_dash_separator_is_reported() -> None:
    entries = (make_malformed_requirement(),)

    findings = validate_feature_file(make_feature_file(requirement_entries=entries))

    assert any(finding.startswith("feature-file-requirement-entry:") for finding in findings)


def test_requirement_line_without_a_number_is_reported() -> None:
    entries = (make_requirement_without_number(),)

    findings = validate_feature_file(make_feature_file(requirement_entries=entries))

    assert any(finding.startswith("feature-file-requirement-entry:") for finding in findings)


def test_requirement_line_with_an_uppercase_tick_is_reported() -> None:
    entries = (make_requirement_with_uppercase_tick(),)

    findings = validate_feature_file(make_feature_file(requirement_entries=entries))

    assert any(finding.startswith("feature-file-requirement-entry:") for finding in findings)


def test_indented_sublist_lines_are_not_requirement_lines() -> None:
    entries = (
        make_requirement(1),
        make_requirement(2, ticked=False),
        make_indented_sublist(),
    )

    findings = validate_feature_file(make_feature_file(requirement_entries=entries))

    assert not any(
        finding.startswith("feature-file-requirement-entry:") for finding in findings
    )


def test_well_formed_requirement_line_is_accepted() -> None:
    findings = validate_feature_file(make_feature_file())

    assert not any(
        finding.startswith("feature-file-requirement-entry:") for finding in findings
    )
