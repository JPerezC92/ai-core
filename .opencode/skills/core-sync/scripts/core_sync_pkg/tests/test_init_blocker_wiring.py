"""Behavior tests for reconciliation blocker wiring in `init`."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    DEST_PLAIN,
    REV_A,
    REV_B,
    SOURCE_NO_MARKERS,
    _bindings_document,
    _init_args,
    _write_file,
)
from core_sync_pkg.domain.constants import RECONCILE_BEGIN  # noqa: E402
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import save_bindings  # noqa: E402


class InitBlockerWiringTests:
    def test_init_writes_block_when_pending_set(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_NO_MARKERS)
        _write_file(destination, "agent.md", DEST_PLAIN)
        _write_file(destination, "CLAUDE.md", "# Root\n\nContent.\n")
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["agent.md"], None, "CLAUDE.md"),
        )
        assert main(_init_args(source, destination, bindings_path, REV_A)) == 0
        text = (destination / "CLAUDE.md").read_text(encoding="utf-8")
        assert RECONCILE_BEGIN in text
