"""Tests for `apply` rejecting invalid destination markers."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    DEST_MARKED,
    REV_A,
    REV_B,
    SOURCE_MARKED,
    _apply_args,
    _bindings_document,
    _write_file,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import save_bindings  # noqa: E402


class ApplyInvalidDestinationMarkersTests:
    """Verify `apply` rejects invalid destination markers."""

    def _setup(
        self, tmp_path: Path, *, destination_content: str = DEST_MARKED
    ) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", destination_content)
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["agent.md"]),
        )
        return source, destination, bindings_path

    def test_apply_invalid_destination_markers_returns_two_without_writing(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = self._setup(
            tmp_path, destination_content="no markers\n"
        )
        destination_path = destination / "agent.md"
        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 2
        assert destination_path.read_text(encoding="utf-8") == "no markers\n"
