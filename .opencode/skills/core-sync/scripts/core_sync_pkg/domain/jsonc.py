"""Pure, IO-free JSON/JSONC object parser: comments, trailing commas, and top-level spans."""

from __future__ import annotations

import re
from typing import TypedDict

from core_sync_pkg.domain.errors import MalformedJsonc

_NUMBER_RE = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?")
_WHITESPACE = " \t\r\n"
_HEX_DIGITS = frozenset("0123456789abcdefABCDEF")
_SIMPLE_ESCAPES = {
    '"': '"',
    "\\": "\\",
    "/": "/",
    "b": "\b",
    "f": "\f",
    "n": "\n",
    "r": "\r",
    "t": "\t",
}


class KeyValueSpan(TypedDict):
    """One top-level member: its key, parsed value, and raw source offsets."""

    key: str
    value: object
    member_start: int
    value_start: int
    value_end: int


class ObjectSpans(TypedDict):
    """A parsed top-level object plus the offsets a top-level merge splices at."""

    value: dict[str, object]
    spans: list[KeyValueSpan]
    close_index: int
    trailing_comma: bool


def parse_object_spans(text: str) -> ObjectSpans:
    """Parse a JSON/JSONC object document into its mapping, member spans, and offsets."""
    return _Scanner(text).parse_document()


def parse_object(text: str) -> dict[str, object]:
    """Parse a JSON/JSONC document whose top level is an object.

    Comments (`//` and `/* */`) and trailing commas are tolerated. A non-object
    top level or malformed syntax raises :class:`MalformedJsonc`.
    """
    return parse_object_spans(text)["value"]


