"""Behavior tests for region-mode `init` idempotence."""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import (
    DEST_PLAIN,
    REV_A,
    REV_B,
    SOURCE_NO_MARKERS,
    _apply_args,
    _bindings_document,
    _init_args,
    _write_file,
    uc,
)


class InitIdempotenceTests:
    """Verify repeated `init` and `apply` calls leave enrollment unchanged."""

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

    def test_init_is_idempotent_when_rerun(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        destination_path = destination / "agent.md"

        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 0
        after_first = destination_path.read_text(encoding="utf-8")
        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 0
        after_refresh = destination_path.read_text(encoding="utf-8")
        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 0
        after_second = destination_path.read_text(encoding="utf-8")

        assert after_first == after_refresh == after_second
