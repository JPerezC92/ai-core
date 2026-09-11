"""Read-only AICore adoption synchronization checker and lock proposer.

This module implements the ``sync-aicore-adoption`` protocol v1. It parses the
machine catalog, the adopter declaration, and the generated adoption lock;
reads accepted and current upstream content from Git objects; projects logical
member content from Git objects and the adopter worktree; and reports
orthogonal mode, upstream delta, destination delta, and disposition per unit.

Safety boundary: ``check`` is strictly read-only and writes nothing, while
``propose-lock`` writes only a candidate lock to stdout. Neither command
mutates the filesystem, the Git index, refs, or the worktree, and there is no
apply, copy, merge, delete, fetch, credential, or destination-adapter path.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import yaml

# --------------------------------------------------------------------------- #
# Protocol constants
# --------------------------------------------------------------------------- #

SCHEMA_VERSION = 1
CATALOG_PATH = ".aicore/core-catalog-v1.yaml"

DEFAULT_EXCLUSIONS: tuple[str, ...] = ("**/__pycache__/**", "**/*.pyc")
DEFAULT_CONTROL_PATHS: tuple[str, ...] = (
    ".git/**",
    ".aicore/adoption.yaml",
    ".aicore/adoption.lock.yaml",
)

FILE_MODES: tuple[str, ...] = ("100644", "100755", "120000")

DECLARED_MODES: tuple[str, ...] = ("mirror", "adapted", "replacement", "destination_owned")
REPORT_MODES: tuple[str, ...] = DECLARED_MODES + ("not_declared",)
DELTAS: tuple[str, ...] = ("unchanged", "added", "modified", "removed", "not_applicable")

BASELINE_UNAVAILABLE = "baseline_unavailable"
INVALID_LOCK = "invalid_lock"
DECLARATION_CHANGED = "declaration_changed"
CATALOG_CHANGED = "catalog_changed"
INVALID_MAPPING = "invalid_mapping"
UNSUPPORTED_PROJECTION = "unsupported_projection"
UNSUPPORTED_SPECIAL_FILE = "unsupported_special_file"

COMMIT_RE = re.compile(r"[0-9a-f]{40}\Z")
DIGEST_RE = re.compile(r"sha256:[0-9a-f]{64}\Z")

GOLDEN_FILE_DIGEST = "sha256:cf41078b082e3740168bd7ad534ba1b70b12489c7ab43c6fb53743b0f3527887"
GOLDEN_TREE_DIGEST = "sha256:4b49b94b71240c8933269684873b2eecf0f53de69ed8ded25eda1e172d3637d7"


# --------------------------------------------------------------------------- #
# Fatal error type
# --------------------------------------------------------------------------- #


class SyncError(Exception):
    """A top-level fatal protocol error that aborts the whole run."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


# --------------------------------------------------------------------------- #
# Value objects
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class TreeEntry:
    """One parsed entry from ``git ls-tree``."""

    mode: str
    object_type: str
    object_id: str
    path: str


@dataclass(frozen=True)
class ProjectedEntry:
    """One logical member entry with a POSIX path, normalized mode, and bytes."""

    path: str
    mode: str
    content: bytes


@dataclass(frozen=True)
class CatalogMember:
    """A catalog member: logical id, tracked source path, canonical destination."""

    id: str
    source: str
    destination: str


@dataclass(frozen=True)
class CatalogUnit:
    """A catalog unit: stable id and a file/tree/none synchronization projection."""

    id: str
    sync_projection: str
    members: tuple[CatalogMember, ...]


@dataclass(frozen=True)
class Catalog:
    """The parsed AICore machine catalog."""

    digest_exclusions: tuple[str, ...]
    control_paths: tuple[str, ...]
    units: tuple[CatalogUnit, ...]


@dataclass(frozen=True)
class DeclarationMember:
    """A declaration member mapping: logical member id to adopter destination."""

    id: str
    destination: str


@dataclass(frozen=True)
class DeclarationUnit:
    """A declaration unit: adopter-intended mode plus destination mapping."""

    id: str
    mode: str
    members: tuple[DeclarationMember, ...]
    replacement_destinations: tuple[str, ...]


@dataclass(frozen=True)
class Declaration:
    """The parsed adopter declaration."""

    upstream_repository: str
    units: tuple[DeclarationUnit, ...]


@dataclass(frozen=True)
class LockMember:
    """A lock member: accepted upstream and destination digests."""

    id: str
    destination: str
    accepted_upstream_digest: str
    accepted_destination_digest: str


@dataclass(frozen=True)
class LockUnit:
    """A lock unit: accepted evidence for one declared unit."""

    id: str
    mode: str
    members: tuple[LockMember, ...]
    replacement_destinations: tuple[str, ...]
    accepted_upstream_digest: str
    accepted_destination_digest: str


@dataclass(frozen=True)
class Lock:
    """The parsed generated adoption lock."""

    upstream_repository: str
    accepted_source_commit: str
    catalog_digest: str
    declaration_digest: str
    units: tuple[LockUnit, ...]


@dataclass(frozen=True)
class MemberReport:
    """A per-member report row."""

    id: str
    destination: str | None
    upstream_delta: str
    destination_delta: str
    accepted_upstream_digest: str
    current_upstream_digest: str
    accepted_destination_digest: str
    current_destination_digest: str


@dataclass(frozen=True)
class UnitReport:
    """A per-unit report row with orthogonal mode/delta/disposition fields."""

    id: str
    mode: str
    upstream_delta: str
    destination_delta: str
    disposition: str
    members: tuple[MemberReport, ...]
    replacement_destinations: tuple[str, ...]


@dataclass(frozen=True)
class CheckReport:
    """The stable top-level ``check`` report."""

    status: str
    error: str | None
    units: tuple[UnitReport, ...]


# --------------------------------------------------------------------------- #
# Pure digest protocol (protocol-v1 Section 4)
# --------------------------------------------------------------------------- #


def sha256_digest(data: bytes) -> str:
    """Return the ``sha256:<hex>`` digest of raw bytes."""

    return "sha256:" + hashlib.sha256(data).hexdigest()


def _path_bytes(value: str) -> bytes:
    """Encode a logical path as UTF-8 with surrogate escaping for Git paths."""

    return value.encode("utf-8", "surrogateescape")


def compute_member_digest(entries: Sequence[ProjectedEntry]) -> str:
    """Compute a member digest over length-prefixed framed entries.

    Entries are ordered by ascending byte order of the logical path. The framing
    is exactly ``protocol-v1.md`` Section 4: an ``entry`` marker followed by
    ``path:``, ``mode:``, ``size:``, and ``content:`` fields, each newline
    terminated, with the content bytes preserved verbatim.
    """

    ordered = sorted(entries, key=lambda entry: _path_bytes(entry.path))
    hasher = hashlib.sha256()
    for entry in ordered:
        hasher.update(b"entry\n")
        hasher.update(b"path:" + _path_bytes(entry.path) + b"\n")
        hasher.update(b"mode:" + entry.mode.encode("ascii") + b"\n")
        hasher.update(b"size:" + str(len(entry.content)).encode("ascii") + b"\n")
        hasher.update(b"content:" + entry.content + b"\n")
    return "sha256:" + hasher.hexdigest()


def digest_unit_from_members(members: Sequence[tuple[str, str]]) -> str:
    """Compute a unit digest over ``(member_id, member_digest)`` pairs in order."""

    hasher = hashlib.sha256()
    for member_id, member_digest in members:
        hasher.update(b"member\n")
        hasher.update(b"id:" + _path_bytes(member_id) + b"\n")
        hasher.update(b"digest:" + member_digest.encode("ascii") + b"\n")
    return "sha256:" + hasher.hexdigest()


def golden_vectors() -> dict[str, str]:
    """Return the protocol's self-check golden vectors for the digest framing."""

    file_entries = (ProjectedEntry(path="", mode="100644", content=b"hello\n"),)
    tree_entries = (
        ProjectedEntry(path="a.txt", mode="100644", content=b"hello\n"),
        ProjectedEntry(path="sub/b.txt", mode="100755", content=b"bye\n"),
    )
    return {
        "file": compute_member_digest(file_entries),
        "tree": compute_member_digest(tree_entries),
    }


