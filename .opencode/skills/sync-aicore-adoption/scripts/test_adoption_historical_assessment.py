"""Historical and accepted-protection assessment tests.

Accepted protection is assessed independently of incoming target changes.
"""

from __future__ import annotations

import json
import subprocess
from typing import cast

import pytest
import yaml

from adoption_constants import RULE_LAYOUT_VALUE
from adoption_loaders import _raw_file_digest
from adoption_test_acceptance_data import (
    PROTECTED_DESTINATION_AGENT,
    PROTECTED_DESTINATION_ROOT,
    PROTECTED_MANDATORY_CORE,
    PROTECTED_SOURCE_ROOT,
)
from adoption_test_data import CATALOG_REL
from adoption_test_prepared import _propose_prepared, _write_prepared_review
from adoption_test_repos import (
    HISTORICAL_RULE_DESTINATION,
    HISTORICAL_RULE_SOURCE,
    UNPROTECTED_RULE_CATALOG,
    AdopterFixture,
    EngineTestCase,
)

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
