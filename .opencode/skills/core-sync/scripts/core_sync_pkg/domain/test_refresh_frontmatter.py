"""Behavior tests for the frontmatter refresh merge rule.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/domain/test_refresh_frontmatter.py
"""

from __future__ import annotations

from core_sync_pkg.domain.refresh_frontmatter import refresh_frontmatter

SOURCE_FRONTMATTER = (
    "---\n"
    "name: odd-workflow\n"
    "description: Current description.\n"
    "version: 2.2.0\n"
    "license: MIT\n"
    "metadata:\n"
    "  author: AICore\n"
    "  version: 2.2.0\n"
    "---\n"
)

DESTINATION_FRONTMATTER = (
    "---\n"
    "name: odd-workflow\n"
    "description: Stale description.\n"
    "version: 1.0.2\n"
    "metadata:\n"
    "  author: Destination Author\n"
    "  version: 1.0.2\n"
    "  category: workflow\n"
    "local-version: 1.0.1\n"
    "---\n"
)

# The source defines only `description`, so every other destination line is
# untouched and must keep its own bytes.
DESCRIPTION_ONLY_SOURCE = "---\ndescription: Current description.\n---\n"

UNTOUCHED_DESTINATION = (
    "---\n"
    "name: odd-workflow\n"
    'quoted: "keep my quotes"\n'
    "description: Stale description.\n"
    "version: 1.10\n"
    "---\n"
)

DUPLICATE_KEY_DESTINATION = (
    "---\n"
    "name: odd-workflow\n"
    "name: odd-workflow-again\n"
    "description: Stale description.\n"
    "---\n"
)


def _line(frontmatter: str, key: str, indent: str = "") -> str:
    """Return the first line at `indent` declaring `key`, terminator included."""
    for line in frontmatter.splitlines(keepends=True):
        if not line.startswith(indent):
            continue
        rest = line[len(indent) :]
        if rest[:1].isspace() or rest.startswith("#"):
            continue
        if rest.partition(":")[0].strip() == key:
            return line
    raise AssertionError(f"no line at indent {indent!r} declares {key}")


def _top_level_keys(frontmatter: str) -> list[str]:
    """Return the top-level keys of a frontmatter in the order they appear."""
    lines = frontmatter.splitlines()[1:-1]
    return [line.partition(":")[0] for line in lines if line[:1].strip()]


