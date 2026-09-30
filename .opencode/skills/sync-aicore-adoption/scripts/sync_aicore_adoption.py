"""Core substrate for the ``sync-aicore-adoption`` protocol v2.

Implements the CLI surface, the v2 document loaders with schema-shape
validation, the Section 7 digest protocol, the Section 6 applicability model,
the read-only ``check`` command (Sections 8-12), the stdout-only
``propose-lock`` command (Sections 3-4, 15), the read-only ``verify-all``
aggregate over the adopter registry (Section 16), the portable-story
index merge (Section 17), and the ``apply`` command (Sections 11, 18): it
classifies the bounded write set, refuses every unit outside it, journals
every path it intends to write, stages the writable members, merges the story
index for writable story units, regenerates the candidate lock through the
``propose-lock`` builder, and verifies the result with the ``check`` report.
Any failure after the first mutation triggers a best-effort restore of every
journaled path before that failure is surfaced; a restore that cannot put a
path back emits an ``apply_restore_failed`` recovery record on stderr naming
every path that may now be inconsistent. The restore is best-effort, never
atomic, and never a crash transaction.

``check``, ``propose-lock``, and ``verify-all`` are read-only by
construction: they mutate no upstream or adopter repository, index, or
worktree, and ``propose-lock`` writes only to stdout. ``apply`` is the single
write path: it writes only adopter worktree content and the adopter lock
file, never Git state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import (
    Callable,
    Iterable,
    Literal,
    Mapping,
    NoReturn,
    Protocol,
    Sequence,
    TypedDict,
)

import yaml

EXIT_FATAL = 2
PROFILE_MARKERS = ("backend_stack", "python_scripts", "ticket_system")
DECLARATION_MODES = ("mirror", "adapted", "replacement", "destination_owned", "not_applicable")
LOCK_MODES = DECLARATION_MODES
PROJECTIONS = ("file", "tree")
SYNC_PROJECTIONS = ("file", "guarded_file", "tree", "assertions")
DESTINATION_POLICIES = ("adopter_root_runtime",)
REVIEW_DECISIONS = ("applied", "declined", "superseded")
COLLISION_POLICIES = ("core_wins",)
STORY_UNIT_KIND = "user-story"
STORY_INDEX_NAME = "index.md"
LOCK_DIGEST_FIELDS = (
    "accepted_catalog_digest",
    "declaration_digest",
    "review_digest",
    "accepted_snapshot_digest",
)
SCHEMA_UPGRADE_GUIDANCE = (
    "schema_version 1 is upgrade-only input. Re-declare the adopter under v2 (add the "
    "profile block, cover every catalog unit including former `none` config units), author "
    "the v2 review, and regenerate a fresh v2 lock at one revision. See "
    "references/protocol-v2.md Section 14."
)


class SyncError(Exception):
    """A protocol failure carrying a stable machine ``code``."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _fail(code: str, message: str) -> NoReturn:
    raise SyncError(code, message)


def _need(condition: object, code: str, message: str) -> None:
    if not condition:
        _fail(code, message)


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _is_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and value.startswith("sha256:")
        and len(value) == 71
        and all(char in "0123456789abcdef" for char in value[7:])
    )


def _field(record: object, name: str, default: object = None) -> object:
    if isinstance(record, Mapping):
        return record.get(name, default)
    return getattr(record, name, default)


def _fields(record: object, where: str, code: str, *names: str) -> None:
    _need(isinstance(record, dict), code, f"{where} must be a mapping")
    for name in names:
        value = _field(record, name)
        _need(
            isinstance(value, str) and bool(value),
            code,
            f"{where}.{name} must be a non-empty string",
        )


def _mapping_list(value: object, where: str, code: str, *names: str) -> list:
    _need(isinstance(value, list) and bool(value), code, f"{where} must be a non-empty list")
    for index, item in enumerate(value):
        _fields(item, f"{where}[{index}]", code, *names)
    return value


def _normalize_destination(destination: str) -> str:
    normalized = destination.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _read_document(path: str, code: str) -> dict:
    """IO helper: read a YAML top-level mapping from ``path`` or fail with ``code``."""
    try:
        with open(path, "r", encoding="utf-8") as handle:
            document = yaml.safe_load(handle)
    except FileNotFoundError:
        _fail(code, f"document not found: {path}")
    except (OSError, yaml.YAMLError) as exc:
        _fail(code, f"cannot read {path}: {exc}")
    _need(isinstance(document, dict), code, f"{path} must be a top-level mapping")
    return document


def _require_v2(document: dict, label: str, code: str) -> None:
    version = document.get("schema_version")
    if version == 1:
        _fail("schema_upgrade_required", f"{label}: schema_version 1 is upgrade-only input")
    _need(version == 2, code, f"{label}: schema_version must be 2, got {version!r}")


def _applicability(node: object, where: str) -> None:
    _need(isinstance(node, dict), "invalid_applicability", f"{where} must be a mapping")
    if set(node) == {"always"}:
        _need(node["always"] is True, "invalid_applicability", f"{where}.always must be true")
        return
    for kind in ("requires", "any_of"):
        if set(node) == {kind}:
            markers = node[kind]
            markers_ok = isinstance(markers, list) and bool(markers)
            markers_ok = markers_ok and all(isinstance(m, str) and m for m in markers)
            _need(
                markers_ok,
                "invalid_applicability",
                f"{where}.{kind} must be a non-empty marker list",
            )
            return
    _fail("invalid_applicability", f"{where} must be always/requires/any_of")


def _catalog_unit(unit: object, where: str, seen: set[str]) -> None:
    _fields(unit, where, "invalid_mapping", "id", "kind", "install_strategy")
    _need(unit["id"] not in seen, "invalid_mapping", f"{where}.id duplicated: {unit['id']}")
    seen.add(unit["id"])
    _applicability(unit.get("applicability"), f"{where}.applicability")
    projection = unit.get("sync_projection")
    _need(
        projection in SYNC_PROJECTIONS,
        "unsupported_projection",
        f"{where}.sync_projection must be one of {SYNC_PROJECTIONS}",
    )
    if projection == "assertions":
        destination = unit.get("destination")
        _need(
            isinstance(destination, str) and bool(destination),
            "invalid_mapping",
            f"{where}.destination must be a non-empty string",
        )
        _mapping_list(
            unit.get("assertions"),
            f"{where}.assertions",
            "invalid_mapping",
            "id",
            "contains",
        )
    else:
        members = _mapping_list(
            unit.get("members"),
            f"{where}.members",
            "invalid_mapping",
            "id",
            "source",
            "destination",
        )
        for index, member in enumerate(members):
            if "collision_policy" not in member:
                continue
            _need(
                member["collision_policy"] in COLLISION_POLICIES,
                "invalid_mapping",
                f"{where}.members[{index}].collision_policy must be one of "
                f"{COLLISION_POLICIES}",
            )
    if projection == "guarded_file":
        _need(
            unit.get("destination_policy") in DESTINATION_POLICIES,
            "invalid_mapping",
            f"{where}.destination_policy must be one of {DESTINATION_POLICIES}",
        )
    else:
        _need(
            "destination_policy" not in unit,
            "invalid_mapping",
            f"{where}.destination_policy is valid only for guarded_file",
        )


def _declaration_unit(unit: object, where: str, seen: set[str]) -> None:
    _fields(unit, where, "invalid_declaration", "id")
    _need(unit["id"] not in seen, "invalid_declaration", f"{where}.id duplicated: {unit['id']}")
    seen.add(unit["id"])
    mode = unit.get("mode")
    _need(
        mode in DECLARATION_MODES,
        "invalid_declaration",
        f"{where}.mode must be one of {DECLARATION_MODES}",
    )
    if unit.get("members") is not None:
        _mapping_list(
            unit.get("members"),
            f"{where}.members",
            "invalid_declaration",
            "id",
            "destination",
        )
    replacement = unit.get("replacement_members")
    if replacement is not None:
        _need(
            mode == "replacement",
            "invalid_declaration",
            f"{where}.replacement_members is valid only for mode replacement",
        )
        rows = _mapping_list(
            replacement,
            f"{where}.replacement_members",
            "invalid_declaration",
            "id",
            "destination",
        )
        replacement_ids: set[str] = set()
        for index, member in enumerate(rows):
            member_id = member["id"]
            _need(
                member_id not in replacement_ids,
                "invalid_declaration",
                f"{where}.replacement_members[{index}].id duplicated: {member_id}",
            )
            replacement_ids.add(member_id)
            projection = member.get("projection")
            _need(
                projection in PROJECTIONS,
                "invalid_declaration",
                f"{where}.replacement_members[{index}].projection must be one of {PROJECTIONS}",
            )
    elif mode == "replacement":
        _fail(
            "invalid_declaration",
            f"{where}.replacement_members required for mode replacement",
        )


def _lock_member(member: object, where: str, seen: set[str], replacement: bool) -> None:
    _fields(member, where, "invalid_lock", "id", "destination")
    _need(member["id"] not in seen, "invalid_lock", f"{where}.id duplicated: {member['id']}")
    seen.add(member["id"])
    if replacement:
        _need(
            member.get("projection") in PROJECTIONS,
            "invalid_lock",
            f"{where}.projection must be one of {PROJECTIONS}",
        )
        names = ("accepted_destination_digest",)
    else:
        names = ("accepted_upstream_digest", "accepted_destination_digest")
    for name in names:
        _need(
            _is_digest(member.get(name)),
            "invalid_lock",
            f"{where}.{name} must be sha256:<hex>",
        )


def _lock_unit(unit: object, where: str, seen: set[str]) -> None:
    _fields(unit, where, "invalid_lock", "id")
    _need(
        "accepted_source_commit" not in unit,
        "invalid_lock",
        f"{where}: per-unit accepted_source_commit forbidden "
        "(single top-level accepted_source_commit)",
    )
    _need(unit["id"] not in seen, "invalid_lock", f"{where}.id duplicated: {unit['id']}")
    seen.add(unit["id"])
    mode = unit.get("mode")
    _need(mode in LOCK_MODES, "invalid_lock", f"{where}.mode must be one of {LOCK_MODES}")
    if mode == "not_applicable":
        return
    for name in ("declaration_unit_digest", "accepted_upstream_digest"):
        _need(
            _is_digest(unit.get(name)),
            "invalid_lock",
            f"{where}.{name} must be sha256:<hex>",
        )
    key = "replacement_members" if mode == "replacement" else "members"
    rows = _mapping_list(
        unit.get(key), f"{where}.{key}", "invalid_lock", "id", "destination"
    )
    member_ids: set[str] = set()
    for index, member in enumerate(rows):
        _lock_member(
            member, f"{where}.{key}[{index}]", member_ids, mode == "replacement"
        )


def load_catalog(path: str) -> dict:
    """Parse and shape-validate a schema-v2 catalog document."""
    document = _read_document(path, "invalid_mapping")
    _require_v2(document, path, "invalid_mapping")
    _fields(
        document.get("catalog"),
        f"{path}: catalog",
        "invalid_mapping",
        "upstream_repository",
    )
    units = document.get("units")
    _need(isinstance(units, list), "invalid_mapping", f"{path}: units must be a list")
    seen: set[str] = set()
    for index, unit in enumerate(units):
        _catalog_unit(unit, f"{path}: units[{index}]", seen)
    return document


def load_declaration(path: str) -> dict:
    """Parse and shape-validate a schema-v2 adopter declaration."""
    document = _read_document(path, "invalid_declaration")
    _require_v2(document, path, "invalid_declaration")
    _fields(document, path, "invalid_declaration", "upstream_repository")
    profile = document.get("profile")
    _need(
        isinstance(profile, dict),
        "invalid_declaration",
        f"{path}: profile must be a mapping",
    )
    for marker in PROFILE_MARKERS:
        _need(
            isinstance(profile.get(marker), bool),
            "invalid_declaration",
            f"{path}: profile.{marker} must be a boolean",
        )
    units = document.get("units")
    _need(isinstance(units, list), "invalid_declaration", f"{path}: units must be a list")
    seen: set[str] = set()
    for index, unit in enumerate(units):
        _declaration_unit(unit, f"{path}: units[{index}]", seen)
    return document


def load_review(path: str) -> dict:
    """Parse and shape-validate a schema-v2 reconciliation review."""
    document = _read_document(path, "invalid_declaration")
    _require_v2(document, path, "invalid_declaration")
    decisions = document.get("decisions")
    _need(
        isinstance(decisions, list),
        "invalid_declaration",
        f"{path}: decisions must be a list",
    )
    for index, decision in enumerate(decisions):
        where = f"{path}: decisions[{index}]"
        _fields(decision, where, "invalid_declaration", "unit", "reviewer")
        choice = decision.get("decision")
        _need(
            choice in REVIEW_DECISIONS,
            "invalid_declaration",
            f"{where}.decision must be one of {REVIEW_DECISIONS}",
        )
        if choice in ("declined", "superseded"):
            _fields(decision, where, "invalid_declaration", "evidence")
    return document


def load_lock(path: str) -> dict:
    """Parse and shape-validate a schema-v2 generated lock."""
    document = _read_document(path, "invalid_lock")
    _require_v2(document, path, "invalid_lock")
    _fields(document, path, "invalid_lock", "accepted_source_commit")
    for name in LOCK_DIGEST_FIELDS:
        _need(
            _is_digest(document.get(name)),
            "invalid_lock",
            f"{path}: {name} must be sha256:<hex>",
        )
    units = document.get("units")
    _need(isinstance(units, list), "invalid_lock", f"{path}: units must be a list")
    seen: set[str] = set()
    for index, unit in enumerate(units):
        _lock_unit(unit, f"{path}: units[{index}]", seen)
    return document


@dataclass(frozen=True)
class ProjectedEntry:
    """One projected file/tree entry: logical path, mode, raw content."""

    path: str
    mode: str
    content: bytes


def _coerce_entry(entry: object) -> ProjectedEntry:
    if isinstance(entry, ProjectedEntry):
        return entry
    path = _field(entry, "path")
    mode = _field(entry, "mode", "100644")
    content = _field(entry, "content", b"")
    _need(
        isinstance(path, str) and isinstance(mode, str) and isinstance(content, bytes),
        "unsupported_special_file",
        "each entry requires path:str, mode:str, content:bytes",
    )
    return ProjectedEntry(path, mode, content)


