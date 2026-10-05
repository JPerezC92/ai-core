"""Prepared candidate acceptance and catalog-transition tests.

The engine emits evidence only; destination edits remain skill-owned. These
tests model the skill workflow with ordinary file operations: prepare reviewed
bytes, record a fresh transition-bound approval, stage only reviewed paths,
emit a separate candidate lock, check that candidate against the same explicit
snapshot, accept the lock, then final-check.

The retired publisher's `apply` writer/journal suite was removed with the
public API. Prepared mirror/adaptation acceptance stays here. Removed-command
rejection and read-only guarantees live in test_adoption_snapshots.py.
Enrollment is clean-start only: a dirty destination aborts before mutation,
and a failed write stops without restore. An existing ignored occupant blocks;
an ignore rule with no file is not unsaved work. New work found after external
preparation aborts and is not restored.
"""

from __future__ import annotations

import ast
import json
import os
import re
import subprocess
from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from typing import cast

import pytest
import yaml

from adoption_constants import AICORE_SUITE_COMMAND, RULE_LAYOUT_VALUE
from adoption_content import (
    _destination_unit_digest,
    _rule_layout,
    _scan_rule_layout,
    _unit_upstream_digest,
)
from adoption_contracts import (
    LockDocument,
    ProjectedEntry,
    StoryMergeMember,
    _strip_comments,
)
from adoption_digests import (
    _retired_descriptor_digest,
    _sha256,
    assertion_status_digest,
    member_digest,
    unit_digest,
)
from adoption_git import (
    _GitRepo,
    _IndexSnapshot,
    _RevisionSnapshot,
    _resolve_git_path,
    _run_controlled_read,
)
from adoption_loaders import _raw_file_digest, load_lock
from adoption_mapping import _catalog_transition, evaluate_applicability
from adoption_reconciliation import _reviewed_unit_source_digest
from adoption_schema import _parse_document_bytes, _validate_lock_document
from adoption_stories import merge_story_index
from adoption_test_acceptance_data import (
    BOOTSTRAP_ADOPTED_PATHS,
    BOOTSTRAP_AGENT_EXTENSION,
    BOOTSTRAP_ASSERTION_CONTAINS,
    BOOTSTRAP_CONFLICT_MANIFEST,
    BOOTSTRAP_DECLARATION,
    BOOTSTRAP_DEBT_HEADER,
    BOOTSTRAP_EXISTING_CONFIG_BEFORE,
    BOOTSTRAP_EXISTING_DEBT,
    BOOTSTRAP_EXISTING_FILES,
    BOOTSTRAP_EXISTING_GITKEEP,
    BOOTSTRAP_EXISTING_INDEX,
    BOOTSTRAP_EXISTING_MANIFEST,
    BOOTSTRAP_EXISTING_PROBLEMS,
    BOOTSTRAP_EXPECTED_EXISTING_DEPENDENCIES,
    BOOTSTRAP_EXPECTED_FRESH_DEPENDENCIES,
    BOOTSTRAP_FORBIDDEN_COMMANDS,
    BOOTSTRAP_FRESH_CONFIG,
    BOOTSTRAP_FRESH_GITKEEP,
    BOOTSTRAP_FRESH_MANIFEST_BEFORE,
    BOOTSTRAP_MIRROR_NOTE,
    BOOTSTRAP_PROBLEM_HEADER,
    BOOTSTRAP_RETAINED_PATHS,
    BOOTSTRAP_REVIEW_EVIDENCE,
    BOOTSTRAP_SKILL,
    BOOTSTRAP_SKILL_NO_DEPENDENCIES,
    BOOTSTRAP_SOURCE_DEBT,
    BOOTSTRAP_SOURCE_FILES,
    BOOTSTRAP_SOURCE_GITKEEP,
    BOOTSTRAP_SOURCE_INDEX,
    BOOTSTRAP_SOURCE_MANIFEST,
    BOOTSTRAP_STORY_FILE,
    BOOTSTRAP_SYMPTOMS,
    MIXED_REVIEW_ALL,
    NOTICE_EXCEPTION_AFTER,
    NOTICE_EXCEPTION_BEFORE,
    NOTICE_PREFERENCE_SENTENCE,
    NOTICE_SOURCE_FAST_TRACK_EXTENSION,
    PROTECTED_AGENT_CATALOG,
    PROTECTED_AGENT_DECLARATION,
    PROTECTED_AGENT_MANDATORY,
    PROTECTED_AGENT_MIRROR_DECLARATION,
    PROTECTED_AGENT_PROFILE,
    PROTECTED_DERIVED_DESTINATION_AGENT,
    PROTECTED_DERIVED_RESULT_LOCAL_CHANGE,
    PROTECTED_DERIVED_RESULT_UPSTREAM_ONLY,
    PROTECTED_DERIVED_SOURCE_AGENT,
    PROTECTED_DERIVED_SOURCE_AGENT_V2,
    PROTECTED_DESTINATION_AGENT,
    PROTECTED_DESTINATION_ROOT,
    PROTECTED_MANDATORY_CORE,
    PROTECTED_ROOT_CATALOG,
    PROTECTED_ROOT_DECLARATION,
    PROTECTED_SOURCE_AGENT,
    PROTECTED_SOURCE_ROOT,
    REAL_CATALOG_DEBT_HEADER,
    REAL_CATALOG_PROBLEM_HEADER,
    REAL_CATALOG_SYMPTOMS,
    RELAY_DESTINATION_BEFORE,
    RELAY_PREVIOUS_CORE,
    RELAY_RESULT_NEW_ENFORCEMENT,
    RELAY_RESULT_UPSTREAM_ONLY,
    RELAY_TARGET_CORE,
    RULE_NOTICE_ACCEPT_CASES,
    RULE_NOTICE_CASES,
    RULE_NOTICE_REJECT_CASES,
    RULE_NOTICE_SEMANTIC_BLOCK_CASES,
    RULE_NOTICE_SEMANTIC_OMISSION_CASES,
    RUNTIME_LINEAGE_CASES,
    RuleNoticeCase,
)
from adoption_test_data import CATALOG_REL, CLEAN_DESTINATION_ROOT, EMPTY_REVIEW, review_with_transition
from adoption_test_repos import (
    HISTORICAL_RULE_DESTINATION,
    HISTORICAL_RULE_SOURCE,
    UNPROTECTED_RULE_CATALOG,
    AdopterFixture,
    EngineTestCase,
    repository_root,
)
from adoption_test_runner_data import AICORE_RUNNER, NO_TESTS_RUNNER

_LINEAGE_CASE_FIELDS: tuple[str, ...] = (
    "previous_core",
    "target_core",
    "destination_before",
    "result",
    "ancestor_before",
    "ancestor_after",
    "local_version_before",
    "local_version_after",
    "review_reasoning",
    "intent",
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
) -> None:
    """Record one fresh transition-bound decision over the prepared snapshot.

    The reviewed destination digest is read from the explicit adopter revision
    that holds the prepared bytes, so altering those bytes after approval makes
    this decision stop matching. ``verified_layout`` records the protected
    two-section attestation only when supplied.
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
            "baseline_lock_digest": _raw_file_digest(str(fixture["lock"])),
            "target_source_commit": target,
            "declaration_digest": _raw_file_digest(str(fixture["declaration"])),
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


class PinConflict(Exception):
    """A prepared skill pin disagrees with an existing manifest pin."""

    def __init__(self, name: str, existing: str, required: str) -> None:
        self.name = name
        self.existing = existing
        self.required = required
        super().__init__(
            f"{name} pin {existing} conflicts with required {required}"
        )


class FrozenReviewMissing(Exception):
    """An adopted-content write was attempted without the frozen review file."""


class CleanStartAbort(Exception):
    """Whole-destination preflight refused before any destination mutation."""


class PartialWriteStopped(Exception):
    """A simulated write failure stopped the run without restoration."""


_DEPENDENCY_SLOT = re.compile(r"^dependencies = (\[.*\])$", re.MULTILINE)
_ENROLL_EVENTS = (
    "preflight",
    "prepare_external",
    "recheck",
    "freeze_controls",
    "recheck_before_write",
    "write_controls",
    "write_content",
    "stage_reviewed",
    "propose",
    "check_candidate",
    "stage_lock_only",
    "check_final",
)
_PLANNED_WRITE_PATHS: tuple[str, ...] = (
    *BOOTSTRAP_ADOPTED_PATHS,
    ".aicore/adoption.yaml",
    ".aicore/adoption-review.yaml",
    ".aicore/adoption.lock.yaml",
)
_OPERATION_PATHS: tuple[tuple[str, str, str], ...] = (
    ("MERGE_HEAD", "file", "in-progress merge"),
    ("CHERRY_PICK_HEAD", "file", "in-progress operation"),
    ("REVERT_HEAD", "file", "in-progress operation"),
    ("rebase-merge", "directory", "in-progress rebase"),
    ("rebase-apply", "directory", "in-progress rebase"),
    ("sequencer", "directory", "in-progress operation"),
)
_STATUS_ARGS: tuple[str, ...] = (
    "status",
    "--porcelain=v2",
    "-z",
    "--untracked-files=all",
    "--ignore-submodules=none",
)


def _skill_dependency_requirements(skill_text: str) -> tuple[str, ...]:
    """Read dependency pins from one enrolled skill's prepared metadata."""
    if not skill_text.startswith("---\n"):
        return ()
    end = skill_text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("enrolled skill frontmatter is not closed")
    document = yaml.safe_load(skill_text[4:end])
    if not isinstance(document, dict):
        return ()
    metadata = document.get("metadata")
    if not isinstance(metadata, dict):
        return ()
    dependencies = metadata.get("dependencies") or []
    if not isinstance(dependencies, list):
        raise ValueError("skill metadata.dependencies must be a list")
    return tuple(str(item) for item in dependencies)


def _manifest_dependencies(manifest: str) -> list[str]:
    match = _DEPENDENCY_SLOT.search(manifest)
    if match is None:
        raise ValueError("manifest has no dependencies slot")
    parsed = ast.literal_eval(match.group(1))
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        raise ValueError("dependencies slot must be a list of strings")
    return list(parsed)


def _pin(spec: str) -> tuple[str, str]:
    name, separator, version = spec.partition("==")
    if not separator or not name or not version:
        raise ValueError(f"dependency is not an exact pin: {spec}")
    return name, version


def _union_manifest_dependencies(before: str, requirements: tuple[str, ...]) -> str:
    """Edit only the dependencies slot. Conflicts abort; empty union is a no-op."""
    current = _manifest_dependencies(before)
    if not requirements:
        return before
    present = {name: version for name, version in (_pin(item) for item in current)}
    merged = list(current)
    for requirement in requirements:
        name, version = _pin(requirement)
        if name in present:
            if present[name] != version:
                raise PinConflict(name, present[name], version)
            continue
        merged.append(requirement)
        present[name] = version
    if merged == current:
        return before
    rendered = "[" + ", ".join(f'"{item}"' for item in merged) + "]"
    match = _DEPENDENCY_SLOT.search(before)
    assert match is not None
    return before[: match.start(1)] + rendered + before[match.end(1) :]


def _prepare_config(before: str | None) -> str:
    """Return valid JSONC containing the required assertion.

    An existing document is edited inside the object. The assertion is never
    appended after the JSON document.
    """
    if before is None:
        rendered = BOOTSTRAP_FRESH_CONFIG
    else:
        if BOOTSTRAP_ASSERTION_CONTAINS in before:
            raise AssertionError("existing config must not already contain the assertion")
        document = json.loads(before)
        if not isinstance(document, dict):
            raise AssertionError("existing config must be a JSON object")
        permission = document.get("permission")
        if not isinstance(permission, dict):
            permission = {}
        bash = permission.get("bash")
        if not isinstance(bash, dict):
            bash = {}
        bash["sudo *"] = "deny"
        permission["bash"] = bash
        document["permission"] = permission
        rendered = json.dumps(document, indent=2) + "\n"
    parsed = json.loads(rendered)
    if not isinstance(parsed, dict) or not rendered.strip().endswith("}"):
        raise AssertionError("prepared config is not a JSON object")
    if BOOTSTRAP_ASSERTION_CONTAINS not in rendered:
        raise AssertionError("prepared config is missing the required assertion")
    return rendered


def _prepare_root(source: str, before: str | None) -> str:
    """Build a destination root from identity plus the source mandatory bytes."""
    source_layout = _rule_layout(source)
    assert source_layout is not None
    spec_match = re.search(
        r"^> \*\*Spec version:\*\* (\d+\.\d+\.\d+)\s*$", source, re.MULTILINE
    )
    assert spec_match is not None
    spec = spec_match.group(1)
    mandatory = source_layout.mandatory.decode("utf-8")
    if before is None:
        framing = (
            "# Relay Runtime\n"
            "> **Project identity:** Relay\n"
            f"> **Spec version:** {spec}\n"
            "> **Local version:** 1.0.0\n"
            "> **Rule layout:** two-section-v1\n"
            "\n"
        )
        extensions = "## Project extensions\n\nDestination-local extension rules.\n\n"
        return framing + extensions + mandatory
    before_layout = _rule_layout(before)
    assert before_layout is not None
    framing = re.sub(
        r"(^> \*\*Spec version:\*\* )\d+\.\d+\.\d+",
        rf"\g<1>{spec}",
        before_layout.framing.decode("utf-8"),
        count=1,
        flags=re.MULTILINE,
    )
    return framing + before_layout.extensions.decode("utf-8") + mandatory


def _prepare_agent(source: str, before: str | None) -> str:
    """Replace agent extensions from destination identity; keep source mandatory."""
    source_layout = _rule_layout(source)
    assert source_layout is not None
    extensions = (
        "## Project extensions\n\n" + BOOTSTRAP_AGENT_EXTENSION.rstrip("\n") + "\n\n"
    )
    mandatory = source_layout.mandatory.decode("utf-8")
    if before is None:
        framing = source_layout.framing.decode("utf-8").replace(
            "# Reviewer\n", "# Reviewer — Relay\n", 1
        )
        return framing + extensions + mandatory
    before_layout = _rule_layout(before)
    assert before_layout is not None
    return before_layout.framing.decode("utf-8") + extensions + mandatory


def _enroll_member(before: str | None, source: str, created: str) -> str:
    """Retain an existing owner member, or create the absent-only header."""
    if before is None:
        return created
    if before == source:
        raise AssertionError("existing member bytes must differ from the source")
    return before


def _prepare_story_index(
    source_index: str, before: str | None
) -> tuple[str, list[str]]:
    members: list[StoryMergeMember] = [
        {
            "id": "alpha",
            "destination": "user-stories/alpha.md",
            "collision_policy": "core_wins",
        }
    ]
    merged, collisions = merge_story_index(
        source_index.encode("utf-8"),
        None if before is None else before.encode("utf-8"),
        members,
    )
    return merged.decode("utf-8"), collisions


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


