"""Integration contract for region-delimited AICore agent source surfaces."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from support.agent_spec_documents import (  # noqa: E402
    AGENT_SPECS_DIR,
    CORE_BEGIN,
    CORE_END,
    PROJECT_BEGIN,
    PROJECT_END,
    REPO_ROOT,
    exact_marker_line_indices,
    extract_source_core,
    find_core_markers,
    split_frontmatter,
    unfenced_lines,
)


SPEC_H3 = (
    "Your Role",
    "Roster Context",
    "Rulebook",
    "Workflow",
    "Tools and References",
    "Output Format",
    "Stop and Report",
    "Hard Rules",
)

CORE_ANCHORS = {
    "atrium.md": "typescript/react.md",
    "forge.md": "Static Data Service Pattern",
    "ledger.md": "Close out now",
    "sentinel.md": "node_modules/",
    "vault.md": "Harness Parent Directories",
    "warden.md": "pnpm audit",
}

LOCAL_ONLY = {
    "crucible.md": (
        "The AICore project's narrow read-only discovery allowance includes "
        "`rg`, `ls`, and `wc`. These commands are not test execution or a "
        "package install. No Git command is authorized: the core no-Git "
        "boundary applies to read-only Git as well as mutations, regardless "
        "of any conflicting harness allow.",
    ),
    "warden.md": (
        "In AICore, use `uv audit --frozen` for the Python advisory check.",
        "Python-environment reference commands were added 2026-06-13 and "
        "validated against uv 0.11.8",
        "The project's reviewed whole-suite command is "
        "`uv run --frozen --group dev pytest -q`.",
    ),
    "herald.md": (
        "This project's protected upstream base ref is `origin/main` — remote "
        "`origin`, branch `main`.",
    ),
}

_CORE_DELIMITERS = {CORE_BEGIN, CORE_END}


def _spec_surfaces() -> list[Path]:
    return sorted(AGENT_SPECS_DIR.glob("*.md"))


def _project_text(content: str) -> str:
    lines = content.splitlines()
    begins = exact_marker_line_indices(lines, PROJECT_BEGIN)
    ends = exact_marker_line_indices(lines, PROJECT_END)
    assert len(begins) == 1 and len(ends) == 1
    return "\n".join(lines[begins[0] + 1 : ends[0]])


def test_agent_sources_place_core_markers_after_frontmatter() -> None:
    spec_paths = _spec_surfaces()
    assert len(spec_paths) == 14

    for path in spec_paths:
        content = path.read_text(encoding="utf-8")
        frontmatter, body = split_frontmatter(content)
        core_markers = find_core_markers(content)
        assert frontmatter, path
        frontmatter_lines = frontmatter.splitlines()
        assert frontmatter_lines[0].strip() == "---", path
        assert frontmatter_lines[-1].strip() == "---", path
        assert core_markers is not None, path
        assert body.startswith(f"{CORE_BEGIN}\n"), path
        assert core_markers[0] == len(frontmatter.splitlines()), path
        core = extract_source_core(content)
        assert core.strip(), path
        assert not any(
            line.strip() in _CORE_DELIMITERS for line in unfenced_lines(core)
        ), path


def test_agent_spec_cores_keep_h3_order() -> None:
    spec_paths = _spec_surfaces()
    for path in spec_paths:
        core = extract_source_core(path.read_text(encoding="utf-8"))
        headings = [
            line.strip()[4:]
            for line in unfenced_lines(core)
            if line.strip() in {f"### {heading}" for heading in SPEC_H3}
        ]
        assert headings == list(SPEC_H3), path


def test_agent_spec_cores_keep_positive_anchors() -> None:
    spec_paths = _spec_surfaces()
    for path in spec_paths:
        anchor = CORE_ANCHORS.get(path.name)
        if anchor is None:
            continue
        core = extract_source_core(path.read_text(encoding="utf-8"))
        assert anchor in core, path


def test_agent_sources_keep_local_facts_out_of_core() -> None:
    for name, facts in LOCAL_ONLY.items():
        content = (AGENT_SPECS_DIR / name).read_text(encoding="utf-8")
        core = extract_source_core(content)
        project = _project_text(content)
        for fact in facts:
            assert fact not in core, name
            assert fact in project, name


def test_agent_sources_keep_optional_project_region_shape() -> None:
    spec_paths = _spec_surfaces()
    for path in spec_paths:
        lines = path.read_text(encoding="utf-8").splitlines()
        begins = exact_marker_line_indices(lines, PROJECT_BEGIN)
        ends = exact_marker_line_indices(lines, PROJECT_END)
        assert len(begins) == len(ends) <= 1, path
        if begins:
            assert begins[0] > 0 and lines[begins[0] - 1].strip() == "", path
            assert lines[-1].strip() == PROJECT_END, path
        else:
            assert lines[-1].strip() == CORE_END, path


HARNESS_CONFIG_PATH = REPO_ROOT / "opencode.jsonc"

# The base policy every OpenCode agent starts with. Only its shell-relevant row
# is exercised here.
BASE_PERMISSION_POLICY = [
    {"action": "*", "resource": "*", "effect": "allow"},
]


def _strip_jsonc_comments(text: str) -> str:
    """Return `text` with `//` comments removed outside double-quoted strings.

    A `//` inside a string is part of the value — a URL, for example — and is
    kept, so only a comment that starts outside a string is dropped.
    """
    out: list[str] = []
    in_string = False
    escaped = False
    index = 0
    while index < len(text):
        char = text[index]
        if in_string:
            out.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            index += 1
            continue
        if char == '"':
            in_string = True
            out.append(char)
            index += 1
            continue
        if char == "/" and text[index + 1 : index + 2] == "/":
            while index < len(text) and text[index] != "\n":
                index += 1
            continue
        out.append(char)
        index += 1
    return "".join(out)


def _harness_config() -> dict:
    """Return the parsed harness configuration."""
    return json.loads(
        _strip_jsonc_comments(HARNESS_CONFIG_PATH.read_text(encoding="utf-8"))
    )


def _glob_pattern(pattern: str) -> re.Pattern[str]:
    escaped: list[str] = []
    for char in pattern:
        if char == "*":
            escaped.append(".*")
        elif char == "?":
            escaped.append(".")
        else:
            escaped.append(re.escape(char))
    return re.compile("".join(escaped))


def _resource_matches(pattern: str, command: str) -> bool:
    """Return whether a shell resource pattern matches a command string.

    A shell resource is matched as a whole value against the raw command text,
    with `*` and `?` as wildcards, and a pattern ending in ` *` also matches
    the command without its arguments.
    """
    if _glob_pattern(pattern).fullmatch(command):
        return True
    if pattern.endswith(" *"):
        return _glob_pattern(pattern[:-2]).fullmatch(command)
    return False


def _effective_permission(config: dict, agent: str, command: str) -> str:
    """Return the effective effect of a shell command for an agent.

    Rules combine in order — the base policy, then the global rules, then the
    agent's own rules — and the last matching rule wins.
    """
    rules = list(BASE_PERMISSION_POLICY)
    rules.extend(config.get("permissions", []))
    rules.extend(config.get("agents", {}).get(agent, {}).get("permissions", []))
    effect = "ask"
    for rule in rules:
        if rule.get("action") not in ("shell", "*"):
            continue
        if _resource_matches(rule.get("resource", ""), command):
            effect = rule["effect"]
    return effect


def _mandatory_check_commands() -> list[str]:
    """Return the check commands the dependency warden's bindings declare."""
    content = (AGENT_SPECS_DIR / "warden.md").read_text(encoding="utf-8")
    project = _project_text(content)
    for line in project.splitlines():
        if line.startswith("**Mandatory check commands:**"):
            return re.findall(r"`([^`]+)`", line)
    return []


