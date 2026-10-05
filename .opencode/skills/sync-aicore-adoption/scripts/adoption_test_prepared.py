"""Shared prepared-review, digest, and index-binding helpers for adoption tests.

This is a non-collected support module (``adoption_test_*``). It holds the
review-, digest-, and index-preparation helpers shared by the concern-scoped
adoption test modules. It defines no collected test class.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import yaml

from adoption_constants import RULE_LAYOUT_VALUE
from adoption_content import _destination_unit_digest, _unit_upstream_digest
from adoption_contracts import ProjectedEntry, _strip_comments
from adoption_digests import (
    assertion_status_digest,
    member_digest,
    unit_digest,
)
from adoption_git import _GitRepo, _IndexSnapshot, _RevisionSnapshot
from adoption_loaders import _raw_file_digest
from adoption_test_acceptance_data import RULE_NOTICE_CASES, RuleNoticeCase
from adoption_test_data import EMPTY_REVIEW, review_with_transition
from adoption_test_repos import AdopterFixture, EngineTestCase


def _bind_review_to_baseline(
    case: EngineTestCase, fixture: dict[str, object]
) -> None:
    """Rewrite the review with a transition bound to the current baseline lock.

    ``propose-lock`` never re-verifies the baseline lock's ``review_digest``, so
    a fresh transition is enough for the proposal path; the lock's own review
    digest is only re-verified by ``check`` after a candidate is installed.
    """
    fixture["review"].write_text(
        review_with_transition(
            EMPTY_REVIEW,
            case.rev(fixture["upstream"]),
            fixture["declaration"].read_text(encoding="utf-8"),
            _raw_file_digest(str(fixture["lock"])),
        ),
        encoding="utf-8",
    )
    fixture["adopter_rev"] = case.commit(
        fixture["adopter"], "fresh transition review"
    )


def _write_prepared_review(
    case: EngineTestCase,
    fixture: AdopterFixture,
    unit_id: str,
    decision: str = "applied",
    *,
    verified_layout: str | None = None,
    reviewed_upstream_digest: str | None = None,
    reviewed_destination_digest: str | None = None,
    baseline_lock_digest: str | None = None,
    target_source_commit: str | None = None,
    declaration_digest: str | None = None,
) -> None:
    """Record one fresh transition-bound decision over the prepared snapshot.

    The reviewed destination digest is read from the explicit adopter revision
    that holds the prepared bytes, so altering those bytes after approval makes
    this decision stop matching. ``verified_layout`` records the protected
    two-section attestation only when supplied. The source, result, and
    transition digests default to the current fixture state; each keyword
    override replaces exactly one field so stale-decision cases can be built.
    """
    catalog = yaml.safe_load(fixture["catalog"].read_text(encoding="utf-8"))
    declaration = yaml.safe_load(fixture["declaration"].read_text(encoding="utf-8"))
    unit = next(item for item in catalog["units"] if item["id"] == unit_id)
    declaration_unit = next(
        item for item in declaration["units"] if item["id"] == unit_id
    )
    target = case.rev(fixture["upstream"])
    source = _unit_upstream_digest(_GitRepo(str(fixture["upstream"])), target, unit)
    result = _destination_unit_digest(
        unit,
        declaration_unit,
        _RevisionSnapshot(
            _GitRepo(str(fixture["adopter"])), str(fixture["adopter_rev"])
        ),
    )
    decision_document: dict[str, object] = {
        "unit": unit_id,
        "decision": decision,
        "reviewer": "reviewer",
        "evidence": (
            "Reviewed prepared core requirement and destination business rule."
        ),
        "reviewed_upstream_digest": reviewed_upstream_digest or source,
        "reviewed_destination_digest": reviewed_destination_digest or result,
    }
    if verified_layout is not None:
        decision_document["verified_layout"] = verified_layout
    document = {
        "schema_version": 2,
        "upstream_repository": catalog["catalog"]["upstream_repository"],
        "transition": {
            "baseline_lock_digest": (
                baseline_lock_digest or _raw_file_digest(str(fixture["lock"]))
            ),
            "target_source_commit": target_source_commit or target,
            "declaration_digest": (
                declaration_digest or _raw_file_digest(str(fixture["declaration"]))
            ),
        },
        "decisions": [decision_document],
    }
    case.write(
        fixture["adopter"],
        ".aicore/adoption-review.yaml",
        yaml.safe_dump(document, sort_keys=False),
    )


def _propose_prepared(
    case: EngineTestCase, fixture: AdopterFixture, revision: str
) -> subprocess.CompletedProcess[str]:
    """Emit a candidate lock for one explicit reviewed adopter revision."""
    return case.run_cli(
        "propose-lock",
        "--upstream-repo",
        str(fixture["upstream"]),
        "--catalog",
        str(fixture["catalog"]),
        "--declaration",
        str(fixture["declaration"]),
        "--review",
        str(fixture["review"]),
        "--lock",
        str(fixture["lock"]),
        "--adopter-revision",
        revision,
    )


def _notice_case(case_id: str) -> RuleNoticeCase:
    return next(case for case in RULE_NOTICE_CASES if case["case_id"] == case_id)


def _file_member_digest(content: bytes, mode: str = "100644") -> str:
    return member_digest([ProjectedEntry("", mode, content)])


def _external_destination_digest(
    catalog_unit: dict[str, object],
    declaration_unit: dict[str, object],
    files: dict[str, tuple[str, bytes]],
) -> str:
    """Digest prepared buffers with the same framing the index snapshot uses."""
    if catalog_unit.get("sync_projection") == "assertions":
        destination = str(catalog_unit.get("destination"))
        text = files[destination][1].decode("utf-8")
        stripped = _strip_comments(text)
        status = [
            (str(assertion.get("id")), str(assertion.get("contains")) in stripped)
            for assertion in catalog_unit.get("assertions", [])
        ]
        return assertion_status_digest(status)
    declared = {
        str(member.get("id")): str(member.get("destination"))
        for member in declaration_unit.get("members", [])
    }
    pairs: list[tuple[str, str]] = []
    for member in catalog_unit.get("members", []):
        member_id = str(member.get("id"))
        destination = declared[member_id]
        mode, content = files[destination]
        pairs.append((member_id, _file_member_digest(content, mode)))
    return unit_digest(pairs)


def _external_unit_digest(
    catalog_unit: dict[str, object],
    declaration_unit: dict[str, object],
    files: dict[str, tuple[str, bytes]],
) -> str:
    """Digest prepared buffers exactly as the staged index snapshot will.

    The general form covers assertions, single-file and tree members so the
    real catalog's protected skills and agents bind from external preparation
    before any destination write.
    """
    if catalog_unit.get("sync_projection") == "assertions":
        destination = str(catalog_unit.get("destination"))
        text = files[destination][1].decode("utf-8")
        stripped = _strip_comments(text)
        status = [
            (str(assertion.get("id")), str(assertion.get("contains")) in stripped)
            for assertion in catalog_unit.get("assertions", [])
        ]
        return assertion_status_digest(status)
    declared = {
        str(member.get("id")): str(member.get("destination"))
        for member in declaration_unit.get("members", [])
    }
    projection = str(catalog_unit.get("sync_projection"))
    pairs: list[tuple[str, str]] = []
    for member in catalog_unit.get("members", []):
        member_id = str(member.get("id"))
        destination = declared[member_id]
        if projection == "tree":
            prefix = destination.rstrip("/") + "/"
            entries = [
                ProjectedEntry(
                    path=relative[len(prefix):],
                    mode=mode,
                    content=content,
                )
                for relative, (mode, content) in files.items()
                if relative.startswith(prefix)
            ]
            pairs.append((member_id, member_digest(entries)))
        else:
            mode, content = files[destination]
            pairs.append((member_id, _file_member_digest(content, mode)))
    return unit_digest(pairs)


def _write_index_review(
    case: EngineTestCase,
    fixture: AdopterFixture,
    decisions: dict[str, tuple[str, bool, str]],
    *,
    baseline_lock_digest: str | None,
) -> None:
    """Bind one fresh review to the staged index, not to the worktree.

    ``decisions`` maps a unit id to ``(decision, verified_layout, evidence)``.
    Digests are read from the index after the caller has staged only the
    reviewed paths.
    """
    catalog = yaml.safe_load(fixture["catalog"].read_text(encoding="utf-8"))
    declaration = yaml.safe_load(fixture["declaration"].read_text(encoding="utf-8"))
    assert isinstance(catalog, dict)
    assert isinstance(declaration, dict)
    snapshot = _IndexSnapshot(_GitRepo(str(fixture["adopter"])))
    upstream = _GitRepo(str(fixture["upstream"]))
    target = case.rev(fixture["upstream"])
    decision_documents: list[dict[str, object]] = []
    for unit in catalog["units"]:
        assert isinstance(unit, dict)
        unit_id = str(unit["id"])
        if unit_id not in decisions:
            continue
        decision, verified_layout, evidence = decisions[unit_id]
        declaration_unit = next(
            item for item in declaration["units"] if item["id"] == unit_id
        )
        document: dict[str, object] = {
            "unit": unit_id,
            "decision": decision,
            "reviewer": "reviewer",
            "evidence": evidence,
            "reviewed_upstream_digest": _unit_upstream_digest(upstream, target, unit),
            "reviewed_destination_digest": _destination_unit_digest(
                unit, declaration_unit, snapshot
            ),
        }
        if verified_layout:
            document["verified_layout"] = RULE_LAYOUT_VALUE
        decision_documents.append(document)
    review = {
        "schema_version": 2,
        "upstream_repository": catalog["catalog"]["upstream_repository"],
        "transition": {
            "baseline_lock_digest": baseline_lock_digest,
            "target_source_commit": target,
            "declaration_digest": _raw_file_digest(str(fixture["declaration"])),
        },
        "decisions": decision_documents,
    }
    case.write(
        fixture["adopter"],
        ".aicore/adoption-review.yaml",
        yaml.safe_dump(review, sort_keys=False),
    )


def _propose_index(
    case: EngineTestCase,
    fixture: AdopterFixture,
    *,
    update: bool,
) -> subprocess.CompletedProcess[str]:
    args = [
        "propose-lock",
        "--upstream-repo",
        str(fixture["upstream"]),
        "--catalog",
        str(fixture["catalog"]),
        "--declaration",
        str(fixture["declaration"]),
        "--review",
        str(fixture["review"]),
        "--adopter-index",
    ]
    if update:
        args.extend(["--lock", str(fixture["lock"])])
    return case.run_cli(*args)


def _check_index(
    case: EngineTestCase,
    fixture: AdopterFixture,
    *,
    lock: Path | None = None,
    json_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    args = [
        "check",
        *case.base_check_args(fixture, lock=lock),
        "--adopter-index",
    ]
    if json_output:
        args.extend(["--format", "json"])
    return case.run_cli(*args)
