"""Behavior tests for source revision mismatch in region-mode `check`."""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import (
    REV_A,
    REV_B,
    SOURCE_MARKED,
    _bindings_document,
    _check_args,
    _write_file,
    uc,
)


class CheckRevisionTests:
    def test_revision_mismatch_returns_one(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", SOURCE_MARKED)
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["agent.md"]),
        )
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 1
