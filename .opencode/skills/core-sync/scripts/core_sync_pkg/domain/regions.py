"""Pure region parsing: split marked files, extract source cores, and rebuild files."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

from core_sync_pkg.domain.constants import (
    BEGIN,
    END,
    FRONTMATTER_DELIMITER,
    PROJECT_BEGIN,
    PROJECT_END,
)
from core_sync_pkg.domain.errors import MalformedSourceMarkers
from core_sync_pkg.domain.markers import (
    find_markers,
    has_exact_core_marker_lines,
    has_exact_project_marker_lines,
    line_without_terminator,
    unfenced_line_indices,
)


class RegionSplit(TypedDict):
    """A marked file split into the bytes before, inside, and after its region."""

    before: str
    begin_line: str
    region: str
    end_line: str
    after: str


def split_regions(content: str) -> RegionSplit | None:
    """Split content into the bytes around and inside its single core region."""
    markers = find_markers(content)
    if markers is None:
        return None
    begin_index, end_index = markers
    lines = content.splitlines(keepends=True)
    return {
        "before": "".join(lines[:begin_index]),
        "begin_line": lines[begin_index],
        "region": "".join(lines[begin_index + 1 : end_index]),
        "end_line": lines[end_index],
        "after": "".join(lines[end_index + 1 :]),
    }


def outside_bytes(region_split: RegionSplit) -> str:
    """Return the bytes that are not the core region, the markers included."""
    return (
        region_split["before"]
        + region_split["begin_line"]
        + region_split["end_line"]
        + region_split["after"]
    )


def split_frontmatter(content: str) -> tuple[str, str]:
    """Split leading YAML frontmatter from the body, preserving both verbatim.

    A delimiter is an exact `---` line with no leading or trailing whitespace,
    and a `---` line inside a fenced code block does not delimit. Returns
    `("", content)` when the content does not open with a `---` line or has no
    closing delimiter.
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
    post-frontmatter body; any malformed exact core marker set raises
    `MalformedSourceMarkers` instead of falling back to markerless behavior. A
    source carrying project markers without a valid core pair is malformed, so
    project content is never read as core.
    """
    region_split = split_regions(content)
    if region_split is not None:
        return region_split["region"]
    if has_exact_core_marker_lines(content) or has_exact_project_marker_lines(
        content
    ):
        raise MalformedSourceMarkers("source core markers are malformed")
    _, body = split_frontmatter(content)
    return body


def ensure_trailing_newline(text: str) -> str:
    """Return `text` with a trailing newline, adding one only when missing."""
    if not text or text.endswith("\n"):
        return text
    return text + "\n"


def render_with_region(destination: RegionSplit, source_region: str) -> str:
    """Rebuild a destination file with the source core region spliced in."""
    return (
        destination["before"]
        + destination["begin_line"]
        + source_region
        + destination["end_line"]
        + destination["after"]
    )


def render_init_file(destination_content: str, source_core: str) -> str:
    """Rebuild a markerless destination as a core region plus a project region.

    The destination frontmatter content is kept verbatim but always ends on its
    own line so the core begin marker stays an exact line; the source core fills
    the new core region; everything after the destination frontmatter is moved
    verbatim into the new project region.
    """
    frontmatter, body = split_frontmatter(destination_content)
    return (
        ensure_trailing_newline(frontmatter)
        + BEGIN
        + "\n"
        + ensure_trailing_newline(source_core)
        + END
        + "\n\n"
        + PROJECT_BEGIN
        + "\n"
        + ensure_trailing_newline(body)
        + PROJECT_END
        + "\n"
    )


def path_is_within(path: Path, root: Path) -> bool:
    """Return whether a resolved path is equal to or nested under a root.

    Public containment predicate for the write-target preflight. Both arguments
    are compared lexically, so callers resolve them first; symlinks are not
    followed here.
    """
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True
