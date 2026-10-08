"""Test cleanup of stale raw-mode paths from pending during apply and init.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_pending_normalization.py
"""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import (
    RAW_SOURCE_BYTES,
    REV_A,
    ROOT_TEXT,
    SOURCE_MARKED,
    _apply_args,
    _binding_entry,
    _bindings_with_entries,
    _init_args,
    _write_bytes_file,
    _write_file,
    uc,
)


class RawPendingNormalizationTests:
    """Remove stale raw-bound pending entries while preserving region entries."""

    def _setup(
        self,
        tmp_path: Path,
        *,
        pending: list[str],
        pinned: str = REV_A,
        preexisting_raw_block: bool = False,
    ) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", SOURCE_MARKED)
        _write_bytes_file(source, "opencode.jsonc", RAW_SOURCE_BYTES)
        _write_bytes_file(destination, "opencode.jsonc", RAW_SOURCE_BYTES)
        root_text = ROOT_TEXT
        if preexisting_raw_block:
            root_text = uc.sync_reconciliation_blocker(
                root_text, ["opencode.jsonc"]
            )
        _write_file(destination, "AGENTS.md", root_text)

        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_with_entries(
                pinned,
                [
                    _binding_entry("agent.md", ["agent.md"], "region"),
                    _binding_entry("opencode.jsonc", ["opencode.jsonc"], "raw"),
                ],
                pending,
                root="AGENTS.md",
            ),
        )
        return source, destination, bindings_path

    def test_apply_clears_raw_pending_and_preserves_region_pending(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = self._setup(
            tmp_path, pending=["agent.md", "opencode.jsonc"], pinned="b" * 40
        )

        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 0

        updated = uc.load_bindings(bindings_path)
        assert updated is not None
        assert updated["pending"] == ["agent.md"]
        assert uc.RECONCILE_BEGIN in (destination / "AGENTS.md").read_text(
            encoding="utf-8"
        )

    def test_init_clears_raw_pending_and_preserves_region_pending(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = self._setup(
            tmp_path, pending=["agent.md", "opencode.jsonc"]
        )

        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 0

        updated = uc.load_bindings(bindings_path)
        assert updated is not None
        assert updated["pending"] == ["agent.md"]
        assert not uc.reconciliation_report_path(bindings_path).exists()
        assert uc.RECONCILE_BEGIN in (destination / "AGENTS.md").read_text(
            encoding="utf-8"
        )
