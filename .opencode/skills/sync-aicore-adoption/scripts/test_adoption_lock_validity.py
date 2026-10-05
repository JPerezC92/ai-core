"""Lock-document validity, retirement, and transition binding tests."""

from __future__ import annotations

import json
from copy import deepcopy

import pytest
import yaml

from adoption_test_repos import AdopterFixture, EngineTestCase

from adoption_contracts import SyncError
from adoption_digests import (
    _retired_descriptor_digest,
    declaration_unit_digest,
    unit_digest,
)
from adoption_git import _GitRepo
from adoption_loaders import _raw_file_digest, load_lock
from adoption_reconciliation import _reviewed_unit_source_digest
from adoption_test_acceptance_data import (
    ADAPTED_RULEBOOK,
    MIXED_CATALOG,
    MIXED_DECLARATION,
    REPLACEMENT_AGENT,
)
from adoption_test_data import (
    EMPTY_REVIEW,
    GREETING_DECLARATION,
    TWO_UNIT_DECLARATION,
    greeting_lock_document,
    member_file,
    placeholder_digest,
    snapshot_digest,
)


class LockValidityTests(EngineTestCase):
    def _retired_candidate(self) -> tuple[dict[str, object], dict[str, object]]:
        """Prepare a candidate retaining removed adapted and replacement mappings."""
        fixture = self.build_mixed_mode()
        catalog = yaml.safe_load(MIXED_CATALOG)
        declaration = yaml.safe_load(MIXED_DECLARATION)
        assert isinstance(catalog, dict)
        assert isinstance(declaration, dict)
        retired_ids = {"rulebook", "helper-agent"}
        catalog["units"] = [
            unit for unit in catalog["units"]
            if unit["id"] not in retired_ids
        ]
        declaration["units"] = [
            unit for unit in declaration["units"] if unit["id"] not in retired_ids
        ]
        self.write(
            fixture["upstream"],
            ".aicore/core-catalog-v2.yaml",
            yaml.safe_dump(catalog, sort_keys=False),
        )
        target = self.commit(fixture["upstream"], "retire non-mirror mappings")
        self.write(
            fixture["adopter"],
            ".aicore/adoption.yaml",
            yaml.safe_dump(declaration, sort_keys=False),
        )
        baseline = yaml.safe_load(fixture["lock"].read_text(encoding="utf-8"))
        assert isinstance(baseline, dict)
        rows = {row["id"]: row for row in baseline["units"]}
        decisions: list[dict[str, object]] = []
        upstream = _GitRepo(str(fixture["upstream"]))
        for unit_id in sorted(retired_ids):
            row = rows[unit_id]
            descriptor = dict(row)
            if row["mode"] == "replacement":
                descriptor["replacement_members"] = [
                    dict(member) for member in row["replacement_members"]
                ]
            else:
                descriptor["members"] = [
                    {**member, "projection": "file"} for member in row["members"]
                ]
            descriptor["retired"] = True
            decisions.append({
                "unit": unit_id,
                "decision": "declined",
                "reviewer": "test-suite",
                "evidence": "Retained destination mapping reviewed after core retirement.",
                "reviewed_upstream_digest": _reviewed_unit_source_digest(
                    upstream,
                    target,
                    None,
                    str(row["accepted_upstream_digest"]),
                ),
                "reviewed_destination_digest": _retired_descriptor_digest(descriptor),
            })
        review = {
            "schema_version": 2,
            "upstream_repository": "example/upstream",
            "transition": {
                "baseline_lock_digest": _raw_file_digest(str(fixture["lock"])),
                "target_source_commit": target,
                "declaration_digest": _raw_file_digest(
                    str(fixture["declaration"])
                ),
            },
            "decisions": decisions,
        }
        self.write(
            fixture["adopter"],
            ".aicore/adoption-review.yaml",
            yaml.safe_dump(review, sort_keys=False),
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "review retirement")
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
        candidate = yaml.safe_load(proposal.stdout)
        assert isinstance(candidate, dict)
        return fixture, candidate

    def test_retired_candidate_preserves_ordinary_and_replacement_descriptors(self) -> None:
        fixture, candidate = self._retired_candidate()
        rows = {row["id"]: row for row in candidate["units"]}
        rulebook = rows["rulebook"]
        helper = rows["helper-agent"]
        assert rulebook["retired"] is True
        assert rulebook["members"][0]["projection"] == "file"
        assert helper["retired"] is True
        assert helper["replacement_members"][0]["projection"] == "file"
        candidate_path = self.write(
            fixture["adopter"],
            ".aicore/adoption.lock.yaml",
            yaml.safe_dump(candidate, sort_keys=False),
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "accept candidate")
        checked = self.run_cli(
            "check",
            *self.base_check_args(fixture, lock=candidate_path),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )
        self.assert_exit(checked, 0)
        report = json.loads(checked.stdout)
        retired = {row["id"]: row for row in report["units"] if row.get("retired")}
        assert retired["rulebook"]["disposition"] == "current"
        assert retired["helper-agent"]["disposition"] == "current"

        self.write(fixture["adopter"], "skills/rules.md", "later local drift\n")
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "drift retained file")
        drift = self.run_cli(
            "check",
            *self.base_check_args(fixture, lock=candidate_path),
            "--adopter-revision", fixture["adopter_rev"],
            "--format", "json",
        )
        self.assert_exit(drift, 1)
        drift_rows = {row["id"]: row for row in json.loads(drift.stdout)["units"]}
        assert drift_rows["rulebook"]["disposition"] == "local_drift"

    @pytest.mark.parametrize("projection", ["file", "tree"])
    def test_retired_ordinary_row_requires_valid_projection(self, projection: str) -> None:
        lock = greeting_lock_document("a" * 40, "hello\n", "hello\n", mode="adapted")
        row = lock["units"][0]
        row["retired"] = True
        row["members"][0]["projection"] = projection
        lock["accepted_snapshot_digest"] = snapshot_digest(
            GREETING_DECLARATION, EMPTY_REVIEW, lock["units"]
        )
        path = self.write(self.root, f"retired-{projection}.lock.yaml", yaml.safe_dump(lock, sort_keys=False))
        assert load_lock(str(path))["units"][0]["retired"] is True

        del row["members"][0]["projection"]
        malformed = self.write(self.root, "retired-malformed.lock.yaml", yaml.safe_dump(lock, sort_keys=False))
        with pytest.raises(SyncError) as caught:
            load_lock(str(malformed))
        assert caught.value.code == "invalid_lock"

    def test_retired_rows_reject_active_assertion_not_applicable_and_overlap_mappings(self) -> None:
        fixture = self.build_greeting()
        lock = yaml.safe_load(fixture["lock"].read_text(encoding="utf-8"))
        assert isinstance(lock, dict)
        active_row = lock["units"][0]
        active_retired_row = {
            **deepcopy(active_row),
            "mode": "adapted",
            "declaration_unit_digest": declaration_unit_digest(
                "adapted", [{"id": "file", "destination": "content/greeting.txt"}], []
            ),
            "members": [{**active_row["members"][0], "projection": "file"}],
            "retired": True,
        }
        lock["units"] = [active_retired_row]
        lock["accepted_snapshot_digest"] = snapshot_digest(
            GREETING_DECLARATION, EMPTY_REVIEW, lock["units"]
        )
        active = self.write(self.root, "active-retired.lock.yaml", yaml.safe_dump(lock, sort_keys=False))
        self.assert_exit(
            self.run_cli("check", *self.base_check_args(fixture, lock=active), "--adopter-revision", fixture["adopter_rev"]),
            2,
            "retired lock row cannot describe a current catalog unit",
        )

        for invalid_mode in ("mirror", "not_applicable"):
            active_retired_row["mode"] = invalid_mode
            invalid = self.write(self.root, f"retired-{invalid_mode}.lock.yaml", yaml.safe_dump(lock, sort_keys=False))
            with pytest.raises(SyncError) as caught:
                load_lock(str(invalid))
            assert caught.value.code == "invalid_lock"
        retired_row = deepcopy(active_retired_row)
        retired_row["mode"] = "adapted"
        retired_row["id"] = "retained-greeting"
        lock["units"] = [active_row]
        lock["units"].append(retired_row)
        lock["accepted_snapshot_digest"] = snapshot_digest(
            GREETING_DECLARATION, EMPTY_REVIEW, lock["units"]
        )
        overlap = self.write(self.root, "overlapping-retired.lock.yaml", yaml.safe_dump(lock, sort_keys=False))
        self.assert_exit(
            self.run_cli("check", *self.base_check_args(fixture, lock=overlap), "--adopter-revision", fixture["adopter_rev"]),
            2,
            "duplicate destination",
        )
    def test_lock_row_with_source_commit_is_invalid_lock(self) -> None:
        lock = greeting_lock_document("a" * 40, "hello\n", "hello\n")
        lock["units"][0]["accepted_source_commit"] = "b" * 40
        path = self.write(self.root, "row-source.lock.yaml", yaml.safe_dump(lock, sort_keys=False))
        with pytest.raises(SyncError) as caught:
            load_lock(str(path))
        assert caught.value.code == "invalid_lock"
        fixture = self.build_greeting()
        args = ["check", *self.base_check_args(fixture, lock=path), "--adopter-revision", fixture["adopter_rev"]]
        self.assert_exit(self.run_cli(*args), 2, "invalid_lock")

    @pytest.mark.parametrize(
        "case_id,bad_commit",
        [
            ("head", "HEAD"),
            ("head-parent", "HEAD~3"),
            ("short", "a" * 39),
            ("uppercase", "A" * 40),
        ],
    )
    def test_movable_or_non_canonical_accepted_source_commit_is_invalid_lock(
        self, case_id: str, bad_commit: str
    ) -> None:
        """A hand-fabricated lock can no longer bind to a movable revspec."""
        lock = greeting_lock_document(bad_commit, "hello\n", "hello\n")
        path = self.write(
            self.root,
            f"bad-accepted-{case_id}.lock.yaml",
            yaml.safe_dump(lock, sort_keys=False),
        )
        with pytest.raises(SyncError) as caught:
            load_lock(str(path))
        assert caught.value.code == "invalid_lock", case_id

    @pytest.mark.parametrize(
        "case_id,bad_commit",
        [
            ("head", "HEAD"),
            ("head-parent", "HEAD~3"),
            ("short", "a" * 39),
            ("uppercase", "A" * 40),
        ],
    )
    def test_check_rejects_movable_accepted_source_commit_without_stdout(
        self, case_id: str, bad_commit: str
    ) -> None:
        fixture = self.build_greeting()
        lock_document = self._load_lock_document(fixture)
        lock_document["accepted_source_commit"] = bad_commit
        tampered = self.write(
            self.root,
            f"bad-accepted-check-{case_id}.lock.yaml",
            yaml.safe_dump(lock_document, sort_keys=False),
        )
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture, lock=tampered),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proc, 2, "invalid_lock")
        assert proc.stdout == ""

    @pytest.mark.parametrize(
        "case_id,bad_commit",
        [
            ("head", "HEAD"),
            ("head-parent", "HEAD~3"),
            ("short", "a" * 39),
            ("uppercase", "A" * 40),
        ],
    )
    def test_propose_lock_rejects_movable_accepted_source_commit_without_stdout(
        self, case_id: str, bad_commit: str
    ) -> None:
        fixture = self.build_greeting()
        lock_document = self._load_lock_document(fixture)
        lock_document["accepted_source_commit"] = bad_commit
        tampered = self.write(
            self.root,
            f"bad-accepted-propose-{case_id}.lock.yaml",
            yaml.safe_dump(lock_document, sort_keys=False),
        )
        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(tampered),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proposal, 2, "invalid_lock")
        assert proposal.stdout == ""

    def test_mixed_baseline_lock_is_rejected(self) -> None:
        fixture = self.build_two_unit(EMPTY_REVIEW)
        lock_document = yaml.safe_load(fixture["lock"].read_text(encoding="utf-8"))
        target_note = self.git(
            fixture["upstream"], "show", f"{fixture['target']}:content/note.txt"
        ).stdout
        for row in lock_document["units"]:
            if row["id"] == "note":
                row["accepted_upstream_digest"] = unit_digest([("file", member_file(target_note))])
        lock_document["accepted_snapshot_digest"] = snapshot_digest(
            TWO_UNIT_DECLARATION, EMPTY_REVIEW, lock_document["units"]
        )
        mixed = self.write(self.root, "mixed-baseline.lock.yaml", yaml.safe_dump(lock_document, sort_keys=False))
        args = ["check", *self.base_check_args(fixture, lock=mixed), "--adopter-revision", fixture["adopter_rev"]]
        self.assert_exit(self.run_cli(*args), 2, "invalid_lock")

    def test_tampered_snapshot_digest_is_invalid_lock(self) -> None:
        fixture = self.build_greeting()
        lock_document = yaml.safe_load(fixture["lock"].read_text(encoding="utf-8"))
        lock_document["accepted_snapshot_digest"] = placeholder_digest("tampered")
        tampered = self.write(self.root, "tampered-snapshot.lock.yaml", yaml.safe_dump(lock_document, sort_keys=False))
        args = ["check", *self.base_check_args(fixture, lock=tampered), "--adopter-revision", fixture["adopter_rev"]]
        self.assert_exit(self.run_cli(*args), 2, "invalid_lock")

    def _reintroduce_rulebook(
        self, fixture: AdopterFixture, applicability: dict[str, object] | None = None
    ) -> None:
        catalog = yaml.safe_load(fixture["catalog"].read_text(encoding="utf-8"))
        assert isinstance(catalog, dict)
        catalog["units"].append({
            "id": "rulebook",
            "kind": "skill",
            "applicability": applicability or {"always": True},
            "install_strategy": "copy",
            "sync_projection": "file",
            "members": [
                {
                    "id": "rules",
                    "source": "skills/rules.md",
                    "destination": "skills/rules.md",
                }
            ],
        })
        fixture["catalog"].write_text(
            yaml.safe_dump(catalog, sort_keys=False), encoding="utf-8"
        )
        self.write(fixture["upstream"], "skills/rules.md", "core rulebook v1\n")
        self.commit(fixture["upstream"], "reintroduce rulebook")
        declaration = yaml.safe_load(fixture["declaration"].read_text(encoding="utf-8"))
        assert isinstance(declaration, dict)
        if applicability is None:
            declaration["units"].append({
                "id": "rulebook",
                "mode": "adapted",
                "members": [{"id": "rules", "destination": "skills/rules.md"}],
            })
        else:
            declaration["units"].append({"id": "rulebook", "mode": "not_applicable"})
        fixture["declaration"].write_text(
            yaml.safe_dump(declaration, sort_keys=False), encoding="utf-8"
        )

    def _load_lock_document(self, fixture: AdopterFixture) -> dict[str, object]:
        lock = yaml.safe_load(fixture["lock"].read_text(encoding="utf-8"))
        assert isinstance(lock, dict)
        return lock

    def test_inconsistent_active_source_fact_rejects_without_stdout(self) -> None:
        fixture = self.build_greeting()
        lock_document = self._load_lock_document(fixture)
        lock_document["units"][0]["accepted_upstream_digest"] = placeholder_digest(
            "wrong-source"
        )
        lock_document["accepted_snapshot_digest"] = snapshot_digest(
            GREETING_DECLARATION, EMPTY_REVIEW, lock_document["units"]
        )
        tampered = self.write(
            self.root,
            "wrong-source.lock.yaml",
            yaml.safe_dump(lock_document, sort_keys=False),
        )
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture, lock=tampered),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proc, 2, "invalid_lock")
        assert proc.stdout == ""

    def test_inconsistent_active_mapping_fact_rejects_without_stdout(self) -> None:
        fixture = self.build_greeting()
        lock_document = self._load_lock_document(fixture)
        lock_document["units"][0]["declaration_unit_digest"] = placeholder_digest(
            "wrong-mapping"
        )
        lock_document["accepted_snapshot_digest"] = snapshot_digest(
            GREETING_DECLARATION, EMPTY_REVIEW, lock_document["units"]
        )
        tampered = self.write(
            self.root,
            "wrong-mapping.lock.yaml",
            yaml.safe_dump(lock_document, sort_keys=False),
        )
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture, lock=tampered),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proc, 2, "invalid_lock")
        assert proc.stdout == ""

    def test_inconsistent_active_member_fact_rejects_without_stdout(self) -> None:
        fixture = self.build_greeting()
        lock_document = self._load_lock_document(fixture)
        lock_document["units"][0]["members"][0]["accepted_destination_digest"] = (
            placeholder_digest("wrong-member")
        )
        tampered = self.write(
            self.root,
            "wrong-member.lock.yaml",
            yaml.safe_dump(lock_document, sort_keys=False),
        )
        proc = self.run_cli(
            "check",
            *self.base_check_args(fixture, lock=tampered),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proc, 2, "invalid_lock")
        assert proc.stdout == ""

    def test_retired_id_reintroduction_rejects_without_stdout(self) -> None:
        fixture, candidate = self._retired_candidate()
        self._reintroduce_rulebook(fixture)
        baseline = self.write(
            self.root,
            "retired-baseline.lock.yaml",
            yaml.safe_dump(candidate, sort_keys=False),
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "reintroduce rulebook")
        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(baseline),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proposal, 2, "invalid_lock")
        assert proposal.stdout == ""

    def test_retired_id_reintroduction_as_not_applicable_rejects_without_stdout(self) -> None:
        fixture, candidate = self._retired_candidate()
        self._reintroduce_rulebook(fixture, applicability={"requires": ["ticket_system"]})
        baseline = self.write(
            self.root,
            "retired-not-applicable-baseline.lock.yaml",
            yaml.safe_dump(candidate, sort_keys=False),
        )
        fixture["adopter_rev"] = self.commit(
            fixture["adopter"], "reintroduce rulebook as not_applicable"
        )
        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(baseline),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proposal, 2, "invalid_lock")
        assert proposal.stdout == ""

    def _write_carry_transition(self, fixture: AdopterFixture, baseline: object) -> None:
        review = yaml.safe_load(fixture["review"].read_text(encoding="utf-8"))
        assert isinstance(review, dict)
        review["transition"] = {
            "baseline_lock_digest": _raw_file_digest(str(baseline)),
            "target_source_commit": self.rev(fixture["upstream"]),
            "declaration_digest": _raw_file_digest(str(fixture["declaration"])),
        }
        fixture["review"].write_text(
            yaml.safe_dump(review, sort_keys=False), encoding="utf-8"
        )

    def test_retired_rows_are_carried_into_the_next_candidate_without_deletion(self) -> None:
        fixture, candidate = self._retired_candidate()
        baseline = self.write(
            self.root,
            "retired-baseline.lock.yaml",
            yaml.safe_dump(candidate, sort_keys=False),
        )
        self._write_carry_transition(fixture, baseline)
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "carry retired rows")
        proposal = self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(baseline),
            "--adopter-revision", fixture["adopter_rev"],
        )
        self.assert_exit(proposal, 0)
        carried = {
            row["id"]: row for row in yaml.safe_load(proposal.stdout)["units"]
        }
        assert carried["rulebook"]["retired"] is True
        assert carried["helper-agent"]["retired"] is True
        assert carried["rulebook"]["members"][0]["projection"] == "file"
        assert (
            fixture["adopter"] / "skills/rules.md"
        ).read_text(encoding="utf-8") == ADAPTED_RULEBOOK
        assert (
            fixture["adopter"] / "agents/helper/profile.md"
        ).read_text(encoding="utf-8") == REPLACEMENT_AGENT
