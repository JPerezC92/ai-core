"""Candidate-lock construction and the stdout-only propose-lock command."""

from __future__ import annotations

import argparse
from typing import Mapping, Sequence

import os
import sys

import yaml

from adoption_constants import _REVIEW_MODES, STORY_UNIT_KIND
from adoption_contracts import (
    CatalogDocument,
    LockDocument,
    LockMember,
    LockUnit,
    _Snapshot,
    _content_projection,
    _fail,
    _need,
    _strip_comments,
)
from adoption_content import (
    _destination_unit_digest,
    _fragment,
    _member_digest_at,
    _protected_documents_violation,
    _snapshot_member_digest,
    _story_index_collisions,
    _target_destination_changed,
    _unit_upstream_digest,
)
from adoption_digests import (
    _retired_descriptor_digest,
    _sha256,
    _snapshot_digest,
    assertion_list_digest,
    assertion_status_digest,
    declaration_unit_digest,
)
from adoption_git import (
    _GitRepo,
    _catalog_at,
    _catalog_blob_at,
    _catalog_digest_at,
    _resolve_adopter_repo,
    _resolve_catalog_path,
    _snapshot_for,
    _trusted_revision,
)
from adoption_loaders import (
    _load_catalog_bytes,
    _read_control_document,
    _read_path_bytes,
)
from adoption_mapping import (
    _catalog_transition,
    _catalog_unit_index,
    _check_destination_set,
    _control_paths,
    _declared_members,
    _validate_catalog_unit_framing,
    _validate_declaration_coverage,
    _validate_destination,
)
from adoption_policies import _destination_policy_violation
from adoption_reconciliation import (
    _applied_verified_layout,
    _carry_retired_row,
    _review_decision_matches,
    _review_transition_matches,
    _reviewed_unit_source_digest,
    _retired_row_from_predecessor,
)
from adoption_schema import (
    _validate_declaration_document,
    _validate_lock_document,
    _validate_review_document,
)

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
) -> LockUnit:
    projection = str(catalog_unit.get("sync_projection"))
    declared = _declared_members(catalog_unit, decl_unit, uid)
    members: list[LockMember] = []
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
) -> LockUnit:
    members: list[LockMember] = []
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
) -> LockUnit:
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