class PreparedCandidateTests(EngineTestCase):
    """The engine emits evidence only; destination edits remain skill-owned."""

    def _candidate_lock(self, text: str) -> LockDocument:
        return _validate_lock_document(
            _parse_document_bytes(text.encode("utf-8"), "candidate", "invalid_lock"),
            "candidate",
        )

    def test_prepared_candidate_is_complete_and_checkable_without_publishing(self) -> None:
        fixture = self.build_greeting()
        adopter, upstream = fixture["adopter"], fixture["upstream"]
        fixture["review"].write_text(
            review_with_transition(
                EMPTY_REVIEW,
                self.rev(fixture["upstream"]),
                fixture["declaration"].read_text(encoding="utf-8"),
                _raw_file_digest(str(fixture["lock"])),
            ),
            encoding="utf-8",
        )
        fixture["adopter_rev"] = self.commit(adopter, "fresh transition")
        before_adopter = self.worktree_bytes(adopter)
        before_upstream = self.worktree_bytes(upstream)
        before_adopter_git = self.git_state(adopter)
        before_upstream_git = self.git_state(upstream)
        proposal = self.run_cli(
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
            fixture["adopter_rev"],
        )
        self.assert_exit(proposal, 0)
        candidate = self._candidate_lock(proposal.stdout)
        assert {row["id"] for row in candidate["units"]} == {"greeting"}
        candidate_lock = self.write(self.root, "candidate.lock.yaml", proposal.stdout)
        check = self.run_cli(
            "check",
            *self.base_check_args(fixture, lock=candidate_lock),
            "--adopter-revision",
            fixture["adopter_rev"],
        )
        self.assert_exit(check, 0)
        assert self.worktree_bytes(adopter) == before_adopter
        assert self.worktree_bytes(upstream) == before_upstream
        assert self.git_state(adopter) == before_adopter_git
        assert self.git_state(upstream) == before_upstream_git

    def test_combined_mirror_and_adaptation_advance_together(self) -> None:
        fixture = self.build_mixed_mode(MIXED_REVIEW_ALL)
        adopter, upstream = fixture["adopter"], fixture["upstream"]
        before = (self.worktree_bytes(adopter), self.git_state(adopter))

        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(upstream),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proposal, 0)
        candidate = self._candidate_lock(proposal.stdout)
        assert candidate["schema_version"] == 2
        unit_ids = {row["id"] for row in candidate["units"]}
        assert "rulebook" in unit_ids
        assert "root-runtime-spec" in unit_ids

        candidate_path = self.write(self.root, "mixed-candidate.lock.yaml", proposal.stdout)
        check = self.run_cli(
            "check",
            *self.base_check_args(fixture, lock=candidate_path),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(check, 0)
        assert (self.worktree_bytes(adopter), self.git_state(adopter)) == before

    def test_catalog_transition_is_reported_and_added_mirror_accepts(self) -> None:
        fixture = self.build_greeting()
        original_destination = (fixture["adopter"] / "content/greeting.txt").read_bytes()

        accepted_catalog = yaml.safe_load(fixture["catalog"].read_text(encoding="utf-8"))
        accepted_declaration = yaml.safe_load(
            fixture["declaration"].read_text(encoding="utf-8")
        )
        assert isinstance(accepted_catalog, dict)
        assert isinstance(accepted_declaration, dict)
        target_catalog = deepcopy(accepted_catalog)
        target_catalog["units"].append({
            "id": "new-unit",
            "kind": "config",
            "applicability": {"always": True},
            "install_strategy": "copy",
            "sync_projection": "file",
            "members": [{"id": "file", "source": "new.txt", "destination": "new.txt"}],
        })
        target_declaration = deepcopy(accepted_declaration)
        target_declaration["units"].append({
            "id": "new-unit",
            "mode": "mirror",
            "members": [{"id": "file", "destination": "new.txt"}],
        })

        transition_accepted = deepcopy(accepted_catalog)
        transition_accepted["units"].append({
            "id": "retired-unit",
            "kind": "config",
            "applicability": {"always": True},
            "install_strategy": "copy",
            "sync_projection": "file",
            "members": [{"id": "file", "source": "retired.txt", "destination": "retired.txt"}],
        })
        transition_accepted_declaration = deepcopy(accepted_declaration)
        transition_accepted_declaration["units"].append({
            "id": "retired-unit",
            "mode": "mirror",
            "members": [{"id": "file", "destination": "retired.txt"}],
        })
        transition_target = deepcopy(target_catalog)
        transition_target["units"][0]["applicability"] = {"requires": ["ticket_system"]}
        transition_target_declaration = deepcopy(target_declaration)
        transition_target_declaration["units"][0] = {
            "id": "greeting", "mode": "not_applicable"
        }
        transition = _catalog_transition(
            transition_accepted,
            transition_target,
            transition_accepted_declaration,
            transition_target_declaration,
        )
        assert transition["added_units"] == ["new-unit"]
        assert transition["removed_units"] == ["retired-unit"]
        changed = {row["id"]: row for row in transition["changed_units"]}
        assert changed["greeting"]["applicability_changed"] is True

        fixture["catalog"].write_text(
            yaml.safe_dump(target_catalog, sort_keys=False), encoding="utf-8"
        )
        self.write(fixture["upstream"], "new.txt", "new content\n")
        self.commit(fixture["upstream"], "add new-unit")
        fixture["declaration"].write_text(
            yaml.safe_dump(target_declaration, sort_keys=False), encoding="utf-8"
        )
        self.write(fixture["adopter"], "new.txt", "new content\n")
        review = review_with_transition(
            EMPTY_REVIEW,
            self.rev(fixture["upstream"]),
            fixture["declaration"].read_text(encoding="utf-8"),
            _raw_file_digest(str(fixture["lock"])),
        )
        fixture["review"].write_text(review, encoding="utf-8")
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "prepare added mirror")

        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proposal, 0)
        candidate = self.write(self.root, "catalog-transition.lock.yaml", proposal.stdout)
        check = self.run_cli(
            "check",
            *self.base_check_args(fixture, lock=candidate),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(check, 0)
        assert (fixture["adopter"] / "content/greeting.txt").read_bytes() == original_destination

    def test_removed_adapted_unit_originates_from_baseline_and_remains_checkable(self) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        baseline = load_lock(str(fixture["lock"]))
        note_row = next(row for row in baseline["units"] if row["id"] == "note")
        catalog = yaml.safe_load(fixture["catalog"].read_text(encoding="utf-8"))
        declaration = yaml.safe_load(fixture["declaration"].read_text(encoding="utf-8"))
        assert isinstance(catalog, dict)
        assert isinstance(declaration, dict)
        catalog["units"] = [unit for unit in catalog["units"] if unit["id"] != "note"]
        declaration["units"] = [
            unit for unit in declaration["units"] if unit["id"] != "note"
        ]
        fixture["catalog"].write_text(yaml.safe_dump(catalog, sort_keys=False), encoding="utf-8")
        target = self.commit(fixture["upstream"], "retire adapted note")
        fixture["declaration"].write_text(
            yaml.safe_dump(declaration, sort_keys=False), encoding="utf-8"
        )
        retired = {
            **note_row,
            "retired": True,
            "members": [{**member, "projection": "file"} for member in note_row["members"]],
        }
        review = {
            "schema_version": 2,
            "upstream_repository": "example/upstream",
            "transition": {
                "baseline_lock_digest": _raw_file_digest(str(fixture["lock"])),
                "target_source_commit": target,
                "declaration_digest": _raw_file_digest(str(fixture["declaration"])),
            },
            "decisions": [{
                "unit": "note",
                "decision": "declined",
                "reviewer": "test-suite",
                "evidence": "Retained adapted destination reviewed after retirement.",
                "reviewed_upstream_digest": _reviewed_unit_source_digest(
                    _GitRepo(str(fixture["upstream"])),
                    target,
                    None,
                    str(note_row["accepted_upstream_digest"]),
                ),
                "reviewed_destination_digest": _retired_descriptor_digest(retired),
            }],
        }
        fixture["review"].write_text(yaml.safe_dump(review, sort_keys=False), encoding="utf-8")
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "review note retirement")

        proposal = self.run_cli(
            "propose-lock", "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]), "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]), "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proposal, 0)
        candidate = self._candidate_lock(proposal.stdout)
        retired_row = next(row for row in candidate["units"] if row["id"] == "note")
        assert retired_row["retired"] is True
        candidate_path = self.write(self.root, "retired-candidate.lock.yaml", proposal.stdout)
        check = self.run_cli(
            "check", *self.base_check_args(fixture, lock=candidate_path),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(check, 0)
        assert (fixture["adopter"] / "content/note-local.txt").read_text(encoding="utf-8") == "note adapted v1\n"

    def test_applicability_change_originates_from_baseline_and_remains_checkable(self) -> None:
        fixture = self.build_greeting()
        destination = fixture["adopter"] / "content/greeting.txt"
        original_destination = destination.read_bytes()
        catalog = yaml.safe_load(fixture["catalog"].read_text(encoding="utf-8"))
        declaration = yaml.safe_load(fixture["declaration"].read_text(encoding="utf-8"))
        assert isinstance(catalog, dict)
        assert isinstance(declaration, dict)
        catalog["units"][0]["applicability"] = {"requires": ["ticket_system"]}
        declaration["units"][0] = {"id": "greeting", "mode": "not_applicable"}
        fixture["catalog"].write_text(yaml.safe_dump(catalog, sort_keys=False), encoding="utf-8")
        target = self.commit(fixture["upstream"], "make greeting inapplicable")
        fixture["declaration"].write_text(
            yaml.safe_dump(declaration, sort_keys=False), encoding="utf-8"
        )
        review = review_with_transition(
            EMPTY_REVIEW,
            target,
            fixture["declaration"].read_text(encoding="utf-8"),
            _raw_file_digest(str(fixture["lock"])),
        )
        fixture["review"].write_text(review, encoding="utf-8")
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "review applicability")

        proposal = self.run_cli(
            "propose-lock", "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]), "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]), "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proposal, 0)
        candidate = self._candidate_lock(proposal.stdout)
        assert candidate["units"] == [{"id": "greeting", "mode": "not_applicable"}]
        candidate_path = self.write(self.root, "inapplicable-candidate.lock.yaml", proposal.stdout)
        check = self.run_cli(
            "check", *self.base_check_args(fixture, lock=candidate_path),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(check, 0)
        assert destination.read_bytes() == original_destination

    def test_pre_edit_added_unit_reports_review_required_and_preserves_bytes(self) -> None:
        fixture = self.build_greeting()
        adopter = fixture["adopter"]
        before = self.worktree_bytes(adopter)
        catalog = yaml.safe_load(fixture["catalog"].read_text(encoding="utf-8"))
        assert isinstance(catalog, dict)
        catalog["units"].append({
            "id": "new-unit",
            "kind": "config",
            "applicability": {"always": True},
            "install_strategy": "copy",
            "sync_projection": "file",
            "members": [{"id": "file", "source": "new.txt", "destination": "new.txt"}],
        })
        fixture["catalog"].write_text(
            yaml.safe_dump(catalog, sort_keys=False), encoding="utf-8"
        )
        self.write(fixture["upstream"], "new.txt", "new content\n")
        self.commit(fixture["upstream"], "add new-unit")

        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert report["compliance"] is False
        assert report["catalog_transition"]["added_units"] == ["new-unit"]
        added = next(unit for unit in report["units"] if unit["id"] == "new-unit")
        assert added["mode"] is None
        assert added["upstream_delta"] == "changed"
        assert added["destination_delta"] is None
        assert added["disposition"] == "review_required"
        assert "new-unit: review_required" in report["blocking_reasons"]
        assert self.worktree_bytes(adopter) == before

    def test_pre_edit_removed_unit_reports_transition_and_preserves_bytes(self) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        adopter = fixture["adopter"]
        before = self.worktree_bytes(adopter)
        catalog = yaml.safe_load(fixture["catalog"].read_text(encoding="utf-8"))
        assert isinstance(catalog, dict)
        catalog["units"] = [unit for unit in catalog["units"] if unit["id"] != "note"]
        fixture["catalog"].write_text(
            yaml.safe_dump(catalog, sort_keys=False), encoding="utf-8"
        )
        self.commit(fixture["upstream"], "remove note")

        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert report["catalog_transition"]["removed_units"] == ["note"]
        removed = next(unit for unit in report["units"] if unit["id"] == "note")
        assert removed["mode"] == "adapted"
        assert removed["upstream_delta"] == "changed"
        assert removed["disposition"] == "review_required"
        assert "note: review_required" in report["blocking_reasons"]
        assert (
            adopter / "content/note-local.txt"
        ).read_text(encoding="utf-8") == "note adapted v1\n"
        assert self.worktree_bytes(adopter) == before

    def test_pre_edit_member_change_reports_review_required_and_preserves_bytes(self) -> None:
        fixture = self.build_greeting()
        adopter = fixture["adopter"]
        before = self.worktree_bytes(adopter)
        catalog = yaml.safe_load(fixture["catalog"].read_text(encoding="utf-8"))
        assert isinstance(catalog, dict)
        catalog["units"][0]["members"].append(
            {"id": "extra", "source": "content/extra.txt", "destination": "content/extra.txt"}
        )
        fixture["catalog"].write_text(
            yaml.safe_dump(catalog, sort_keys=False), encoding="utf-8"
        )
        self.write(fixture["upstream"], "content/extra.txt", "extra\n")
        self.commit(fixture["upstream"], "add greeting member")

        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        changed = {
            row["id"]: row for row in report["catalog_transition"]["changed_units"]
        }
        assert changed["greeting"]["added_members"] == ["extra"]
        greeting = next(unit for unit in report["units"] if unit["id"] == "greeting")
        assert greeting["disposition"] == "review_required"
        assert greeting["destination_delta"] is None
        assert "greeting: review_required" in report["blocking_reasons"]
        assert (adopter / "content/greeting.txt").read_bytes() == b"hello\n"
        assert self.worktree_bytes(adopter) == before

    def test_pre_edit_applicability_change_reports_baseline_advance_and_preserves_bytes(
        self,
    ) -> None:
        fixture = self.build_greeting()
        adopter = fixture["adopter"]
        before = self.worktree_bytes(adopter)
        catalog = yaml.safe_load(fixture["catalog"].read_text(encoding="utf-8"))
        assert isinstance(catalog, dict)
        catalog["units"][0]["applicability"] = {"requires": ["ticket_system"]}
        fixture["catalog"].write_text(
            yaml.safe_dump(catalog, sort_keys=False), encoding="utf-8"
        )
        self.commit(fixture["upstream"], "make greeting inapplicable")

        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        changed = {
            row["id"]: row for row in report["catalog_transition"]["changed_units"]
        }
        assert changed["greeting"]["applicability_changed"] is True
        greeting = next(unit for unit in report["units"] if unit["id"] == "greeting")
        assert greeting["disposition"] == "baseline_advance_required"
        assert "greeting: baseline_advance_required" in report["blocking_reasons"]
        assert (adopter / "content/greeting.txt").read_bytes() == b"hello\n"
        assert self.worktree_bytes(adopter) == before


class PreparedAcceptanceWorkflowTests(EngineTestCase):
    """Complete skill workflow: prepare, candidate, same-snapshot check, accept."""

    def test_combined_mirror_and_adaptation_advance_through_candidate_to_final_check(
        self,
    ) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        adopter, upstream = fixture["adopter"], fixture["upstream"]
        owner_notes = self.write(adopter, "OWNER-NOTES.md", "unrelated owner work\n")
        fixture["adopter_rev"] = self.commit(adopter, "owner notes")

        # The target advances both the mirror member and the adapted rule.
        self.write(upstream, "content/greeting.txt", "hello world\n")
        self.write(upstream, "content/note.txt", "note v2: REQUIRED_CORE_GUARD\n")
        self.commit(upstream, "advance mirror and adapted rule")

        # Reviewed prepared edits: a mirror source copy plus a reconciled
        # adaptation that retains the new core requirement and local behavior.
        self.write(adopter, "content/greeting.txt", "hello world\n")
        self.write(
            adopter,
            "content/note-local.txt",
            "note v2: REQUIRED_CORE_GUARD\nLOCAL_BUSINESS_RULE: relay billing\n",
        )
        fixture["adopter_rev"] = self.commit(adopter, "prepared reviewed update")
        _write_prepared_review(self, fixture, "note", "applied")

        before_cli = self.worktree_bytes(adopter)
        proposal = _propose_prepared(self, fixture, str(fixture["adopter_rev"]))
        self.assert_exit(proposal, 0)
        assert self.worktree_bytes(adopter) == before_cli, "propose must not write"

        candidate_path = self.write(
            self.root, "workflow-candidate.lock.yaml", proposal.stdout
        )
        candidate_check = self.run_cli(
            "check",
            *self.base_check_args(fixture, lock=candidate_path),
            "--adopter-revision",
            str(fixture["adopter_rev"]),
        )
        self.assert_exit(candidate_check, 0)

        # Accept only after the same-snapshot candidate check passes.
        self.write(adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
        fixture["adopter_rev"] = self.commit(adopter, "accept candidate lock")
        final_check = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            str(fixture["adopter_rev"]),
            "--format",
            "json",
        )
        self.assert_exit(final_check, 0)

        prepared = (adopter / "content/note-local.txt").read_text(encoding="utf-8")
        assert "REQUIRED_CORE_GUARD" in prepared
        assert "LOCAL_BUSINESS_RULE" in prepared
        assert (adopter / "content/greeting.txt").read_text(encoding="utf-8") == (
            "hello world\n"
        )
        assert owner_notes.read_text(encoding="utf-8") == "unrelated owner work\n"

    def test_no_mirror_copy_update_reconciles_adaptation_through_final_check(
        self,
    ) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        adopter = fixture["adopter"]
        greeting_before = (adopter / "content/greeting.txt").read_bytes()

        # Only the adapted rule advanced; no mirror member needs a copy. The
        # reviewed override still binds the exact prepared destination bytes.
        self.write(
            adopter,
            "content/note-local.txt",
            "note v2 acknowledged\nLOCAL_BUSINESS_RULE: keep local flow\n",
        )
        fixture["adopter_rev"] = self.commit(adopter, "reconcile adaptation only")
        _write_prepared_review(self, fixture, "note", "superseded")

        proposal = _propose_prepared(self, fixture, str(fixture["adopter_rev"]))
        self.assert_exit(proposal, 0)
        candidate_path = self.write(
            self.root, "no-mirror-candidate.lock.yaml", proposal.stdout
        )
        self.assert_exit(
            self.run_cli(
                "check",
                *self.base_check_args(fixture, lock=candidate_path),
                "--adopter-revision",
                str(fixture["adopter_rev"]),
            ),
            0,
        )
        self.write(adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
        fixture["adopter_rev"] = self.commit(adopter, "accept no-mirror candidate")
        self.assert_exit(
            self.run_cli(
                "check",
                *self.base_check_args(fixture),
                "--adopter-revision",
                str(fixture["adopter_rev"]),
                "--format",
                "json",
            ),
            0,
        )
        assert (adopter / "content/greeting.txt").read_bytes() == greeting_before


class RuntimeLineageWorkflowTests(EngineTestCase):
    """Prepared runtime-lineage cases: real ancestors, preserved local versions.

    Python binds the prepared bytes and rejects a result altered after review.
    The semantic comparison, the incorporation/override judgment, and every
    local-version rationale are established by the independent model review over
    ``RUNTIME_LINEAGE_CASES``; no assertion here classifies meaning or a bump.
    """

    def _accept_prepared_root(
        self, fixture: AdopterFixture, result: str
    ) -> None:
        """Prepare, propose, same-snapshot check, accept, and final-check a root."""
        adopter = fixture["adopter"]
        self.write(adopter, "AGENTS.md", result)
        fixture["adopter_rev"] = self.commit(
            adopter, "prepared runtime reconciliation"
        )
        _write_prepared_review(self, fixture, "root-runtime-spec", "applied")

        proposal = _propose_prepared(self, fixture, str(fixture["adopter_rev"]))
        self.assert_exit(proposal, 0)
        candidate_path = self.write(
            self.root, "lineage-candidate.lock.yaml", proposal.stdout
        )
        self.assert_exit(
            self.run_cli(
                "check",
                *self.base_check_args(fixture, lock=candidate_path),
                "--adopter-revision",
                str(fixture["adopter_rev"]),
            ),
            0,
        )
        self.write(adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
        fixture["adopter_rev"] = self.commit(adopter, "accept lineage candidate")
        self.assert_exit(
            self.run_cli(
                "check",
                *self.base_check_args(fixture),
                "--adopter-revision",
                str(fixture["adopter_rev"]),
                "--format",
                "json",
            ),
            0,
        )

    def test_root_upstream_only_adopts_target_ancestor_and_keeps_local_version(
        self,
    ) -> None:
        fixture = self.build_guarded_root(
            RELAY_DESTINATION_BEFORE, upstream_root=RELAY_PREVIOUS_CORE
        )
        adopter, upstream = fixture["adopter"], fixture["upstream"]
        self.write(upstream, "AGENTS.md", RELAY_TARGET_CORE)
        self.commit(upstream, "upstream-only runtime update")

        self._accept_prepared_root(fixture, RELAY_RESULT_UPSTREAM_ONLY)

        destination = (adopter / "AGENTS.md").read_text(encoding="utf-8")
        source = (upstream / "AGENTS.md").read_text(encoding="utf-8")
        assert "> **Spec version:** 2.2.0" in destination
        assert "> **Local version:** 1.4.2" in destination
        assert "CORE_RULE_TWO" in destination
        assert "LOCAL_BUSINESS_RULE" in destination
        assert "Local version" not in source
        assert "local-version" not in source

    def test_new_enforceable_rule_is_bound_and_existing_local_rule_survives(
        self,
    ) -> None:
        fixture = self.build_guarded_root(
            RELAY_DESTINATION_BEFORE, upstream_root=RELAY_PREVIOUS_CORE
        )
        adopter, upstream = fixture["adopter"], fixture["upstream"]
        self.write(upstream, "AGENTS.md", RELAY_TARGET_CORE)
        self.commit(upstream, "upstream runtime update")

        self._accept_prepared_root(fixture, RELAY_RESULT_NEW_ENFORCEMENT)

        destination = (adopter / "AGENTS.md").read_text(encoding="utf-8")
        assert "> **Spec version:** 2.2.0" in destination
        assert "> **Local version:** 1.5.0" in destination
        assert "LOCAL_ENFORCEMENT_RULE" in destination
        assert "LOCAL_BUSINESS_RULE" in destination

    def test_result_altered_after_review_is_rejected_without_acceptance(
        self,
    ) -> None:
        fixture = self.build_guarded_root(
            RELAY_DESTINATION_BEFORE, upstream_root=RELAY_PREVIOUS_CORE
        )
        adopter, upstream = fixture["adopter"], fixture["upstream"]
        self.write(upstream, "AGENTS.md", RELAY_TARGET_CORE)
        self.commit(upstream, "upstream runtime update")
        self.write(adopter, "AGENTS.md", RELAY_RESULT_NEW_ENFORCEMENT)
        fixture["adopter_rev"] = self.commit(adopter, "prepared enforceable bump")
        _write_prepared_review(self, fixture, "root-runtime-spec", "applied")

        tampered = RELAY_RESULT_NEW_ENFORCEMENT.replace(
            "> **Local version:** 1.5.0", "> **Local version:** 1.5.1"
        )
        self.write(adopter, "AGENTS.md", tampered)
        tampered_rev = self.commit(adopter, "unreviewed version change")
        rejected = _propose_prepared(self, fixture, tampered_rev)
        self.assert_exit(rejected, 2, "review_changed")
        assert rejected.stdout == ""

        self._accept_prepared_root(fixture, RELAY_RESULT_NEW_ENFORCEMENT)
        accepted = (adopter / "AGENTS.md").read_text(encoding="utf-8")
        assert "> **Local version:** 1.5.0" in accepted

    def test_lineage_case_payloads_are_complete_mechanical_inputs(self) -> None:
        """Structural completeness only; the model review judges meaning."""
        identifiers = [case["case_id"] for case in RUNTIME_LINEAGE_CASES]
        assert len(identifiers) == len(set(identifiers))
        for case in RUNTIME_LINEAGE_CASES:
            payload = cast(dict[str, str], case)
            assert all(
                payload[field] for field in _LINEAGE_CASE_FIELDS
            ), case["case_id"]

    def test_lineage_sources_omit_destination_local_markers(self) -> None:
        """Mechanical guard for the source/destination lineage boundary.

        ``AGENTS.md`` line 30 keeps destination ``Local version`` / ``local-version``
        markers out of AICore ancestor surfaces, so every case's ``previous_core``
        and ``target_core`` omit them while its ``destination_before`` and
        ``result`` carry one. This is a byte-level framing check, not the
        semantic/byte-binding acceptance the model review performs.
        """
        for case in RUNTIME_LINEAGE_CASES:
            payload = cast(dict[str, str], case)
            for source_field in ("previous_core", "target_core"):
                source = payload[source_field]
                assert "local-version" not in source, case["case_id"]
                assert "Local version" not in source, case["case_id"]
            for destination_field in ("destination_before", "result"):
                destination = payload[destination_field]
                assert (
                    "local-version" in destination or "Local version" in destination
                ), case["case_id"]


class DerivedRuntimeByteBindingTests(EngineTestCase):
    """Prepared derived runtime specs whose destination frontmatter is bound.

    Python binds the prepared bytes through the same propose/check engine as
    the root lineage and rejects a result altered after review. The semantic
    comparison and every local-version rationale are established by the
    independent model review over the derived lineage case; no assertion here
    classifies the meaning of the marker or the correctness of a bump.
    """

    def _accept_prepared_derived(
        self, fixture: AdopterFixture, result: str
    ) -> None:
        """Prepare, propose, same-snapshot check, accept, and final-check an agent."""
        adopter = fixture["adopter"]
        self.write(adopter, ".opencode/agents/reviewer.md", result)
        fixture["adopter_rev"] = self.commit(adopter, "prepared derived runtime")
        _write_prepared_review(
            self,
            fixture,
            "reviewer-agent",
            "applied",
            verified_layout=RULE_LAYOUT_VALUE,
        )
        proposal = _propose_prepared(self, fixture, str(fixture["adopter_rev"]))
        self.assert_exit(proposal, 0)
        candidate_path = self.write(
            self.root, "derived-candidate.lock.yaml", proposal.stdout
        )
        self.assert_exit(
            self.run_cli(
                "check",
                *self.base_check_args(fixture, lock=candidate_path),
                "--adopter-revision",
                str(fixture["adopter_rev"]),
            ),
            0,
        )
        self.write(adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
        fixture["adopter_rev"] = self.commit(adopter, "accept derived candidate")
        final = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            str(fixture["adopter_rev"]),
            "--format",
            "json",
        )
        self.assert_exit(final, 0)
        assert json.loads(final.stdout)["compliance"] is True

    def test_derived_upstream_only_update_preserves_frontmatter_local_version(
        self,
    ) -> None:
        fixture = self.build_protected_agent(
            destination_agent=PROTECTED_DERIVED_DESTINATION_AGENT,
            upstream_agent=PROTECTED_DERIVED_SOURCE_AGENT,
        )
        self.write(
            fixture["upstream"],
            ".opencode/agents/reviewer.md",
            PROTECTED_DERIVED_SOURCE_AGENT_V2,
        )
        self.commit(fixture["upstream"], "upstream derived runtime update")

        self._accept_prepared_derived(
            fixture, PROTECTED_DERIVED_RESULT_UPSTREAM_ONLY
        )

        destination = (
            fixture["adopter"] / ".opencode/agents/reviewer.md"
        ).read_text(encoding="utf-8")
        source = (
            fixture["upstream"] / ".opencode/agents/reviewer.md"
        ).read_text(encoding="utf-8")
        assert "local-version: 1.4.2" in destination
        assert "AGENT_CORE_RULE_TWO" in destination
        assert "local-version" not in source

    def test_derived_destination_local_change_is_bound_and_accepted(self) -> None:
        fixture = self.build_protected_agent(
            destination_agent=PROTECTED_DERIVED_DESTINATION_AGENT,
            upstream_agent=PROTECTED_DERIVED_SOURCE_AGENT,
        )

        self._accept_prepared_derived(fixture, PROTECTED_DERIVED_RESULT_LOCAL_CHANGE)

        destination = (
            fixture["adopter"] / ".opencode/agents/reviewer.md"
        ).read_text(encoding="utf-8")
        assert "local-version: 1.5.0" in destination
        assert "LOCAL_AGENT_RULE" in destination

    def test_derived_result_altered_after_review_is_rejected(self) -> None:
        fixture = self.build_protected_agent(
            destination_agent=PROTECTED_DERIVED_DESTINATION_AGENT,
            upstream_agent=PROTECTED_DERIVED_SOURCE_AGENT,
        )
        adopter = fixture["adopter"]
        self.write(
            adopter,
            ".opencode/agents/reviewer.md",
            PROTECTED_DERIVED_RESULT_LOCAL_CHANGE,
        )
        fixture["adopter_rev"] = self.commit(
            adopter, "prepared derived local change"
        )
        _write_prepared_review(
            self,
            fixture,
            "reviewer-agent",
            "applied",
            verified_layout=RULE_LAYOUT_VALUE,
        )

        tampered = PROTECTED_DERIVED_RESULT_LOCAL_CHANGE.replace(
            "local-version: 1.5.0", "local-version: 1.5.1"
        )
        self.write(adopter, ".opencode/agents/reviewer.md", tampered)
        tampered_rev = self.commit(adopter, "unreviewed derived version change")
        rejected = _propose_prepared(self, fixture, tampered_rev)
        self.assert_exit(rejected, 2, "review_changed")
        assert rejected.stdout == ""

        self._accept_prepared_derived(fixture, PROTECTED_DERIVED_RESULT_LOCAL_CHANGE)
        accepted = (
            adopter / ".opencode/agents/reviewer.md"
        ).read_text(encoding="utf-8")
        assert "local-version: 1.5.0" in accepted


class ProtectedAcceptanceTests(EngineTestCase):
    """Protected rule-document convergence, attestation and refusal paths."""

    def _check(self, fixture: AdopterFixture, *, lock: Path | None = None) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "check",
            *self.base_check_args(fixture, lock=lock),
            "--adopter-revision",
            str(fixture["adopter_rev"]),
            "--format",
            "json",
        )

    def _candidate_check(
        self, fixture: AdopterFixture, text: str
    ) -> subprocess.CompletedProcess[str]:
        path = self.write(self.root, "protected-candidate.lock.yaml", text)
        return self.run_cli(
            "check",
            *self.base_check_args(fixture, lock=path),
            "--adopter-revision",
            str(fixture["adopter_rev"]),
        )

    def test_protected_root_candidate_round_trip_and_extension_isolation(self) -> None:
        fixture = self.build_protected_root()
        report = json.loads(self._check(fixture).stdout)
        assert report["compliance"], report["blocking_reasons"]
        assert report["units"][0]["disposition"] == "current"
        destination = (fixture["adopter"] / "AGENTS.md").read_text(encoding="utf-8")
        assert "Destination-local extension rules." in destination
        assert "Core-owned environment preferences." not in destination
        assert "MANDATORY_CORE_V1" in destination

        _write_prepared_review(
            self,
            fixture,
            "root-runtime-spec",
            "applied",
            verified_layout=RULE_LAYOUT_VALUE,
        )
        fixture["adopter_rev"] = self.commit(
            fixture["adopter"], "fresh protected review"
        )
        before = self.worktree_bytes(fixture["adopter"])
        proposal = _propose_prepared(self, fixture, str(fixture["adopter_rev"]))
        self.assert_exit(proposal, 0)
        assert self.worktree_bytes(fixture["adopter"]) == before
        self.assert_exit(self._candidate_check(fixture, proposal.stdout), 0)
        self.write(fixture["adopter"], ".aicore/adoption.lock.yaml", proposal.stdout)
        fixture["adopter_rev"] = self.commit(
            fixture["adopter"], "accept protected candidate"
        )
        final = self._check(fixture)
        self.assert_exit(final, 0)
        assert json.loads(final.stdout)["compliance"]

    def test_protected_mandatory_edit_cannot_emit_candidate(self) -> None:
        fixture = self.build_protected_root()
        path = fixture["adopter"] / "AGENTS.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "MANDATORY_CORE_V1", "ALTERED_CORE"
            ),
            encoding="utf-8",
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "edit mandatory core")
        _write_prepared_review(
            self,
            fixture,
            "root-runtime-spec",
            "applied",
            verified_layout=RULE_LAYOUT_VALUE,
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "fresh review")
        proposal = _propose_prepared(self, fixture, str(fixture["adopter_rev"]))
        self.assert_exit(proposal, 2, "policy_violation")
        assert proposal.stdout == ""

    def test_protected_missing_document_cannot_emit_candidate(self) -> None:
        fixture = self.build_protected_root()
        (fixture["adopter"] / "AGENTS.md").unlink()
        fixture["adopter_rev"] = self.commit(
            fixture["adopter"], "remove protected document"
        )
        _write_prepared_review(
            self,
            fixture,
            "root-runtime-spec",
            "applied",
            verified_layout=RULE_LAYOUT_VALUE,
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "fresh review")
        proposal = _propose_prepared(self, fixture, str(fixture["adopter_rev"]))
        self.assert_exit(proposal, 2, "policy_violation")
        assert proposal.stdout == ""

    def test_protected_marker_without_attestation_rejected(self) -> None:
        fixture = self.build_protected_root()
        _write_prepared_review(
            self, fixture, "root-runtime-spec", "applied", verified_layout=None
        )
        fixture["adopter_rev"] = self.commit(
            fixture["adopter"], "marker without attestation"
        )
        proposal = _propose_prepared(self, fixture, str(fixture["adopter_rev"]))
        self.assert_exit(proposal, 2, "review_changed")
        assert proposal.stdout == ""

    @pytest.mark.parametrize(
        "field", ["reviewed_upstream_digest", "reviewed_destination_digest"]
    )
    def test_protected_stale_source_or_result_rejected(self, field: str) -> None:
        fixture = self.build_protected_root()
        _write_prepared_review(
            self,
            fixture,
            "root-runtime-spec",
            "applied",
            verified_layout=RULE_LAYOUT_VALUE,
            **{field: "sha256:" + "b" * 64},
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "stale digest")
        proposal = _propose_prepared(self, fixture, str(fixture["adopter_rev"]))
        self.assert_exit(proposal, 2, "review_changed")
        assert proposal.stdout == "", field

    def test_protected_stale_transition_rejected(self) -> None:
        fixture = self.build_protected_root()
        _write_prepared_review(
            self,
            fixture,
            "root-runtime-spec",
            "applied",
            verified_layout=RULE_LAYOUT_VALUE,
        )
        review = yaml.safe_load(fixture["review"].read_text(encoding="utf-8"))
        review["transition"]["baseline_lock_digest"] = "sha256:" + "c" * 64
        fixture["review"].write_text(
            yaml.safe_dump(review, sort_keys=False), encoding="utf-8"
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "stale transition")
        proposal = _propose_prepared(self, fixture, str(fixture["adopter_rev"]))
        self.assert_exit(proposal, 2, "review_changed")
        assert proposal.stdout == ""

    def test_protected_post_review_mutation_rejected(self) -> None:
        fixture = self.build_protected_root()
        _write_prepared_review(
            self,
            fixture,
            "root-runtime-spec",
            "applied",
            verified_layout=RULE_LAYOUT_VALUE,
        )
        fixture["adopter_rev"] = self.commit(
            fixture["adopter"], "record reviewed destination"
        )
        path = fixture["adopter"] / "AGENTS.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "Destination-local extension rules.", "Mutated after review."
            ),
            encoding="utf-8",
        )
        fixture["adopter_rev"] = self.commit(
            fixture["adopter"], "mutate after review"
        )
        proposal = _propose_prepared(self, fixture, str(fixture["adopter_rev"]))
        self.assert_exit(proposal, 2, "review_changed")
        assert proposal.stdout == ""

    def test_protected_extension_change_preserves_core(self) -> None:
        fixture = self.build_protected_root()
        path = fixture["adopter"] / "AGENTS.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "Destination-local extension rules.", "Destination extension v2."
            ),
            encoding="utf-8",
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "extension edit")
        _write_prepared_review(
            self,
            fixture,
            "root-runtime-spec",
            "applied",
            verified_layout=RULE_LAYOUT_VALUE,
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "fresh review")
        proposal = _propose_prepared(self, fixture, str(fixture["adopter_rev"]))
        self.assert_exit(proposal, 0)
        assert "MANDATORY_CORE_V1" in (
            fixture["adopter"] / "AGENTS.md"
        ).read_text(encoding="utf-8")

    def test_protected_core_divergence_declined_cannot_emit_candidate(self) -> None:
        fixture = self.build_protected_root()
        path = fixture["adopter"] / "AGENTS.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "MANDATORY_CORE_V1", "LOCAL_WEAKENED_CORE"
            ),
            encoding="utf-8",
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "diverge core")
        _write_prepared_review(
            self,
            fixture,
            "root-runtime-spec",
            "declined",
            verified_layout=RULE_LAYOUT_VALUE,
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "declined review")
        proposal = _propose_prepared(self, fixture, str(fixture["adopter_rev"]))
        self.assert_exit(proposal, 2, "policy_violation")
        assert proposal.stdout == ""

    def test_protected_malformed_source_is_fatal_invalid_mapping(self) -> None:
        fixture = self.build_protected(
            PROTECTED_ROOT_CATALOG,
            PROTECTED_ROOT_DECLARATION,
            {
                "AGENTS.md": (
                    "# Core Runtime\n"
                    "> **Spec version:** 3.0.0\n"
                    "\n"
                    "No ownership sections here.\n"
                )
            },
            {"AGENTS.md": PROTECTED_DESTINATION_ROOT},
            "root-runtime-spec",
            propose=False,
        )
        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proposal, 2, "invalid_mapping")
        assert proposal.stdout == ""

    def test_protected_mirror_unit_still_requires_verified_decision(self) -> None:
        fixture = self.build_protected(
            PROTECTED_AGENT_CATALOG,
            PROTECTED_AGENT_MIRROR_DECLARATION,
            {
                ".opencode/agents/reviewer.md": PROTECTED_SOURCE_AGENT,
                "agents/reviewer/profile.md": PROTECTED_AGENT_PROFILE,
            },
            {
                ".opencode/agents/reviewer.md": PROTECTED_SOURCE_AGENT,
                "agents/reviewer/profile.md": PROTECTED_AGENT_PROFILE,
            },
            "reviewer-agent",
        )
        report = json.loads(self._check(fixture).stdout)
        assert report["compliance"], report["blocking_reasons"]
        _write_prepared_review(
            self, fixture, "reviewer-agent", "applied", verified_layout=None
        )
        fixture["adopter_rev"] = self.commit(
            fixture["adopter"], "mirror without attestation"
        )
        proposal = _propose_prepared(self, fixture, str(fixture["adopter_rev"]))
        self.assert_exit(proposal, 2, "review_changed")
        assert proposal.stdout == ""

    def test_protected_accepted_core_drift_reported_on_pre_edit_path(self) -> None:
        fixture = self.build_protected_root()
        v2_mandatory = (
            "## Mandatory core\n\n"
            "MANDATORY_CORE_V2\n\n"
            "### Hard Rules\n"
            "- Never weaken the mandatory core.\n"
        )
        # The target core and the destination both move to V2, so the target-side
        # comparison is clean; only the accepted-source comparison can see that
        # the destination diverged from its accepted mandatory core.
        self.write(
            fixture["upstream"],
            "AGENTS.md",
            PROTECTED_SOURCE_ROOT.replace(PROTECTED_MANDATORY_CORE, v2_mandatory),
        )
        self.commit(fixture["upstream"], "target core v2")
        self.write(
            fixture["adopter"],
            "AGENTS.md",
            PROTECTED_DESTINATION_ROOT.replace(PROTECTED_MANDATORY_CORE, v2_mandatory),
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "destination core v2")

        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            fixture["adopter_rev"],
            "--format",
            "json",
        )
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert report["compliance"] is False
        assert report["units"][0]["disposition"] == "local_drift"
        assert "root-runtime-spec: local_drift" in report["blocking_reasons"]

    def test_protected_legacy_target_is_assessable_and_reports_pending_review(self) -> None:
        fixture = self.build_guarded_root(CLEAN_DESTINATION_ROOT)
        self.write(fixture["upstream"], CATALOG_REL, PROTECTED_ROOT_CATALOG)
        self.write(fixture["upstream"], "AGENTS.md", PROTECTED_SOURCE_ROOT)
        self.commit(fixture["upstream"], "protected target")
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            fixture["adopter_rev"],
            "--format",
            "json",
        )
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert report["compliance"] is False
        assert report["units"][0]["disposition"] == "review_required"
        assert "root-runtime-spec: review_required" in report["blocking_reasons"]


