"""Test the H1 title line that opens the feature file."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from feature_file_validation.domain._test_support import make_feature_file  # noqa: E402
from feature_file_validation.domain.rules import validate_feature_file  # noqa: E402


def test_missing_title_is_reported() -> None:
    findings = validate_feature_file(make_feature_file(include_title=False))

    assert any(finding.startswith("feature-file-title:") for finding in findings)


def test_title_is_accepted() -> None:
    findings = validate_feature_file(make_feature_file())

    assert not any(finding.startswith("feature-file-title:") for finding in findings)