def _is_excluded(path: str) -> bool:
    return "__pycache__" in path.replace("\\", "/").split("/") or path.endswith(".pyc")


def member_digest(entries: Iterable[object]) -> str:
    """Digest a file/tree member: Section 7 entry/path/mode/size/content framing."""
    ordered = sorted(
        (_coerce_entry(entry) for entry in entries),
        key=lambda item: item.path.encode("utf-8"),
    )
    chunks: list[bytes] = []
    for entry in ordered:
        if _is_excluded(entry.path):
            continue
        chunks.append(
            b"entry\npath:" + entry.path.encode("utf-8")
            + b"\nmode:" + entry.mode.encode("ascii")
            + b"\nsize:" + str(len(entry.content)).encode("ascii")
            + b"\ncontent:" + entry.content + b"\n"
        )
    return _sha256(b"".join(chunks))


def unit_digest(members: Iterable[tuple[str, str]]) -> str:
    """Digest a unit over ordered ``(member_id, member_digest)`` pairs."""
    chunks: list[bytes] = []
    for member_id, digest in members:
        chunks.append(
            b"member\nid:" + member_id.encode("utf-8")
            + b"\ndigest:" + digest.encode("ascii")
            + b"\n"
        )
    return _sha256(b"".join(chunks))


def declaration_unit_digest(
    mode: str,
    members: Sequence[object] | None = None,
    replacement_members: Sequence[object] | None = None,
) -> str:
    """Digest one declaration unit's intent: mode plus normalized mapping."""
    chunks: list[bytes] = [b"mode:" + mode.encode("ascii") + b"\n"]
    ordered_members = sorted(
        (
            _field(m, "id"),
            _normalize_destination(str(_field(m, "destination"))),
        )
        for m in (members or [])
    )
    for member_id, destination in ordered_members:
        chunks.append(
            b"member\nid:" + str(member_id).encode("utf-8")
            + b"\ndestination:" + destination.encode("utf-8")
            + b"\n"
        )
    ordered_replacements = sorted(
        (
            _field(m, "id"),
            _normalize_destination(str(_field(m, "destination"))),
            _field(m, "projection"),
        )
        for m in (replacement_members or [])
    )
    for member_id, destination, projection in ordered_replacements:
        chunks.append(
            b"replacement\nid:" + str(member_id).encode("utf-8")
            + b"\ndestination:" + destination.encode("utf-8")
            + b"\nprojection:" + str(projection).encode("ascii")
            + b"\n"
        )
    return _sha256(b"".join(chunks))


def assertion_list_digest(assertions: Iterable[object]) -> str:
    """Digest the ordered catalog assertion list using Section 7 framing."""
    chunks: list[bytes] = []
    for assertion in assertions:
        assertion_id = _field(assertion, "id")
        contains = _field(assertion, "contains")
        _need(
            isinstance(assertion_id, str) and bool(assertion_id),
            "invalid_mapping",
            "assertion.id must be a non-empty string",
        )
        _need(
            isinstance(contains, str) and bool(contains),
            "invalid_mapping",
            "assertion.contains must be a non-empty string",
        )
        chunks.append(
            b"assertion\nid:" + assertion_id.encode("utf-8")
            + b"\ncontains:" + contains.encode("utf-8")
            + b"\n"
        )
    return _sha256(b"".join(chunks))


def assertion_status_digest(
    status_map: Mapping[str, object] | Iterable[tuple[str, object]],
) -> str:
    """Digest ordered assertion presence: ``present`` becomes ``1`` or ``0``."""
    items = status_map.items() if isinstance(status_map, Mapping) else status_map
    chunks: list[bytes] = []
    for assertion_id, present in items:
        chunks.append(
            b"status\nid:" + str(assertion_id).encode("utf-8")
            + b"\npresent:" + (b"1" if present else b"0")
            + b"\n"
        )
    return _sha256(b"".join(chunks))


def evaluate_applicability(catalog_unit: object, profile: Mapping[str, object]) -> bool:
    """Return whether a catalog unit applies under the declaration profile (Section 6)."""
    applicability = _field(catalog_unit, "applicability")
    _need(
        isinstance(applicability, Mapping),
        "invalid_applicability",
        "unit applicability must be a mapping",
    )
    if set(applicability) == {"always"}:
        return applicability["always"] is True
    if set(applicability) == {"requires"}:
        requires = applicability["requires"]
        return all(bool(profile.get(str(marker), False)) for marker in requires)
    if set(applicability) == {"any_of"}:
        any_of = applicability["any_of"]
        return any(bool(profile.get(str(marker), False)) for marker in any_of)
    _fail("invalid_applicability", "applicability must be always/requires/any_of")


# ---------------------------------------------------------------------------
# portable story projection (protocol-v2 Section 17): index merge
# ---------------------------------------------------------------------------


def _line_content(line: bytes) -> bytes:
    """Return one line's bytes without its trailing line ending."""
    return line.rstrip(b"\r\n")


def _line_ending(line: bytes) -> bytes:
    """Return the trailing line-ending bytes of one line (possibly empty)."""
    return line[len(_line_content(line)):]


def _is_story_separator(line: bytes) -> bool:
    """Return whether a table line is the markdown separator row (``|---|``)."""
    content = _line_content(line).strip()
    return (
        content.startswith(b"|")
        and b"-" in content
        and not (set(content) - set(b"|-: \t"))
    )


def _story_row_slug(line: bytes) -> str | None:
    """Return a table row's first cell as its slug key, or ``None`` when unkeyed."""
    content = _line_content(line)
    if not content.startswith(b"|"):
        return None
    cells = content.split(b"|")
    if len(cells) < 3:
        return None
    first = cells[1].strip()
    if len(first) >= 3 and first.startswith(b"`") and first.endswith(b"`"):
        first = first[1:-1]
    if not first:
        return None
    try:
        return first.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _story_table_block(lines: Sequence[bytes]) -> tuple[int, int] | None:
    """Return the ``[start, end)`` line span of the first markdown table."""
    start: int | None = None
    end = 0
    for index, line in enumerate(lines):
        if _line_content(line).startswith(b"|"):
            if start is None:
                start = index
            end = index + 1
        elif start is not None:
            break
    if start is None:
        return None
    return start, end


def _keyed_story_rows(lines: Sequence[bytes]) -> dict[str, bytes]:
    """Map each data-row slug of the first table to its content (no ending)."""
    rows: dict[str, bytes] = {}
    block = _story_table_block(lines)
    if block is None:
        return rows
    start, end = block
    for index in range(start + 1, end):
        if _is_story_separator(lines[index]):
            continue
        slug = _story_row_slug(lines[index])
        if slug is not None and slug not in rows:
            rows[slug] = _line_content(lines[index])
    return rows


def _seed_story_index(core_lines: Sequence[bytes], slugs: Sequence[str]) -> bytes:
    """Build a fresh destination index: the core document minus non-member rows."""
    wanted = set(slugs)
    block = _story_table_block(core_lines)
    if block is None:
        return b"".join(core_lines)
    start, end = block
    kept: list[bytes] = []
    for index, line in enumerate(core_lines):
        if start <= index < end and index != start and not _is_story_separator(line):
            slug = _story_row_slug(line)
            if slug is not None and slug not in wanted:
                continue
        kept.append(line)
    return b"".join(kept)


def _append_core_story_table(
    destination_index: bytes,
    core_lines: Sequence[bytes],
    core_rows: Mapping[str, bytes],
    members: Sequence[tuple[str, str, object]],
) -> bytes:
    """Append the applicable core table block after a destination without a table."""
    block = _story_table_block(core_lines)
    if block is None:
        return destination_index
    start, end = block
    header = core_lines[start]
    ending = _line_ending(header) or b"\n"
    table_lines = [header]
    for index in range(start + 1, end):
        if _is_story_separator(core_lines[index]):
            table_lines.append(core_lines[index])
            break
    table_lines.extend(
        core_rows[slug] + ending for slug, _destination, _policy in members
    )
    out = destination_index
    if out and not out.endswith(b"\n"):
        out += b"\n"
    if out and not out.endswith(b"\n\n"):
        out += b"\n"
    return out + b"".join(table_lines)


def _merge_story_rows(
    destination_index: bytes,
    core_lines: Sequence[bytes],
    core_rows: Mapping[str, bytes],
    members: Sequence[tuple[str, str, object]],
) -> tuple[bytes, list[str]]:
    """Merge core rows into an existing destination table, reporting collisions."""
    lines = destination_index.splitlines(keepends=True)
    block = _story_table_block(lines)
    if block is None:
        return (
            _append_core_story_table(destination_index, core_lines, core_rows, members),
            [],
        )
    start, end = block
    table_ending = _line_ending(lines[start]) or b"\n"
    row_index: dict[str, int] = {}
    for index in range(start + 1, end):
        if _is_story_separator(lines[index]):
            continue
        slug = _story_row_slug(lines[index])
        if slug is not None and slug not in row_index:
            row_index[slug] = index
    collisions: list[str] = []
    missing: list[str] = []
    for slug, destination, policy in members:
        index = row_index.get(slug)
        if index is None:
            missing.append(slug)
            continue
        core_row = core_rows[slug]
        if _line_content(lines[index]) == core_row:
            continue
        if policy not in COLLISION_POLICIES:
            continue
        lines[index] = core_row + _line_ending(lines[index])
        collisions.append(f"collision: path {destination}; core wins")
        collisions.append(f"collision: slug {slug}; core wins")
    if missing:
        if not lines[end - 1].endswith((b"\n", b"\r")):
            lines[end - 1] = lines[end - 1] + table_ending
        lines[end:end] = [core_rows[slug] + table_ending for slug in missing]
    return b"".join(lines), collisions


class StoryMergeMember(TypedDict):
    id: str
    destination: str
    collision_policy: str | None


def merge_story_index(
    core_index: bytes,
    destination_index: bytes | None,
    members: Sequence[StoryMergeMember],
) -> tuple[bytes, list[str]]:
    """Pure story-index merge (bytes in, bytes out, no file IO).

    Seeds a fresh destination with only the applicable core rows; for an
    existing index inserts missing core rows and replaces differing rows
    inside the existing table. Destination-only rows, rows of members
    without ``collision_policy: core_wins``, and every byte before and
    after the table are preserved byte-for-byte (line endings included).
    Returns the merged bytes plus one ``collision: path <destination>;
    core wins`` and one ``collision: slug <slug>; core wins`` string per
    differing ``core_wins`` member; identical rows report nothing.
    """
    parsed: list[tuple[str, str, object]] = []
    for index, member in enumerate(members):
        slug = _field(member, "id")
        destination = _field(member, "destination")
        _need(
            isinstance(slug, str) and bool(slug),
            "invalid_mapping",
            f"members[{index}].id must be a non-empty string",
        )
        _need(
            isinstance(destination, str) and bool(destination),
            "invalid_mapping",
            f"members[{index}].destination must be a non-empty string",
        )
        policy = _field(member, "collision_policy")
        _need(
            policy is None or policy in COLLISION_POLICIES,
            "invalid_mapping",
            f"members[{index}].collision_policy must be one of {COLLISION_POLICIES}",
        )
        parsed.append((str(slug), str(destination), policy))
    core_lines = core_index.splitlines(keepends=True)
    core_rows = _keyed_story_rows(core_lines)
    for slug, _destination, _policy in parsed:
        _need(
            slug in core_rows,
            "invalid_mapping",
            f"core story index has no row for member {slug!r}",
        )
    if destination_index is None or destination_index == b"":
        return _seed_story_index(core_lines, [slug for slug, _, _ in parsed]), []
    return _merge_story_rows(destination_index, core_lines, core_rows, parsed)


def _sibling_story_index(member_path: str) -> str:
    """Return the ``index.md`` path beside one story member path."""
    normalized = member_path.replace("\\", "/")
    if "/" not in normalized:
        return STORY_INDEX_NAME
    directory = normalized.rsplit("/", 1)[0]
    return f"{directory}/{STORY_INDEX_NAME}"


def _story_index_collisions(
    uid: str,
    catalog_unit: Mapping[str, object],
    decl_unit: Mapping[str, object],
    upstream: _GitRepo,
    commit: str,
    snapshot: _Snapshot,
) -> list[str]:
    """IO boundary: merge one applicable story unit's index in memory.

    The core index sits beside the unit's catalog member sources and the
    destination index beside the declared member destinations. The merged
    bytes stay in memory — this command path writes nothing.
    """
    declared = _declared_members(catalog_unit, decl_unit, uid)
    members = list(catalog_unit.get("members", []))
    _need(members, "invalid_mapping", f"{uid}: user-story unit must declare members")
    first = members[0]
    core_index_path = _sibling_story_index(str(_field(first, "source")))
    destination_index_path = _sibling_story_index(
        _normalize_destination(declared[str(_field(first, "id"))])
    )
    core_entry = upstream.file_entry(commit, core_index_path, "baseline_unavailable")
    destination_entry = snapshot.file_entry(destination_index_path)
    rows: list[StoryMergeMember] = [
        {
            "id": str(_field(member, "id")),
            "destination": declared[str(_field(member, "id"))],
            "collision_policy": _field(member, "collision_policy"),
        }
        for member in members
    ]
    _merged, collisions = merge_story_index(
        core_entry.content if core_entry is not None else b"",
        destination_entry.content if destination_entry is not None else None,
        rows,
    )
    return collisions


# ---------------------------------------------------------------------------
# check (protocol-v2 Sections 8-12): read-only compliance report
# ---------------------------------------------------------------------------

_BLOCKING_DISPOSITIONS = frozenset(
    {
        "policy_violation",
        "update_available",
        "local_drift",
        "review_required",
        "conflict",
        "baseline_advance_required",
    }
)
_REVIEW_MODES = ("adapted", "replacement", "destination_owned")


