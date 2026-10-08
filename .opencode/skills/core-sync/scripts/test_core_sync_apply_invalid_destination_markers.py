"""Tests for `apply` rejecting invalid destination markers."""

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
        uc.save_bindings(
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
        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 2
        assert destination_path.read_text(encoding="utf-8") == "no markers\n"
