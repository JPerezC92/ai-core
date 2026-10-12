"""Behavior tests for source revision mismatch in region-mode `check`."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    REV_A,
    REV_B,
    SOURCE_MARKED,
    _bindings_document,
    _check_args,
    _write_file,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import save_bindings  # noqa: E402


class CheckRevisionTests:
    def test_revision_mismatch_returns_one(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", SOURCE_MARKED)
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["agent.md"]),
        )
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1
