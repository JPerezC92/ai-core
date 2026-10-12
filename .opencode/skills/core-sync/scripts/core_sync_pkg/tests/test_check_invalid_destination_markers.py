"""Tests for `check` rejecting invalid destination markers."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    REV_A,
    SOURCE_MARKED,
    _bindings_document,
    _check_args,
    _write_file,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import save_bindings  # noqa: E402


class CheckInvalidDestinationMarkersTests:
    """Verify `check` rejects invalid destination markers."""

    def _setup(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", SOURCE_MARKED)
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_A, "agent.md", ["agent.md"]),
        )
        return source, destination, bindings_path

    def test_invalid_destination_markers_return_two(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        _write_file(destination, "agent.md", "no markers\n")
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 2
