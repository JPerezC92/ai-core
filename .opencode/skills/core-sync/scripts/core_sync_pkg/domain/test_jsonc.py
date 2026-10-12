"""Behavior tests for the pure JSONC object parser: `parse_object` / `parse_object_spans`.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/domain/test_jsonc.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest  # noqa: E402

from core_sync_pkg.domain.errors import MalformedJsonc  # noqa: E402
from core_sync_pkg.domain.jsonc import (  # noqa: E402
    parse_object,
    parse_object_spans,
)


class JsoncParserTests:
    """Parse object-only JSONC documents and report malformed input."""

    def test_plain_object(self) -> None:
        assert parse_object('{"a": 1, "b": "two"}') == {"a": 1, "b": "two"}

    def test_line_comments_ignored(self) -> None:
        text = '{\n  // leading\n  "a": 1, // trailing\n  // between\n  "b": 2\n}\n'
        assert parse_object(text) == {"a": 1, "b": 2}

    def test_block_comments_ignored(self) -> None:
        text = '{ /* one */ "a": 1 /* two */ }'
        assert parse_object(text) == {"a": 1}

    def test_trailing_commas_allowed(self) -> None:
        text = '{"a": 1, "b": [1, 2, 3,],}'
        assert parse_object(text) == {"a": 1, "b": [1, 2, 3]}

    def test_nested_objects_and_arrays(self) -> None:
        text = '{"outer": {"inner": [1, {"deep": true}]}, "n": null}'
        assert parse_object(text) == {
            "outer": {"inner": [1, {"deep": True}]},
            "n": None,
        }

    def test_string_escapes(self) -> None:
        text = r'{"s": "a\"b\\c\n\t\u0041"}'
        assert parse_object(text) == {"s": 'a"b\\c\n\tA'}

    def test_surrogate_pair_escape(self) -> None:
        text = r'{"s": "\uD83D\uDE00"}'
        assert parse_object(text) == {"s": "\U0001F600"}

    def test_empty_object(self) -> None:
        assert parse_object("{}") == {}
        assert parse_object("{ // nothing\n }") == {}

    def test_spans_report_member_and_value_offsets(self) -> None:
        text = '{\n  // keep\n  "b": 2,\n  "a": [1]\n}\n'
        parsed = parse_object_spans(text)
        assert parsed["close_index"] == text.rindex("}")
        assert parsed["trailing_comma"] is False
        assert [span["key"] for span in parsed["spans"]] == ["b", "a"]
        first, second = parsed["spans"]
        assert text[first["member_start"] : first["value_end"]] == '"b": 2'
        assert text[second["value_start"] : second["value_end"]] == "[1]"

    def test_trailing_comma_flag(self) -> None:
        assert parse_object_spans('{"a": 1,}')["trailing_comma"] is True

    @pytest.mark.parametrize(
        "text",
        ["[1, 2, 3]", "42", '"a string"', "true", "", "   "],
        ids=["array", "number", "string", "literal", "empty", "whitespace"],
    )
    def test_non_object_top_level_rejected(self, text: str) -> None:
        with pytest.raises(MalformedJsonc):
            parse_object(text)

    @pytest.mark.parametrize(
        "text",
        [
            '{"a": }',
            '{"a" 1}',
            "{a: 1}",
            '{"a": 1,, "b": 2}',
            '{"a": "unterminated}',
            '{"a": tru}',
            '{"a": 1} trailing',
            "{ /* unterminated",
            '{"a": 01}',
        ],
        ids=[
            "missing-value",
            "missing-colon",
            "unquoted-key",
            "double-comma",
            "unterminated-string",
            "bad-literal",
            "trailing-content",
            "unterminated-comment",
            "leading-zero",
        ],
    )
    def test_malformed_documents_rejected(self, text: str) -> None:
        with pytest.raises(MalformedJsonc):
            parse_object(text)
