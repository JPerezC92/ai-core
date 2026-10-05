"""Prepared rule-notice round-trip and rejection tests.

Tests bind reviewed bytes and engine exit codes. They do not classify notice
prose or read ``intended_verdict``.
"""

from __future__ import annotations

import json

import pytest
import yaml

from adoption_constants import RULE_LAYOUT_VALUE
from adoption_content import _rule_layout
from adoption_loaders import _raw_file_digest
from adoption_test_acceptance_data import (
    NOTICE_EXCEPTION_AFTER,
    NOTICE_EXCEPTION_BEFORE,
    NOTICE_PREFERENCE_SENTENCE,
    NOTICE_SOURCE_FAST_TRACK_EXTENSION,
    RULE_NOTICE_ACCEPT_CASES,
    RULE_NOTICE_REJECT_CASES,
    RuleNoticeCase,
)
from adoption_test_prepared import (
    _check_index,
    _notice_case,
    _propose_index,
    _write_index_review,
)
from adoption_test_repos import AdopterFixture, EngineTestCase

_NOTICE_ENGINE_ERRORS: dict[str, str] = {
    "notice-core-divergence-declined": "mandatory core differs",
    "notice-counterfeit-attestation": "mandatory core differs",
    "notice-missing-affected-file": "protected rule document is missing",
}


