"""Test the one paragraph that says what the feature is."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from feature_file_validation.domain._test_support import make_feature_file  # noqa: E402
from feature_file_validation.domain.rules import validate_feature_file  # noqa: E402


def test_title_without_a_description_is_reported() -> None:
    findings = validate_feature_file(make_feature_file(description=""))

    assert any(finding.startswith("feature-file-description:") for finding in findings)


def test_title_with_a_description_is_accepted() -> None:
    findings = validate_feature_file(make_feature_file())

    assert not any(
        finding.startswith("feature-file-description:") for finding in findings
    )
