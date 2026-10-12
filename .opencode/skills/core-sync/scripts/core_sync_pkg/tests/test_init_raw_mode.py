"""Tests for copying bytes to an already-declared raw-mode target."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    RAW_SOURCE_BYTES,
    REV_A,
    _init_args,
    _raw_setup,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import load_bindings  # noqa: E402


class RawInitExistingTargetTests:
    def test_init_copies_and_adds_no_pending_or_report(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _raw_setup(
            tmp_path, destination_content=b"stale\n"
        )
        destination_path = destination / "opencode.jsonc"
        assert main(_init_args(source, destination, bindings_path, REV_A)) == 0
        assert destination_path.read_bytes() == RAW_SOURCE_BYTES
        updated = load_bindings(bindings_path)
        assert updated is not None
        assert updated["pending"] == []
        report_path = bindings_path.parent / "reconciliation" / "init.yaml"
        assert not report_path.exists()
