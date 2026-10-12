"""Behavior tests for selecting the destination root runtime file.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_root_selection.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    REV_A,
    _check_args,
    _region_fixture,
    _write_file,
)
from core_sync_pkg.domain.constants import RECONCILE_BEGIN  # noqa: E402
from core_sync_pkg.infrastructure.composition import main  # noqa: E402


class RootSelectionTests:
    """Verify default root runtime file selection for blocker updates."""

    def test_check_defaults_to_agents_md_when_present(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _region_fixture(
            tmp_path, pending=["agent.md"], root=None, root_file="CLAUDE.md"
        )
        (destination / "CLAUDE.md").unlink()
        _write_file(destination, "AGENTS.md", "# Agents\n\nBody.\n")

        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1
        assert RECONCILE_BEGIN in (destination / "AGENTS.md").read_text(
            encoding="utf-8"
        )
        assert not (destination / "CLAUDE.md").exists()
