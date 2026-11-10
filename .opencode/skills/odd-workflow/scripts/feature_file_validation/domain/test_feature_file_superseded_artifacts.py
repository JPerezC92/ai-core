"""Test that the superseded completion-sheet artifacts are rejected."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from feature_file_validation.domain._test_support import (  # noqa: E402
    make_completion_section,
    make_feature_file,
    make_prose_section,
    make_requirement,
)
from feature_file_validation.domain.rules import validate_feature_file  # noqa: E402


def test_completion_section_is_reported() -> None:
    document = make_feature_file(extra_sections=(make_completion_section(),))

    findings = validate_feature_file(document)

    assert any(
        finding.startswith("feature-file-superseded-section:") for finding in findings
    )


def test_state_field_on_a_requirement_line_is_reported() -> None:
    entries = (
        make_requirement(1, tail=" State: satisfied"),
        make_requirement(2, ticked=False),
    )

    findings = validate_feature_file(make_feature_file(requirement_entries=entries))

    assert any(finding.startswith("feature-file-superseded-state:") for finding in findings)


def test_state_field_outside_a_requirement_line_is_not_reported() -> None:
    document = make_feature_file(
        extra_sections=(make_prose_section("State: a prose mention only."),)
    )

    findings = validate_feature_file(document)

    assert not any(
        finding.startswith("feature-file-superseded-state:") for finding in findings
    )


def test_current_format_carries_no_superseded_artifact() -> None:
    findings = validate_feature_file(make_feature_file())

    assert not any(finding.startswith("feature-file-superseded") for finding in findings)
