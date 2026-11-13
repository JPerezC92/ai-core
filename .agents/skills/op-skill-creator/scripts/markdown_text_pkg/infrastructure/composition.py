"""Composition root: parse CLI, wire adapters, serialize diagnostics, and map exits."""

from __future__ import annotations

import argparse
import io
import sys
from collections.abc import Sequence

from markdown_text_pkg.application.check_text import CheckText
from markdown_text_pkg.domain.models import (
    EDITOR_DRIFT_ID,
    CheckOutcome,
    DomainError,
    EditorDriftFinding,
    Finding,
    Utf8Finding,
)
from markdown_text_pkg.domain.policy import canonical_hex
from markdown_text_pkg.domain.scan import escape_for_diagnostic
from markdown_text_pkg.infrastructure.filesystem import MarkdownFilesystem, PolicyLoader


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments, execute the check, write diagnostics, and return the exit code."""

    sys.stdout = _configure_stdio(sys.stdout)
    sys.stderr = _configure_stdio(sys.stderr)
    parser = _build_parser()
    args = parser.parse_args(None if argv is None else list(argv))
    outcome = CheckText(PolicyLoader(), MarkdownFilesystem()).execute(
        policy_path=args.policy,
        roots=tuple(args.paths),
        editor_path=args.check_editor,
    )
    return _render(outcome)


def _build_parser() -> argparse.ArgumentParser:
    """Build the required --policy CLI with optional editor check and explicit paths."""

    parser = argparse.ArgumentParser(
        prog="check_markdown_text.py",
        description=(
            "Read-only Markdown text-integrity checker. "
            "Requires --policy PATH and one or more explicit Markdown file or directory paths."
        ),
        epilog="Exit codes: 0 no errors (warnings allowed), 1 content errors or EDITOR-DRIFT, 2 policy/input/IO.",
    )
    parser.add_argument(
        "--policy",
        required=True,
        metavar="PATH",
        help="caller-supplied policy JSON path (required; no default location)",
    )
    parser.add_argument(
        "--check-editor",
        default=None,
        metavar="PATH",
        help="optional settings JSON path for representable editor-projection comparison",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        metavar="PATH",
        help="explicit Markdown file or directory paths (no implicit repository scan)",
    )
    return parser


def _render(outcome: CheckOutcome) -> int:
    """Write findings to stdout, failures to stderr, and map the CLI exit code."""

    for failure in outcome.failures:
        sys.stderr.write(_format_failure(failure))
        sys.stderr.write("\n")
    for finding in outcome.findings:
        sys.stdout.write(_format_finding(finding))
        sys.stdout.write("\n")
    if outcome.failures:
        return 2
    if any(_is_error_finding(finding) for finding in outcome.findings):
        return 1
    return 0


def _format_failure(failure: DomainError) -> str:
    """Serialize one policy/input/IO failure for stderr."""

    return escape_for_diagnostic(f"{failure.code}: {failure.message}")


def _format_finding(finding: Finding) -> str:
    """Serialize one stdout diagnostic line with escaped controls."""

    path = escape_for_diagnostic(finding.path.replace("\\", "/"))
    if isinstance(finding, Utf8Finding):
        rule_id = escape_for_diagnostic(finding.rule_id)
        severity = escape_for_diagnostic(finding.severity)
        return (
            f"{path}:{finding.line}:{finding.column}: "
            f"{severity} {rule_id} byte {finding.byte_offset}"
        )
    if isinstance(finding, EditorDriftFinding):
        missing = ",".join(_sanitize_ascii_key(key) for key in finding.missing)
        extra = ",".join(_sanitize_ascii_key(key) for key in finding.extra)
        mismatched = ",".join(_sanitize_ascii_key(key) for key in finding.mismatched)
        return (
            f"{path}: error {EDITOR_DRIFT_ID} "
            f"missing={missing} extra={extra} mismatched={mismatched}"
        )
    severity = escape_for_diagnostic(finding.severity)
    rule_id = escape_for_diagnostic(finding.rule_id)
    name = escape_for_diagnostic(finding.unicode_name if finding.unicode_name else "-")
    excerpt = escape_for_diagnostic(finding.excerpt)
    return (
        f"{path}:{finding.line}:{finding.column}: "
        f"{severity} {rule_id} {canonical_hex(finding.codepoint)} {name} {excerpt}"
    )


def _is_error_finding(finding: Finding) -> bool:
    """Return whether a finding is an error, including editor drift."""

    if isinstance(finding, EditorDriftFinding):
        return True
    return finding.severity == "error"


def _sanitize_ascii_key(key: str) -> str:
    """Keep printable ASCII in EDITOR-DRIFT keys; spell other code points as U+XXXX."""

    parts: list[str] = []
    for char in key:
        codepoint = ord(char)
        if 0x20 <= codepoint <= 0x7E:
            parts.append(char)
        else:
            parts.append(f"U+{codepoint:04X}")
    return "".join(parts)


def _configure_stdio(stream: io.TextIOBase) -> io.TextIOBase:
    """Configure CLI stdio as UTF-8 text with LF newlines.

    Prefers ``TextIO.reconfigure``. Streams without that interface are wrapped
    from their binary buffer as UTF-8 TextIO. Later write encoding errors are
    not caught; ``errors`` stays strict so data is not replaced.
    """

    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        try:
            reconfigure(encoding="utf-8", newline="\n", errors="strict")
            return stream
        except (AttributeError, io.UnsupportedOperation):
            pass
    detach = getattr(stream, "detach", None)
    if detach is None:
        return stream
    try:
        buffer = detach()
    except (AttributeError, io.UnsupportedOperation):
        return stream
    return io.TextIOWrapper(
        buffer,
        encoding="utf-8",
        errors="strict",
        newline="\n",
        line_buffering=True,
    )
