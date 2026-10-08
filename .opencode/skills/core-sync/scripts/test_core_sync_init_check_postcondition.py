"""Behavior tests for the postcondition of region-mode `init` then `check`."""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import (
    DEST_PLAIN,
    REV_A,
    REV_B,
    SOURCE_NO_MARKERS,
    _bindings_document,
    _check_args,
    _init_args,
    _write_file,
    uc,
)


class InitCheckPostconditionTests:
    """Verify initialized bindings pass `check` after pending paths are cleared."""

    def _setup(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_NO_MARKERS)
        _write_file(destination, "agent.md", DEST_PLAIN)
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["agent.md"]),
        )
        return source, destination, bindings_path

    def test_init_then_check_current_after_pending_cleared(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = self._setup(tmp_path)

        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 0
        updated = uc.load_bindings(bindings_path)
        assert updated is not None
        updated["pending"] = []
        uc.save_bindings(bindings_path, updated)

        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 0
