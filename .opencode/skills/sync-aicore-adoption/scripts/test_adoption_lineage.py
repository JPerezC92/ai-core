"""Prepared runtime-lineage acceptance tests.

Python binds the prepared bytes and rejects a result altered after review. The
semantic comparison, the incorporation/override judgment, and every local-version
rationale are established by the independent model review over the lineage
cases; no assertion here classifies meaning or a bump.
"""

from __future__ import annotations

import json
from typing import cast

from adoption_constants import RULE_LAYOUT_VALUE
from adoption_test_acceptance_data import (
    PROTECTED_DERIVED_DESTINATION_AGENT,
    PROTECTED_DERIVED_RESULT_LOCAL_CHANGE,
    PROTECTED_DERIVED_RESULT_UPSTREAM_ONLY,
    PROTECTED_DERIVED_SOURCE_AGENT,
    PROTECTED_DERIVED_SOURCE_AGENT_V2,
    RELAY_DESTINATION_BEFORE,
    RELAY_PREVIOUS_CORE,
    RELAY_RESULT_NEW_ENFORCEMENT,
    RELAY_RESULT_UPSTREAM_ONLY,
    RELAY_TARGET_CORE,
    RUNTIME_LINEAGE_CASES,
)
from adoption_test_prepared import _propose_prepared, _write_prepared_review
from adoption_test_repos import AdopterFixture, EngineTestCase

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
