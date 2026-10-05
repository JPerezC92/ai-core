"""Configuration assertion and guarded-root policy tests."""

from __future__ import annotations

import json
import subprocess

import pytest
import yaml

from adoption_test_repos import EngineTestCase

from adoption_constants import DESTINATION_POLICIES
from adoption_contracts import SyncError
from adoption_digests import unit_digest
from adoption_loaders import load_catalog
from adoption_policies import _adopter_root_policy_violation
from adoption_test_data import (
    CLEAN_DESTINATION_ROOT,
    MINIMAL_UPSTREAM_LINEAGE_ROOT,
    ORIGINAL_REUSE_GUIDE_ROOT,
    UPSTREAM_ROOT,
    VERBOSE_UPSTREAM_LINEAGE_ROOT,
    member_file,
)
from adoption_test_prepared import _bind_review_to_baseline


class AssertionTests(EngineTestCase):
    def _check(self, fixture: dict[str, object]) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "check", *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"], "--format", "json",
        )

    def _propose(self, fixture: dict[str, object]) -> subprocess.CompletedProcess[str]:
        _bind_review_to_baseline(self, fixture)
        return self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        )

    def test_assertions_present_compliant_and_proposable(self) -> None:
        fixture = self.build_assertions()
        proc = self._check(fixture)
        self.assert_exit(proc, 0)
        assert json.loads(proc.stdout)["compliance"]
        proposal = self._propose(fixture)
        self.assert_exit(proposal, 0)
        self.write(fixture["adopter"], ".aicore/adoption.lock.yaml", proposal.stdout)
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "install candidate")
        installed = self._check(fixture)
        self.assert_exit(installed, 0)
        assert json.loads(installed.stdout)["compliance"]

    def test_missing_opencode_gate_noncompliant_and_propose_refuses(self) -> None:
        fixture = self.build_assertions(current_opencode=False)
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        assert not json.loads(proc.stdout)["compliance"]
        self.assert_exit(self._propose(fixture), 2, "local_drift")

    def test_missing_gitignore_entry_noncompliant_and_propose_refuses(self) -> None:
        fixture = self.build_assertions(current_gitignore=False)
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        assert not json.loads(proc.stdout)["compliance"]
        self.assert_exit(self._propose(fixture), 2, "local_drift")