ADAPTED_RULEBOOK_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: rulebook
    mode: adapted
    members:
      - { id: rules, destination: skills/rules.md }
"""
REPLACEMENT_ROOT_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: root-runtime-spec
    mode: replacement
    replacement_members:
      - { id: local-root, destination: AGENTS.md, projection: file }
"""


class HistoricalProtectionAssessmentTests(EngineTestCase):
    """Accepted protection is assessed independently of incoming target changes."""

    def _check(self, fixture: AdopterFixture) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            fixture["adopter_rev"],
            "--format",
            "json",
        )

    def _unit(self, report: dict[str, object], unit_id: str) -> dict[str, object]:
        units = cast(list[dict[str, object]], report["units"])
        return next(unit for unit in units if unit["id"] == unit_id)

    def _assert_cli_readonly(
        self, fixture: AdopterFixture
    ) -> subprocess.CompletedProcess[str]:
        before_upstream = self.worktree_bytes(fixture["upstream"])
        before_adopter = self.worktree_bytes(fixture["adopter"])
        proc = self._check(fixture)
        assert self.worktree_bytes(fixture["upstream"]) == before_upstream
        assert self.worktree_bytes(fixture["adopter"]) == before_adopter
        return proc

    def _commit_incoming_protection(self, fixture: AdopterFixture) -> None:
        catalog = yaml.safe_load(UNPROTECTED_RULE_CATALOG)
        assert isinstance(catalog, dict)
        catalog["units"][0]["rule_documents"] = ["skills/rules.md"]
        self.write(
            fixture["upstream"],
            CATALOG_REL,
            yaml.safe_dump(catalog, sort_keys=False),
        )
        self.write(fixture["upstream"], "skills/rules.md", HISTORICAL_RULE_SOURCE)
        self.commit(fixture["upstream"], "incoming protection")

    @pytest.mark.parametrize("mode", ["replacement", "destination_owned"])
    def test_incoming_protection_is_pending_not_fatal(self, mode: str) -> None:
        fixture = self.build_unprotected_rule_mode(mode)
        self._commit_incoming_protection(fixture)
        proc = self._assert_cli_readonly(fixture)
        self.assert_exit(proc, 1)
        assert proc.stdout != ""
        report = json.loads(proc.stdout)
        unit = self._unit(report, "rulebook")
        assert unit["disposition"] == "review_required"
        assert "rulebook: review_required" in report["blocking_reasons"]
        assert "invalid_declaration" not in proc.stderr

    def test_reviewed_conversion_reaches_candidate_and_final_check(self) -> None:
        fixture = self.build_unprotected_rule_mode("replacement")
        self._commit_incoming_protection(fixture)
        pending = self._check(fixture)
        self.assert_exit(pending, 1)
        assert self._unit(json.loads(pending.stdout), "rulebook")["disposition"] == (
            "review_required"
        )
        adopter = fixture["adopter"]
        self.write(adopter, ".aicore/adoption.yaml", ADAPTED_RULEBOOK_DECLARATION)
        self.write(adopter, "skills/rules.md", HISTORICAL_RULE_DESTINATION)
        fixture["adopter_rev"] = self.commit(adopter, "prepared protected conversion")
        _write_prepared_review(
            self,
            fixture,
            "rulebook",
            "applied",
            verified_layout=RULE_LAYOUT_VALUE,
        )
        before_upstream = self.worktree_bytes(fixture["upstream"])
        before_adopter = self.worktree_bytes(adopter)
        proposal = _propose_prepared(self, fixture, str(fixture["adopter_rev"]))
        self.assert_exit(proposal, 0)
        assert self.worktree_bytes(fixture["upstream"]) == before_upstream
        assert self.worktree_bytes(adopter) == before_adopter
        candidate_path = self.write(
            self.root, "historical-conversion.lock.yaml", proposal.stdout
        )
        self.assert_exit(
            self.run_cli(
                "check",
                *self.base_check_args(fixture, lock=candidate_path),
                "--adopter-revision",
                str(fixture["adopter_rev"]),
                "--format",
                "json",
            ),
            0,
        )
        self.write(adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
        fixture["adopter_rev"] = self.commit(adopter, "accept conversion candidate")
        final = self._check(fixture)
        self.assert_exit(final, 0)
        assert json.loads(final.stdout)["compliance"] is True
        assert (adopter / "skills/rules.md").read_text(encoding="utf-8") == (
            HISTORICAL_RULE_DESTINATION
        )

    def test_target_mode_rejection_remains_intact(self) -> None:
        fixture = self.build_protected_root()
        declaration = self.write(
            fixture["adopter"],
            ".aicore/replacement-root.yaml",
            REPLACEMENT_ROOT_DECLARATION,
        )
        before_upstream = self.worktree_bytes(fixture["upstream"])
        before_adopter = self.worktree_bytes(fixture["adopter"])
        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(declaration),
            "--review", str(fixture["review"]),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proposal, 2, "invalid_declaration")
        assert proposal.stdout == ""
        assert self.worktree_bytes(fixture["upstream"]) == before_upstream
        assert self.worktree_bytes(fixture["adopter"]) == before_adopter
        lock = yaml.safe_load(fixture["lock"].read_text(encoding="utf-8"))
        assert isinstance(lock, dict)
        self.write(fixture["adopter"], ".aicore/adoption.yaml", REPLACEMENT_ROOT_DECLARATION)
        lock["declaration_digest"] = _raw_file_digest(str(fixture["declaration"]))
        old_members = lock["units"][0].pop("members")
        lock["units"][0]["mode"] = "replacement"
        lock["units"][0]["replacement_members"] = [
            {
                "id": "local-root",
                "destination": "AGENTS.md",
                "projection": "file",
                "accepted_destination_digest": old_members[0]["accepted_destination_digest"],
            }
        ]
        self.write(
            fixture["adopter"],
            ".aicore/adoption.lock.yaml",
            yaml.safe_dump(lock, sort_keys=False),
        )
        checked = self._check(fixture)
        self.assert_exit(checked, 2, "invalid_declaration")
        assert checked.stdout == ""
        assert self.worktree_bytes(fixture["upstream"]) == before_upstream

    def test_accepted_drift_wins_over_target_mismatch(self) -> None:
        fixture = self.build_protected_root()
        target_core = PROTECTED_MANDATORY_CORE.replace(
            "MANDATORY_CORE_V1", "MANDATORY_CORE_V2"
        )
        drifted_core = PROTECTED_MANDATORY_CORE.replace(
            "MANDATORY_CORE_V1", "MANDATORY_CORE_V3"
        )
        self.write(
            fixture["upstream"],
            "AGENTS.md",
            PROTECTED_SOURCE_ROOT.replace(PROTECTED_MANDATORY_CORE, target_core),
        )
        self.commit(fixture["upstream"], "target core v2")
        self.write(
            fixture["adopter"],
            "AGENTS.md",
            PROTECTED_DESTINATION_ROOT.replace(PROTECTED_MANDATORY_CORE, drifted_core),
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "destination core v3")
        proc = self._assert_cli_readonly(fixture)
        self.assert_exit(proc, 1)
        unit = self._unit(json.loads(proc.stdout), "root-runtime-spec")
        assert unit["disposition"] == "local_drift"
        assert "root-runtime-spec: local_drift" in json.loads(proc.stdout)["blocking_reasons"]

    def test_member_and_protection_changes_cannot_hide_accepted_drift(self) -> None:
        added = self.build_protected_agent()
        catalog = yaml.safe_load(added["catalog"].read_text(encoding="utf-8"))
        assert isinstance(catalog, dict)
        catalog["units"][0]["members"].append(
            {
                "id": "extra",
                "source": "agents/reviewer/extra.md",
                "destination": "agents/reviewer/extra.md",
            }
        )
        self.write(added["upstream"], CATALOG_REL, yaml.safe_dump(catalog, sort_keys=False))
        self.commit(added["upstream"], "add member")
        self.write(
            added["adopter"],
            ".opencode/agents/reviewer.md",
            PROTECTED_DESTINATION_AGENT.replace(
                "MANDATORY_AGENT_CORE", "MANDATORY_AGENT_DRIFT"
            ),
        )
        added["adopter_rev"] = self.commit(added["adopter"], "drift spec")
        added_proc = self._assert_cli_readonly(added)
        self.assert_exit(added_proc, 1)
        assert self._unit(json.loads(added_proc.stdout), "reviewer-agent")["disposition"] == (
            "local_drift"
        )

        removed = self.build_protected_agent()
        removed_catalog = yaml.safe_load(removed["catalog"].read_text(encoding="utf-8"))
        assert isinstance(removed_catalog, dict)
        removed_catalog["units"][0]["members"] = [
            member
            for member in removed_catalog["units"][0]["members"]
            if member["id"] == "spec"
        ]
        self.write(
            removed["upstream"],
            CATALOG_REL,
            yaml.safe_dump(removed_catalog, sort_keys=False),
        )
        self.commit(removed["upstream"], "remove member")
        self.write(
            removed["adopter"],
            ".opencode/agents/reviewer.md",
            PROTECTED_DESTINATION_AGENT.replace(
                "MANDATORY_AGENT_CORE", "MANDATORY_AGENT_DRIFT"
            ),
        )
        removed["adopter_rev"] = self.commit(removed["adopter"], "drift spec")
        removed_proc = self._check(removed)
        self.assert_exit(removed_proc, 1)
        assert self._unit(json.loads(removed_proc.stdout), "reviewer-agent")[
            "disposition"
        ] == "local_drift"

        dropped = self.build_protected_root()
        dropped_catalog = yaml.safe_load(dropped["catalog"].read_text(encoding="utf-8"))
        assert isinstance(dropped_catalog, dict)
        del dropped_catalog["units"][0]["rule_documents"]
        self.write(
            dropped["upstream"],
            CATALOG_REL,
            yaml.safe_dump(dropped_catalog, sort_keys=False),
        )
        self.commit(dropped["upstream"], "drop protection")
        self.write(
            dropped["adopter"],
            "AGENTS.md",
            PROTECTED_DESTINATION_ROOT.replace(
                "MANDATORY_CORE_V1", "MANDATORY_CORE_DRIFT"
            ),
        )
        dropped["adopter_rev"] = self.commit(dropped["adopter"], "drift root")
        dropped_proc = self._check(dropped)
        self.assert_exit(dropped_proc, 1)
        assert self._unit(json.loads(dropped_proc.stdout), "root-runtime-spec")[
            "disposition"
        ] == "local_drift"

        retired = self.build_protected_root()
        retired_catalog = yaml.safe_load(retired["catalog"].read_text(encoding="utf-8"))
        assert isinstance(retired_catalog, dict)
        retired_catalog["units"] = [
            {
                "id": "note",
                "kind": "skill",
                "applicability": {"always": True},
                "install_strategy": "copy",
                "sync_projection": "file",
                "members": [
                    {
                        "id": "file",
                        "source": "content/note.txt",
                        "destination": "content/note.txt",
                    }
                ],
            }
        ]
        self.write(
            retired["upstream"],
            CATALOG_REL,
            yaml.safe_dump(retired_catalog, sort_keys=False),
        )
        self.write(retired["upstream"], "content/note.txt", "note\n")
        self.commit(retired["upstream"], "remove protected unit")
        self.write(
            retired["adopter"],
            "AGENTS.md",
            PROTECTED_DESTINATION_ROOT.replace(
                "MANDATORY_CORE_V1", "MANDATORY_CORE_DRIFT"
            ),
        )
        retired["adopter_rev"] = self.commit(retired["adopter"], "drift removed unit")
        retired_proc = self._check(retired)
        self.assert_exit(retired_proc, 1)
        assert self._unit(json.loads(retired_proc.stdout), "root-runtime-spec")[
            "disposition"
        ] == "local_drift"

    def test_compliant_target_changes_report_pending_work(self) -> None:
        added = self.build_protected_agent()
        catalog = yaml.safe_load(added["catalog"].read_text(encoding="utf-8"))
        assert isinstance(catalog, dict)
        catalog["units"][0]["members"].append(
            {
                "id": "extra",
                "source": "agents/reviewer/extra.md",
                "destination": "agents/reviewer/extra.md",
            }
        )
        self.write(added["upstream"], CATALOG_REL, yaml.safe_dump(catalog, sort_keys=False))
        self.commit(added["upstream"], "add member")
        added_proc = self._assert_cli_readonly(added)
        self.assert_exit(added_proc, 1)
        assert self._unit(json.loads(added_proc.stdout), "reviewer-agent")["disposition"] == (
            "review_required"
        )

        dropped = self.build_protected_root()
        dropped_catalog = yaml.safe_load(dropped["catalog"].read_text(encoding="utf-8"))
        assert isinstance(dropped_catalog, dict)
        del dropped_catalog["units"][0]["rule_documents"]
        self.write(
            dropped["upstream"],
            CATALOG_REL,
            yaml.safe_dump(dropped_catalog, sort_keys=False),
        )
        self.commit(dropped["upstream"], "drop protection")
        dropped_proc = self._check(dropped)
        self.assert_exit(dropped_proc, 1)
        assert self._unit(json.loads(dropped_proc.stdout), "root-runtime-spec")[
            "disposition"
        ] == "baseline_advance_required"

    def test_removed_unit_still_reports_pending_accepted_work(self) -> None:
        retired = self.build_protected_root()
        retired_catalog = yaml.safe_load(retired["catalog"].read_text(encoding="utf-8"))
        assert isinstance(retired_catalog, dict)
        retired_catalog["units"] = []
        self.write(
            retired["upstream"],
            CATALOG_REL,
            yaml.safe_dump(retired_catalog, sort_keys=False),
        )
        self.commit(retired["upstream"], "remove unit")
        retired_proc = self._assert_cli_readonly(retired)
        self.assert_exit(retired_proc, 1)
        assert self._unit(json.loads(retired_proc.stdout), "root-runtime-spec")[
            "disposition"
        ] == "review_required"


