"""Catalog, declaration, review, lock, and registry document shape validation."""

from __future__ import annotations

import re
from typing import cast

import yaml

from adoption_constants import (
    COLLISION_POLICIES,
    DECLARATION_MODES,
    DESTINATION_POLICIES,
    LOCK_DIGEST_FIELDS,
    LOCK_MODES,
    PROFILE_MARKERS,
    PROJECTIONS,
    REVIEW_DECISIONS,
    RULE_DOCUMENT_SUFFIX,
    RULE_LAYOUT_VALUE,
    SYNC_PROJECTIONS,
    TEST_RUNNER_KEYS,
    TEST_RUNNER_SCOPE,
    _REVIEW_MODES,
)
from adoption_contracts import (
    CatalogDocument,
    DeclarationDocument,
    LockDocument,
    RegistryDocument,
    ReviewDocument,
    TestRunner,
    _fail,
    _field,
    _need,
    _normalize_source_path,
)
from adoption_digests import _is_digest

# The closed set of catalog install strategies. ``preserve`` marks a
# destination-owned member that is never converged with upstream content.
_INSTALL_STRATEGIES = ("copy", "merge", "preserve")


def _fields(record: object, where: str, code: str, *names: str) -> None:
    _need(isinstance(record, dict), code, f"{where} must be a mapping")
    for name in names:
        value = _field(record, name)
        _need(
            isinstance(value, str) and bool(value),
            code,
            f"{where}.{name} must be a non-empty string",
        )


def _mapping_list(
    value: object, where: str, code: str, *names: str
) -> list[dict[str, object]]:
    _need(isinstance(value, list) and bool(value), code, f"{where} must be a non-empty list")
    for index, item in enumerate(value):
        _fields(item, f"{where}[{index}]", code, *names)
    return value


