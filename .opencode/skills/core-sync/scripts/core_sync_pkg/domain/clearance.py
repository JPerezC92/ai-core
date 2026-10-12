"""Pure clearance parsing and validation: schema-2 path-keyed records and root role.

The reader accepts only the current clearance schema (``CLEARANCE_SCHEMA``) and
returns business failures as typed :class:`DomainError` values, never raised:
malformed JSON, duplicate keys, unsupported or legacy schema versions, unknown
fields, missing or invalid modes, unsafe/noncanonical paths, and multiple roots.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from core_sync_pkg.domain.constants import (
    CLEARANCE_SCHEMA,
    MODE_REGION,
    ROLE_ROOT,
    VALID_MODES,
    VALID_ROLES,
)
from core_sync_pkg.domain.errors import CODE_INVALID, CODE_LEGACY_SCHEMA, DomainError
from core_sync_pkg.domain.markers import _is_safe_relative

_RECORD_FIELDS = frozenset({"mode", "role"})
_DOCUMENT_FIELDS = frozenset({"schema", "cleared"})


@dataclass(frozen=True)
class ClearanceRecord:
    """One cleared source path with its operational mode and optional root role."""

    mode: str
    role: str | None = None


ClearanceParseResult = dict[str, ClearanceRecord] | DomainError


class _DuplicateKeyError(ValueError):
    """Raised by the object-pairs hook when a JSON object repeats a key."""


def _object_pairs_without_duplicates(
    pairs: list[tuple[str, object]],
) -> dict[str, object]:
    """Build a JSON object, rejecting any repeated key at any nesting level."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(key)
        result[key] = value
    return result


def _parse_record(path: object, raw_record: object) -> ClearanceRecord | DomainError:
    """Validate one cleared path and its ``{mode, role?}`` record."""
    if not isinstance(path, str) or not _is_safe_relative(path):
        return DomainError(
            CODE_INVALID, f"cleared path is not a safe relative path: {path!r}"
        )
    if not isinstance(raw_record, dict):
        return DomainError(
            CODE_INVALID, f"cleared record for {path!r} must be a JSON object"
        )
    unknown = set(raw_record) - _RECORD_FIELDS
    if unknown:
        return DomainError(
            CODE_INVALID,
            f"cleared record for {path!r} has unknown fields: {sorted(unknown)}",
        )
    mode = raw_record.get("mode")
    if mode not in VALID_MODES:
        return DomainError(
            CODE_INVALID,
            f"cleared record for {path!r} requires mode in {list(VALID_MODES)}",
        )
    role = raw_record.get("role")
    if role is not None and role not in VALID_ROLES:
        return DomainError(
            CODE_INVALID, f"cleared record for {path!r} has invalid role: {role!r}"
        )
    if role == ROLE_ROOT and mode != MODE_REGION:
        return DomainError(
            CODE_INVALID, f"root role for {path!r} must use region mode"
        )
    return ClearanceRecord(mode=mode, role=role)


def parse_clearance(text: str) -> ClearanceParseResult:
    """Parse and validate a schema-2 clearance document from its JSON text."""
    try:
        data = json.loads(text, object_pairs_hook=_object_pairs_without_duplicates)
    except _DuplicateKeyError as exc:
        return DomainError(CODE_INVALID, f"duplicate key in clearance document: {exc}")
    except json.JSONDecodeError as exc:
        return DomainError(CODE_INVALID, f"malformed clearance JSON: {exc}")

    if not isinstance(data, dict):
        return DomainError(CODE_INVALID, "clearance document must be a JSON object")
    schema = data.get("schema")
    if isinstance(schema, bool) or not isinstance(schema, int):
        return DomainError(
            CODE_INVALID, f"clearance schema must be an integer: {schema!r}"
        )
    if schema == 1:
        return DomainError(
            CODE_LEGACY_SCHEMA,
            "clearance schema 1 is legacy; rewrite it as schema 2 with a "
            "path-keyed 'cleared' object, a required per-record 'mode' "
            "(region|raw), and an optional 'role' of 'root' on the region-mode root",
        )
    if schema != CLEARANCE_SCHEMA:
        return DomainError(
            CODE_INVALID,
            f"unsupported clearance schema: {schema!r} (expected {CLEARANCE_SCHEMA})",
        )
    unknown = set(data) - _DOCUMENT_FIELDS
    if unknown:
        return DomainError(
            CODE_INVALID, f"clearance document has unknown fields: {sorted(unknown)}"
        )
    raw_cleared = data.get("cleared")
    if not isinstance(raw_cleared, dict):
        return DomainError(
            CODE_INVALID, "clearance 'cleared' must be a path-keyed JSON object"
        )

    records: dict[str, ClearanceRecord] = {}
    root_path: str | None = None
    for path, raw_record in raw_cleared.items():
        record = _parse_record(path, raw_record)
        if isinstance(record, DomainError):
            return record
        if record.role == ROLE_ROOT:
            if root_path is not None:
                return DomainError(
                    CODE_INVALID,
                    f"multiple root roles: {root_path!r} and {path!r}",
                )
            root_path = path
        records[path] = record
    return records