# --------------------------------------------------------------------------- #
# Pure glob, exclusion, and control-path helpers
# --------------------------------------------------------------------------- #


@functools.lru_cache(maxsize=128)
def _glob_pattern(pattern: str) -> re.Pattern[str]:
    """Translate a ``**``-aware glob into an anchored regular expression."""

    parts: list[str] = ["(?s:"]
    index = 0
    length = len(pattern)
    while index < length:
        char = pattern[index]
        if char == "*":
            if index + 1 < length and pattern[index + 1] == "*":
                if index + 2 < length and pattern[index + 2] == "/":
                    parts.append("(?:.*/)?")
                    index += 3
                    continue
                parts.append(".*")
                index += 2
                continue
            parts.append("[^/]*")
            index += 1
            continue
        if char == "?":
            parts.append("[^/]")
        elif char in ".^$+()|{}[]\\":
            parts.append("\\" + char)
        else:
            parts.append(char)
        index += 1
    parts.append(")\\Z")
    return re.compile("".join(parts))


def is_excluded_path(path: str, exclusions: Sequence[str]) -> bool:
    """Return True when a logical path matches a catalog digest exclusion."""

    return any(_glob_pattern(pattern).match(path) for pattern in exclusions)


def is_control_path(destination: str, control_paths: Sequence[str]) -> bool:
    """Return True when a destination targets or contains an adoption control path."""

    for pattern in control_paths:
        base = pattern[:-3] if pattern.endswith("/**") else pattern
        if destination == base or destination.startswith(base + "/"):
            return True
        if base.startswith(destination + "/"):
            return True
    return False


def normalize_destination(raw: str) -> str:
    """Validate and normalize a repository-relative destination path."""

    if not isinstance(raw, str) or raw == "":
        raise SyncError(INVALID_MAPPING, "destination must be a non-empty string")
    if raw.startswith("/"):
        raise SyncError(INVALID_MAPPING, f"destination {raw!r} must be repository-relative")
    if re.match(r"^[A-Za-z]:[\\/]", raw):
        raise SyncError(INVALID_MAPPING, f"destination {raw!r} must be repository-relative")
    segments = raw.replace("\\", "/").split("/")
    if any(segment == ".." for segment in segments):
        raise SyncError(INVALID_MAPPING, f"destination {raw!r} must not contain '..'")
    cleaned = [segment for segment in segments if segment not in ("", ".")]
    if not cleaned:
        raise SyncError(INVALID_MAPPING, f"destination {raw!r} is empty after normalization")
    return "/".join(cleaned)


# --------------------------------------------------------------------------- #
# Schema parsing helpers (pure: bytes/dict in, typed value out)
# --------------------------------------------------------------------------- #


def _load_yaml(raw: bytes, source: str, error_code: str) -> object:
    """Decode and YAML-load raw bytes, raising a protocol error on failure."""

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise SyncError(error_code, f"{source}: not valid UTF-8: {exc}") from exc
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise SyncError(error_code, f"{source}: not valid YAML: {exc}") from exc


def _require_mapping(value: object, context: str, error_code: str) -> dict[str, object]:
    """Require a YAML mapping, returning it typed as ``dict[str, object]``."""

    if not isinstance(value, dict):
        raise SyncError(error_code, f"{context} must be a mapping")
    return value


def _require_str(mapping: dict[str, object], key: str, context: str, error_code: str) -> str:
    """Require a non-empty string field from a mapping."""

    value = mapping.get(key)
    if not isinstance(value, str) or value == "":
        raise SyncError(error_code, f"{context}.{key} must be a non-empty string")
    return value


def _string_list(
    value: object,
    fallback: Sequence[str],
    context: str,
    error_code: str,
) -> tuple[str, ...]:
    """Require a list of non-empty strings, defaulting when absent."""

    if value is None:
        return tuple(fallback)
    if not isinstance(value, list):
        raise SyncError(error_code, f"{context} must be a list of strings")
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or item == "":
            raise SyncError(error_code, f"{context} must be a list of non-empty strings")
        result.append(item)
    return tuple(result)


def _reject_duplicate_ids(ids: Iterable[str], context: str, error_code: str) -> None:
    """Reject duplicate logical ids in a collection."""

    seen: set[str] = set()
    for item_id in ids:
        if item_id in seen:
            raise SyncError(error_code, f"{context}: duplicate id {item_id!r}")
        seen.add(item_id)


# --------------------------------------------------------------------------- #
# Catalog, declaration, and lock parsing
# --------------------------------------------------------------------------- #


def _parse_catalog_member(value: object, unit_id: str) -> CatalogMember:
    """Parse one catalog member mapping."""

    mapping = _require_mapping(value, f"catalog unit {unit_id} member", CATALOG_CHANGED)
    member_id = _require_str(mapping, "id", f"catalog unit {unit_id} member", CATALOG_CHANGED)
    source = _require_str(mapping, "source", f"catalog member {unit_id}.{member_id}", CATALOG_CHANGED)
    destination = _require_str(
        mapping, "destination", f"catalog member {unit_id}.{member_id}", CATALOG_CHANGED
    )
    return CatalogMember(id=member_id, source=source, destination=destination)


def _parse_catalog_unit(value: object) -> CatalogUnit:
    """Parse one catalog unit mapping."""

    mapping = _require_mapping(value, "catalog unit", CATALOG_CHANGED)
    unit_id = _require_str(mapping, "id", "catalog unit", CATALOG_CHANGED)
    projection = _require_str(mapping, "sync_projection", f"catalog unit {unit_id}", CATALOG_CHANGED)
    if projection not in ("file", "tree", "none"):
        raise SyncError(
            UNSUPPORTED_PROJECTION,
            f"catalog unit {unit_id!r}: unknown sync_projection {projection!r}",
        )
    members_raw = mapping.get("members")
    if not isinstance(members_raw, list) or not members_raw:
        raise SyncError(CATALOG_CHANGED, f"catalog unit {unit_id!r}: members must be a non-empty list")
    members = tuple(_parse_catalog_member(item, unit_id) for item in members_raw)
    _reject_duplicate_ids(
        (member.id for member in members), f"catalog unit {unit_id!r} members", CATALOG_CHANGED
    )
    return CatalogUnit(id=unit_id, sync_projection=projection, members=members)


def parse_catalog(raw: bytes, source: str) -> Catalog:
    """Parse the machine catalog from raw file bytes."""

    root = _require_mapping(_load_yaml(raw, source, CATALOG_CHANGED), "catalog document", CATALOG_CHANGED)
    version = root.get("schema_version")
    if version != SCHEMA_VERSION:
        raise SyncError(CATALOG_CHANGED, f"{source}: unsupported catalog schema_version {version!r}")
    block = _require_mapping(root.get("catalog"), "catalog", CATALOG_CHANGED)
    exclusions = _string_list(
        block.get("digest_exclusions"), DEFAULT_EXCLUSIONS, "catalog.digest_exclusions", CATALOG_CHANGED
    )
    controls = _string_list(
        block.get("control_paths"), DEFAULT_CONTROL_PATHS, "catalog.control_paths", CATALOG_CHANGED
    )
    units_raw = root.get("units")
    if not isinstance(units_raw, list) or not units_raw:
        raise SyncError(CATALOG_CHANGED, f"{source}: units must be a non-empty list")
    units = tuple(_parse_catalog_unit(item) for item in units_raw)
    _reject_duplicate_ids((unit.id for unit in units), "catalog units", CATALOG_CHANGED)
    return Catalog(digest_exclusions=exclusions, control_paths=controls, units=units)


def _parse_declaration_member(value: object, unit_id: str) -> DeclarationMember:
    """Parse one declaration member mapping."""

    mapping = _require_mapping(value, f"declaration unit {unit_id} member", INVALID_MAPPING)
    member_id = _require_str(mapping, "id", f"declaration unit {unit_id} member", INVALID_MAPPING)
    destination = _require_str(
        mapping, "destination", f"declaration unit {unit_id} member {member_id}", INVALID_MAPPING
    )
    return DeclarationMember(id=member_id, destination=destination)