def _parse_document_bytes(content: bytes, label: str, code: str) -> dict[str, object]:
    """Pure parser for one YAML document supplied by a Git object or file loader."""
    try:
        document = yaml.safe_load(content.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        _fail(code, f"cannot parse {label}: {exc}")
    _need(isinstance(document, dict), code, f"{label} must be a top-level mapping")
    return document


def _require_v2(document: dict[str, object], label: str, code: str) -> None:
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


def _member_source(member: dict[str, object]) -> str:
    """Return one catalog member's normalized source path."""
    return _normalize_source_path(str(member.get("source")))


def _covers_rule_document(path: str, source: str, projection: object) -> bool:
    """Return whether one member source covers a protected document path."""
    if projection == "tree":
        root = source.rstrip("/")
        return path == root or path.startswith(root + "/")
    return path == source


def _reject_ambiguous_protected_coverage(
    where: str, projection: object, sources: list[str]
) -> None:
    """Reject duplicate or overlapping sources before any protected projection.

    Unprotected units never reach this check. Equal file sources and overlapping
    tree roots would make one protected path resolve to more than one member.
    """
    for index, source in enumerate(sources):
        for other in sources[index + 1:]:
            if projection == "tree":
                left = source.rstrip("/")
                right = other.rstrip("/")
                shorter, longer = (left, right) if len(left) <= len(right) else (right, left)
                _need(
                    shorter != longer and not longer.startswith(shorter + "/"),
                    "invalid_mapping",
                    f"{where}: overlapping protected tree coverage: {left} and {right}",
                )
            else:
                _need(
                    source != other,
                    "invalid_mapping",
                    f"{where}: duplicate protected source coverage: {source}",
                )


def _rule_documents(
    unit: dict[str, object], where: str, projection: object, members: list[dict[str, object]]
) -> None:
    """Validate a protected unit's unique normalized, unambiguous rule paths.

    An omitted ``rule_documents`` key is unprotected. A present null, empty, or
    non-list value is malformed inventory and must not disable protection.
    """
    if "rule_documents" not in unit:
        return
    raw = unit.get("rule_documents")
    _need(
        projection in ("file", "guarded_file", "tree"),
        "invalid_mapping",
        f"{where}.rule_documents is valid only for file/guarded_file/tree units",
    )
    _need(
        isinstance(raw, list) and bool(raw),
        "invalid_mapping",
        f"{where}.rule_documents must be a non-empty list",
    )
    normalized: list[str] = []
    for index, document in enumerate(raw):
        _need(
            isinstance(document, str) and bool(document),
            "invalid_mapping",
            f"{where}.rule_documents[{index}] must be a non-empty string",
        )
        path = _normalize_source_path(document)
        _need(
            path.lower().endswith(RULE_DOCUMENT_SUFFIX),
            "invalid_mapping",
            f"{where}.rule_documents[{index}] must be a Markdown path: {document}",
        )
        _need(
            path not in normalized,
            "invalid_mapping",
            f"{where}.rule_documents[{index}] duplicated: {path}",
        )
        normalized.append(path)
    sources = [_member_source(member) for member in members]
    _reject_ambiguous_protected_coverage(where, projection, sources)
    for path in normalized:
        matches = [
            source for source in sources if _covers_rule_document(path, source, projection)
        ]
        _need(
            len(matches) == 1,
            "invalid_mapping",
            f"{where}.rule_documents path must match exactly one member source, "
            f"matched {len(matches)}: {path}",
        )


def _catalog_unit(unit: object, where: str, seen: set[str]) -> None:
    _fields(unit, where, "invalid_mapping", "id", "kind", "install_strategy")
    _need(unit["id"] not in seen, "invalid_mapping", f"{where}.id duplicated: {unit['id']}")
    seen.add(unit["id"])
    _need(
        unit["install_strategy"] in _INSTALL_STRATEGIES,
        "invalid_mapping",
        f"{where}.install_strategy must be one of {_INSTALL_STRATEGIES}",
    )
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
        _need(
            "rule_documents" not in unit,
            "invalid_mapping",
            f"{where}.rule_documents is invalid for assertion units",
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
        _rule_documents(unit, where, projection, members)
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


def _lock_member(
    member: object, where: str, seen: set[str], replacement: bool, retired: bool
) -> None:
    _fields(member, where, "invalid_lock", "id", "destination")
    _need(member["id"] not in seen, "invalid_lock", f"{where}.id duplicated: {member['id']}")
    seen.add(member["id"])
    if replacement:
        _need(
            "accepted_upstream_digest" not in member,
            "invalid_lock",
            f"{where}.accepted_upstream_digest is invalid for replacement members",
        )
        _need(
            member.get("projection") in PROJECTIONS,
            "invalid_lock",
            f"{where}.projection must be one of {PROJECTIONS}",
        )
        names = ("accepted_destination_digest",)
    else:
        _need(
            ("projection" not in member) if not retired else member.get("projection") in PROJECTIONS,
            "invalid_lock",
            f"{where}.projection is required and must be one of {PROJECTIONS} for retired ordinary members"
            if retired
            else f"{where}.projection is valid only for replacement members",
        )
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
    retired = unit.get("retired", False)
    _need(
        isinstance(retired, bool),
        "invalid_lock",
        f"{where}.retired must be a boolean when present",
    )
    if retired:
        _need(
            mode in _REVIEW_MODES,
            "invalid_lock",
            f"{where}: retired rows are limited to non-mirror review modes",
        )
    if mode == "not_applicable":
        _need(
            "members" not in unit and "replacement_members" not in unit,
            "invalid_lock",
            f"{where}: not_applicable units must not carry member facts",
        )
        return
    for name in ("declaration_unit_digest", "accepted_upstream_digest"):
        _need(
            _is_digest(unit.get(name)),
            "invalid_lock",
            f"{where}.{name} must be sha256:<hex>",
        )
    key = "replacement_members" if mode == "replacement" else "members"
    incompatible_key = "members" if mode == "replacement" else "replacement_members"
    _need(
        incompatible_key not in unit,
        "invalid_lock",
        f"{where}.{incompatible_key} is incompatible with mode {mode}",
    )
    rows = _mapping_list(
        unit.get(key), f"{where}.{key}", "invalid_lock", "id", "destination"
    )
    member_ids: set[str] = set()
    for index, member in enumerate(rows):
        _lock_member(
            member,
            f"{where}.{key}[{index}]",
            member_ids,
            mode == "replacement",
            bool(retired),
        )


def _validate_catalog_document(
    document: dict[str, object], label: str
) -> CatalogDocument:
    """Shape-validate a catalog already parsed from a file or Git blob."""
    _require_v2(document, label, "invalid_mapping")
    _fields(
        document.get("catalog"),
        f"{label}: catalog",
        "invalid_mapping",
        "upstream_repository",
    )
    units = document.get("units")
    _need(isinstance(units, list), "invalid_mapping", f"{label}: units must be a list")
    seen: set[str] = set()
    for index, unit in enumerate(units):
        _catalog_unit(unit, f"{label}: units[{index}]", seen)
    return cast(CatalogDocument, document)


def _validate_declaration_document(
    document: dict[str, object], label: str
) -> DeclarationDocument:
    """Shape-validate a declaration already parsed from a file or Git blob."""
    _require_v2(document, label, "invalid_declaration")
    _fields(document, label, "invalid_declaration", "upstream_repository")
    profile = document.get("profile")
    _need(
        isinstance(profile, dict),
        "invalid_declaration",
        f"{label}: profile must be a mapping",
    )
    for marker in PROFILE_MARKERS:
        _need(
            isinstance(profile.get(marker), bool),
            "invalid_declaration",
            f"{label}: profile.{marker} must be a boolean",
        )
    units = document.get("units")
    _need(isinstance(units, list), "invalid_declaration", f"{label}: units must be a list")
    seen: set[str] = set()
    for index, unit in enumerate(units):
        _declaration_unit(unit, f"{label}: units[{index}]", seen)
    raw_test_runner = document.get("test_runner")
    if raw_test_runner is not None:
        _need(
            isinstance(raw_test_runner, dict),
            "invalid_declaration",
            f"{label}: test_runner must be a mapping",
        )
        test_runner = cast(TestRunner, raw_test_runner)
        unknown = sorted(set(test_runner) - set(TEST_RUNNER_KEYS))
        _need(
            not unknown,
            "invalid_declaration",
            f"{label}: test_runner has unknown keys {unknown}",
        )
        if test_runner.get("no_tests") is True:
            for absent in ("commands", "executor", "scope"):
                _need(
                    absent not in test_runner,
                    "invalid_declaration",
                    f"{label}: test_runner.{absent} is invalid with no_tests: true",
                )
            for required in ("reviewer", "evidence"):
                _need(
                    isinstance(test_runner.get(required), str)
                    and bool(test_runner.get(required)),
                    "invalid_declaration",
                    f"{label}: test_runner.{required} must be a non-empty string",
                )
        else:
            commands = test_runner.get("commands")
            _need(
                isinstance(commands, list) and bool(commands),
                "invalid_declaration",
                f"{label}: test_runner.commands must be a non-empty list",
            )
            for index, command in enumerate(commands):
                _need(
                    isinstance(command, str) and bool(command),
                    "invalid_declaration",
                    f"{label}: test_runner.commands[{index}] must be a non-empty string",
                )
                _need(
                    isinstance(command, str)
                    and "*" not in command
                    and "?" not in command,
                    "invalid_declaration",
                    f"{label}: test_runner.commands[{index}] must be a literal "
                    "command without '*' or '?' wildcard metacharacters",
                )
            for required in ("executor", "reviewer", "evidence"):
                _need(
                    isinstance(test_runner.get(required), str)
                    and bool(test_runner.get(required)),
                    "invalid_declaration",
                    f"{label}: test_runner.{required} must be a non-empty string",
                )
            _need(
                test_runner.get("scope") == TEST_RUNNER_SCOPE,
                "invalid_declaration",
                f"{label}: test_runner.scope must be {TEST_RUNNER_SCOPE!r}",
            )
    return cast(DeclarationDocument, document)


def _validate_review_document(
    document: dict[str, object], label: str
) -> ReviewDocument:
    """Shape-validate a review while retaining legacy v2 review readability."""
    _require_v2(document, label, "invalid_declaration")
    _fields(document, label, "invalid_declaration", "upstream_repository")
    decisions = document.get("decisions")
    _need(
        isinstance(decisions, list),
        "invalid_declaration",
        f"{label}: decisions must be a list",
    )
    seen: set[str] = set()
    for index, decision in enumerate(decisions):
        where = f"{label}: decisions[{index}]"
        _fields(decision, where, "invalid_declaration", "unit", "reviewer")
        unit_id = str(decision.get("unit"))
        _need(
            unit_id not in seen,
            "invalid_declaration",
            f"{where}.unit duplicated: {unit_id}",
        )
        seen.add(unit_id)
        choice = decision.get("decision")
        _need(
            choice in REVIEW_DECISIONS,
            "invalid_declaration",
            f"{where}.decision must be one of {REVIEW_DECISIONS}",
        )
        if "verified_layout" in decision:
            _need(
                decision.get("verified_layout") == RULE_LAYOUT_VALUE,
                "invalid_declaration",
                f"{where}.verified_layout must be {RULE_LAYOUT_VALUE!r}",
            )
        for digest_name in (
            "reviewed_upstream_digest",
            "reviewed_destination_digest",
        ):
            if digest_name in decision:
                _need(
                    _is_digest(decision.get(digest_name)),
                    "invalid_declaration",
                    f"{where}.{digest_name} must be sha256:<hex>",
                )
    transition = document.get("transition")
    if transition is not None:
        transition_fields = (
            "baseline_lock_digest",
            "target_source_commit",
            "declaration_digest",
        )
        _need(
            isinstance(transition, dict)
            and set(transition) == set(transition_fields),
            "invalid_declaration",
            f"{label}: transition must contain exactly {transition_fields}",
        )
        for digest_name in ("declaration_digest",):
            _need(
                _is_digest(transition.get(digest_name)),
                "invalid_declaration",
                f"{label}: transition.{digest_name} must be sha256:<hex>",
            )
        _need(
            transition.get("baseline_lock_digest") is None
            or _is_digest(transition.get("baseline_lock_digest")),
            "invalid_declaration",
            f"{label}: transition.baseline_lock_digest must be null or sha256:<hex>",
        )
        _need(
            isinstance(transition.get("target_source_commit"), str)
            and re.fullmatch(r"[0-9a-f]{40}", str(transition.get("target_source_commit")))
            is not None,
            "invalid_declaration",
            f"{label}: transition.target_source_commit must be a full 40-character SHA",
        )
        for index, decision in enumerate(decisions):
            where = f"{label}: decisions[{index}]"
            _fields(
                decision,
                where,
                "invalid_declaration",
                "evidence",
                "reviewed_upstream_digest",
                "reviewed_destination_digest",
            )
    return cast(ReviewDocument, document)


def _validate_lock_document(document: dict[str, object], label: str) -> LockDocument:
    """Shape-validate a lock already parsed from a file or Git blob."""
    _require_v2(document, label, "invalid_lock")
    _fields(document, label, "invalid_lock", "accepted_source_commit")
    accepted = document.get("accepted_source_commit")
    _need(
        isinstance(accepted, str)
        and re.fullmatch(r"[0-9a-f]{40}", accepted) is not None,
        "invalid_lock",
        f"{label}: accepted_source_commit must be a full 40-character lowercase SHA",
    )
    for name in LOCK_DIGEST_FIELDS:
        _need(
            _is_digest(document.get(name)),
            "invalid_lock",
            f"{label}: {name} must be sha256:<hex>",
        )
    units = document.get("units")
    _need(isinstance(units, list), "invalid_lock", f"{label}: units must be a list")
    seen: set[str] = set()
    for index, unit in enumerate(units):
        _lock_unit(unit, f"{label}: units[{index}]", seen)
    return cast(LockDocument, document)


def _validate_registry_document(
    document: dict[str, object], label: str
) -> RegistryDocument:
    """Shape-validate a registry already parsed from a file or Git blob."""
    _require_v2(document, label, "invalid_declaration")
    _fields(document, label, "invalid_declaration", "upstream_repository")
    adopters = document.get("adopters")
    _need(
        isinstance(adopters, list),
        "invalid_declaration",
        f"{label}: adopters must be a list",
    )
    seen: set[str] = set()
    for index, adopter in enumerate(adopters):
        where = f"{label}: adopters[{index}]"
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
    return cast(RegistryDocument, document)
