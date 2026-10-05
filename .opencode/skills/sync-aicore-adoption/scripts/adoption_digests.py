"""Deterministic content, mapping, and snapshot digest functions."""

from __future__ import annotations

import hashlib
from typing import Iterable, Mapping, Sequence

from adoption_contracts import ProjectedEntry, _field, _need, _normalize_destination


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _is_digest(value: object) -> bool:
    return (
        isinstance(value, str)
        and value.startswith("sha256:")
        and len(value) == 71
        and all(char in "0123456789abcdef" for char in value[7:])
    )


def _is_excluded(path: str) -> bool:
    return "__pycache__" in path.replace("\\", "/").split("/") or path.endswith(".pyc")


def member_digest(entries: Iterable[ProjectedEntry]) -> str:
    """Digest a file/tree member: Section 2 entry/path/mode/size/content framing."""
    ordered = sorted(entries, key=lambda item: item.path.encode("utf-8"))
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
    """Digest the ordered catalog assertion list using Section 2 framing."""
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


def _retired_descriptor_digest(row: Mapping[str, object]) -> str:
    """Digest a lock-only retained mapping for its retirement review binding."""
    chunks = [
        b"retired\nunit:" + str(row.get("id")).encode("utf-8")
        + b"\nmode:" + str(row.get("mode")).encode("ascii")
        + b"\ndeclaration:" + str(row.get("declaration_unit_digest")).encode("ascii")
        + b"\nupstream:" + str(row.get("accepted_upstream_digest")).encode("ascii")
        + b"\n"
    ]
    members = (
        row.get("replacement_members")
        if row.get("mode") == "replacement"
        else row.get("members", [])
    )
    for member in members or []:
        chunks.append(
            b"member\nid:" + str(member.get("id")).encode("utf-8")
            + b"\ndestination:" + str(member.get("destination")).encode("utf-8")
            + b"\nprojection:" + str(member.get("projection", "file")).encode("ascii")
            + b"\nupstream:" + str(member.get("accepted_upstream_digest", "")).encode("ascii")
            + b"\ndestination_digest:"
            + str(member.get("accepted_destination_digest")).encode("ascii")
            + b"\n"
        )
    return _sha256(b"".join(chunks))


def _locked_destination_digest(row: Mapping[str, object]) -> str:
    """Digest the accepted result facts of a normal or retired lock row."""
    members = (
        row.get("replacement_members")
        if row.get("mode") == "replacement"
        else row.get("members", [])
    )
    return unit_digest(
        (
            str(member.get("id")),
            str(member.get("accepted_destination_digest")),
        )
        for member in members or []
    )


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
        if row.get("retired", False):
            chunks.append(
                b"retired\nunit:" + str(row.get("id")).encode("utf-8")
                + b"\ndescriptor:" + _retired_descriptor_digest(row).encode("ascii")
                + b"\n"
            )
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
