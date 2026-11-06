"""Pure frontmatter refresh: merge a source's keys into a destination's.

Region mode rewrites a destination's frontmatter identity keys — the
`description` and `version` a catalog advertises — while every key the source
does not define keeps its original bytes, `local-version` included.
"""

from __future__ import annotations

from typing import TypedDict

import yaml

from core_sync_pkg.domain.constants import FRONTMATTER_DELIMITER
from core_sync_pkg.domain.markers import line_without_terminator

_METADATA_KEY = "metadata"
_MERGE_KEY = "<<"


class _Segment(TypedDict):
    """One raw frontmatter run: a key's lines, or a comment run with no key."""

    key: str | None
    text: str


class RefreshedText(TypedDict):
    """Text a refresh produced, and the reason part of it was left unrefreshed.

    An empty `skipped` means everything the source defines was applied. A
    non-empty value names what could not be merged, so a caller can surface it
    instead of reporting a silent no-op as success.
    """

    text: str
    skipped: str


class _Block(TypedDict):
    """A member's header line plus its raw child segments at one indent."""

    header: str
    indent: str
    segments: list[_Segment]
    trailing: str


class _Layout(TypedDict):
    """A parsed frontmatter and the raw lines each of its keys occupies."""

    opening: str
    segments: list[_Segment]
    trailing: str
    closing: str
    mapping: dict[str, object]


def refresh_frontmatter(
    frontmatter: str, source_frontmatter: str
) -> RefreshedText:
    """Return a destination frontmatter refreshed with the source's keys.

    Both arguments are leading frontmatter texts as `split_frontmatter`
    produced them, delimiters included. The merge is surgical: only the blocks
    the source defines are replaced or inserted, and their replacement text is
    the source frontmatter's own raw lines, so no value is ever written back
    through a parser. Every other destination line is copied through untouched,
    which is what keeps a destination scalar such as `version: 1.10` from being
    read as a float and rewritten as `1.1`.

    A key present in both sides takes the source value, a source-only key is
    appended in source order, and a destination-only key keeps its bytes. The
    same source-wins rule applies one level down inside `metadata`, whose
    children are replaced or inserted inside the destination's existing block so
    a destination-only child survives. Destination key order is preserved; the
    `---` delimiters are re-emitted and the bytes after the closing delimiter
    never pass through here.

    A missing, non-mapping, unparseable, or positionally unmappable frontmatter
    on either side returns `frontmatter` unchanged with the reason in `skipped`,
    so a destination that cannot be read is never rewritten and the caller can
    report why. The produced frontmatter is laid out again before it is returned;
    if that self-check fails, the input is returned unchanged with that reason.
    """
    if not frontmatter or not source_frontmatter:
        return {"text": frontmatter, "skipped": ""}
    destination, destination_reason = _layout(frontmatter)
    if destination is None:
        return {"text": frontmatter, "skipped": destination_reason}
    source, source_reason = _layout(source_frontmatter)
    if source is None:
        return {"text": frontmatter, "skipped": source_reason}
    merged, skipped = _merge_layouts(destination, source)
    if merged == frontmatter:
        return {"text": frontmatter, "skipped": skipped}
    checked, check_reason = _layout(merged)
    if checked is None:
        return {"text": frontmatter, "skipped": check_reason}
    return {"text": merged, "skipped": skipped}


def frontmatter_is_current(frontmatter: str, source_frontmatter: str) -> bool:
    """Return whether a destination frontmatter already says what a write emits.

    The one comparison the read paths use, so `check` and a write cannot
    disagree: it runs the same refresh rule and asks whether the destination
    would change. Terminators are normalized on both sides because the write
    path emits LF only, so a destination an earlier sync already wrote must not
    read as drifted just because the source document was checked out with CRLF;
    a frontmatter that differs in content still reads as drifted.
    """
    refreshed = refresh_frontmatter(frontmatter, source_frontmatter)["text"]
    return _lf(refreshed) == _lf(frontmatter)


def _layout(frontmatter: str) -> tuple[_Layout | None, str]:
    """Return a frontmatter's parsed keys and raw lines, or None and a reason."""
    lines = frontmatter.splitlines(keepends=True)
    if len(lines) < 2:
        return None, "frontmatter is not a `---` delimiter pair"
    if (
        line_without_terminator(lines[0]) != FRONTMATTER_DELIMITER
        or line_without_terminator(lines[-1]) != FRONTMATTER_DELIMITER
    ):
        return None, "frontmatter is not a `---` delimiter pair"
    body = lines[1:-1]
    mapping = _mapping("".join(body))
    if mapping is None:
        return None, "frontmatter is not a readable YAML mapping"
    segments = _segments(body, "", list(mapping))
    if segments is None:
        return None, "frontmatter keys cannot be mapped to their lines"
    return (
        {
            "opening": lines[0],
            "segments": segments[0],
            "trailing": segments[1],
            "closing": lines[-1],
            "mapping": mapping,
        },
        "",
    )


