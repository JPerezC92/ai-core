"""Test the requirements section and its minimum of one requirement line."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from feature_file_validation.domain._test_support import (  # noqa: E402
    make_feature_file,
    make_requirement,
    make_requirements_section,
)
from feature_file_validation.domain.rules import validate_feature_file  # noqa: E402


def test_missing_requirements_section_is_reported() -> None:
    findings = validate_feature_file(make_feature_file(requirements_heading="## Other"))

    assert any(finding.startswith("feature-file-requirements:") for finding in findings)


def test_requirements_section_without_a_requirement_line_is_reported() -> None:
    findings = validate_feature_file(make_feature_file(requirement_entries=()))

    assert any(finding.startswith("feature-file-requirements:") for finding in findings)


def test_repeated_requirements_section_is_reported() -> None:
    document = make_feature_file(
        extra_sections=(make_requirements_section(make_requirement(3)),)
    )

    findings = validate_feature_file(document)

    assert any(finding.startswith("feature-file-requirements:") for finding in findings)


def test_requirements_section_with_a_requirement_line_is_accepted() -> None:
    findings = validate_feature_file(make_feature_file())

    assert not any(finding.startswith("feature-file-requirements:") for finding in findings)
