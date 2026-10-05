"""Applicability evaluation, member mappings, coverage validation, and destination path protections."""

from __future__ import annotations

from typing import Mapping, Sequence, TypeAlias

from adoption_constants import PROTECTED_DECLARATION_MODES
from adoption_contracts import (
    CatalogTransition,
    CatalogTransitionRow,
    _fail,
    _field,
    _need,
    _normalize_source_path,
)

CatalogUnitIndex: TypeAlias = dict[str, Mapping[str, object]]
DeclarationUnitIndex: TypeAlias = dict[str, Mapping[str, object]]
LockUnitIndex: TypeAlias = dict[str, Mapping[str, object]]

# The debt register is destination-owned: it ships as a 0-entry template
# (``knowledge/debt.template.md``) and must never be byte-converged with an
# upstream register. A ``mirror`` declaration would import source debt, so it is
# rejected here for both ``propose-lock`` and ``check``. Only this unit is
# scoped; the ``plans``/``user-stories`` preserve units stay mirror-declarable.
DEBT_UNIT_ID = "knowledge-debt"


def evaluate_applicability(catalog_unit: object, profile: Mapping[str, object]) -> bool:
    """Return whether a catalog unit applies under the declaration profile (Section 1)."""
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


def _validate_declaration_coverage(
    catalog: Mapping[str, object],
    declaration: Mapping[str, object],
    profile: Mapping[str, object],
) -> tuple[CatalogUnitIndex, DeclarationUnitIndex]:
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
) -> tuple[CatalogUnitIndex, DeclarationUnitIndex, LockUnitIndex]:
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
            not bool(lock_units[uid].get("retired", False)),
            "invalid_lock",
            f"{uid}: a retired lock row cannot describe a current catalog unit",
        )
        _need(
            lock_units[uid].get("mode") == mode,
            "invalid_lock",
            f"{uid}: lock mode does not match the declaration",
        )
    extra_rows = set(lock_units) - set(catalog_units)
    for uid in extra_rows:
        _need(
            bool(lock_units[uid].get("retired", False)),
            "invalid_lock",
            f"{uid}: lock row is absent from the accepted catalog but is not retired",
        )
    return catalog_units, declaration_units, lock_units


def _validate_target_declaration(
    catalog: Mapping[str, object],
    declaration: Mapping[str, object],
    profile: Mapping[str, object],
) -> tuple[CatalogUnitIndex, DeclarationUnitIndex]:
    """Validate declared target rows without requiring new catalog coverage.

    Read-only assessment must first establish the accepted baseline.  A target
    catalog can legitimately contain a newly added unit before its owner has
    prepared a target-complete declaration; that absence is reportable review
    work, not malformed accepted evidence.
    """
    catalog_units = _catalog_unit_index(catalog)
    declaration_units = _declaration_unit_index(declaration)
    unknown = sorted(uid for uid in declaration_units if uid not in catalog_units)
    _need(
        not unknown,
        "invalid_declaration",
        f"declaration references unknown catalog units: {unknown}",
    )
    for uid, declaration_unit in declaration_units.items():
        mode = str(declaration_unit.get("mode"))
        applicable = evaluate_applicability(catalog_units[uid], profile)
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
    _validate_catalog_unit_framing(
        {uid: catalog_units[uid] for uid in declaration_units}, declaration_units
    )
    return catalog_units, declaration_units


