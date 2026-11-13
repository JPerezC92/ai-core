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
    ("_template.md", ".aicore/core/odd/features/_template.md", "./odd/features/_template.md"),
)
def test_template_reference_is_recognized(reference: str) -> None:
    assert is_template_reference(reference)


def test_a_feature_file_is_not_a_template_reference() -> None:
    assert not is_template_reference(".aicore/core/odd/features/durable-feature-file.md")


def test_references_are_sorted_stably() -> None:
    references = (".aicore/core/odd/features/b.md", ".aicore/core/odd/features/_template.md", ".aicore/core/odd/features/a.md")

    assert sort_feature_file_references(references) == (
        ".aicore/core/odd/features/_template.md",
        ".aicore/core/odd/features/a.md",
        ".aicore/core/odd/features/b.md",
    )
