"""Pure marker parsing: exact marker lines, code-fence awareness, and safe path checks."""

from __future__ import annotations

import re
from pathlib import PureWindowsPath

from core_sync_pkg.domain.constants import (
    BEGIN,
    END,
    FENCE_OPEN_RE,
    PROJECT_BEGIN,
    PROJECT_END,
)


def _is_safe_relative(path: str) -> bool:
    """Return True when a bindings path is a canonical safe relative POSIX path."""
    if not path or "\x00" in path or "\\" in path:
        return False
    if any(part in ("", ".", "..") for part in path.split("/")):
        return False
    windows_path = PureWindowsPath(path)
    return not windows_path.drive and not windows_path.root


def line_without_terminator(line: str) -> str:
    """Return `line` with only its trailing CR/LF terminator removed.

    No other whitespace is trimmed, so a padded line is not treated as its
    unpadded counterpart.
    """
    return line.rstrip("\r\n")


def unfenced_line_indices(lines: list[str]) -> list[int]:
    """Return the indices of lines that are outside any Markdown code fence.

    Fences use at least three matching backticks or tildes. A closer must use
    the opening character at least as many times, have at most three leading
    spaces, and contain no trailing content beyond horizontal whitespace. A
    backtick fence whose info string contains a backtick does not open a fence.
    Fence delimiter lines themselves are not returned.
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


def _exact_marker_line_indices(lines: list[str], marker: str) -> list[int]:
    """Return the indices of exact stripped `marker` lines outside code fences.

    Marker-looking lines inside a fence are skipped; see `unfenced_line_indices`
    for the fence rule.
    """
    return [
        index
        for index in unfenced_line_indices(lines)
        if line_without_terminator(lines[index]).strip() == marker
    ]


def find_markers(content: str) -> tuple[int, int] | None:
    """Return the (begin, end) line indices of the single valid marker pair.

    A marker counts only as an exact stripped line outside a fenced code block.
    Returns None when the BEGIN/END markers are missing, duplicated, or reversed.
    """
    lines = content.splitlines()
    begins = _exact_marker_line_indices(lines, BEGIN)
    ends = _exact_marker_line_indices(lines, END)
    if len(begins) != 1 or len(ends) != 1:
        return None
    if begins[0] > ends[0]:
        return None
    return (begins[0], ends[0])


def has_exact_core_marker_lines(content: str) -> bool:
    """Return whether either exact core marker occurs outside a code fence."""
    lines = content.splitlines()
    return bool(
        _exact_marker_line_indices(lines, BEGIN)
        or _exact_marker_line_indices(lines, END)
    )


def has_exact_project_marker_lines(content: str) -> bool:
    """Return whether either exact project marker occurs outside a code fence."""
    lines = content.splitlines()
    return bool(
        _exact_marker_line_indices(lines, PROJECT_BEGIN)
        or _exact_marker_line_indices(lines, PROJECT_END)
    )
