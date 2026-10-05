"""Live-state review and baseline single-read tests."""

from __future__ import annotations

import subprocess

import yaml

from adoption_test_repos import AdopterFixture, EngineTestCase

from adoption_content import _destination_unit_digest, _unit_upstream_digest
from adoption_digests import _sha256
from adoption_git import (
    _GitRepo,
    _RevisionSnapshot,
)
from adoption_loaders import _control_document_from_bytes, _raw_file_digest
from adoption_schema import _validate_lock_document
from adoption_test_data import (
    EMPTY_REVIEW,
    TWO_UNIT_DECISION_REVIEW,
    review_with_transition,
)


class LiveStateReviewTests(EngineTestCase):
    """Snapshot verification is distinct from unchecked live worktree state."""

    def _prepare_and_review(self, fixture: AdopterFixture) -> str:
        self.write(
            fixture["adopter"],
            "content/note-local.txt",
            "note v2 reconciled\nLOCAL_BUSINESS_RULE: keep\n",
        )
        prepared_rev = self.commit(fixture["adopter"], "prepared note adaptation")
        fixture["adopter_rev"] = prepared_rev
        catalog = yaml.safe_load(fixture["catalog"].read_text(encoding="utf-8"))
        declaration = yaml.safe_load(
            fixture["declaration"].read_text(encoding="utf-8")
        )
        unit = next(item for item in catalog["units"] if item["id"] == "note")
        declaration_unit = next(
            item for item in declaration["units"] if item["id"] == "note"
        )
        target = self.rev(fixture["upstream"])
        source = _unit_upstream_digest(
            _GitRepo(str(fixture["upstream"])), target, unit
        )
        result = _destination_unit_digest(
            unit,
            declaration_unit,
            _RevisionSnapshot(_GitRepo(str(fixture["adopter"])), prepared_rev),
        )
        fixture["review"].write_text(
            review_with_transition(
                TWO_UNIT_DECISION_REVIEW,
                target,
                fixture["declaration"].read_text(encoding="utf-8"),
                _raw_file_digest(str(fixture["lock"])),
                decision_digests={"note": (source, result)},
            ),
            encoding="utf-8",
        )
        return prepared_rev

    def _propose_index(self, fixture: AdopterFixture) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-index",
        )

    def test_altered_staged_snapshot_after_review_rejects_candidate(self) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        self._prepare_and_review(fixture)
        first = self._propose_index(fixture)
        self.assert_exit(first, 0)

        # Changing the staged snapshot after approval no longer matches the
        # reviewed destination digest, so candidate generation must fail.
        self.write(fixture["adopter"], "content/note-local.txt", "tampered after review\n")
        self.git(fixture["adopter"], "add", "content/note-local.txt")
        rejected = self._propose_index(fixture)
        self.assert_exit(rejected, 2, "review_changed")
        assert rejected.stdout == ""

    def test_worktree_edit_after_verified_snapshot_survives_for_re_review(self) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        self._prepare_and_review(fixture)
        proposal = self._propose_index(fixture)
        self.assert_exit(proposal, 0)
        candidate = self.write(self.root, "reviewed-candidate.lock.yaml", proposal.stdout)
        self.assert_exit(
            self.run_cli(
                "check", *self.base_check_args(fixture, lock=candidate),
                "--adopter-index", "--format", "json",
            ),
            0,
        )

        # A newer unstaged local edit is not part of the verified snapshot and
        # is never replaced by it; the owner must re-review before acceptance.
        note = fixture["adopter"] / "content/note-local.txt"
        note.write_text("newer local edit\n", encoding="utf-8")
        self.assert_exit(
            self.run_cli(
                "check", *self.base_check_args(fixture, lock=candidate),
                "--adopter-index", "--format", "json",
            ),
            0,
        )
        assert note.read_text(encoding="utf-8") == "newer local edit\n"
        staged = self.git(
            fixture["adopter"], "show", ":content/note-local.txt"
        ).stdout
        assert staged == "note v2 reconciled\nLOCAL_BUSINESS_RULE: keep\n"


class BaselineSingleReadTests(EngineTestCase):
    """The baseline digest and the parsed rows derive from exactly one buffer."""

    def test_baseline_digest_is_derived_from_the_parsed_bytes(self) -> None:
        """The shared loader seam never re-reads ``path``.

        Check and propose both parse and hash through this captured buffer.

        The supplied buffer deliberately differs from the file on disk: if
        the seam parsed or hashed the path instead of the buffer, both
        outputs would reflect the on-disk bytes and this test would fail.
        """
        fixture = self.build_greeting()
        on_disk = fixture["lock"].read_bytes()
        alternate = on_disk.replace(b"example/upstream", b"example/alternate")
        assert alternate != on_disk
        document, digest = _control_document_from_bytes(
            str(fixture["lock"]), "invalid_lock", alternate, _validate_lock_document
        )
        assert digest == _sha256(alternate)
        assert digest != _raw_file_digest(str(fixture["lock"]))
        assert document["upstream_repository"] == "example/alternate"
