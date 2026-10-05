"""Review-evidence and prepared first-adoption snapshot tests."""

from __future__ import annotations

import json
import subprocess
from typing import cast

import pytest
import yaml

from adoption_test_repos import AdopterFixture, EngineTestCase

from adoption_content import (
    _destination_unit_digest,
    _unit_upstream_digest,
)
from adoption_contracts import CheckReport, SyncError
from adoption_mapping import _rule_document_destination
from adoption_digests import unit_digest
from adoption_git import (
    _GitRepo,
    _RevisionSnapshot,
)
from adoption_loaders import _raw_file_digest
from adoption_test_acceptance_data import (
    ADAPTED_RULEBOOK,
    MIXED_CATALOG,
)
from adoption_test_data import (
    CATALOG_REL,
    EMPTY_REVIEW,
    TWO_UNIT_DECISION_REVIEW,
    member_file,
    review_with_transition,
)


class PreparedUpdateSnapshotTests(EngineTestCase):
    """Prepared update snapshots; no test executes the prose migration skill."""

    def _propose_args(self, fixture: AdopterFixture, *extra: str) -> list[str]:
        return [
            "propose-lock",
            "--upstream-repo",
            str(fixture["upstream"]),
            "--catalog",
            CATALOG_REL,
            "--declaration",
            str(fixture["declaration"]),
            "--review",
            str(fixture["review"]),
            "--lock",
            str(fixture["lock"]),
            "--adopter-revision",
            str(fixture["adopter_rev"]),
            *extra,
        ]

    def _check_json(self, fixture: AdopterFixture) -> CheckReport:
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            str(fixture["adopter_rev"]),
            "--format",
            "json",
        )
        self.assert_exit(proc, 0)
        report = json.loads(proc.stdout)
        assert isinstance(report, dict)
        assert set(report) == {
            "compliance",
            "accepted_revision",
            "required_revision",
            "diagnostic",
            "units",
            "catalog_transition",
            "collisions",
            "blocking_reasons",
        }
        assert isinstance(report["compliance"], bool)
        assert isinstance(report["accepted_revision"], str)
        assert isinstance(report["required_revision"], str)
        assert isinstance(report["diagnostic"], bool)
        assert isinstance(report["units"], list)
        for unit in report["units"]:
            assert isinstance(unit, dict)
            assert {"id", "mode", "upstream_delta", "destination_delta", "disposition"}.issubset(unit)
            assert set(unit).issubset({
                "id", "mode", "retired", "upstream_delta", "destination_delta", "disposition"
            })
            assert isinstance(unit["id"], str)
            assert unit["mode"] is None or isinstance(unit["mode"], str)
            assert unit["upstream_delta"] is None or isinstance(unit["upstream_delta"], str)
            assert unit["destination_delta"] is None or isinstance(unit["destination_delta"], str)
            assert isinstance(unit["disposition"], str)
            assert "retired" not in unit or isinstance(unit["retired"], bool)
        transition = report["catalog_transition"]
        assert isinstance(transition, dict)
        assert set(transition) == {"added_units", "removed_units", "changed_units"}
        assert all(isinstance(transition[name], list) for name in transition)
        assert all(isinstance(unit_id, str) for unit_id in transition["added_units"])
        assert all(isinstance(unit_id, str) for unit_id in transition["removed_units"])
        for changed in transition["changed_units"]:
            assert isinstance(changed, dict)
            assert set(changed) == {
                "id", "added_members", "removed_members", "changed_members",
                "applicability_changed", "accepted_applicable", "target_applicable",
                "accepted_mode", "target_mode",
            }
            assert isinstance(changed["id"], str)
            assert all(isinstance(changed[name], list) for name in (
                "added_members", "removed_members", "changed_members"
            ))
            assert all(isinstance(value, str) for name in (
                "added_members", "removed_members", "changed_members"
            ) for value in changed[name])
            assert all(isinstance(changed[name], bool) for name in (
                "applicability_changed", "accepted_applicable", "target_applicable"
            ))
            assert changed["accepted_mode"] is None or isinstance(changed["accepted_mode"], str)
            assert changed["target_mode"] is None or isinstance(changed["target_mode"], str)
        assert all(isinstance(value, str) for value in report["collisions"])
        assert all(isinstance(value, str) for value in report["blocking_reasons"])
        return cast(CheckReport, report)

    def test_modes_and_review_are_recorded_before_any_core_byte_is_staged(self) -> None:
        fixture = self.build_mixed_mode()
        adopter = fixture["adopter"]
        owner_names = self.git(
            adopter, "ls-tree", "-r", "--name-only", fixture["owner_commit"]
        ).stdout.splitlines()
        assert ".aicore/adoption.yaml" not in owner_names
        assert ".aicore/adoption-review.yaml" not in owner_names
        assert "user-stories/alpha.md" not in owner_names
        control_names = self.git(
            adopter, "ls-tree", "-r", "--name-only", fixture["control_commit"]
        ).stdout.splitlines()
        assert sorted(control_names) == sorted(
            [
                ".aicore/adoption-review.yaml",
                ".aicore/adoption.yaml",
                "AGENTS.md",
                "agents/helper/profile.md",
                "skills/rules.md",
                "user-stories/index.md",
            ]
        )
        assert "user-stories/alpha.md" not in control_names
        declaration = yaml.safe_load(
            self.git(adopter, "show", f"{fixture['control_commit']}:.aicore/adoption.yaml").stdout
        )
        catalog = yaml.safe_load(MIXED_CATALOG)
        assert [unit["id"] for unit in declaration["units"]] == [
            unit["id"] for unit in catalog["units"]
        ], "every catalog unit must be classified before the first copy"
        modes = {unit["id"]: unit["mode"] for unit in declaration["units"]}
        assert modes == {
            "rulebook": "adapted",
            "helper-agent": "replacement",
            "root-runtime-spec": "adapted",
            "portable-stories-always": "mirror",
            "portable-stories-ticket": "not_applicable",
        }
        review = yaml.safe_load(
            self.git(adopter, "show", f"{fixture['control_commit']}:.aicore/adoption-review.yaml").stdout
        )
        assert [decision["unit"] for decision in review["decisions"]] == ["root-runtime-spec", "rulebook", "helper-agent"]
        rules_at_control = self.git(
            adopter, "show", f"{fixture['control_commit']}:skills/rules.md"
        ).stdout
        assert rules_at_control == ADAPTED_RULEBOOK
        parent = self.git(adopter, "rev-parse", f"{fixture['staged_commit']}^").stdout.strip()
        assert parent == fixture["control_commit"]
        staged_names = self.git(
            adopter, "ls-tree", "-r", "--name-only", fixture["staged_commit"]
        ).stdout.splitlines()
        assert "user-stories/alpha.md" in staged_names

    def test_mixed_mode_fixture_passes_check_with_recorded_decisions(self) -> None:
        fixture = self.build_mixed_mode()
        report = self._check_json(fixture)
        assert report["compliance"]
        dispositions = {unit["id"]: unit["disposition"] for unit in report["units"]}
        assert dispositions == {
            "rulebook": "current",
            "helper-agent": "current",
            "root-runtime-spec": "current",
            "portable-stories-always": "current",
            "portable-stories-ticket": "not_applicable",
        }
        assert report["collisions"] == []

    def test_unreviewed_differing_non_mirror_blocks_propose_before_stdout(self) -> None:
        fixture = self.build_mixed_mode()
        self.write(fixture["upstream"], "skills/rules.md", "core rulebook v2\n")
        self.commit(fixture["upstream"], "rulebook v2")
        # Bind the recorded review to the baseline lock so the freshness check
        # reaches the stale rulebook decision instead of the transition binding.
        recorded = yaml.safe_load(fixture["review"].read_text(encoding="utf-8"))
        recorded["transition"] = {
            "baseline_lock_digest": _raw_file_digest(str(fixture["lock"])),
            "target_source_commit": self.rev(fixture["upstream"]),
            "declaration_digest": _raw_file_digest(str(fixture["declaration"])),
        }
        fixture["review"].write_text(
            yaml.safe_dump(recorded, sort_keys=False), encoding="utf-8"
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "bind review to baseline")
        blocked = self.run_cli(*self._propose_args(fixture))
        self.assert_exit(blocked, 2, "review_changed")
        assert "rulebook" in blocked.stderr
        assert blocked.stdout == "", "no lock YAML may reach stdout before the decision is recorded"
        ReviewEvidenceTests.write_fresh_review(self, fixture, "rulebook", "applied")
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "rulebook decision recorded")
        proposal = self.run_cli(*self._propose_args(fixture))
        self.assert_exit(proposal, 0)
        assert "schema_version: 2" in proposal.stdout
        self.write(fixture["adopter"], ".aicore/adoption.lock.yaml", proposal.stdout)
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "reviewed lock")
        report = self._check_json(fixture)
        assert report["compliance"], report["blocking_reasons"]

    def test_adapted_bytes_survive_a_careful_edit(self) -> None:
        fixture = self.build_mixed_mode()
        adopter = fixture["adopter"]
        rules_path = adopter / "skills/rules.md"
        core_bytes = (fixture["upstream"] / "skills/rules.md").read_bytes()
        reviewed = rules_path.read_bytes()
        assert reviewed == ADAPTED_RULEBOOK.encode("utf-8")
        assert reviewed != core_bytes, "the adapted destination must differ from the core bytes"
        edited = reviewed + b"# Reviewed local extension.\n"
        rules_path.write_bytes(edited)
        fixture["adopter_rev"] = self.commit(adopter, "careful adapted edit")
        ReviewEvidenceTests.write_fresh_review(self, fixture, "rulebook", "applied")
        fixture["adopter_rev"] = self.commit(adopter, "reviewed adapted edit")
        proposal = self.run_cli(*self._propose_args(fixture))
        self.assert_exit(proposal, 0)
        lock = yaml.safe_load(proposal.stdout)
        rulebook_row = next(row for row in lock["units"] if row["id"] == "rulebook")
        assert rulebook_row["accepted_upstream_digest"] == unit_digest(
            [("rules", member_file("core rulebook v1\n"))]
        ), "the lock must keep binding the upstream digest, not destination bytes"
        assert rulebook_row["members"][0]["accepted_destination_digest"] == member_file(
            edited.decode("utf-8")
        ), "the lock must record the reviewed destination bytes, never core bytes"
        self.write(adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
        fixture["adopter_rev"] = self.commit(adopter, "lock after edit")
        before_check = self.worktree_bytes(adopter)
        report = self._check_json(fixture)
        assert report["compliance"], report["blocking_reasons"]
        assert rules_path.read_bytes() == edited
        assert self.worktree_bytes(adopter) == before_check

    def test_only_applicable_story_units_arrive_and_index_bytes_survive(self) -> None:
        fixture = self.build_mixed_mode()
        adopter = fixture["adopter"]
        index_path = adopter / "user-stories/index.md"
        index_before = index_path.read_bytes()
        assert (adopter / "user-stories/alpha.md").read_bytes() == b"alpha v1\n"
        assert not (adopter / "user-stories/gamma.md").exists()
        report = self._check_json(fixture)
        assert report["collisions"] == []
        ticket = next(unit for unit in report["units"] if unit["id"] == "portable-stories-ticket")
        assert ticket["disposition"] == "not_applicable"
        fixture["review"].write_text(
            review_with_transition(
                EMPTY_REVIEW,
                self.rev(fixture["upstream"]),
                fixture["declaration"].read_text(encoding="utf-8"),
                _raw_file_digest(str(fixture["lock"])),
            ),
            encoding="utf-8",
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "fresh transition")
        proposal = self.run_cli(*self._propose_args(fixture))
        self.assert_exit(proposal, 0)
        assert index_path.read_bytes() == index_before
        assert b"| `dest-own` | Destination owned |" in index_before
        assert index_before.endswith(b"Local trailing section that must survive byte-for-byte.\n")
        assert b"| `gamma` |" not in index_before


class ReviewEvidenceTests(EngineTestCase):
    @staticmethod
    def write_fresh_review(
        case: EngineTestCase,
        fixture: AdopterFixture,
        unit_id: str,
        decision: str,
        **overrides: str,
    ) -> None:
        catalog = yaml.safe_load(fixture["catalog"].read_text(encoding="utf-8"))
        declaration = yaml.safe_load(
            fixture["declaration"].read_text(encoding="utf-8")
        )
        lock = yaml.safe_load(fixture["lock"].read_text(encoding="utf-8"))
        unit = next(item for item in catalog["units"] if item["id"] == unit_id)
        declaration_unit = next(
            item for item in declaration["units"] if item["id"] == unit_id
        )
        target = case.rev(fixture["upstream"])
        source = _unit_upstream_digest(
            _GitRepo(str(fixture["upstream"])), target, unit
        )
        result = _destination_unit_digest(
            unit,
            declaration_unit,
            _RevisionSnapshot(
                _GitRepo(str(fixture["adopter"])), fixture["adopter_rev"]
            ),
        )
        transition = {
            "baseline_lock_digest": _raw_file_digest(str(fixture["lock"])),
            "target_source_commit": target,
            "declaration_digest": _raw_file_digest(str(fixture["declaration"])),
        }
        for key in ("baseline_lock_digest", "target_source_commit", "declaration_digest"):
            if key in overrides:
                transition[key] = overrides[key]
        document = {
            "schema_version": 2,
            "upstream_repository": catalog["catalog"]["upstream_repository"],
            "transition": transition,
            "decisions": [{
                "unit": unit_id, "decision": decision, "reviewer": "reviewer",
                "evidence": "reviewed prepared bytes",
                "reviewed_upstream_digest": overrides.get("reviewed_upstream_digest", source),
                "reviewed_destination_digest": overrides.get("reviewed_destination_digest", result),
            }],
        }
        case.write(
            fixture["adopter"], ".aicore/adoption-review.yaml", yaml.safe_dump(document, sort_keys=False)
        )

    def _propose(self, fixture: AdopterFixture) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", CATALOG_REL,
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        )

    def test_review_decision_for_unknown_unit_is_invalid_declaration(self) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        self.write(
            fixture["adopter"],
            ".aicore/adoption-review.yaml",
            """schema_version: 2
upstream_repository: example/upstream
decisions:
  - unit: ghost
    decision: applied
    reviewer: reviewer
""",
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "unknown decision unit")

        proposal = self._propose(fixture)

        self.assert_exit(proposal, 2, "invalid_declaration")
        assert proposal.stdout == ""

    def test_changed_non_mirror_without_legacy_decision_requires_review(self) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        checked = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            fixture["adopter_rev"],
            "--format",
            "json",
        )
        self.assert_exit(checked, 1)
        report = json.loads(checked.stdout)
        note = next(unit for unit in report["units"] if unit["id"] == "note")
        assert note["disposition"] == "review_required"
        self.assert_exit(self._propose(fixture), 2, "review_changed")

    def test_legacy_unit_only_decision_is_readable_but_cannot_authorize_new_change(self) -> None:
        fixture = self.build_two_unit(TWO_UNIT_DECISION_REVIEW)
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert report["compliance"] is False
        note = next(unit for unit in report["units"] if unit["id"] == "note")
        assert note["disposition"] == "review_required"
        proposal = self._propose(fixture)
        self.assert_exit(proposal, 2, "review_changed")
        assert proposal.stdout == ""

    def test_transition_with_wrong_baseline_target_or_declaration_rejects_candidate(self) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        for field, value in (
            ("baseline_lock_digest", "sha256:" + "b" * 64),
            ("target_source_commit", "b" * 40),
            ("declaration_digest", "sha256:" + "b" * 64),
        ):
            self.write_fresh_review(self, fixture, "note", "applied", **{field: value})
            rejected = self._propose(fixture)
            self.assert_exit(rejected, 2, "review_changed")
            assert rejected.stdout == ""

    def test_fresh_decision_choices_authorize_candidate(self) -> None:
        for decision in ("applied", "declined", "superseded"):
            fixture = self.build_two_unit(EMPTY_REVIEW)
            self.write_fresh_review(self, fixture, "note", decision)
            proposal = self._propose(fixture)
            self.assert_exit(proposal, 0)

    def test_fresh_source_or_result_digest_mismatch_rejects_candidate(self) -> None:
        for field in ("reviewed_upstream_digest", "reviewed_destination_digest"):
            fixture = self.build_two_unit(EMPTY_REVIEW)
            self.write_fresh_review(
                self, fixture, "note", "applied", **{field: "sha256:" + "b" * 64}
            )
            proposal = self._propose(fixture)
            self.assert_exit(proposal, 2, "review_changed")
            assert proposal.stdout == ""

    def test_prepared_destination_change_after_review_rejects_candidate(self) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        self.write_fresh_review(self, fixture, "note", "applied")
        self.write(fixture["adopter"], "content/note-local.txt", "edited after review\n")
        fixture["adopter_rev"] = self.commit(
            fixture["adopter"], "change prepared destination after review"
        )

        proposal = self._propose(fixture)

        self.assert_exit(proposal, 2, "review_changed")
        assert proposal.stdout == ""

    def test_target_source_change_after_review_rejects_candidate(self) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        self.write_fresh_review(self, fixture, "note", "applied")
        self.write(fixture["upstream"], "content/note.txt", "note v3\n")
        self.commit(fixture["upstream"], "change target after review")

        proposal = self._propose(fixture)

        self.assert_exit(proposal, 2, "review_changed")
        assert proposal.stdout == ""

    def test_review_only_no_delta_substitution_rejects_without_stdout(self) -> None:
        fixture = self.build_greeting()
        fixture["review"].write_text(
            review_with_transition(
                EMPTY_REVIEW,
                self.rev(fixture["upstream"]),
                fixture["declaration"].read_text(encoding="utf-8"),
                _raw_file_digest(str(fixture["lock"])),
            ),
            encoding="utf-8",
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "fresh no-delta review")
        self.assert_exit(self._propose(fixture), 0)

        fixture["review"].write_text(
            review_with_transition(
                EMPTY_REVIEW,
                self.rev(fixture["upstream"]),
                fixture["declaration"].read_text(encoding="utf-8"),
                "sha256:" + "b" * 64,
            ),
            encoding="utf-8",
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "stale no-delta review")

        rejected = self._propose(fixture)

        self.assert_exit(rejected, 2, "review_changed")
        assert rejected.stdout == ""


