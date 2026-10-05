"""Shared error types, snapshot interfaces, and pure helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, NoReturn, Protocol, TypedDict


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


@dataclass(frozen=True)
class ProjectedEntry:
    """One projected file/tree entry: logical path, mode, raw content."""

    path: str
    mode: str
    content: bytes


class _Snapshot(Protocol):
    """One explicit adopter content source: a commit tree or the staged index."""

    def file_entry(self, path: str) -> ProjectedEntry | None: ...

    def tree_entries(self, root: str) -> list[ProjectedEntry]: ...


class StoryMergeMember(TypedDict):
    id: str
    destination: str
    collision_policy: str | None


class CatalogMember(TypedDict, total=False):
    """One catalog member mapping supplied by upstream."""

    id: str
    source: str
    destination: str
    collision_policy: str


class CatalogUnit(TypedDict, total=False):
    """One catalog unit with its ownership and projection metadata."""

    id: str
    kind: str
    install_strategy: str
    applicability: dict[str, object]
    sync_projection: str
    destination_policy: str
    destination: str
    rule_documents: list[str]
    members: list[CatalogMember]
    assertions: list[dict[str, str]]


class CatalogDocument(TypedDict, total=False):
    """A parsed schema-v2 upstream catalog document."""

    schema_version: int
    catalog: dict[str, object]
    units: list[CatalogUnit]


class DeclarationMember(TypedDict, total=False):
    """One adopter-owned destination mapping."""

    id: str
    destination: str
    projection: str


class DeclarationUnit(TypedDict, total=False):
    """One adopter declaration unit and its selected ownership mode."""

    id: str
    mode: str
    members: list[DeclarationMember]
    replacement_members: list[DeclarationMember]


class TestRunner(TypedDict, total=False):
    """One declaration's reviewed whole-project test-runner metadata.

    Either the ``no_tests`` disposition or the whole-project ``commands`` with
    their designated ``executor``, ``scope``, ``reviewer``, and ``evidence``.
    Shape validation rejects any key outside this closed set.
    """

    no_tests: bool
    commands: list[str]
    executor: str
    scope: str
    reviewer: str
    evidence: str


class DeclarationDocument(TypedDict, total=False):
    """A parsed schema-v2 adopter declaration document."""

    schema_version: int
    upstream_repository: str
    profile: dict[str, bool]
    units: list[DeclarationUnit]
    test_runner: TestRunner


class ReviewDecision(TypedDict, total=False):
    """One human reconciliation decision bound to reviewed bytes.

    ``verified_layout`` is the closed optional two-section attestation. It is
    recorded only after a whole-document review of every protected document in
    the unit; a marker added to an unreviewed file never sets it.
    """

    unit: str
    decision: str
    reviewer: str
    evidence: str
    verified_layout: str
    reviewed_upstream_digest: str
    reviewed_destination_digest: str


class ReviewTransition(TypedDict):
    """The global binding for one proposed acceptance transition."""

    baseline_lock_digest: str | None
    target_source_commit: str
    declaration_digest: str


class ReviewDocument(TypedDict, total=False):
    """A parsed schema-v2 reconciliation review document."""

    schema_version: int
    upstream_repository: str
    transition: ReviewTransition
    decisions: list[ReviewDecision]


class LockMember(TypedDict, total=False):
    """One accepted source/destination digest pair in a lock row."""

    id: str
    destination: str
    projection: str
    accepted_upstream_digest: str
    accepted_destination_digest: str


class LockUnit(TypedDict, total=False):
    """One accepted catalog-unit row in a schema-v2 lock."""

    id: str
    mode: str
    retired: bool
    declaration_unit_digest: str
    accepted_upstream_digest: str
    members: list[LockMember]
    replacement_members: list[LockMember]


class LockDocument(TypedDict, total=False):
    """A parsed or proposed schema-v2 adoption lock document."""

    schema_version: int
    upstream_repository: str
    accepted_source_commit: str
    accepted_catalog_digest: str
    declaration_digest: str
    review_digest: str
    accepted_snapshot_digest: str
    units: list[LockUnit]


class RegistryAdopter(TypedDict, total=False):
    """One registered adopter checkout descriptor."""

    id: str
    repository: str
    default_branch: str
    declaration_path: str
    lock_path: str
    review_path: str


class RegistryDocument(TypedDict, total=False):
    """A parsed schema-v2 adopter registry document."""

    schema_version: int
    upstream_repository: str
    adopters: list[RegistryAdopter]


class CatalogTransitionRow(TypedDict):
    """One changed catalog unit and its applicability/mode facts."""

    id: str
    added_members: list[str]
    removed_members: list[str]
    changed_members: list[str]
    applicability_changed: bool
    accepted_applicable: bool
    target_applicable: bool
    accepted_mode: str | None
    target_mode: str | None


class CatalogTransition(TypedDict):
    """Reported delta between the accepted and target catalog definitions."""

    added_units: list[str]
    removed_units: list[str]
    changed_units: list[CatalogTransitionRow]


class CheckUnitReport(TypedDict, total=False):
    """One unit-level compliance result emitted by the read-only check command."""

    id: str
    mode: str | None
    retired: bool
    upstream_delta: str | None
    destination_delta: str | None
    disposition: str


class CheckReport(TypedDict):
    """Structured compliance result emitted by check and verify-all."""

    compliance: bool
    accepted_revision: str
    required_revision: str
    diagnostic: bool
    units: list[CheckUnitReport]
    catalog_transition: CatalogTransition
    collisions: list[str]
    blocking_reasons: list[str]


def _field(record: object, name: str, default: object = None) -> object:
    if isinstance(record, Mapping):
        return record.get(name, default)
    return getattr(record, name, default)


def _normalize_destination(destination: str) -> str:
    normalized = destination.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _normalize_source_path(path: str) -> str:
    """Normalize one source-relative path, rejecting absolute/parent traversal."""
    raw = str(path).replace("\\", "/")
    normalized = raw
    while normalized.startswith("./"):
        normalized = normalized[2:]
    _need(not normalized.startswith("/"), "invalid_mapping", f"absolute source path: {raw}")
    segments = [segment for segment in normalized.split("/") if segment not in ("", ".")]
    _need(
        ".." not in segments,
        "invalid_mapping",
        f"parent traversal in source path: {raw}",
    )
    joined = "/".join(segments)
    _need(bool(joined), "invalid_mapping", f"source path is empty: {raw}")
    return joined


def _content_projection(projection: str) -> str:
    """Normalize guarded files to ordinary file digest framing."""
    return "file" if projection == "guarded_file" else projection


def _strip_comments(text: str) -> str:
    lines = [
        line
        for line in text.splitlines()
        if not line.strip().startswith(("//", "#"))
    ]
    return "\n".join(lines)
