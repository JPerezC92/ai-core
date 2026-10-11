"""Integration contract for region-delimited AICore agent source surfaces."""

from __future__ import annotations

import re
from pathlib import Path

from _core_sync_testkit import uc


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

PROFILE_H2 = (
    "Personality",
    "Traits",
    "Role within the roster",
    "Collaboration Style",
)

CORE_ANCHORS = {
    "atrium.md": "DOMAIN LAYER",
    "forge.md": "Static Data Service Pattern",
    "ledger.md": "Close out now",
    "sentinel.md": "node_modules/",
    "vault.md": "Harness Parent Directories",
    "warden.md": "pnpm audit",
}

LOCAL_ONLY = {
    "crucible.md": (
        "The AICore project's narrow read-only discovery allowance includes "
        "`rg`, `ls`, `wc`, and read-only `git log`, `git show`, and `git diff` "
        "commands. These commands are not test execution, not a package install, "
        "and not a Git mutation.",
    ),
    "warden.md": (
        "In AICore, no scanner is configured in Warden's permitted command list; "
        "report it as unavailable and do not invoke direct `pip-audit`, `uvx`, "
        "or `uv tool run`.",
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

_CORE_DELIMITERS = {uc.BEGIN, uc.END}


def _surfaces() -> tuple[list[Path], list[Path]]:
    repo_root = Path(__file__).resolve().parents[4]
    return (
        sorted((repo_root / ".opencode/agents").glob("*.md")),
        sorted((repo_root / "agents").glob("*/profile.md")),
    )


def _unfenced_lines(text: str) -> list[str]:
    """Return lines outside fenced examples so example headings are not required."""
    active_fence: tuple[str, int] | None = None
    kept: list[str] = []
    for line in text.splitlines():
        raw = line.rstrip("\r\n")
        if active_fence is not None:
            fence_char, fence_length = active_fence
            if re.fullmatch(
                rf" {{0,3}}{re.escape(fence_char)}{{{fence_length},}}[ \t]*",
                raw,
            ):
                active_fence = None
            continue
        opening = uc.FENCE_OPEN_RE.match(line)
        if opening is not None:
            fence = opening.group(1)
            info = opening.group(2)
            if fence[0] != "`" or "`" not in info:
                active_fence = (fence[0], len(fence))
                continue
        kept.append(line)
    return kept


def _project_text(content: str) -> str:
    lines = content.splitlines()
    begins = uc._exact_marker_line_indices(lines, uc.PROJECT_BEGIN)
    ends = uc._exact_marker_line_indices(lines, uc.PROJECT_END)
    assert len(begins) == 1 and len(ends) == 1
    return "\n".join(lines[begins[0] + 1 : ends[0]])


def test_agent_sources_place_core_markers_after_frontmatter() -> None:
    spec_paths, profile_paths = _surfaces()
    assert len(spec_paths) == 16
    assert len(profile_paths) == 17

    for path in [*spec_paths, *profile_paths]:
        content = path.read_text(encoding="utf-8")
        frontmatter, body = uc.split_frontmatter(content)
        core_markers = uc.find_markers(content)
        assert frontmatter, path
        frontmatter_lines = frontmatter.splitlines()
        assert frontmatter_lines[0].strip() == "---", path
        assert frontmatter_lines[-1].strip() == "---", path
        assert core_markers is not None, path
        assert body.startswith(f"{uc.BEGIN}\n"), path
        assert core_markers[0] == len(frontmatter.splitlines()), path
        core = uc.extract_source_core(content)
        assert core.strip(), path
        assert not any(
            line.strip() in _CORE_DELIMITERS for line in _unfenced_lines(core)
        ), path


def test_agent_spec_cores_keep_h3_order() -> None:
    spec_paths, _profile_paths = _surfaces()
    for path in spec_paths:
        core = uc.extract_source_core(path.read_text(encoding="utf-8"))
        headings = [
            line.strip()[4:]
            for line in _unfenced_lines(core)
            if line.strip() in {f"### {heading}" for heading in SPEC_H3}
        ]
        assert headings == list(SPEC_H3), path


def test_agent_spec_cores_keep_positive_anchors() -> None:
    spec_paths, _profile_paths = _surfaces()
    for path in spec_paths:
        anchor = CORE_ANCHORS.get(path.name)
        if anchor is None:
            continue
        core = uc.extract_source_core(path.read_text(encoding="utf-8"))
        assert anchor in core, path


def test_agent_sources_keep_local_facts_out_of_core() -> None:
    repo_root = Path(__file__).resolve().parents[4]
    for name, facts in LOCAL_ONLY.items():
        content = (repo_root / ".opencode/agents" / name).read_text(encoding="utf-8")
        core = uc.extract_source_core(content)
        project = _project_text(content)
        for fact in facts:
            assert fact not in core, name
            assert fact in project, name


def test_agent_profiles_keep_heading_order() -> None:
    _spec_paths, profile_paths = _surfaces()
    for path in profile_paths:
        core = uc.extract_source_core(path.read_text(encoding="utf-8"))
        positions = [core.find(f"## {heading}") for heading in PROFILE_H2]
        assert all(index >= 0 for index in positions), path
        assert positions == sorted(positions), path
        assert len(re.findall(r"^## What .+ Does NOT Do$", core, re.MULTILINE)) == 1, path


def test_agent_sources_keep_optional_project_region_shape() -> None:
    spec_paths, profile_paths = _surfaces()
    for path in [*spec_paths, *profile_paths]:
        lines = path.read_text(encoding="utf-8").splitlines()
        begins = uc._exact_marker_line_indices(lines, uc.PROJECT_BEGIN)
        ends = uc._exact_marker_line_indices(lines, uc.PROJECT_END)
        assert len(begins) == len(ends) <= 1, path
        if begins:
            assert begins[0] > 0 and lines[begins[0] - 1].strip() == "", path
            assert lines[-1].strip() == uc.PROJECT_END, path
        else:
            assert lines[-1].strip() == uc.END, path