class _GitRepo:
    """Read-only Git object reader; never writes the repository, index, or worktree."""

    def __init__(self, path: str) -> None:
        self.path = path

    def _run(self, *args: str) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            ["git", "-C", self.path, *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def resolve(self, rev: str) -> str | None:
        proc = self._run("rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")
        if proc.returncode == 0:
            return proc.stdout.decode("ascii", "replace").strip()
        return None

    def toplevel(self) -> str | None:
        proc = self._run("rev-parse", "--show-toplevel")
        if proc.returncode == 0:
            return proc.stdout.decode("utf-8", "replace").strip()
        return None

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        proc = self._run("merge-base", "--is-ancestor", ancestor, descendant)
        return proc.returncode == 0

    def blob(self, object_id: str, code: str) -> bytes:
        proc = self._run("cat-file", "-p", object_id)
        if proc.returncode != 0:
            _fail(code, f"cannot read Git object {object_id}")
        return proc.stdout

    def show_blob(self, commit: str, path: str) -> bytes | None:
        proc = self._run("show", f"{commit}:{path}")
        if proc.returncode == 0:
            return proc.stdout
        return None

    def file_entry(self, rev: str, path: str, code: str) -> ProjectedEntry | None:
        blobs = [record for record in self._ls_tree(rev, path) if record[1] == "blob"]
        if len(blobs) != 1:
            return None
        return ProjectedEntry(
            path="",
            mode=blobs[0][0],
            content=self.blob(blobs[0][2], code),
        )

    def tree_entries(self, rev: str, root: str, code: str) -> list[ProjectedEntry]:
        prefix = root.rstrip("/") + "/"
        entries: list[ProjectedEntry] = []
        for mode, otype, object_id, full in self._ls_tree(rev, root):
            _need(
                otype == "blob",
                "unsupported_special_file",
                f"{root}: non-blob Git entry {full!r}",
            )
            logical = full[len(prefix):] if full.startswith(prefix) else full
            entries.append(
                ProjectedEntry(
                    path=logical,
                    mode=mode,
                    content=self.blob(object_id, code),
                )
            )
        return entries

    def _ls_tree(self, rev: str, path: str) -> list[tuple[str, str, str, str]]:
        proc = self._run("ls-tree", "-r", "-z", rev, "--", path)
        if proc.returncode != 0:
            return []
        records: list[tuple[str, str, str, str]] = []
        for raw in proc.stdout.split(b"\0"):
            if not raw:
                continue
            meta, _, full = raw.partition(b"\t")
            parts = meta.split(b" ")
            if len(parts) < 3:
                continue
            records.append(
                (
                    parts[0].decode("ascii"),
                    parts[1].decode("ascii"),
                    parts[2].decode("ascii"),
                    full.decode("utf-8", "replace"),
                )
            )
        return records

    def index_file_entry(self, path: str) -> ProjectedEntry | None:
        records = self._index_records(path)
        if len(records) != 1:
            return None
        return ProjectedEntry(
            path="",
            mode=records[0][0],
            content=self.blob(records[0][1], "adopter_snapshot_unavailable"),
        )

    def index_tree_entries(self, root: str) -> list[ProjectedEntry]:
        prefix = root.rstrip("/") + "/"
        entries: list[ProjectedEntry] = []
        for mode, object_id, full in self._index_records(root):
            logical = full[len(prefix):] if full.startswith(prefix) else full
            entries.append(
                ProjectedEntry(
                    path=logical,
                    mode=mode,
                    content=self.blob(object_id, "adopter_snapshot_unavailable"),
                )
            )
        return entries

    def _index_records(self, path: str) -> list[tuple[str, str, str]]:
        proc = self._run("ls-files", "-s", "-z", "--", path)
        if proc.returncode != 0:
            return []
        records: list[tuple[str, str, str]] = []
        for raw in proc.stdout.split(b"\0"):
            if not raw:
                continue
            meta, _, full = raw.partition(b"\t")
            parts = meta.split(b" ")
            if len(parts) < 3:
                continue
            _need(
                parts[2] == b"0",
                "adopter_snapshot_unavailable",
                f"unmerged index entry for {path}",
            )
            records.append(
                (
                    parts[0].decode("ascii"),
                    parts[1].decode("ascii"),
                    full.decode("utf-8", "replace"),
                )
            )
        return records


class _Snapshot(Protocol):
    """One explicit adopter content source: a commit tree or the staged index."""

    def file_entry(self, path: str) -> ProjectedEntry | None: ...

    def tree_entries(self, root: str) -> list[ProjectedEntry]: ...


class _RevisionSnapshot:
    """Adopter snapshot read from the tree of one explicit commit (never the worktree)."""

    def __init__(self, repo: _GitRepo, revision: str) -> None:
        self.repo = repo
        self.revision = revision

    def file_entry(self, path: str) -> ProjectedEntry | None:
        return self.repo.file_entry(self.revision, path, "adopter_snapshot_unavailable")

    def tree_entries(self, root: str) -> list[ProjectedEntry]:
        return self.repo.tree_entries(
            self.revision, root, "adopter_snapshot_unavailable"
        )


class _IndexSnapshot:
    """Adopter snapshot read from the staged Git index only (never the worktree)."""

    def __init__(self, repo: _GitRepo) -> None:
        self.repo = repo

    def file_entry(self, path: str) -> ProjectedEntry | None:
        return self.repo.index_file_entry(path)

    def tree_entries(self, root: str) -> list[ProjectedEntry]:
        return self.repo.index_tree_entries(root)


def _adopter_repo(declaration: str) -> _GitRepo:
    repo = _GitRepo(os.path.dirname(os.path.abspath(declaration)) or os.getcwd())
    top = repo.toplevel()
    return _GitRepo(top) if top else repo


def _resolve_adopter_repo(args: argparse.Namespace) -> _GitRepo:
    explicit = getattr(args, "adopter_repo", None)
    if explicit:
        return _GitRepo(str(explicit))
    return _adopter_repo(str(args.declaration))


def _resolve_catalog_path(catalog: str, upstream_repo: str) -> str:
    if os.path.isabs(catalog) or os.path.exists(catalog):
        return catalog
    candidate = os.path.join(upstream_repo, catalog)
    return candidate if os.path.exists(candidate) else catalog


def _trusted_revision(upstream: _GitRepo, diagnostic: str | None) -> tuple[str, bool]:
    if diagnostic:
        target = upstream.resolve(diagnostic)
        _need(
            target is not None,
            "baseline_unavailable",
            f"diagnostic revision not resolvable: {diagnostic}",
        )
        return str(target), True
    for ref in ("refs/remotes/origin/main", "refs/heads/main"):
        target = upstream.resolve(ref)
        if target:
            return target, False
    _fail(
        "baseline_unavailable",
        "no protected default branch (refs/remotes/origin/main or refs/heads/main)",
    )


def _snapshot_for(args: argparse.Namespace, adopter: _GitRepo) -> _Snapshot:
    _need(
        args.adopter_revision is not None or args.adopter_index,
        "adopter_snapshot_unavailable",
        "exactly one of --adopter-revision or --adopter-index is required",
    )
    if args.adopter_index:
        return _IndexSnapshot(adopter)
    revision = adopter.resolve(str(args.adopter_revision))
    _need(
        revision is not None,
        "adopter_snapshot_unavailable",
        f"adopter revision not resolvable: {args.adopter_revision}",
    )
    return _RevisionSnapshot(adopter, str(revision))


def _member_digest_at(repo: _GitRepo, commit: str, source: str, projection: str) -> str:
    if _content_projection(projection) == "tree":
        return member_digest(repo.tree_entries(commit, source, "baseline_unavailable"))
    entry = repo.file_entry(commit, source, "baseline_unavailable")
    return member_digest([entry] if entry is not None else [])


def _unit_upstream_digest(
    repo: _GitRepo, commit: str, catalog_unit: Mapping[str, object]
) -> str:
    if catalog_unit.get("sync_projection") == "assertions":
        return assertion_list_digest(catalog_unit.get("assertions", []))
    projection = str(catalog_unit.get("sync_projection"))
    members = list(catalog_unit.get("members", []) or [])
    pairs = [
        (
            str(m.get("id")),
            _member_digest_at(repo, commit, str(m.get("source")), projection),
        )
        for m in members
    ]
    return unit_digest(pairs)


def _snapshot_member_digest(
    snapshot: _Snapshot, destination: str, projection: str
) -> str:
    if _content_projection(projection) == "tree":
        return member_digest(snapshot.tree_entries(destination))
    entry = snapshot.file_entry(destination)
    return member_digest([entry] if entry is not None else [])


def _destination_changed(
    decl_unit: Mapping[str, object],
    lock_row: Mapping[str, object],
    snapshot: _Snapshot,
    projection: str,
) -> bool:
    if decl_unit.get("mode") == "replacement":
        expected = {
            str(m.get("id")): m.get("accepted_destination_digest")
            for m in lock_row.get("replacement_members", [])
        }
        for member in decl_unit.get("replacement_members", []):
            digest = _snapshot_member_digest(
                snapshot,
                str(member.get("destination")),
                str(member.get("projection")),
            )
            if digest != expected.get(str(member.get("id"))):
                return True
        return False
    expected = {
        str(m.get("id")): m.get("accepted_destination_digest")
        for m in lock_row.get("members", [])
    }
    for member in decl_unit.get("members", []):
        digest = _snapshot_member_digest(
            snapshot, str(member.get("destination")), projection
        )
        if digest != expected.get(str(member.get("id"))):
            return True
    return False


def _strip_comments(text: str) -> str:
    lines = [
        line
        for line in text.splitlines()
        if not line.strip().startswith(("//", "#"))
    ]
    return "\n".join(lines)


def _fragment(snapshot: _Snapshot, destination: str) -> str:
    entry = snapshot.file_entry(destination)
    return entry.content.decode("utf-8", "replace") if entry is not None else ""


def _content_projection(projection: str) -> str:
    """Normalize guarded files to ordinary file digest framing."""
    return "file" if projection == "guarded_file" else projection


_ADOPTER_ROOT_FORBIDDEN_REFERENCES = (
    "aicore",
    "ai-core",
    "migrate-core-to-project",
    "sync-aicore-adoption",
    ".aicore/",
    "upstream provenance",
    "upstream lineage",
    "reuse guide",
)
_ADOPTER_ROOT_REQUIRED_MARKERS = (
    (
        "Project identity",
        re.compile(r"^> \*\*Project identity:\*\* \S.*$", re.MULTILINE),
    ),
    (
        "Spec version",
        re.compile(r"^> \*\*Spec version:\*\* \d+\.\d+\.\d+\s*$", re.MULTILINE),
    ),
    (
        "Local version",
        re.compile(r"^> \*\*Local version:\*\* \d+\.\d+\.\d+\s*$", re.MULTILINE),
    ),
)


def _adopter_root_policy_violation(content: bytes) -> str | None:
    """Return the first adopter-root policy violation, or ``None`` when valid."""
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return "mapped root must be UTF-8 text"
    folded = text.casefold()
    for forbidden in _ADOPTER_ROOT_FORBIDDEN_REFERENCES:
        if forbidden in folded:
            return f"mapped root contains prohibited reference {forbidden!r}"
    for marker, pattern in _ADOPTER_ROOT_REQUIRED_MARKERS:
        if pattern.search(text) is None:
            return f"mapped root is missing required {marker!r} marker"
    return None


def _destination_policy_violation(
    uid: str,
    catalog_unit: Mapping[str, object],
    decl_unit: Mapping[str, object],
    snapshot: _Snapshot,
) -> str | None:
    """Evaluate a catalog unit's closed destination policy against its snapshot.

    The adopter's ``opencode.jsonc`` — the destination of the catalog's
    ``opencode-config`` assertions unit — is evaluated first: every
    ``agent.*.permission.bash`` allow is classified under the runner policy.
    The guarded root-runtime identity policy then runs unchanged for
    ``guarded_file`` units.
    """
    destination = str(catalog_unit.get("destination") or "")
    if _is_opencode_config_destination(destination):
        entry = snapshot.file_entry(destination)
        if entry is None:
            # A missing config stays governed by the unit's assertions.
            return None
        return _opencode_config_policy_violation(entry.content)
    if catalog_unit.get("sync_projection") != "guarded_file":
        return None
    policy = str(catalog_unit.get("destination_policy"))
    _need(
        policy in DESTINATION_POLICIES,
        "invalid_mapping",
        f"{uid}: unsupported destination policy {policy!r}",
    )
    if decl_unit.get("mode") == "replacement":
        replacements = list(decl_unit.get("replacement_members", []) or [])
        if len(replacements) != 1 or _content_projection(
            str(replacements[0].get("projection"))
        ) != "file":
            return "guarded root replacement must map exactly one file"
        destination = str(replacements[0].get("destination"))
    else:
        declared = _declared_members(catalog_unit, decl_unit, uid)
        members = list(catalog_unit.get("members", []) or [])
        if len(members) != 1:
            return "guarded root must declare exactly one catalog member"
        destination = declared[str(members[0].get("id"))]
    entry = snapshot.file_entry(destination)
    content = entry.content if entry is not None else b""
    return _adopter_root_policy_violation(content)


AICORE_SUITE_COMMAND = "uv run --frozen --group dev pytest -q"


def _runner_policy_violation(grant: object) -> str | None:
    """Return the runner-grant policy violation, or ``None`` when reviewed.

    Accepts the reviewed AICore suite command by exact literal comparison
    (no whitespace normalisation) and the bounded package test scripts
    ``pnpm test``, ``npm test``, ``yarn test``, and ``cargo test``. Every
    other payload — another ``uv run`` payload, an appended test path, a
    wildcard, reordered tokens, interior double-spaces, or a broad
    catch-all allow — is rejected with a reason naming why.
    """
    if not isinstance(grant, str):
        return "runner grant must be a string"
    if grant == AICORE_SUITE_COMMAND:
        return None
    bounded_runners = ("pnpm test", "npm test", "yarn test", "cargo test")
    if grant in bounded_runners:
        return None
    return "runner grant is not a reviewed test-runner command"


OPENCODE_CONFIG_BASENAME = "opencode.jsonc"
_PACKAGE_TEST_SCRIPT_HEADS = frozenset(
    {("pnpm", "test"), ("npm", "test"), ("yarn", "test"), ("cargo", "test")}
)
_INTERPRETER_RUNNER_HEADS = frozenset(
    {
        # shells
        "bash",
        "sh",
        "zsh",
        "dash",
        "fish",
        "csh",
        "ksh",
        # language interpreters
        "python",
        "python2",
        "python3",
        "node",
        "deno",
        "bun",
        "ruby",
        "perl",
        "php",
        "lua",
        "java",
        "go",
        # package, test, and tool runners
        "uv",
        "uvx",
        "uv run",
        "uv tool run",
        "pytest",
        "py.test",
        "npm",
        "pnpm",
        "yarn",
        "npx",
        "npm exec",
        "pnpm dlx",
        "yarn dlx",
        "cargo",
        "rustc",
        "docker",
        "podman",
        "git",
        "gh",
    }
)


def _is_opencode_config_destination(destination: str) -> bool:
    """Return whether a catalog destination names the adopter's opencode config."""
    return (
        _normalize_destination(destination).rsplit("/", 1)[-1]
        == OPENCODE_CONFIG_BASENAME
    )


def _catch_all_policy_violation(pattern: str) -> str | None:
    """Return the catch-all violation for an allow pattern, or ``None``.

    Rule 2 of the runner policy: ``*``, ``**``, and any trailing-``*``
    pattern whose head is a bare interpreter/runner invocation (``uv *``,
    ``pytest *``, ``bash *``, ``uv run *``) grants a whole interpreter or
    runner and is rejected outright. A trailing ``*`` under a concrete
    subcommand head (``pnpm install *``) stays scoped and is not a
    catch-all.
    """
    if pattern.strip() in ("*", "**"):
        return f"allow {pattern!r} grants every command"
    if pattern.endswith("*"):
        head = pattern[:-1].rstrip()
        if head in _INTERPRETER_RUNNER_HEADS:
            return f"allow {pattern!r} grants a whole interpreter/runner"
    return None


def _is_test_runner_pattern(pattern: str) -> bool:
    """Return whether an allow pattern names a pytest or package-test command.

    Test-runner commands are anything containing ``pytest`` (any payload,
    any ordering) or a package test script — ``pnpm test``, ``npm test``,
    ``yarn test``, ``cargo test`` — with or without appended arguments.
    Every identified pattern must then satisfy ``_runner_policy_violation``.
    """
    if "pytest" in pattern.casefold():
        return True
    return tuple(pattern.split()[:2]) in _PACKAGE_TEST_SCRIPT_HEADS


def _bash_grant_policy_violation(where: str, bash: object) -> str | None:
    """Classify one agent's ``permission.bash`` grants under the runner policy.

    Rule 1: only ``allow`` entries are examined — a ``deny`` entry (including
    the deny-first ``"*": "deny"`` catch-all) and an ``ask`` entry are never
    judged. Rule 2: a broad catch-all allow is rejected outright. Rule 3: an
    identified test-runner allow must satisfy ``_runner_policy_violation`` —
    exactly ``AICORE_SUITE_COMMAND`` or a bounded package test script — any
    other payload is rejected. Rule 4: an allow that is neither a catch-all
    nor a test runner (``pnpm install``) is skipped. An absent test-runner
    allow is not a violation by itself. A blanket string ``"allow"`` is the
    mapping catch-all ``"*": "allow"`` and is rejected with it.
    """
    if isinstance(bash, str):
        if bash == "allow":
            return f"{where}: blanket string 'allow' grants every command"
        return None
    if not isinstance(bash, Mapping):
        return None
    for pattern, action in bash.items():
        if not isinstance(pattern, str) or not isinstance(action, str):
            continue
        if action != "allow":
            continue
        catch_all = _catch_all_policy_violation(pattern)
        if catch_all is not None:
            return f"{where}: {catch_all}"
        if _is_test_runner_pattern(pattern):
            reason = _runner_policy_violation(pattern)
            if reason is not None:
                return f"{where}: test-runner allow {pattern!r}: {reason}"
    return None


def _opencode_config_policy_violation(content: bytes) -> str | None:
    """Return the first runner-allow violation in the adopter opencode config.

    Reuses the guarded-config comment stripper and the existing JSON loader:
    the bytes are decoded as UTF-8, ``//``/``#`` comment lines are stripped,
    the document is parsed as JSON, and every ``agent.*.permission.bash``
    block is classified. Content that is not UTF-8, not a JSONC object, or
    that carries no ``agent.*.permission.bash`` block yields ``None`` — the
    catalog assertions keep governing those states exactly as before, and
    the top-level ``permission.bash`` block is out of scope.
    """
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        return None
    try:
        document = json.loads(_strip_comments(text))
    except json.JSONDecodeError:
        return None
    if not isinstance(document, dict):
        return None
    agents = document.get("agent")
    if not isinstance(agents, Mapping):
        return None
    for name, agent in agents.items():
        if not isinstance(agent, Mapping):
            continue
        permission = agent.get("permission")
        if not isinstance(permission, Mapping):
            continue
        violation = _bash_grant_policy_violation(
            f"agent {str(name)!r} permission.bash", permission.get("bash")
        )
        if violation is not None:
            return violation
    return None


def _assertion_deltas(
    catalog_unit: Mapping[str, object],
    lock_row: Mapping[str, object],
    snapshot: _Snapshot,
    accepted_assertions: Sequence[object],
) -> tuple[bool, bool]:
    accepted_list = assertion_list_digest(accepted_assertions)
    upstream_changed = (
        assertion_list_digest(catalog_unit.get("assertions", [])) != accepted_list
    )
    stripped = _strip_comments(_fragment(snapshot, str(catalog_unit.get("destination"))))
    status = [
        (str(a.get("id")), str(a.get("contains")) in stripped)
        for a in catalog_unit.get("assertions", [])
    ]
    lock_member = next(iter(lock_row.get("members", [])), {})
    destination_changed = assertion_status_digest(status) != lock_member.get(
        "accepted_destination_digest"
    )
    return upstream_changed, destination_changed


def _disposition(mode: str, upstream_changed: bool, destination_changed: bool) -> str:
    if mode == "not_applicable":
        return "not_applicable"
    if mode == "destination_owned":
        return "review_required" if upstream_changed else "unmanaged"
    if mode == "replacement":
        if upstream_changed:
            return "review_required"
        return "local_drift" if destination_changed else "current"
    if mode == "adapted":
        if upstream_changed and destination_changed:
            return "review_required"
        if upstream_changed:
            return "update_available"
        return "local_drift" if destination_changed else "current"
    if upstream_changed and destination_changed:
        return "conflict"
    if upstream_changed:
        return "update_available"
    return "local_drift" if destination_changed else "current"


def _validate_declaration_coverage(
    catalog: Mapping[str, object],
    declaration: Mapping[str, object],
    profile: Mapping[str, object],
) -> tuple[dict, dict]:
    catalog_units = {str(u.get("id")): u for u in catalog.get("units", [])}
    declaration_units = {str(u.get("id")): u for u in declaration.get("units", [])}
    missing = sorted(uid for uid in catalog_units if uid not in declaration_units)
    _need(
        not missing,
        "declaration_incomplete",
        f"catalog units missing from declaration: {missing}",
    )
    unknown = sorted(uid for uid in declaration_units if uid not in catalog_units)
    _need(
        not unknown,
        "invalid_declaration",
        f"declaration references unknown catalog units: {unknown}",
    )
    for uid, unit in catalog_units.items():
        mode = str(declaration_units[uid].get("mode"))
        applicable = evaluate_applicability(unit, profile)
        _need(
            not (applicable and mode == "not_applicable"),
            "invalid_applicability",
            f"{uid}: applicable unit declared not_applicable",
        )
        _need(
            not ((not applicable) and mode != "not_applicable"),
            "invalid_applicability",
            f"{uid}: inapplicable unit must be not_applicable",
        )
    return catalog_units, declaration_units


def _validate_coverage(
    catalog: Mapping[str, object],
    declaration: Mapping[str, object],
    lock: Mapping[str, object],
    profile: Mapping[str, object],
) -> tuple[dict, dict, dict]:
    catalog_units, declaration_units = _validate_declaration_coverage(
        catalog, declaration, profile
    )
    lock_units = {str(u.get("id")): u for u in lock.get("units", [])}
    missing_lock = sorted(uid for uid in catalog_units if uid not in lock_units)
    _need(
        not missing_lock,
        "invalid_lock",
        f"lock is missing catalog units: {missing_lock}",
    )
    for uid in catalog_units:
        mode = str(declaration_units[uid].get("mode"))
        _need(
            lock_units[uid].get("mode") == mode,
            "invalid_lock",
            f"{uid}: lock mode does not match the declaration",
        )
    return catalog_units, declaration_units, lock_units


def _repo_relative_path(repo: _GitRepo, path: str) -> str:
    top = repo.toplevel()
    absolute = os.path.abspath(path)
    if top and absolute.startswith(os.path.abspath(top) + os.sep):
        return os.path.relpath(absolute, os.path.abspath(top))
    return path


def _catalog_blob_at(upstream: _GitRepo, commit: str, catalog_path: str) -> bytes:
    relative = _repo_relative_path(upstream, catalog_path)
    blob = upstream.show_blob(commit, relative)
    if blob is None:
        _fail("catalog_changed", f"cannot read catalog at {commit}:{relative}")
    return blob


def _catalog_digest_at(upstream: _GitRepo, commit: str, catalog_path: str) -> str:
    return _sha256(_catalog_blob_at(upstream, commit, catalog_path))


def _catalog_assertions_at(
    upstream: _GitRepo, commit: str, catalog_path: str, uid: str
) -> list[object]:
    blob = _catalog_blob_at(upstream, commit, catalog_path)
    try:
        document = yaml.safe_load(blob.decode("utf-8", "replace"))
    except yaml.YAMLError as exc:
        _fail("catalog_changed", f"{uid}: cannot parse the catalog at {commit}: {exc}")
    units = document.get("units", []) if isinstance(document, Mapping) else []
    for unit in units if isinstance(units, list) else []:
        if isinstance(unit, Mapping) and str(unit.get("id")) == uid:
            assertions = unit.get("assertions", [])
            _need(
                isinstance(assertions, list),
                "catalog_changed",
                f"{uid}: accepted catalog assertions must be a list",
            )
            return list(assertions)
    _fail("catalog_changed", f"{uid}: unit is absent from the catalog at {commit}")


def _check_report(
    declaration_path: str,
    lock_path: str,
    review_path: str | None,
    catalog_path: str,
    upstream: _GitRepo,
    target: str,
    diagnostic: bool,
    snapshot_factory: Callable[[], _Snapshot],
) -> dict:
    """Build the compliance report shared by ``check`` and ``verify-all``."""
    declaration = load_declaration(declaration_path)
    lock = load_lock(lock_path)
    review = (
        load_review(review_path)
        if review_path
        else {"schema_version": 2, "decisions": []}
    )
    catalog = load_catalog(catalog_path)
    accepted = str(lock.get("accepted_source_commit"))
    _need(
        upstream.is_ancestor(accepted, target),
        "baseline_unavailable",
        f"accepted commit {accepted} is not an ancestor of {target}",
    )
    declaration_bytes_digest = _raw_file_digest(declaration_path)
    _need(
        lock.get("declaration_digest") == declaration_bytes_digest,
        "declaration_changed",
        f"{declaration_path}: declaration_digest does not match the declaration bytes",
    )
    expected_review_digest = (
        _raw_file_digest(review_path) if review_path else _sha256(b"")
    )
    _need(
        lock.get("review_digest") == expected_review_digest,
        "review_changed",
        f"{review_path or '<no review>'}: review_digest does not match the review bytes",
    )
    _need(
        lock.get("accepted_catalog_digest")
        == _catalog_digest_at(upstream, accepted, catalog_path),
        "catalog_changed",
        f"{catalog_path}: accepted_catalog_digest does not match the catalog at "
        f"{accepted}",
    )
    expected_snapshot_digest = _snapshot_digest(
        declaration_bytes_digest,
        expected_review_digest,
        lock.get("units", []),
    )
    _need(
        lock.get("accepted_snapshot_digest") == expected_snapshot_digest,
        "invalid_lock",
        "accepted_snapshot_digest does not reproduce from the lock rows, "
        "declaration_digest, and review_digest",
    )
    snapshot = snapshot_factory()
    catalog_units, declaration_units, lock_units = _validate_coverage(
        catalog, declaration, lock, declaration.get("profile", {})
    )
    decisions = {str(d.get("unit")): d for d in review.get("decisions", [])}
    results: list[dict[str, object]] = []
    collisions: list[str] = []
    blocking: list[str] = []
    for uid, catalog_unit in catalog_units.items():
        decl_unit = declaration_units[uid]
        mode = str(decl_unit.get("mode"))
        if mode == "not_applicable":
            results.append(
                {
                    "id": uid,
                    "mode": mode,
                    "upstream_delta": None,
                    "destination_delta": None,
                    "disposition": "not_applicable",
                }
            )
            continue
        projection = str(catalog_unit.get("sync_projection"))
        lock_row = lock_units[uid]
        policy_violation = _destination_policy_violation(
            uid, catalog_unit, decl_unit, snapshot
        )
        if projection == "assertions":
            accepted_assertions = _catalog_assertions_at(
                upstream, accepted, catalog_path, uid
            )
            _need(
                assertion_list_digest(accepted_assertions)
                == lock_row.get("accepted_upstream_digest"),
                "invalid_lock",
                f"{uid}: accepted assertion list digest does not reproduce at {accepted}",
            )
            upstream_changed, destination_changed = _assertion_deltas(
                catalog_unit, lock_row, snapshot, accepted_assertions
            )
        else:
            mapping = (
                decl_unit.get("replacement_members")
                if mode == "replacement"
                else decl_unit.get("members")
            )
            _need(
                mapping,
                "invalid_declaration",
                f"{uid}: {mode} requires an explicit member mapping",
            )
            accepted_digest = _unit_upstream_digest(upstream, accepted, catalog_unit)
            _need(
                accepted_digest == lock_row.get("accepted_upstream_digest"),
                "invalid_lock",
                f"{uid}: accepted upstream digest does not reproduce at {accepted}",
            )
            upstream_changed = (
                _unit_upstream_digest(upstream, target, catalog_unit) != accepted_digest
            )
            destination_changed = _destination_changed(
                decl_unit, lock_row, snapshot, projection
            )
        if (
            policy_violation is None
            and mode in _REVIEW_MODES
            and upstream_changed
            and uid not in decisions
        ):
            _fail(
                "review_changed",
                f"{uid}: upstream changed but the review has no decision for it",
            )
        disposition = (
            "policy_violation"
            if policy_violation is not None
            else _disposition(mode, upstream_changed, destination_changed)
        )
        if disposition == "current" and accepted != target:
            disposition = "baseline_advance_required"
        if mode != "replacement" and catalog_unit.get("kind") == STORY_UNIT_KIND:
            collisions.extend(
                _story_index_collisions(
                    uid, catalog_unit, decl_unit, upstream, target, snapshot
                )
            )
        results.append(
            {
                "id": uid,
                "mode": mode,
                "upstream_delta": "changed" if upstream_changed else "unchanged",
                "destination_delta": "changed" if destination_changed else "unchanged",
                "disposition": disposition,
            }
        )
        if disposition in _BLOCKING_DISPOSITIONS:
            blocking.append(f"{uid}: {disposition}")
    compliance = (not diagnostic) and not blocking
    return {
        "compliance": compliance,
        "accepted_revision": accepted,
        "required_revision": target,
        "diagnostic": diagnostic,
        "units": results,
        "collisions": collisions,
        "blocking_reasons": blocking,
    }


def run_check(args: argparse.Namespace) -> int:
    """Execute the read-only ``check`` command; return 0 or 1, or raise ``SyncError``."""
    _need(
        args.adopter_revision is not None or args.adopter_index,
        "adopter_snapshot_unavailable",
        "exactly one of --adopter-revision or --adopter-index is required",
    )
    for name, value, code in (
        ("--declaration", args.declaration, "invalid_declaration"),
        ("--lock", args.lock, "invalid_lock"),
    ):
        _need(value, code, f"{name} is required")
    catalog_path = _resolve_catalog_path(str(args.catalog), str(args.upstream_repo))
    upstream = _GitRepo(str(args.upstream_repo))
    target, diagnostic = _trusted_revision(upstream, args.diagnostic_revision)
    adopter = _resolve_adopter_repo(args)
    report = _check_report(
        str(args.declaration),
        str(args.lock),
        str(args.review) if args.review else None,
        catalog_path,
        upstream,
        target,
        diagnostic,
        lambda: _snapshot_for(args, adopter),
    )
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        _print_human(report)
    return 0 if report["compliance"] else 1


def _print_human(report: Mapping[str, object]) -> None:
    print(f"compliance: {str(report['compliance']).lower()}")
    print(f"accepted_revision: {report['accepted_revision']}")
    print(f"required_revision: {report['required_revision']}")
    if report["diagnostic"]:
        print("diagnostic: true (diagnostic runs can never be compliant)")
    for unit in report["units"]:
        delta = (
            f"upstream={unit['upstream_delta'] or 'n/a'} "
            f"destination={unit['destination_delta'] or 'n/a'}"
        )
        print(f"  {unit['id']} [{unit['mode']}] {delta} -> {unit['disposition']}")
    for collision in report.get("collisions") or []:
        print(collision)
    for reason in report["blocking_reasons"]:
        print(f"blocking: {reason}")


# ---------------------------------------------------------------------------
# propose-lock (protocol-v2 Sections 3, 4, 15): emit one candidate lock
# ---------------------------------------------------------------------------

_CONTROL_PATH_DEFAULTS = (
    ".git/**",
    ".aicore/adoption.yaml",
    ".aicore/adoption.lock.yaml",
    ".aicore/adoption-review.yaml",
)


def _control_paths(catalog: Mapping[str, object]) -> list[str]:
    block = catalog.get("catalog")
    declared = block.get("control_paths") if isinstance(block, Mapping) else None
    paths = list(_CONTROL_PATH_DEFAULTS)
    for path in declared if isinstance(declared, list) else []:
        if str(path) not in paths:
            paths.append(str(path))
    return paths


def _raw_file_digest(path: str) -> str:
    """IO helper: sha256 over the exact bytes of one input document."""
    with open(path, "rb") as handle:
        return _sha256(handle.read())


def _validate_destination(
    destination: object, where: str, control_paths: Sequence[str]
) -> str:
    _need(
        isinstance(destination, str) and bool(destination),
        "invalid_mapping",
        f"{where}: destination must be a non-empty string",
    )
    raw = str(destination).replace("\\", "/")
    _need(
        not raw.startswith("/"),
        "invalid_mapping",
        f"{where}: absolute destinations are forbidden: {raw}",
    )
    segments = [segment for segment in raw.split("/") if segment not in ("", ".")]
    _need(
        ".." not in segments,
        "invalid_mapping",
        f"{where}: parent traversal is forbidden: {raw}",
    )
    normalized = "/".join(segments)
    _need(
        bool(normalized),
        "invalid_mapping",
        f"{where}: destination resolves to an empty path",
    )
    for control in control_paths:
        prefix = control[:-3] if control.endswith("/**") else control
        _need(
            not (normalized == prefix or normalized.startswith(prefix + "/")),
            "invalid_mapping",
            f"{where}: destination is a protected control path: {raw}",
        )
    return normalized


def _check_destination_set(entries: Sequence[tuple[str, str, str]]) -> None:
    seen: dict[str, str] = {}
    for unit_id, member_id, destination in entries:
        owner = f"{unit_id}.{member_id}"
        _need(
            destination not in seen,
            "invalid_mapping",
            f"duplicate destination {destination} for {owner} and "
            f"{seen.get(destination)}",
        )
        seen[destination] = owner
    ordered = sorted(seen)
    for index, first in enumerate(ordered):
        for second in ordered[index + 1:]:
            _need(
                not second.startswith(first + "/"),
                "invalid_mapping",
                f"overlapping destinations: {first} and {second}",
            )


def _declared_members(
    catalog_unit: Mapping[str, object], decl_unit: Mapping[str, object], uid: str
) -> dict[str, str]:
    catalog_ids = [str(m.get("id")) for m in catalog_unit.get("members", [])]
    raw_members = list(decl_unit.get("members", []) or [])
    declared = {str(m.get("id")): str(m.get("destination")) for m in raw_members}
    _need(
        len(declared) == len(raw_members),
        "invalid_declaration",
        f"{uid}: duplicate declared member ids",
    )
    _need(
        set(declared) == set(catalog_ids),
        "invalid_declaration",
        f"{uid}: declaration must map every catalog member exactly once "
        f"(catalog={catalog_ids}, declared={sorted(declared)})",
    )
    return declared


def _member_row(
    uid: str,
    catalog_unit: Mapping[str, object],
    decl_unit: Mapping[str, object],
    mode: str,
    target_upstream: str,
    repo: _GitRepo,
    commit: str,
    snapshot: _Snapshot,
    control_paths: Sequence[str],
    destinations: list[tuple[str, str, str]],
) -> dict:
    projection = str(catalog_unit.get("sync_projection"))
    declared = _declared_members(catalog_unit, decl_unit, uid)
    members: list[dict[str, object]] = []
    for member in catalog_unit.get("members", []):
        member_id = str(member.get("id"))
        destination = declared[member_id]
        normalized = _validate_destination(
            destination, f"{uid}.{member_id}", control_paths
        )
        destinations.append((uid, member_id, normalized))
        upstream_member = _member_digest_at(
            repo, commit, str(member.get("source")), projection
        )
        destination_member = _snapshot_member_digest(snapshot, destination, projection)
        if mode == "mirror":
            _need(
                upstream_member == destination_member,
                "invalid_lock",
                f"{uid}.{member_id}: mirror member does not converge "
                f"({upstream_member} != {destination_member})",
            )
        members.append(
            {
                "id": member_id,
                "destination": destination,
                "accepted_upstream_digest": upstream_member,
                "accepted_destination_digest": destination_member,
            }
        )
    return {
        "id": uid,
        "mode": mode,
        "declaration_unit_digest": declaration_unit_digest(
            mode, decl_unit.get("members", []), []
        ),
        "accepted_upstream_digest": target_upstream,
        "members": members,
    }


def _replacement_row(
    uid: str,
    decl_unit: Mapping[str, object],
    target_upstream: str,
    snapshot: _Snapshot,
    control_paths: Sequence[str],
    destinations: list[tuple[str, str, str]],
) -> dict:
    members: list[dict[str, object]] = []
    for member in decl_unit.get("replacement_members", []):
        member_id = str(member.get("id"))
        destination = str(member.get("destination"))
        projection = str(member.get("projection"))
        normalized = _validate_destination(
            destination, f"{uid}.{member_id}", control_paths
        )
        destinations.append((uid, member_id, normalized))
        members.append(
            {
                "id": member_id,
                "destination": destination,
                "projection": projection,
                "accepted_destination_digest": _snapshot_member_digest(
                    snapshot, destination, projection
                ),
            }
        )
    return {
        "id": uid,
        "mode": "replacement",
        "declaration_unit_digest": declaration_unit_digest(
            "replacement", [], decl_unit.get("replacement_members", [])
        ),
        "accepted_upstream_digest": target_upstream,
        "replacement_members": members,
    }


def _assertion_row(
    uid: str,
    catalog_unit: Mapping[str, object],
    snapshot: _Snapshot,
    control_paths: Sequence[str],
    destinations: list[tuple[str, str, str]],
) -> dict:
    destination = str(catalog_unit.get("destination"))
    normalized = _validate_destination(destination, f"{uid}.assertions", control_paths)
    destinations.append((uid, "assertions", normalized))
    stripped = _strip_comments(_fragment(snapshot, destination))
    status: list[tuple[str, bool]] = []
    missing: list[str] = []
    for assertion in catalog_unit.get("assertions", []):
        assertion_id = str(assertion.get("id"))
        present = str(assertion.get("contains")) in stripped
        status.append((assertion_id, present))
        if not present:
            missing.append(assertion_id)
    _need(
        not missing,
        "local_drift",
        f"{uid}: required assertions absent from the adopter snapshot: {missing}",
    )
    list_digest = assertion_list_digest(catalog_unit.get("assertions", []))
    return {
        "id": uid,
        "mode": "mirror",
        "declaration_unit_digest": declaration_unit_digest("mirror", [], []),
        "accepted_upstream_digest": list_digest,
        "members": [
            {
                "id": "assertions",
                "destination": destination,
                "accepted_upstream_digest": list_digest,
                "accepted_destination_digest": assertion_status_digest(status),
            }
        ],
    }


def _snapshot_digest(
    declaration_digest: str, review_digest: str, rows: Sequence[Mapping[str, object]]
) -> str:
    chunks = [
        b"declaration:" + declaration_digest.encode("ascii") + b"\n",
        b"review:" + review_digest.encode("ascii") + b"\n",
    ]
    for row in rows:
        if str(row.get("mode")) == "not_applicable":
            continue
        members = (
            row.get("members")
            if row.get("members") is not None
            else row.get("replacement_members", [])
        )
        for member in members or []:
            chunks.append(
                b"snapshot\nunit:" + str(row.get("id")).encode("utf-8")
                + b"\nmember:" + str(member.get("id")).encode("utf-8")
                + b"\ndigest:"
                + str(member.get("accepted_destination_digest")).encode("ascii")
                + b"\n"
            )
    return _sha256(b"".join(chunks))


def _propose_lock_document(args: argparse.Namespace, snapshot: _Snapshot) -> dict:
    """Build one candidate v2 lock document; print nothing and write nothing.

    Shared builder behind ``propose-lock``, which emits the document to
    stdout only, and ``apply``, which writes it to the adopter lock file.
    Every input is read from ``args``; the caller supplies the explicit
    adopter snapshot. Portable story collisions (Section 17) are diagnostics
    and stay on stderr, so every caller's stdout contract remains intact.
    """
    catalog_path = _resolve_catalog_path(str(args.catalog), str(args.upstream_repo))
    declaration = load_declaration(str(args.declaration))
    review = (
        load_review(str(args.review))
        if args.review
        else {"schema_version": 2, "decisions": []}
    )
    catalog = load_catalog(catalog_path)
    block = catalog.get("catalog")
    _need(
        isinstance(block, Mapping)
        and block.get("upstream_repository") == declaration.get("upstream_repository"),
        "repository_identity_mismatch",
        "catalog and declaration upstream_repository differ",
    )
    upstream = _GitRepo(str(args.upstream_repo))
    target, _diagnostic = _trusted_revision(upstream, None)
    catalog_units, declaration_units = _validate_declaration_coverage(
        catalog, declaration, declaration.get("profile", {})
    )
    decisions = {str(d.get("unit")) for d in review.get("decisions", [])}
    baseline_lock = (
        load_lock(str(args.lock))
        if args.lock and os.path.isfile(str(args.lock))
        else None
    )
    if baseline_lock is not None:
        _need(
            baseline_lock.get("upstream_repository")
            in (None, declaration.get("upstream_repository")),
            "repository_identity_mismatch",
            "baseline lock upstream_repository differs from the declaration",
        )
    baseline = {
        str(row.get("id")): row
        for row in (baseline_lock or {}).get("units", [])
    }
    control_paths = _control_paths(catalog)
    destinations: list[tuple[str, str, str]] = []
    rows: list[dict[str, object]] = []
    for uid, catalog_unit in catalog_units.items():
        decl_unit = declaration_units[uid]
        mode = str(decl_unit.get("mode"))
        projection = str(catalog_unit.get("sync_projection"))
        if mode == "not_applicable":
            rows.append({"id": uid, "mode": "not_applicable"})
            continue
        policy_violation = _destination_policy_violation(
            uid, catalog_unit, decl_unit, snapshot
        )
        if policy_violation is not None:
            _fail("policy_violation", f"{uid}: {policy_violation}")
        if projection == "assertions":
            _need(
                not decl_unit.get("members"),
                "invalid_declaration",
                f"{uid}: assertion units must not declare members",
            )
            rows.append(
                _assertion_row(uid, catalog_unit, snapshot, control_paths, destinations)
            )
            continue
        target_upstream = _unit_upstream_digest(upstream, target, catalog_unit)
        if mode in _REVIEW_MODES:
            baseline_row = baseline.get(uid)
            if (
                baseline_row is not None
                and target_upstream != baseline_row.get("accepted_upstream_digest")
                and uid not in decisions
            ):
                _fail(
                    "review_changed",
                    f"{uid}: upstream changed at {target} but the review has no decision",
                )
        if mode == "replacement":
            _need(
                not decl_unit.get("members"),
                "invalid_declaration",
                f"{uid}: replacement must not declare members",
            )
            rows.append(
                _replacement_row(
                    uid,
                    decl_unit,
                    target_upstream,
                    snapshot,
                    control_paths,
                    destinations,
                )
            )
        else:
            rows.append(
                _member_row(
                    uid,
                    catalog_unit,
                    decl_unit,
                    mode,
                    target_upstream,
                    upstream,
                    target,
                    snapshot,
                    control_paths,
                    destinations,
                )
            )
        if mode != "replacement" and catalog_unit.get("kind") == STORY_UNIT_KIND:
            for collision in _story_index_collisions(
                uid, catalog_unit, decl_unit, upstream, target, snapshot
            ):
                print(collision, file=sys.stderr)
    _check_destination_set(destinations)
    declaration_digest = _raw_file_digest(str(args.declaration))
    review_digest = (
        _raw_file_digest(str(args.review))
        if args.review and os.path.isfile(str(args.review))
        else _sha256(b"")
    )
    return {
        "schema_version": 2,
        "upstream_repository": declaration.get("upstream_repository"),
        "accepted_source_commit": target,
        "accepted_catalog_digest": _catalog_digest_at(upstream, target, catalog_path),
        "declaration_digest": declaration_digest,
        "review_digest": review_digest,
        "accepted_snapshot_digest": _snapshot_digest(
            declaration_digest, review_digest, rows
        ),
        "units": rows,
    }


def run_propose(args: argparse.Namespace) -> int:
    """Build one candidate v2 lock at the trusted revision; emit YAML to stdout only."""
    _need(
        args.adopter_revision is not None or args.adopter_index,
        "adopter_snapshot_unavailable",
        "exactly one of --adopter-revision or --adopter-index is required",
    )
    for name, value, code in (
        ("--declaration", args.declaration, "invalid_declaration"),
        ("--catalog", args.catalog, "invalid_mapping"),
    ):
        _need(value, code, f"{name} is required")
    lock = _propose_lock_document(
        args, _snapshot_for(args, _resolve_adopter_repo(args))
    )
    text = yaml.safe_dump(lock, sort_keys=False, default_flow_style=False)
    sys.stdout.write(text.rstrip("\n") + "\n")
    return 0


# ---------------------------------------------------------------------------
# verify-all (protocol-v2 Section 16): aggregate registry compliance
# ---------------------------------------------------------------------------


def load_registry(path: str) -> dict:
    """Parse and shape-validate a schema-v2 adopter registry."""
    document = _read_document(path, "invalid_declaration")
    _require_v2(document, path, "invalid_declaration")
    _fields(document, path, "invalid_declaration", "upstream_repository")
    adopters = document.get("adopters")
    _need(
        isinstance(adopters, list),
        "invalid_declaration",
        f"{path}: adopters must be a list",
    )
    seen: set[str] = set()
    for index, adopter in enumerate(adopters):
        where = f"{path}: adopters[{index}]"
        _fields(
            adopter,
            where,
            "invalid_declaration",
            "id",
            "repository",
            "default_branch",
            "declaration_path",
            "lock_path",
            "review_path",
        )
        adopter_id = str(adopter.get("id"))
        _need(
            adopter_id not in seen,
            "invalid_declaration",
            f"{where}.id duplicated: {adopter_id}",
        )
        seen.add(adopter_id)
    return document


def _git_clone(repository: str, destination: str, branch: str) -> str | None:
    """IO helper: shallow read-only ``gh repo clone``; returns None or an error message."""
    command = [
        "gh",
        "repo",
        "clone",
        repository,
        destination,
        "--",
        "--branch",
        branch,
        "--depth",
        "1",
    ]
    try:
        proc = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        return "gh is not available"
    if proc.returncode != 0:
        lines = proc.stderr.decode("utf-8", "replace").strip().splitlines()
        return lines[-1] if lines else f"gh exited {proc.returncode}"
    return None


def _summarize_dispositions(units: Sequence[Mapping[str, object]]) -> str:
    interesting = [
        f"{u.get('id')}:{u.get('disposition')}"
        for u in units
        if str(u.get("disposition")) not in ("current", "not_applicable")
    ]
    return ", ".join(interesting) if interesting else "all current"


def _verify_adopter(
    entry: Mapping[str, object],
    checkouts_root: str | None,
    catalog_path: str,
    upstream: _GitRepo,
    target: str,
    temp_dirs: list[str],
) -> dict:
    adopter_id = str(entry.get("id"))
    result: dict[str, object] = {
        "id": adopter_id,
        "repository": str(entry.get("repository")),
        "checked_commit": "",
        "compliance": False,
        "disposition_summary": "",
        "error": "",
    }
    checkout: str | None = None
    if checkouts_root:
        candidate = os.path.join(str(checkouts_root), adopter_id)
        if os.path.isdir(candidate):
            checkout = candidate
    if checkout is None:
        checkout = tempfile.mkdtemp(prefix=f"aicore-verify-{adopter_id}-")
        temp_dirs.append(checkout)
        failure = _git_clone(
            str(entry.get("repository")),
            checkout,
            str(entry.get("default_branch")),
        )
        if failure is not None:
            result["error"] = f"repository_unavailable: {failure}"
            return result
    repo = _GitRepo(checkout)
    head = repo.resolve("HEAD")
    if head is None:
        result["error"] = "adopter_snapshot_unavailable: checkout HEAD is not a commit"
        return result
    result["checked_commit"] = head
    declaration_path = os.path.join(checkout, str(entry.get("declaration_path")))
    lock_path = os.path.join(checkout, str(entry.get("lock_path")))
    review_path = os.path.join(checkout, str(entry.get("review_path")))
    try:
        report = _check_report(
            declaration_path,
            lock_path,
            review_path,
            catalog_path,
            upstream,
            target,
            False,
            lambda: _RevisionSnapshot(repo, head),
        )
    except SyncError as exc:
        result["error"] = f"{exc.code}: {exc.message}"
        return result
    result["compliance"] = bool(report.get("compliance"))
    result["disposition_summary"] = _summarize_dispositions(report.get("units", []))
    return result


def _print_verify_human(report: Mapping[str, object]) -> None:
    print(f"compliance: {str(report['compliance']).lower()}")
    for adopter in report["adopters"]:
        status = "pass" if adopter["compliance"] else "fail"
        detail = adopter["error"] or adopter["disposition_summary"]
        commit = adopter["checked_commit"] or "unresolved"
        print(
            f"  {adopter['id']} [{status}] {adopter['repository']} @ {commit} {detail}"
        )
    for reason in report["blocking_reasons"]:
        print(f"blocking: {reason}")


def run_verify(args: argparse.Namespace) -> int:
    """Verify every registered adopter; return 0 only when every adopter passes."""
    catalog_path = _resolve_catalog_path(str(args.catalog), str(args.upstream_repo))
    registry_path = (
        str(args.registry)
        if args.registry
        else os.path.join(str(args.upstream_repo), ".aicore/adopters.yaml")
    )
    registry = load_registry(registry_path)
    catalog = load_catalog(catalog_path)
    block = catalog.get("catalog")
    _need(
        isinstance(block, Mapping)
        and block.get("upstream_repository") == registry.get("upstream_repository"),
        "repository_identity_mismatch",
        "catalog and registry upstream_repository differ",
    )
    upstream = _GitRepo(str(args.upstream_repo))
    target, _diagnostic = _trusted_revision(upstream, None)
    results: list[dict[str, object]] = []
    blocking: list[str] = []
    temp_dirs: list[str] = []
    try:
        for entry in registry.get("adopters", []):
            result = _verify_adopter(
                entry,
                args.checkouts_root,
                catalog_path,
                upstream,
                target,
                temp_dirs,
            )
            results.append(result)
            if not result["compliance"]:
                detail = result["error"] or (
                    "non-compliant (" + str(result["disposition_summary"]) + ")"
                )
                blocking.append(f"{result['id']}: {detail}")
    finally:
        for temp in temp_dirs:
            try:
                shutil.rmtree(temp)
            except OSError as exc:
                print(f"sync-aicore-adoption: temp cleanup failed for {temp}: {exc}", file=sys.stderr)
    compliance = not blocking
    report = {
        "compliance": compliance,
        "adopters": results,
        "blocking_reasons": blocking,
    }
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        _print_verify_human(report)
    return 0 if compliance else 1


# ---------------------------------------------------------------------------
# apply (protocol-v2 Sections 11, 18): classification, refusal, write path
# ---------------------------------------------------------------------------

ApplyClassification = Literal["writable", "refused", "skipped", "no_action"]


@dataclass(frozen=True)
class ApplyContext:
    """Read-only inputs shared by one ``apply`` classification run."""

    upstream: _GitRepo
    target: str
    accepted: str
    snapshot: _Snapshot
    catalog_path: str


class ApplyUnitState(TypedDict):
    """Observed state of one declared unit at the trusted target revision."""

    id: str
    mode: str
    install_strategy: str
    disposition: str
    upstream_changed: bool
    policy_violation: str | None
    core_wins_members: tuple[str, ...]


class ApplyUnitDecision(TypedDict):
    """One unit's classification under the bounded ``apply`` write-set rule."""

    id: str
    mode: str
    install_strategy: str
    disposition: str
    classification: ApplyClassification
    refusal_code: str | None
    reason: str
    core_wins_members: tuple[str, ...]


def _apply_decision(
    state: ApplyUnitState,
    classification: ApplyClassification,
    refusal_code: str | None,
    reason: str,
) -> ApplyUnitDecision:
    """Build one typed decision row from an observed unit state."""
    return {
        "id": state["id"],
        "mode": state["mode"],
        "install_strategy": state["install_strategy"],
        "disposition": state["disposition"],
        "classification": classification,
        "refusal_code": refusal_code,
        "reason": reason,
        "core_wins_members": state["core_wins_members"],
    }


def _apply_destination_changed(
    decl_unit: Mapping[str, object],
    baseline_row: Mapping[str, object] | None,
    snapshot: _Snapshot,
    projection: str,
) -> bool:
    """Destination delta for ``apply`` over the accepted lock baseline.

    A member with no ``accepted_destination_digest`` in the baseline (declared
    after the accepted snapshot) is seeded with the empty member digest, so it
    reads as unchanged while its destination holds no bytes: nothing was ever
    accepted there, so nothing can be lost. Accepted members keep
    ``_destination_changed``'s strict comparison, so pre-existing destination
    bytes still surface as ``local_drift`` or ``conflict``. The baseline row
    itself is never mutated: the seeded copy is local to this call.
    """
    row: Mapping[str, object] = baseline_row if baseline_row is not None else {}
    key = "replacement_members" if decl_unit.get("mode") == "replacement" else "members"
    accepted_ids = {str(member.get("id")) for member in (row.get(key, []) or [])}
    never_accepted: list[dict[str, object]] = [
        {
            "id": str(member.get("id")),
            "accepted_destination_digest": member_digest([]),
        }
        for member in (decl_unit.get(key, []) or [])
        if str(member.get("id")) not in accepted_ids
    ]
    if not never_accepted:
        return _destination_changed(decl_unit, row, snapshot, projection)
    merged: dict[str, object] = dict(row)
    merged[key] = list(row.get(key, []) or []) + never_accepted
    return _destination_changed(decl_unit, merged, snapshot, projection)


def _apply_unit_state(
    uid: str,
    catalog_unit: Mapping[str, object],
    decl_unit: Mapping[str, object],
    baseline_row: Mapping[str, object] | None,
    context: ApplyContext,
) -> ApplyUnitState:
    """Observe one declared unit against the accepted lock baseline.

    The upstream delta compares the unit digest at the trusted target revision
    with the digest recorded in the lock row: a unit with no baseline row is
    new at the target revision. ``core_wins_members`` carries only members
    that declare ``collision_policy: core_wins``, so no other index row can
    ever be treated as core-winnable downstream.
    """
    mode = str(decl_unit.get("mode"))
    strategy = str(catalog_unit.get("install_strategy"))
    core_wins = tuple(
        str(member.get("id"))
        for member in (catalog_unit.get("members", []) or [])
        if member.get("collision_policy") in COLLISION_POLICIES
    )
    if mode == "not_applicable":
        # Inapplicable units are never observed: no policy check, no delta.
        return {
            "id": uid,
            "mode": mode,
            "install_strategy": strategy,
            "disposition": "not_applicable",
            "upstream_changed": False,
            "policy_violation": None,
            "core_wins_members": core_wins,
        }
    projection = str(catalog_unit.get("sync_projection"))
    violation = _destination_policy_violation(
        uid, catalog_unit, decl_unit, context.snapshot
    )
    upstream_changed = (
        baseline_row is None
        or _unit_upstream_digest(context.upstream, context.target, catalog_unit)
        != baseline_row.get("accepted_upstream_digest")
    )
    if projection == "assertions":
        if baseline_row is None:
            destination_changed = True
        else:
            accepted_assertions = _catalog_assertions_at(
                context.upstream, context.accepted, context.catalog_path, uid
            )
            # Only the destination half is consumed: the upstream delta above
            # already compares the recorded baseline with the target revision.
            destination_changed = _assertion_deltas(
                catalog_unit, baseline_row, context.snapshot, accepted_assertions
            )[1]
    else:
        destination_changed = _apply_destination_changed(
            decl_unit, baseline_row, context.snapshot, projection
        )
    disposition = (
        "policy_violation"
        if violation is not None
        else _disposition(mode, upstream_changed, destination_changed)
    )
    return {
        "id": uid,
        "mode": mode,
        "install_strategy": strategy,
        "disposition": disposition,
        "upstream_changed": upstream_changed,
        "policy_violation": violation,
        "core_wins_members": core_wins,
    }


def _apply_refusal_reason(state: ApplyUnitState) -> str:
    """Explain why one unit outside ``apply``'s writable set cannot be written.

    Exactly one branch matches: a ``copy`` + ``mirror`` unit the writable rule
    already turned down, a non-``copy`` unit ``apply`` never writes, or a
    ``copy`` unit in a non-``mirror`` mode that its review governs.
    """
    strategy = state["install_strategy"]
    disposition = state["disposition"]
    if strategy == "copy" and state["mode"] == "mirror":
        return (
            f"copy mirror unit is {disposition}; destination bytes are "
            "never overwritten by apply"
        )
    if strategy != "copy":
        return (
            f"install_strategy {strategy} is never written by apply and "
            f"the unit is {disposition}"
        )
    return (
        f"{state['mode']} unit is never written by apply and "
        f"the unit is {disposition}"
    )


def _classify_apply_unit(state: ApplyUnitState, decided: set[str]) -> ApplyUnitDecision:
    """Apply the bounded write-set rule to one observed unit.

    WRITABLE is exactly ``copy`` ∩ ``mirror`` ∩ ``update_available`` (Section
    11). ``not_applicable`` units are skipped; every other applicable unit
    outside that writable set whose disposition is blocking is refused
    fail-closed — whatever its ``install_strategy`` and mode — because the
    lock regeneration is global and would otherwise re-baseline a unit whose
    state still blocks; every remaining unit (``current``, ``unmanaged``, any
    other non-blocking state) is an explicit no-action row, so no unit is
    classified by omission.
    """
    uid = state["id"]
    mode = state["mode"]
    strategy = state["install_strategy"]
    disposition = state["disposition"]
    if mode == "not_applicable":
        return _apply_decision(state, "skipped", None, "not_applicable mode is skipped")
    if state["policy_violation"] is not None:
        return _apply_decision(
            state, "refused", "policy_violation", str(state["policy_violation"])
        )
    if mode in _REVIEW_MODES and state["upstream_changed"] and uid not in decided:
        return _apply_decision(
            state,
            "refused",
            "review_changed",
            "upstream changed at the target revision but the review has no "
            "decision for it",
        )
    if strategy == "copy" and mode == "mirror" and disposition == "update_available":
        return _apply_decision(
            state,
            "writable",
            None,
            "copy mirror unit with an upstream update and an unchanged "
            "destination",
        )
    if disposition in _BLOCKING_DISPOSITIONS:
        return _apply_decision(
            state, "refused", disposition, _apply_refusal_reason(state)
        )
    if strategy == "copy" and mode == "mirror":
        return _apply_decision(
            state, "no_action", None, f"copy mirror unit is {disposition}"
        )
    if strategy != "copy":
        return _apply_decision(
            state,
            "no_action",
            None,
            f"install_strategy {strategy} is never written by apply and "
            f"the unit is {disposition}",
        )
    return _apply_decision(
        state,
        "no_action",
        None,
        f"{mode} unit is never written by apply; the review governs it",
    )


def _apply_decisions(
    catalog_units: Mapping[str, Mapping[str, object]],
    declaration_units: Mapping[str, Mapping[str, object]],
    baseline: Mapping[str, Mapping[str, object]],
    decided: set[str],
    context: ApplyContext,
) -> list[ApplyUnitDecision]:
    """Build the complete decision set, one row per declared catalog unit.

    Mapping validation is ``propose-lock``'s: every applicable non-replacement
    unit maps every catalog member exactly once, a replacement unit declares no
    members, and ``not_applicable`` units are skipped before any observation.
    """
    decisions: list[ApplyUnitDecision] = []
    for uid, catalog_unit in catalog_units.items():
        decl_unit = declaration_units[uid]
        mode = str(decl_unit.get("mode"))
        if mode != "not_applicable":
            if mode == "replacement":
                _need(
                    not decl_unit.get("members"),
                    "invalid_declaration",
                    f"{uid}: replacement must not declare members",
                )
            else:
                _declared_members(catalog_unit, decl_unit, uid)
        baseline_row = baseline.get(uid)
        if (
            baseline_row is not None
            and str(baseline_row.get("mode")) == "not_applicable"
        ):
            # A not_applicable lock row accepted nothing for this unit, so it
            # carries no member evidence for the destination comparison.
            baseline_row = None
        state = _apply_unit_state(uid, catalog_unit, decl_unit, baseline_row, context)
        decisions.append(_classify_apply_unit(state, decided))
    return decisions


class ApplyJournalEntry(TypedDict):
    """Pre-mutation record of one path ``apply`` intends to write.

    ``content`` and ``mode`` are ``None`` when the path does not exist yet,
    so the later restore path knows the write created the file. The journal
    is held in memory only; nothing here persists it.
    """

    path: str
    relative: str
    content: bytes | None
    mode: int | None


class ApplyRecoveryRecord(TypedDict):
    """Escape hatch for paths a failed restore could not put back.

    Emitted on stderr under the ``apply_restore_failed`` code when
    best-effort restoration leaves any journaled path out of sync with the
    journal: those paths must then be reconciled by hand, and ``paths``
    names each of them as a relative path. ``original`` is the failure that
    triggered the restore, rendered ``<code>: <message>`` for a
    ``SyncError`` and ``<type>: <message>`` otherwise. Nothing here
    promises atomicity or crash-transaction semantics.
    """

    original: str
    paths: tuple[str, ...]


class ApplyReport(TypedDict):
    """Machine-readable ``apply`` outcome printed to stdout.

    ``apply`` is ``success``, ``noop``, or ``failure``; ``verify`` is
    ``pass``, ``skipped``, or ``fail``; ``blocking`` carries the ``check``
    report's blocking reasons (empty on success and no-op runs).
    """

    apply: str
    written: list[str]
    lock: str | None
    verify: str
    blocking: list[str]


@dataclass(frozen=True)
class ApplyStagedWrite:
    """One planned content write: adopter-relative path, bytes, POSIX mode."""

    relative: str
    content: bytes
    mode: int


@dataclass(frozen=True)
class ApplyStoryIndexPlan:
    """One writable story unit's planned index merge (Section 17)."""

    relative: str
    core_index: bytes
    rows: tuple[StoryMergeMember, ...]


class _WorktreeSnapshot:
    """Adopter snapshot read from on-disk worktree bytes, for ``apply`` only.

    ``check``, ``propose-lock``, and ``verify-all`` never construct this
    class: they keep reading exactly one explicit commit or staged index.
    ``apply`` uses it after staging so lock regeneration and verification
    report the state ``apply`` actually wrote. Regular files only: the Git
    mode is derived from the executable bit, matching how Git records
    ``100644``/``100755`` blobs.
    """

    def __init__(self, root: str) -> None:
        self.root = root

    def _absolute(self, relative: str) -> str:
        if os.path.isabs(relative):
            return relative
        return os.path.join(self.root, *relative.split("/"))

    def _entry(self, absolute: str, logical: str, entry_path: str) -> ProjectedEntry:
        try:
            with open(absolute, "rb") as handle:
                content = handle.read()
            permission_bits = os.stat(absolute).st_mode
        except OSError as exc:
            _fail(
                "adopter_snapshot_unavailable",
                f"cannot read worktree file {logical}: {exc}",
            )
        return ProjectedEntry(
            path=entry_path,
            mode="100755" if permission_bits & 0o111 else "100644",
            content=content,
        )

    def file_entry(self, path: str) -> ProjectedEntry | None:
        absolute = self._absolute(path)
        if not os.path.isfile(absolute):
            return None
        return self._entry(absolute, path, "")

    def tree_entries(self, root: str) -> list[ProjectedEntry]:
        base = self._absolute(root)
        entries: list[ProjectedEntry] = []
        if not os.path.isdir(base):
            return entries
        for current, _directories, files in os.walk(base):
            for name in sorted(files):
                absolute = os.path.join(current, name)
                relative = os.path.relpath(absolute, base).replace(os.sep, "/")
                logical = f"{root.rstrip('/')}/{relative}"
                entries.append(self._entry(absolute, logical, relative))
        return entries


def _posix_file_mode(git_mode: str, where: str) -> int:
    """Map a Git regular-file mode to the POSIX bits ``apply`` writes."""
    _need(
        git_mode in ("100644", "100755"),
        "unsupported_special_file",
        f"{where}: unsupported file mode {git_mode}",
    )
    return 0o755 if git_mode == "100755" else 0o644


def _apply_worktree_path(root: str, relative: str) -> str:
    """Resolve one adopter-relative destination to its absolute worktree path."""
    if os.path.isabs(relative):
        return relative
    return os.path.join(root, *relative.split("/"))


def _apply_path_state(root: str, relative: str) -> ApplyJournalEntry:
    """IO helper: capture one intended path's current bytes and file mode.

    Reads only; nothing is written. An absent path records ``None`` bytes
    and mode so the journal can distinguish an update from a creation.
    """
    path = _apply_worktree_path(root, relative)
    if not os.path.isfile(path):
        return {"path": path, "relative": relative, "content": None, "mode": None}
    try:
        with open(path, "rb") as handle:
            content = handle.read()
        mode = stat.S_IMODE(os.stat(path).st_mode)
    except OSError as exc:
        _fail(
            "adopter_snapshot_unavailable",
            f"cannot read current bytes of {relative}: {exc}",
        )
    return {"path": path, "relative": relative, "content": content, "mode": mode}


def _apply_write_file(path: str, relative: str, content: bytes, mode: int) -> None:
    """IO helper: write one staged file and its POSIX mode, or fail closed."""
    try:
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(content)
        os.chmod(path, mode)
    except OSError as exc:
        _fail("apply_write_failed", f"cannot write {relative}: {exc}")


def _apply_restore_matches(entry: ApplyJournalEntry) -> bool:
    """IO helper: return whether one journaled path matches its recorded state."""
    path = entry["path"]
    content = entry["content"]
    if content is None:
        # The journal recorded no regular file here, so a regular file now
        # can only be this run's creation. A pre-existing directory or link
        # is not this run's work and is left exactly where it is.
        return not os.path.isfile(path)
    if not os.path.isfile(path):
        return False
    try:
        with open(path, "rb") as handle:
            current = handle.read()
        mode = stat.S_IMODE(os.stat(path).st_mode)
    except OSError:
        return False
    recorded_mode = entry["mode"]
    return current == content and (recorded_mode is None or mode == recorded_mode)


def _apply_restore_entry(entry: ApplyJournalEntry) -> bool:
    """IO helper: best-effort restore of a single journaled path.

    A path with recorded bytes is rewritten and re-chmodded to its recorded
    mode; a path that held no regular file before the run has the regular
    file this run created removed from it. Returns ``False`` when the path
    cannot be put back or does not verify against the journal. IO failures
    are converted to that ``False`` outcome — this never raises.
    """
    path = entry["path"]
    content = entry["content"]
    mode = entry["mode"]
    try:
        if content is None:
            if os.path.isfile(path):
                os.remove(path)
        else:
            with open(path, "wb") as handle:
                handle.write(content)
            if mode is not None:
                os.chmod(path, mode)
    except OSError:
        return False
    return _apply_restore_matches(entry)


def _apply_restore(journal: Sequence[ApplyJournalEntry]) -> tuple[str, ...]:
    """Best-effort restore of every journaled path after a failed mutation.

    Attempts each journaled path exactly once and never stops at the first
    restore failure: a path that cannot be put back is recorded and the loop
    keeps going. Returns the adopter-relative paths whose on-disk state still
    does not match the journal — an empty tuple means every journaled path is
    back to its recorded pre-apply bytes and file mode. Only journaled paths
    are restored; parent directories this run created along the way are not
    journaled and stay where they are. This is a best-effort restore, not a
    transaction and not crash-atomic.
    """
    inconsistent: list[str] = []
    for entry in journal:
        if not _apply_restore_entry(entry):
            inconsistent.append(entry["relative"])
    return tuple(inconsistent)


def _apply_original_failure(exc: BaseException) -> str:
    """Render one mutation failure as a recovery record's ``original`` field."""
    if isinstance(exc, SyncError):
        return f"{exc.code}: {exc.message}"
    return f"{type(exc).__name__}: {exc}"


def _emit_apply_recovery(record: ApplyRecoveryRecord) -> None:
    """Emit one recovery record on stderr under ``apply_restore_failed``."""
    payload = json.dumps(
        {"original": record["original"], "paths": list(record["paths"])},
        sort_keys=True,
        separators=(",", ":"),
    )
    print(
        f"sync-aicore-adoption: apply_restore_failed: recovery record: {payload}",
        file=sys.stderr,
    )


def _apply_abandon(
    journal: Sequence[ApplyJournalEntry], exc: BaseException
) -> NoReturn:
    """Surface a mutation failure only after a best-effort journal restore.

    Every journaled path is restored first. When all of them verify against
    the journal, the original failure is re-raised under its own code — or
    under ``apply_write_failed`` when it was not a ``SyncError`` — with an
    explicit statement that every journaled path is back to its recorded
    pre-apply bytes and mode, and the run exits non-zero. When any journaled
    path cannot be put back, the recovery record naming those paths is
    emitted on stderr and the same run exits non-zero under
    ``apply_restore_failed``, leaving the adopter to be reconciled by hand
    from that record. The restore is best-effort: no atomicity or
    crash-transaction guarantee is claimed anywhere on either path.
    """
    original = _apply_original_failure(exc)
    inconsistent = _apply_restore(journal)
    restored = "every journaled path was restored to its recorded pre-apply bytes and mode"
    if not inconsistent:
        if isinstance(exc, SyncError):
            raise SyncError(
                exc.code, f"{exc.message}; {restored}"
            ) from exc
        raise SyncError(
            "apply_write_failed", f"{original}; {restored}"
        ) from exc
    _emit_apply_recovery(
        ApplyRecoveryRecord(original=original, paths=inconsistent)
    )
    raise SyncError(
        "apply_restore_failed",
        f"apply failed ({original}); best-effort restore left "
        f"{len(inconsistent)} journaled path(s) possibly inconsistent: "
        f"{', '.join(inconsistent)}",
    ) from exc


def _apply_write_plan(
    writable_ids: Sequence[str],
    catalog_units: Mapping[str, Mapping[str, object]],
    declaration_units: Mapping[str, Mapping[str, object]],
    control_paths: Sequence[str],
    lock_relative: str,
    upstream: _GitRepo,
    target: str,
) -> tuple[list[ApplyStagedWrite], list[ApplyStoryIndexPlan]]:
    """Plan every content write ``apply`` intends to make; write nothing.

    IO boundary: reads upstream Git objects at ``target`` through
    ``_GitRepo`` and validates destinations; the adopter worktree is never
    touched here. Destinations are validated with ``propose-lock``'s rules —
    no absolute path, no parent traversal, no protected control path, no
    duplicate or overlapping destination — and the lock path participates
    in the same conflict check, so an invalid mapping can never reach the
    worktree before it fails closed. Only ``file``, ``guarded_file``, and
    ``tree`` projections carry stageable content; assertion units never do.
    """
    staged: list[ApplyStagedWrite] = []
    stories: list[ApplyStoryIndexPlan] = []
    destinations: list[tuple[str, str, str]] = [("<apply>", "lock", lock_relative)]
    index_paths: set[str] = set()
    for uid in writable_ids:
        catalog_unit = catalog_units[uid]
        decl_unit = declaration_units[uid]
        projection = str(catalog_unit.get("sync_projection"))
        _need(
            projection in ("file", "guarded_file", "tree"),
            "unsupported_projection",
            f"{uid}: sync_projection {projection} carries no stageable content",
        )
        declared = _declared_members(catalog_unit, decl_unit, uid)
        members = list(catalog_unit.get("members", []) or [])
        _need(members, "invalid_mapping", f"{uid}: writable unit must declare members")
        normalized_by_id: dict[str, str] = {}
        for member in members:
            member_id = str(member.get("id"))
            source = str(member.get("source"))
            normalized = _validate_destination(
                declared[member_id], f"{uid}.{member_id}", control_paths
            )
            normalized_by_id[member_id] = normalized
            destinations.append((uid, member_id, normalized))
            if _content_projection(projection) == "tree":
                entries = upstream.tree_entries(target, source, "baseline_unavailable")
                _need(
                    entries,
                    "baseline_unavailable",
                    f"{uid}.{member_id}: source tree is empty at {target}; "
                    "apply never deletes destination files",
                )
                for entry in entries:
                    staged.append(
                        ApplyStagedWrite(
                            relative=f"{normalized}/{entry.path}",
                            content=entry.content,
                            mode=_posix_file_mode(entry.mode, f"{uid}.{member_id}"),
                        )
                    )
                continue
            entry = upstream.file_entry(target, source, "baseline_unavailable")
            _need(
                entry is not None,
                "baseline_unavailable",
                f"{uid}.{member_id}: source file is missing at {target}",
            )
            staged.append(
                ApplyStagedWrite(
                    relative=normalized,
                    content=entry.content,
                    mode=_posix_file_mode(entry.mode, f"{uid}.{member_id}"),
                )
            )
        if catalog_unit.get("kind") == STORY_UNIT_KIND:
            first = members[0]
            first_id = str(first.get("id"))
            index_relative = _sibling_story_index(normalized_by_id[first_id])
            core_path = _sibling_story_index(str(first.get("source")))
            core_entry = upstream.file_entry(target, core_path, "baseline_unavailable")
            if index_relative not in index_paths:
                # Story units may legitimately share one destination index;
                # their merges compose instead of conflicting (Section 17).
                index_paths.add(index_relative)
                destinations.append((uid, "index", index_relative))
            rows = tuple(
                StoryMergeMember(
                    id=str(member.get("id")),
                    destination=declared[str(member.get("id"))],
                    collision_policy=member.get("collision_policy"),
                )
                for member in members
            )
            stories.append(
                ApplyStoryIndexPlan(
                    relative=index_relative,
                    core_index=(
                        core_entry.content if core_entry is not None else b""
                    ),
                    rows=rows,
                )
            )
    _check_destination_set(destinations)
    return staged, stories


def _print_apply_report(report: ApplyReport, output_format: str) -> None:
    """Print one terse, machine-readable ``apply`` outcome to stdout."""
    if output_format == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"apply: {report['apply']}")
    written = ", ".join(report["written"]) if report["written"] else "none"
    print(f"written: {written}")
    print(f"lock: {report['lock'] if report['lock'] is not None else 'none'}")
    print(f"verify: {report['verify']}")
    for reason in report["blocking"]:
        print(f"blocking: {reason}")


