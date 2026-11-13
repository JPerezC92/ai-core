"""Test the optional requirement mark and its closed vocabulary."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from feature_file_validation.domain._test_support import (  # noqa: E402
    MARKS,
    make_feature_file,
    make_requirement,
)
from feature_file_validation.domain.rules import validate_feature_file  # noqa: E402


@pytest.mark.parametrize("mark", MARKS)
def test_known_marks_are_accepted(mark: str) -> None:
    entries = (make_requirement(1, mark=mark), make_requirement(2, ticked=False))

    findings = validate_feature_file(make_feature_file(requirement_entries=entries))

    assert not any(
        finding.startswith("feature-file-requirement-mark:") for finding in findings
    )


def test_unknown_mark_is_reported() -> None:
    entries = (
        make_requirement(1, mark="upstream · widened"),
        make_requirement(2, ticked=False),
    )

    findings = validate_feature_file(make_feature_file(requirement_entries=entries))

    assert any(finding.startswith("feature-file-requirement-mark:") for finding in findings)
    assert any("upstream · widened" in finding for finding in findings)


def test_requirement_without_a_mark_is_accepted() -> None:
    findings = validate_feature_file(make_feature_file())

    assert not any(
        finding.startswith("feature-file-requirement-mark:") for finding in findings
    )
