"""CLI behavior tests for merge-mode `check` exit codes 0/1/2.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_merge_check.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    MERGE_DESTINATION_MERGED,
    MERGE_MCP_DESTINATION_CURRENT,
    MERGE_MCP_DESTINATION_MISSING_CORE,
    MERGE_MCP_DESTINATION_STALE_SHARED,
    MERGE_MCP_SOURCE,
    REV_A,
    _check_args,
    _merge_setup,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402


class MergeCheckTests:
    """Verify `check` accepts a merged destination and reports drift/malformed."""

    def test_current_when_every_source_key_present(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _merge_setup(
            tmp_path, destination_content=MERGE_DESTINATION_MERGED
        )
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 0

    def test_current_when_destination_added_mcp_server(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _merge_setup(
            tmp_path,
            source_content=MERGE_MCP_SOURCE,
            destination_content=MERGE_MCP_DESTINATION_CURRENT,
        )
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 0

    def test_drift_when_core_mcp_server_missing(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _merge_setup(
            tmp_path,
            source_content=MERGE_MCP_SOURCE,
            destination_content=MERGE_MCP_DESTINATION_MISSING_CORE,
        )
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1

    def test_drift_when_mcp_server_value_differs(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _merge_setup(
            tmp_path,
            source_content=MERGE_MCP_SOURCE,
            destination_content=MERGE_MCP_DESTINATION_STALE_SHARED,
        )
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1

    def test_drift_when_source_key_missing(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _merge_setup(
            tmp_path, destination_content='{\n  "shared": "source"\n}\n'
        )
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1

    def test_drift_when_source_value_differs(self, tmp_path: Path) -> None:
        destination_content = (
            '{\n  "shared": "source",\n  "theme": "light"\n}\n'
        )
        source, destination, bindings_path = _merge_setup(
            tmp_path, destination_content=destination_content
        )
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1

    def test_drift_when_destination_missing(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _merge_setup(
            tmp_path, destination_content=None
        )
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1

    def test_invalid_when_destination_malformed(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _merge_setup(
            tmp_path, destination_content='{"theme": }'
        )
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 2

    def test_invalid_when_source_malformed(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _merge_setup(
            tmp_path, source_content="[1, 2, 3]\n"
        )
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 2
