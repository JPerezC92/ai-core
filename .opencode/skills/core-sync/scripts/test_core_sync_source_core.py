"""Behavior tests for source-core extraction: `extract_source_core`.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_source_core.py
"""

from __future__ import annotations

import pytest

from _core_sync_testkit import SOURCE_MARKED, uc


class SourceCoreTests:
    def test_markerless_source_uses_body_after_frontmatter(self) -> None:
        content = "---\nname: sample\n---\n\nBody line one\nBody line two\n"
        assert uc.extract_source_core(content) == "\nBody line one\nBody line two\n"

    def test_markerless_source_without_frontmatter_uses_whole_body(self) -> None:
        assert uc.extract_source_core("plain body\n") == "plain body\n"

    def test_markerless_source_ignores_marker_lines_inside_fenced_code(self) -> None:
        content = (
            "---\nname: sample\n---\n"
            "\nExample:\n```markdown\n"
            "<!-- core:begin -->\nExample core\n<!-- core:end -->\n"
            "```\nAfter example.\n"
        )

        assert uc.extract_source_core(content) == (
            "\nExample:\n```markdown\n"
            "<!-- core:begin -->\nExample core\n<!-- core:end -->\n"
            "```\nAfter example.\n"
        )

    def test_marked_source_uses_region(self) -> None:
        assert uc.extract_source_core(SOURCE_MARKED) == (
            "\nCore body line one\nCore body line two\n"
        )

    @pytest.mark.parametrize(
        "content",
        [
            "<!-- core:begin -->\nCore body\n",
            "<!-- core:end -->\nCore body\n",
            "<!-- core:begin -->\n<!-- core:begin -->\n"
            "Core body\n<!-- core:end -->\n",
            "<!-- core:begin -->\nCore body\n"
            "<!-- core:end -->\n<!-- core:end -->\n",
            "<!-- core:end -->\nCore body\n<!-- core:begin -->\n",
        ],
        ids=[
            "missing-end",
            "missing-begin",
            "duplicate-begin",
            "duplicate-end",
            "reversed",
        ],
    )
    def test_malformed_source_markers_raise_distinct_error(
        self, content: str
    ) -> None:
        with pytest.raises(uc.MalformedSourceMarkers):
            uc.extract_source_core(content)