def _parse_declaration_unit(value: object) -> DeclarationUnit:
    """Parse one declaration unit mapping."""

    mapping = _require_mapping(value, "declaration unit", INVALID_MAPPING)
    unit_id = _require_str(mapping, "id", "declaration unit", INVALID_MAPPING)
    mode = _require_str(mapping, "mode", f"declaration unit {unit_id}", INVALID_MAPPING)
    if mode not in DECLARED_MODES:
        raise SyncError(INVALID_MAPPING, f"declaration unit {unit_id!r}: unknown mode {mode!r}")

    if mode == "replacement":
        raw_destinations = mapping.get("replacement_destinations")
        if not isinstance(raw_destinations, list) or not raw_destinations:
            raise SyncError(
                INVALID_MAPPING,
                f"declaration unit {unit_id!r}: replacement_destinations must be a non-empty list",
            )
        destinations: list[str] = []
        for destination in raw_destinations:
            if not isinstance(destination, str) or destination == "":
                raise SyncError(
                    INVALID_MAPPING,
                    f"declaration unit {unit_id!r}: replacement destinations must be non-empty strings",
                )
            destinations.append(destination)
        if mapping.get("members") not in (None, []):
            raise SyncError(
                INVALID_MAPPING, f"declaration unit {unit_id!r}: replacement must not declare members"
            )
        return DeclarationUnit(
            id=unit_id, mode=mode, members=(), replacement_destinations=tuple(destinations)
        )

    members_raw = mapping.get("members")
    if not isinstance(members_raw, list) or not members_raw:
        raise SyncError(INVALID_MAPPING, f"declaration unit {unit_id!r}: members must be a non-empty list")
    members = tuple(_parse_declaration_member(item, unit_id) for item in members_raw)
    _reject_duplicate_ids(
        (member.id for member in members), f"declaration unit {unit_id!r} members", INVALID_MAPPING
    )
    if mapping.get("replacement_destinations") not in (None, []):
        raise SyncError(
            INVALID_MAPPING,
            f"declaration unit {unit_id!r}: non-replacement must not declare replacement_destinations",
        )
    return DeclarationUnit(id=unit_id, mode=mode, members=members, replacement_destinations=())


def parse_declaration(raw: bytes, source: str) -> Declaration:
    """Parse the adopter declaration from raw file bytes."""

    root = _require_mapping(_load_yaml(raw, source, INVALID_MAPPING), "declaration", INVALID_MAPPING)
    version = root.get("schema_version")
    if version != SCHEMA_VERSION:
        raise SyncError(INVALID_MAPPING, f"{source}: unsupported declaration schema_version {version!r}")
    upstream = _require_str(root, "upstream_repository", "declaration", INVALID_MAPPING)
    units_raw = root.get("units")
    if not isinstance(units_raw, list):
        raise SyncError(INVALID_MAPPING, f"{source}: units must be a list")
    units = tuple(_parse_declaration_unit(item) for item in units_raw)
    _reject_duplicate_ids((unit.id for unit in units), "declaration units", INVALID_MAPPING)
    return Declaration(upstream_repository=upstream, units=units)


def _parse_lock_member(value: object, unit_id: str) -> LockMember:
    """Parse one lock member mapping."""

    mapping = _require_mapping(value, f"lock unit {unit_id} member", INVALID_LOCK)
    member_id = _require_str(mapping, "id", f"lock unit {unit_id} member", INVALID_LOCK)
    destination = _require_str(mapping, "destination", f"lock unit {unit_id} member {member_id}", INVALID_LOCK)
    accepted_upstream = _require_str(
        mapping, "accepted_upstream_digest", f"lock unit {unit_id} member {member_id}", INVALID_LOCK
    )
    accepted_destination = _require_str(
        mapping, "accepted_destination_digest", f"lock unit {unit_id} member {member_id}", INVALID_LOCK
    )
    if not DIGEST_RE.fullmatch(accepted_upstream):
        raise SyncError(INVALID_LOCK, f"lock unit {unit_id!r} member {member_id!r}: invalid upstream digest")
    if not DIGEST_RE.fullmatch(accepted_destination):
        raise SyncError(INVALID_LOCK, f"lock unit {unit_id!r} member {member_id!r}: invalid destination digest")
    return LockMember(
        id=member_id,
        destination=destination,
        accepted_upstream_digest=accepted_upstream,
        accepted_destination_digest=accepted_destination,
    )


def _parse_lock_unit(value: object) -> LockUnit:
    """Parse one lock unit mapping."""

    mapping = _require_mapping(value, "lock unit", INVALID_LOCK)
    unit_id = _require_str(mapping, "id", "lock unit", INVALID_LOCK)
    mode = _require_str(mapping, "mode", f"lock unit {unit_id}", INVALID_LOCK)
    if mode not in DECLARED_MODES:
        raise SyncError(INVALID_LOCK, f"lock unit {unit_id!r}: unknown mode {mode!r}")

    if mode == "replacement":
        raw_destinations = mapping.get("replacement_destinations")
        if not isinstance(raw_destinations, list) or not raw_destinations:
            raise SyncError(
                INVALID_LOCK,
                f"lock unit {unit_id!r}: replacement_destinations must be a non-empty list",
            )
        destinations: list[str] = []
        for destination in raw_destinations:
            if not isinstance(destination, str) or destination == "":
                raise SyncError(
                    INVALID_LOCK,
                    f"lock unit {unit_id!r}: replacement destinations must be non-empty strings",
                )
            destinations.append(destination)
        accepted_upstream = _require_str(mapping, "accepted_upstream_digest", f"lock unit {unit_id}", INVALID_LOCK)
        accepted_destination = _require_str(
            mapping, "accepted_destination_digest", f"lock unit {unit_id}", INVALID_LOCK
        )
        if not DIGEST_RE.fullmatch(accepted_upstream):
            raise SyncError(INVALID_LOCK, f"lock unit {unit_id!r}: invalid accepted_upstream_digest")
        if accepted_destination != "not_applicable":
            raise SyncError(
                INVALID_LOCK,
                f"lock unit {unit_id!r}: replacement accepted_destination_digest must be not_applicable",
            )
        if mapping.get("members") not in (None, []):
            raise SyncError(INVALID_LOCK, f"lock unit {unit_id!r}: replacement must not declare members")
        return LockUnit(
            id=unit_id,
            mode=mode,
            members=(),
            replacement_destinations=tuple(destinations),
            accepted_upstream_digest=accepted_upstream,
            accepted_destination_digest=accepted_destination,
        )

    members_raw = mapping.get("members")
    if not isinstance(members_raw, list) or not members_raw:
        raise SyncError(INVALID_LOCK, f"lock unit {unit_id!r}: members must be a non-empty list")
    members = tuple(_parse_lock_member(item, unit_id) for item in members_raw)
    _reject_duplicate_ids((member.id for member in members), f"lock unit {unit_id!r} members", INVALID_LOCK)
    return LockUnit(
        id=unit_id,
        mode=mode,
        members=members,
        replacement_destinations=(),
        accepted_upstream_digest="",
        accepted_destination_digest="",
    )


