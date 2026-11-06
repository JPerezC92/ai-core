"""Behavior tests for the drift predicate `check` uses on a destination frontmatter.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/domain/test_frontmatter_current.py
"""

from __future__ import annotations

from core_sync_pkg.domain.refresh_frontmatter import frontmatter_is_current

SOURCE_FRONTMATTER = "---\ndescription: Current description.\n---\n"
STALE_FRONTMATTER = "---\ndescription: Stale description.\n---\n"
CURRENT_FRONTMATTER = "---\ndescription: Current description.\n---\n"


class FrontmatterCurrentTests:
    """Current means a write would emit the destination's own bytes."""

    def test_a_stale_key_is_not_current(self) -> None:
        assert not frontmatter_is_current(
            STALE_FRONTMATTER, SOURCE_FRONTMATTER
        )

    def test_a_refreshed_key_is_current(self) -> None:
        assert frontmatter_is_current(
            CURRENT_FRONTMATTER, SOURCE_FRONTMATTER
        )

    def test_a_refreshed_frontmatter_read_back_as_lf_is_current(self) -> None:
        # The writer emits LF only, so a destination an earlier sync wrote must
        # not read as stale merely because the source was read with CRLF.
        assert frontmatter_is_current(
            CURRENT_FRONTMATTER,
            "---\r\ndescription: Current description.\r\n---\r\n",
        )

    def test_a_destination_without_frontmatter_is_current(self) -> None:
        assert frontmatter_is_current("", SOURCE_FRONTMATTER)
