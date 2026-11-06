"""Behavior tests for an unrefreshable destination frontmatter.

A frontmatter that cannot be merged is left byte-identical, the write still
succeeds, and the result message names the path and the reason. A block the merge
cannot match is reported the same way while the keys it can match still apply.
Both write commands are covered: `apply`, and `init` on its markerless and its
already-marked enrollment paths.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_frontmatter_skip.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    REV_A,
    _apply_args,
    _bindings_document,
    _check_args,
    _init_args,
    _write_file,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import save_bindings  # noqa: E402

SOURCE_SKILL = (
    "---\n"
    "name: odd-workflow\n"
    "description: Current description.\n"
    "---\n"
    "<!-- core:begin -->\n"
    "New core body\n"
    "<!-- core:end -->\n"
)

# Two `name` lines cannot be matched to the single parsed key, so no block can be
# replaced without guessing which line the key belongs to.
DUPLICATE_KEY_DESTINATION = (
    "---\n"
    "name: odd-workflow\n"
    "name: odd-workflow-again\n"
    "description: Stale description.\n"
    "local-version: 1.10\n"
    "---\n"
    "<!-- core:begin -->\n"
    "Old core body\n"
    "<!-- core:end -->\n"
)

SKIP_REASON = "frontmatter keys cannot be mapped to their lines"

# A duplicate child key makes only the `metadata` block unmappable, so the other
# shared keys still refresh and the block keeps its own bytes: the partial skip.
UNMAPPABLE_METADATA_SOURCE = (
    "---\n"
    "name: odd-workflow\n"
    "description: Current description.\n"
    "metadata:\n"
    "  version: 2.2.0\n"
    "---\n"
    "<!-- core:begin -->\n"
    "New core body\n"
    "<!-- core:end -->\n"
)

UNMAPPABLE_METADATA_DESTINATION = (
    "---\n"
    "name: odd-workflow\n"
    "description: Stale description.\n"
    "metadata:\n"
    "  version: 1.0.2\n"
    "  version: 1.0.2\n"
    "local-version: 1.0.1\n"
    "---\n"
    "<!-- core:begin -->\n"
    "Old core body\n"
    "<!-- core:end -->\n"
)

PARTIALLY_REFRESHED_DESTINATION = (
    "---\n"
    "name: odd-workflow\n"
    "description: Current description.\n"
    "metadata:\n"
    "  version: 1.0.2\n"
    "  version: 1.0.2\n"
    "local-version: 1.0.1\n"
    "---\n"
    "<!-- core:begin -->\n"
    "New core body\n"
    "<!-- core:end -->\n"
)

METADATA_SKIP_REASON = (
    "destination `metadata` child keys cannot be mapped to its lines"
)

# A markerless destination is enrolled through the creation path, which refreshes
# the destination's own frontmatter before wrapping the rest in a project region.
MARKERLESS_DUPLICATE_KEY_DESTINATION = (
    "---\n"
    "name: odd-workflow\n"
    "name: odd-workflow-again\n"
    "description: Stale description.\n"
    "local-version: 1.10\n"
    "---\n"
    "\n"
    "# Old title\n"
    "\n"
    "Old body line\n"
)

MARKERLESS_DUPLICATE_KEY_FRONTMATTER = (
    "---\n"
    "name: odd-workflow\n"
    "name: odd-workflow-again\n"
    "description: Stale description.\n"
    "local-version: 1.10\n"
    "---\n"
)


class FrontmatterSkipTests:
    """An unrefreshable frontmatter is preserved and the reason is reported."""

    def _setup(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "SKILL.md", SOURCE_SKILL)
        _write_file(destination, "SKILL.md", DUPLICATE_KEY_DESTINATION)
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_A, "SKILL.md", ["SKILL.md"]),
        )
        return source, destination, bindings_path

    def test_apply_keeps_the_frontmatter_and_reports_the_reason(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        destination_path = destination / "SKILL.md"

        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 0

        captured = capsys.readouterr()
        assert f"frontmatter not refreshed: {destination_path}" in captured.out
        assert f"({SKIP_REASON})" in captured.out
        written = destination_path.read_text(encoding="utf-8")
        frontmatter, _ = DUPLICATE_KEY_DESTINATION.split(
            "<!-- core:begin -->", 1
        )
        assert written.startswith(frontmatter)
        # The core region still moved: an unrefreshable frontmatter is a partial
        # skip, not a whole-document one.
        assert "New core body\n" in written
        assert "Old core body\n" not in written

    def test_check_stays_current_because_the_same_rule_skips_it(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # `check` applies the merge rule the write applied, so a frontmatter that
        # cannot be refreshed never becomes permanent, unwinnable drift.
        source, destination, bindings_path = self._setup(tmp_path)

        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 0

        capsys.readouterr()
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 0
        assert capsys.readouterr().out == "current\n"

    def test_apply_reports_a_metadata_block_skip_and_keeps_its_bytes(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # Only the `metadata` block is unmappable here, so the write still applies
        # the keys it can and names the block in the reason: the partial skip is a
        # different outcome from the whole-document one, not a silent no-op.
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "SKILL.md", UNMAPPABLE_METADATA_SOURCE)
        destination_path = _write_file(
            destination, "SKILL.md", UNMAPPABLE_METADATA_DESTINATION
        )
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_A, "SKILL.md", ["SKILL.md"]),
        )

        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 0

        expected_line = (
            f"frontmatter not refreshed: {destination_path} "
            f"({METADATA_SKIP_REASON})"
        )
        assert expected_line in capsys.readouterr().out
        written = destination_path.read_text(encoding="utf-8")
        # The whole document is pinned, which is what proves the block kept its
        # own bytes rather than merely still containing the version string.
        assert written == PARTIALLY_REFRESHED_DESTINATION
        block = written.split("metadata:\n", 1)[1].split("local-version:", 1)[0]
        assert block == "  version: 1.0.2\n  version: 1.0.2\n"


class InitFrontmatterSkipTests:
    """`init` reports an unrefreshable frontmatter on both enrollment paths."""

    def _setup(
        self, tmp_path: Path, source_content: str, destination_content: str
    ) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "SKILL.md", source_content)
        _write_file(destination, "SKILL.md", destination_content)
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_A, "SKILL.md", ["SKILL.md"]),
        )
        return source, destination, bindings_path

    def test_init_keeps_a_markerless_destination_and_reports_the_reason(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # A markerless destination takes the creation path, which refreshes the
        # destination's own frontmatter separately from the marked path: a bare
        # `initialized` would report success for a frontmatter never refreshed.
        source, destination, bindings_path = self._setup(
            tmp_path,
            SOURCE_SKILL,
            MARKERLESS_DUPLICATE_KEY_DESTINATION,
        )
        destination_path = destination / "SKILL.md"

        assert main(_init_args(source, destination, bindings_path, REV_A)) == 0

        expected_line = (
            f"frontmatter not refreshed: {destination_path} ({SKIP_REASON})"
        )
        assert capsys.readouterr().out == f"initialized; {expected_line}\n"
        written = destination_path.read_text(encoding="utf-8")
        # Everything before the new core marker is the untouched frontmatter.
        frontmatter = written.split("<!-- core:begin -->", 1)[0]
        assert frontmatter == MARKERLESS_DUPLICATE_KEY_FRONTMATTER
        # Both regions were still built: the skip is the frontmatter only.
        assert "New core body\n" in written
        assert "# Old title\n\nOld body line\n" in written

    def test_init_reports_a_metadata_block_skip_and_keeps_its_bytes(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # The already-marked path reports through the same reason channel, and
        # only the `metadata` block is left alone: `description` still takes the
        # source value.
        source, destination, bindings_path = self._setup(
            tmp_path,
            UNMAPPABLE_METADATA_SOURCE,
            UNMAPPABLE_METADATA_DESTINATION,
        )
        destination_path = destination / "SKILL.md"

        assert main(_init_args(source, destination, bindings_path, REV_A)) == 0

        expected_line = (
            f"frontmatter not refreshed: {destination_path} "
            f"({METADATA_SKIP_REASON})"
        )
        assert capsys.readouterr().out == f"initialized; {expected_line}\n"
        written = destination_path.read_text(encoding="utf-8")
        # The whole document is pinned, so the block provably kept its bytes
        # rather than merely still containing the version string.
        assert written == PARTIALLY_REFRESHED_DESTINATION
        block = written.split("metadata:\n", 1)[1].split("local-version:", 1)[0]
        assert block == "  version: 1.0.2\n  version: 1.0.2\n"
        assert "description: Current description.\n" in written
