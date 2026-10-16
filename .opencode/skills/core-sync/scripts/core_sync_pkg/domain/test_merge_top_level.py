"""Behavior tests for the pure top-level JSON merge transformation: `merge_top_level`.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/domain/test_merge_top_level.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest  # noqa: E402

from _core_sync_testkit import (  # noqa: E402
    MERGE_MCP_DESTINATION,
    MERGE_MCP_RESULT,
    MERGE_MCP_SOURCE,
)
from core_sync_pkg.domain.errors import MalformedJsonc  # noqa: E402
from core_sync_pkg.domain.jsonc import parse_object  # noqa: E402
from core_sync_pkg.domain.merge import merge_top_level  # noqa: E402


class MergeTopLevelTests:
    """Merge source-owned top-level keys while preserving destination bytes."""

    def test_source_value_wins_on_conflict(self) -> None:
        merged = merge_top_level('{"theme": "dark"}', '{\n  "theme": "light"\n}\n')
        assert parse_object(merged) == {"theme": "dark"}

    def test_destination_only_key_and_comment_preserved(self) -> None:
        destination = (
            "{\n  // user preference\n  \"theme\": \"light\",\n"
            '  "custom": true\n}\n'
        )
        merged = merge_top_level('{"theme": "dark"}', destination)
        assert "// user preference" in merged
        assert '"custom": true' in merged
        assert parse_object(merged) == {"theme": "dark", "custom": True}

    def test_source_only_key_inserted(self) -> None:
        merged = merge_top_level(
            '{"theme": "dark", "model": "x"}', '{\n  "theme": "light"\n}\n'
        )
        assert parse_object(merged) == {"theme": "dark", "model": "x"}

    def test_destination_formatting_outside_touched_keys_preserved(self) -> None:
        destination = (
            "{\n  // header comment\n  \"theme\": \"light\",\n\n"
            '  "keep": {\n    "nested": 1\n  }\n}\n'
        )
        merged = merge_top_level('{"theme": "dark"}', destination)
        assert '"keep": {\n    "nested": 1\n  }' in merged
        assert "// header comment" in merged
        assert parse_object(merged) == {
            "theme": "dark",
            "keep": {"nested": 1},
        }

    def test_insertion_into_empty_object(self) -> None:
        merged = merge_top_level('{"a": 1}', "{}\n")
        assert parse_object(merged) == {"a": 1}
        assert merged.endswith("}\n")

    def test_merging_empty_source_is_a_noop(self) -> None:
        destination = '{\n  "a": 1\n}\n'
        assert merge_top_level("{}", destination) == destination

    def test_remerge_is_idempotent(self) -> None:
        source = '{"theme": "dark", "model": "x"}'
        destination = (
            '{\n  // keep\n  "theme": "light",\n  "other": 1\n}\n'
        )
        once = merge_top_level(source, destination)
        assert merge_top_level(source, once) == once

    def test_mcp_key_merges_servers_by_name(self) -> None:
        merged = merge_top_level(MERGE_MCP_SOURCE, MERGE_MCP_DESTINATION)
        assert parse_object(merged) == MERGE_MCP_RESULT

    def test_mcp_key_keeps_destination_comment_and_non_servers_child(self) -> None:
        merged = merge_top_level(MERGE_MCP_SOURCE, MERGE_MCP_DESTINATION)
        assert "// keep this comment" in merged
        assert '"enabled": true' in merged

    def test_mcp_key_inserts_source_only_server_with_member_indent(self) -> None:
        merged = merge_top_level(MERGE_MCP_SOURCE, MERGE_MCP_DESTINATION)
        assert '"core": {\n        "command": "core"\n      }' in merged

    def test_mcp_remerge_is_byte_idempotent(self) -> None:
        once = merge_top_level(MERGE_MCP_SOURCE, MERGE_MCP_DESTINATION)
        assert merge_top_level(MERGE_MCP_SOURCE, once) == once

    def test_mcp_key_replaced_wholesale_when_destination_has_no_mcp(self) -> None:
        merged = merge_top_level(MERGE_MCP_SOURCE, '{\n  "other": 1\n}\n')
        assert parse_object(merged) == {
            "other": 1,
            "mcp": {
                "servers": {
                    "core": {"command": "core"},
                    "shared": {"command": "source-shared"},
                }
            },
        }

    def test_mcp_key_replaced_wholesale_when_destination_mcp_not_object(self) -> None:
        merged = merge_top_level(MERGE_MCP_SOURCE, '{\n  "mcp": "legacy"\n}\n')
        assert parse_object(merged) == {
            "mcp": {
                "servers": {
                    "core": {"command": "core"},
                    "shared": {"command": "source-shared"},
                }
            },
        }

    def test_mcp_key_replaced_wholesale_when_servers_not_object(self) -> None:
        destination = '{\n  "mcp": {\n    "servers": []\n  }\n}\n'
        merged = merge_top_level(MERGE_MCP_SOURCE, destination)
        assert parse_object(merged) == {
            "mcp": {
                "servers": {
                    "core": {"command": "core"},
                    "shared": {"command": "source-shared"},
                }
            },
        }

    def test_non_mcp_object_key_still_replaced_wholesale(self) -> None:
        merged = merge_top_level(
            '{"agents": {"a": 1}}',
            '{\n  "agents": {\n    "a": 1,\n    "extra": 2\n  }\n}\n',
        )
        assert parse_object(merged) == {"agents": {"a": 1}}

    def test_non_object_source_rejected(self) -> None:
        with pytest.raises(MalformedJsonc):
            merge_top_level("[1, 2]", "{}")

    def test_malformed_destination_rejected(self) -> None:
        with pytest.raises(MalformedJsonc):
            merge_top_level('{"a": 1}', '{"a": }')
