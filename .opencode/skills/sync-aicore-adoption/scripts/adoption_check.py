"""Compliance evaluation and the read-only check command."""

from __future__ import annotations

import argparse
import os
import json

from typing import Callable, Mapping

from adoption_constants import (
    PROTECTED_DECLARATION_MODES,
    _BLOCKING_DISPOSITIONS,
    _REVIEW_MODES,
    STORY_UNIT_KIND,
)
from adoption_contracts import CheckReport, CheckUnitReport, _Snapshot, _need
from adoption_content import (
    _destination_unit_digest,
    _protected_documents_violation,
    _story_index_collisions,
    _target_destination_changed,
    _unit_upstream_digest,
)
from adoption_digests import (
    _locked_destination_digest,
    _retired_descriptor_digest,
    _sha256,
    _snapshot_digest,
    assertion_list_digest,
    declaration_unit_digest,
)
from adoption_git import (
    _GitRepo,
    _catalog_at,
    _catalog_digest_at,
    _resolve_adopter_repo,
    _resolve_catalog_path,
    _snapshot_for,
    _trusted_revision,
)
from adoption_loaders import _read_control_document, load_catalog
from adoption_schema import (
    _validate_declaration_document,
    _validate_lock_document,
    _validate_review_document,
)
from adoption_mapping import (
    _catalog_transition,
    _catalog_unit_index,
    _check_destination_set,
    _control_paths,
    _declaration_unit_index,
    _validate_catalog_unit_framing,
    _validate_coverage,
    _validate_destination,
    _validate_target_declaration,
)
from adoption_policies import _destination_policy_violation
from adoption_reconciliation import (
    _applied_verified_layout,
    _debt_mirror_disposition,
    _disposition,
    _review_decision_matches,
    _reviewed_unit_source_digest,
    _retired_destination_digest,
)

def _accepted_protected_drift(
    accepted_catalog_units: Mapping[str, Mapping[str, object]],
    accepted_declaration_units: Mapping[str, Mapping[str, object]],
    upstream: _GitRepo,
    accepted: str,
    snapshot: _Snapshot,
) -> dict[str, str]:
    """Return accepted protected-document violations keyed by unit id.

    The comparison uses the accepted catalog, accepted member mappings, and
    accepted source revision. Target membership, dropped protection, and
    removed units must not skip it.
    """
    violations: dict[str, str] = {}
    for uid, accepted_unit in accepted_catalog_units.items():
        if not accepted_unit.get("rule_documents"):
            continue
        accepted_decl = accepted_declaration_units.get(uid)
        if accepted_decl is None or str(accepted_decl.get("mode")) == "not_applicable":
            continue
        violation = _protected_documents_violation(
            uid,
            accepted_unit,
            accepted_decl,
            upstream,
            accepted,
            snapshot,
        )
        if violation is not None:
            violations[uid] = violation
    return violations


