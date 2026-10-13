"""Pure clearance parsing, validation, and skill-root expansion (version-1 entries).

The reader accepts only the current clearance schema (``CLEARANCE_SCHEMA``) and
returns business failures as typed :class:`DomainError` values, never raised:
malformed JSON, duplicate keys, unsupported schema versions, unknown fields,
missing or invalid modes, unsafe/noncanonical paths, and multiple roots.
Version-1 ``cleared`` entries are a union: a file entry (``mode``, optional root
``role``) or a skill-root entry (a key ending in ``/`` with a default ``mode``
and root-relative ``region_files``). Expansion over enumerated paths is pure.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import PureWindowsPath
from typing import Iterable, Mapping

from core_sync_pkg.domain.constants import (
    CLEARANCE_SCHEMA,
    MODE_REGION,
    ROLE_ROOT,
    VALID_MODES,
    VALID_ROLES,
)
from core_sync_pkg.domain.errors import CODE_INVALID, DomainError
from core_sync_pkg.domain.markers import _is_safe_relative

_RECORD_FIELDS = frozenset({"mode", "role"})
_ROOT_ENTRY_FIELDS = frozenset({"mode", "region_files"})
_DOCUMENT_FIELDS = frozenset({"schema", "cleared"})


@dataclass(frozen=True)
class ClearanceRecord:
    """One cleared source path with its operational mode and optional root role."""

    mode: str
    role: str | None = None


@dataclass(frozen=True)
class SkillRootEntry:
    """One cleared skill root: a default mode plus root-relative region files."""

    mode: str
    region_files: tuple[str, ...]


ClearanceEntry = ClearanceRecord | SkillRootEntry
ClearanceParseResult = dict[str, ClearanceEntry] | DomainError


class _DuplicateKeyError(ValueError):
    """Raised by the object_pairs hook when a JSON object repeats a key."""


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


def _is_absolute_path(path: str) -> bool:
    """Return True for a POSIX- or Windows-absolute path."""
    windows_path = PureWindowsPath(path)
    return path.startswith("/") or bool(windows_path.drive) or bool(windows_path.root)


def _parse_skill_root(root: str, raw_record: object) -> SkillRootEntry | DomainError:
    """Validate one skill-root entry: default mode plus root-relative region files.

    ``region_files`` is optional and defaults to an empty subset; when present it
    must be a list of safe relative paths under the entry's root.
    """
    if not root.endswith("/") or not _is_safe_relative(root[:-1]):
        return DomainError(
            CODE_INVALID,
            f"skill-root key is not a safe relative directory path: {root!r}",
        )
    if not isinstance(raw_record, dict):
        return DomainError(
            CODE_INVALID, f"cleared record for {root!r} must be a JSON object"
        )
    unknown = set(raw_record) - _ROOT_ENTRY_FIELDS
    if unknown:
        return DomainError(
            CODE_INVALID,
            f"cleared record for {root!r} has unknown fields: {sorted(unknown)}",
        )
    mode = raw_record.get("mode")
    if mode not in VALID_MODES:
        return DomainError(
            CODE_INVALID,
            f"cleared record for {root!r} requires mode in {list(VALID_MODES)}",
        )
    raw_region_files = raw_record.get("region_files", [])
    if not isinstance(raw_region_files, list):
        return DomainError(
            CODE_INVALID,
            f"skill-root entry for {root!r} requires a region_files list",
        )
    region_files: list[str] = []
    for member in raw_region_files:
        if not isinstance(member, str):
            return DomainError(
                CODE_INVALID,
                f"skill-root entry for {root!r} has a non-string region_files "
                f"member: {member!r}",
            )
        if member == "":
            return DomainError(
                CODE_INVALID,
                f"skill-root entry for {root!r} has an empty region_files member",
            )
        if ".." in member or _is_absolute_path(member):
            return DomainError(
                CODE_INVALID,
                f"region_files member contains '..' or is absolute: {member!r}",
            )
        if not _is_safe_relative(member):
            return DomainError(
                CODE_INVALID,
                f"region_files member is not under skill root {root!r}: {member!r}",
            )
        region_files.append(member)
    return SkillRootEntry(mode=mode, region_files=tuple(region_files))


def _is_interpreter_cache(path: str) -> bool:
    """Return True for an interpreter cache path: ``__pycache__`` part or ``.pyc``."""
    return "__pycache__" in path.split("/") or path.endswith(".pyc")


def expand_skill_root(
    root: str, entry: SkillRootEntry, file_paths: Iterable[str]
) -> dict[str, str]:
    """Map every enumerated root-relative file under a skill root to its mode.

    A path listed in ``entry.region_files`` resolves ``region``; every other
    enumerated file resolves the root's default ``entry.mode``. Interpreter
    caches never enter the map. Keys are repo-relative: ``root`` followed by
    the enumerated root-relative path. Enumeration is an infrastructure
    concern; this rule receives the paths as data.
    """
    region_files = set(entry.region_files)
    modes: dict[str, str] = {}
    for relative_path in file_paths:
        if _is_interpreter_cache(relative_path):
            continue
        mode = MODE_REGION if relative_path in region_files else entry.mode
        modes[root + relative_path] = mode
    return modes


def expand_clearance(
    entries: Mapping[str, ClearanceEntry],
    enumerated: Mapping[str, list[str]],
) -> dict[str, str]:
    """Expand a parsed clearance into the path-to-mode map for the sync set.

    File entries keep their declared mode; each skill-root entry contributes
    the files enumerated under it via :func:`expand_skill_root`, keyed by their
    repo-relative paths. Interpreter caches never enter a root expansion.
    """
    modes: dict[str, str] = {}
    for path, entry in entries.items():
        if isinstance(entry, SkillRootEntry):
            modes.update(expand_skill_root(path, entry, enumerated.get(path, ())))
        else:
            modes[path] = entry.mode
    return modes


def parse_clearance(text: str) -> ClearanceParseResult:
    """Parse and validate a version-1 clearance document from its JSON text.

    Exactly one schema version exists: any other label fails closed with the
    invalid/unsupported error. There is no legacy or migration path.
    """
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

    entries: dict[str, ClearanceEntry] = {}
    root_path: str | None = None
    for path, raw_record in raw_cleared.items():
        entry = (
            _parse_skill_root(path, raw_record)
            if path.endswith("/")
            else _parse_record(path, raw_record)
        )
        if isinstance(entry, DomainError):
            return entry
        if isinstance(entry, ClearanceRecord) and entry.role == ROLE_ROOT:
            if root_path is not None:
                return DomainError(
                    CODE_INVALID,
                    f"multiple root roles: {root_path!r} and {path!r}",
                )
            root_path = path
        entries[path] = entry
    return entries