def parse_lock(raw: bytes, source: str) -> Lock:
    """Parse the generated adoption lock from raw file bytes."""

    root = _require_mapping(_load_yaml(raw, source, INVALID_LOCK), "lock", INVALID_LOCK)
    version = root.get("schema_version")
    if version != SCHEMA_VERSION:
        raise SyncError(INVALID_LOCK, f"{source}: unsupported lock schema_version {version!r}")
    upstream = _require_str(root, "upstream_repository", "lock", INVALID_LOCK)
    commit = _require_str(root, "accepted_source_commit", "lock", INVALID_LOCK)
    if not COMMIT_RE.fullmatch(commit):
        raise SyncError(INVALID_LOCK, "accepted_source_commit must be a full 40-character sha")
    catalog_digest = _require_str(root, "catalog_digest", "lock", INVALID_LOCK)
    if not DIGEST_RE.fullmatch(catalog_digest):
        raise SyncError(INVALID_LOCK, "catalog_digest must be a sha256 digest")
    declaration_digest = _require_str(root, "declaration_digest", "lock", INVALID_LOCK)
    if not DIGEST_RE.fullmatch(declaration_digest):
        raise SyncError(INVALID_LOCK, "declaration_digest must be a sha256 digest")
    units_raw = root.get("units")
    if not isinstance(units_raw, list):
        raise SyncError(INVALID_LOCK, f"{source}: units must be a list")
    units = tuple(_parse_lock_unit(item) for item in units_raw)
    _reject_duplicate_ids((unit.id for unit in units), "lock units", INVALID_LOCK)
    return Lock(
        upstream_repository=upstream,
        accepted_source_commit=commit,
        catalog_digest=catalog_digest,
        declaration_digest=declaration_digest,
        units=units,
    )


# --------------------------------------------------------------------------- #
# Declaration and mapping validation (protocol-v1 Section 6)
# --------------------------------------------------------------------------- #


def validate_destination_mappings(
    owned: Sequence[tuple[str, str]],
    control_paths: Sequence[str],
) -> tuple[tuple[str, str], ...]:
    """Validate destinations: control paths, duplicates, and overlapping ownership."""

    normalized: list[tuple[str, str]] = []
    for raw_destination, kind in owned:
        destination = normalize_destination(raw_destination)
        if is_control_path(destination, control_paths):
            raise SyncError(
                INVALID_MAPPING,
                f"destination {raw_destination!r} targets an adoption control path",
            )
        normalized.append((destination, kind))

    seen: dict[str, str] = {}
    for destination, kind in normalized:
        if destination in seen:
            raise SyncError(INVALID_MAPPING, f"duplicate destination {destination!r}")
        seen[destination] = kind

    for left in range(len(normalized)):
        for right in range(len(normalized)):
            if left == right:
                continue
            left_destination = normalized[left][0]
            right_destination = normalized[right][0]
            if right_destination.startswith(left_destination + "/"):
                raise SyncError(
                    INVALID_MAPPING,
                    f"overlapping destinations {left_destination!r} and {right_destination!r}",
                )
    return tuple(normalized)


def validate_declaration(
    declaration: Declaration,
    accepted_units: dict[str, CatalogUnit],
    current_units: dict[str, CatalogUnit],
    control_paths: Sequence[str],
) -> tuple[tuple[str, str], ...]:
    """Validate a declaration against the baseline catalog and protocol rules.

    The member mapping is checked against the accepted (baseline) catalog when
    available so an unchanged declaration remains valid even when upstream adds
    or removes members. Returns the normalized ``(destination, kind)`` ownership
    list for the filesystem symlink-escape check.
    """

    owned: list[tuple[str, str]] = []
    for unit in declaration.units:
        accepted_unit = accepted_units.get(unit.id)
        current_unit = current_units.get(unit.id)
        if accepted_unit is None and current_unit is None:
            raise SyncError(INVALID_MAPPING, f"declaration unit {unit.id!r} is not present in the catalog")
        for candidate in (accepted_unit, current_unit):
            if candidate is None:
                continue
            if candidate.sync_projection == "none":
                raise SyncError(
                    UNSUPPORTED_PROJECTION,
                    f"declaration unit {unit.id!r} references an installer-only sync_projection: none unit",
                )
            if candidate.sync_projection not in ("file", "tree"):
                raise SyncError(
                    UNSUPPORTED_PROJECTION,
                    f"declaration unit {unit.id!r} has unsupported sync_projection {candidate.sync_projection!r}",
                )

        reference = accepted_unit if accepted_unit is not None else current_unit
        if reference is None:  # pragma: no cover - guarded by the checks above
            raise SyncError(INVALID_MAPPING, f"declaration unit {unit.id!r} has no catalog reference")

        if unit.mode == "replacement":
            if unit.members:
                raise SyncError(INVALID_MAPPING, f"replacement unit {unit.id!r} must not declare members")
            if not unit.replacement_destinations:
                raise SyncError(INVALID_MAPPING, f"replacement unit {unit.id!r} needs replacement_destinations")
            for destination in unit.replacement_destinations:
                owned.append((destination, "file"))
            continue

        reference_ids = sorted(member.id for member in reference.members)
        declared_ids = sorted(member.id for member in unit.members)
        if reference_ids != declared_ids:
            raise SyncError(
                INVALID_MAPPING,
                f"declaration unit {unit.id!r} must map every catalog member exactly once",
            )
        for member in unit.members:
            owned.append((member.destination, reference.sync_projection))

    return validate_destination_mappings(owned, control_paths)


def validate_lock_matches_declaration(
    declaration: Declaration,
    lock: Lock,
) -> None:
    """Validate that the lock is the accepted evidence for this declaration."""

    lock_by_id = {unit.id: unit for unit in lock.units}
    declared_ids = {unit.id for unit in declaration.units}
    for unit in declaration.units:
        lock_unit = lock_by_id.get(unit.id)
        if lock_unit is None:
            raise SyncError(INVALID_LOCK, f"lock is missing declared unit {unit.id!r}")
        if lock_unit.mode != unit.mode:
            raise SyncError(INVALID_LOCK, f"lock unit {unit.id!r} mode does not match the declaration")
        if unit.mode == "replacement":
            lock_destinations = tuple(
                normalize_destination(destination) for destination in lock_unit.replacement_destinations
            )
            declared_destinations = tuple(
                normalize_destination(destination) for destination in unit.replacement_destinations
            )
            if lock_destinations != declared_destinations:
                raise SyncError(
                    INVALID_LOCK,
                    f"lock unit {unit.id!r} replacement destinations do not match the declaration",
                )
            continue
        lock_members = {member.id: member for member in lock_unit.members}
        if len(lock_members) != len(unit.members):
            raise SyncError(INVALID_LOCK, f"lock unit {unit.id!r} member set does not match the declaration")
        for member in unit.members:
            lock_member = lock_members.get(member.id)
            if lock_member is None:
                raise SyncError(INVALID_LOCK, f"lock unit {unit.id!r} is missing member {member.id!r}")
            if normalize_destination(lock_member.destination) != normalize_destination(member.destination):
                raise SyncError(
                    INVALID_LOCK,
                    f"lock unit {unit.id!r} member {member.id!r} destination does not match the declaration",
                )
            if (
                unit.mode == "mirror"
                and lock_member.accepted_upstream_digest != lock_member.accepted_destination_digest
            ):
                raise SyncError(
                    INVALID_LOCK,
                    f"mirror unit {unit.id!r} member {member.id!r} has unequal accepted source/destination digests",
                )
    for lock_unit in lock.units:
        if lock_unit.id not in declared_ids:
            raise SyncError(INVALID_LOCK, f"lock contains undeclared unit {lock_unit.id!r}")


def assert_no_symlink_escape(adopter_repo: Path, owned: Sequence[tuple[str, str]]) -> None:
    """Reject any destination that escapes the adopter repository through a symlink."""

    root = adopter_repo.resolve()
    for destination, _kind in owned:
        resolved = (adopter_repo / destination).resolve()
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise SyncError(
                INVALID_MAPPING,
                f"destination {destination!r} escapes the repository root through a symlink",
            ) from exc


# --------------------------------------------------------------------------- #
# IO helpers: subprocess Git reads and filesystem reads
# --------------------------------------------------------------------------- #


def _git(repo: Path, args: Sequence[str]) -> subprocess.CompletedProcess[bytes]:
    """Execute a read-only Git command and capture its bytes."""

    try:
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            capture_output=True,
            check=False,
        )
    except OSError as exc:
        raise SyncError(BASELINE_UNAVAILABLE, f"unable to execute git: {exc}") from exc


def git_resolve_commit(repo: Path, revision: str) -> str | None:
    """Resolve a revision to a full 40-character commit id, or None."""

    result = _git(repo, ["rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}"])
    if result.returncode != 0:
        return None
    resolved = result.stdout.decode("ascii", "replace").strip()
    if not COMMIT_RE.fullmatch(resolved):
        return None
    return resolved


