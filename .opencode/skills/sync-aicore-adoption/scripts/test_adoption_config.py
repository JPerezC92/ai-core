"""Configuration assertions, guarded-root policy, and runner-policy tests."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
import yaml

from adoption_test_repos import EngineTestCase

from adoption_constants import AICORE_SUITE_COMMAND, DESTINATION_POLICIES
from adoption_content import (
    _rule_layout,
    _rule_layout_violation,
    _scan_rule_layout,
)
from adoption_contracts import SyncError
from adoption_digests import unit_digest
from adoption_loaders import _raw_file_digest, load_catalog, load_declaration
from adoption_policies import (
    _JsoncCommentError,
    _adopter_root_policy_violation,
    _broad_grant_violation,
    _effective_bash_action,
    _opencode_config_policy_violation,
    _strip_jsonc_comments,
    _wildcard_match,
)
from adoption_test_data import (
    CLEAN_DESTINATION_ROOT,
    EMPTY_REVIEW,
    MINIMAL_UPSTREAM_LINEAGE_ROOT,
    ORIGINAL_REUSE_GUIDE_ROOT,
    UPSTREAM_ROOT,
    VERBOSE_UPSTREAM_LINEAGE_ROOT,
    member_file,
    review_with_transition,
)
from adoption_test_runner_data import (
    AICORE_ROOT_CONFIG,
    AICORE_RUNNER,
    ASSERTION_DECLARATION_DESTINATION_SUITE,
    ASSERTION_DECLARATION_NO_TESTS,
    MINIMAL_RUNNER_DECLARATION,
    NO_TESTS_RUNNER,
    broad_grant_configs,
    misnested_other_agent_config,
    misnested_top_level_config,
    opencode_runner_config,
    unrelated_agent_grants_config,
)


def _bind_review_to_baseline(
    case: EngineTestCase, fixture: dict[str, object]
) -> None:
    """Rewrite the review with a transition bound to the current baseline lock.

    ``propose-lock`` never re-verifies the baseline lock's ``review_digest``, so
    a fresh transition is enough for the proposal path; the lock's own review
    digest is only re-verified by ``check`` after a candidate is installed.
    """
    fixture["review"].write_text(
        review_with_transition(
            EMPTY_REVIEW,
            case.rev(fixture["upstream"]),
            fixture["declaration"].read_text(encoding="utf-8"),
            _raw_file_digest(str(fixture["lock"])),
        ),
        encoding="utf-8",
    )
    fixture["adopter_rev"] = case.commit(
        fixture["adopter"], "fresh transition review"
    )


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


class RunnerPolicyTests(EngineTestCase):
    """Destination-owned test_runner metadata and designated-executor grants."""

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

    def _with_grants(self, fixture: dict[str, object], *allows: str) -> None:
        config = opencode_runner_config(*allows)
        target = fixture["adopter"] / "opencode.jsonc"
        if target.is_file() and target.read_text(encoding="utf-8") == config:
            return
        self.write(fixture["adopter"], "opencode.jsonc", config)
        fixture["adopter_rev"] = self.commit(fixture["adopter"], "runner grants")

    def test_aicore_shape_grant_with_metadata_has_no_violation(self) -> None:
        config = opencode_runner_config(AICORE_SUITE_COMMAND)
        assert _opencode_config_policy_violation(config.encode(), AICORE_RUNNER) is None

    def test_aicore_root_config_shape_passes_structural_validation(self) -> None:
        path = self.write(self.root, "opencode.jsonc", AICORE_ROOT_CONFIG)
        assert _opencode_config_policy_violation(path.read_bytes(), AICORE_RUNNER) is None

    def test_different_approved_suite_commands_are_accepted(self) -> None:
        for command in ("dotnet test", "go test ./..."):
            metadata = {**AICORE_RUNNER, "commands": [command]}
            config = opencode_runner_config(command)
            assert (
                _opencode_config_policy_violation(config.encode(), metadata) is None
            ), command

    def test_changed_approved_command_is_a_violation(self) -> None:
        metadata = {**AICORE_RUNNER, "commands": ["go test ./..."]}
        changed = opencode_runner_config("go test ./cmd/...")
        violation = _opencode_config_policy_violation(changed.encode(), metadata)
        assert violation is not None and "missing approved" in violation

    def test_missing_approved_command_is_a_violation(self) -> None:
        metadata = {**AICORE_RUNNER, "commands": ["go test ./..."]}
        missing = opencode_runner_config("dotnet build")
        violation = _opencode_config_policy_violation(missing.encode(), metadata)
        assert violation is not None and "missing approved" in violation

    def test_unapproved_test_command_is_a_violation(self) -> None:
        metadata = {**AICORE_RUNNER, "commands": ["pnpm test"]}
        config = opencode_runner_config("npm test")
        violation = _opencode_config_policy_violation(config.encode(), metadata)
        assert violation is not None and "missing approved" in violation

    def test_misnested_grant_under_other_agent_is_a_violation(self) -> None:
        metadata = {**AICORE_RUNNER, "commands": ["pnpm test"]}
        config = misnested_other_agent_config("crucible", "pnpm test")
        violation = _opencode_config_policy_violation(config.encode(), metadata)
        assert violation is not None and "missing approved" in violation

    def test_misnested_grant_at_top_level_is_a_violation(self) -> None:
        metadata = {**AICORE_RUNNER, "commands": ["pnpm test"]}
        config = misnested_top_level_config("crucible", "pnpm test")
        violation = _opencode_config_policy_violation(config.encode(), metadata)
        assert violation is not None and "missing approved" in violation

    def test_missing_metadata_is_a_violation(self) -> None:
        config = opencode_runner_config(AICORE_SUITE_COMMAND)
        violation = _opencode_config_policy_violation(config.encode(), None)
        assert violation is not None and "no reviewed test_runner metadata" in violation

    def test_malformed_jsonc_is_a_violation(self) -> None:
        for content in (
            b"// comment\n{ not json",
            b"[1, 2, 3]",
            b"\xff\xfe",
            b"# bad",
            b'# hash is not a JSONC comment\n{"agent": {}}\n',
        ):
            violation = _opencode_config_policy_violation(content, AICORE_RUNNER)
            assert violation == "opencode config is not a valid JSONC object", content

    def test_unterminated_block_comment_is_a_violation(self) -> None:
        metadata = {**AICORE_RUNNER, "commands": ["pnpm test"]}
        config = (
            '{"agent": {"crucible": {"permission": {"bash": '
            '{"*": "deny", "pnpm test": "allow"}}}}} /* trailing'
        )
        violation = _opencode_config_policy_violation(config.encode(), metadata)
        assert violation == "opencode config is not a valid JSONC object"

    def test_strip_jsonc_reports_unterminated_block_comment(self) -> None:
        with pytest.raises(_JsoncCommentError):
            _strip_jsonc_comments('{"a": 1} /* no closer')

    def test_strip_jsonc_preserves_token_boundaries(self) -> None:
        assert _strip_jsonc_comments("1/* comment */2") == "1 2"
        assert json.loads(_strip_jsonc_comments('{"a": 1 /* x */ }')) == {"a": 1}

    def test_carriage_return_comment_cannot_hide_broad_allow(self) -> None:
        """Defeat 1: a ``\\r``-terminated ``//`` comment hid ``"*": "allow"``."""
        metadata = {**AICORE_RUNNER, "commands": ["uv run --frozen pytest -q"]}
        config = (
            '{"agent": {"crucible": {"permission": {"bash": '
            '{"uv run --frozen pytest -q": "allow" //c\r,'
            '"*": "allow"\n}}}}}'
        )
        violation = _opencode_config_policy_violation(config.encode(), metadata)
        assert violation is not None
        assert "grants arbitrary commands" in violation

    @pytest.mark.parametrize("terminator", ["\n", "\r", "\r\n"])
    def test_line_comment_terminators_keep_following_json(
        self, terminator: str
    ) -> None:
        text = '{"a": 1, // trailing comment' + terminator + '"b": 2}'
        stripped = _strip_jsonc_comments(text)
        assert stripped == '{"a": 1, ' + terminator + '"b": 2}'
        assert json.loads(stripped) == {"a": 1, "b": 2}

    @pytest.mark.parametrize("separator", ["\u2028", "\u2029"])
    def test_unicode_line_separators_terminate_line_comments(
        self, separator: str
    ) -> None:
        text = '{"a": 1, // c' + separator + '"b": 2}'
        stripped = _strip_jsonc_comments(text)
        # The ECMAScript-only terminator ends the comment and is normalized
        # to "\n" so the stripped text is valid JSON whitespace.
        assert stripped == '{"a": 1, \n"b": 2}'
        assert json.loads(stripped) == {"a": 1, "b": 2}

    @pytest.mark.parametrize("separator", ["\u2028", "\u2029"], ids=["ls", "ps"])
    def test_line_separator_comment_cannot_hide_broad_allow(
        self, separator: str
    ) -> None:
        """The defeat-1 document with an ECMAScript-only terminator fails closed."""
        metadata = {**AICORE_RUNNER, "commands": ["uv run --frozen pytest -q"]}
        config = (
            '{"agent": {"crucible": {"permission": {"bash": '
            '{"uv run --frozen pytest -q": "allow" //c'
            + separator
            + ',"*": "allow"\n}}}}}'
        )
        violation = _opencode_config_policy_violation(config.encode(), metadata)
        assert violation is not None
        assert "grants arbitrary commands" in violation

    def test_inline_block_comment_is_accepted(self) -> None:
        metadata = {**AICORE_RUNNER, "commands": ["pnpm test"]}
        config = (
            '{ /* inline */ "agent": { "crucible": { "permission": '
            '{ "bash": { "*": "deny", "pnpm test": "allow" } } } } }'
        )
        assert _opencode_config_policy_violation(config.encode(), metadata) is None

    def test_comments_between_tokens_are_accepted(self) -> None:
        metadata = {**AICORE_RUNNER, "commands": ["pnpm test"]}
        config = (
            '{ "agent" /* between */ : { "crucible" : { "permission" : '
            '{ "bash" : { "*" : "deny", "pnpm test" : "allow" } } } } }'
        )
        assert _opencode_config_policy_violation(config.encode(), metadata) is None

    def test_escaped_strings_and_comment_markers_are_preserved(self) -> None:
        metadata = {**AICORE_RUNNER, "commands": ["pnpm test"]}
        config = (
            "{\n"
            "  // a line comment with /* and */ markers\n"
            '  "agent": {\n'
            '    "crucible": {\n'
            '      "permission": {\n'
            "        /* block comment between tokens */\n"
            '        "bash": {\n'
            '          "*": "deny",\n'
            '          "pnpm test": "allow"\n'
            "        }\n"
            "      },\n"
            '      "note": "escaped \\"quote\\" and /* literal */ text"\n'
            "    }\n"
            "  }\n"
            "}\n"
        )
        assert _opencode_config_policy_violation(config.encode(), metadata) is None

    def test_later_deny_or_ask_overrides_literal_allow(self) -> None:
        metadata = {**AICORE_RUNNER, "commands": ["pnpm test"]}
        for action in ("deny", "ask"):
            config = json.dumps(
                {
                    "agent": {
                        "crucible": {
                            "permission": {
                                "bash": {
                                    "*": "deny",
                                    "pnpm test": "allow",
                                    "pnpm *": action,
                                }
                            }
                        }
                    }
                }
            )
            violation = _opencode_config_policy_violation(config.encode(), metadata)
            assert violation is not None and "missing approved" in violation, action

    def test_allow_after_deny_baseline_is_executable(self) -> None:
        metadata = {**AICORE_RUNNER, "commands": ["pnpm test"]}
        config = json.dumps(
            {
                "agent": {
                    "crucible": {
                        "permission": {"bash": {"*": "deny", "pnpm test": "allow"}}
                    }
                }
            }
        )
        assert _opencode_config_policy_violation(config.encode(), metadata) is None

    def test_wildcard_matching_follows_opencode_semantics(self) -> None:
        assert _wildcard_match("*", "")
        assert _wildcard_match("*", "anything here")
        assert _wildcard_match("pnpm *", "pnpm test")
        assert _wildcard_match("p?pm test", "pnpm test")
        assert not _wildcard_match("p?pm test", "pnpm  test")
        assert not _wildcard_match("pnpm test", "pnpm testing")

    def test_effective_action_uses_last_matching_rule(self) -> None:
        assert (
            _effective_bash_action(
                {"*": "deny", "pnpm test": "allow", "pnpm *": "ask"}, "pnpm test"
            )
            == "ask"
        )
        assert (
            _effective_bash_action({"pnpm test": "allow", "*": "deny"}, "pnpm test")
            == "deny"
        )
        assert _effective_bash_action({"*": "deny"}, "pnpm test") == "deny"
        assert _effective_bash_action({}, "pnpm test") is None

    @pytest.mark.parametrize(
        "bad_action",
        ["Deny", "deny ", True, {"nested": "allow"}],
        ids=["capital-deny", "trailing-space", "boolean-true", "object"],
    )
    def test_non_canonical_action_fails_closed_with_earlier_allow(
        self, bad_action: object
    ) -> None:
        """Defeat 3: ``{"pnpm test": "allow", "pnpm *": <bad>}`` fails closed."""
        metadata = {**AICORE_RUNNER, "commands": ["pnpm test"]}
        config = json.dumps(
            {
                "agent": {
                    "crucible": {
                        "permission": {
                            "bash": {"pnpm test": "allow", "pnpm *": bad_action}
                        }
                    }
                }
            }
        )
        violation = _opencode_config_policy_violation(config.encode(), metadata)
        assert violation is not None, bad_action
        assert "unrecognized action" in violation

    @pytest.mark.parametrize(
        "bad_action",
        ["Deny", "deny ", True, {"nested": "allow"}],
        ids=["capital-deny", "trailing-space", "boolean-true", "object"],
    )
    def test_ordered_effect_never_resolves_non_canonical_action_to_allow(
        self, bad_action: object
    ) -> None:
        resolved = _effective_bash_action(
            {"pnpm test": "allow", "pnpm *": bad_action}, "pnpm test"
        )
        assert resolved != "allow"

    def test_broad_catch_all_is_a_violation(self) -> None:
        metadata = {**AICORE_RUNNER, "commands": ["pnpm test"]}
        for config in broad_grant_configs("crucible"):
            assert (
                _opencode_config_policy_violation(config.encode(), metadata) is not None
            ), config

    def test_broad_grant_helper_rejects_wildcards(self) -> None:
        commands = {"pnpm test", AICORE_SUITE_COMMAND}
        for broad in (
            "*", "**", "***", "****", "uv *", "uv **", "uv ***", "pytest *",
            "dotnet *", "dotnet **", "make *", "gradle *", "jest *",
            "uv run *", "python3 -c *", "pnpm install *", "dotnet test *",
        ):
            assert _broad_grant_violation(broad, commands) is not None, broad
        for scoped in (
            "pnpm install",
            "dotnet test",
            "pnpm test",
            AICORE_SUITE_COMMAND,
        ):
            assert _broad_grant_violation(scoped, commands) is None, scoped

    @pytest.mark.parametrize(
        "wildcard_command", ["uv run *", "pnpm ? test", "pytest -q *"]
    )
    def test_wildcard_command_declaration_is_invalid_declaration(
        self, wildcard_command: str
    ) -> None:
        block = (
            "test_runner:\n  commands:\n"
            f'    - "{wildcard_command}"\n'
            "  executor: crucible\n  scope: whole_project\n"
            "  reviewer: test-suite\n  evidence: destination reviewed\n"
        )
        path = self.write(
            self.root, "wildcard-command.yaml", MINIMAL_RUNNER_DECLARATION + block
        )
        with pytest.raises(SyncError) as caught:
            load_declaration(str(path))
        assert caught.value.code == "invalid_declaration"
        assert "wildcard" in caught.value.message

    def test_wildcard_approved_command_pair_fails_closed(self) -> None:
        """Defeat 2: ``commands: ["uv run *"]`` cannot launder a wildcard grant."""
        metadata = {**AICORE_RUNNER, "commands": ["uv run *"]}
        config = json.dumps(
            {"agent": {"crucible": {"permission": {"bash": {"uv run *": "allow"}}}}}
        )
        violation = _opencode_config_policy_violation(config.encode(), metadata)
        assert violation is not None
        assert "wildcard" in violation

    def test_unrelated_agent_grants_are_not_inspected(self) -> None:
        metadata = {**AICORE_RUNNER, "commands": ["pnpm test"]}
        config = unrelated_agent_grants_config("crucible", "pnpm test")
        assert _opencode_config_policy_violation(config.encode(), metadata) is None

    def test_no_tests_metadata_skips_grant_checks(self) -> None:
        assert (
            _opencode_config_policy_violation(
                b"// managed file\n{}\n", NO_TESTS_RUNNER
            )
            is None
        )

    def test_valid_no_tests_declaration_loads(self) -> None:
        path = self.write(self.root, "no-tests.yaml", ASSERTION_DECLARATION_NO_TESTS)
        loaded = load_declaration(str(path))
        assert loaded["test_runner"]["no_tests"] is True

    @pytest.mark.parametrize(
        "block",
        [
            "test_runner:\n  no_tests: true\n",
            "test_runner:\n  no_tests: true\n  reviewer: test-suite\n",
            "test_runner:\n  no_tests: true\n  evidence: destination has no tests\n",
            "test_runner:\n  no_tests: true\n  commands:\n    - pnpm test\n"
            "  reviewer: test-suite\n  evidence: destination has no tests\n",
        ],
    )
    def test_no_tests_requires_reviewer_and_evidence(self, block: str) -> None:
        path = self.write(
            self.root, "bad-no-tests.yaml", MINIMAL_RUNNER_DECLARATION + block
        )
        with pytest.raises(SyncError) as caught:
            load_declaration(str(path))
        assert caught.value.code == "invalid_declaration"

    def test_unknown_test_runner_key_is_invalid_declaration(self) -> None:
        block = (
            "test_runner:\n  commands:\n    - pnpm test\n  executor: crucible\n"
            "  scope: whole_project\n  reviewer: test-suite\n"
            "  evidence: destination reviewed\n  sweep: true\n"
        )
        path = self.write(
            self.root, "bad-unknown.yaml", MINIMAL_RUNNER_DECLARATION + block
        )
        with pytest.raises(SyncError) as caught:
            load_declaration(str(path))
        assert caught.value.code == "invalid_declaration"

    def test_check_accepts_reviewed_runner(self) -> None:
        fixture = self.build_assertions()
        self._with_grants(fixture, AICORE_SUITE_COMMAND)
        proc = self._check(fixture)
        assert proc.returncode in (0, 1), proc.stderr
        report = json.loads(proc.stdout)
        assert report["units"][0]["disposition"] != "policy_violation"

    def test_check_reports_policy_violation_for_path_variant(self) -> None:
        fixture = self.build_assertions()
        self._with_grants(fixture, "uv run --frozen --group dev pytest tests/ -q")
        proc = self._check(fixture)
        assert proc.returncode == 1, (proc.returncode, proc.stderr)
        report = json.loads(proc.stdout)
        assert not report["compliance"]
        assert any(
            reason.endswith("policy_violation") for reason in report["blocking_reasons"]
        )

    def test_check_reports_policy_violation_for_catch_all_allow(self) -> None:
        fixture = self.build_assertions()
        self._with_grants(fixture, "*")
        proc = self._check(fixture)
        assert proc.returncode == 1, (proc.returncode, proc.stderr)
        report = json.loads(proc.stdout)
        assert not report["compliance"]

    def test_propose_lock_refuses_bad_runner_with_empty_stdout(self) -> None:
        fixture = self.build_assertions()
        self._with_grants(fixture, "uv run --frozen --group dev pytest tests/ -q")
        proc = self._propose(fixture)
        self.assert_exit(proc, 2, "policy_violation")
        assert proc.stdout == ""

    def test_propose_lock_accepts_destination_package_test(self) -> None:
        fixture = self.build_assertions(
            declaration=ASSERTION_DECLARATION_DESTINATION_SUITE
        )
        self._with_grants(fixture, "pnpm test")
        proc = self._propose(fixture)
        assert proc.returncode == 0, (proc.returncode, proc.stderr)
        yaml.safe_load(proc.stdout)


