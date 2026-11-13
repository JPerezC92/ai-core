"""Test that the template-only guidance section is rejected on a real feature file."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from feature_file_validation.domain._test_support import (  # noqa: E402
    make_feature_file,
    make_guidance_section,
)
from feature_file_validation.domain.rules import validate_feature_file  # noqa: E402


def test_guidance_section_is_reported() -> None:
    document = make_feature_file(extra_sections=(make_guidance_section(),))

    findings = validate_feature_file(document)

    assert any(
        finding.startswith("feature-file-template-guidance:") for finding in findings
    )


def test_file_without_a_guidance_section_is_accepted() -> None:
    findings = validate_feature_file(make_feature_file())

    assert not any(
        finding.startswith("feature-file-template-guidance:") for finding in findings
    )
