"""Unit tests for pure Markdown byte scan against a minimum policy."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from markdown_text_pkg.domain.models import (  # noqa: E402
    Policy,
    ScalarFinding,
    Utf8Finding,
)
from markdown_text_pkg.domain.policy import parse_policy  # noqa: E402
from markdown_text_pkg.domain.scan import (  # noqa: E402
    escape_for_diagnostic,
    scan_markdown_bytes,
)

DISPLAY_PATH = "sample.md"
EN_DASH = "\u2013"
ZWSP = "\u200b"
ZWNJ = "\u200c"
ZWJ = "\u200d"
VS16 = "\ufe0f"
NUL = "\x00"
SOH = "\x01"
TAB = "\t"
CR = "\r"
FAMILY = "\U0001f468" + ZWJ + "\U0001f469" + ZWJ + "\U0001f467"
SUN = "\u2600" + VS16
ACCENTED = "café"
NON_LATIN = "Привет"
EMOJI = "😀"
ESCAPED_ZWSP_SPELLING = "U+200B"
INLINE_RANGE = f"`1{EN_DASH}3`"
PROSE_RANGE = f"1{EN_DASH}3"


def create(**overrides: object) -> dict[str, object]:
    """Return the fixed minimum valid schema v1 policy document."""

    document: dict[str, object] = {
        "version": 1,
        "id": "min-markdown-text",
        "default_classification": "allow",
        "decoding": {
            "encoding": "utf-8",
            "invalid_sequence": {
                "id": "ERR-UTF8",
                "severity": "error",
                "class": "invalid_utf8",
                "rationale": "ill-formed UTF-8",
            },
        },
        "rules": [
            {
                "id": "ERR-NUL",
                "severity": "error",
                "class": "nul",
                "rationale": "NUL",
                "codepoints": [{"cp": 0, "hex": "U+0000"}],
            },
            {
                "id": "ERR-C0",
                "severity": "error",
                "class": "c0_controls",
                "rationale": "C0",
                "ranges": [
                    {
                        "start": 1,
                        "end": 8,
                        "start_hex": "U+0001",
                        "end_hex": "U+0008",
                    }
                ],
            },
            {
                "id": "WARN-ZWSP",
                "severity": "warning",
                "class": "zero_width_space",
                "rationale": "ZWSP",
                "codepoints": [{"cp": 8203, "hex": "U+200B"}],
            },
        ],
        "editor_projection": {
            "scope": "[markdown]",
            "setting_key": "gremlins.characters",
            "overrides": [
                {
                    "codepoint": 8211,
                    "hex": "U+2013",
                    "gremlins_key": "2013",
                    "severity": "none",
                    "description": "en dash",
                }
            ],
        },
    }
    document.update(copy.deepcopy(overrides))
    return document


def parsed() -> Policy:
    """Parse the minimum policy used by every scan case."""

    result = parse_policy(create())
    assert isinstance(result, Policy)
    return result


def create_allowed_prose() -> bytes:
    """Return permitted punctuation, ranges, Unicode, emoji, joiners, and escaped spelling."""

    text = " ".join(
        [
            "ASCII",
            ACCENTED,
            NON_LATIN,
            EMOJI,
            FAMILY,
            f"a{ZWNJ}b",
            SUN,
            PROSE_RANGE,
            INLINE_RANGE,
            ESCAPED_ZWSP_SPELLING,
            TAB,
        ]
    )
    return f"{text}\n".encode("utf-8")


def create_crlf() -> bytes:
    """Return a CRLF line pair; CR is a scalar, LF is the line break."""

    return f"a{CR}\nb".encode("utf-8")


def create_nul() -> bytes:
    """Return one NUL on the first column."""

    return f"{NUL}ok\n".encode("utf-8")


def create_c0() -> bytes:
    """Return one unexpected C0 control from the min policy range."""

    return f"x{SOH}y".encode("utf-8")


def create_zwsp_line() -> bytes:
    """Return a line containing a real zero-width space."""

    return f"ab{ZWSP}cd".encode("utf-8")


def create_invalid_utf8() -> bytes:
    """Return valid prefix `ab\\nc` then one ill-formed byte."""

    return b"ab\nc\xff"


INVALID_UTF8_LINE = 2
INVALID_UTF8_COLUMN = 2
INVALID_UTF8_BYTE_OFFSET = 5


class ScanAllowedTests:
    """Default-allow Unicode, typography, joiners, and escaped spellings."""

    def test_permitted_prose_has_no_findings(self) -> None:
        findings = scan_markdown_bytes(create_allowed_prose(), parsed(), DISPLAY_PATH)
        assert findings == ()

    def test_unknown_codepoint_is_allowed(self) -> None:
        findings = scan_markdown_bytes("A".encode("utf-8"), parsed(), DISPLAY_PATH)
        assert findings == ()

    def test_tab_lf_and_cr_are_allowed(self) -> None:
        payload = f"a{TAB}b{CR}\nc".encode("utf-8")
        findings = scan_markdown_bytes(payload, parsed(), DISPLAY_PATH)
        assert findings == ()


class ScanWarningAndErrorTests:
    """Policy-backed warnings and errors, including UTF-8 envelope positions."""

    def test_zwsp_is_a_warning_at_unicode_column(self) -> None:
        findings = scan_markdown_bytes(create_zwsp_line(), parsed(), DISPLAY_PATH)
        assert len(findings) == 1
        finding = findings[0]
        assert isinstance(finding, ScalarFinding)
        assert finding.rule_id == "WARN-ZWSP"
        assert finding.severity == "warning"
        assert finding.line == 1
        assert finding.column == 3
        assert finding.codepoint == 8203
        assert "U+200B" in finding.excerpt
        assert ZWSP not in finding.excerpt

    def test_nul_is_an_error_at_column_one(self) -> None:
        findings = scan_markdown_bytes(create_nul(), parsed(), DISPLAY_PATH)
        assert len(findings) == 1
        finding = findings[0]
        assert isinstance(finding, ScalarFinding)
        assert finding.rule_id == "ERR-NUL"
        assert finding.severity == "error"
        assert finding.line == 1
        assert finding.column == 1
        assert finding.codepoint == 0

    def test_c0_control_is_an_error(self) -> None:
        findings = scan_markdown_bytes(create_c0(), parsed(), DISPLAY_PATH)
        assert len(findings) == 1
        finding = findings[0]
        assert isinstance(finding, ScalarFinding)
        assert finding.rule_id == "ERR-C0"
        assert finding.column == 2

    def test_invalid_utf8_reports_first_offset_and_stops(self) -> None:
        payload = create_invalid_utf8() + b"\x00"
        findings = scan_markdown_bytes(payload, parsed(), DISPLAY_PATH)
        assert len(findings) == 1
        finding = findings[0]
        assert isinstance(finding, Utf8Finding)
        assert finding.rule_id == "ERR-UTF8"
        assert finding.severity == "error"
        assert finding.line == INVALID_UTF8_LINE
        assert finding.column == INVALID_UTF8_COLUMN
        assert finding.byte_offset == INVALID_UTF8_BYTE_OFFSET

    def test_crlf_does_not_treat_cr_as_a_line_break(self) -> None:
        findings = scan_markdown_bytes(create_crlf(), parsed(), DISPLAY_PATH)
        assert findings == ()
        nul_second_line = f"a{CR}\n{NUL}".encode("utf-8")
        findings = scan_markdown_bytes(nul_second_line, parsed(), DISPLAY_PATH)
        assert len(findings) == 1
        finding = findings[0]
        assert isinstance(finding, ScalarFinding)
        assert finding.line == 2
        assert finding.column == 1

    def test_posix_display_path_is_normalized(self) -> None:
        findings = scan_markdown_bytes(create_nul(), parsed(), r"dir\file.md")
        assert findings[0].path == "dir/file.md"


class ScanEscapeTests:
    """Diagnostic excerpts never retain raw controls."""

    def test_escape_replaces_controls_with_hex_spellings(self) -> None:
        assert escape_for_diagnostic(f"a{NUL}b") == "aU+0000b"
        assert ZWSP not in escape_for_diagnostic(f"a{ZWSP}b")
        assert "U+200B" in escape_for_diagnostic(f"a{ZWSP}b")