def _merge_layouts(destination: _Layout, source: _Layout) -> tuple[str, str]:
    """Return a destination frontmatter with the source's keys merged in."""
    source_texts = _texts_by_key(source["segments"])
    destination_keys = set(_texts_by_key(destination["segments"]))
    notes: list[str] = []
    parts = [destination["opening"]]
    for segment in destination["segments"]:
        key = segment["key"]
        if key is None or key not in source_texts:
            parts.append(segment["text"])
            continue
        replacement, skipped = _replacement(
            key,
            segment["text"],
            source_texts[key],
            destination["mapping"][key],
            source["mapping"][key],
        )
        if skipped:
            notes.append(skipped)
        parts.append(replacement)
    for segment in source["segments"]:
        key = segment["key"]
        if key is not None and key not in destination_keys:
            parts.append(segment["text"])
    parts.append(destination["trailing"])
    parts.append(destination["closing"])
    return "".join(parts), "; ".join(notes)


def _replacement(
    key: str,
    destination_text: str,
    source_text: str,
    destination_value: object,
    source_value: object,
) -> tuple[str, str]:
    """Return the text standing in for a destination key the source defines.

    Only `metadata` is merged instead of replaced, so a destination-only child
    survives; every other key takes the source's own raw lines. A destination
    block that cannot be matched child by child is kept as it is, with the
    reason it could not be merged.
    """
    if key == _METADATA_KEY:
        destination_children = _string_mapping(destination_value)
        source_children = _string_mapping(source_value)
        if destination_children is not None and source_children is not None:
            if not destination_children:
                return _choose(destination_text, source_text), ""
            merged, skipped = _merge_metadata_block(
                destination_text,
                source_text,
                destination_children,
                source_children,
            )
            return _choose(destination_text, merged), skipped
    return _choose(destination_text, source_text), ""


def _merge_metadata_block(
    destination_text: str,
    source_text: str,
    destination_children: dict[str, object],
    source_children: dict[str, object],
) -> tuple[str, str]:
    """Return a `metadata` block with the source's children merged in place.

    A destination child the source defines is replaced by the source's own raw
    lines, re-indented to the destination block's child indent; a
    destination-only child keeps its lines verbatim; source-only children are
    appended in source order. When either side cannot be matched, the
    destination block is returned unchanged with the reason.
    """
    destination_block, destination_reason = _block(
        destination_text, destination_children
    )
    if destination_block is None:
        return destination_text, f"destination {destination_reason}"
    source_block, source_reason = _block(source_text, source_children)
    if source_block is None:
        return destination_text, f"source {source_reason}"
    source_texts = _texts_by_key(source_block["segments"])
    destination_keys = set(_texts_by_key(destination_block["segments"]))
    parts = [destination_block["header"]]
    for segment in destination_block["segments"]:
        key = segment["key"]
        if key is None or key not in source_texts:
            parts.append(segment["text"])
            continue
        candidate = _reindent(
            source_texts[key],
            source_block["indent"],
            destination_block["indent"],
        )
        parts.append(_choose(segment["text"], candidate))
    for segment in source_block["segments"]:
        key = segment["key"]
        if key is not None and key not in destination_keys:
            parts.append(
                _reindent(
                    segment["text"],
                    source_block["indent"],
                    destination_block["indent"],
                )
            )
    parts.append(destination_block["trailing"])
    return "".join(parts), ""


def _block(
    text: str, children: dict[str, object]
) -> tuple[_Block | None, str]:
    """Return a member's raw child segments, or None and the reason."""
    lines = text.splitlines(keepends=True)
    if not lines:
        return None, "`metadata` has no lines"
    indent = _child_indent(lines[1:])
    if indent is None:
        return None, "`metadata` has no child lines"
    segments = _segments(lines[1:], indent, list(children))
    if segments is None:
        return None, "`metadata` child keys cannot be mapped to its lines"
    return (
        {
            "header": lines[0],
            "indent": indent,
            "segments": segments[0],
            "trailing": segments[1],
        },
        "",
    )