def git_is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    """Return True when ``ancestor`` is an ancestor of ``descendant``."""

    result = _git(repo, ["merge-base", "--is-ancestor", ancestor, descendant])
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    raise SyncError(BASELINE_UNAVAILABLE, "unable to evaluate commit ancestry")


def git_read_object(repo: Path, revision: str, path: str) -> bytes | None:
    """Read a repository path at a revision as raw bytes, or None when absent."""

    result = _git(repo, ["show", f"{revision}:{path}"])
    if result.returncode != 0:
        return None
    return result.stdout


def git_read_blob_by_id(repo: Path, object_id: str) -> bytes | None:
    """Read a Git blob by object id as raw bytes, or None when absent."""

    result = _git(repo, ["cat-file", "blob", object_id])
    if result.returncode != 0:
        return None
    return result.stdout


def _parse_ls_tree(data: bytes) -> tuple[TreeEntry, ...]:
    """Parse NUL-delimited ``git ls-tree -z`` output."""

    entries: list[TreeEntry] = []
    for record in data.split(b"\x00"):
        if not record:
            continue
        meta, _, path_bytes = record.partition(b"\t")
        fields = meta.split(b" ")
        if len(fields) != 3:
            continue
        mode, object_type, object_id = fields
        entries.append(
            TreeEntry(
                mode=mode.decode("ascii", "replace"),
                object_type=object_type.decode("ascii", "replace"),
                object_id=object_id.decode("ascii", "replace"),
                path=path_bytes.decode("utf-8", "surrogateescape"),
            )
        )
    return tuple(entries)


def git_ls_tree(repo: Path, revision: str, path: str, recursive: bool) -> tuple[TreeEntry, ...] | None:
    """List a repository path at a revision via ``git ls-tree``."""

    if recursive:
        args = ["ls-tree", "-z", "-r", f"{revision}:{path}"]
    else:
        args = ["ls-tree", "-z", revision, "--", path]
    result = _git(repo, args)
    if result.returncode != 0:
        return None
    return _parse_ls_tree(result.stdout)


def read_file_bytes(path: Path, error_code: str, label: str) -> bytes:
    """Read a filesystem file as raw bytes, raising a protocol error on failure."""

    try:
        return path.read_bytes()
    except OSError as exc:
        raise SyncError(error_code, f"unable to read {label} at {path}: {exc}") from exc


# --------------------------------------------------------------------------- #
# Content projection
# --------------------------------------------------------------------------- #


def project_file_source(
    repo: Path,
    revision: str,
    source: str,
    error_code: str,
    label: str,
) -> tuple[ProjectedEntry, ...]:
    """Project a single tracked source file into one logical ``""`` entry."""

    if source == "":
        raise SyncError(error_code, f"{label}: empty source path")
    entries = git_ls_tree(repo, revision, source, recursive=False)
    if not entries:
        raise SyncError(error_code, f"{label}: source {source!r} is not present at {revision}")
    entry = entries[0]
    if entry.object_type != "blob" or entry.mode not in FILE_MODES:
        raise SyncError(
            UNSUPPORTED_SPECIAL_FILE,
            f"{label}: source {source!r} at {revision} is not a regular, executable, or symlink file",
        )
    content = git_read_blob_by_id(repo, entry.object_id)
    if content is None:
        raise SyncError(error_code, f"{label}: unable to read blob for {source!r} at {revision}")
    return (ProjectedEntry(path="", mode=entry.mode, content=content),)


def project_tree_source(
    repo: Path,
    revision: str,
    source: str,
    exclusions: Sequence[str],
    error_code: str,
    label: str,
) -> tuple[ProjectedEntry, ...]:
    """Project a tracked source tree into member-relative POSIX entries."""

    entries = git_ls_tree(repo, revision, source, recursive=True)
    if entries is None:
        raise SyncError(error_code, f"{label}: tree source {source!r} is not present at {revision}")
    projected: list[ProjectedEntry] = []
    for entry in entries:
        if is_excluded_path(entry.path, exclusions):
            continue
        if entry.object_type != "blob" or entry.mode not in FILE_MODES:
            raise SyncError(
                UNSUPPORTED_SPECIAL_FILE,
                f"{label}: {entry.path!r} at {revision} is not a regular, executable, or symlink file",
            )
        content = git_read_blob_by_id(repo, entry.object_id)
        if content is None:
            raise SyncError(error_code, f"{label}: unable to read blob for {entry.path!r} at {revision}")
        projected.append(ProjectedEntry(path=entry.path, mode=entry.mode, content=content))
    return tuple(projected)


def project_file_path(path: Path) -> tuple[ProjectedEntry, ...]:
    """Project an adopter filesystem file (or symlink) into one entry."""

    if path.is_symlink():
        target = os.readlink(path)
        return (ProjectedEntry(path="", mode="120000", content=os.fsencode(target)),)
    if not path.exists():
        return ()
    if not path.is_file():
        raise SyncError(UNSUPPORTED_SPECIAL_FILE, f"{path} is not a regular, executable, or symlink file")
    content = path.read_bytes()
    mode = "100755" if (path.stat().st_mode & 0o111) else "100644"
    return (ProjectedEntry(path="", mode=mode, content=content),)


def _walk_tree(
    directory: Path,
    relative: str,
    exclusions: Sequence[str],
    out: list[ProjectedEntry],
) -> None:
    """Recursively project an adopter directory into logical tree entries."""

    try:
        with os.scandir(directory) as scanner:
            scanned = sorted(scanner, key=lambda entry: entry.name)
    except FileNotFoundError:
        return
    for entry in scanned:
        child = entry.name if relative == "" else f"{relative}/{entry.name}"
        if is_excluded_path(child, exclusions):
            continue
        if entry.is_symlink():
            target = os.readlink(entry.path)
            out.append(ProjectedEntry(path=child, mode="120000", content=os.fsencode(target)))
        elif entry.is_dir(follow_symlinks=False):
            _walk_tree(Path(entry.path), child, exclusions, out)
        elif entry.is_file(follow_symlinks=False):
            stat = entry.stat(follow_symlinks=False)
            mode = "100755" if (stat.st_mode & 0o111) else "100644"
            out.append(ProjectedEntry(path=child, mode=mode, content=Path(entry.path).read_bytes()))
        else:
            raise SyncError(
                UNSUPPORTED_SPECIAL_FILE, f"{entry.path} is not a regular, executable, or symlink file"
            )


def project_tree_path(root: Path, exclusions: Sequence[str]) -> tuple[ProjectedEntry, ...]:
    """Project an adopter filesystem tree into member-relative POSIX entries."""

    if root.is_symlink():
        raise SyncError(UNSUPPORTED_SPECIAL_FILE, f"{root} is a symlink, not a directory")
    if not root.is_dir():
        return ()
    out: list[ProjectedEntry] = []
    _walk_tree(root, "", exclusions, out)
    return tuple(out)


def project_destination(
    adopter_repo: Path,
    destination: str,
    projection: str,
    exclusions: Sequence[str],
) -> tuple[ProjectedEntry, ...]:
    """Project an adopter destination as a file or tree according to projection."""

    path = adopter_repo / destination
    if projection == "file":
        return project_file_path(path)
    if projection == "tree":
        return project_tree_path(path, exclusions)
    raise SyncError(
        UNSUPPORTED_PROJECTION,
        f"destination {destination!r} has unsupported projection {projection!r}",
    )


def digest_entries(entries: Sequence[ProjectedEntry]) -> str | None:
    """Digest a projected entry set, returning None when the destination is absent."""

    if not entries:
        return None
    return compute_member_digest(entries)


# --------------------------------------------------------------------------- #
# Unit/content digest assembly and delta derivation
# --------------------------------------------------------------------------- #


