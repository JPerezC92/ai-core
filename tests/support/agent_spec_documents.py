"""Structure of the agent runtime specs, read for the repository contract tests.

The Python synchronization engine that used to own this parsing was removed
together with the engine, so the helpers live here as a shared test resource:
they observe a document's own structure and never re-implement an engine
operation. The rules are the ones the runtime specs are written against — a
marker counts only as an exact line outside a fenced code block, a leading
`---` pair delimits the frontmatter, and the core region is the text between
the core markers.
"""

from __future__ import annotations

import re
from pathlib import Path

CORE_BEGIN = "<!-- core:begin -->"
CORE_END = "<!-- core:end -->"
PROJECT_BEGIN = "<!-- project:begin -->"
PROJECT_END = "<!-- project:end -->"
FRONTMATTER_DELIMITER = "---"

FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENT_SPECS_DIR = REPO_ROOT / ".opencode" / "agents"


class MalformedSourceMarkers(ValueError):
    """Raised when a document claims marked regions it does not carry."""


def line_without_terminator(line: str) -> str:
    """Return `line` with only its trailing CR/LF terminator removed."""
    return line.rstrip("\r\n")


def unfenced_line_indices(lines: list[str]) -> list[int]:
    """Return the indices of lines that are outside any Markdown code fence.

    A fence opens with at least three matching backticks or tildes and closes
    with that character repeated at least as many times, with at most three
    leading spaces and nothing but horizontal whitespace after it. A backtick
    fence whose info string contains a backtick does not open a fence. Fence
    delimiter lines themselves are not returned.
    """
    active_fence: tuple[str, int] | None = None
    indices: list[int] = []
    for index, line in enumerate(lines):
        text = line_without_terminator(line)
        if active_fence is not None:
            fence_char, fence_length = active_fence
            closing_pattern = (
                rf" {{0,3}}{re.escape(fence_char)}{{{fence_length},}}[ \t]*"
            )
            if re.fullmatch(closing_pattern, text):
                active_fence = None
            continue

        opening = FENCE_OPEN_RE.match(line)
        if opening is not None:
            fence = opening.group(1)
            info = opening.group(2)
            if fence[0] != "`" or "`" not in info:
                active_fence = (fence[0], len(fence))
                continue

        indices.append(index)
    return indices


def unfenced_lines(text: str) -> list[str]:
    """Return the lines of `text` that sit outside any fenced code block."""
    lines = text.splitlines()
    return [lines[index] for index in unfenced_line_indices(lines)]


def exact_marker_line_indices(lines: list[str], marker: str) -> list[int]:
    """Return the indices of exact stripped `marker` lines outside code fences."""
    return [
        index
        for index in unfenced_line_indices(lines)
        if line_without_terminator(lines[index]).strip() == marker
    ]


def find_core_markers(content: str) -> tuple[int, int] | None:
    """Return the (begin, end) line indices of the single valid core marker pair.

    Returns `None` when the core markers are missing, duplicated or reversed.
    """
    lines = content.splitlines()
    begins = exact_marker_line_indices(lines, CORE_BEGIN)
    ends = exact_marker_line_indices(lines, CORE_END)
    if len(begins) != 1 or len(ends) != 1:
        return None
    if begins[0] > ends[0]:
        return None
    return (begins[0], ends[0])


def split_frontmatter(content: str) -> tuple[str, str]:
    """Split leading YAML frontmatter from the body, preserving both verbatim.

    A delimiter is an exact `---` line, and a `---` line inside a fenced code
    block does not delimit. Returns `("", content)` when the content does not
    open with a `---` line or has no closing delimiter.
    """
    lines = content.splitlines(keepends=True)
    if not lines or line_without_terminator(lines[0]) != FRONTMATTER_DELIMITER:
        return ("", content)
    for index in unfenced_line_indices(lines):
        if index == 0:
            continue
        if line_without_terminator(lines[index]) == FRONTMATTER_DELIMITER:
            return ("".join(lines[: index + 1]), "".join(lines[index + 1 :]))
    return ("", content)


def extract_source_core(content: str) -> str:
    """Return a source file's core bytes.

    A valid marker pair yields its region. A markerless source uses its whole
    post-frontmatter body; a source carrying exact core or project marker lines
    without a valid core pair is malformed, so its project content is never
    read as core.
    """
    markers = find_core_markers(content)
    if markers is not None:
        begin_index, end_index = markers
        lines = content.splitlines(keepends=True)
        return "".join(lines[begin_index + 1 : end_index])
    if _has_exact_marker_lines(content, CORE_BEGIN, CORE_END) or (
        _has_exact_marker_lines(content, PROJECT_BEGIN, PROJECT_END)
    ):
        raise MalformedSourceMarkers("source core markers are malformed")
    _, body = split_frontmatter(content)
    return body


def _has_exact_marker_lines(content: str, begin: str, end: str) -> bool:
    """Return whether either exact marker occurs outside a code fence."""
    lines = content.splitlines()
    return bool(
        exact_marker_line_indices(lines, begin)
        or exact_marker_line_indices(lines, end)
    )
