"""Select the remote branch an active feature document still claims."""

from __future__ import annotations

import re
from pathlib import PurePath

STATUS_FIELD_RE = re.compile(r"^> \*\*Status:\*\* (?P<value>.*)$")
BRANCH_FIELD_RE = re.compile(r"^> \*\*Branch:\*\* (?P<value>.*)$")
BACKTICK_SPAN_RE = re.compile(r"`([^`]*)`")
NO_BRANCH_PREFIX = "N/A"
ACTIVE_STATUS = "active"


def is_template_reference(reference: str) -> bool:
    """Identify template filenames using host-specific lexical path semantics."""
    return PurePath(reference).name == "_template.md"


def sort_feature_references(references: tuple[str, ...]) -> tuple[str, ...]:
    """Sort references stably using host-specific lexical path semantics."""
    return tuple(sorted(references, key=PurePath))


def _declared(text: str, pattern: re.Pattern[str]) -> str | None:
    """Return the first matching header field value as written, or None when absent."""
    for line in text.splitlines():
        match = pattern.match(line.strip())
        if match:
            return match.group("value").strip()
    return None


def _branch_token(value: str) -> str:
    """Return the first branch name in a declared value, preferring a quoted name."""
    quoted = BACKTICK_SPAN_RE.search(value)
    if quoted:
        return quoted.group(1).strip()
    tokens = value.split()
    return tokens[0] if tokens else ""


def _unquoted(value: str) -> str:
    """Return the value with one wrapping backtick span removed, so quoted and bare text read alike."""
    quoted = BACKTICK_SPAN_RE.match(value)
    return quoted.group(1).strip() if quoted else value.strip()


def branch_to_check(text: str) -> str | None:
    """Return the branch an active document still claims, or None when none is checkable."""
    if _declared(text, STATUS_FIELD_RE) != ACTIVE_STATUS:
        return None
    declared = _declared(text, BRANCH_FIELD_RE)
    if declared is None or _unquoted(declared).upper().startswith(NO_BRANCH_PREFIX):
        return None
    return _branch_token(declared) or None