def unit_member_digests(
    repo: Path,
    revision: str,
    unit: CatalogUnit,
    exclusions: Sequence[str],
    error_code: str,
    label: str,
) -> dict[str, str]:
    """Compute per-member digests for a catalog unit at a revision.

    A source path referenced by the catalog but absent at the revision is a
    ``catalog_changed`` fatal error; the message names the unit, member, source
    path, and revision (protocol-v1 Section 8).
    """

    digests: dict[str, str] = {}
    for member in unit.members:
        member_label = f"{label} member {member.id!r}"
        if unit.sync_projection == "file":
            entries = project_file_source(repo, revision, member.source, error_code, member_label)
        elif unit.sync_projection == "tree":
            entries = project_tree_source(
                repo, revision, member.source, exclusions, error_code, member_label
            )
        else:
            raise SyncError(
                UNSUPPORTED_PROJECTION,
                f"{label}: unsupported projection {unit.sync_projection!r}",
            )
        digests[member.id] = compute_member_digest(entries)
    return digests


def unit_content_digest(unit: CatalogUnit, member_digests: dict[str, str]) -> str:
    """Compute a unit digest from its per-member digest map in catalog order."""

    return digest_unit_from_members(tuple((member.id, member_digests[member.id]) for member in unit.members))


def upstream_delta(accepted_digest: str | None, current_digest: str | None) -> str:
    """Derive an upstream delta from accepted and current digests."""

    if accepted_digest is not None and current_digest is not None:
        return "unchanged" if accepted_digest == current_digest else "modified"
    if current_digest is not None:
        return "added"
    if accepted_digest is not None:
        return "removed"
    return "not_applicable"


def member_destination_delta(accepted_digest: str, current_digest: str | None) -> str:
    """Derive a destination delta from an accepted lock digest and current digest."""

    if accepted_digest == "not_applicable":
        return "not_applicable" if current_digest is None else "added"
    if current_digest is None:
        return "removed"
    return "unchanged" if current_digest == accepted_digest else "modified"


def aggregate_destination_delta(deltas: Sequence[str]) -> str:
    """Aggregate member destination deltas into one unit-level delta."""

    if not deltas:
        return "not_applicable"
    if all(delta == "unchanged" for delta in deltas):
        return "unchanged"
    if any(delta == "modified" for delta in deltas):
        return "modified"
    if any(delta == "added" for delta in deltas):
        return "added"
    if any(delta == "removed" for delta in deltas):
        return "removed"
    return "not_applicable"


def _base_disposition(mode: str, delta_upstream: str, delta_destination: str) -> str:
    """Derive the protocol-v1 Section 7 disposition for a mode and both deltas."""

    if mode == "replacement":
        return "review_required"
    if mode == "destination_owned":
        return "unmanaged" if delta_upstream == "unchanged" else "retirement_available"
    if delta_upstream == "removed":
        return "retirement_available"
    upstream_changed = delta_upstream in ("modified", "added")
    destination_changed = delta_destination in ("modified", "added", "removed")
    if not upstream_changed and not destination_changed:
        return "current"
    if upstream_changed and not destination_changed:
        return "update_available"
    if not upstream_changed and destination_changed:
        return "local_drift"
    return "conflict" if mode == "mirror" else "review_required"


def disposition_for(mode: str, delta_upstream: str, delta_destination: str, baseline_behind: bool) -> str:
    """Derive the full disposition including undeclared and baseline-advance cases."""

    if mode == "not_declared":
        if delta_upstream == "added":
            return "adoption_available"
        if delta_upstream == "removed":
            return "retirement_available"
        return "unmanaged"
    base = _base_disposition(mode, delta_upstream, delta_destination)
    if base == "current" and baseline_behind:
        return "baseline_advance_required"
    return base


# --------------------------------------------------------------------------- #
# Report builders
# --------------------------------------------------------------------------- #


def _upstream_member_reports(
    accepted_unit: CatalogUnit | None,
    current_unit: CatalogUnit | None,
    accepted_digests: dict[str, str],
    current_digests: dict[str, str],
) -> tuple[MemberReport, ...]:
    """Build member reports for a unit without a destination mapping."""

    ordered_ids: list[str] = []
    for source in (accepted_unit, current_unit):
        if source is None:
            continue
        for member in source.members:
            if member.id not in ordered_ids:
                ordered_ids.append(member.id)
    reports: list[MemberReport] = []
    for member_id in ordered_ids:
        accepted_digest = accepted_digests.get(member_id)
        current_digest = current_digests.get(member_id)
        reports.append(
            MemberReport(
                id=member_id,
                destination=None,
                upstream_delta=upstream_delta(accepted_digest, current_digest),
                destination_delta="not_applicable",
                accepted_upstream_digest=accepted_digest if accepted_digest is not None else "not_applicable",
                current_upstream_digest=current_digest if current_digest is not None else "not_applicable",
                accepted_destination_digest="not_applicable",
                current_destination_digest="not_applicable",
            )
        )
    return tuple(reports)


def _declared_member_reports(
    unit: DeclarationUnit,
    lock_unit: LockUnit,
    accepted_unit: CatalogUnit | None,
    current_unit: CatalogUnit | None,
    accepted_digests: dict[str, str],
    current_digests: dict[str, str],
    adopter_repo: Path,
    exclusions: Sequence[str],
) -> tuple[MemberReport, ...]:
    """Build member reports for a declared mirror/adapted/destination_owned unit."""

    lock_members = {member.id: member for member in lock_unit.members}
    reference = current_unit if current_unit is not None else accepted_unit
    if reference is None:  # pragma: no cover - validated earlier
        raise SyncError(INVALID_LOCK, f"declared unit {unit.id!r} has no catalog reference")
    projection = reference.sync_projection
    reports: list[MemberReport] = []
    for member in unit.members:
        lock_member = lock_members[member.id]
        destination = normalize_destination(member.destination)
        current_entries = project_destination(adopter_repo, destination, projection, exclusions)
        current_destination_digest = digest_entries(current_entries)
        accepted_digest = accepted_digests.get(member.id)
        current_digest = current_digests.get(member.id)
        reports.append(
            MemberReport(
                id=member.id,
                destination=destination,
                upstream_delta=upstream_delta(accepted_digest, current_digest),
                destination_delta=member_destination_delta(
                    lock_member.accepted_destination_digest, current_destination_digest
                ),
                accepted_upstream_digest=(
                    accepted_digest if accepted_digest is not None else "not_applicable"
                ),
                current_upstream_digest=current_digest if current_digest is not None else "not_applicable",
                accepted_destination_digest=lock_member.accepted_destination_digest,
                current_destination_digest=(
                    current_destination_digest if current_destination_digest is not None else "not_applicable"
                ),
            )
        )
    return tuple(reports)


