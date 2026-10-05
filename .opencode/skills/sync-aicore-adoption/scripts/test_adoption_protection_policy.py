"""Phase 1 layout-defect policy outcome tests.

Proposal and check outcomes for the Phase 1 layout defects. These paths
exercise the protected-document helper, not only the layout helper. Check JSON
keeps existing dispositions and does not grow a detailed-reason field.
"""

from __future__ import annotations

import json
import subprocess

import pytest

from adoption_constants import RULE_LAYOUT_VALUE
from adoption_test_acceptance_data import (
    PROTECTED_AGENT_CATALOG,
    PROTECTED_AGENT_DECLARATION,
    PROTECTED_AGENT_MANDATORY,
    PROTECTED_AGENT_PROFILE,
    PROTECTED_DESTINATION_AGENT,
    PROTECTED_SOURCE_AGENT,
)
from adoption_test_prepared import _write_prepared_review
from adoption_test_repos import AdopterFixture, EngineTestCase

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
