"""Test the status line and its three allowed values."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from feature_file_validation.domain._test_support import (  # noqa: E402
    make_feature_file,
    make_status_line,
)
from feature_file_validation.domain.rules import validate_feature_file  # noqa: E402


@pytest.mark.parametrize("status", ("achieved", "partial", "not started"))
def test_allowed_status_values_are_accepted(status: str) -> None:
    findings = validate_feature_file(make_feature_file(status=status))

    assert not any(finding.startswith("feature-file-status:") for finding in findings)


def test_unknown_status_value_is_reported() -> None:
    findings = validate_feature_file(make_feature_file(status="done"))

    assert any(finding.startswith("feature-file-status:") for finding in findings)
    assert any("'done'" in finding for finding in findings)


def test_missing_status_line_is_reported() -> None:
    findings = validate_feature_file(make_feature_file(include_status=False))

    assert any(finding.startswith("feature-file-status:") for finding in findings)


def test_repeated_status_line_is_reported() -> None:
    document = make_feature_file(extra_sections=(make_status_line("achieved"),))

    findings = validate_feature_file(document)

    assert any(finding.startswith("feature-file-status:") for finding in findings)
