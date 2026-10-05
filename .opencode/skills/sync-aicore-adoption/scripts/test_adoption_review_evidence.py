"""Review-evidence freshness and transition-binding tests."""

from __future__ import annotations

import json
import subprocess

from adoption_loaders import _raw_file_digest
from adoption_test_data import (
    CATALOG_REL,
    EMPTY_REVIEW,
    TWO_UNIT_DECISION_REVIEW,
    review_with_transition,
)
from adoption_test_prepared import _write_prepared_review
from adoption_test_repos import AdopterFixture, EngineTestCase


class ReviewEvidenceTests(EngineTestCase):
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
            _write_prepared_review(self, fixture, "note", "applied", **{field: value})
            rejected = self._propose(fixture)
            self.assert_exit(rejected, 2, "review_changed")
            assert rejected.stdout == ""

    def test_fresh_decision_choices_authorize_candidate(self) -> None:
        for decision in ("applied", "declined", "superseded"):
            fixture = self.build_two_unit(EMPTY_REVIEW)
            _write_prepared_review(self, fixture, "note", decision)
            proposal = self._propose(fixture)
            self.assert_exit(proposal, 0)

    def test_fresh_source_or_result_digest_mismatch_rejects_candidate(self) -> None:
        for field in ("reviewed_upstream_digest", "reviewed_destination_digest"):
            fixture = self.build_two_unit(EMPTY_REVIEW)
            _write_prepared_review(
                self, fixture, "note", "applied", **{field: "sha256:" + "b" * 64}
            )
            proposal = self._propose(fixture)
            self.assert_exit(proposal, 2, "review_changed")
            assert proposal.stdout == ""

    def test_prepared_destination_change_after_review_rejects_candidate(self) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        _write_prepared_review(self, fixture, "note", "applied")
        self.write(fixture["adopter"], "content/note-local.txt", "edited after review\n")
        fixture["adopter_rev"] = self.commit(
            fixture["adopter"], "change prepared destination after review"
        )

        proposal = self._propose(fixture)

        self.assert_exit(proposal, 2, "review_changed")
        assert proposal.stdout == ""

    def test_target_source_change_after_review_rejects_candidate(self) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        _write_prepared_review(self, fixture, "note", "applied")
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
