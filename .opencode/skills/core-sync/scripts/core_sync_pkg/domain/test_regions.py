"""Behavior tests for valid region decomposition and outside-byte extraction.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_regions.py
"""

from __future__ import annotations

from core_sync_pkg.domain.markers import has_exact_core_marker_lines
from core_sync_pkg.domain.regions import (
    extract_source_core,
    outside_bytes,
    render_init_file,
    split_frontmatter,
    split_regions,
)


class FrontmatterDelimiterTests:
    def test_padded_delimiter_lines_are_not_frontmatter(self) -> None:
        content = "  ---  \nrule\n  ---  \nbody\n"

        assert split_frontmatter(content) == ("", content)
        assert extract_source_core(content) == content

    def test_empty_frontmatter_splits_on_second_delimiter(self) -> None:
        # A `---` immediately after the opening bookend still closes frontmatter.
        assert split_frontmatter("---\n---\nbody\n") == ("---\n---\n", "body\n")

    def test_unclosed_frontmatter_returns_content_unsplit(self) -> None:
        # No closing delimiter: nothing is frontmatter, so no key is lost.
        assert split_frontmatter("---\nrule\n") == ("", "---\nrule\n")

    def test_unterminated_fence_prevents_closing_delimiter(self) -> None:
        # The fence never closes, so the trailing `---` is inside it and therefore
        # never a delimiter; the whole content stays body.
        assert split_frontmatter("---\nname: x\n```\n---\n") == (
            "",
            "---\nname: x\n```\n---\n",
        )

    def test_delimiter_as_unterminated_last_line_closes_frontmatter(self) -> None:
        # A closing delimiter on a final line with no terminator still closes.
        assert split_frontmatter("---\nname: x\n---") == ("---\nname: x\n---", "")


class FencedFrontmatterDelimiterTests:
    def test_indented_fenced_delimiter_does_not_close_frontmatter(self) -> None:
        # S3 with a fence present: the indented `---` inside the fence is BOTH
        # padded (so never a delimiter on its own) and fenced. Kept as the
        # padded+fenced combination; the column-0 case below is the one that
        # isolates fence awareness.
        content = (
            "---\n"
            "name: x\n"
            "example: |\n"
            "  ```yaml\n"
            "  ---\n"
            "  ```\n"
            "---\n"
            "body\n"
        )

        frontmatter, body = split_frontmatter(content)

        assert frontmatter == (
            "---\nname: x\nexample: |\n  ```yaml\n  ---\n  ```\n---\n"
        )
        assert body == "body\n"

    def test_column_zero_fenced_delimiter_does_not_close_frontmatter(self) -> None:
        # S4 isolated: every `---` here is column 0, so the split is correct only
        # if the closing scan skips `---` lines inside a fence.
        content = (
            "---\n"
            "name: x\n"
            "example: |\n"
            "```yaml\n"
            "---\n"
            "```\n"
            "---\n"
            "body\n"
        )

        assert split_frontmatter(content) == (
            "---\nname: x\nexample: |\n```yaml\n---\n```\n---\n",
            "body\n",
        )


class RenderInitFileTests:
    def test_frontmatter_without_trailing_newline_stays_parseable(self) -> None:
        rendered = render_init_file("---\nname: x\n---", "CORE")

        split = split_regions(rendered)

        assert has_exact_core_marker_lines(rendered)
        assert split is not None
        assert split["begin_line"] == "<!-- core:begin -->\n"

    def test_frontmatter_with_trailing_newline_is_unchanged(self) -> None:
        # S2 claim 2: the destination frontmatter is never concatenated directly
        # with the begin marker, and is otherwise byte-identical to before.
        assert render_init_file("---\nname: x\n---\n", "CORE") == (
            "---\nname: x\n---\n"
            "<!-- core:begin -->\n"
            "CORE\n"
            "<!-- core:end -->\n"
            "\n"
            "<!-- project:begin -->\n"
            "<!-- project:end -->\n"
        )
        # S2 claim 1: a destination without a trailing newline renders identically.
        assert render_init_file("---\nname: x\n---", "CORE") == render_init_file(
            "---\nname: x\n---\n", "CORE"
        )


class RegionDecompositionTests:
    def test_valid_markers_split_region_and_outside(self) -> None:
        content = "head\n<!-- core:begin -->\nbody\n<!-- core:end -->\ntail\n"
        split = split_regions(content)
        assert split is not None
        assert split["before"] == "head\n"
        assert split["region"] == "body\n"
        assert split["after"] == "tail\n"
        assert (
            outside_bytes(split)
            == "head\n<!-- core:begin -->\n<!-- core:end -->\ntail\n"
        )
