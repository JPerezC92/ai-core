"""Tests for `check` rejecting invalid destination markers."""

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


class CheckInvalidDestinationMarkersTests:
    """Verify `check` rejects invalid destination markers."""

    def _setup(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", SOURCE_MARKED)
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_A, "agent.md", ["agent.md"]),
        )
        return source, destination, bindings_path

    def test_invalid_destination_markers_return_two(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        _write_file(destination, "agent.md", "no markers\n")
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 2
