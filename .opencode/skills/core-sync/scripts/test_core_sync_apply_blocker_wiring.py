"""Behavior tests for reconciliation blocker wiring in `apply`."""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import (
    DEST_MARKED,
    REV_A,
    REV_B,
    SOURCE_MARKED,
    _apply_args,
    _bindings_document,
    _write_file,
    uc,
)


class ApplyBlockerWiringTests:
    def test_apply_writes_block_when_pending(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", DEST_MARKED)
        _write_file(destination, "CLAUDE.md", "# Root\n\nContent.\n")
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(
                REV_B, "agent.md", ["agent.md"], ["agent.md"], "CLAUDE.md"
            ),
        )
        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 0
        text = (destination / "CLAUDE.md").read_text(encoding="utf-8")
        assert uc.RECONCILE_BEGIN in text