def run_apply(args: argparse.Namespace) -> int:
    """Classify the bounded ``apply`` write set, stage it, re-lock, verify.

    Reuses ``propose-lock``'s loaders, coverage validation, trusted-revision
    and snapshot resolution, then builds one decision per declared unit
    against the accepted lock baseline. Every refusal raises ``SyncError``
    (exit 2) naming the units and their reasons before anything is written.

    A refusal-free run then: journals every path it intends to write with
    current bytes and file mode (in memory), stages the writable members,
    merges the portable story index for writable story units, regenerates
    the candidate lock through the ``propose-lock`` builder, and runs the
    ``check`` report against the written worktree. Classification reads the
    declared explicit snapshot; lock regeneration and verification read the
    post-write worktree, so the result reported is the state actually
    staged. An empty write set is a no-op that exits 0 without touching the
    adopter; compliance exits 0, a non-compliant check exits 1 with its
    blocking reasons, and fatal protocol failures exit 2.

    Every mutation after the journal — content staging, story-index writes,
    and the lock write — plus lock regeneration and verification run inside
    one guarded region. Any failure there restores every journaled path from
    the in-memory journal before the failure is surfaced, so a failed run
    never leaves content half-written under a lock that would make ``check``
    pass silently on it. The restore is best-effort, not atomic: when it
    cannot put a path back it emits an ``apply_restore_failed`` recovery
    record on stderr naming every path that may now be inconsistent and
    still exits non-zero. A restored-and-abandoned failure exits 2 with its
    original code (``apply_write_failed`` for a write IO error); a
    non-compliant verify still exits 1 on its written, lock-consistent
    state.
    """
    _need(
        args.adopter_revision is not None or args.adopter_index,
        "adopter_snapshot_unavailable",
        "exactly one of --adopter-revision or --adopter-index is required",
    )
    for name, value, code in (
        ("--declaration", args.declaration, "invalid_declaration"),
        ("--lock", args.lock, "invalid_lock"),
        ("--catalog", args.catalog, "invalid_mapping"),
    ):
        _need(value, code, f"{name} is required")
    catalog_path = _resolve_catalog_path(str(args.catalog), str(args.upstream_repo))
    declaration = load_declaration(str(args.declaration))
    review = (
        load_review(str(args.review))
        if args.review
        else {"schema_version": 2, "decisions": []}
    )
    catalog = load_catalog(catalog_path)
    block = catalog.get("catalog")
    _need(
        isinstance(block, Mapping)
        and block.get("upstream_repository") == declaration.get("upstream_repository"),
        "repository_identity_mismatch",
        "catalog and declaration upstream_repository differ",
    )
    upstream = _GitRepo(str(args.upstream_repo))
    target, _diagnostic = _trusted_revision(upstream, None)
    adopter = _resolve_adopter_repo(args)
    snapshot = _snapshot_for(args, adopter)
    catalog_units, declaration_units = _validate_declaration_coverage(
        catalog, declaration, declaration.get("profile", {})
    )
    decided = {str(d.get("unit")) for d in review.get("decisions", [])}
    baseline_lock = load_lock(str(args.lock))
    _need(
        baseline_lock.get("upstream_repository")
        in (None, declaration.get("upstream_repository")),
        "repository_identity_mismatch",
        "baseline lock upstream_repository differs from the declaration",
    )
    accepted = str(baseline_lock.get("accepted_source_commit"))
    _need(
        upstream.is_ancestor(accepted, target),
        "baseline_unavailable",
        f"accepted commit {accepted} is not an ancestor of {target}",
    )
    baseline = {str(row.get("id")): row for row in baseline_lock.get("units", [])}
    unit_decisions = _apply_decisions(
        catalog_units,
        declaration_units,
        baseline,
        decided,
        ApplyContext(
            upstream=upstream,
            target=target,
            accepted=accepted,
            snapshot=snapshot,
            catalog_path=catalog_path,
        ),
    )
    refusals = [row for row in unit_decisions if row["classification"] == "refused"]
    if refusals:
        detail = "; ".join(f"{row['id']}: {row['reason']}" for row in refusals)
        _fail(str(refusals[0]["refusal_code"]), f"apply refused: {detail}")
    writable = [row for row in unit_decisions if row["classification"] == "writable"]
    if not writable:
        _print_apply_report(
            ApplyReport(
                apply="noop",
                written=[],
                lock=None,
                verify="skipped",
                blocking=[],
            ),
            args.format,
        )
        return 0
    root = adopter.toplevel() or adopter.path
    lock_path = str(args.lock)
    lock_relative = _repo_relative_path(adopter, lock_path)
    staged, stories = _apply_write_plan(
        [row["id"] for row in writable],
        catalog_units,
        declaration_units,
        _control_paths(catalog),
        lock_relative,
        upstream,
        target,
    )
    # Journal first: record every path this run intends to write, with its
    # current bytes and file mode, in memory. Nothing is mutated yet; the
    # guarded region below consumes this journal for restoration. A shared
    # story index is journaled exactly once.
    intended = (
        [write.relative for write in staged]
        + [plan.relative for plan in stories]
        + [lock_relative]
    )
    journal: list[ApplyJournalEntry] = [
        _apply_path_state(root, relative)
        for relative in dict.fromkeys(intended)
    ]
    journal_by_relative = {entry["relative"]: entry for entry in journal}
    # One guarded region covers every mutation and both post-mutation reads:
    # content staging, story-index writes, the lock write, lock regeneration,
    # and verification. Any exception raised inside it — including a
    # ``SyncError`` from a merge, from the propose-lock builder, or from the
    # check report — hands the journal to ``_apply_abandon``, which restores
    # first and only then surfaces the failure. ``KeyboardInterrupt`` and
    # ``SystemExit`` are ``BaseException`` and deliberately propagate
    # untouched.
    try:
        # Stage the writable members' core content at their declared destinations.
        for write in staged:
            entry = journal_by_relative[write.relative]
            _apply_write_file(entry["path"], write.relative, write.content, write.mode)
        # Merge the portable story index for each writable story unit: core rows
        # for members carrying collision_policy: core_wins replace differing rows;
        # destination-only rows and every byte outside the table survive intact.
        # Units sharing one destination index compose in declared order — each
        # merge reads the previous one's result — and the composed bytes are
        # written once per index path.
        merged_indexes: dict[str, bytes] = {}
        for plan in stories:
            entry = journal_by_relative[plan.relative]
            base = merged_indexes.get(plan.relative, entry["content"])
            result, _collisions = merge_story_index(plan.core_index, base, plan.rows)
            merged_indexes[plan.relative] = result
        for relative, content in merged_indexes.items():
            entry = journal_by_relative[relative]
            mode = entry["mode"] if entry["mode"] is not None else 0o644
            _apply_write_file(entry["path"], relative, content, mode)
        # Regenerate the candidate lock through the propose-lock builder at the
        # one target revision, reading the post-write worktree, and write it only
        # after every content byte is staged.
        candidate = _propose_lock_document(args, _WorktreeSnapshot(root))
        text = yaml.safe_dump(candidate, sort_keys=False, default_flow_style=False)
        lock_entry = journal_by_relative[lock_relative]
        lock_mode = lock_entry["mode"] if lock_entry["mode"] is not None else 0o644
        _apply_write_file(
            lock_entry["path"],
            lock_relative,
            (text.rstrip("\n") + "\n").encode("utf-8"),
            lock_mode,
        )
        # Verify with the existing check logic against the written worktree and
        # require its exit 0 before this run may report success. A failure here
        # must also restore: content without its regenerated lock is exactly the
        # half-written state no run may leave behind.
        verification = _check_report(
            str(args.declaration),
            lock_path,
            str(args.review) if args.review else None,
            catalog_path,
            upstream,
            target,
            False,
            lambda: _WorktreeSnapshot(root),
        )
    except Exception as exc:
        _apply_abandon(journal, exc)
    # Non-compliance is not a mutation failure: the worktree and its lock are
    # written and mutually consistent, so ``check`` reports the same blocking
    # reasons here instead of passing silently, and the run exits 1 on it.
    compliance = bool(verification.get("compliance"))
    _print_apply_report(
        ApplyReport(
            apply="success" if compliance else "failure",
            written=[row["id"] for row in writable],
            lock=lock_path,
            verify="pass" if compliance else "fail",
            blocking=[
                str(reason) for reason in verification.get("blocking_reasons", [])
            ],
        ),
        args.format,
    )
    return 0 if compliance else 1


