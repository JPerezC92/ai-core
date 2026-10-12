"""Test cleanup of stale raw-mode paths from pending during apply and init.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_pending_normalization.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
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
)
from core_sync_pkg.domain.constants import RECONCILE_BEGIN  # noqa: E402
from core_sync_pkg.domain.reconciliation import (  # noqa: E402
    reconciliation_report_path,
    sync_reconciliation_blocker,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import (  # noqa: E402
    load_bindings,
    save_bindings,
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
            root_text = sync_reconciliation_blocker(
                root_text, ["opencode.jsonc"]
            )
        _write_file(destination, "AGENTS.md", root_text)

        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
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

        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 0

        updated = load_bindings(bindings_path)
        assert updated is not None
        assert updated["pending"] == ["agent.md"]
        assert RECONCILE_BEGIN in (destination / "AGENTS.md").read_text(
            encoding="utf-8"
        )

    def test_init_clears_raw_pending_and_preserves_region_pending(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = self._setup(
            tmp_path, pending=["agent.md", "opencode.jsonc"]
        )

        assert main(_init_args(source, destination, bindings_path, REV_A)) == 0

        updated = load_bindings(bindings_path)
        assert updated is not None
        assert updated["pending"] == ["agent.md"]
        assert not reconciliation_report_path(bindings_path).exists()
        assert RECONCILE_BEGIN in (destination / "AGENTS.md").read_text(
            encoding="utf-8"
        )
