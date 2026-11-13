"""Pure Markdown byte scan against a validated policy; no filesystem IO."""

from __future__ import annotations

import unicodedata

from markdown_text_pkg.domain.models import (
    Finding,
    Policy,
    ScalarFinding,
    Utf8Finding,
)
from markdown_text_pkg.domain.policy import classify_codepoint


def escape_for_diagnostic(text: str) -> str:
    """Replace control and other non-printable code points with U+XXXX spellings."""

    parts: list[str] = []
    for char in text:
        if _is_safe_diagnostic_char(char):
            parts.append(char)
        else:
            parts.append(f"U+{ord(char):04X}")
    return "".join(parts)


def scan_markdown_bytes(data: bytes, policy: Policy, path: str) -> tuple[Finding, ...]:
    """Scan decoded scalars against policy rules; stop after the first invalid UTF-8."""

    display = path.replace("\\", "/")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return (_utf8_finding(data, policy, display, exc.start),)

    findings: list[Finding] = []
    lines = text.split("\n")
    for line_number, line in enumerate(lines, start=1):
        excerpt = escape_for_diagnostic(line)
        for column, char in enumerate(line, start=1):
            codepoint = ord(char)
            rule = classify_codepoint(policy, codepoint)
            if rule is None:
                continue
            name = unicodedata.name(char, "-")
            findings.append(
                ScalarFinding(
                    path=display,
                    line=line_number,
                    column=column,
                    severity=rule.severity,
                    rule_id=rule.id,
                    codepoint=codepoint,
                    unicode_name=name if name else "-",
                    excerpt=excerpt,
                )
            )
    return tuple(findings)


def _utf8_finding(
    data: bytes, policy: Policy, path: str, start: int
) -> Utf8Finding:
    """Build the envelope finding from the valid UTF-8 prefix and first invalid byte."""

    prefix = data[:start]
    line = 1 + prefix.count(b"\n")
    last_newline = prefix.rfind(b"\n")
    tail = prefix[last_newline + 1 :] if last_newline >= 0 else prefix
    column = 1 + len(tail.decode("utf-8"))
    envelope = policy.decoding.invalid_sequence
    return Utf8Finding(
        path=path,
        line=line,
        column=column,
        severity=envelope.severity,
        rule_id=envelope.id,
        byte_offset=start + 1,
    )


def _is_safe_diagnostic_char(char: str) -> bool:
    """Allow printable characters that cannot inject controls into diagnostics."""

    if not char.isprintable():
        return False
    return unicodedata.category(char) not in {"Cc", "Cf", "Cs", "Co", "Cn"}