def _check_report(
    declaration_path: str,
    lock_path: str,
    review_path: str | None,
    catalog_path: str,
    upstream: _GitRepo,
    target: str,
    diagnostic: bool,
    snapshot_factory: Callable[[], _Snapshot],
) -> CheckReport:
    """Build the compliance report shared by ``check`` and ``verify-all``."""
    # Validate every current v2 control document before reading the accepted
    # historical catalog. This preserves the upgrade-only contract even when
    # the accepted commit is no longer available in the local upstream clone.
    declaration, declaration_bytes_digest = _read_control_document(
        declaration_path,
        "invalid_declaration",
        "declaration",
        _validate_declaration_document,
    )
    lock, _lock_digest = _read_control_document(
        lock_path, "invalid_lock", "lock", _validate_lock_document
    )
    if review_path:
        review, current_review_digest = _read_control_document(
            review_path,
            "invalid_declaration",
            "review",
            _validate_review_document,
        )
    else:
        review = {"schema_version": 2, "upstream_repository": "", "decisions": []}
        current_review_digest = _sha256(b"")
    # Validate catalog schema before Git-tree resolution so a v1 catalog
    # reports schema_upgrade_required rather than catalog_changed.
    if os.path.isfile(catalog_path):
        load_catalog(catalog_path)
    catalog = _catalog_at(upstream, target, catalog_path)
    accepted = str(lock.get("accepted_source_commit"))
    _need(
        upstream.is_ancestor(accepted, target),
        "baseline_unavailable",
        f"accepted commit {accepted} is not an ancestor of {target}",
    )
    snapshot = snapshot_factory()
    _need(
        lock.get("declaration_digest") == declaration_bytes_digest,
        "declaration_changed",
        f"{declaration_path}: declaration_digest does not match the declaration bytes",
    )
    _need(
        lock.get("review_digest") == current_review_digest,
        "review_changed",
        f"{review_path or '<no review>'}: review_digest does not match the review bytes",
    )
    accepted_catalog = _catalog_at(upstream, accepted, catalog_path)
    accepted_declaration = declaration
    _need(
        lock.get("accepted_catalog_digest")
        == _catalog_digest_at(upstream, accepted, catalog_path),
        "catalog_changed",
        f"{catalog_path}: accepted_catalog_digest does not match the catalog at "
        f"{accepted}",
    )
    accepted_block = accepted_catalog.get("catalog")
    target_block = catalog.get("catalog")
    _need(
        isinstance(accepted_block, Mapping)
        and isinstance(target_block, Mapping)
        and accepted_block.get("upstream_repository")
        == accepted_declaration.get("upstream_repository")
        and target_block.get("upstream_repository")
        == declaration.get("upstream_repository")
        and lock.get("upstream_repository")
        in (None, accepted_declaration.get("upstream_repository"))
        and (
            not review.get("upstream_repository")
            or review.get("upstream_repository") == declaration.get("upstream_repository")
        ),
        "repository_identity_mismatch",
        "catalog, declaration, review, and lock repository identities differ",
    )
    _validate_coverage(
        accepted_catalog,
        accepted_declaration,
        lock,
        accepted_declaration.get("profile", {}),
    )
    accepted_catalog_units = _catalog_unit_index(accepted_catalog)
    accepted_declaration_units = _declaration_unit_index(accepted_declaration)
    accepted_lock_units = {
        str(row.get("id")): row for row in lock.get("units", [])
    }
    _validate_catalog_unit_framing(
        accepted_catalog_units, accepted_declaration_units, accepted_lock_units
    )
    for unit_id, accepted_unit in accepted_catalog_units.items():
        accepted_mode = str(accepted_declaration_units[unit_id].get("mode"))
        if accepted_mode == "not_applicable":
            continue
        row = accepted_lock_units[unit_id]
        _need(
            row.get("declaration_unit_digest")
            == declaration_unit_digest(
                accepted_mode,
                accepted_declaration_units[unit_id].get("members", []),
                accepted_declaration_units[unit_id].get("replacement_members", []),
            ),
            "invalid_lock",
            f"{unit_id}: accepted declaration mapping digest does not reproduce",
        )
        accepted_upstream_digest = (
            assertion_list_digest(accepted_unit.get("assertions", []))
            if accepted_unit.get("sync_projection") == "assertions"
            else _unit_upstream_digest(upstream, accepted, accepted_unit)
        )
        _need(
            row.get("accepted_upstream_digest") == accepted_upstream_digest,
            "invalid_lock",
            f"{unit_id}: accepted upstream digest does not reproduce at {accepted}",
        )
    expected_snapshot_digest = _snapshot_digest(
        str(lock.get("declaration_digest")),
        str(lock.get("review_digest")),
        lock.get("units", []),
    )
    _need(
        lock.get("accepted_snapshot_digest") == expected_snapshot_digest,
        "invalid_lock",
        "accepted_snapshot_digest does not reproduce from the lock rows, "
        "declaration_digest, and review_digest",
    )
    # Pre-edit assessment validates every declared target row but tolerates
    # accepted-baseline-only declarations: a unit removed from the target
    # catalog still appears in the unchanged accepted declaration and is
    # reported through catalog_transition.removed_units. Candidate acceptance
    # enforces complete target coverage in propose-lock.
    target_catalog_units = _catalog_unit_index(catalog)
    target_declaration_scope = {
        **declaration,
        "units": [
            unit
            for unit in declaration.get("units", [])
            if str(unit.get("id")) in target_catalog_units
        ],
    }
    if accepted == target:
        # Same snapshot: the declaration is the target-complete candidate, so
        # enforce strict applicability consistency.
        _, target_declaration_units = _validate_target_declaration(
            catalog, target_declaration_scope, declaration.get("profile", {})
        )
    else:
        # Pre-edit path: the accepted declaration mode reflects accepted
        # applicability and is enforced by the accepted-side coverage check.
        # Incoming protected modes are pending conversion, not a fatal
        # rejection of the accepted ownership declaration. Same-snapshot
        # checks above still apply target framing strictly.
        target_declaration_units = {
            str(unit.get("id")): unit for unit in target_declaration_scope["units"]
        }
    for uid, accepted_row in accepted_lock_units.items():
        _need(
            not (
                bool(accepted_row.get("retired", False))
                and uid in target_catalog_units
            ),
            "invalid_lock",
            f"{uid}: a retired lock unit cannot be reintroduced by the target catalog",
        )
    control_paths = _control_paths(catalog)
    destinations: list[tuple[str, str, str]] = []
    for uid, row in accepted_lock_units.items():
        if bool(row.get("retired", False)) or row.get("mode") == "not_applicable":
            continue
        member_key = "replacement_members" if row.get("mode") == "replacement" else "members"
        for member in row.get(member_key, []):
            normalized = _validate_destination(
                member.get("destination"), f"{uid}.{member.get('id')}", control_paths
            )
            destinations.append((uid, str(member.get("id")), normalized))
    for uid, row in accepted_lock_units.items():
        if not bool(row.get("retired", False)):
            continue
        member_key = "replacement_members" if row.get("mode") == "replacement" else "members"
        for member in row.get(member_key, []):
            normalized = _validate_destination(
                member.get("destination"), f"{uid}.{member.get('id')}", control_paths
            )
            destinations.append((uid, str(member.get("id")), normalized))
    _check_destination_set(destinations)
    decisions = {str(d.get("unit")): d for d in review.get("decisions", [])}
    known_review_units = (
        set(accepted_catalog_units)
        | set(target_catalog_units)
        | {
            uid
            for uid, row in accepted_lock_units.items()
            if bool(row.get("retired", False))
        }
    )
    unknown_decisions = sorted(set(decisions) - known_review_units)
    _need(
        not unknown_decisions,
        "invalid_declaration",
        f"review references unknown catalog units: {unknown_decisions}",
    )
    catalog_change = _catalog_transition(
        accepted_catalog,
        catalog,
        lock,
        declaration,
    )
    transition = review.get("transition")
    transition_metadata_matches = (
        isinstance(transition, Mapping)
        and transition.get("target_source_commit") == accepted
        and transition.get("declaration_digest") == lock.get("declaration_digest")
    )
    if isinstance(transition, Mapping):
        _need(
            transition_metadata_matches,
            "review_changed",
            "accepted review transition does not bind the accepted source and declaration",
        )
        for uid, decision in decisions.items():
            accepted_unit = accepted_catalog_units.get(uid)
            accepted_decl = accepted_declaration_units.get(uid)
            accepted_row = accepted_lock_units.get(uid)
            retired = accepted_row is not None and bool(accepted_row.get("retired", False))
            accepted_members = (
                accepted_row.get("replacement_members", [])
                if accepted_row is not None and accepted_row.get("mode") == "replacement"
                else accepted_row.get("members", [])
                if accepted_row is not None
                else []
            )
            accepted_destination_digest = (
                _retired_descriptor_digest(accepted_row)
                if retired
                else str(next(iter(accepted_members), {}).get("accepted_destination_digest"))
                if accepted_unit is not None
                and accepted_unit.get("sync_projection") == "assertions"
                else _locked_destination_digest(accepted_row)
                if accepted_row is not None
                else ""
            )
            accepted_source_digest = _reviewed_unit_source_digest(
                upstream,
                accepted,
                None if retired else accepted_unit,
                str(accepted_row.get("accepted_upstream_digest"))
                if accepted_row is not None
                else None,
            )
            _need(
                accepted_row is not None
                and (retired or (accepted_unit is not None and accepted_decl is not None))
                and _review_decision_matches(
                    decision,
                    accepted_source_digest,
                    accepted_destination_digest,
                ),
                "review_changed",
                f"{uid}: accepted review decision does not bind the locked source and destination result",
            )
    accepted_protected_violations = _accepted_protected_drift(
        accepted_catalog_units,
        accepted_declaration_units,
        upstream,
        accepted,
        snapshot,
    )
    results: list[CheckUnitReport] = []
    collisions: list[str] = []
    blocking: list[str] = []
    added_ids = set(catalog_change["added_units"])
    changed_ids = {str(row.get("id")) for row in catalog_change["changed_units"]}
    for uid in catalog_change["added_units"]:
        # Accepted coverage forbids declaration units outside the accepted
        # catalog, so an added unit is never declared and always needs the
        # unmapped review report below.
        results.append(
            {
                "id": uid,
                "mode": None,
                "upstream_delta": "changed",
                "destination_delta": None,
                "disposition": "review_required",
            }
        )
        blocking.append(f"{uid}: review_required")
    for uid, catalog_unit in target_catalog_units.items():
        if uid not in target_declaration_units:
            continue
        decl_unit = target_declaration_units[uid]
        mode = str(decl_unit.get("mode"))
        if mode == "not_applicable":
            disposition = (
                "baseline_advance_required"
                if uid in changed_ids or uid in added_ids
                else "not_applicable"
            )
            results.append(
                {
                    "id": uid,
                    "mode": mode,
                    "upstream_delta": None,
                    "destination_delta": None,
                    "disposition": disposition,
                }
            )
            if disposition in _BLOCKING_DISPOSITIONS:
                blocking.append(f"{uid}: {disposition}")
            continue
        projection = str(catalog_unit.get("sync_projection"))
        # Accepted coverage guarantees a lock row for every declared unit, and
        # accepted declaration modes already equal their lock modes, so a
        # not-applicable row can never reach this non-not-applicable path.
        lock_row = accepted_lock_units[uid]
        if mode != "replacement" and accepted != target:
            declared_member_ids = {
                str(member.get("id")) for member in (decl_unit.get("members") or [])
            }
            target_member_ids = {
                str(member.get("id")) for member in catalog_unit.get("members", [])
            }
            if declared_member_ids != target_member_ids:
                # The accepted declaration maps the accepted member set; a
                # target member addition/removal is unmapped pre-edit, so report
                # it for review without inventing a destination result or
                # running policy/mapping checks that require a complete mapping.
                # Accepted protected drift was already evaluated and wins.
                disposition = (
                    "local_drift"
                    if uid in accepted_protected_violations
                    else "review_required"
                )
                results.append(
                    {
                        "id": uid,
                        "mode": mode,
                        "upstream_delta": "changed",
                        "destination_delta": None,
                        "disposition": disposition,
                    }
                )
                blocking.append(f"{uid}: {disposition}")
                continue
        protected = bool(catalog_unit.get("rule_documents"))
        if (
            protected
            and accepted != target
            and mode not in PROTECTED_DECLARATION_MODES
        ):
            # Incoming protection on a historically allowed ownership mode is
            # pending conversion. Replacement and destination-owned mappings
            # are not protected destinations and must not fatal-resolve.
            protected_violation = None
        elif protected:
            protected_violation = _protected_documents_violation(
                uid, catalog_unit, decl_unit, upstream, target, snapshot
            )
        else:
            protected_violation = None
        accepted_protected_violation = (
            accepted_protected_violations.get(uid) if accepted != target else None
        )
        policy_violation = _destination_policy_violation(
            uid, catalog_unit, decl_unit, snapshot,
            declaration.get("test_runner"),
        )
        if projection == "assertions":
            target_digest = assertion_list_digest(catalog_unit.get("assertions", []))
            upstream_changed = (
                target_digest != lock_row.get("accepted_upstream_digest")
            )
            destination_changed = _target_destination_changed(
                catalog_unit, decl_unit, lock_row, snapshot, upstream, target
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
            target_digest = _unit_upstream_digest(upstream, target, catalog_unit)
            upstream_changed = (
                target_digest != lock_row.get("accepted_upstream_digest")
            )
            destination_changed = _target_destination_changed(
                catalog_unit, decl_unit, lock_row, snapshot, upstream, target
            )
        decision = decisions.get(uid)
        needs_review = mode in _REVIEW_MODES and (
            upstream_changed or destination_changed
        )
        result_digest = _destination_unit_digest(catalog_unit, decl_unit, snapshot)
        source_digest = _reviewed_unit_source_digest(
            upstream,
            target,
            catalog_unit,
            str(lock_row.get("accepted_upstream_digest")),
        )
        fresh_decision = (
            transition_metadata_matches
            and _review_decision_matches(decision, source_digest, result_digest)
            and (not protected or _applied_verified_layout(decision))
        )
        disposition = _disposition(mode, upstream_changed, destination_changed)
        debt_mirror = _debt_mirror_disposition(uid, mode)
        if debt_mirror is not None:
            disposition = debt_mirror
        elif policy_violation is not None:
            disposition = "policy_violation"
        elif accepted_protected_violation is not None:
            disposition = "local_drift"
        elif protected_violation is not None:
            disposition = "policy_violation" if accepted == target else "review_required"
        elif protected and not fresh_decision:
            disposition = "review_required"
        elif needs_review:
            disposition = (
                "baseline_advance_required" if fresh_decision else "review_required"
            )
        elif disposition == "current" and (
            accepted != target or bool(catalog_change["added_units"])
            or bool(catalog_change["removed_units"])
            or bool(catalog_change["changed_units"])
        ):
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
    for uid in catalog_change["removed_units"]:
        # A removed unit is present in the accepted catalog, so accepted
        # coverage guarantees its catalog unit, declaration mapping, and lock
        # row all exist.
        accepted_unit = accepted_catalog_units[uid]
        accepted_decl_unit = accepted_declaration_units[uid]
        accepted_row = accepted_lock_units[uid]
        mode = str(accepted_row.get("mode"))
        if mode == "not_applicable":
            destination_delta = None
        else:
            destination_delta = (
                "changed"
                if _target_destination_changed(
                    accepted_unit,
                    accepted_decl_unit,
                    accepted_row,
                    snapshot,
                    upstream,
                    target,
                )
                else "unchanged"
            )
        disposition = (
            "local_drift"
            if uid in accepted_protected_violations
            else "review_required"
            if mode in _REVIEW_MODES
            else "baseline_advance_required"
        )
        results.append(
            {
                "id": uid,
                "mode": mode,
                "upstream_delta": "changed",
                "destination_delta": destination_delta,
                "disposition": disposition,
            }
        )
        blocking.append(f"{uid}: {disposition}")
    for uid, row in accepted_lock_units.items():
        if not row.get("retired", False):
            continue
        destination_changed = (
            _retired_destination_digest(row, snapshot) != _locked_destination_digest(row)
        )
        disposition = "local_drift" if destination_changed else "current"
        results.append(
            {
                "id": uid,
                "mode": row.get("mode"),
                "retired": True,
                "upstream_delta": None,
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
        "catalog_transition": catalog_change,
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