def _validate_catalog_unit_framing(
    catalog_units: Mapping[str, Mapping[str, object]],
    declaration_units: Mapping[str, Mapping[str, object]] | None = None,
    lock_units: Mapping[str, Mapping[str, object]] | None = None,
) -> None:
    """Validate catalog-dependent declaration and accepted-lock member framing."""
    if declaration_units is not None:
        for uid, catalog_unit in catalog_units.items():
            declaration_unit = declaration_units[uid]
            mode = declaration_unit.get("mode")
            if uid == DEBT_UNIT_ID and mode == "mirror":
                _fail(
                    "invalid_declaration",
                    f"{uid}: the destination-owned debt register cannot be declared "
                    f"mirror; declare it adapted so destination debt is preserved",
                )
            if catalog_unit.get("rule_documents") and (
                mode not in PROTECTED_DECLARATION_MODES
            ):
                _fail(
                    "invalid_declaration",
                    f"{uid}: protected rule units permit only "
                    f"{PROTECTED_DECLARATION_MODES}",
                )
            if mode == "not_applicable":
                _need(
                    "members" not in declaration_unit
                    and "replacement_members" not in declaration_unit,
                    "invalid_declaration",
                    f"{uid}: not_applicable units must not declare members",
                )
            if catalog_unit.get("sync_projection") == "assertions":
                _need(
                    mode in ("mirror", "not_applicable")
                    and
                    "members" not in declaration_unit
                    and "replacement_members" not in declaration_unit,
                    "invalid_declaration",
                    f"{uid}: assertion units must not declare members",
                )
            if mode == "replacement":
                _need(
                    "members" not in declaration_unit
                    and isinstance(declaration_unit.get("replacement_members"), list),
                    "invalid_declaration",
                    f"{uid}: replacement units require replacement_members only",
                )
    if lock_units is not None:
        _need(
            set(catalog_units).issubset(set(lock_units)),
            "invalid_lock",
            "lock is missing accepted catalog units",
        )
        for uid, lock_unit in lock_units.items():
            if uid not in catalog_units:
                _need(
                    bool(lock_unit.get("retired", False)),
                    "invalid_lock",
                    f"{uid}: extra accepted-lock row must be retired",
                )
                continue
            _need(
                not bool(lock_unit.get("retired", False)),
                "invalid_lock",
                f"{uid}: retired lock row cannot describe an accepted catalog unit",
            )
        for uid, catalog_unit in catalog_units.items():
            lock_unit = lock_units[uid]
            mode = lock_unit.get("mode")
            if catalog_unit.get("sync_projection") == "assertions":
                if mode == "not_applicable":
                    _need(
                        "members" not in lock_unit
                        and "replacement_members" not in lock_unit,
                        "invalid_lock",
                        f"{uid}: not_applicable assertion rows must not carry members",
                    )
                else:
                    members = lock_unit.get("members")
                    _need(
                        mode == "mirror"
                        and isinstance(members, list)
                        and len(members) == 1
                        and members[0].get("id") == "assertions"
                        and "replacement_members" not in lock_unit,
                        "invalid_lock",
                        f"{uid}: assertion units require one assertions member in a mirror row",
                    )
            if mode == "replacement":
                _need(
                    "members" not in lock_unit
                    and isinstance(lock_unit.get("replacement_members"), list),
                    "invalid_lock",
                    f"{uid}: replacement rows require replacement_members only",
                )


def _catalog_unit_index(catalog: Mapping[str, object]) -> CatalogUnitIndex:
    return {
        str(unit.get("id")): unit
        for unit in catalog.get("units", [])
        if isinstance(unit, Mapping)
    }


def _declaration_unit_index(
    declaration: Mapping[str, object],
) -> DeclarationUnitIndex:
    return {
        str(unit.get("id")): unit
        for unit in declaration.get("units", [])
        if isinstance(unit, Mapping)
    }