_NOTICE_ENGINE_ERRORS: dict[str, str] = {
    "notice-core-divergence-declined": "mandatory core differs",
    "notice-counterfeit-attestation": "mandatory core differs",
    "notice-missing-affected-file": "protected rule document is missing",
}
class RuleNoticeAcceptanceTests(EngineTestCase):
    """Prepared notice cases round-trip or reject through the read-only engine.

    Tests bind reviewed bytes and engine exit codes. They do not classify
    notice prose or read ``intended_verdict``.
    """

    def _prepare_notice_index(
        self,
        case: RuleNoticeCase,
        *,
        verified_layout: bool | None = None,
    ) -> AdopterFixture:
        fixture = self.build_protected(
            case["catalog"],
            case["declaration"],
            {
                surface["path"]: surface["previous_source"]
                for surface in case["surfaces"]
            },
            {
                surface["path"]: surface["destination_before"]
                for surface in case["surfaces"]
            },
            case["unit"],
        )
        for surface in case["surfaces"]:
            self.write(
                fixture["upstream"], surface["path"], surface["target_source"]
            )
        self.commit(fixture["upstream"], "target notice core")
        self.write(fixture["adopter"], "OWNER-NOTES.md", "unrelated owner work\n")
        for surface in case["surfaces"]:
            destination = fixture["adopter"] / surface["path"]
            if surface["path"] in case["omit_paths"]:
                if destination.exists():
                    destination.unlink()
                continue
            self.write(fixture["adopter"], surface["path"], surface["result"])
        self.stage(
            fixture["adopter"],
            *(surface["path"] for surface in case["surfaces"]),
        )
        layout = (
            case["verified_layout"] if verified_layout is None else verified_layout
        )
        _write_index_review(
            self,
            fixture,
            {
                case["unit"]: (
                    case["decision"],
                    layout,
                    case["review_notice"],
                )
            },
            baseline_lock_digest=_raw_file_digest(str(fixture["lock"])),
        )
        self.stage(fixture["adopter"], ".aicore/adoption-review.yaml")
        return fixture

    def _assert_notice_bytes(self, case: RuleNoticeCase, fixture: AdopterFixture) -> None:
        review = yaml.safe_load(fixture["review"].read_text(encoding="utf-8"))
        assert isinstance(review, dict)
        decision = review["decisions"][0]
        assert decision["evidence"] == case["review_notice"]
        assert decision["decision"] == "applied"
        assert decision["verified_layout"] == RULE_LAYOUT_VALUE
        for surface in case["surfaces"]:
            accepted = (fixture["adopter"] / surface["path"]).read_text(encoding="utf-8")
            source = (fixture["upstream"] / surface["path"]).read_text(encoding="utf-8")
            assert accepted == surface["result"]
            assert source == surface["target_source"]
            assert self.staged_bytes(fixture["adopter"], surface["path"]) == (
                surface["result"].encode("utf-8")
            )
            source_layout = _rule_layout(source)
            accepted_layout = _rule_layout(accepted)
            assert source_layout is not None and accepted_layout is not None
            assert accepted_layout.mandatory == source_layout.mandatory
        root = next(
            surface for surface in case["surfaces"] if surface["path"] == "AGENTS.md"
        )
        before_layout = _rule_layout(root["destination_before"])
        result_layout = _rule_layout(root["result"])
        assert before_layout is not None and result_layout is not None
        preference = f"{NOTICE_PREFERENCE_SENTENCE}\n".encode("utf-8")
        assert preference in before_layout.extensions
        assert preference in result_layout.extensions
        if NOTICE_EXCEPTION_BEFORE in root["destination_before"]:
            assert NOTICE_EXCEPTION_BEFORE not in root["result"]
            assert NOTICE_EXCEPTION_AFTER in root["result"]
        else:
            assert before_layout.extensions == result_layout.extensions
        policy = next(
            (
                surface
                for surface in case["surfaces"]
                if surface["path"] == "policies/fast-track.md"
            ),
            None,
        )
        if policy is not None:
            assert NOTICE_EXCEPTION_BEFORE in policy["destination_before"]
            assert NOTICE_EXCEPTION_BEFORE not in policy["result"]
            assert NOTICE_EXCEPTION_AFTER in policy["result"]
            assert NOTICE_SOURCE_FAST_TRACK_EXTENSION in policy["target_source"]
            assert NOTICE_SOURCE_FAST_TRACK_EXTENSION not in policy["result"]
            assert NOTICE_SOURCE_FAST_TRACK_EXTENSION not in policy["destination_before"]

    @pytest.mark.parametrize(
        "case_id",
        [case["case_id"] for case in RULE_NOTICE_ACCEPT_CASES],
    )
    def test_valid_notice_round_trip_binds_reviewed_bytes(self, case_id: str) -> None:
        case = _notice_case(case_id)
        fixture = self._prepare_notice_index(case)
        adopter = fixture["adopter"]
        assert self.index_entry(adopter, "OWNER-NOTES.md") is None
        before = self.worktree_bytes(adopter)
        proposal = _propose_index(self, fixture, update=True)
        self.assert_exit(proposal, 0)
        assert self.worktree_bytes(adopter) == before
        candidate = self.write(self.root, f"{case_id}.lock.yaml", proposal.stdout)
        self.assert_exit(_check_index(self, fixture, lock=candidate), 0)
        self.write(adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
        self.stage(adopter, ".aicore/adoption.lock.yaml")
        final = _check_index(self, fixture, json_output=True)
        self.assert_exit(final, 0)
        assert json.loads(final.stdout)["compliance"] is True
        assert (adopter / "OWNER-NOTES.md").read_text(encoding="utf-8") == (
            "unrelated owner work\n"
        )
        assert self.index_entry(adopter, "OWNER-NOTES.md") is None
        self._assert_notice_bytes(case, fixture)

    @pytest.mark.parametrize(
        "case_id",
        [case["case_id"] for case in RULE_NOTICE_REJECT_CASES],
    )
    def test_invalid_notice_case_rejects(self, case_id: str) -> None:
        case = _notice_case(case_id)
        fixture = self._prepare_notice_index(case)
        review = yaml.safe_load(fixture["review"].read_text(encoding="utf-8"))
        assert isinstance(review, dict)
        assert review["decisions"][0]["decision"] == case["decision"]
        if case["verified_layout"]:
            assert review["decisions"][0]["verified_layout"] == RULE_LAYOUT_VALUE
        else:
            assert "verified_layout" not in review["decisions"][0]
        if case["omit_paths"]:
            for relative in case["omit_paths"]:
                assert self.index_entry(fixture["adopter"], relative) is None
        before_lock = fixture["lock"].read_bytes()
        before = self.worktree_bytes(fixture["adopter"])
        proposal = _propose_index(self, fixture, update=True)
        self.assert_exit(proposal, 2, "policy_violation")
        self.assert_exit(proposal, 2, _NOTICE_ENGINE_ERRORS[case_id])
        assert proposal.stdout == ""
        assert fixture["lock"].read_bytes() == before_lock
        assert self.worktree_bytes(fixture["adopter"]) == before

    def test_result_altered_after_notice_review_rejects(self) -> None:
        case = _notice_case("notice-compatible-extension")
        fixture = self._prepare_notice_index(case)
        accepted = (fixture["adopter"] / "AGENTS.md").read_text(encoding="utf-8")
        tampered = accepted.replace(
            NOTICE_PREFERENCE_SENTENCE, "Relay release notes were altered.", 1
        )
        self.write(fixture["adopter"], "AGENTS.md", tampered)
        self.stage(fixture["adopter"], "AGENTS.md")
        rejected = _propose_index(self, fixture, update=True)
        self.assert_exit(rejected, 2, "review_changed")
        assert rejected.stdout == ""
        assert self.index_entry(fixture["adopter"], "OWNER-NOTES.md") is None

    def test_missing_layout_approval_rejects(self) -> None:
        case = _notice_case("notice-compatible-extension")
        fixture = self._prepare_notice_index(case, verified_layout=False)
        review = yaml.safe_load(fixture["review"].read_text(encoding="utf-8"))
        assert isinstance(review, dict)
        assert "verified_layout" not in review["decisions"][0]
        rejected = _propose_index(self, fixture, update=True)
        self.assert_exit(rejected, 2, "review_changed")
        assert rejected.stdout == ""


class OrderedEnrollmentDriverMixin:
    """Ordered clean-start driver reused by synthetic and real-catalog flows.

    The driver owns the reviewed sequence: controlled preflight, external
    complete preparation, recheck, freeze controls, recheck before write, write
    controls then content, stage reviewed paths, propose an external candidate,
    check that candidate, install the lock only, and final-check. Preparation,
    declaration, and review generation are supplied by the caller.
    """

    def _fixture(self, accepted: str) -> AdopterFixture:
        return {
            "accepted": accepted,
            "target": self.rev(self.upstream),
            "adopter_rev": accepted,
            "upstream": self.upstream,
            "adopter": self.adopter,
            "catalog": self.upstream / CATALOG_REL,
            "declaration": self.adopter / ".aicore/adoption.yaml",
            "review": self.adopter / ".aicore/adoption-review.yaml",
            "lock": self.adopter / ".aicore/adoption.lock.yaml",
        }

    def _write_adopted(
        self,
        adopter: Path,
        relative: str,
        text: str,
        declaration_text: str,
        review_text: str,
    ) -> None:
        review = adopter / ".aicore/adoption-review.yaml"
        declaration = adopter / ".aicore/adoption.yaml"
        if not review.is_file() or review.read_text(encoding="utf-8") != review_text:
            raise FrozenReviewMissing("frozen review file is absent")
        if (
            not declaration.is_file()
            or declaration.read_text(encoding="utf-8") != declaration_text
        ):
            raise FrozenReviewMissing("frozen declaration file is absent")
        self.write(adopter, relative, text)

    def _assert_driver_trace(self, start: int) -> list[tuple[str, ...]]:
        trace = self.command_trace[start:]
        assert trace, "the test driver recorded no commands"
        for argv in trace:
            rendered = " ".join(argv)
            for forbidden in BOOTSTRAP_FORBIDDEN_COMMANDS:
                assert forbidden not in rendered, rendered
            for mutation in ("stash", "reset", "clean", "restore"):
                assert mutation not in argv, rendered
            if "sync_aicore_adoption.py" in rendered:
                assert "propose-lock" in argv or "check" in argv, rendered
            else:
                assert argv[0] == "git", rendered
        return trace

    def _read(self, repo: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
        """Inspect through the shared controlled read. Fixture mutations stay on ``git``."""
        return _run_controlled_read(str(repo), args)

    def _in_progress_operation(self, repo: Path) -> str | None:
        """Resolve policy paths with ``--git-path``. A gitfile is not dirtiness."""
        for name, kind, reason in _OPERATION_PATHS:
            resolved = _resolve_git_path(str(repo), name)
            if resolved is None:
                return "cleanliness cannot be confirmed"
            path = Path(resolved)
            if kind == "file" and path.is_file():
                return reason
            if kind == "directory" and path.exists():
                return reason
        return None

    def _index_flag_block(self, payload: bytes) -> str | None:
        """Abort on skip-worktree, assume-unchanged, or an unknown index flag."""
        for raw in payload.split(b"\0"):
            if not raw:
                continue
            flag = chr(raw[0])
            if flag == "H":
                continue
            if flag == "S" or flag.islower():
                return "assume-unchanged or skip-worktree entry"
            return "cleanliness cannot be confirmed"
        return None

    def _ignored_write_occupant(self, repo: Path) -> str | None:
        """Block an existing ignored occupant. An absent ignore-rule path is not one."""
        for relative in _PLANNED_WRITE_PATHS:
            ignored = self._read(repo, "check-ignore", "-q", "--", relative)
            if ignored.returncode not in (0, 1):
                return "cleanliness cannot be confirmed"
            if ignored.returncode != 0:
                continue
            occupant = repo / relative
            if occupant.exists() or occupant.is_symlink():
                return f"ignored path would be overwritten: {relative}"
        return None

    def _preflight(self, repo: Path, editor_confirmed: bool | None) -> str | None:
        """Read-only whole-destination gate. Uncertainty blocks; it does not default true."""
        if editor_confirmed is not True:
            return "saved-editor confirmation is required"
        inside = self._read(repo, "rev-parse", "--is-inside-work-tree")
        if inside.returncode != 0 or inside.stdout.strip() != b"true":
            return "repository state is unknown"
        head = self._read(repo, "rev-parse", "--verify", "HEAD")
        if head.returncode != 0:
            return "destination has no committed HEAD"
        operation = self._in_progress_operation(repo)
        if operation is not None:
            return operation
        status = self._read(repo, *_STATUS_ARGS)
        if status.returncode != 0:
            return "cleanliness cannot be confirmed"
        if status.stdout:
            return "destination has unsaved or uncommitted work"
        flags = self._read(repo, "ls-files", "-v", "-z")
        if flags.returncode != 0:
            return "cleanliness cannot be confirmed"
        flag_block = self._index_flag_block(flags.stdout)
        if flag_block is not None:
            return flag_block
        return self._ignored_write_occupant(repo)

    def _ordered_enroll(
        self,
        *,
        editor_confirmed: bool | None,
        before: dict[str, str] | None,
        prepare: "Callable[[dict[str, str] | None], tuple[dict[str, str], list[str]]]",
        declaration_text: str,
        build_review: "Callable[[dict[str, str], str], str]",
        baseline_lock: bool = False,
        fail_after_content_writes: int | None = None,
        approval: bool = True,
        after_prepare: Callable[[], None] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        """Run one ordered enrollment over caller-supplied preparation."""
        adopter = self.adopter
        self.events: list[str] = []
        reason = self._preflight(adopter, editor_confirmed)
        self.events.append("preflight")
        if reason is not None:
            self.events.append("abort")
            raise CleanStartAbort(reason)
        prepared, collisions = prepare(before)
        self.collisions = collisions
        self.events.append("prepare_external")
        if after_prepare is not None:
            after_prepare()
        reason = self._preflight(adopter, editor_confirmed)
        self.events.append("recheck")
        if reason is not None:
            self.events.append("abort")
            raise CleanStartAbort(reason)
        if not approval:
            self.events.append("missing_approval")
            raise FrozenReviewMissing("review was not frozen")
        review_text = build_review(prepared, declaration_text)
        self.events.append("freeze_controls")
        reason = self._preflight(adopter, editor_confirmed)
        self.events.append("recheck_before_write")
        if reason is not None:
            self.events.append("abort")
            raise CleanStartAbort(reason)
        self.write(adopter, ".aicore/adoption.yaml", declaration_text)
        self.write(adopter, ".aicore/adoption-review.yaml", review_text)
        self.events.append("write_controls")
        written = 0
        for relative, text in prepared.items():
            if (
                fail_after_content_writes is not None
                and written >= fail_after_content_writes
            ):
                self.events.append("stop_partial")
                raise PartialWriteStopped(relative)
            self._write_adopted(adopter, relative, text, declaration_text, review_text)
            written += 1
        frozen_review = (adopter / ".aicore/adoption-review.yaml").read_bytes()
        self.events.append("write_content")
        assert (adopter / ".aicore/adoption-review.yaml").read_bytes() == frozen_review
        self.stage(
            adopter,
            ".aicore/adoption.yaml",
            ".aicore/adoption-review.yaml",
            *prepared,
        )
        self.events.append("stage_reviewed")
        fixture = self._fixture(self.rev(self.upstream))
        proposal = _propose_index(self, fixture, update=baseline_lock)
        self.events.append("propose")
        self.assert_exit(proposal, 0)
        candidate = self.write(self.root, "ordered-candidate.lock.yaml", proposal.stdout)
        checked = _check_index(self, fixture, lock=candidate, json_output=True)
        self.events.append("check_candidate")
        self.assert_exit(checked, 0)
        report = json.loads(checked.stdout)
        assert report["compliance"] is True
        assert report["diagnostic"] is False
        assert report["blocking_reasons"] == []
        self.write(adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
        self.stage(adopter, ".aicore/adoption.lock.yaml")
        self.events.append("stage_lock_only")
        final = _check_index(self, fixture, json_output=True)
        self.events.append("check_final")
        self.assert_exit(final, 0)
        final_report = json.loads(final.stdout)
        assert final_report["compliance"] is True
        assert final_report["diagnostic"] is False
        assert final_report["blocking_reasons"] == []
        assert self.events == list(_ENROLL_EVENTS)
        self.proposal_stdout = proposal.stdout
        return proposal


class OrderedBootstrapAcceptanceTests(EngineTestCase, OrderedEnrollmentDriverMixin):
    """One fresh and one existing enrollment. Approval is frozen before writes."""

    def _prepare_all(
        self, before: dict[str, str] | None
    ) -> tuple[dict[str, str], list[str]]:
        """Prepare every adopted result outside the destination."""
        source = BOOTSTRAP_SOURCE_FILES
        root_before = None if before is None else before["AGENTS.md"]
        agent_before = None if before is None else before[".opencode/agents/reviewer.md"]
        manifest_before = (
            BOOTSTRAP_FRESH_MANIFEST_BEFORE
            if before is None
            else before["pyproject.toml"]
        )
        config_before = None if before is None else before["opencode.jsonc"]
        index_before = None if before is None else before["user-stories/index.md"]
        requirements = _skill_dependency_requirements(source[".opencode/skills/enrolled/SKILL.md"])
        manifest = _union_manifest_dependencies(manifest_before, requirements)
        index, collisions = _prepare_story_index(source["user-stories/index.md"], index_before)
        prepared = {
            "AGENTS.md": _prepare_root(source["AGENTS.md"], root_before),
            ".opencode/agents/reviewer.md": _prepare_agent(
                source[".opencode/agents/reviewer.md"], agent_before
            ),
            "agents/reviewer/profile.md": source["agents/reviewer/profile.md"],
            "skills/mirror-note.md": source["skills/mirror-note.md"],
            "knowledge/debt.md": _enroll_member(
                None if before is None else before["knowledge/debt.md"],
                source["knowledge/debt.md"],
                BOOTSTRAP_DEBT_HEADER,
            ),
            "knowledge/symptoms.md": source["knowledge/symptoms.md"],
            "knowledge/problems.md": _enroll_member(
                None if before is None else before["knowledge/problems.md"],
                source["knowledge/problems.md"],
                BOOTSTRAP_PROBLEM_HEADER,
            ),
            "plans/.gitkeep": _enroll_member(
                None if before is None else before["plans/.gitkeep"],
                source["plans/.gitkeep"],
                BOOTSTRAP_FRESH_GITKEEP,
            ),
            "pyproject.toml": manifest,
            ".opencode/skills/enrolled/SKILL.md": source[".opencode/skills/enrolled/SKILL.md"],
            "opencode.jsonc": _prepare_config(config_before),
            "user-stories/alpha.md": source["user-stories/alpha.md"],
            "user-stories/index.md": index,
        }
        assert tuple(prepared) == BOOTSTRAP_ADOPTED_PATHS
        return prepared, collisions

    def _review_text(self, prepared: dict[str, str], declaration_text: str) -> str:
        catalog = yaml.safe_load((self.upstream / CATALOG_REL).read_text(encoding="utf-8"))
        declaration = yaml.safe_load(declaration_text)
        assert isinstance(catalog, dict)
        assert isinstance(declaration, dict)
        files = {
            relative: ("100644", text.encode("utf-8"))
            for relative, text in prepared.items()
        }
        upstream = _GitRepo(str(self.upstream))
        target = self.rev(self.upstream)
        decisions: list[dict[str, object]] = []
        for unit in catalog["units"]:
            assert isinstance(unit, dict)
            declaration_unit = next(
                item for item in declaration["units"] if item["id"] == unit["id"]
            )
            protected = bool(unit.get("rule_documents"))
            mode = str(declaration_unit["mode"])
            if not protected and mode not in ("adapted", "replacement", "destination_owned"):
                continue
            document: dict[str, object] = {
                "unit": unit["id"],
                "decision": "applied",
                "reviewer": "reviewer",
                "evidence": BOOTSTRAP_REVIEW_EVIDENCE,
                "reviewed_upstream_digest": _unit_upstream_digest(upstream, target, unit),
                "reviewed_destination_digest": _external_destination_digest(
                    unit, declaration_unit, files
                ),
            }
            if protected:
                document["verified_layout"] = RULE_LAYOUT_VALUE
            decisions.append(document)
        review = {
            "schema_version": 2,
            "upstream_repository": catalog["catalog"]["upstream_repository"],
            "transition": {
                "baseline_lock_digest": None,
                "target_source_commit": target,
                "declaration_digest": _sha256(declaration_text.encode("utf-8")),
            },
            "decisions": decisions,
        }
        return yaml.safe_dump(review, sort_keys=False)

    def _enroll(
        self,
        *,
        editor_confirmed: bool | None,
        before: dict[str, str] | None,
        fail_after_content_writes: int | None = None,
        approval: bool = True,
        after_prepare: Callable[[], None] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return self._ordered_enroll(
            editor_confirmed=editor_confirmed,
            before=before,
            prepare=self._prepare_all,
            declaration_text=BOOTSTRAP_DECLARATION,
            build_review=self._review_text,
            fail_after_content_writes=fail_after_content_writes,
            approval=approval,
            after_prepare=after_prepare,
        )

    def _commit_owner_notes(self) -> None:
        self.write(self.adopter, "OWNER-NOTES.md", "unrelated owner work\n")
        self.commit(self.adopter, "owner notes")

    def _assert_transformations(self, *, fresh: bool) -> None:
        adopter = self.adopter
        upstream = self.upstream
        destination = (adopter / "AGENTS.md").read_text(encoding="utf-8")
        source = (upstream / "AGENTS.md").read_text(encoding="utf-8")
        destination_layout, destination_violation = _scan_rule_layout(destination)
        source_layout, source_violation = _scan_rule_layout(source)
        assert destination_layout is not None, destination_violation
        assert source_layout is not None, source_violation
        assert destination_layout.mandatory == source_layout.mandatory
        assert destination_layout.extensions != source_layout.extensions
        assert b"Destination-local extension rules." in destination_layout.extensions
        assert b"Core-owned environment preferences." not in destination_layout.extensions
        agent = (adopter / ".opencode/agents/reviewer.md").read_text(encoding="utf-8")
        agent_source = (upstream / ".opencode/agents/reviewer.md").read_text(encoding="utf-8")
        agent_layout, agent_violation = _scan_rule_layout(agent)
        agent_source_layout, agent_source_violation = _scan_rule_layout(agent_source)
        assert agent_layout is not None, agent_violation
        assert agent_source_layout is not None, agent_source_violation
        assert agent_layout.mandatory == agent_source_layout.mandatory
        assert BOOTSTRAP_AGENT_EXTENSION.strip() in agent
        assert (adopter / "agents/reviewer/profile.md").read_bytes() == (
            upstream / "agents/reviewer/profile.md"
        ).read_bytes()
        assert (adopter / "skills/mirror-note.md").read_bytes() == (
            upstream / "skills/mirror-note.md"
        ).read_bytes()
        assert (adopter / "knowledge/symptoms.md").read_bytes() == (
            upstream / "knowledge/symptoms.md"
        ).read_bytes()
        assert "DEBT-001" not in (adopter / "knowledge/debt.md").read_text(encoding="utf-8")
        assert "P-001" not in (adopter / "knowledge/problems.md").read_text(encoding="utf-8")
        assert BOOTSTRAP_SOURCE_GITKEEP not in (adopter / "plans/.gitkeep").read_text(
            encoding="utf-8"
        )
        manifest = (adopter / "pyproject.toml").read_text(encoding="utf-8")
        assert "core-upstream" not in manifest
        assert "core-history" not in manifest
        assert 'name = "relay"' in manifest
        assert "[tool.relay]" in manifest
        config = json.loads((adopter / "opencode.jsonc").read_text(encoding="utf-8"))
        assert config["permission"]["bash"]["sudo *"] == "deny"
        assert (adopter / "OWNER-NOTES.md").read_text(encoding="utf-8") == (
            "unrelated owner work\n"
        )
        lock = yaml.safe_load(self.proposal_stdout)
        assert isinstance(lock, dict)
        destinations = [
            member.get("destination")
            for unit in lock["units"]
            for member in unit.get("members") or []
        ]
        assert "user-stories/index.md" not in destinations
        if fresh:
            assert (adopter / "knowledge/debt.md").read_text(encoding="utf-8") == (
                BOOTSTRAP_DEBT_HEADER
            )
            assert (adopter / "knowledge/problems.md").read_text(encoding="utf-8") == (
                BOOTSTRAP_PROBLEM_HEADER
            )
            assert (adopter / "plans/.gitkeep").read_text(encoding="utf-8") == (
                BOOTSTRAP_FRESH_GITKEEP
            )
            assert _manifest_dependencies(manifest) == list(BOOTSTRAP_EXPECTED_FRESH_DEPENDENCIES)
            assert self.collisions == []
            assert config["local"] == "fresh-custom"
        else:
            assert (adopter / "knowledge/debt.md").read_text(encoding="utf-8") == (
                BOOTSTRAP_EXISTING_DEBT
            )
            assert (adopter / "knowledge/problems.md").read_text(encoding="utf-8") == (
                BOOTSTRAP_EXISTING_PROBLEMS
            )
            assert (adopter / "plans/.gitkeep").read_text(encoding="utf-8") == (
                BOOTSTRAP_EXISTING_GITKEEP
            )
            assert 'version = "1.4.2"' in manifest
            assert 'requires-python = ">=3.11"' in manifest
            assert _manifest_dependencies(manifest) == list(
                BOOTSTRAP_EXPECTED_EXISTING_DEPENDENCIES
            )
            assert "relay-own" in (adopter / "user-stories/index.md").read_text(
                encoding="utf-8"
            )
            assert "Local trailing section" in (
                adopter / "user-stories/index.md"
            ).read_text(encoding="utf-8")
            assert self.collisions == [
                "collision: path user-stories/alpha.md; core wins",
                "collision: slug alpha; core wins",
            ]
            assert config["local"] == "existing-custom"

    def test_fresh_enrollment_freezes_approval_before_writes(self) -> None:
        self.init_bootstrap_upstream()
        self.init_repo(self.adopter)
        assert not (self.adopter / "knowledge/debt.md").exists()
        self._commit_owner_notes()
        start = len(self.command_trace)
        self._enroll(editor_confirmed=True, before=None)
        self._assert_driver_trace(start)
        self._assert_transformations(fresh=True)
        assert not (self.adopter / "node_modules").exists()

    def test_existing_enrollment_transforms_predecessor_not_final_bytes(self) -> None:
        self.init_bootstrap_upstream()
        self.init_repo(self.adopter)
        for relative, text in BOOTSTRAP_EXISTING_FILES.items():
            self.write(self.adopter, relative, text)
        self._commit_owner_notes()
        before = {
            relative: (self.adopter / relative).read_bytes()
            for relative in BOOTSTRAP_EXISTING_FILES
        }
        requirements = _skill_dependency_requirements(BOOTSTRAP_SKILL)
        once = _union_manifest_dependencies(BOOTSTRAP_EXISTING_MANIFEST, requirements)
        assert _union_manifest_dependencies(once, requirements) == once
        assert (
            _union_manifest_dependencies(BOOTSTRAP_EXISTING_MANIFEST, ())
            == BOOTSTRAP_EXISTING_MANIFEST
        )
        assert (
            _union_manifest_dependencies(
                BOOTSTRAP_EXISTING_MANIFEST,
                _skill_dependency_requirements(BOOTSTRAP_SKILL_NO_DEPENDENCIES),
            )
            == BOOTSTRAP_EXISTING_MANIFEST
        )
        start = len(self.command_trace)
        self._enroll(editor_confirmed=True, before=dict(BOOTSTRAP_EXISTING_FILES))
        self._assert_driver_trace(start)
        adopter = self.adopter
        assert (adopter / "AGENTS.md").read_bytes() != before["AGENTS.md"]
        assert (adopter / ".opencode/agents/reviewer.md").read_bytes() != before[
            ".opencode/agents/reviewer.md"
        ]
        assert (adopter / "pyproject.toml").read_bytes() != before["pyproject.toml"]
        assert (adopter / "opencode.jsonc").read_bytes() != before["opencode.jsonc"]
        assert (adopter / "user-stories/index.md").read_bytes() != before[
            "user-stories/index.md"
        ]
        for relative in BOOTSTRAP_RETAINED_PATHS:
            assert (adopter / relative).read_bytes() == before[relative]
        self._assert_transformations(fresh=False)

    def test_pin_conflict_stops_before_destination_writes(self) -> None:
        self.init_bootstrap_upstream()
        self.init_repo(self.adopter)
        predecessor = dict(BOOTSTRAP_EXISTING_FILES)
        predecessor["pyproject.toml"] = BOOTSTRAP_CONFLICT_MANIFEST
        for relative, text in predecessor.items():
            self.write(self.adopter, relative, text)
        self._commit_owner_notes()
        before = self.worktree_bytes(self.adopter)
        with pytest.raises(PinConflict):
            self._enroll(editor_confirmed=True, before=predecessor)
        assert self.worktree_bytes(self.adopter) == before
        assert not (self.adopter / ".aicore").exists()

    def test_missing_approval_stops_before_writes(self) -> None:
        self.init_bootstrap_upstream()
        self.init_repo(self.adopter)
        self._commit_owner_notes()
        before = self.worktree_bytes(self.adopter)
        with pytest.raises(FrozenReviewMissing):
            self._enroll(editor_confirmed=True, before=None, approval=False)
        assert self.worktree_bytes(self.adopter) == before
        assert "missing_approval" in self.events
        assert "write_controls" not in self.events

    def test_mid_write_failure_stops_without_restore(self) -> None:
        self.init_bootstrap_upstream()
        self.init_repo(self.adopter)
        self._commit_owner_notes()
        start = len(self.command_trace)
        with pytest.raises(PartialWriteStopped):
            self._enroll(
                editor_confirmed=True, before=None, fail_after_content_writes=1
            )
        adopter = self.adopter
        assert (adopter / ".aicore/adoption.yaml").is_file()
        assert (adopter / ".aicore/adoption-review.yaml").is_file()
        assert (adopter / "AGENTS.md").is_file()
        assert not (adopter / "user-stories/index.md").exists()
        assert not (adopter / ".aicore/adoption.lock.yaml").exists()
        assert "stop_partial" in self.events
        for argv in self.command_trace[start:]:
            assert "restore" not in argv
            assert "reset" not in argv
            assert "stash" not in argv
            assert "clean" not in argv

    @pytest.mark.parametrize(
        "kind",
        (
            "staged",
            "unstaged",
            "untracked",
            "conflict",
            "editor",
            "repository",
            "skip_worktree",
        ),
    )
    def test_dirty_destination_aborts_before_mutation(self, kind: str) -> None:
        editor_confirmed: bool | None = True
        if kind == "repository":
            self.adopter = self.root / "not-a-repo"
            self.adopter.mkdir()
        else:
            self.init_repo(self.adopter)
            self._commit_owner_notes()
            if kind == "staged":
                self.write(self.adopter, "STAGED.md", "staged\n")
                self.stage(self.adopter, "STAGED.md")
            elif kind == "unstaged":
                self.write(self.adopter, "OWNER-NOTES.md", "dirty\n")
            elif kind == "untracked":
                self.write(self.adopter, "UNTRACKED.md", "new\n")
            elif kind == "conflict":
                self.write(self.adopter, "conflict.txt", "base\n")
                self.commit(self.adopter, "base")
                self.git(self.adopter, "checkout", "-b", "other")
                self.write(self.adopter, "conflict.txt", "other\n")
                self.commit(self.adopter, "other side")
                self.git(self.adopter, "checkout", "main")
                self.write(self.adopter, "conflict.txt", "main\n")
                self.commit(self.adopter, "main side")
                self.git(self.adopter, "merge", "other", check=False)
            elif kind == "editor":
                editor_confirmed = None
            elif kind == "skip_worktree":
                self.git(self.adopter, "update-index", "--skip-worktree", "OWNER-NOTES.md")
            else:
                raise AssertionError(kind)
        before = self.worktree_bytes(self.adopter)
        start = len(self.command_trace)
        with pytest.raises(CleanStartAbort):
            self._enroll(editor_confirmed=editor_confirmed, before=None)
        assert self.worktree_bytes(self.adopter) == before
        assert "abort" in self.events
        assert "write_controls" not in self.events
        for argv in self.command_trace[start:]:
            assert "add" not in argv
            assert "commit" not in argv
            assert "stash" not in argv
            assert "reset" not in argv
            assert "clean" not in argv
            assert "restore" not in argv

    @pytest.mark.parametrize(
        "relative",
        (
            ".aicore/adoption.yaml",
            ".aicore/adoption-review.yaml",
            ".aicore/adoption.lock.yaml",
            "plans/.gitkeep",
        ),
    )
    def test_t5_existing_ignored_occupant_aborts_before_write(self, relative: str) -> None:
        self.init_repo(self.adopter)
        self._commit_owner_notes()
        self.write(self.adopter, ".gitignore", relative + "\n")
        self.commit(self.adopter, "ignore planned write")
        occupant = "ignored occupant\n"
        self.write(self.adopter, relative, occupant)
        before = self.worktree_bytes(self.adopter)
        with pytest.raises(CleanStartAbort) as caught:
            self._enroll(editor_confirmed=True, before=None)
        assert str(caught.value) == f"ignored path would be overwritten: {relative}"
        assert self.worktree_bytes(self.adopter) == before
        assert (self.adopter / relative).read_text(encoding="utf-8") == occupant
        assert "write_controls" not in self.events
        assert "unsaved" not in str(caught.value)

    def test_t5_absent_ignore_rule_is_not_unsaved_occupant(self) -> None:
        self.init_bootstrap_upstream()
        self.init_repo(self.adopter)
        self.write(self.adopter, ".gitignore", "plans/.gitkeep\n")
        self._commit_owner_notes()
        assert not (self.adopter / "plans/.gitkeep").exists()
        reason = self._preflight(self.adopter, True)
        assert reason is None
        before = self.worktree_bytes(self.adopter)
        start = len(self.command_trace)
        with pytest.raises(FrozenReviewMissing):
            self._enroll(editor_confirmed=True, before=None, approval=False)
        assert self.worktree_bytes(self.adopter) == before
        assert "missing_approval" in self.events
        assert "write_controls" not in self.events
        assert "unsaved" not in " ".join(self.events)
        for argv in self.command_trace[start:]:
            assert "-f" not in argv
            assert "add" not in argv

    def test_t4_regular_and_linked_worktree_operation_paths(self) -> None:
        self.init_repo(self.adopter)
        self._commit_owner_notes()
        regular = _resolve_git_path(str(self.adopter), "MERGE_HEAD")
        assert regular is not None
        assert Path(regular).resolve() == (self.adopter / ".git" / "MERGE_HEAD").resolve()
        linked = self.root / "linked"
        self.git(self.adopter, "worktree", "add", "--detach", str(linked), "HEAD")
        assert (linked / ".git").is_file()
        assert self._preflight(linked, True) is None
        resolved = _resolve_git_path(str(linked), "MERGE_HEAD")
        assert resolved is not None
        assert resolved != str(linked / ".git" / "MERGE_HEAD")
        assert "worktrees" in resolved
        Path(resolved).write_text(self.rev(self.adopter) + "\n", encoding="utf-8")
        status = self._read(linked, *_STATUS_ARGS)
        assert status.returncode == 0
        assert status.stdout == b""
        assert self._preflight(linked, True) == "in-progress merge"

    @pytest.mark.parametrize(
        ("name", "kind", "reason"),
        (
            ("MERGE_HEAD", "file", "in-progress merge"),
            ("CHERRY_PICK_HEAD", "file", "in-progress operation"),
            ("REVERT_HEAD", "file", "in-progress operation"),
            ("rebase-merge", "directory", "in-progress rebase"),
            ("rebase-apply", "directory", "in-progress rebase"),
            ("sequencer", "directory", "in-progress operation"),
        ),
    )
    def test_t4_unfinished_operation_aborts_with_empty_porcelain(
        self, name: str, kind: str, reason: str
    ) -> None:
        self.init_repo(self.adopter)
        self._commit_owner_notes()
        resolved = _resolve_git_path(str(self.adopter), name)
        assert resolved is not None
        target = Path(resolved)
        if kind == "file":
            target.write_text(self.rev(self.adopter) + "\n", encoding="utf-8")
        else:
            target.mkdir()
        status = self._read(self.adopter, *_STATUS_ARGS)
        assert status.returncode == 0
        assert status.stdout == b""
        before = self.worktree_bytes(self.adopter)
        with pytest.raises(CleanStartAbort) as caught:
            self._enroll(editor_confirmed=True, before=None)
        assert str(caught.value) == reason
        assert self.worktree_bytes(self.adopter) == before
        assert "write_controls" not in self.events

    def test_t4_gitfile_and_clean_bisect_are_not_dirty(self) -> None:
        self.init_repo(self.adopter)
        self._commit_owner_notes()
        regular_bisect = _resolve_git_path(str(self.adopter), "BISECT_START")
        assert regular_bisect is not None
        Path(regular_bisect).write_text(self.rev(self.adopter) + "\n", encoding="utf-8")
        assert self._preflight(self.adopter, True) is None
        linked = self.root / "linked-bisect"
        self.git(self.adopter, "worktree", "add", "--detach", str(linked), "HEAD")
        assert (linked / ".git").is_file()
        linked_bisect = _resolve_git_path(str(linked), "BISECT_START")
        assert linked_bisect is not None
        assert "worktrees" in linked_bisect
        Path(linked_bisect).write_text(self.rev(self.adopter) + "\n", encoding="utf-8")
        assert self._preflight(linked, True) is None

    def test_t6_new_work_after_prepare_is_not_restored(self) -> None:
        self.init_bootstrap_upstream()
        self.init_repo(self.adopter)
        self._commit_owner_notes()

        def contaminate() -> None:
            self.write(self.adopter, "NEW.md", "sneaky\n")

        with pytest.raises(CleanStartAbort) as caught:
            self._enroll(editor_confirmed=True, before=None, after_prepare=contaminate)
        assert "unsaved" in str(caught.value)
        assert (self.adopter / "NEW.md").read_text(encoding="utf-8") == "sneaky\n"
        assert not (self.adopter / ".aicore").exists()
        assert not (self.adopter / "AGENTS.md").exists()
        assert "write_controls" not in self.events
        assert "recheck" in self.events
        assert "recheck_before_write" not in self.events


_POLICY_MARKER = "> **Rule layout:** two-section-v1\n"
_POLICY_EXTENSIONS = _POLICY_MARKER + "## Project extensions\n"
_POLICY_ORPHAN = "orphan region: expected exactly two ownership headings"


def _policy_p17(body: str) -> str:
    """Prefix one valid literal-scalar frontmatter block without changing body bytes."""
    return (
        "---\n"
        "description: |\n"
        "  ## Fake\n"
        "  ```\n"
        "  Extra\n"
        "  ---\n"
        "  > **Rule layout:** two-section-v1\n"
        "---\n"
        + body[body.index("# Reviewer") :]
    )


class Phase01ProtectionPolicyTests(EngineTestCase):
    """Proposal and check outcomes for the Phase 1 layout defects.

    These paths exercise the protected-document helper, not only the layout
    helper. Check JSON keeps existing dispositions and does not grow a
    detailed-reason field.
    """

    def _check(self, fixture: AdopterFixture) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            str(fixture["adopter_rev"]),
            "--format",
            "json",
        )

    def _propose(self, fixture: AdopterFixture) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
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
            str(fixture["adopter_rev"]),
        )

    @pytest.mark.parametrize(
        "document",
        [
            _POLICY_EXTENSIONS + "~~~text\n~~~not-a-close\n" + PROTECTED_AGENT_MANDATORY,
            _POLICY_EXTENSIONS + "Extra\n---\n" + PROTECTED_AGENT_MANDATORY,
        ],
        ids=["P02", "P09"],
    )
    def test_invalid_destination_is_policy_violation_and_historical_drift(
        self, document: str
    ) -> None:
        assert document.endswith(PROTECTED_AGENT_MANDATORY)
        fixture = self.build_protected_agent()
        self.write(fixture["adopter"], ".opencode/agents/reviewer.md", document)
        fixture["adopter_rev"] = self.commit(
            fixture["adopter"], "invalid protected destination"
        )
        checked = self._check(fixture)
        self.assert_exit(checked, 1)
        report = json.loads(checked.stdout)
        unit = next(item for item in report["units"] if item["id"] == "reviewer-agent")
        assert unit["disposition"] == "policy_violation"
        assert "reviewer-agent: policy_violation" in report["blocking_reasons"]
        assert "detailed_reason" not in report
        assert "detailed_reason" not in unit

        self.write(
            fixture["upstream"],
            ".opencode/agents/reviewer.md",
            PROTECTED_SOURCE_AGENT.replace(
                "Source extension note.", "Newer source extension note."
            ),
        )
        self.commit(fixture["upstream"], "newer valid source")
        drifted = self._check(fixture)
        self.assert_exit(drifted, 1)
        drifted_report = json.loads(drifted.stdout)
        drifted_unit = next(
            item for item in drifted_report["units"] if item["id"] == "reviewer-agent"
        )
        assert drifted_unit["disposition"] == "local_drift"
        assert "reviewer-agent: local_drift" in drifted_report["blocking_reasons"]
        assert "detailed_reason" not in drifted_report
        assert "detailed_reason" not in drifted_unit

        _write_prepared_review(
            self,
            fixture,
            "reviewer-agent",
            "applied",
            verified_layout=RULE_LAYOUT_VALUE,
        )
        fixture["adopter_rev"] = self.commit(
            fixture["adopter"], "fresh verified layout review"
        )
        proposal = self._propose(fixture)
        self.assert_exit(proposal, 2, "policy_violation")
        self.assert_exit(proposal, 2, _POLICY_ORPHAN)
        assert proposal.stdout == ""

    def test_p17_frontmatter_proposes_and_same_snapshot_check_passes(self) -> None:
        destination = _policy_p17(PROTECTED_DESTINATION_AGENT)
        assert PROTECTED_AGENT_MANDATORY in destination
        assert PROTECTED_AGENT_MANDATORY in PROTECTED_SOURCE_AGENT
        fixture = self.build_protected_agent(destination_agent=destination, propose=False)
        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo",
            str(fixture["upstream"]),
            "--catalog",
            str(fixture["catalog"]),
            "--declaration",
            str(fixture["declaration"]),
            "--review",
            str(fixture["review"]),
            "--adopter-revision",
            str(fixture["adopter_rev"]),
        )
        self.assert_exit(proposal, 0)
        candidate = self.write(self.root, "p17-candidate.lock.yaml", proposal.stdout)
        checked = self.run_cli(
            "check",
            *self.base_check_args(fixture, lock=candidate),
            "--adopter-revision",
            str(fixture["adopter_rev"]),
            "--format",
            "json",
        )
        self.assert_exit(checked, 0)
        report = json.loads(checked.stdout)
        assert report["compliance"] is True
        assert report["units"][0]["disposition"] == "current"
        assert "detailed_reason" not in report

    def test_malformed_source_remains_fatal_invalid_mapping(self) -> None:
        fixture = self.build_protected(
            PROTECTED_AGENT_CATALOG,
            PROTECTED_AGENT_DECLARATION,
            {
                ".opencode/agents/reviewer.md": (
                    _POLICY_EXTENSIONS + "~~~text\n~~~not-a-close\n" + PROTECTED_AGENT_MANDATORY
                ),
                "agents/reviewer/profile.md": PROTECTED_AGENT_PROFILE,
            },
            {
                ".opencode/agents/reviewer.md": PROTECTED_DESTINATION_AGENT,
                "agents/reviewer/profile.md": PROTECTED_AGENT_PROFILE,
            },
            "reviewer-agent",
            propose=False,
        )
        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo",
            str(fixture["upstream"]),
            "--catalog",
            str(fixture["catalog"]),
            "--declaration",
            str(fixture["declaration"]),
            "--review",
            str(fixture["review"]),
            "--adopter-revision",
            str(fixture["adopter_rev"]),
        )
        self.assert_exit(proposal, 2, "invalid_mapping")
        assert proposal.stdout == ""


_REAL_CATALOG_ROOT_UNIT = "root-runtime-spec"
_REAL_CATALOG_ADAPTED_UNITS = frozenset({"knowledge-debt", "symptom-problem-register"})
_REAL_CATALOG_STORY_KIND = "user-story"
_REAL_CATALOG_COPY_SKIP = frozenset({"__pycache__", ".git"})


def _real_catalog_excluded(relative: Path) -> bool:
    """Return whether a copied corpus path is generated rather than source."""
    return any(
        part in _REAL_CATALOG_COPY_SKIP or part.endswith(".pyc")
        for part in relative.parts
    )


def _real_catalog_members(unit: dict[str, object]) -> list[dict[str, str]]:
    """Map one catalog unit's member ids to their declared destination paths."""
    return [
        {"id": str(member["id"]), "destination": str(member["destination"])}
        for member in cast(list[dict[str, object]], unit["members"])
    ]


def _real_catalog_assertions(
    catalog: dict[str, object], unit_id: str
) -> list[dict[str, object]]:
    """Return one catalog config unit's reviewed assertion entries."""
    unit = next(
        item
        for item in cast(list[dict[str, object]], catalog["units"])
        if str(item["id"]) == unit_id
    )
    return list(cast(list[dict[str, object]], unit.get("assertions", [])))


def _real_catalog_bash_fragment(catalog: dict[str, object]) -> dict[str, str]:
    """Build the destination bash mapping from the catalog's key/value assertions.

    The opencode-config assertions are JSON ``key: value`` fragments, so the
    destination fragment is a projection of the catalog rather than a
    hand-copied token table. A renamed or reformatted assertion fails here.
    """
    fragment: dict[str, str] = {}
    for assertion in _real_catalog_assertions(catalog, "opencode-config"):
        contains = str(assertion["contains"])
        parsed = json.loads("{" + contains + "}")
        if not isinstance(parsed, dict) or len(parsed) != 1:
            raise AssertionError(
                f"opencode-config assertion {assertion['id']!r} is not a key/value pair"
            )
        for key, value in parsed.items():
            if not isinstance(key, str) or not isinstance(value, str):
                raise AssertionError(
                    f"opencode-config assertion {assertion['id']!r} is not a string pair"
                )
            fragment[key] = value
    return fragment


def _real_catalog_gitignore_fragment(catalog: dict[str, object]) -> str:
    """Build the destination ignore lines from the catalog's ignore assertions."""
    lines = [
        str(assertion["contains"])
        for assertion in _real_catalog_assertions(catalog, "gitignore-config")
    ]
    return "\n".join(lines) + "\n"


def _real_catalog_opencode_config(catalog: dict[str, object]) -> str:
    """A destination config carrying the catalog's reviewed assertions."""
    return (
        json.dumps(
            {"permission": {"bash": _real_catalog_bash_fragment(catalog)}},
            indent=2,
        )
        + "\n"
    )


def _real_catalog_runner_config(catalog: dict[str, object]) -> str:
    """A destination config with the catalog assertions plus the executor grant."""
    return (
        json.dumps(
            {
                "permission": {"bash": _real_catalog_bash_fragment(catalog)},
                "agent": {
                    str(AICORE_RUNNER["executor"]): {
                        "permission": {
                            "bash": {
                                "*": "deny",
                                AICORE_SUITE_COMMAND: "allow",
                            }
                        }
                    }
                },
            },
            indent=2,
        )
        + "\n"
    )


def _real_catalog_gitignore(catalog: dict[str, object]) -> str:
    """A destination .gitignore carrying the catalog's reviewed ignore assertions."""
    return _real_catalog_gitignore_fragment(catalog)


class RealCatalogEnrollmentTests(EngineTestCase, OrderedEnrollmentDriverMixin):
    """Fresh and existing enrollment against the shipped catalog and real corpus.

    Both flows drive the shared ordered driver. The fresh flow uses the null
    baseline and a reviewed whole-project ``test_runner`` with its literal
    destination grant; the existing flow accepts a predecessor lock and then
    reviews a transition bound to that baseline. Everything is built under
    ``tmp_path`` and the real checkout is only read.
    """

    def _copy_source_to(
        self, base: Path, source: str, destination: str, repository: Path
    ) -> None:
        origin = repository / source
        target = self._confined_path(base / destination, "catalog copy target")
        if origin.is_dir():
            for path in sorted(origin.rglob("*")):
                if not path.is_file():
                    continue
                relative = path.relative_to(origin)
                if _real_catalog_excluded(relative):
                    continue
                written = self._confined_path(
                    base / f"{destination.rstrip('/')}/{relative.as_posix()}",
                    "catalog copy target",
                )
                written.parent.mkdir(parents=True, exist_ok=True)
                written.write_bytes(path.read_bytes())
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(origin.read_bytes())

    def _profile(self) -> dict[str, bool]:
        return {"backend_stack": True, "python_scripts": True, "ticket_system": True}

    def _init_real_catalog(self) -> tuple[dict[str, object], dict[str, bool]]:
        """Copy the shipped catalog and complete corpus into the temporary upstream."""
        repository = repository_root()
        catalog_text = (repository / CATALOG_REL).read_text(encoding="utf-8")
        catalog = yaml.safe_load(catalog_text)
        assert isinstance(catalog, dict)
        profile = self._profile()
        self.init_repo(self.upstream)
        self.write(self.upstream, CATALOG_REL, catalog_text)
        self._real_catalog_source(catalog, profile, repository)
        self.commit(self.upstream, "shipped catalog source")
        return catalog, profile

    def _real_catalog_declaration(
        self,
        catalog: dict[str, object],
        profile: dict[str, bool],
        test_runner: dict[str, object],
    ) -> dict[str, object]:
        """Declare every catalog unit at the reviewed profile and runner."""
        units: list[dict[str, object]] = []
        for unit in cast(list[dict[str, object]], catalog["units"]):
            uid = str(unit["id"])
            if not evaluate_applicability(unit, profile):
                units.append({"id": uid, "mode": "not_applicable"})
            elif uid == _REAL_CATALOG_ROOT_UNIT:
                units.append(
                    {"id": uid, "mode": "adapted", "members": _real_catalog_members(unit)}
                )
            elif unit.get("sync_projection") == "assertions":
                units.append({"id": uid, "mode": "mirror"})
            elif uid in _REAL_CATALOG_ADAPTED_UNITS:
                units.append(
                    {"id": uid, "mode": "adapted", "members": _real_catalog_members(unit)}
                )
            else:
                units.append(
                    {"id": uid, "mode": "mirror", "members": _real_catalog_members(unit)}
                )
        return {
            "schema_version": 2,
            "upstream_repository": cast(
                dict[str, object], catalog["catalog"]
            )["upstream_repository"],
            "profile": profile,
            "test_runner": test_runner,
            "units": units,
        }

    def _real_catalog_source(
        self, catalog: dict[str, object], profile: dict[str, bool], repository: Path
    ) -> None:
        """Copy the complete applicable corpus into the temporary upstream."""
        for unit in cast(list[dict[str, object]], catalog["units"]):
            if not evaluate_applicability(unit, profile):
                continue
            if unit.get("sync_projection") == "assertions":
                continue
            for member in cast(list[dict[str, object]], unit["members"]):
                source = str(member["source"])
                self._copy_source_to(self.upstream, source, source, repository)
        self._copy_source_to(
            self.upstream,
            "user-stories/index.md",
            "user-stories/index.md",
            repository,
        )

    def _read_tree(self, origin: Path, destination: str, prepared: dict[str, str]) -> None:
        """Read one member (file or tree) from the selected source into buffers."""
        if origin.is_dir():
            for path in sorted(origin.rglob("*")):
                if not path.is_file():
                    continue
                relative = path.relative_to(origin)
                if _real_catalog_excluded(relative):
                    continue
                rendered = f"{destination.rstrip('/')}/{relative.as_posix()}"
                prepared[rendered] = path.read_text(encoding="utf-8")
        else:
            prepared[destination] = origin.read_text(encoding="utf-8")

    def _real_catalog_prepare(
        self,
        catalog: dict[str, object],
        declaration: dict[str, object],
        profile: dict[str, bool],
        before: dict[str, str] | None,
        test_runner: dict[str, object],
    ) -> tuple[dict[str, str], list[str]]:
        """Prepare every destination result outside the destination.

        Protected documents mirror the selected source; the root and the
        destination-owned registers are prepared from destination identity and
        structural headers; the story index is merged from the source rows.
        """
        before_map = before or {}
        declarations = {
            str(unit["id"]): unit
            for unit in cast(list[dict[str, object]], declaration["units"])
        }
        prepared: dict[str, str] = {}
        prepared["AGENTS.md"] = _prepare_root(
            (self.upstream / "AGENTS.md").read_text(encoding="utf-8"),
            before_map.get("AGENTS.md"),
        )
        debt_source = (self.upstream / "knowledge/debt.md").read_text(encoding="utf-8")
        prepared["knowledge/debt.md"] = _enroll_member(
            before_map.get("knowledge/debt.md"), debt_source, REAL_CATALOG_DEBT_HEADER
        )
        symptoms_source = (self.upstream / "knowledge/symptoms.md").read_text(
            encoding="utf-8"
        )
        problems_source = (self.upstream / "knowledge/problems.md").read_text(
            encoding="utf-8"
        )
        prepared["knowledge/symptoms.md"] = _enroll_member(
            before_map.get("knowledge/symptoms.md"),
            symptoms_source,
            REAL_CATALOG_SYMPTOMS,
        )
        prepared["knowledge/problems.md"] = _enroll_member(
            before_map.get("knowledge/problems.md"),
            problems_source,
            REAL_CATALOG_PROBLEM_HEADER,
        )
        for unit in cast(list[dict[str, object]], catalog["units"]):
            uid = str(unit["id"])
            if not evaluate_applicability(unit, profile):
                continue
            if unit.get("sync_projection") == "assertions":
                continue
            if uid == _REAL_CATALOG_ROOT_UNIT or uid in _REAL_CATALOG_ADAPTED_UNITS:
                continue
            declared = {
                str(member["id"]): str(member["destination"])
                for member in cast(
                    list[dict[str, object]], declarations[uid].get("members", [])
                )
            }
            for member in cast(list[dict[str, object]], unit["members"]):
                source = str(member["source"])
                destination = declared[str(member["id"])]
                self._read_tree(self.upstream / source, destination, prepared)
        if test_runner.get("no_tests") is True:
            prepared["opencode.jsonc"] = _real_catalog_opencode_config(catalog)
        else:
            prepared["opencode.jsonc"] = _real_catalog_runner_config(catalog)
        prepared[".gitignore"] = _real_catalog_gitignore(catalog)
        story_members = self._real_catalog_story_members(catalog, declaration)
        core_index = (self.upstream / "user-stories/index.md").read_text(encoding="utf-8")
        before_index = before_map.get("user-stories/index.md")
        merged, collisions = merge_story_index(
            core_index.encode("utf-8"),
            None if before_index is None else before_index.encode("utf-8"),
            story_members,
        )
        prepared["user-stories/index.md"] = merged.decode("utf-8")
        return prepared, collisions

    def _real_catalog_story_members(
        self, catalog: dict[str, object], declaration: dict[str, object]
    ) -> list[StoryMergeMember]:
        """Collect the applicable portable story rows for the index merge."""
        declarations = {
            str(unit["id"]): unit
            for unit in cast(list[dict[str, object]], declaration["units"])
        }
        members: list[StoryMergeMember] = []
        for unit in cast(list[dict[str, object]], catalog["units"]):
            if unit.get("kind") != _REAL_CATALOG_STORY_KIND:
                continue
            decl_unit = declarations[str(unit["id"])]
            if decl_unit.get("mode") == "not_applicable":
                continue
            declared = {
                str(member["id"]): str(member["destination"])
                for member in cast(
                    list[dict[str, object]], decl_unit.get("members", [])
                )
            }
            for member in cast(list[dict[str, object]], unit["members"]):
                policy = member.get("collision_policy")
                members.append(
                    {
                        "id": str(member["id"]),
                        "destination": declared[str(member["id"])],
                        "collision_policy": (
                            str(policy) if policy is not None else None
                        ),
                    }
                )
        return members

    def _real_catalog_review(
        self,
        catalog: dict[str, object],
        declaration_text: str,
        prepared: dict[str, str],
        *,
        target: str,
        baseline_lock_digest: str | None,
    ) -> str:
        """Bind each protected or reconciled unit to the prepared result."""
        declaration = yaml.safe_load(declaration_text)
        assert isinstance(declaration, dict)
        upstream = _GitRepo(str(self.upstream))
        files = {
            relative: ("100644", text.encode("utf-8"))
            for relative, text in prepared.items()
        }
        declarations = {
            str(unit["id"]): unit
            for unit in cast(list[dict[str, object]], declaration["units"])
        }
        decisions: list[dict[str, object]] = []
        for unit in cast(list[dict[str, object]], catalog["units"]):
            uid = str(unit["id"])
            decl_unit = declarations[uid]
            mode = str(decl_unit.get("mode"))
            protected = bool(unit.get("rule_documents"))
            if mode == "not_applicable":
                continue
            if not (
                protected or mode in ("adapted", "replacement", "destination_owned")
            ):
                continue
            document: dict[str, object] = {
                "unit": uid,
                "decision": "applied",
                "reviewer": "test-suite",
                "evidence": (
                    "Reviewed the shipped catalog unit against the prepared destination."
                ),
                "reviewed_upstream_digest": _unit_upstream_digest(upstream, target, unit),
                "reviewed_destination_digest": _external_unit_digest(
                    unit, decl_unit, files
                ),
            }
            if protected:
                document["verified_layout"] = RULE_LAYOUT_VALUE
            decisions.append(document)
        review = {
            "schema_version": 2,
            "upstream_repository": cast(
                dict[str, object], catalog["catalog"]
            )["upstream_repository"],
            "transition": {
                "baseline_lock_digest": baseline_lock_digest,
                "target_source_commit": target,
                "declaration_digest": _sha256(declaration_text.encode("utf-8")),
            },
            "decisions": decisions,
        }
        return yaml.safe_dump(review, sort_keys=False)

    def _worktree_text(self, repo: Path) -> dict[str, str]:
        """Read destination text so a transition can retain owner register bytes."""
        return {
            str(path.relative_to(repo)): path.read_text(encoding="utf-8")
            for path in repo.rglob("*")
            if path.is_file() and path.relative_to(repo).parts[0] != ".git"
        }

    def _assert_real_catalog_enrolled(self, catalog: dict[str, object]) -> None:
        """Assert the complete applicable corpus is enrolled as protected."""
        adopter = self.adopter
        lock = yaml.safe_load(self.proposal_stdout)
        assert isinstance(lock, dict)
        modes = {str(row["id"]): str(row.get("mode")) for row in lock["units"]}
        assert modes[_REAL_CATALOG_ROOT_UNIT] == "adapted"
        assert modes["knowledge-debt"] == "adapted"
        assert modes["symptom-problem-register"] == "adapted"
        rule_documents = sorted(
            {
                str(document)
                for unit in cast(list[dict[str, object]], catalog["units"])
                for document in (unit.get("rule_documents") or [])
            }
        )
        assert rule_documents, "the real catalog must declare protected rule documents"
        for document in rule_documents:
            destination = (adopter / document).read_text(encoding="utf-8")
            source = (self.upstream / document).read_text(encoding="utf-8")
            destination_layout, destination_violation = _scan_rule_layout(destination)
            source_layout, source_violation = _scan_rule_layout(source)
            assert destination_layout is not None, (document, destination_violation)
            assert source_layout is not None, (document, source_violation)
            assert destination_layout.mandatory == source_layout.mandatory, document
        debt = (adopter / "knowledge/debt.md").read_text(encoding="utf-8")
        problems = (adopter / "knowledge/problems.md").read_text(encoding="utf-8")
        assert "DEBT-001" not in debt
        assert "P-001" not in problems
        index = (adopter / "user-stories/index.md").read_text(encoding="utf-8")
        assert "aicore-adoption-sync" not in index
        assert "`plan-enforce`" in index
        assert (adopter / "OWNER-NOTES.md").read_text(encoding="utf-8") == (
            "unrelated owner work\n"
        )

    def test_real_catalog_fresh_enrollment_orders_runner_flow(self) -> None:
        catalog, profile = self._init_real_catalog()
        declaration = self._real_catalog_declaration(catalog, profile, AICORE_RUNNER)
        declaration_text = yaml.safe_dump(declaration, sort_keys=False)
        self.init_repo(self.adopter)
        self.write(self.adopter, "OWNER-NOTES.md", "unrelated owner work\n")
        self.commit(self.adopter, "owner notes")
        start = len(self.command_trace)
        self._ordered_enroll(
            editor_confirmed=True,
            before=None,
            prepare=lambda before: self._real_catalog_prepare(
                catalog, declaration, profile, before, AICORE_RUNNER
            ),
            declaration_text=declaration_text,
            build_review=lambda prepared, text: self._real_catalog_review(
                catalog,
                text,
                prepared,
                target=self.rev(self.upstream),
                baseline_lock_digest=None,
            ),
        )
        self._assert_driver_trace(start)
        self._assert_real_catalog_enrolled(catalog)
        config = json.loads((self.adopter / "opencode.jsonc").read_text(encoding="utf-8"))
        executor = str(AICORE_RUNNER["executor"])
        bash = config["agent"][executor]["permission"]["bash"]
        assert bash["*"] == "deny"
        assert bash[AICORE_SUITE_COMMAND] == "allow"

    def test_real_catalog_existing_enrollment_transitions_ordered(self) -> None:
        catalog, profile = self._init_real_catalog()
        declaration = self._real_catalog_declaration(catalog, profile, NO_TESTS_RUNNER)
        declaration_text = yaml.safe_dump(declaration, sort_keys=False)
        self.init_repo(self.adopter)
        self.write(self.adopter, "OWNER-NOTES.md", "unrelated owner work\n")
        self.commit(self.adopter, "owner notes")
        # Predecessor: the same ordered driver accepts the complete enrollment.
        self._ordered_enroll(
            editor_confirmed=True,
            before=None,
            prepare=lambda before: self._real_catalog_prepare(
                catalog, declaration, profile, before, NO_TESTS_RUNNER
            ),
            declaration_text=declaration_text,
            build_review=lambda prepared, text: self._real_catalog_review(
                catalog,
                text,
                prepared,
                target=self.rev(self.upstream),
                baseline_lock_digest=None,
            ),
        )
        self.commit(self.adopter, "accept predecessor lock")
        # An existing destination-owned register keeps local rows across the
        # reviewed transition; the source registers are never copied in.
        self.write(
            self.adopter,
            "knowledge/debt.md",
            REAL_CATALOG_DEBT_HEADER + "\nDEBT-014 Relay keeps this local deferral.\n",
        )
        self.write(
            self.adopter,
            "knowledge/problems.md",
            REAL_CATALOG_PROBLEM_HEADER
            + "\nP-014 Relay keeps this local problem row.\n",
        )
        self.commit(self.adopter, "owner register rows")
        baseline_lock_digest = _raw_file_digest(
            str(self.adopter / ".aicore/adoption.lock.yaml")
        )
        advanced = (self.upstream / "knowledge/agents.md").read_text(encoding="utf-8")
        self.write(
            self.upstream,
            "knowledge/agents.md",
            advanced + "\nTRANSITION_MANDATORY_LINE\n",
        )
        self.commit(self.upstream, "advance protected rule document")
        before = self._worktree_text(self.adopter)
        start = len(self.command_trace)
        self._ordered_enroll(
            editor_confirmed=True,
            before=before,
            prepare=lambda current: self._real_catalog_prepare(
                catalog, declaration, profile, current, NO_TESTS_RUNNER
            ),
            declaration_text=declaration_text,
            build_review=lambda prepared, text: self._real_catalog_review(
                catalog,
                text,
                prepared,
                target=self.rev(self.upstream),
                baseline_lock_digest=baseline_lock_digest,
            ),
            baseline_lock=True,
        )
        self._assert_driver_trace(start)
        self._assert_real_catalog_enrolled(catalog)
        debt = (self.adopter / "knowledge/debt.md").read_text(encoding="utf-8")
        problems = (self.adopter / "knowledge/problems.md").read_text(encoding="utf-8")
        assert "DEBT-014" in debt
        assert "P-014" in problems
        lock = yaml.safe_load(self.proposal_stdout)
        assert isinstance(lock, dict)
        assert lock["accepted_source_commit"] == self.rev(self.upstream)
        declaration_document = yaml.safe_load(
            (self.adopter / ".aicore/adoption.yaml").read_text(encoding="utf-8")
        )
        assert declaration_document["test_runner"]["no_tests"] is True