class GuardedRootPolicyTests(EngineTestCase):
    def _check(self, fixture: dict[str, object]) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "check", *self.base_check_args(fixture),
            "--adopter-revision", fixture["adopter_rev"], "--format", "json",
        )

    def _propose(self, fixture: dict[str, object]) -> subprocess.CompletedProcess[str]:
        _bind_review_to_baseline(self, fixture)
        return self.run_cli(
            "propose-lock",
            "--upstream-repo", str(fixture["upstream"]),
            "--catalog", str(fixture["catalog"]),
            "--declaration", str(fixture["declaration"]),
            "--review", str(fixture["review"]),
            "--lock", str(fixture["lock"]),
            "--adopter-revision", fixture["adopter_rev"],
        )

    def assert_proposal_policy_violation(self, root: str) -> None:
        fixture = self.build_guarded_root(root)
        proc = self._propose(fixture)
        self.assert_exit(proc, 2, "policy_violation")
        assert proc.stdout == "", "a rejected proposal must emit no YAML"

    def test_clean_destination_root_passes_with_unchanged_lock_shape(self) -> None:
        fixture = self.build_guarded_root(CLEAN_DESTINATION_ROOT)
        check = self._check(fixture)
        self.assert_exit(check, 0)
        report = json.loads(check.stdout)
        assert report["compliance"]
        assert report["units"][0]["disposition"] == "current"
        proposal = self._propose(fixture)
        self.assert_exit(proposal, 0)
        unit = yaml.safe_load(proposal.stdout)["units"][0]
        member = unit["members"][0]
        upstream_member = member_file(UPSTREAM_ROOT)
        assert unit["accepted_upstream_digest"] == unit_digest([("root", upstream_member)])
        assert member["accepted_upstream_digest"] == upstream_member
        assert member["accepted_destination_digest"] == member_file(CLEAN_DESTINATION_ROOT)
        assert set(member) == {
            "id", "destination", "accepted_upstream_digest", "accepted_destination_digest"
        }

    def test_missing_required_destination_markers_rejects_proposal(self) -> None:
        self.assert_proposal_policy_violation(
            "# Relay project runtime\n> **Project identity:** Relay\n"
        )

    @pytest.mark.parametrize(
        "marker",
        [
            "> **Project identity:** Relay\n",
            "> **Spec version:** 2.1.0\n",
            "> **Local version:** 1.0.0\n",
        ],
    )
    def test_each_required_destination_marker_is_enforced(self, marker: str) -> None:
        violation = _adopter_root_policy_violation(
            CLEAN_DESTINATION_ROOT.replace(marker, "").encode("utf-8")
        )
        assert violation is not None

    @pytest.mark.parametrize(
        "reference",
        [
            "AiCoRe", "AI-CORE", "MIGRATE-CORE-TO-PROJECT", "SYNC-AICORE-ADOPTION",
            ".AICORE/", "UPSTREAM PROVENANCE", "UPSTREAM LINEAGE", "REUSE GUIDE",
        ],
    )
    def test_all_forbidden_references_are_case_insensitive(self, reference: str) -> None:
        content = (CLEAN_DESTINATION_ROOT + "\n" + reference).encode("utf-8")
        assert _adopter_root_policy_violation(content) is not None

    def test_original_reuse_guide_rejects_proposal(self) -> None:
        self.assert_proposal_policy_violation(ORIGINAL_REUSE_GUIDE_ROOT)

    def test_renamed_verbose_upstream_lineage_rejects_proposal(self) -> None:
        self.assert_proposal_policy_violation(VERBOSE_UPSTREAM_LINEAGE_ROOT)

    def test_current_minimal_aicore_lineage_rejects_proposal(self) -> None:
        self.assert_proposal_policy_violation(MINIMAL_UPSTREAM_LINEAGE_ROOT)

    def test_locked_prohibited_root_is_policy_violation(self) -> None:
        fixture = self.build_guarded_root(MINIMAL_UPSTREAM_LINEAGE_ROOT)
        proc = self._check(fixture)
        self.assert_exit(proc, 1)
        report = json.loads(proc.stdout)
        assert not report["compliance"]
        assert report["units"][0]["upstream_delta"] == "unchanged"
        assert report["units"][0]["destination_delta"] == "unchanged"
        assert report["units"][0]["disposition"] == "policy_violation"
        assert "root-runtime-spec: policy_violation" in report["blocking_reasons"]

    def test_policy_violation_precedes_needs_review(self) -> None:
        """A changed prohibited guarded root stays policy_violation, not review_required."""
        fixture = self.build_guarded_root(CLEAN_DESTINATION_ROOT)
        self.write(
            fixture["adopter"],
            "AGENTS.md",
            CLEAN_DESTINATION_ROOT + "\nAiCoRe\n",
        )
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "prohibited root edit")

        check = self._check(fixture)

        self.assert_exit(check, 1)
        report = json.loads(check.stdout)
        assert not report["compliance"]
        unit = report["units"][0]
        assert unit["destination_delta"] == "changed"
        assert unit["disposition"] == "policy_violation"
        assert "root-runtime-spec: policy_violation" in report["blocking_reasons"]

    def test_non_utf8_destination_root_rejects_proposal(self) -> None:
        fixture = self.build_guarded_root(CLEAN_DESTINATION_ROOT)
        (fixture["adopter"] / "AGENTS.md").write_bytes(b"\xff\xfe")
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "non-utf8 root")
        proc = self._propose(fixture)
        self.assert_exit(proc, 2, "policy_violation")
        assert proc.stdout == ""

    def test_unknown_destination_policy_is_invalid_mapping(self) -> None:
        assert "adopter_root_runtime" in DESTINATION_POLICIES
        assert "adopter_root_rules" in DESTINATION_POLICIES
        catalog = self.write(self.root, "unknown-policy.yaml", UNKNOWN_POLICY_CATALOG)
        with pytest.raises(SyncError) as caught:
            load_catalog(str(catalog))
        assert caught.value.code == "invalid_mapping"
        assert "destination_policy" in caught.value.message


UNKNOWN_POLICY_CATALOG = """schema_version: 2
catalog:
  version: 2.5.0
  upstream_repository: example/upstream
  digest_algorithm: sha256
units:
  - id: root-runtime-spec
    kind: config
    applicability: { always: true }
    install_strategy: merge
    sync_projection: guarded_file
    destination_policy: adopter_root_rules_v2
    members:
      - { id: root, source: AGENTS.md, destination: AGENTS.md }
"""