VALID_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension note.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core rule.\n"
)

VALID_FRONTMATTER_LAYOUT = (
    "---\n"
    "name: reviewer\n"
    "mode: subagent\n"
    "version: 1.0.0\n"
    "---\n"
    "\n"
    "# Reviewer\n"
    "\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "**Persona / personality:** see `agents/reviewer/profile.md`.\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
)

QUOTED_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Inline quotation `> **Rule layout:** two-section-v1` is a syntax example.\n"
    "\n"
    "| field | value |\n"
    "|---|---|\n"
    "| marker | `> **Rule layout:** two-section-v1` |\n"
    "\n"
    "```markdown\n"
    "> **Rule layout:** two-section-v1\n"
    "## Project extensions\n"
    "## Mandatory core\n"
    "```\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core rule.\n"
)

MISSING_MARKER_LAYOUT = (
    "# Reviewer\n\n## Project extensions\n\nExtension.\n\n## Mandatory core\n\nCore.\n"
)

DUPLICATE_MARKER_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
)

MISPLACED_MARKER_LAYOUT = (
    "# Reviewer\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
)

OPERATIONAL_INTRO_LAYOUT = (
    "# Reviewer\n"
    "\n"
    "This operational sentence must not be framing.\n"
    "\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
)

BLOCKQUOTED_INTRO_LAYOUT = (
    "# Reviewer\n"
    "> **Note:** an operational blockquote is not version metadata.\n"
    "\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
)

