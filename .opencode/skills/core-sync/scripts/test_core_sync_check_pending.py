"""Behavior tests for nonempty pending status in region-mode `check`."""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import (
    REV_A,
    SOURCE_MARKED,
    _bindings_document,
    _check_args,
    _write_file,
    uc,
)


class CheckPendingTests:
    def test_nonempty_pending_returns_one(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", SOURCE_MARKED)
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(
                REV_A, "agent.md", ["agent.md"], pending=["agent.md"]
            ),
        )
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 1
