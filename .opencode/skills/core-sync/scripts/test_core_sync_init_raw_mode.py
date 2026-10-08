"""Behavior tests for raw-mode `init` byte-copying.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_init_raw_mode.py
"""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import (
    RAW_SOURCE_BYTES,
    REV_A,
    _init_args,
    _raw_setup,
    uc,
)


class RawInitTests:
    def test_init_copies_and_adds_no_pending_or_report(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _raw_setup(
            tmp_path, destination_content=b"stale\n"
        )
        destination_path = destination / "opencode.jsonc"
        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 0
        assert destination_path.read_bytes() == RAW_SOURCE_BYTES
        updated = uc.load_bindings(bindings_path)
        assert updated is not None
        assert updated["pending"] == []
        report_path = bindings_path.parent / "reconciliation" / "init.yaml"
        assert not report_path.exists()