OUT_OF_ORDER_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension.\n"
)

ORPHAN_REGION_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension.\n"
    "\n"
    "## Orphan\n"
    "\n"
    "Orphan.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
)

# A leading ``---`` whose only exact close lies at/after the first ownership
# heading must not open frontmatter and hide operational prose.
FAKE_FRONTMATTER_CLOSE_LAYOUT = (
    "---\n"
    "name: x\n"
    "> **Rule layout:** two-section-v1\n"
    "OPERATIONAL PROSE THAT MUST BE REJECTED\n"
    "## Project extensions\n"
    "ext\n"
    "## Mandatory core\n"
    "CORE\n"
    "---\n"
)

FENCED_FAKE_FRONTMATTER_CLOSE_LAYOUT = (
    "---\n"
    "name: x\n"
    "> **Rule layout:** two-section-v1\n"
    "OPERATIONAL PROSE THAT MUST BE REJECTED\n"
    "## Project extensions\n"
    "ext\n"
    "```markdown\n"
    "---\n"
    "```\n"
    "## Mandatory core\n"
    "CORE\n"
)

# A real ``--- ... ---`` block can still hide non-YAML operational prose.
HIDDEN_INTRO_IN_FRONTMATTER_LAYOUT = (
    "---\n"
    "name: x\n"
    "> ## Project extensions\n"
    "OPERATIONAL PROSE\n"
    "---\n"
    "> **Rule layout:** two-section-v1\n"
    "## Project extensions\n"
    "ext\n"
    "## Mandatory core\n"
    "CORE\n"
)

