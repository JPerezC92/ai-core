"""CLI behavior tests for merge-mode `apply`: source-wins, comment preservation.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_merge_apply.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    REV_A,
    _apply_args,
    _merge_setup,
)
from core_sync_pkg.domain.jsonc import parse_object  # noqa: E402
from core_sync_pkg.domain.reconciliation import (  # noqa: E402
    reconciliation_report_path,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import load_bindings  # noqa: E402


class MergeApplyTests:
    """Verify `apply` merges top-level keys and preserves destination extras."""

    def test_apply_merges_source_keys_and_keeps_destination_only_key(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = _merge_setup(tmp_path)
        destination_path = destination / "opencode.jsonc"

        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 0

        written = destination_path.read_text(encoding="utf-8")
        assert "// destination-only comment" in written
        assert '"custom": 42' in written
        assert parse_object(written) == {
            "theme": "dark",
            "shared": "source",
            "custom": 42,
        }

    def test_apply_creates_no_report_and_no_pending(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _merge_setup(
            tmp_path, pending=["opencode.jsonc"]
        )

        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 0

        updated = load_bindings(bindings_path)
        assert updated is not None
        assert updated["pending"] == []
        assert not reconciliation_report_path(bindings_path).exists()
        header = (destination / "opencode.jsonc").read_text(encoding="utf-8")
        assert "core:begin" not in header

    def test_apply_is_idempotent(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _merge_setup(tmp_path)
        destination_path = destination / "opencode.jsonc"

        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 0
        first = destination_path.read_bytes()
        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 0
        assert destination_path.read_bytes() == first

    def test_apply_reports_missing_destination(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _merge_setup(
            tmp_path, destination_content=None
        )
        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 1
        assert not (destination / "opencode.jsonc").exists()

    def test_apply_invalid_when_destination_malformed(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _merge_setup(
            tmp_path, destination_content='{"theme": }'
        )
        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 2

    def test_apply_invalid_when_source_malformed(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _merge_setup(
            tmp_path, source_content="[1, 2, 3]\n"
        )
        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 2