def _segments(
    lines: list[str], indent: str, keys: list[str]
) -> tuple[list[_Segment], str] | None:
    """Split lines into key blocks and verbatim comment runs at `indent`.

    A key's block runs from its key line to the line before the next key at the
    same indent, so continuation lines, nested values and blank lines stay with
    the key they belong to. A comment at exactly the member indent cannot sit
    inside any value, so it becomes its own verbatim segment and is never
    absorbed by a replaced key. Returns None when the number of key blocks does
    not match `keys`, because then no block can be matched to its parsed key and
    nothing may be rewritten. A YAML merge key is also unmappable: the parser
    expands it into the mapping and drops its own member, so a count can still
    agree while every later block is labelled one key too early.
    """
    segments: list[_Segment] = []
    separator: list[str] = []
    current: list[str] | None = None
    position = 0

    def close_member() -> None:
        nonlocal current
        if current is not None:
            segments.append({"key": keys[position - 1], "text": "".join(current)})
            current = None

    for line in lines:
        if _is_member_line(line, indent):
            close_member()
            if separator:
                segments.append({"key": None, "text": "".join(separator)})
                separator = []
            if position >= len(keys) or _declares_merge_key(line, indent):
                return None
            current = [line]
            position += 1
            continue
        if _is_comment_line(line, indent):
            close_member()
            separator.append(line)
            continue
        if current is None:
            separator.append(line)
        else:
            current.append(line)
    close_member()
    if position != len(keys):
        return None
    return segments, "".join(separator)


def _texts_by_key(segments: list[_Segment]) -> dict[str, str]:
    """Return each key's raw block text, ignoring the comment runs."""
    return {
        segment["key"]: segment["text"]
        for segment in segments
        if segment["key"] is not None
    }


def _is_member_line(line: str, indent: str) -> bool:
    """Return whether a line starts a key at exactly `indent`."""
    if not line.strip() or not line.startswith(indent):
        return False
    rest = line[len(indent) :]
    return not rest[:1].isspace() and not rest.startswith("#")


def _is_comment_line(line: str, indent: str) -> bool:
    """Return whether a line is a comment at exactly `indent`."""
    if not line.startswith(indent):
        return False
    return line[len(indent) :].startswith("#")


def _declares_merge_key(line: str, indent: str) -> bool:
    """Return whether a member line declares a YAML merge key.

    `yaml.safe_load` expands `<<: *anchor` into the surrounding mapping and drops
    the member itself, so a block list labelled positionally against the parsed
    keys would attach a source-defined key to the wrong destination line. Only
    the plain `<<` token merges; a quoted `"<<"` is an ordinary key and is left
    to the count check.
    """
    return line[len(indent) :].partition(":")[0].strip() == _MERGE_KEY


def _child_indent(lines: list[str]) -> str | None:
    """Return the indentation of a block's first non-blank child line."""
    for line in lines:
        if line.strip():
            return line[: len(line) - len(line.lstrip())]
    return None


def _reindent(text: str, source_indent: str, destination_indent: str) -> str:
    """Return a source block with its leading indent retargeted.

    Only leading indentation changes, so the block's quoting, spacing and scalar
    form are copied through exactly. Text that cannot be retargeted — a line
    less indented than its own block — is returned unchanged.
    """
    if source_indent == destination_indent:
        return text
    lines = text.splitlines(keepends=True)
    if not all(
        not line.strip() or line.startswith(source_indent) for line in lines
    ):
        return text
    return "".join(
        destination_indent + line[len(source_indent) :]
        if line.strip() and line.startswith(source_indent)
        else line
        for line in lines
    )


def _choose(destination_text: str, candidate: str) -> str:
    """Return `destination_text` when `candidate` already says the same thing.

    Terminators are compared normalized, so a destination written in LF is not
    rewritten just because the source block was read as CRLF; when the blocks
    match, the destination's own bytes are kept.
    """
    return (
        destination_text
        if _lf(candidate) == _lf(destination_text)
        else candidate
    )


def _lf(text: str) -> str:
    """Return `text` with CRLF and lone CR terminators normalized to LF."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _mapping(body: str) -> dict[str, object] | None:
    """Return a frontmatter body's top-level mapping, or None when unreadable."""
    if not body.strip():
        return {}
    try:
        data: object = yaml.safe_load(body)
    except yaml.YAMLError:
        return None
    return _string_mapping(data)


def _string_mapping(value: object) -> dict[str, object] | None:
    """Return `value` as a string-keyed mapping, or None when it is not one."""
    if not isinstance(value, dict):
        return None
    mapping: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            return None
        mapping[key] = item
    return mapping
