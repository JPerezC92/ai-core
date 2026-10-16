"""CLI behavior tests for merge-mode `init`: merge existing, never create.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_merge_init.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    MERGE_MCP_DESTINATION,
    MERGE_MCP_RESULT,
    MERGE_MCP_SOURCE,
    REV_A,
    _init_args,
    _merge_setup,
)
from core_sync_pkg.domain.jsonc import parse_object  # noqa: E402
from core_sync_pkg.domain.reconciliation import (  # noqa: E402
    reconciliation_report_path,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import load_bindings  # noqa: E402


class MergeInitTests:
    """Verify `init` merges existing destinations and never creates merge targets."""

    def test_init_merges_existing_destination_without_report_or_pending(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = _merge_setup(tmp_path)

        assert main(_init_args(source, destination, bindings_path, REV_A)) == 0

        written = (destination / "opencode.jsonc").read_text(encoding="utf-8")
        assert parse_object(written) == {
            "theme": "dark",
            "shared": "source",
            "custom": 42,
        }
        updated = load_bindings(bindings_path)
        assert updated is not None
        assert updated["pending"] == []
        assert not reconciliation_report_path(bindings_path).exists()

    def test_init_reports_missing_destination_and_creates_nothing(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = _merge_setup(
            tmp_path, destination_content=None
        )
        assert main(_init_args(source, destination, bindings_path, REV_A)) == 1
        assert not (destination / "opencode.jsonc").exists()

    def test_init_keeps_destination_mcp_server_and_inserts_core_servers(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = _merge_setup(
            tmp_path,
            source_content=MERGE_MCP_SOURCE,
            destination_content=MERGE_MCP_DESTINATION,
        )

        assert main(_init_args(source, destination, bindings_path, REV_A)) == 0

        written = (destination / "opencode.jsonc").read_text(encoding="utf-8")
        assert parse_object(written) == MERGE_MCP_RESULT

    def test_init_invalid_when_destination_malformed(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _merge_setup(
            tmp_path, destination_content='{"theme": }'
        )
        assert main(_init_args(source, destination, bindings_path, REV_A)) == 2

    def test_init_invalid_when_source_malformed(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _merge_setup(
            tmp_path, source_content="[1, 2, 3]\n"
        )
        assert main(_init_args(source, destination, bindings_path, REV_A)) == 2
