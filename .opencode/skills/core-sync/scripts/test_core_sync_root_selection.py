"""Behavior tests for selecting the destination root runtime file.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_root_selection.py
"""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import REV_A, _check_args, _region_fixture, _write_file, uc


class RootSelectionTests:
    """Verify default root runtime file selection for blocker updates."""

    def test_check_defaults_to_agents_md_when_present(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _region_fixture(
            tmp_path, pending=["agent.md"], root=None, root_file="CLAUDE.md"
        )
        (destination / "CLAUDE.md").unlink()
        _write_file(destination, "AGENTS.md", "# Agents\n\nBody.\n")

        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 1
        assert uc.RECONCILE_BEGIN in (destination / "AGENTS.md").read_text(
            encoding="utf-8"
        )
        assert not (destination / "CLAUDE.md").exists()