# Indented prose inside a real block is not a YAML continuation of a key with a
# value, and an orphan indented list item has no preceding key/block opener.
INDENTED_HIDDEN_INTRO_LAYOUT = (
    "---\n"
    "name: x\n"
    "  > ## Project extensions\n"
    "  OPERATIONAL PROSE\n"
    "---\n"
    "> **Rule layout:** two-section-v1\n"
    "## Project extensions\n"
    "ext\n"
    "## Mandatory core\n"
    "CORE\n"
)

ORPHAN_INDENTED_PROSE_LAYOUT = (
    "---\n"
    "  - OPERATIONAL PROSE\n"
    "name: x\n"
    "---\n"
    "> **Rule layout:** two-section-v1\n"
    "## Project extensions\n"
    "ext\n"
    "## Mandatory core\n"
    "CORE\n"
)

TAB_H2_LAYOUT = VALID_LAYOUT.replace(
    "## Mandatory core\n",
    "##\tHidden region\n\n## Mandatory core\n",
)
INDENTED_H2_LAYOUT = VALID_LAYOUT.replace(
    "## Mandatory core\n",
    " ## Hidden region\n\n   ## Also hidden\n\n## Mandatory core\n",
)
INVALID_FENCE_INFO_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension note.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core rule.\n"
    "```bad`info\n"
    "## Extra ownership\n"
    "```\n"
)
INVALID_CLOSER_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension note.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core rule.\n"
    "```\n"
    "example\n"
    "``` trailing\n"
    "## Extra ownership\n"
)
SHORT_BACKTICK_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension note.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core rule.\n"
    "`\n"
    "## Extra ownership\n"
)
SHORT_TILDE_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension note.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core rule.\n"
    "~~\n"
    "## Extra ownership\n"
)
INDENTED_CODE_FENCE_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension note.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core rule.\n"
    "    ```\n"
    "## Extra ownership\n"
    "    ```\n"
)
FRAMING_FENCE_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "```markdown\n"
    "hidden operational prose\n"
    "```\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
)
INTERNAL_TILDE_FENCE_LAYOUT = (
    "# Reviewer\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "~~~markdown\n"
    "## Project extensions\n"
    "## Mandatory core\n"
    "~~~\n"
    "\n"
    "   ```\n"
    "   ## Not an ownership heading\n"
    "   ```\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core rule.\n"
)
RICH_FRONTMATTER_LAYOUT = (
    "---\n"
    "# reviewer metadata\n"
    "name: reviewer\n"
    "description: |\n"
    "  reviews changes\n"
    "  across lines\n"
    "metadata:\n"
    "  owner: core\n"
    "  tags:\n"
    "    - layout\n"
    "---\n"
    "\n"
    "# Reviewer\n"
    "\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "Extension.\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "Core.\n"
)
MALFORMED_SCALAR_LAYOUT = (
    "---\n"
    "name: \"unterminated\n"
    "---\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "ext\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "CORE\n"
)
UNSAFE_TAG_LAYOUT = (
    "---\n"
    "name: !!python/object/apply:os.system [\"true\"]\n"
    "---\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "ext\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "CORE\n"
)
LIST_FRONTMATTER_LAYOUT = (
    "---\n"
    "- not-a-mapping\n"
    "---\n"
    "> **Rule layout:** two-section-v1\n"
    "\n"
    "## Project extensions\n"
    "\n"
    "ext\n"
    "\n"
    "## Mandatory core\n"
    "\n"
    "CORE\n"
)

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


