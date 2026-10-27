"""Typed policy, finding, failure, and discovery values for Markdown text integrity."""

from __future__ import annotations

from dataclasses import dataclass

CODE_POLICY = "policy"
CODE_INPUT = "input"
CODE_IO = "io"
EDITOR_DRIFT_ID = "EDITOR-DRIFT"
EDITOR_DRIFT_SEVERITY = "error"
MAX_UNICODE_SCALAR = 0x10FFFF
SURROGATE_START = 0xD800
SURROGATE_END = 0xDFFF


@dataclass(frozen=True)
class DomainError:
    """A typed policy, input, or IO failure returned as a value."""

    code: str
    message: str


@dataclass(frozen=True)
class CodepointSpec:
    """One explicitly listed Unicode scalar in a rule."""

    cp: int
    hex: str


@dataclass(frozen=True)
class RangeSpec:
    """One inclusive Unicode scalar range in a rule."""

    start: int
    end: int
    start_hex: str
    end_hex: str


@dataclass(frozen=True)
class Rule:
    """One policy rule covering code points or ranges, never both."""

    id: str
    severity: str
    class_name: str
    rationale: str
    codepoints: tuple[CodepointSpec, ...]
    ranges: tuple[RangeSpec, ...]


@dataclass(frozen=True)
class InvalidSequence:
    """Decoding envelope for the first ill-formed UTF-8 sequence."""

    id: str
    severity: str
    class_name: str
    rationale: str


@dataclass(frozen=True)
class Decoding:
    """Declared decoding envelope; encoding must be UTF-8 in schema v1."""

    encoding: str
    invalid_sequence: InvalidSequence


@dataclass(frozen=True)
class EditorOverride:
    """One representable editor allow-override; not a scan rule."""

    codepoint: int
    hex: str
    gremlins_key: str
    severity: str
    description: str


@dataclass(frozen=True)
class EditorProjection:
    """Representable Markdown editor overrides projected from policy."""

    scope: str
    setting_key: str
    overrides: tuple[EditorOverride, ...]


@dataclass(frozen=True)
class Policy:
    """Validated schema v1 Markdown text-integrity policy."""

    version: int
    id: str
    default_classification: str
    decoding: Decoding
    rules: tuple[Rule, ...]
    editor_projection: EditorProjection


@dataclass(frozen=True)
class ScalarFinding:
    """A decoded-scalar match against a policy rule."""

    path: str
    line: int
    column: int
    severity: str
    rule_id: str
    codepoint: int
    unicode_name: str
    excerpt: str


@dataclass(frozen=True)
class Utf8Finding:
    """The first ill-formed UTF-8 sequence in a file; scanning stops there."""

    path: str
    line: int
    column: int
    severity: str
    rule_id: str
    byte_offset: int


@dataclass(frozen=True)
class EditorDriftFinding:
    """Representable editor-projection mismatch; not a character finding."""

    path: str
    missing: tuple[str, ...]
    extra: tuple[str, ...]
    mismatched: tuple[str, ...]


Finding = ScalarFinding | Utf8Finding | EditorDriftFinding


@dataclass(frozen=True)
class FileTarget:
    """A discovered regular Markdown file identity without following links."""

    display_path: str
    abs_norm: str


@dataclass(frozen=True)
class DiscoverResult:
    """Discovered Markdown targets plus input/IO failures from the same walk."""

    targets: tuple[FileTarget, ...]
    failures: tuple[DomainError, ...]


@dataclass(frozen=True)
class CheckOutcome:
    """Typed execute() result: character/editor findings and policy/input/IO failures."""

    findings: tuple[Finding, ...]
    failures: tuple[DomainError, ...]


def finding_sort_key(finding: Finding) -> tuple[str, int, int, str]:
    """Return the deterministic stdout sort key for a finding."""

    path = finding.path.replace("\\", "/")
    if isinstance(finding, EditorDriftFinding):
        return (path, 0, 0, EDITOR_DRIFT_ID)
    return (path, finding.line, finding.column, finding.rule_id)
