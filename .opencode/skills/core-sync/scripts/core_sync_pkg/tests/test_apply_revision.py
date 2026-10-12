"""Behavior tests for the region-mode `apply` revision pin."""

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
from core_sync_pkg.infrastructure.stores import (  # noqa: E402
    load_bindings,
    save_bindings,
)


class ApplyRevisionTests:
    """Verify that successful `apply` pins the requested core revision."""

    def _setup(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", DEST_MARKED)
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["agent.md"]),
        )
        return source, destination, bindings_path

    def test_apply_pins_core_revision(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 0
        updated = load_bindings(bindings_path)
        assert updated is not None
        assert updated["core_revision"] == REV_A