def _repository_root() -> Path:
    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".aicore" / "core-catalog-v2.yaml").is_file():
            return candidate
    raise AssertionError("repository root with the v2 catalog was not found")


_MARKER = "> **Rule layout:** two-section-v1\n"
_EXTENSIONS = _MARKER + "## Project extensions\n"
_CORE = "## Mandatory core\nCORE\n"
_VALID = _EXTENSIONS + _CORE
_ORPHAN = "orphan region: expected exactly two ownership headings"
_UNSUPPORTED = "orphan region: unsupported Markdown block context"
_SEPARATORS = (
    "\u000b",
    "\u000c",
    "\u001c",
    "\u001d",
    "\u001e",
    "\u0085",
    "\u2028",
    "\u2029",
)
_YAML_FORBIDDEN = ("\u000b", "\u000c", "\u001c", "\u001d", "\u001e")
_YAML_QUOTED_SEPARATORS = ("\u0085", "\u2028", "\u2029")


def _assert_valid(document: str) -> None:
    layout, violation = _scan_rule_layout(document)
    assert layout is not None, violation
    assert violation is None
    assert layout.framing + layout.extensions + layout.mandatory == document.encode("utf-8")


class LayoutContractTests:
    """Single layout owner: corpus partitions and distinct boundary attacks.

    Parser cases do not inherit the repository fixture. One scan supplies both
    the layout and the diagnostic.
    """

    def test_valid_framing_with_quotations_accepts(self) -> None:
        layout = _rule_layout(QUOTED_LAYOUT)
        assert layout is not None
        assert layout.mandatory.endswith(b"Core rule.\n")
        assert b"Inline quotation" in layout.extensions
        assert _rule_layout_violation(QUOTED_LAYOUT) is None
        # The quoted fenced headings are not ownership boundaries: only the two
        # real headings are extracted, so the mandatory core matches exactly.
        quoted = _rule_layout(QUOTED_LAYOUT)
        plain = _rule_layout(VALID_LAYOUT)
        assert quoted is not None and plain is not None
        assert quoted.mandatory == plain.mandatory
        assert quoted.framing == plain.framing
        assert quoted.extensions != plain.extensions

    @pytest.mark.parametrize(
        ("document", "fragment"),
        (
            (MISSING_MARKER_LAYOUT, "missing"),
            (DUPLICATE_MARKER_LAYOUT, "duplicate"),
            (MISPLACED_MARKER_LAYOUT, "precede"),
            (OPERATIONAL_INTRO_LAYOUT, "operational prose"),
            (BLOCKQUOTED_INTRO_LAYOUT, "operational prose"),
            (FAKE_FRONTMATTER_CLOSE_LAYOUT, "operational prose"),
            (FENCED_FAKE_FRONTMATTER_CLOSE_LAYOUT, "operational prose"),
            (HIDDEN_INTRO_IN_FRONTMATTER_LAYOUT, "operational prose"),
            (INDENTED_HIDDEN_INTRO_LAYOUT, "operational prose"),
            (ORPHAN_INDENTED_PROSE_LAYOUT, "operational prose"),
            (OUT_OF_ORDER_LAYOUT, "first ownership heading"),
            (ORPHAN_REGION_LAYOUT, "orphan region"),
        ),
    )
    def test_marker_contract_rejections(self, document: str, fragment: str) -> None:
        layout, violation = _scan_rule_layout(document)
        assert layout is None
        assert violation is not None
        assert fragment in violation

    def test_bounded_frontmatter_close_accepts_valid_frontmatter(self) -> None:
        assert _rule_layout_violation(VALID_FRONTMATTER_LAYOUT) is None
        layout = _rule_layout(VALID_FRONTMATTER_LAYOUT)
        assert layout is not None
        assert b"Persona / personality" in layout.framing
        assert layout.mandatory.endswith(b"Core.\n")

    def test_mandatory_bytes_ignore_framing_and_extension_differences(self) -> None:
        source = _rule_layout(VALID_LAYOUT)
        destination = _rule_layout(
            VALID_LAYOUT.replace("# Reviewer", "# Relay").replace(
                "Extension note.", "Destination extension note."
            )
        )
        assert source is not None and destination is not None
        assert source.mandatory == destination.mandatory
        assert source.extensions != destination.extensions
        assert source.framing != destination.framing

    def test_noncanonical_headings_and_invalid_fences_reject(self) -> None:
        for document, fragment in (
            (TAB_H2_LAYOUT, "orphan region"),
            (INDENTED_H2_LAYOUT, "orphan region"),
            (INVALID_FENCE_INFO_LAYOUT, "orphan region"),
            (INDENTED_CODE_FENCE_LAYOUT, "orphan region"),
            (SHORT_BACKTICK_LAYOUT, "orphan region"),
            (SHORT_TILDE_LAYOUT, "orphan region"),
            (FRAMING_FENCE_LAYOUT, "operational prose"),
        ):
            violation = _rule_layout_violation(document)
            assert violation is not None, document
            assert fragment in violation, (fragment, violation)
        layout = _rule_layout(INVALID_CLOSER_LAYOUT)
        assert layout is not None
        assert _rule_layout_violation(INVALID_CLOSER_LAYOUT) is None
        assert b"``` trailing\n## Extra ownership\n" in layout.mandatory

    def test_internal_fences_do_not_create_ownership_regions(self) -> None:
        layout = _rule_layout(INTERNAL_TILDE_FENCE_LAYOUT)
        assert layout is not None
        assert layout.mandatory == _rule_layout(VALID_LAYOUT).mandatory
        assert b"## Project extensions" in layout.extensions
        assert _rule_layout_violation(INTERNAL_TILDE_FENCE_LAYOUT) is None

    def test_yaml_mapping_frontmatter_accepts_comments_blocks_and_nesting(self) -> None:
        layout = _rule_layout(RICH_FRONTMATTER_LAYOUT)
        assert layout is not None
        assert _rule_layout_violation(RICH_FRONTMATTER_LAYOUT) is None
        assert layout.mandatory.endswith(b"Core.\n")
        assert b"reviews changes" in layout.framing

    def test_malformed_frontmatter_rejects_without_inferring_prose(self) -> None:
        for document in (
            MALFORMED_SCALAR_LAYOUT,
            UNSAFE_TAG_LAYOUT,
            LIST_FRONTMATTER_LAYOUT,
        ):
            violation = _rule_layout_violation(document)
            assert violation is not None, document
            assert "operational prose" in violation
            assert "YAML" in violation or "mapping" in violation

    def test_mandatory_slice_is_the_unnormalized_byte_suffix(self) -> None:
        document = VALID_LAYOUT.replace("Core rule.\n", "Core rule.  \n")
        layout = _rule_layout(document)
        assert layout is not None
        start = document.index("## Mandatory core\n")
        assert layout.mandatory == document[start:].encode("utf-8")
        assert layout.mandatory.endswith(b"Core rule.  \n")

    def test_every_catalog_rule_document_has_a_valid_layout(self) -> None:
        root = _repository_root()
        catalog = load_catalog(str(root / ".aicore" / "core-catalog-v2.yaml"))
        paths = [
            str(document)
            for unit in catalog["units"]
            for document in (unit.get("rule_documents") or [])
        ]
        distinct = sorted(set(paths))
        assert len(distinct) == 27, distinct
        for document in distinct:
            raw = (root / document).read_bytes()
            text = raw.decode("utf-8")
            layout, violation = _scan_rule_layout(text)
            assert layout is not None, (document, violation)
            assert layout.framing + layout.extensions + layout.mandatory == raw

    def test_p01_valid_document_keeps_exact_mandatory_bytes(self) -> None:
        _assert_valid(_VALID)
        layout = _rule_layout(_VALID)
        assert layout is not None
        assert layout.mandatory == _CORE.encode("utf-8")

    def test_p02_trailing_info_before_mandatory_is_orphan(self) -> None:
        document = _EXTENSIONS + "~~~text\n~~~not-a-close\n" + _CORE
        assert _rule_layout(document) is None
        assert _rule_layout_violation(document) == _ORPHAN
        assert document.endswith(_CORE)

    def test_p03_later_valid_closer_keeps_example_fenced(self) -> None:
        document = _EXTENSIONS + "~~~text\n~~~not-a-close\n## Example\n~~~\n" + _CORE
        _assert_valid(document)
        layout = _rule_layout(document)
        assert layout is not None
        assert b"## Example\n" in layout.extensions
        assert layout.mandatory == _CORE.encode("utf-8")

    def test_p04_shorter_closer_is_literal(self) -> None:
        document = _EXTENSIONS + "````\n```\n## Example\n````\n" + _CORE
        _assert_valid(document)
        layout = _rule_layout(document)
        assert layout is not None
        assert b"## Example\n" in layout.extensions

    def test_p05_other_delimiter_is_literal(self) -> None:
        document = _EXTENSIONS + "```\n~~~\n## Example\n```\n" + _CORE
        _assert_valid(document)
        layout = _rule_layout(document)
        assert layout is not None
        assert b"## Example\n" in layout.extensions

    def test_p06_indented_closer_is_literal(self) -> None:
        document = _EXTENSIONS + "```\n    ```\n## Example\n```\n" + _CORE
        _assert_valid(document)
        layout = _rule_layout(document)
        assert layout is not None
        assert b"## Example\n" in layout.extensions

    def test_p07_unclosed_trailing_info_is_valid_mandatory_drift(self) -> None:
        document = _VALID + "```\n``` trailing\n## Example\n"
        _assert_valid(document)
        base = _rule_layout(_VALID)
        drifted = _rule_layout(document)
        assert base is not None and drifted is not None
        assert drifted.mandatory != base.mandatory
        assert b"## Example\n" in drifted.mandatory

    def test_p08_invalid_openers_do_not_hide_extra_headings(self) -> None:
        for document in (
            _VALID + "```bad`info\n## Extra\n",
            _VALID + "`\n## Extra\n",
            _VALID + "~~\n## Extra\n",
        ):
            assert _rule_layout_violation(document) == _ORPHAN

    def test_p09_dash_setext_underlines_are_extra_headings(self) -> None:
        for underline in ("---", "-", "--"):
            document = _EXTENSIONS + "Extra\n" + underline + "\n" + _CORE
            assert _rule_layout_violation(document) == _ORPHAN

    def test_container_shaped_setext_underline_is_orphan(self) -> None:
        document = _EXTENSIONS + "Extra ownership\n- \n" + _CORE
        assert _rule_layout_violation(document) == _ORPHAN
        _assert_valid(_EXTENSIONS + "- item\n" + _CORE)

    def test_p10_multiline_paragraph_setext_is_extra_heading(self) -> None:
        document = _EXTENSIONS + "First line\nsecond line\n---\n" + _CORE
        assert _rule_layout_violation(document) == _ORPHAN

    def test_p11_blank_line_resets_setext_paragraph(self) -> None:
        _assert_valid(_EXTENSIONS + "Extra\n\n---\n" + _CORE)

    def test_p12_atx_does_not_seed_setext(self) -> None:
        for heading in ("### Example", "# Example"):
            _assert_valid(_EXTENSIONS + heading + "\n---\n" + _CORE)

    def test_p13_thematic_break_and_equals_setext_are_not_h2(self) -> None:
        _assert_valid(_EXTENSIONS + "Extra\n- - -\n" + _CORE)
        _assert_valid(_EXTENSIONS + "Extra\n===\n---\n" + _CORE)

    def test_p14_fenced_and_indented_setext_examples_are_literal(self) -> None:
        _assert_valid(_EXTENSIONS + "```\nExtra\n---\n```\n" + _CORE)
        _assert_valid(_EXTENSIONS + "\n    Extra\n    ---\n" + _CORE)

    def test_p15_setext_is_not_a_canonical_ownership_spelling(self) -> None:
        document = _MARKER + "Project extensions\n---\n" + _CORE
        violation = _rule_layout_violation(document)
        assert violation == "first ownership heading must be '## Project extensions'"

    def test_p16_indented_continuation_before_setext_is_unsupported(self) -> None:
        document = _EXTENSIONS + "Extra\n    continuation\n---\n" + _CORE
        assert _rule_layout_violation(document) == _UNSUPPORTED

    def test_p17_block_and_folded_scalars_do_not_enter_markdown_state(self) -> None:
        for indicator in ("|", ">"):
            document = (
                "---\n"
                f"description: {indicator}\n"
                "  ## Fake\n"
                "  ```\n"
                "  Extra\n"
                "  ---\n"
                "  > **Rule layout:** two-section-v1\n"
                "---\n"
                + _VALID
            )
            _assert_valid(document)
            layout = _rule_layout(document)
            assert layout is not None
            assert layout.mandatory == _CORE.encode("utf-8")
            assert b"## Fake\n" in layout.framing

    def test_p18_quoted_scalar_example_does_not_enter_markdown_state(self) -> None:
        document = (
            "---\n"
            'description: "text\n'
            "## Fake\n"
            "```\n"
            "> **Rule layout:** two-section-v1\n"
            '"\n'
            "---\n"
            + _VALID
        )
        _assert_valid(document)
        layout = _rule_layout(document)
        assert layout is not None
        assert b"## Fake\n" in layout.framing
        assert layout.mandatory == _CORE.encode("utf-8")

    def test_p19_mapping_accepts_and_nonmapping_malformed_and_unsafe_reject(self) -> None:
        mapping = (
            "---\n"
            "# reviewer metadata\n"
            "name: reviewer\n"
            "metadata:\n"
            "  owner: core\n"
            "---\n"
            + _VALID
        )
        _assert_valid(mapping)
        sequence = "---\n- not-a-mapping\n---\n" + _VALID
        unterminated = '---\nname: "unterminated\n---\n' + _VALID
        unsafe = '---\nname: !!python/object/apply:os.system ["true"]\n---\n' + _VALID
        for document in (sequence, unterminated, unsafe):
            violation = _rule_layout_violation(document)
            assert violation is not None
            assert violation.startswith("operational prose outside ownership sections: ")
            assert "invalid YAML framing" in violation or "YAML mapping" in violation

    def test_p20_missing_late_and_heading_frontmatter_never_accept(self) -> None:
        missing = "---\nname: x\n" + _VALID
        assert _rule_layout_violation(missing) == (
            "operational prose outside ownership sections: "
            "missing bounded YAML frontmatter close"
        )
        late = missing + "---\n"
        late_violation = _rule_layout_violation(late)
        assert late_violation is not None
        assert late_violation.startswith("operational prose outside ownership sections: ")
        hidden = (
            "---\n"
            "name: x\n"
            "## Project extensions\n"
            "## Mandatory core\n"
            "---\n"
            + _VALID
        )
        assert _rule_layout_violation(hidden) == (
            "operational prose outside ownership sections: "
            "frontmatter close must precede ownership headings"
        )

    def test_p21_crlf_trailing_spaces_and_missing_newline_partition_exactly(self) -> None:
        document = (
            "# Reviewer café\r\n"
            "> **Rule layout:** two-section-v1\r\n"
            "\r\n"
            "## Project extensions\r\n"
            "\r\n"
            "Extension note.  \r\n"
            "## Mandatory core\r\n"
            "Core rule.  "
        )
        layout = _rule_layout(document)
        assert layout is not None
        raw = document.encode("utf-8")
        assert layout.framing + layout.extensions + layout.mandatory == raw
        assert layout.framing == document[: document.index("## Project extensions")].encode("utf-8")
        assert layout.extensions == document[
            document.index("## Project extensions") : document.index("## Mandatory core")
        ].encode("utf-8")
        assert layout.mandatory == document[document.index("## Mandatory core") :].encode("utf-8")
        assert b"\r\n" in layout.mandatory
        assert b"\n" not in layout.mandatory.replace(b"\r\n", b"")

    def test_p23_quote_list_and_table_examples_do_not_seed_headings(self) -> None:
        document = (
            _EXTENSIONS
            + "> ## Quoted example\n"
            + "\n"
            + "- List item\n"
            + "\n"
            + "| A | B |\n"
            + "| --- | --- |\n"
            + "| ## Literal | row |\n"
            + "\n"
            + _CORE
        )
        _assert_valid(document)
        layout = _rule_layout(document)
        assert layout is not None
        assert b"> ## Quoted example\n" in layout.extensions
        assert b"| ## Literal | row |\n" in layout.extensions
        assert layout.mandatory == _CORE.encode("utf-8")

    def test_p24_lazy_container_continuation_is_unsupported(self) -> None:
        document = _EXTENSIONS + "- Item\ncontinuation\n---\n" + _CORE
        assert _rule_layout_violation(document) == _UNSUPPORTED

    def test_p25_standalone_html_opener_is_unsupported(self) -> None:
        document = _EXTENSIONS + "<div>\n## Hidden\n</div>\n" + _CORE
        assert _rule_layout_violation(document) == _UNSUPPORTED

    def test_p26_inline_and_fenced_html_remain_literal(self) -> None:
        document = (
            _EXTENSIONS
            + "Use <span>inline</span> text.\n"
            + "\n"
            + "```html\n"
            + "<div>\n"
            + "## Example\n"
            + "</div>\n"
            + "```\n"
            + _CORE
        )
        _assert_valid(document)
        layout = _rule_layout(document)
        assert layout is not None
        assert b"<div>\n" in layout.extensions
        assert layout.mandatory == _CORE.encode("utf-8")

    def test_p27_cr_only_partitions_are_not_normalized(self) -> None:
        document = _VALID.replace("\n", "\r")
        layout = _rule_layout(document)
        assert layout is not None
        raw = document.encode("utf-8")
        assert layout.framing + layout.extensions + layout.mandatory == raw
        assert b"\n" not in raw
        assert layout.mandatory == _CORE.replace("\n", "\r").encode("utf-8")

    def test_p28_separator_fence_and_yaml_controls_follow_reader_rules(self) -> None:
        for separator in _SEPARATORS:
            body = _EXTENSIONS + "text" + separator + "## Extra\n" + _CORE
            assert _rule_layout_violation(body) == _UNSUPPORTED, repr(separator)
            fenced = _EXTENSIONS + "```text\nA" + separator + "B\n```\n" + _CORE
            _assert_valid(fenced)
            layout = _rule_layout(fenced)
            assert layout is not None
            assert separator.encode("utf-8") in (
                layout.framing + layout.extensions + layout.mandatory
            )
        for control in _YAML_FORBIDDEN:
            document = '---\ndescription: "A' + control + 'B"\n---\n' + _VALID
            violation = _rule_layout_violation(document)
            assert violation is not None
            assert violation.startswith(
                "operational prose outside ownership sections: invalid YAML framing"
            )
        for separator in _YAML_QUOTED_SEPARATORS:
            document = '---\ndescription: "A' + separator + 'B"\n---\n' + _VALID
            _assert_valid(document)
            layout = _rule_layout(document)
            assert layout is not None
            assert separator.encode("utf-8") in layout.framing
        for escape in ("\\x0B", "\\x0C", "\\x1C", "\\x1D", "\\x1E"):
            document = '---\ndescription: "A' + escape + 'B"\n---\n' + _VALID
            _assert_valid(document)
            assert escape in document
            assert "\u000b" not in document
            assert "\u000c" not in document
            assert "\u001c" not in document
            assert "\u001d" not in document
            assert "\u001e" not in document
