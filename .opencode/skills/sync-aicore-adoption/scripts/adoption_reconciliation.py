"""Review binding validation and retired-unit descriptor handling."""

from __future__ import annotations

from typing import Mapping, Sequence

from adoption_constants import RULE_LAYOUT_VALUE, _REVIEW_MODES
from adoption_contracts import _Snapshot, _need
from adoption_content import _snapshot_member_digest, _unit_upstream_digest
from adoption_digests import _locked_destination_digest, _sha256, unit_digest
from adoption_git import _GitRepo
from adoption_mapping import _validate_destination

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


def _review_transition_matches(
    review: Mapping[str, object],
    baseline_lock_digest: str | None,
    target_revision: str,
    declaration_digest: str,
) -> bool:
    transition = review.get("transition")
    return (
        isinstance(transition, Mapping)
        and transition.get("baseline_lock_digest") == baseline_lock_digest
        and transition.get("target_source_commit") == target_revision
        and transition.get("declaration_digest") == declaration_digest
    )


def _reviewed_unit_source_digest(
    upstream: _GitRepo,
    target_revision: str,
    catalog_unit: Mapping[str, object] | None,
    accepted_digest: str | None,
) -> str:
    if catalog_unit is not None:
        return _unit_upstream_digest(upstream, target_revision, catalog_unit)
    # A retired unit has no target bytes. Bind the explicit retirement to the
    # accepted source digest instead of treating absence as an unbound choice.
    return _sha256(b"retired-upstream\n" + str(accepted_digest or "").encode("ascii"))


def _retired_destination_digest(row: Mapping[str, object], snapshot: _Snapshot) -> str:
    """Digest the live retained destinations using their lock-only descriptor."""
    members = (
        row.get("replacement_members")
        if row.get("mode") == "replacement"
        else row.get("members", [])
    )
    return unit_digest(
        (
            str(member.get("id")),
            _snapshot_member_digest(
                snapshot,
                str(member.get("destination")),
                str(member.get("projection", "file")),
            ),
        )
        for member in members or []
    )


def _retired_row_from_predecessor(
    predecessor: Mapping[str, object],
    projection: str,
    snapshot: _Snapshot,
    control_paths: Sequence[str],
    destinations: list[tuple[str, str, str]],
) -> dict[str, object]:
    """Copy one validated non-mirror predecessor into a lock-only retired row."""
    uid = str(predecessor.get("id"))
    _need(
        predecessor.get("mode") in _REVIEW_MODES and not predecessor.get("retired", False),
        "invalid_lock",
        f"{uid}: retirement requires a non-retired non-mirror predecessor row",
    )
    member_key = "replacement_members" if predecessor.get("mode") == "replacement" else "members"
    members = predecessor.get(member_key, [])
    for member in members:
        normalized = _validate_destination(
            member.get("destination"), f"{uid}.{member.get('id')}", control_paths
        )
        destinations.append((uid, str(member.get("id")), normalized))
    row = dict(predecessor)
    row[member_key] = [
        {**dict(member), **({"projection": projection} if member_key == "members" else {})}
        for member in members
    ]
    row["retired"] = True
    _need(
        _retired_destination_digest(row, snapshot) == _locked_destination_digest(row),
        "local_drift",
        f"{uid}: retained destination differs from its predecessor lock; destination files are preserved",
    )
    return row


def _carry_retired_row(
    row: Mapping[str, object],
    snapshot: _Snapshot,
    control_paths: Sequence[str],
    destinations: list[tuple[str, str, str]],
) -> dict[str, object]:
    """Carry an unchanged lock-only retirement descriptor into the next candidate."""
    uid = str(row.get("id"))
    _need(
        bool(row.get("retired", False)),
        "invalid_lock",
        f"{uid}: only a retired predecessor row can be carried",
    )
    _need(
        _retired_destination_digest(row, snapshot) == _locked_destination_digest(row),
        "local_drift",
        f"{uid}: retained destination differs from its locked descriptor",
    )
    member_key = "replacement_members" if row.get("mode") == "replacement" else "members"
    members = row.get(member_key, [])
    for member in members:
        normalized = _validate_destination(
            member.get("destination"), f"{uid}.{member.get('id')}", control_paths
        )
        destinations.append((uid, str(member.get("id")), normalized))
    carried = dict(row)
    carried[member_key] = [dict(member) for member in members]
    return carried


def _review_decision_matches(
    decision: Mapping[str, object] | None,
    upstream_digest: str,
    destination_digest: str,
) -> bool:
    return (
        decision is not None
        and decision.get("reviewed_upstream_digest") == upstream_digest
        and decision.get("reviewed_destination_digest") == destination_digest
    )


def _applied_verified_layout(decision: Mapping[str, object] | None) -> bool:
    """Return whether a decision attests a complete applied layout review.

    The attestation is distinct from the marker: it only counts when the
    decision is ``applied`` and the reviewed source/result digests match the
    prepared bytes (checked by the caller), so a stale or unreviewed marker
    never authorizes a candidate.
    """
    return (
        decision is not None
        and decision.get("decision") == "applied"
        and decision.get("verified_layout") == RULE_LAYOUT_VALUE
    )