FAKE_MARKER_ONLY_AGENT = (
    "# Reviewer — Destination\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Marker added without a mandatory core region.\n"
)

TREE_MANDATORY = "## Mandatory core\n\nTREE_MANDATORY_RULE\n"
TREE_SKILL_SOURCE = (
    "# Skill\n> **Rule layout:** two-section-v1\n\n## Project extensions\n\n"
    "Source skill note.\n\n" + TREE_MANDATORY
)
TREE_SKILL_DESTINATION = (
    "# Skill — Destination\n> **Rule layout:** two-section-v1\n\n## Project extensions\n\n"
    "Destination skill note.\n\n" + TREE_MANDATORY
)
TREE_REFERENCE_MANDATORY = "## Mandatory core\n\nREFERENCE_MANDATORY_RULE\n"
TREE_REFERENCE_SOURCE = (
    "# Reference\n> **Rule layout:** two-section-v1\n\n## Project extensions\n\n"
    "Source reference note.\n\n" + TREE_REFERENCE_MANDATORY
)
TREE_REFERENCE_DESTINATION = (
    "# Reference — Destination\n> **Rule layout:** two-section-v1\n\n## Project extensions\n\n"
    "Destination reference note.\n\n" + TREE_REFERENCE_MANDATORY
)

TREE_PROTECTED_CATALOG = """schema_version: 2
catalog:
  version: 2.5.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: protected-skill
    kind: skill
    applicability: { always: true }
    install_strategy: copy
    sync_projection: tree
    rule_documents:
      - .opencode/skills/protected/SKILL.md
      - .opencode/skills/protected/reference.md
    members:
      - { id: tree, source: .opencode/skills/protected, destination: .opencode/skills/protected }
"""

