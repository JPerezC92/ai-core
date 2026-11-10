"""Test which feature-file references are selected and in which order."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from feature_file_validation.domain.rules import (  # noqa: E402
    is_template_reference,
    sort_feature_file_references,
)


@pytest.mark.parametrize(
    "reference",
    ("_template.md", "odd/features/_template.md", "./odd/features/_template.md"),
)
def test_template_reference_is_recognized(reference: str) -> None:
    assert is_template_reference(reference)


def test_a_feature_file_is_not_a_template_reference() -> None:
    assert not is_template_reference("odd/features/durable-feature-file.md")


def test_references_are_sorted_stably() -> None:
    references = ("odd/features/b.md", "odd/features/_template.md", "odd/features/a.md")

    assert sort_feature_file_references(references) == (
        "odd/features/_template.md",
        "odd/features/a.md",
        "odd/features/b.md",
    )
