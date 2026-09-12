"""Core substrate for the ``sync-aicore-adoption`` protocol v2.

Implements the CLI surface, the v2 document loaders with schema-shape
validation, the Section 7 digest protocol, the Section 6 applicability model,
the read-only ``check`` command (Sections 8-12), the stdout-only
``propose-lock`` command (Sections 3-4, 15), and the read-only ``verify-all``
aggregate over the adopter registry (Section 16).

Read-only by construction: nothing here mutates an upstream or adopter
repository, the index, or the worktree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, NoReturn, Protocol, Sequence

import yaml

EXIT_FATAL = 2
PROFILE_MARKERS = ("backend_stack", "python_scripts", "ticket_system")
DECLARATION_MODES = ("mirror", "adapted", "replacement", "destination_owned", "not_applicable")
LOCK_MODES = DECLARATION_MODES
PROJECTIONS = ("file", "tree")
SYNC_PROJECTIONS = ("file", "tree", "assertions")
REVIEW_DECISIONS = ("applied", "declined", "superseded")
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
        _mapping_list(
            unit.get("members"),
            f"{where}.members",
            "invalid_mapping",
            "id",
            "source",
            "destination",
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
# check (protocol-v2 Sections 8-12): read-only compliance report
# ---------------------------------------------------------------------------

_BLOCKING_DISPOSITIONS = frozenset(
    {
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
    if projection == "tree":
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
    if projection == "tree":
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
        if mode in _REVIEW_MODES and upstream_changed and uid not in decisions:
            _fail(
                "review_changed",
                f"{uid}: upstream changed but the review has no decision for it",
            )
        disposition = _disposition(mode, upstream_changed, destination_changed)
        if disposition == "current" and accepted != target:
            disposition = "baseline_advance_required"
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
    snapshot = _snapshot_for(args, _resolve_adopter_repo(args))
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
    _check_destination_set(destinations)
    declaration_digest = _raw_file_digest(str(args.declaration))
    review_digest = (
        _raw_file_digest(str(args.review))
        if args.review and os.path.isfile(str(args.review))
        else _sha256(b"")
    )
    lock = {
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
            shutil.rmtree(temp, ignore_errors=True)
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
        dest="command", metavar="{check,propose-lock,verify-all}"
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