def test_mandatory_warden_checks_are_executable_under_effective_permissions() -> None:
    commands = _mandatory_check_commands()
    assert commands, "warden.md declares no mandatory check commands"
    config = _harness_config()
    for command in commands:
        effect = _effective_permission(config, "warden", command)
        assert effect == "allow", f"mandatory check {command!r} resolves to {effect!r}"


def test_dependency_permission_boundaries_are_enforced() -> None:
    config = _harness_config()

    allowed_for_forge = (
        "pnpm install --lockfile-only --ignore-scripts",
        "pnpm --dir cli/aicore test",
        "pnpm --dir cli/aicore test:e2e",
        "pnpm --dir cli/aicore typecheck",
        "pnpm --dir .opencode/plugins/odd-adviser exec vitest run",
        "pnpm --dir .opencode/plugins/odd-adviser typecheck",
        "pnpm --dir mcp-servers/system-one exec vitest run",
        "pnpm --dir mcp-servers/system-one typecheck",
        "pnpm --dir .agents/skills/odd-workflow exec vitest run",
        "pnpm --dir .agents/skills/odd-workflow typecheck",
    )
    for command in allowed_for_forge:
        effect = _effective_permission(config, "forge", command)
        assert effect == "allow", f"{command!r} resolves to {effect!r} for forge"

    denied_for_forge = (
        "pnpm install",
        "pnpm install --ignore-scripts",
        "pnpm install --lockfile-only",
        "pnpm --dir cli/aicore install",
        "pnpm i",
        "pnpm add yaml",
        "pnpm remove yaml",
        "pnpm update",
        "pnpm audit --fix",
    )
    for command in denied_for_forge:
        effect = _effective_permission(config, "forge", command)
        assert effect == "deny", f"{command!r} resolves to {effect!r} for forge"

    denied_for_warden = (
        "pnpm install",
        "pnpm --dir cli/aicore install",
        "uv sync",
        "uv add pyyaml",
        "npm install yaml",
    )
    for command in denied_for_warden:
        effect = _effective_permission(config, "warden", command)
        assert effect == "deny", f"{command!r} resolves to {effect!r} for warden"

    # The dependency warden's own advisory and maintenance commands stay usable.
    for command in ("pnpm audit --json", "pnpm outdated --json"):
        effect = _effective_permission(config, "warden", command)
        assert effect == "allow", f"{command!r} resolves to {effect!r} for warden"

    # The test architect's existing installation authority is untouched.
    effect = _effective_permission(config, "crucible", "pnpm install")
    assert effect == "allow", f"crucible 'pnpm install' resolves to {effect!r}"