def _propose_lock_document(
    args: argparse.Namespace, snapshot: _Snapshot
) -> LockDocument:
    """Build one candidate v2 lock document; print nothing and write nothing.

    Shared builder behind ``propose-lock``. It emits the document to stdout
    only; content edits and lock acceptance remain the reviewed skill workflow.
    Every input is read from ``args``; the caller supplies the explicit
    adopter snapshot. Portable story collisions are diagnostics
    and stay on stderr, so every caller's stdout contract remains intact.
    Each control file (declaration, review, baseline lock, catalog) is read
    exactly once: the parsed rows and every emitted digest derive from the
    same bytes (protocol §3).
    """
    catalog_path = _resolve_catalog_path(str(args.catalog), str(args.upstream_repo))
    declaration, declaration_digest = _read_control_document(
        str(args.declaration),
        "invalid_declaration",
        "declaration",
        _validate_declaration_document,
    )
    review, review_digest = (
        _read_control_document(
            str(args.review),
            "invalid_declaration",
            "review",
            _validate_review_document,
        )
        if args.review
        else ({"schema_version": 2, "upstream_repository": "", "decisions": []}, _sha256(b""))
    )
    upstream = _GitRepo(str(args.upstream_repo))
    target, _diagnostic = _trusted_revision(upstream, None)
    catalog_bytes = _read_path_bytes(catalog_path, "invalid_mapping", "catalog")
    _need(
        catalog_bytes == _catalog_blob_at(upstream, target, catalog_path),
        "catalog_changed",
        "the supplied catalog bytes do not match the target revision",
    )
    # The file bytes were just proven identical to the trusted-revision blob,
    # so validating and parsing that single buffer preserves the original
    # file-path error label while keeping one read and one parse per control.
    catalog = _load_catalog_bytes(catalog_bytes, catalog_path)
    block = catalog.get("catalog")
    _need(
        isinstance(block, Mapping)
        and block.get("upstream_repository") == declaration.get("upstream_repository"),
        "repository_identity_mismatch",
        "catalog and declaration upstream_repository differ",
    )
    _need(
        not review.get("upstream_repository")
        or review.get("upstream_repository") == declaration.get("upstream_repository"),
        "repository_identity_mismatch",
        "review and declaration upstream_repository differ",
    )
    catalog_units, declaration_units = _validate_declaration_coverage(
        catalog, declaration, declaration.get("profile", {})
    )
    _validate_catalog_unit_framing(catalog_units, declaration_units)
    decision_map = {str(d.get("unit")): d for d in review.get("decisions", [])}
    baseline_lock: LockDocument | None = None
    baseline_lock_digest: str | None = None
    if args.lock and os.path.isfile(str(args.lock)):
        baseline_lock, baseline_lock_digest = _read_control_document(
            str(args.lock),
            "invalid_lock",
            "lock",
            _validate_lock_document,
        )
    accepted_catalog: CatalogDocument | None = None
    _need(
        baseline_lock is not None or not args.lock,
        "baseline_unavailable",
        "a supplied update lock is unreadable; initial enrollment must omit --lock",
    )
    _need(
        set(decision_map).issubset(set(catalog_units))
        if baseline_lock is None
        else True,
        "invalid_declaration",
        "initial-enrollment review references a unit absent from the target catalog",
    )
    if baseline_lock is None:
        _need(
            _review_transition_matches(
                review, None, target, declaration_digest
            ),
            "review_changed",
            "initial enrollment requires an explicit null-baseline transition bound to target and declaration",
        )
    if baseline_lock is not None:
        _need(
            baseline_lock.get("upstream_repository")
            in (None, declaration.get("upstream_repository")),
            "repository_identity_mismatch",
            "baseline lock upstream_repository differs from the declaration",
        )
        accepted = str(baseline_lock.get("accepted_source_commit"))
        accepted_catalog = _catalog_at(upstream, accepted, catalog_path)
        _validate_catalog_unit_framing(
            _catalog_unit_index(accepted_catalog),
            lock_units={
                str(row.get("id")): row for row in baseline_lock.get("units", [])
            },
        )
        _need(
            baseline_lock.get("accepted_catalog_digest")
            == _catalog_digest_at(upstream, accepted, catalog_path),
            "baseline_unavailable",
            "accepted catalog bytes do not reproduce accepted_catalog_digest",
        )
        _need(
            baseline_lock.get("accepted_snapshot_digest")
            == _snapshot_digest(
                str(baseline_lock.get("declaration_digest")),
                str(baseline_lock.get("review_digest")),
                baseline_lock.get("units", []),
            ),
            "baseline_unavailable",
            "baseline lock snapshot digest does not reproduce its recorded facts",
        )
    baseline = {
        str(row.get("id")): row
        for row in (baseline_lock or {}).get("units", [])
    }
    if baseline_lock is not None:
        accepted = str(baseline_lock.get("accepted_source_commit"))
        _need(
            upstream.is_ancestor(accepted, target),
            "baseline_unavailable",
            f"accepted commit {accepted} is not an ancestor of {target}",
        )
        assert accepted_catalog is not None and baseline_lock is not None
        accepted_units = _catalog_unit_index(accepted_catalog)
        _need(
            set(decision_map).issubset(
                set(accepted_units)
                | set(catalog_units)
                | {
                    uid
                    for uid, row in baseline.items()
                    if bool(row.get("retired", False))
                }
            ),
            "invalid_declaration",
                "review references a unit absent from both accepted and target catalogs",
        )
    if baseline_lock is not None and accepted_catalog is not None:
        accepted_revision = str(baseline_lock.get("accepted_source_commit"))
        accepted_catalog_units = _catalog_unit_index(accepted_catalog)
        for uid, baseline_row in baseline.items():
            if bool(baseline_row.get("retired", False)):
                continue
            if baseline_row.get("mode") == "not_applicable":
                continue
            accepted_unit = accepted_catalog_units.get(uid)
            _need(
                accepted_unit is not None,
                "baseline_unavailable",
                f"{uid}: accepted lock row has no accepted catalog unit",
            )
            expected_upstream = (
                assertion_list_digest(accepted_unit.get("assertions", []))
                if accepted_unit.get("sync_projection") == "assertions"
                else _unit_upstream_digest(upstream, accepted_revision, accepted_unit)
            )
            _need(
                baseline_row.get("accepted_upstream_digest") == expected_upstream,
                "baseline_unavailable",
                f"{uid}: accepted baseline upstream digest does not reproduce at {accepted_revision}",
            )
        for uid, baseline_row in baseline.items():
            _need(
                not (bool(baseline_row.get("retired", False)) and uid in catalog_units),
                "invalid_lock",
                f"{uid}: a retired lock unit cannot be reintroduced by the target catalog",
            )
        _need(
            _review_transition_matches(
                review, baseline_lock_digest, target, declaration_digest
            ),
            "review_changed",
            "every proposal against an accepted baseline requires a fresh transition bound to the baseline, target, and declaration",
        )
    catalog_change = (
        _catalog_transition(
            accepted_catalog,
            catalog,
            baseline_lock,
            declaration,
        )
        if accepted_catalog is not None and baseline_lock is not None
        else {"added_units": [], "removed_units": [], "changed_units": []}
    )
    control_paths = _control_paths(catalog)
    destinations: list[tuple[str, str, str]] = []
    rows: list[LockUnit] = []
    for uid, catalog_unit in catalog_units.items():
        decl_unit = declaration_units[uid]
        mode = str(decl_unit.get("mode"))
        projection = str(catalog_unit.get("sync_projection"))
        if mode == "not_applicable":
            rows.append({"id": uid, "mode": "not_applicable"})
            continue
        policy_violation = _destination_policy_violation(
            uid, catalog_unit, decl_unit, snapshot,
            declaration.get("test_runner"),
        )
        if policy_violation is not None:
            _fail("policy_violation", f"{uid}: {policy_violation}")
        protected = bool(catalog_unit.get("rule_documents"))
        if protected:
            protected_violation = _protected_documents_violation(
                uid, catalog_unit, decl_unit, upstream, target, snapshot
            )
            if protected_violation is not None:
                _fail("policy_violation", protected_violation)
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
        baseline_row = baseline.get(uid)
        if baseline_row is not None and baseline_row.get("mode") == "not_applicable":
            baseline_row = None
        upstream_changed = (
            baseline_row is None
            or target_upstream != baseline_row.get("accepted_upstream_digest")
        )
        destination_changed = _target_destination_changed(
            catalog_unit, decl_unit, baseline_row, snapshot, upstream, target
        )
        needs_review = mode in _REVIEW_MODES and (
            upstream_changed
            or destination_changed
        )
        decision = decision_map.get(uid)
        if needs_review or protected:
            _expected_dst = _destination_unit_digest(catalog_unit, decl_unit, snapshot)
            fresh = (
                _review_transition_matches(
                    review, baseline_lock_digest, target, declaration_digest
                )
                and _review_decision_matches(
                    decision,
                    target_upstream,
                    _expected_dst,
                )
                and (not protected or _applied_verified_layout(decision))
            )
            _need(
                fresh,
                "review_changed",
                f"{uid}: reconciliation needs a fresh transition-bound decision "
                f"and reviewed destination result"
                + (" with verified_layout" if protected else ""),
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
    if baseline_lock is not None and accepted_catalog is not None:
        for uid in catalog_change["removed_units"]:
            accepted_unit = _catalog_unit_index(accepted_catalog)[str(uid)]
            baseline_row = baseline.get(str(uid))
            _need(
                baseline_row is not None,
                "baseline_unavailable",
                f"{uid}: retired target unit has no predecessor lock row",
            )
            if baseline_row.get("mode") not in _REVIEW_MODES:
                continue
            _need(
                not baseline_row.get("retired", False),
                "invalid_lock",
                f"{uid}: an already-retired row cannot be retired again",
            )
            _need(
                baseline_row.get("accepted_upstream_digest")
                == _unit_upstream_digest(
                    upstream, str(baseline_lock.get("accepted_source_commit")), accepted_unit
                ),
                "baseline_unavailable",
                f"{uid}: predecessor upstream digest does not reproduce",
            )
            decision = decision_map.get(str(uid))
            retired_digest = _reviewed_unit_source_digest(
                upstream,
                target,
                None,
                str(baseline_row.get("accepted_upstream_digest")),
            )
            retired_row = _retired_row_from_predecessor(
                baseline_row,
                _content_projection(str(accepted_unit.get("sync_projection"))),
                snapshot,
                control_paths,
                destinations,
            )
            _need(
                _review_transition_matches(
                    review,
                    baseline_lock_digest,
                    target,
                    declaration_digest,
                )
                and _review_decision_matches(
                    decision, retired_digest, _retired_descriptor_digest(retired_row)
                )
                and decision is not None
                and decision.get("decision") in ("declined", "superseded"),
                "review_changed",
                f"{uid}: retired non-mirror unit needs a fresh declined/superseded decision; destination files are preserved",
            )
            rows.append(retired_row)
        for uid, baseline_row in baseline.items():
            if not baseline_row.get("retired", False) or uid in catalog_units:
                continue
            rows.append(
                _carry_retired_row(
                    baseline_row, snapshot, control_paths, destinations
                )
            )
    _check_destination_set(destinations)
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
