"""Behavior tests for the pure `is_merged` predicate over top-level JSON objects.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/domain/test_is_merged.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest  # noqa: E402

from core_sync_pkg.domain.errors import MalformedJsonc  # noqa: E402
from core_sync_pkg.domain.merge import is_merged  # noqa: E402


class IsMergedTests:
    """Report whether every source top-level key is present with an equal value."""

    def test_true_when_source_keys_present_with_equal_values(self) -> None:
        destination = (
            '{\n  "theme": "dark",\n  "model": "x",\n  "extra": 1\n}\n'
        )
        assert is_merged('{"theme": "dark", "model": "x"}', destination) is True

    def test_false_when_value_differs(self) -> None:
        assert is_merged('{"theme": "dark"}', '{"theme": "light"}') is False

    def test_false_when_key_missing(self) -> None:
        assert is_merged('{"theme": "dark"}', '{"other": 1}') is False

    def test_ignores_destination_comments_and_formatting(self) -> None:
        assert is_merged('{"theme":"dark"}', '{\n  // c\n  "theme": "dark"\n}\n')

    def test_mcp_key_allows_extra_destination_server(self) -> None:
        source = '{"mcp": {"servers": {"core": {"command": "core"}}}}'
        destination = (
            '{"mcp": {"servers": {"core": {"command": "core"}, '
            '"local": {"command": "local"}}}}'
        )
        assert is_merged(source, destination) is True

    def test_mcp_key_false_when_core_server_missing(self) -> None:
        source = '{"mcp": {"servers": {"core": {"command": "core"}}}}'
        destination = '{"mcp": {"servers": {"local": {"command": "local"}}}}'
        assert is_merged(source, destination) is False

    def test_mcp_key_false_when_server_value_differs(self) -> None:
        source = '{"mcp": {"servers": {"core": {"command": "core"}}}}'
        destination = '{"mcp": {"servers": {"core": {"command": "other"}}}}'
        assert is_merged(source, destination) is False

    def test_mcp_key_ignores_destination_non_servers_children(self) -> None:
        source = '{"mcp": {"servers": {"core": {}}, "core_flag": true}}'
        destination = (
            '{"mcp": {"servers": {"core": {}, "local": {}}, "enabled": true}}'
        )
        assert is_merged(source, destination) is True

    def test_mcp_key_compared_exactly_when_not_an_object(self) -> None:
        assert is_merged('{"mcp": "a"}', '{"mcp": "a"}') is True
        assert is_merged('{"mcp": "a"}', '{"mcp": {"servers": {}}}') is False

    def test_mcp_key_compared_exactly_without_servers_object(self) -> None:
        source = '{"mcp": {"enabled": true}}'
        destination = '{"mcp": {"enabled": true, "servers": {"core": {}}}}'
        assert is_merged(source, destination) is False

    def test_mcp_key_compared_exactly_when_servers_not_object(self) -> None:
        source = '{"mcp": {"servers": []}}'
        assert is_merged(source, '{"mcp": {"servers": []}}') is True
        assert is_merged(source, '{"mcp": {"servers": [1]}}') is False

    def test_empty_source_is_always_merged(self) -> None:
        assert is_merged("{}", '{"anything": [1, 2]}') is True

    def test_non_object_destination_rejected(self) -> None:
        with pytest.raises(MalformedJsonc):
            is_merged('{"a": 1}', "[1]")

    def test_malformed_destination_rejected(self) -> None:
        with pytest.raises(MalformedJsonc):
            is_merged('{"a": 1}', "{")
