"""Behavior tests for refreshing a marked destination's frontmatter with `init`.

An already-marked destination whose core region is current but whose identity
keys are stale is still refreshed, and no reconciliation work is recorded for it.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_init_frontmatter_refresh.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    REV_A,
    _bindings_document,
    _init_args,
    _write_file,
)
from core_sync_pkg.domain.reconciliation import (  # noqa: E402
    reconciliation_report_path,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import (  # noqa: E402
    load_bindings,
    save_bindings,
)

# The core region already matches the source, so only the frontmatter is stale.
SOURCE_SKILL = (
    "---\n"
    "name: odd-workflow\n"
    "description: Current description.\n"
    "metadata:\n"
    "  version: 2.2.0\n"
    "---\n"
    "<!-- core:begin -->\n"
    "Core body\n"
    "<!-- core:end -->\n"
)

STALE_MARKED_DESTINATION = (
    "---\n"
    "name: odd-workflow\n"
    "description: Stale description.\n"
    "metadata:\n"
    "  version: 1.0.2\n"
    "  category: workflow\n"
    "local-version: 1.0.1\n"
    "---\n"
    "<!-- core:begin -->\n"
    "Core body\n"
    "<!-- core:end -->\n"
)

REFRESHED_DESTINATION = (
    "---\n"
    "name: odd-workflow\n"
    "description: Current description.\n"
    "metadata:\n"
    "  version: 2.2.0\n"
    "  category: workflow\n"
    "local-version: 1.0.1\n"
    "---\n"
    "<!-- core:begin -->\n"
    "Core body\n"
    "<!-- core:end -->\n"
)


class InitFrontmatterRefreshTests:
    """`init` refreshes a marked destination's frontmatter, not only its region."""

    def test_init_refreshes_frontmatter_with_an_unchanged_region(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "SKILL.md", SOURCE_SKILL)
        destination_path = _write_file(
            destination, "SKILL.md", STALE_MARKED_DESTINATION
        )
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_A, "SKILL.md", ["SKILL.md"]),
        )

        assert main(_init_args(source, destination, bindings_path, REV_A)) == 0

        assert destination_path.read_text(encoding="utf-8") == REFRESHED_DESTINATION
        assert "local-version: 1.0.1\n" in (
            destination_path.read_text(encoding="utf-8").splitlines(keepends=True)
        )
        assert capsys.readouterr().out == "initialized\n"

        # A refreshed frontmatter is core-owned metadata, not displaced project
        # content, so no reconciliation entry or pending path is recorded for a
        # write that replaced no core region byte.
        updated = load_bindings(bindings_path)
        assert updated is not None
        assert updated["pending"] == []
        assert not reconciliation_report_path(bindings_path).exists()
