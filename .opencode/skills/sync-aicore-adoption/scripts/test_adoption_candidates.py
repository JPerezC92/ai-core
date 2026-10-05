"""Prepared candidate acceptance and complete prepared-workflow tests.

The engine emits evidence only; destination edits remain skill-owned. These
tests model the skill workflow with ordinary file operations: prepare reviewed
bytes, record a fresh transition-bound approval, stage only reviewed paths,
emit a separate candidate lock, check that candidate against the same explicit
snapshot, accept the lock, then final-check.
"""

from __future__ import annotations

import json
from copy import deepcopy

import yaml

from adoption_contracts import LockDocument
from adoption_digests import _retired_descriptor_digest
from adoption_git import _GitRepo
from adoption_loaders import _raw_file_digest, load_lock
from adoption_mapping import _catalog_transition
from adoption_reconciliation import _reviewed_unit_source_digest
from adoption_schema import _parse_document_bytes, _validate_lock_document
from adoption_test_acceptance_data import MIXED_REVIEW_ALL
from adoption_test_data import EMPTY_REVIEW, review_with_transition
from adoption_test_prepared import _propose_prepared, _write_prepared_review
from adoption_test_repos import EngineTestCase


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