def build_check_reports(
    declaration: Declaration,
    lock: Lock,
    accepted_catalog: Catalog,
    current_catalog: Catalog,
    upstream_repo: Path,
    adopter_repo: Path,
    accepted_commit: str,
    current_commit: str,
) -> tuple[UnitReport, ...]:
    """Reconcile accepted and current catalogs into orthogonal unit reports."""

    accepted_by_id = {unit.id: unit for unit in accepted_catalog.units}
    current_by_id = {unit.id: unit for unit in current_catalog.units}
    declaration_by_id = {unit.id: unit for unit in declaration.units}
    lock_by_id = {unit.id: unit for unit in lock.units}
    baseline_behind = accepted_commit != current_commit

    all_ids = sorted(set(accepted_by_id) | set(current_by_id))
    reports: list[UnitReport] = []
    for unit_id in all_ids:
        accepted_unit = accepted_by_id.get(unit_id)
        current_unit = current_by_id.get(unit_id)
        declaration_unit = declaration_by_id.get(unit_id)

        accepted_present = accepted_unit is not None and accepted_unit.sync_projection in ("file", "tree")
        current_present = current_unit is not None and current_unit.sync_projection in ("file", "tree")
        if not accepted_present and not current_present:
            continue

        accepted_digests: dict[str, str] = {}
        current_digests: dict[str, str] = {}
        accepted_unit_digest: str | None = None
        current_unit_digest: str | None = None
        if accepted_present and accepted_unit is not None:
            accepted_digests = unit_member_digests(
                upstream_repo,
                accepted_commit,
                accepted_unit,
                accepted_catalog.digest_exclusions,
                CATALOG_CHANGED,
                f"accepted unit {unit_id!r}",
            )
            accepted_unit_digest = unit_content_digest(accepted_unit, accepted_digests)
        if current_present and current_unit is not None:
            current_digests = unit_member_digests(
                upstream_repo,
                current_commit,
                current_unit,
                current_catalog.digest_exclusions,
                CATALOG_CHANGED,
                f"current unit {unit_id!r}",
            )
            current_unit_digest = unit_content_digest(current_unit, current_digests)

        delta_upstream = upstream_delta(accepted_unit_digest, current_unit_digest)

        if declaration_unit is None:
            members = _upstream_member_reports(accepted_unit, current_unit, accepted_digests, current_digests)
            reports.append(
                UnitReport(
                    id=unit_id,
                    mode="not_declared",
                    upstream_delta=delta_upstream,
                    destination_delta="not_applicable",
                    disposition=disposition_for(
                        "not_declared", delta_upstream, "not_applicable", baseline_behind
                    ),
                    members=members,
                    replacement_destinations=(),
                )
            )
            continue

        if declaration_unit.mode == "replacement":
            members = _upstream_member_reports(accepted_unit, current_unit, accepted_digests, current_digests)
            reports.append(
                UnitReport(
                    id=unit_id,
                    mode="replacement",
                    upstream_delta=delta_upstream,
                    destination_delta="not_applicable",
                    disposition=disposition_for(
                        "replacement", delta_upstream, "not_applicable", baseline_behind
                    ),
                    members=members,
                    replacement_destinations=declaration_unit.replacement_destinations,
                )
            )
            continue

        lock_unit = lock_by_id[unit_id]
        members = _declared_member_reports(
            declaration_unit,
            lock_unit,
            accepted_unit,
            current_unit,
            accepted_digests,
            current_digests,
            adopter_repo,
            accepted_catalog.digest_exclusions,
        )
        delta_destination = aggregate_destination_delta(tuple(member.destination_delta for member in members))
        reports.append(
            UnitReport(
                id=unit_id,
                mode=declaration_unit.mode,
                upstream_delta=delta_upstream,
                destination_delta=delta_destination,
                disposition=disposition_for(
                    declaration_unit.mode, delta_upstream, delta_destination, baseline_behind
                ),
                members=members,
                replacement_destinations=(),
            )
        )
    return tuple(reports)


# --------------------------------------------------------------------------- #
# Top-level drivers
# --------------------------------------------------------------------------- #


def check_adoption(
    upstream_repo: Path,
    adopter_repo: Path,
    current_revision: str,
    declaration_path: Path,
    lock_path: Path,
) -> CheckReport:
    """Run the read-only dual-baseline comparison and return the report.

    The accepted catalog and content come from the lock's accepted commit; the
    current catalog and content come from the explicit current revision. The
    declaration and lock are read from the adopter repository, and destination
    content is read from the adopter worktree. No worktree is written.
    """

    current_revision = require_full_commit(current_revision)
    declaration_raw = read_file_bytes(declaration_path, INVALID_MAPPING, "adoption declaration")
    declaration = parse_declaration(declaration_raw, str(declaration_path))
    lock_raw = read_file_bytes(lock_path, INVALID_LOCK, "adoption lock")
    lock = parse_lock(lock_raw, str(lock_path))

    if sha256_digest(declaration_raw) != lock.declaration_digest:
        raise SyncError(
            DECLARATION_CHANGED,
            "declaration raw digest differs from the lock's declaration_digest",
        )
    if lock.upstream_repository != declaration.upstream_repository:
        raise SyncError(INVALID_LOCK, "lock and declaration upstream_repository differ")

    current_commit = git_resolve_commit(upstream_repo, current_revision)
    if current_commit is None:
        raise SyncError(BASELINE_UNAVAILABLE, f"current revision {current_revision!r} is not a commit")
    accepted_commit = git_resolve_commit(upstream_repo, lock.accepted_source_commit)
    if accepted_commit is None:
        raise SyncError(
            BASELINE_UNAVAILABLE,
            f"accepted commit {lock.accepted_source_commit!r} is missing or is not a commit",
        )
    if not git_is_ancestor(upstream_repo, accepted_commit, current_commit):
        raise SyncError(
            BASELINE_UNAVAILABLE,
            f"accepted commit {accepted_commit} is not an ancestor of {current_commit}",
        )

    accepted_catalog_raw = git_read_object(upstream_repo, accepted_commit, CATALOG_PATH)
    if accepted_catalog_raw is None:
        raise SyncError(CATALOG_CHANGED, f"accepted catalog {CATALOG_PATH} is missing at {accepted_commit}")
    if sha256_digest(accepted_catalog_raw) != lock.catalog_digest:
        raise SyncError(
            CATALOG_CHANGED,
            "accepted catalog raw digest differs from the lock's catalog_digest",
        )
    accepted_catalog = parse_catalog(accepted_catalog_raw, f"{CATALOG_PATH}@{accepted_commit}")

    current_catalog_raw = git_read_object(upstream_repo, current_commit, CATALOG_PATH)
    if current_catalog_raw is None:
        raise SyncError(CATALOG_CHANGED, f"current catalog {CATALOG_PATH} is missing at {current_commit}")
    current_catalog = parse_catalog(current_catalog_raw, f"{CATALOG_PATH}@{current_commit}")

    accepted_by_id = {unit.id: unit for unit in accepted_catalog.units}
    current_by_id = {unit.id: unit for unit in current_catalog.units}
    owned = validate_declaration(declaration, accepted_by_id, current_by_id, accepted_catalog.control_paths)
    assert_no_symlink_escape(adopter_repo, owned)
    validate_lock_matches_declaration(declaration, lock)

    units = build_check_reports(
        declaration,
        lock,
        accepted_catalog,
        current_catalog,
        upstream_repo,
        adopter_repo,
        accepted_commit,
        current_commit,
    )
    return CheckReport(status="ok", error=None, units=units)


def _build_lock_unit_document(
    unit: DeclarationUnit,
    catalog_unit: CatalogUnit,
    upstream_repo: Path,
    adopter_repo: Path,
    revision: str,
    exclusions: Sequence[str],
) -> dict[str, object]:
    """Build one candidate lock unit document with accepted digests."""

    if unit.mode == "replacement":
        member_digests = unit_member_digests(
            upstream_repo, revision, catalog_unit, exclusions, CATALOG_CHANGED, f"unit {unit.id!r}"
        )
        return {
            "id": unit.id,
            "mode": "replacement",
            "replacement_destinations": [
                normalize_destination(destination) for destination in unit.replacement_destinations
            ],
            "accepted_upstream_digest": unit_content_digest(catalog_unit, member_digests),
            "accepted_destination_digest": "not_applicable",
        }

    catalog_members = {member.id: member for member in catalog_unit.members}
    lock_members: list[dict[str, str]] = []
    for member in unit.members:
        catalog_member = catalog_members.get(member.id)
        if catalog_member is None:  # pragma: no cover - validated earlier
            raise SyncError(INVALID_MAPPING, f"declaration unit {unit.id!r} member {member.id!r} is unknown")
        member_label = f"unit {unit.id!r} member {member.id!r}"
        if catalog_unit.sync_projection == "file":
            entries = project_file_source(
                upstream_repo, revision, catalog_member.source, CATALOG_CHANGED, member_label
            )
        else:
            entries = project_tree_source(
                upstream_repo,
                revision,
                catalog_member.source,
                exclusions,
                CATALOG_CHANGED,
                member_label,
            )
        upstream_digest = compute_member_digest(entries)
        destination = normalize_destination(member.destination)
        destination_entries = project_destination(
            adopter_repo, destination, catalog_unit.sync_projection, exclusions
        )
        destination_digest = digest_entries(destination_entries)
        if destination_digest is None:
            raise SyncError(
                INVALID_MAPPING,
                f"declared destination {destination!r} is missing in the adopter repository",
            )
        if unit.mode == "mirror" and upstream_digest != destination_digest:
            raise SyncError(
                INVALID_LOCK,
                f"mirror unit {unit.id!r} member {member.id!r} accepted source and destination digests differ",
            )
        lock_members.append(
            {
                "id": member.id,
                "destination": destination,
                "accepted_upstream_digest": upstream_digest,
                "accepted_destination_digest": destination_digest,
            }
        )
    return {"id": unit.id, "mode": unit.mode, "members": lock_members}


