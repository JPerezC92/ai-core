"""Focused runner metadata, declarations and permission-grant templates.

The destination-owned ``test_runner`` contract and the OpenCode
``agent.<executor>.permission.bash`` grant matrices are reviewed data, not test
actions, so they live in this single owner. Tests import the real owner directly
and keep only small action-specific inputs, such as the command under test,
inline.
"""

from __future__ import annotations

import json

from adoption_constants import AICORE_SUITE_COMMAND

AICORE_RUNNER: dict[str, object] = {
    "commands": [AICORE_SUITE_COMMAND],
    "executor": "crucible",
    "scope": "whole_project",
    "reviewer": "test-suite",
    "evidence": "aicore-whole-suite-reviewed",
}

NO_TESTS_RUNNER: dict[str, object] = {
    "no_tests": True,
    "reviewer": "test-suite",
    "evidence": "destination has no tests",
}

MINIMAL_RUNNER_DECLARATION = (
    "schema_version: 2\n"
    "upstream_repository: example/upstream\n"
    "profile: { backend_stack: false, python_scripts: false, ticket_system: false }\n"
    "units: []\n"
)

# A hermetic mirror of AICore's reviewed root ``opencode.jsonc`` shape: a
# ``https://`` schema URL (slashes inside a string), a line comment, unrelated
# ``plan``/``build`` agents, the nominated ``crucible`` block with the
# deny-first baseline plus the literal install and exact suite allows, and a
# global ``permission`` block whose ``bash`` entry carries a ``/*`` string and
# wildcard denies. It is pinned here so runner validation never reads mutable
# live-repository state.
AICORE_ROOT_CONFIG = (
    '{\n'
    '    "$schema": "https://opencode.ai/config.json",\n'
    '    "autoupdate": true,\n'
    '    "agent": {\n'
    '        "plan": {"permission": {"question": "allow"}},\n'
    '        "build": {"permission": {"question": "allow"}},\n'
    '        "crucible": {\n'
    '            "permission": {\n'
    '                "bash": {\n'
    '                    "*": "deny",\n'
    '                    "pnpm install": "allow",\n'
    f'                    "{AICORE_SUITE_COMMAND}": "allow"\n'
    '                }\n'
    '            }\n'
    '        }\n'
    '    },\n'
    '    // Project instructions (optional): point at your own docs.\n'
    '    "permission": {\n'
    '        "read": {"*": "allow", "*.env": "deny", "*.env.*": "deny"},\n'
    '        "glob": "allow",\n'
    '        "grep": "allow",\n'
    '        "question": "deny",\n'
    '        "edit": "allow",\n'
    '        "bash": {\n'
    '            "*": "allow",\n'
    '            "rm -rf /*": "deny",\n'
    '            "sudo *": "deny"\n'
    '        }\n'
    '    }\n'
    '}\n'
)

ASSERTION_DECLARATION_DESTINATION_SUITE = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: opencode-config
    mode: mirror
  - id: gitignore-config
    mode: mirror
test_runner:
  commands:
    - pnpm test
  executor: crucible
  scope: whole_project
  reviewer: test-suite
  evidence: destination-whole-suite-reviewed
"""

ASSERTION_DECLARATION_NO_TESTS = """schema_version: 2
upstream_repository: example/upstream
profile: { backend_stack: false, python_scripts: false, ticket_system: false }
units:
  - id: opencode-config
    mode: mirror
  - id: gitignore-config
    mode: mirror
test_runner:
  no_tests: true
  reviewer: test-suite
  evidence: destination-has-no-tests
"""


def opencode_runner_config(
    *allows: str,
    executor: str = "crucible",
    sudo_deny: bool = True,
) -> str:
    """Return a valid JSONC config granting ``allows`` to ``executor``.

    The config is a real JSONC object so the destination policy can parse it.
    It always carries the deny-first ``"*": "deny"`` baseline, the catalog's
    ``"sudo *": "deny"`` assertion, and one ``allow`` entry per requested
    command under ``agent.<executor>.permission.bash``.
    """
    bash: dict[str, str] = {"*": "deny"}
    if sudo_deny:
        bash["sudo *"] = "deny"
    for allow in allows:
        bash[allow] = "allow"
    document = {"agent": {executor: {"permission": {"bash": bash}}}}
    return "// managed file\n" + json.dumps(document, indent=2) + "\n"


def misnested_other_agent_config(executor: str, command: str) -> str:
    """Return a config that grants ``command`` only to an unrelated agent."""
    return json.dumps(
        {
            "agent": {
                executor: {"permission": {"bash": {"*": "deny"}}},
                "warden": {"permission": {"bash": {command: "allow"}}},
            }
        }
    )


def misnested_top_level_config(executor: str, command: str) -> str:
    """Return a config granting ``command`` at top level, not under ``executor``."""
    return json.dumps(
        {
            "agent": {executor: {"permission": {"bash": {"*": "deny"}}}},
            "permission": {"bash": {command: "allow"}},
        }
    )


def unrelated_agent_grants_config(executor: str, command: str) -> str:
    """Return a config with a valid executor grant and broad unrelated grants.

    The unrelated agent keeps Git, install and wildcard test grants that the
    narrow, executor-scoped validation must never inspect.
    """
    return json.dumps(
        {
            "agent": {
                executor: {"permission": {"bash": {"*": "deny", command: "allow"}}},
                "warden": {
                    "permission": {
                        "bash": {
                            "*": "deny",
                            "git status": "allow",
                            "pnpm install": "allow",
                            "pytest *": "allow",
                        }
                    }
                },
            }
        }
    )


def broad_grant_configs(executor: str) -> tuple[str, ...]:
    """Return configs whose executor allow entry grants arbitrary command text."""
    return (
        json.dumps({"agent": {executor: {"permission": {"bash": "*"}}}}),
        json.dumps({"agent": {executor: {"permission": {"bash": {"*": "allow"}}}}}),
        json.dumps(
            {"agent": {executor: {"permission": {"bash": {"pnpm *": "allow"}}}}}
        ),
        json.dumps(
            {"agent": {executor: {"permission": {"bash": {"dotnet *": "allow"}}}}}
        ),
        json.dumps(
            {"agent": {executor: {"permission": {"bash": {"uv **": "allow"}}}}}
        ),
        json.dumps(
            {"agent": {executor: {"permission": {"bash": {"dotnet **": "allow"}}}}}
        ),
        json.dumps(
            {"agent": {executor: {"permission": {"bash": {"***": "allow"}}}}}
        ),
        json.dumps(
            {"agent": {executor: {"permission": {"bash": {"uv run *": "allow"}}}}}
        ),
        json.dumps(
            {"agent": {executor: {"permission": {"bash": {"python3 -c *": "allow"}}}}}
        ),
    )
