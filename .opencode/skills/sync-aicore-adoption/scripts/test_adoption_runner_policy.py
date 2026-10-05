"""Destination-owned test_runner metadata and designated-executor grant tests."""

from __future__ import annotations

import json
import subprocess

import pytest
import yaml

from adoption_test_repos import EngineTestCase

from adoption_constants import AICORE_SUITE_COMMAND
from adoption_contracts import SyncError
from adoption_loaders import load_declaration
from adoption_policies import (
    _JsoncCommentError,
    _broad_grant_violation,
    _effective_bash_action,
    _opencode_config_policy_violation,
    _strip_jsonc_comments,
    _wildcard_match,
)
from adoption_test_prepared import _bind_review_to_baseline
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