def propose_lock(
    upstream_repo: Path,
    adopter_repo: Path,
    current_revision: str,
    declaration_path: Path,
) -> str:
    """Build a candidate adoption lock and return candidate YAML text.

    The candidate's accepted commit is the current revision. Nothing is written
    to the filesystem; the caller writes the returned text to stdout.
    """

    current_revision = require_full_commit(current_revision)
    declaration_raw = read_file_bytes(declaration_path, INVALID_MAPPING, "adoption declaration")
    declaration = parse_declaration(declaration_raw, str(declaration_path))

    current_commit = git_resolve_commit(upstream_repo, current_revision)
    if current_commit is None:
        raise SyncError(BASELINE_UNAVAILABLE, f"current revision {current_revision!r} is not a commit")

    catalog_raw = git_read_object(upstream_repo, current_commit, CATALOG_PATH)
    if catalog_raw is None:
        raise SyncError(CATALOG_CHANGED, f"catalog {CATALOG_PATH} is missing at {current_commit}")
    catalog = parse_catalog(catalog_raw, f"{CATALOG_PATH}@{current_commit}")
    units_by_id = {unit.id: unit for unit in catalog.units}

    owned = validate_declaration(declaration, units_by_id, units_by_id, catalog.control_paths)
    assert_no_symlink_escape(adopter_repo, owned)

    lock_units = [
        _build_lock_unit_document(
            unit,
            units_by_id[unit.id],
            upstream_repo,
            adopter_repo,
            current_commit,
            catalog.digest_exclusions,
        )
        for unit in declaration.units
    ]
    document: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "upstream_repository": declaration.upstream_repository,
        "accepted_source_commit": current_commit,
        "catalog_digest": sha256_digest(catalog_raw),
        "declaration_digest": sha256_digest(declaration_raw),
        "units": lock_units,
    }
    text = yaml.safe_dump(document, sort_keys=False, default_flow_style=False, allow_unicode=True)
    return text.rstrip("\n") + "\n"


# --------------------------------------------------------------------------- #
# Stable rendering
# --------------------------------------------------------------------------- #


def render_check_json(report: CheckReport) -> str:
    """Render a ``check`` report as stable JSON text."""

    document: dict[str, object] = {
        "status": report.status,
        "error": report.error,
        "units": [
            {
                "id": unit.id,
                "mode": unit.mode,
                "upstream_delta": unit.upstream_delta,
                "destination_delta": unit.destination_delta,
                "disposition": unit.disposition,
                "members": [
                    {
                        "id": member.id,
                        "destination": member.destination,
                        "upstream_delta": member.upstream_delta,
                        "destination_delta": member.destination_delta,
                        "accepted_upstream_digest": member.accepted_upstream_digest,
                        "current_upstream_digest": member.current_upstream_digest,
                        "accepted_destination_digest": member.accepted_destination_digest,
                        "current_destination_digest": member.current_destination_digest,
                    }
                    for member in unit.members
                ],
                "replacement_destinations": list(unit.replacement_destinations),
            }
            for unit in report.units
        ],
    }
    return json.dumps(document, indent=2) + "\n"


def render_check_human(report: CheckReport) -> str:
    """Render a ``check`` report as stable human-readable text."""

    lines = [
        f"status: {report.status}",
        f"error: {report.error if report.error is not None else 'null'}",
    ]
    for unit in report.units:
        lines.append(
            f"- {unit.id} | mode={unit.mode} | upstream_delta={unit.upstream_delta} "
            f"| destination_delta={unit.destination_delta} | disposition={unit.disposition}"
        )
        for member in unit.members:
            lines.append(
                f"    member {member.id} | destination={member.destination} "
                f"| upstream_delta={member.upstream_delta} | destination_delta={member.destination_delta}"
            )
    return "\n".join(lines) + "\n"


def render_check(report: CheckReport, output_format: str) -> str:
    """Render a ``check`` report in the requested format."""

    if output_format == "json":
        return render_check_json(report)
    return render_check_human(report)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _resolve_adopter_path(adopter_repo: Path, raw: str) -> Path:
    """Resolve a declaration/lock path relative to the adopter repository."""

    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate
    return adopter_repo / candidate


def require_full_commit(revision: str) -> str:
    """Require a full 40-character lowercase hex commit id.

    Rejects branch names, tags, abbreviated shas, and any other revision form
    with a fatal ``baseline_unavailable`` before the command does any work.
    """

    if not isinstance(revision, str) or not COMMIT_RE.fullmatch(revision):
        raise SyncError(
            BASELINE_UNAVAILABLE,
            f"--current-revision must be a full 40-character commit: {revision!r}",
        )
    return revision


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser exposing only ``check`` and ``propose-lock``."""

    parser = argparse.ArgumentParser(
        prog="sync_aicore_adoption.py",
        description="Read-only AICore adoption synchronization checker and lock proposer.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="Report per-unit mode, deltas, and disposition.")
    check.add_argument("--upstream-repo", required=True, help="Path to the AICore upstream repository.")
    check.add_argument("--adopter-repo", required=True, help="Path to the adopter repository.")
    check.add_argument(
        "--current-revision", required=True, help="Full 40-character commit to compare against."
    )
    check.add_argument("--declaration", default=".aicore/adoption.yaml", help="Adopter declaration path.")
    check.add_argument("--lock", default=".aicore/adoption.lock.yaml", help="Adoption lock path.")
    check.add_argument("--format", choices=("json", "human"), default="human", help="Output format.")

    propose = subparsers.add_parser(
        "propose-lock", help="Emit a candidate adoption lock to stdout only."
    )
    propose.add_argument("--upstream-repo", required=True, help="Path to the AICore upstream repository.")
    propose.add_argument("--adopter-repo", required=True, help="Path to the adopter repository.")
    propose.add_argument(
        "--current-revision", required=True, help="Full 40-character commit to accept as the baseline."
    )
    propose.add_argument("--declaration", default=".aicore/adoption.yaml", help="Adopter declaration path.")

    return parser


def _run_check(args: argparse.Namespace) -> int:
    """Execute the ``check`` subcommand and return its exit code."""

    adopter_repo = Path(args.adopter_repo)
    declaration_path = _resolve_adopter_path(adopter_repo, args.declaration)
    lock_path = _resolve_adopter_path(adopter_repo, args.lock)
    try:
        report = check_adoption(
            Path(args.upstream_repo),
            adopter_repo,
            args.current_revision,
            declaration_path,
            lock_path,
        )
    except SyncError as exc:
        error_report = CheckReport(status="error", error=exc.code, units=())
        sys.stdout.write(render_check(error_report, args.format))
        sys.stderr.write(f"error: {exc.code}: {exc.message}\n")
        return 2
    sys.stdout.write(render_check(report, args.format))
    return 0


def _run_propose_lock(args: argparse.Namespace) -> int:
    """Execute the ``propose-lock`` subcommand and return its exit code."""

    adopter_repo = Path(args.adopter_repo)
    declaration_path = _resolve_adopter_path(adopter_repo, args.declaration)
    try:
        output = propose_lock(
            Path(args.upstream_repo),
            adopter_repo,
            args.current_revision,
            declaration_path,
        )
    except SyncError as exc:
        sys.stderr.write(f"error: {exc.code}: {exc.message}\n")
        return 2
    sys.stdout.write(output)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Parse arguments and dispatch to the requested subcommand."""

    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "check":
        return _run_check(args)
    if args.command == "propose-lock":
        return _run_propose_lock(args)
    parser.error(f"unknown command {args.command!r}")  # pragma: no cover - argparse guards this
    return 2  # pragma: no cover - argparse exits before this


if __name__ == "__main__":
    sys.exit(main())
