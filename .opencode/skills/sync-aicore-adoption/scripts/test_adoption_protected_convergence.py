"""Protected rule-document convergence, attestation, and refusal-path tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

from adoption_constants import RULE_LAYOUT_VALUE
from adoption_test_acceptance_data import (
    PROTECTED_AGENT_CATALOG,
    PROTECTED_AGENT_MIRROR_DECLARATION,
    PROTECTED_AGENT_PROFILE,
    PROTECTED_DESTINATION_ROOT,
    PROTECTED_MANDATORY_CORE,
    PROTECTED_ROOT_CATALOG,
    PROTECTED_ROOT_DECLARATION,
    PROTECTED_SOURCE_AGENT,
    PROTECTED_SOURCE_ROOT,
)
from adoption_test_data import CATALOG_REL, CLEAN_DESTINATION_ROOT
from adoption_test_prepared import _propose_prepared, _write_prepared_review
from adoption_test_repos import AdopterFixture, EngineTestCase


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