def _add_global_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--upstream-repo",
        default=".",
        help="upstream AICore repository (default: .)",
    )
    parser.add_argument(
        "--catalog",
        default=".aicore/core-catalog-v2.yaml",
        help="catalog path",
    )
    parser.add_argument("--declaration", help="adopter declaration path")
    parser.add_argument("--review", help="adopter review path")
    parser.add_argument("--lock", help="adopter lock path")
    parser.add_argument("--registry", help="adopter registry path")
    parser.add_argument(
        "--format",
        choices=("json", "human"),
        default="human",
        help="output format",
    )


def _add_snapshot_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--adopter-repo",
        help="adopter Git repository (default: inferred from --declaration)",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--adopter-revision",
        metavar="<sha>",
        help="explicit adopter commit tree",
    )
    group.add_argument(
        "--adopter-index",
        action="store_true",
        help="staged Git index only",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sync-aicore-adoption",
        description="AICore adoption synchronization (protocol v2) core substrate",
    )
    _add_global_options(parser)
    subparsers = parser.add_subparsers(
        dest="command", metavar="{check,propose-lock,verify-all,apply}"
    )
    subparsers.required = True
    check = subparsers.add_parser("check", help="report adoption compliance")
    _add_global_options(check)
    _add_snapshot_options(check)
    check.add_argument(
        "--diagnostic-revision",
        metavar="<sha>",
        help="diagnostic-only comparison revision",
    )
    check.set_defaults(func=run_check)
    propose = subparsers.add_parser(
        "propose-lock", help="emit a candidate lock to stdout"
    )
    _add_global_options(propose)
    _add_snapshot_options(propose)
    propose.set_defaults(func=run_propose)
    verify = subparsers.add_parser(
        "verify-all", help="check every registered adopter"
    )
    _add_global_options(verify)
    verify.add_argument("--checkouts-root", help="cached read-only checkout root")
    verify.set_defaults(func=run_verify)
    apply = subparsers.add_parser(
        "apply", help="apply a reviewed byte-equal update to the adopter"
    )
    _add_global_options(apply)
    _add_snapshot_options(apply)
    apply.set_defaults(func=run_apply)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except SyncError as exc:
        print(f"sync-aicore-adoption: {exc.code}: {exc.message}", file=sys.stderr)
        if exc.code == "schema_upgrade_required":
            print(SCHEMA_UPGRADE_GUIDANCE, file=sys.stderr)
        return EXIT_FATAL


if __name__ == "__main__":
    sys.exit(main())
