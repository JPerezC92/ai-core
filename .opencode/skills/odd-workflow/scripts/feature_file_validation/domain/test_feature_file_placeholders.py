"""Test unfilled placeholder detection and its code exemptions."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from feature_file_validation.domain._test_support import (  # noqa: E402
    make_bullet_line,
    make_feature_file,
    make_fenced_block,
)
from feature_file_validation.domain.rules import validate_feature_file  # noqa: E402


def test_unfilled_placeholder_is_reported() -> None:
    document = make_feature_file(
        extra_sections=(make_bullet_line("The requirement states <what proves it>."),)
    )

    findings = validate_feature_file(document)

    assert any(
        finding.startswith("feature-file-unfilled-placeholder:") for finding in findings
    )


def test_placeholder_inside_a_code_span_is_ignored() -> None:
    document = make_feature_file(
        extra_sections=(
            make_bullet_line("The file lives at `odd/features/<feature-name>.md`."),
        )
    )

    findings = validate_feature_file(document)

    assert not any(
        finding.startswith("feature-file-unfilled-placeholder:") for finding in findings
    )


def test_placeholder_inside_a_fenced_block_is_ignored() -> None:
    document = make_feature_file(extra_sections=(make_fenced_block("<placeholder>"),))

    findings = validate_feature_file(document)

    assert not any(
        finding.startswith("feature-file-unfilled-placeholder:") for finding in findings
    )