TREE_PROTECTED_DECLARATION = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: protected-skill
    mode: adapted
    members:
      - { id: tree, destination: .opencode/skills/protected }
"""


class ProtectedDocumentTests(EngineTestCase):
    """Protected documents resolve through file and tree member mappings."""

    def test_file_projection_round_trips(self) -> None:
        fixture = self.build_protected_agent()
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            fixture["adopter_rev"],
            "--format",
            "json",
        )
        self.assert_exit(proc, 0)
        assert json.loads(proc.stdout)["compliance"]

    def test_fake_marker_only_boundary_rejected(self) -> None:
        fixture = self.build_protected_agent(
            destination_agent=FAKE_MARKER_ONLY_AGENT, propose=False
        )
        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proposal, 2, "policy_violation")
        assert proposal.stdout == ""

    def test_tree_projection_resolves_every_rule_document(self) -> None:
        fixture = self.build_protected(
            TREE_PROTECTED_CATALOG,
            TREE_PROTECTED_DECLARATION,
            {
                ".opencode/skills/protected/SKILL.md": TREE_SKILL_SOURCE,
                ".opencode/skills/protected/reference.md": TREE_REFERENCE_SOURCE,
                ".opencode/skills/protected/notes.txt": "non-rule member\n",
            },
            {
                ".opencode/skills/protected/SKILL.md": TREE_SKILL_DESTINATION,
                ".opencode/skills/protected/reference.md": TREE_REFERENCE_DESTINATION,
                ".opencode/skills/protected/notes.txt": "non-rule member\n",
            },
            "protected-skill",
        )
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture),
            "--adopter-revision",
            fixture["adopter_rev"],
            "--format",
            "json",
        )
        self.assert_exit(proc, 0)
        assert json.loads(proc.stdout)["compliance"]

    def test_ambiguous_resolution_has_no_first_match(self) -> None:
        duplicate = {
            "id": "dup",
            "sync_projection": "file",
            "members": [
                {"id": "first", "source": "first.md"},
                {"id": "second", "source": "./first.md"},
            ],
        }
        duplicate_decl = {
            "members": [
                {"id": "first", "destination": "only-first.md"},
                {"id": "second", "destination": "second.md"},
            ],
        }
        with pytest.raises(SyncError) as caught:
            _rule_document_destination(duplicate, duplicate_decl, "first.md")
        assert caught.value.code == "invalid_mapping"
        assert "exactly one" in caught.value.message
        assert "only-first.md" not in caught.value.message
        overlap = {
            "id": "tree",
            "sync_projection": "tree",
            "members": [
                {"id": "outer", "source": "skills"},
                {"id": "inner", "source": "skills/protected"},
            ],
        }
        overlap_decl = {
            "members": [
                {"id": "outer", "destination": "dest-skills"},
                {"id": "inner", "destination": "dest-inner"},
            ],
        }
        with pytest.raises(SyncError) as overlap_caught:
            _rule_document_destination(
                overlap, overlap_decl, "skills/protected/SKILL.md"
            )
        assert overlap_caught.value.code == "invalid_mapping"
        assert "matched 2" in overlap_caught.value.message

    def test_unique_resolution_returns_only_the_matching_destination(self) -> None:
        catalog_unit = {
            "id": "rules",
            "sync_projection": "file",
            "members": [
                {"id": "spec", "source": "skills/rules.md"},
                {"id": "notes", "source": "skills/notes.txt"},
            ],
        }
        declaration_unit = {
            "members": [
                {"id": "spec", "destination": "local/rules.md"},
                {"id": "notes", "destination": "local/notes.txt"},
            ],
        }
        assert (
            _rule_document_destination(
                catalog_unit, declaration_unit, "skills/rules.md"
            )
            == "local/rules.md"
        )