class RuleNoticeAcceptanceTests(EngineTestCase):
    """Prepared notice cases round-trip or reject through the read-only engine.

    Tests bind reviewed bytes and engine exit codes. They do not classify
    notice prose or read ``intended_verdict``.
    """

    def _prepare_notice_index(
        self,
        case: RuleNoticeCase,
        *,
        verified_layout: bool | None = None,
    ) -> AdopterFixture:
        fixture = self.build_protected(
            case["catalog"],
            case["declaration"],
            {
                surface["path"]: surface["previous_source"]
                for surface in case["surfaces"]
            },
            {
                surface["path"]: surface["destination_before"]
                for surface in case["surfaces"]
            },
            case["unit"],
        )
        for surface in case["surfaces"]:
            self.write(
                fixture["upstream"], surface["path"], surface["target_source"]
            )
        self.commit(fixture["upstream"], "target notice core")
        self.write(fixture["adopter"], "OWNER-NOTES.md", "unrelated owner work\n")
        for surface in case["surfaces"]:
            destination = fixture["adopter"] / surface["path"]
            if surface["path"] in case["omit_paths"]:
                if destination.exists():
                    destination.unlink()
                continue
            self.write(fixture["adopter"], surface["path"], surface["result"])
        self.stage(
            fixture["adopter"],
            *(surface["path"] for surface in case["surfaces"]),
        )
        layout = (
            case["verified_layout"] if verified_layout is None else verified_layout
        )
        _write_index_review(
            self,
            fixture,
            {
                case["unit"]: (
                    case["decision"],
                    layout,
                    case["review_notice"],
                )
            },
            baseline_lock_digest=_raw_file_digest(str(fixture["lock"])),
        )
        self.stage(fixture["adopter"], ".aicore/adoption-review.yaml")
        return fixture

    def _assert_notice_bytes(self, case: RuleNoticeCase, fixture: AdopterFixture) -> None:
        review = yaml.safe_load(fixture["review"].read_text(encoding="utf-8"))
        assert isinstance(review, dict)
        decision = review["decisions"][0]
        assert decision["evidence"] == case["review_notice"]
        assert decision["decision"] == "applied"
        assert decision["verified_layout"] == RULE_LAYOUT_VALUE
        for surface in case["surfaces"]:
            accepted = (fixture["adopter"] / surface["path"]).read_text(encoding="utf-8")
            source = (fixture["upstream"] / surface["path"]).read_text(encoding="utf-8")
            assert accepted == surface["result"]
            assert source == surface["target_source"]
            assert self.staged_bytes(fixture["adopter"], surface["path"]) == (
                surface["result"].encode("utf-8")
            )
            source_layout = _rule_layout(source)
            accepted_layout = _rule_layout(accepted)
            assert source_layout is not None and accepted_layout is not None
            assert accepted_layout.mandatory == source_layout.mandatory
        root = next(
            surface for surface in case["surfaces"] if surface["path"] == "AGENTS.md"
        )
        before_layout = _rule_layout(root["destination_before"])
        result_layout = _rule_layout(root["result"])
        assert before_layout is not None and result_layout is not None
        preference = f"{NOTICE_PREFERENCE_SENTENCE}\n".encode("utf-8")
        assert preference in before_layout.extensions
        assert preference in result_layout.extensions
        if NOTICE_EXCEPTION_BEFORE in root["destination_before"]:
            assert NOTICE_EXCEPTION_BEFORE not in root["result"]
            assert NOTICE_EXCEPTION_AFTER in root["result"]
        else:
            assert before_layout.extensions == result_layout.extensions
        policy = next(
            (
                surface
                for surface in case["surfaces"]
                if surface["path"] == "policies/fast-track.md"
            ),
            None,
        )
        if policy is not None:
            assert NOTICE_EXCEPTION_BEFORE in policy["destination_before"]
            assert NOTICE_EXCEPTION_BEFORE not in policy["result"]
            assert NOTICE_EXCEPTION_AFTER in policy["result"]
            assert NOTICE_SOURCE_FAST_TRACK_EXTENSION in policy["target_source"]
            assert NOTICE_SOURCE_FAST_TRACK_EXTENSION not in policy["result"]
            assert NOTICE_SOURCE_FAST_TRACK_EXTENSION not in policy["destination_before"]

    @pytest.mark.parametrize(
        "case_id",
        [case["case_id"] for case in RULE_NOTICE_ACCEPT_CASES],
    )
    def test_valid_notice_round_trip_binds_reviewed_bytes(self, case_id: str) -> None:
        case = _notice_case(case_id)
        fixture = self._prepare_notice_index(case)
        adopter = fixture["adopter"]
        assert self.index_entry(adopter, "OWNER-NOTES.md") is None
        before = self.worktree_bytes(adopter)
        proposal = _propose_index(self, fixture, update=True)
        self.assert_exit(proposal, 0)
        assert self.worktree_bytes(adopter) == before
        candidate = self.write(self.root, f"{case_id}.lock.yaml", proposal.stdout)
        self.assert_exit(_check_index(self, fixture, lock=candidate), 0)
        self.write(adopter, ".aicore/adoption.lock.yaml", proposal.stdout)
        self.stage(adopter, ".aicore/adoption.lock.yaml")
        final = _check_index(self, fixture, json_output=True)
        self.assert_exit(final, 0)
        assert json.loads(final.stdout)["compliance"] is True
        assert (adopter / "OWNER-NOTES.md").read_text(encoding="utf-8") == (
            "unrelated owner work\n"
        )
        assert self.index_entry(adopter, "OWNER-NOTES.md") is None
        self._assert_notice_bytes(case, fixture)

    @pytest.mark.parametrize(
        "case_id",
        [case["case_id"] for case in RULE_NOTICE_REJECT_CASES],
    )
    def test_invalid_notice_case_rejects(self, case_id: str) -> None:
        case = _notice_case(case_id)
        fixture = self._prepare_notice_index(case)
        review = yaml.safe_load(fixture["review"].read_text(encoding="utf-8"))
        assert isinstance(review, dict)
        assert review["decisions"][0]["decision"] == case["decision"]
        if case["verified_layout"]:
            assert review["decisions"][0]["verified_layout"] == RULE_LAYOUT_VALUE
        else:
            assert "verified_layout" not in review["decisions"][0]
        if case["omit_paths"]:
            for relative in case["omit_paths"]:
                assert self.index_entry(fixture["adopter"], relative) is None
        before_lock = fixture["lock"].read_bytes()
        before = self.worktree_bytes(fixture["adopter"])
        proposal = _propose_index(self, fixture, update=True)
        self.assert_exit(proposal, 2, "policy_violation")
        self.assert_exit(proposal, 2, _NOTICE_ENGINE_ERRORS[case_id])
        assert proposal.stdout == ""
        assert fixture["lock"].read_bytes() == before_lock
        assert self.worktree_bytes(fixture["adopter"]) == before

    def test_result_altered_after_notice_review_rejects(self) -> None:
        case = _notice_case("notice-compatible-extension")
        fixture = self._prepare_notice_index(case)
        accepted = (fixture["adopter"] / "AGENTS.md").read_text(encoding="utf-8")
        tampered = accepted.replace(
            NOTICE_PREFERENCE_SENTENCE, "Relay release notes were altered.", 1
        )
        self.write(fixture["adopter"], "AGENTS.md", tampered)
        self.stage(fixture["adopter"], "AGENTS.md")
        rejected = _propose_index(self, fixture, update=True)
        self.assert_exit(rejected, 2, "review_changed")
        assert rejected.stdout == ""
        assert self.index_entry(fixture["adopter"], "OWNER-NOTES.md") is None

    def test_missing_layout_approval_rejects(self) -> None:
        case = _notice_case("notice-compatible-extension")
        fixture = self._prepare_notice_index(case, verified_layout=False)
        review = yaml.safe_load(fixture["review"].read_text(encoding="utf-8"))
        assert isinstance(review, dict)
        assert "verified_layout" not in review["decisions"][0]
        rejected = _propose_index(self, fixture, update=True)
        self.assert_exit(rejected, 2, "review_changed")
        assert rejected.stdout == ""