class FrontmatterRefreshTests:
    """The source wins per key, one level into `metadata`, and adds keys."""

    def test_shared_key_takes_the_source_value(self) -> None:
        refreshed = refresh_frontmatter(
            DESTINATION_FRONTMATTER, SOURCE_FRONTMATTER
        )

        assert _line(refreshed["text"], "description") == (
            "description: Current description.\n"
        )
        assert _line(refreshed["text"], "version") == "version: 2.2.0\n"
        assert refreshed["skipped"] == ""

    def test_source_only_key_is_added(self) -> None:
        refreshed = refresh_frontmatter(
            DESTINATION_FRONTMATTER, SOURCE_FRONTMATTER
        )

        assert _line(refreshed["text"], "license") == "license: MIT\n"

    def test_local_version_survives_a_version_refresh_byte_identically(
        self,
    ) -> None:
        refreshed = refresh_frontmatter(
            DESTINATION_FRONTMATTER, SOURCE_FRONTMATTER
        )

        assert _line(refreshed["text"], "version") == "version: 2.2.0\n"
        assert _line(DESTINATION_FRONTMATTER, "local-version") in (
            refreshed["text"].splitlines(keepends=True)
        )

    def test_metadata_merges_one_level_and_keeps_a_destination_only_child(
        self,
    ) -> None:
        refreshed = refresh_frontmatter(
            DESTINATION_FRONTMATTER, SOURCE_FRONTMATTER
        )

        assert _line(refreshed["text"], "author", "  ") == "  author: AICore\n"
        assert _line(DESTINATION_FRONTMATTER, "category", "  ") in (
            refreshed["text"].splitlines(keepends=True)
        )

    def test_merged_keys_keep_destination_order_then_source_only_keys(
        self,
    ) -> None:
        refreshed = refresh_frontmatter(
            DESTINATION_FRONTMATTER, SOURCE_FRONTMATTER
        )

        assert _top_level_keys(refreshed["text"]) == [
            "name",
            "description",
            "version",
            "metadata",
            "local-version",
            "license",
        ]

    def test_an_untouched_ambiguous_scalar_is_preserved_byte_identically(
        self,
    ) -> None:
        # `1.10` would be read as the float 1.1 and written back as `1.1` by any
        # implementation that re-serialises a key the source does not define.
        refreshed = refresh_frontmatter(
            UNTOUCHED_DESTINATION, DESCRIPTION_ONLY_SOURCE
        )

        assert _line(refreshed["text"], "version") == "version: 1.10\n"
        assert "version: 1.1\n" not in refreshed["text"]

    def test_only_the_source_defined_block_changes(self) -> None:
        refreshed = refresh_frontmatter(
            UNTOUCHED_DESTINATION, DESCRIPTION_ONLY_SOURCE
        )
        before = UNTOUCHED_DESTINATION.splitlines(keepends=True)
        after = refreshed["text"].splitlines(keepends=True)

        assert len(before) == len(after)
        assert [old for old, new in zip(before, after) if old != new] == [
            "description: Stale description.\n"
        ]
        assert refreshed["text"] == UNTOUCHED_DESTINATION.replace(
            "description: Stale description.\n",
            "description: Current description.\n",
        )

    def test_only_the_source_defined_block_changes_with_an_ambiguous_local_version(
        self,
    ) -> None:
        destination = (
            "---\n"
            "name: odd-workflow\n"
            "description: Stale description.\n"
            "local-version: 1.10\n"
            "---\n"
        )

        refreshed = refresh_frontmatter(destination, DESCRIPTION_ONLY_SOURCE)

        assert refreshed["text"] == destination.replace(
            "description: Stale description.\n",
            "description: Current description.\n",
        )

    def test_untouched_quoting_style_is_preserved(self) -> None:
        refreshed = refresh_frontmatter(
            UNTOUCHED_DESTINATION, DESCRIPTION_ONLY_SOURCE
        )

        assert 'quoted: "keep my quotes"\n' in refreshed["text"]

    def test_a_destination_comment_keeps_its_place_and_bytes(self) -> None:
        destination = (
            "---\n"
            "name: odd-workflow\n"
            "description: Stale description.\n"
            "# owned by the destination\n"
            "local-version: 1.0.1\n"
            "---\n"
        )

        refreshed = refresh_frontmatter(destination, DESCRIPTION_ONLY_SOURCE)

        assert refreshed["text"] == (
            "---\n"
            "name: odd-workflow\n"
            "description: Current description.\n"
            "# owned by the destination\n"
            "local-version: 1.0.1\n"
            "---\n"
        )

    def test_a_destination_without_frontmatter_is_unchanged(self) -> None:
        assert refresh_frontmatter("", SOURCE_FRONTMATTER)["text"] == ""

    def test_an_empty_frontmatter_takes_the_source_keys(self) -> None:
        refreshed = refresh_frontmatter("---\n---\n", SOURCE_FRONTMATTER)

        assert _top_level_keys(refreshed["text"]) == [
            "name",
            "description",
            "version",
            "license",
            "metadata",
        ]

    def test_a_source_without_frontmatter_leaves_the_destination_unchanged(
        self,
    ) -> None:
        assert refresh_frontmatter(DESTINATION_FRONTMATTER, "")["text"] == (
            DESTINATION_FRONTMATTER
        )

    def test_an_unreadable_frontmatter_is_left_unchanged_and_says_why(
        self,
    ) -> None:
        broken = "---\nname: [unclosed\n---\n"

        refreshed = refresh_frontmatter(broken, SOURCE_FRONTMATTER)

        assert refreshed["text"] == broken
        assert refreshed["skipped"] == "frontmatter is not a readable YAML mapping"

    def test_an_unmappable_destination_is_left_unchanged_and_says_why(self) -> None:
        # Two `name` lines cannot be matched to the one parsed key, so the file
        # is not rewritten and the caller is told why instead of a silent no-op.
        refreshed = refresh_frontmatter(
            DUPLICATE_KEY_DESTINATION, DESCRIPTION_ONLY_SOURCE
        )

        assert refreshed["text"] == DUPLICATE_KEY_DESTINATION
        assert refreshed["skipped"] == (
            "frontmatter keys cannot be mapped to their lines"
        )

    def test_an_unmappable_metadata_block_reports_only_that_block(self) -> None:
        # A duplicate child key leaves the `metadata` block byte-identical while
        # the other shared keys still refresh, so the reason names the block
        # rather than the whole document. The expectation is the whole text: a
        # presence check would still pass if the untouched block lost a duplicate
        # child, lost its last line, or were re-indented.
        destination = (
            "---\n"
            "name: odd-workflow\n"
            "description: Stale description.\n"
            "metadata:\n"
            "  version: 1.0.2\n"
            "  version: 1.0.2\n"
            "---\n"
        )
        source = (
            "---\n"
            "description: Current description.\n"
            "metadata:\n"
            "  version: 2.2.0\n"
            "---\n"
        )

        refreshed = refresh_frontmatter(destination, source)

        assert refreshed["text"] == destination.replace(
            "description: Stale description.\n",
            "description: Current description.\n",
        )
        assert refreshed["skipped"] == (
            "destination `metadata` child keys cannot be mapped to its lines"
        )

    def test_a_yaml_merge_key_is_left_unchanged_and_says_why(self) -> None:
        # The parser expands `<<: *b` into the mapping and drops the `<<` member,
        # so the parsed key count still matches the member count while the block
        # labels drift one key early: the `base` block would be labelled `x` and
        # replaced by the source's `x`, rewriting a destination line the source
        # never declared. Rejecting the merge key is what prevents that.
        destination = (
            "---\n"
            "base: &b\n"
            "  x: 1\n"
            "<<: *b\n"
            "c: 2\n"
            "---\n"
        )
        source = "---\nx: from-source\n---\n"

        refreshed = refresh_frontmatter(destination, source)

        assert refreshed["text"] == destination
        assert refreshed["skipped"] == (
            "frontmatter keys cannot be mapped to their lines"
        )