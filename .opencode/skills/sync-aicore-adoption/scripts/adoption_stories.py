"""Pure portable story-index merge transformations."""

from __future__ import annotations

from typing import Mapping, Sequence

from adoption_constants import COLLISION_POLICIES
from adoption_contracts import StoryMergeMember, _field, _need

def _line_content(line: bytes) -> bytes:
    """Return one line's bytes without its trailing line ending."""
    return line.rstrip(b"\r\n")


def _line_ending(line: bytes) -> bytes:
    """Return the trailing line-ending bytes of one line (possibly empty)."""
    return line[len(_line_content(line)):]


def _is_story_separator(line: bytes) -> bool:
    """Return whether a table line is the markdown separator row (``|---|``)."""
    content = _line_content(line).strip()
    return (
        content.startswith(b"|")
        and b"-" in content
        and not (set(content) - set(b"|-: \t"))
    )


def _story_row_slug(line: bytes) -> str | None:
    """Return a table row's first cell as its slug key, or ``None`` when unkeyed."""
    content = _line_content(line)
    if not content.startswith(b"|"):
        return None
    cells = content.split(b"|")
    if len(cells) < 3:
        return None
    first = cells[1].strip()
    if len(first) >= 3 and first.startswith(b"`") and first.endswith(b"`"):
        first = first[1:-1]
    if not first:
        return None
    try:
        return first.decode("utf-8")
    except UnicodeDecodeError:
        return None


def _story_table_block(lines: Sequence[bytes]) -> tuple[int, int] | None:
    """Return the ``[start, end)`` line span of the first markdown table."""
    start: int | None = None
    end = 0
    for index, line in enumerate(lines):
        if _line_content(line).startswith(b"|"):
            if start is None:
                start = index
            end = index + 1
        elif start is not None:
            break
    if start is None:
        return None
    return start, end


def _keyed_story_rows(lines: Sequence[bytes]) -> dict[str, bytes]:
    """Map each data-row slug of the first table to its content (no ending)."""
    rows: dict[str, bytes] = {}
    block = _story_table_block(lines)
    if block is None:
        return rows
    start, end = block
    for index in range(start + 1, end):
        if _is_story_separator(lines[index]):
            continue
        slug = _story_row_slug(lines[index])
        if slug is not None and slug not in rows:
            rows[slug] = _line_content(lines[index])
    return rows


def _seed_story_index(core_lines: Sequence[bytes], slugs: Sequence[str]) -> bytes:
    """Build a fresh destination index: the core document minus non-member rows."""
    wanted = set(slugs)
    block = _story_table_block(core_lines)
    if block is None:
        return b"".join(core_lines)
    start, end = block
    kept: list[bytes] = []
    for index, line in enumerate(core_lines):
        if start <= index < end and index != start and not _is_story_separator(line):
            slug = _story_row_slug(line)
            if slug is not None and slug not in wanted:
                continue
        kept.append(line)
    return b"".join(kept)


def _append_core_story_table(
    destination_index: bytes,
    core_lines: Sequence[bytes],
    core_rows: Mapping[str, bytes],
    members: Sequence[tuple[str, str, object]],
) -> bytes:
    """Append the applicable core table block after a destination without a table."""
    block = _story_table_block(core_lines)
    if block is None:
        return destination_index
    start, end = block
    header = core_lines[start]
    ending = _line_ending(header) or b"\n"
    table_lines = [header]
    for index in range(start + 1, end):
        if _is_story_separator(core_lines[index]):
            table_lines.append(core_lines[index])
            break
    table_lines.extend(
        core_rows[slug] + ending for slug, _destination, _policy in members
    )
    out = destination_index
    if out and not out.endswith(b"\n"):
        out += b"\n"
    if out and not out.endswith(b"\n\n"):
        out += b"\n"
    return out + b"".join(table_lines)


def _merge_story_rows(
    destination_index: bytes,
    core_lines: Sequence[bytes],
    core_rows: Mapping[str, bytes],
    members: Sequence[tuple[str, str, object]],
) -> tuple[bytes, list[str]]:
    """Merge core rows into an existing destination table, reporting collisions."""
    lines = destination_index.splitlines(keepends=True)
    block = _story_table_block(lines)
    if block is None:
        return (
            _append_core_story_table(destination_index, core_lines, core_rows, members),
            [],
        )
    start, end = block
    table_ending = _line_ending(lines[start]) or b"\n"
    row_index: dict[str, int] = {}
    for index in range(start + 1, end):
        if _is_story_separator(lines[index]):
            continue
        slug = _story_row_slug(lines[index])
        if slug is not None and slug not in row_index:
            row_index[slug] = index
    collisions: list[str] = []
    missing: list[str] = []
    for slug, destination, policy in members:
        index = row_index.get(slug)
        if index is None:
            missing.append(slug)
            continue
        core_row = core_rows[slug]
        if _line_content(lines[index]) == core_row:
            continue
        if policy not in COLLISION_POLICIES:
            continue
        lines[index] = core_row + _line_ending(lines[index])
        collisions.append(f"collision: path {destination}; core wins")
        collisions.append(f"collision: slug {slug}; core wins")
    if missing:
        if not lines[end - 1].endswith((b"\n", b"\r")):
            lines[end - 1] = lines[end - 1] + table_ending
        lines[end:end] = [core_rows[slug] + table_ending for slug in missing]
    return b"".join(lines), collisions


def merge_story_index(
    core_index: bytes,
    destination_index: bytes | None,
    members: Sequence[StoryMergeMember],
) -> tuple[bytes, list[str]]:
    """Pure story-index merge (bytes in, bytes out, no file IO).

    Seeds a fresh destination with only the applicable core rows; for an
    existing index inserts missing core rows and replaces differing rows
    inside the existing table. Destination-only rows, rows of members
    without ``collision_policy: core_wins``, and every byte before and
    after the table are preserved byte-for-byte (line endings included).
    Returns the merged bytes plus one ``collision: path <destination>;
    core wins`` and one ``collision: slug <slug>; core wins`` string per
    differing ``core_wins`` member; identical rows report nothing.
    """
    parsed: list[tuple[str, str, object]] = []
    for index, member in enumerate(members):
        slug = _field(member, "id")
        destination = _field(member, "destination")
        _need(
            isinstance(slug, str) and bool(slug),
            "invalid_mapping",
            f"members[{index}].id must be a non-empty string",
        )
        _need(
            isinstance(destination, str) and bool(destination),
            "invalid_mapping",
            f"members[{index}].destination must be a non-empty string",
        )
        policy = _field(member, "collision_policy")
        _need(
            policy is None or policy in COLLISION_POLICIES,
            "invalid_mapping",
            f"members[{index}].collision_policy must be one of {COLLISION_POLICIES}",
        )
        parsed.append((str(slug), str(destination), policy))
    core_lines = core_index.splitlines(keepends=True)
    core_rows = _keyed_story_rows(core_lines)
    for slug, _destination, _policy in parsed:
        _need(
            slug in core_rows,
            "invalid_mapping",
            f"core story index has no row for member {slug!r}",
        )
    if destination_index is None or destination_index == b"":
        return _seed_story_index(core_lines, [slug for slug, _, _ in parsed]), []
    return _merge_story_rows(destination_index, core_lines, core_rows, parsed)

