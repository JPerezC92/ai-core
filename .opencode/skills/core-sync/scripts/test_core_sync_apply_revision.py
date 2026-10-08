"""Behavior tests for the region-mode `apply` revision pin."""

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


class ApplyRevisionTests:
    """Verify that successful `apply` pins the requested core revision."""

    def _setup(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", DEST_MARKED)
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["agent.md"]),
        )
        return source, destination, bindings_path

    def test_apply_pins_core_revision(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 0
        updated = uc.load_bindings(bindings_path)
        assert updated is not None
        assert updated["core_revision"] == REV_A
