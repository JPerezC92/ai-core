"""Test feature-document placeholder detection and code exemptions."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from feature_testkit import make_feature  # noqa: E402
from feature_validation.domain.rules import validate_feature  # noqa: E402


def test_placeholder_title_is_rejected() -> None:
    findings = validate_feature(make_feature(title="Feature name"))
    assert any("title" in finding for finding in findings)


def test_created_date_placeholder_is_rejected() -> None:
    findings = validate_feature(make_feature(created="date"))
    assert any("Created" in finding for finding in findings)


def test_unfilled_placeholder_outside_code_is_rejected() -> None:
    findings = validate_feature(make_feature(spec_entries=("- S1 — A <placeholder> requirement.",)))
    assert any("placeholder" in finding for finding in findings)


def test_placeholder_inside_code_is_ignored() -> None:
    document = make_feature(spec_entries=("- S1 — Use `odd/tasks/<feature-name>.md`.",))
    assert validate_feature(document) == []


def test_placeholder_inside_fenced_block_is_ignored() -> None:
    document = make_feature(spec_entries=("- S1 — A requirement.\n\n```\n<placeholder>\n```",))
    assert validate_feature(document) == []