def _catalog_transition(
    accepted_catalog: Mapping[str, object],
    target_catalog: Mapping[str, object],
    accepted_lock: Mapping[str, object],
    target_declaration: Mapping[str, object],
) -> CatalogTransition:
    """Describe catalog transitions from locked accepted outcomes to target intent."""
    accepted_units = _catalog_unit_index(accepted_catalog)
    target_units = _catalog_unit_index(target_catalog)
    accepted_modes = {
        str(row.get("id")): row for row in accepted_lock.get("units", [])
    }
    target_modes = _declaration_unit_index(target_declaration)
    target_profile = target_declaration.get("profile", {})
    added = sorted(set(target_units) - set(accepted_units))
    removed = sorted(set(accepted_units) - set(target_units))
    changed: list[CatalogTransitionRow] = []
    for unit_id in sorted(set(accepted_units) & set(target_units)):
        old = accepted_units[unit_id]
        new = target_units[unit_id]
        accepted_row = accepted_modes.get(unit_id)
        _need(
            accepted_row is not None,
            "baseline_unavailable",
            f"{unit_id}: accepted catalog unit has no accepted lock row",
        )
        old_members = {
            str(member.get("id")): member
            for member in old.get("members", [])
            if isinstance(member, Mapping)
        }
        new_members = {
            str(member.get("id")): member
            for member in new.get("members", [])
            if isinstance(member, Mapping)
        }
        added_members = sorted(set(new_members) - set(old_members))
        removed_members = sorted(set(old_members) - set(new_members))
        changed_members = sorted(
            member_id
            for member_id in set(old_members) & set(new_members)
            if old_members[member_id] != new_members[member_id]
        )
        # A v2 lock records the accepted applicability outcome through its
        # mode, but does not archive a declaration profile.  Do not invent one
        # from the target declaration when reporting a transition.
        old_applicable = accepted_row.get("mode") != "not_applicable"
        new_applicable = evaluate_applicability(new, target_profile)
        structural_change = (
            old != new
            or old_applicable != new_applicable
            or accepted_row.get("mode")
            != target_modes.get(unit_id, {}).get("mode")
        )
        if structural_change:
            changed.append(
                {
                    "id": unit_id,
                    "added_members": added_members,
                    "removed_members": removed_members,
                    "changed_members": changed_members,
                    "applicability_changed": old.get("applicability")
                    != new.get("applicability"),
                    "accepted_applicable": old_applicable,
                    "target_applicable": new_applicable,
                    "accepted_mode": accepted_row.get("mode"),
                    "target_mode": target_modes.get(unit_id, {}).get("mode"),
                }
            )
    return {"added_units": added, "removed_units": removed, "changed_units": changed}


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


def _rule_document_destination(
    catalog_unit: Mapping[str, object],
    decl_unit: Mapping[str, object],
    rule_document: str,
) -> str:
    """Map one protected source path to its destination through declared members.

    The path is resolved only through the unit's ordinary file/tree member
    mappings; arbitrary destination paths are never scanned. A tree member maps
    the relative remainder beneath its declared destination root, and a
    file/guarded_file member must match the rule document exactly.
    """
    uid = str(catalog_unit.get("id"))
    projection = str(catalog_unit.get("sync_projection"))
    members = [
        member
        for member in catalog_unit.get("members", []) or []
        if isinstance(member, Mapping)
    ]
    declared = _declared_members(catalog_unit, decl_unit, uid)
    matches: list[Mapping[str, object]] = []
    if projection == "tree":
        for member in members:
            source = _normalize_source_path(str(member.get("source")))
            root = source.rstrip("/")
            if rule_document == source or rule_document.startswith(root + "/"):
                matches.append(member)
    else:
        for member in members:
            if _normalize_source_path(str(member.get("source"))) == rule_document:
                matches.append(member)
    # Ambiguous protected paths have no first-match fallback. Zero matches and
    # overlapping tree or duplicate file coverage both fail closed.
    if len(matches) != 1:
        _fail(
            "invalid_mapping",
            f"{uid}: rule document {rule_document} must match exactly one member "
            f"source, matched {len(matches)}",
        )
    member = matches[0]
    if projection == "tree":
        source = _normalize_source_path(str(member.get("source")))
        destination_root = declared[str(member.get("id"))]
        relative = rule_document[len(source):].lstrip("/")
        if not relative:
            return destination_root
        return f"{destination_root.rstrip('/')}/{relative}"
    return declared[str(member.get("id"))]