class _Scanner:
    """A recursive-descent scanner over one JSON/JSONC document string."""

    def __init__(self, text: str) -> None:
        self._text = text
        self._pos = 0
        self._length = len(text)

    def parse_document(self) -> ObjectSpans:
        """Parse the whole document, requiring a single top-level object."""
        self._skip_trivia()
        if self._pos >= self._length or self._text[self._pos] != "{":
            raise MalformedJsonc("document top level must be a JSON object")
        value, spans, close_index, trailing_comma = self._parse_object_body()
        self._skip_trivia()
        if self._pos != self._length:
            raise MalformedJsonc(
                f"unexpected content after the top-level object at offset {self._pos}"
            )
        return {
            "value": value,
            "spans": spans,
            "close_index": close_index,
            "trailing_comma": trailing_comma,
        }

    def _parse_object_body(
        self,
    ) -> tuple[dict[str, object], list[KeyValueSpan], int, bool]:
        """Parse an object starting at `{`, returning its map, spans, and offsets."""
        if self._pos >= self._length or self._text[self._pos] != "{":
            raise MalformedJsonc(f"expected '{{' at offset {self._pos}")
        self._pos += 1
        result: dict[str, object] = {}
        spans: list[KeyValueSpan] = []
        trailing_comma = False
        self._skip_trivia()
        if self._pos < self._length and self._text[self._pos] == "}":
            close_index = self._pos
            self._pos += 1
            return result, spans, close_index, trailing_comma
        while True:
            self._skip_trivia()
            if self._pos >= self._length or self._text[self._pos] != '"':
                raise MalformedJsonc(f"expected an object key at offset {self._pos}")
            member_start = self._pos
            key = self._parse_string()
            self._skip_trivia()
            if self._pos >= self._length or self._text[self._pos] != ":":
                raise MalformedJsonc(
                    f"expected ':' after key {key!r} at offset {self._pos}"
                )
            self._pos += 1
            self._skip_trivia()
            value_start = self._pos
            value = self._parse_value()
            value_end = self._pos
            result[key] = value
            spans.append(
                {
                    "key": key,
                    "value": value,
                    "member_start": member_start,
                    "value_start": value_start,
                    "value_end": value_end,
                }
            )
            self._skip_trivia()
            if self._pos < self._length and self._text[self._pos] == ",":
                self._pos += 1
                self._skip_trivia()
                if self._pos < self._length and self._text[self._pos] == "}":
                    trailing_comma = True
                    close_index = self._pos
                    self._pos += 1
                    return result, spans, close_index, trailing_comma
                continue
            if self._pos < self._length and self._text[self._pos] == "}":
                close_index = self._pos
                self._pos += 1
                return result, spans, close_index, trailing_comma
            raise MalformedJsonc(f"expected ',' or '}}' at offset {self._pos}")

    def _parse_value(self) -> object:
        """Parse one JSON value at the current position."""
        if self._pos >= self._length:
            raise MalformedJsonc("unexpected end of document while parsing a value")
        char = self._text[self._pos]
        if char == "{":
            value, _spans, _close, _trailing = self._parse_object_body()
            return value
        if char == "[":
            return self._parse_array()
        if char == '"':
            return self._parse_string()
        if char == "t":
            return self._parse_literal("true", True)
        if char == "f":
            return self._parse_literal("false", False)
        if char == "n":
            return self._parse_literal("null", None)
        if char == "-" or char in "0123456789":
            return self._parse_number()
        raise MalformedJsonc(f"unexpected character {char!r} at offset {self._pos}")

    def _parse_array(self) -> list[object]:
        """Parse an array starting at `[`, allowing trailing commas."""
        self._pos += 1
        items: list[object] = []
        self._skip_trivia()
        if self._pos < self._length and self._text[self._pos] == "]":
            self._pos += 1
            return items
        while True:
            self._skip_trivia()
            items.append(self._parse_value())
            self._skip_trivia()
            if self._pos < self._length and self._text[self._pos] == ",":
                self._pos += 1
                self._skip_trivia()
                if self._pos < self._length and self._text[self._pos] == "]":
                    self._pos += 1
                    return items
                continue
            if self._pos < self._length and self._text[self._pos] == "]":
                self._pos += 1
                return items
            raise MalformedJsonc(f"expected ',' or ']' at offset {self._pos}")

    def _parse_literal(self, word: str, value: bool | None) -> bool | None:
        """Consume an exact `true`, `false`, or `null` token."""
        if not self._text.startswith(word, self._pos):
            raise MalformedJsonc(f"invalid literal at offset {self._pos}")
        self._pos += len(word)
        return value

    def _parse_number(self) -> int | float:
        """Parse a JSON number into an int or float."""
        match = _NUMBER_RE.match(self._text, self._pos)
        if match is None:
            raise MalformedJsonc(f"invalid number at offset {self._pos}")
        token = match.group(0)
        self._pos = match.end()
        if any(marker in token for marker in (".", "e", "E")):
            return float(token)
        return int(token)

    def _parse_string(self) -> str:
        """Parse a double-quoted string, decoding JSON escapes."""
        self._pos += 1
        characters: list[str] = []
        while self._pos < self._length:
            char = self._text[self._pos]
            if char == '"':
                self._pos += 1
                return "".join(characters)
            if char == "\\":
                characters.append(self._parse_escape())
                continue
            if char < " ":
                raise MalformedJsonc(
                    f"unescaped control character in a string at offset {self._pos}"
                )
            characters.append(char)
            self._pos += 1
        raise MalformedJsonc("unterminated string")

    def _parse_escape(self) -> str:
        """Decode one JSON escape sequence, starting at its backslash."""
        escape_offset = self._pos
        self._pos += 1
        if self._pos >= self._length:
            raise MalformedJsonc("unterminated escape sequence")
        char = self._text[self._pos]
        if char == "u":
            self._pos += 1
            return self._parse_unicode_escape()
        if char in _SIMPLE_ESCAPES:
            self._pos += 1
            return _SIMPLE_ESCAPES[char]
        raise MalformedJsonc(f"invalid escape sequence at offset {escape_offset}")

    def _parse_unicode_escape(self) -> str:
        """Decode a `\\uXXXX` escape, combining a surrogate pair when present."""
        code = self._read_hex4()
        if 0xD800 <= code <= 0xDBFF and self._text.startswith("\\u", self._pos):
            self._pos += 2
            low = self._read_hex4()
            if not 0xDC00 <= low <= 0xDFFF:
                raise MalformedJsonc("invalid surrogate pair in a \\u escape")
            combined = 0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00)
            return chr(combined)
        return chr(code)

    def _read_hex4(self) -> int:
        """Read exactly four hexadecimal digits at the current position."""
        end = self._pos + 4
        if end > self._length:
            raise MalformedJsonc("truncated \\u escape")
        digits = self._text[self._pos : end]
        if any(digit not in _HEX_DIGITS for digit in digits):
            raise MalformedJsonc(f"invalid \\u escape at offset {self._pos}")
        self._pos = end
        return int(digits, 16)

    def _skip_trivia(self) -> None:
        """Advance past whitespace and comments."""
        while self._pos < self._length:
            char = self._text[self._pos]
            if char in _WHITESPACE:
                self._pos += 1
            elif char == "/" and self._text.startswith("//", self._pos):
                self._skip_line_comment()
            elif char == "/" and self._text.startswith("/*", self._pos):
                self._skip_block_comment()
            else:
                return

    def _skip_line_comment(self) -> None:
        """Advance past a `//` comment up to the end of its line."""
        newline = self._text.find("\n", self._pos)
        self._pos = self._length if newline == -1 else newline

    def _skip_block_comment(self) -> None:
        """Advance past a `/* */` comment, raising when it is unterminated."""
        start = self._pos
        end = self._text.find("*/", self._pos + 2)
        if end == -1:
            raise MalformedJsonc(f"unterminated block comment at offset {start}")
        self._pos = end + 2
