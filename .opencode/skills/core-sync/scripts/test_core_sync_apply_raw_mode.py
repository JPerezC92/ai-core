"""Behavior tests for raw-mode `apply` byte-copying.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_apply_raw_mode.py
"""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import (
    RAW_SOURCE_BYTES,
    REV_A,
    _apply_args,
    _raw_setup,
    uc,
)


class RawApplyTests:
    def test_apply_copies_source_bytes_verbatim(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _raw_setup(
            tmp_path, destination_content=b"stale\n"
        )
        destination_path = destination / "opencode.jsonc"
        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 0
        assert destination_path.read_bytes() == RAW_SOURCE_BYTES

    def test_apply_copies_non_utf8_bytes_verbatim(self, tmp_path: Path) -> None:
        payload = b'{"note": "\xff\xfe raw", "n": 1}\n'
        source, destination, bindings_path = _raw_setup(
            tmp_path, source_content=payload, destination_content=b"{}\n"
        )
        destination_path = destination / "opencode.jsonc"
        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 0
        assert destination_path.read_bytes() == payload
