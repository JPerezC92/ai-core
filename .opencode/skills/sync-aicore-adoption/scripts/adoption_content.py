"""Content digest reading, two-section layout extraction, and comparison helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping

import yaml
from yaml.tokens import ScalarToken

from adoption_constants import (
    RULE_LAYOUT_EXTENSIONS_HEADING,
    RULE_LAYOUT_MANDATORY_HEADING,
    RULE_LAYOUT_MARKER,
    STORY_INDEX_NAME,
)
from adoption_contracts import StoryMergeMember, _Snapshot, _content_projection, _fail, _field, _need, _normalize_destination, _normalize_source_path, _strip_comments
from adoption_digests import assertion_list_digest, assertion_status_digest, member_digest, unit_digest
from adoption_git import _GitRepo
from adoption_mapping import _declared_members, _rule_document_destination
from adoption_stories import merge_story_index


_FRAMING_METADATA = re.compile(
    r"^> \*\*(Spec version|Local version|Project identity|Rule layout):\*\*\s+"
    r"\S",
)
_H2_HEADING = re.compile(r"^ {0,3}##(?:[ \t]|$)")
_ATX_HEADING = re.compile(r"^ {0,3}#{1,6}(?:[ \t]|$)")
_SETEXT_DASH = re.compile(r"^ {0,3}-+[ \t]*$")
_SETEXT_EQUALS = re.compile(r"^ {0,3}=+[ \t]*$")
_THEMATIC_BREAK = re.compile(
    r"^ {0,3}(?:(?:-[ \t]*){3,}|(?:_[ \t]*){3,}|(?:\*[ \t]*){3,})$"
)
_CONTAINER_PREFIX = re.compile(
    r"^ {0,3}(?:>|[-+*][ \t]|[0-9]{1,9}[.)][ \t])"
)
_HTML_BLOCK = re.compile(r"^ {0,3}<(?:[!?]|/?[A-Za-z])")
_TABLE_DELIMITER_CELL = re.compile(r"^:?-{3,}:?$")
_UNSUPPORTED_SEPARATORS = frozenset("\u000b\u000c\u001c\u001d\u001e\u0085\u2028\u2029")
_YAML_FORBIDDEN_CONTROLS = frozenset("\u000b\u000c\u001c\u001d\u001e")
_MISSING_FRONTMATTER_CLOSE = (
    "operational prose outside ownership sections: "
    "missing bounded YAML frontmatter close"
)
_FRONTMATTER_HEADING = (
    "operational prose outside ownership sections: "
    "frontmatter close must precede ownership headings"
)
_UNSUPPORTED_CONTEXT = "orphan region: unsupported Markdown block context"
_ORPHAN_HEADING_COUNT = "orphan region: expected exactly two ownership headings"


def _fence_body(content: str) -> str | None:
    """Return the text after a 0–3 space indent, or None when not fence-eligible.

    Four or more spaces are indented code. A leading tab is not a 0–3 space
    indent, so neither form can open or close a fence.
    """
    indent = 0
    while indent < len(content) and content[indent] == " ":
        indent += 1
    if indent > 3 or (indent < len(content) and content[indent] == "\t"):
        return None
    return content[indent:]


def _fence_run(text: str) -> tuple[str, int] | None:
    """Return a leading backtick or tilde run of at least three, or None."""
    if not text or text[0] not in "`~":
        return None
    char = text[0]
    run = 0
    while run < len(text) and text[run] == char:
        run += 1
    if run < 3:
        return None
    return char, run


def _opening_fence(content: str) -> tuple[str, int] | None:
    """Return a valid opening fence, rejecting backtick info strings with backticks."""
    rest = _fence_body(content)
    if rest is None:
        return None
    parsed = _fence_run(rest)
    if parsed is None:
        return None
    char, length = parsed
    if char == "`" and "`" in rest[length:]:
        return None
    return char, length


def _closing_fence(content: str, fence_char: str, fence_len: int) -> bool:
    """Return whether the line is a valid closer for the open fence."""
    rest = _fence_body(content)
    if rest is None:
        return False
    parsed = _fence_run(rest)
    if parsed is None or parsed[0] != fence_char or parsed[1] < fence_len:
        return False
    return rest[parsed[1]:].strip(" \t") == ""


def _frontmatter_mapping_violation(interior: str) -> str | None:
    """Reject leading frontmatter that is not a safe YAML mapping.

    Comments, nested metadata, and block scalars are syntax. The loader does
    not interpret prose meaning. Malformed scalars and unsafe tags fail closed.
    Raw YAML-forbidden controls stay illegal even inside quotes.
    """
    if any(char in _YAML_FORBIDDEN_CONTROLS for char in interior):
        return (
            "operational prose outside ownership sections: "
            "invalid YAML framing: forbidden raw control character"
        )
    try:
        parsed = yaml.safe_load(interior)
    except yaml.YAMLError as exc:
        return (
            "operational prose outside ownership sections: "
            f"invalid YAML framing: {exc}"
        )
    if not isinstance(parsed, dict):
        return (
            "operational prose outside ownership sections: "
            "frontmatter must be a YAML mapping"
        )
    return None


def _scalar_spans(interior: str) -> list[tuple[int, int]] | None:
    """Return quoted and block scalar source spans, or None when scanning fails."""
    try:
        tokens = list(yaml.scan(interior))
    except yaml.YAMLError:
        return None
    return [
        (token.start_mark.index, token.end_mark.index)
        for token in tokens
        if isinstance(token, ScalarToken)
    ]


def _heading_outside_scalar(interior: str) -> bool:
    """Return whether an ownership-looking H2 sits outside scalar token spans."""
    spans = _scalar_spans(interior)
    if spans is None:
        return True
    for line in _physical_lines(interior):
        match = _H2_HEADING.match(line.content)
        if match is None:
            continue
        marker = line.start + line.content.find("##")
        if not any(start <= marker < end for start, end in spans):
            return True
    return False


@dataclass(frozen=True)
class _PhysicalLine:
    """One LF, CRLF, or CR record with its original offsets."""

    start: int
    end: int
    content: str
    has_unsupported: bool


def _physical_lines(text: str) -> list[_PhysicalLine]:
    """Split on LF, CRLF, and CR only, preserving unsupported separators."""
    lines: list[_PhysicalLine] = []
    start = 0
    index = 0
    length = len(text)
    while index < length:
        char = text[index]
        if char != "\n" and char != "\r":
            index += 1
            continue
        terminator = 2 if char == "\r" and index + 1 < length and text[index + 1] == "\n" else 1
        content = text[start:index]
        lines.append(
            _PhysicalLine(
                start,
                index + terminator,
                content,
                any(item in _UNSUPPORTED_SEPARATORS for item in content),
            )
        )
        index += terminator
        start = index
    if start < length:
        content = text[start:]
        lines.append(
            _PhysicalLine(
                start,
                length,
                content,
                any(item in _UNSUPPORTED_SEPARATORS for item in content),
            )
        )
    return lines


def _is_blank(content: str) -> bool:
    """Return whether the line contains only spaces or tabs."""
    return content.strip(" \t") == ""


def _is_indented_code(content: str) -> bool:
    """Return whether the line is four-space or tab indented code."""
    return content.startswith("    ") or content.startswith("\t")


def _is_framing_metadata(content: str) -> bool:
    """Return whether the line is allowed technical framing, not prose."""
    return (
        content == RULE_LAYOUT_MARKER
        or content.startswith("# ")
        or _FRAMING_METADATA.match(content) is not None
        or content.startswith("**Persona / personality:**")
    )


def _pipe_cells(content: str) -> list[str] | None:
    """Return trimmed cells of a leading-and-trailing pipe row, or None."""
    stripped = content.strip(" \t")
    if len(stripped) < 2 or not stripped.startswith("|") or not stripped.endswith("|"):
        return None
    return [cell.strip(" \t") for cell in stripped[1:-1].split("|")]


def _is_delimiter_row(content: str, count: int) -> bool:
    """Return whether the line is a matching supported table delimiter row."""
    cells = _pipe_cells(content)
    if cells is None or len(cells) != count or not cells:
        return False
    return all(_TABLE_DELIMITER_CELL.fullmatch(cell) is not None for cell in cells)


def _continuation_affects_heading(content: str, following: str | None) -> bool:
    """Return whether a lazy continuation changes a heading, setext, or fence."""
    if (
        _SETEXT_DASH.match(content) is not None
        or _SETEXT_EQUALS.match(content) is not None
        or _ATX_HEADING.match(content) is not None
        or _opening_fence(content) is not None
    ):
        return True
    if following is None:
        return False
    return (
        _SETEXT_DASH.match(following) is not None
        or _SETEXT_EQUALS.match(following) is not None
        or _ATX_HEADING.match(following) is not None
        or _opening_fence(following) is not None
    )


@dataclass(frozen=True)
class _Heading:
    """One counted H2 and the exact text used for the canonical spelling check."""

    offset: int
    text: str


@dataclass(frozen=True)
class _MarkdownScan:
    """Marker, heading, and fence state after the validated frontmatter block."""

    markers: tuple[int, ...]
    headings: tuple[_Heading, ...]
    fenced_starts: frozenset[int]
    unsupported: bool


def _scan_markdown(lines: list[_PhysicalLine]) -> _MarkdownScan:
    """Scan Markdown after frontmatter. Only a valid closer exits a fence."""
    markers: list[int] = []
    headings: list[_Heading] = []
    fenced: set[int] = set()
    in_fence = False
    fence_char = ""
    fence_len = 0
    paragraph_active = False
    paragraph_offset = 0
    paragraph_text = ""
    in_container = False
    in_table = False
    unsupported = False
    index = 0
    while index < len(lines):
        line = lines[index]
        content = line.content
        following = lines[index + 1].content if index + 1 < len(lines) else None
        if in_fence:
            fenced.add(line.start)
            if _closing_fence(content, fence_char, fence_len):
                in_fence = False
            index += 1
            continue
        if line.has_unsupported or _HTML_BLOCK.match(content) is not None:
            unsupported = True
            break
        if _is_blank(content):
            paragraph_active = False
            in_container = False
            in_table = False
            index += 1
            continue
        if _is_framing_metadata(content):
            if content == RULE_LAYOUT_MARKER:
                markers.append(line.start)
            paragraph_active = False
            in_container = False
            in_table = False
            index += 1
            continue
        if _ATX_HEADING.match(content) is not None:
            if _H2_HEADING.match(content) is not None:
                headings.append(_Heading(line.start, content))
            paragraph_active = False
            in_container = False
            in_table = False
            index += 1
            continue
        opener = _opening_fence(content)
        if opener is not None:
            in_fence = True
            fence_char, fence_len = opener
            fenced.add(line.start)
            paragraph_active = False
            in_container = False
            in_table = False
            index += 1
            continue
        if in_table:
            if _pipe_cells(content) is None:
                in_table = False
                continue
            paragraph_active = False
            index += 1
            continue
        if (
            _THEMATIC_BREAK.match(content) is not None
            and not (paragraph_active and _SETEXT_DASH.match(content) is not None)
        ):
            paragraph_active = False
            in_container = False
            in_table = False
            index += 1
            continue
        if in_container and _CONTAINER_PREFIX.match(content) is None:
            if _continuation_affects_heading(content, following):
                unsupported = True
                break
            index += 1
            continue
        if paragraph_active and _SETEXT_DASH.match(content) is not None:
            headings.append(_Heading(paragraph_offset, paragraph_text))
            paragraph_active = False
            index += 1
            continue
        if _CONTAINER_PREFIX.match(content) is not None:
            paragraph_active = False
            in_container = True
            in_table = False
            index += 1
            continue
        header_cells = _pipe_cells(content)
        if (
            header_cells is not None
            and following is not None
            and _is_delimiter_row(following, len(header_cells))
        ):
            in_table = True
            paragraph_active = False
            in_container = False
            index += 2
            continue
        if _is_indented_code(content):
            if (
                paragraph_active
                and following is not None
                and _SETEXT_DASH.match(following) is not None
            ):
                unsupported = True
                break
            paragraph_active = False
            in_container = False
            in_table = False
            index += 1
            continue
        if paragraph_active and _SETEXT_DASH.match(content) is not None:
            headings.append(_Heading(paragraph_offset, paragraph_text))
            paragraph_active = False
            index += 1
            continue
        if paragraph_active and _SETEXT_EQUALS.match(content) is not None:
            paragraph_active = False
            index += 1
            continue
        if not paragraph_active:
            paragraph_offset = line.start
            paragraph_text = content
            paragraph_active = True
        index += 1
    return _MarkdownScan(
        tuple(markers),
        tuple(headings),
        frozenset(fenced),
        unsupported,
    )


@dataclass(frozen=True)
class RuleLayout:
    """One protected document's exact two-section byte regions.

    ``mandatory`` spans the ``## Mandatory core`` heading line through end of
    document; ``extensions`` spans the ``## Project extensions`` heading line up
    to (but not including) the mandatory heading; ``framing`` is everything
    before the extensions heading.
    """

    framing: bytes
    extensions: bytes
    mandatory: bytes


def _validated_frontmatter_end(text: str, lines: list[_PhysicalLine]) -> tuple[int, str | None]:
    """Recognize a leading YAML block before any Markdown scan.

    The first exact column-zero ``---`` closes the block. There is no
    fence-aware retry. The returned offset is the first Markdown character.
    """
    if not lines or lines[0].content != "---":
        return 0, None
    close = next((line for line in lines[1:] if line.content == "---"), None)
    if close is None:
        return 0, _MISSING_FRONTMATTER_CLOSE
    interior = text[lines[0].end:close.start]
    violation = _frontmatter_mapping_violation(interior)
    if violation is not None:
        return 0, violation
    if _heading_outside_scalar(interior):
        return 0, _FRONTMATTER_HEADING
    return close.end, None


def _scan_rule_layout(text: str) -> tuple[RuleLayout | None, str | None]:
    """Extract the two-section layout after YAML, then bounded Markdown.

    Returns ``(layout, None)`` when the document satisfies the contract, or
    ``(None, reason)`` otherwise. Only a valid fence closer exits a fence.
    Partitions are original UTF-8 slices and concatenate to the source bytes.
    """
    lines = _physical_lines(text)
    frontmatter_end, frontmatter_violation = _validated_frontmatter_end(text, lines)
    if frontmatter_violation is not None:
        return None, frontmatter_violation
    markdown = [line for line in lines if line.start >= frontmatter_end]
    scanned = _scan_markdown(markdown)
    if len(scanned.markers) > 1:
        return None, "duplicate standalone two-section layout marker"
    if scanned.unsupported:
        return None, _UNSUPPORTED_CONTEXT
    if not scanned.markers:
        return None, "missing standalone two-section layout marker"
    if len(scanned.headings) != 2:
        return None, _ORPHAN_HEADING_COUNT
    extensions, mandatory = scanned.headings
    if extensions.text != RULE_LAYOUT_EXTENSIONS_HEADING:
        return None, "first ownership heading must be '## Project extensions'"
    if mandatory.text != RULE_LAYOUT_MANDATORY_HEADING:
        return None, "second ownership heading must be '## Mandatory core'"
    if scanned.markers[0] > extensions.offset:
        return None, "standalone layout marker must precede the first ownership heading"
    framing_violation = _framing_violation(
        lines, extensions.offset, frontmatter_end, scanned.fenced_starts
    )
    if framing_violation is not None:
        return None, framing_violation
    encoded = text.encode("utf-8")
    framing = text[: extensions.offset].encode("utf-8")
    extensions_bytes = text[extensions.offset : mandatory.offset].encode("utf-8")
    mandatory_bytes = text[mandatory.offset :].encode("utf-8")
    if framing + extensions_bytes + mandatory_bytes != encoded:
        return None, _UNSUPPORTED_CONTEXT
    return RuleLayout(framing, extensions_bytes, mandatory_bytes), None


def _framing_violation(
    lines: list[_PhysicalLine],
    extensions_offset: int,
    frontmatter_end: int,
    fenced_starts: frozenset[int],
) -> str | None:
    """Reject operational prose before the first ownership region.

    ``frontmatter_end`` is the already validated boundary. This function does
    not search for another close.
    """
    for line in lines:
        if line.start >= extensions_offset:
            break
        if line.start < frontmatter_end:
            continue
        content = line.content
        if line.start in fenced_starts:
            return f"operational prose outside ownership sections: {content!r}"
        if _is_blank(content) or _is_framing_metadata(content):
            continue
        return f"operational prose outside ownership sections: {content!r}"
    return None


def _rule_layout(text: str) -> RuleLayout | None:
    """Return the extracted layout, or ``None`` when the document is invalid."""
    return _scan_rule_layout(text)[0]


def _rule_layout_violation(text: str) -> str | None:
    """Return the layout-contract violation for one document, or ``None``."""
    return _scan_rule_layout(text)[1]


def _protected_rule_documents(catalog_unit: Mapping[str, object]) -> list[str]:
    documents = catalog_unit.get("rule_documents")
    if not isinstance(documents, list):
        return []
    return [_normalize_source_path(str(document)) for document in documents]


def _protected_documents_violation(
    uid: str,
    catalog_unit: Mapping[str, object],
    decl_unit: Mapping[str, object],
    upstream: _GitRepo,
    commit: str,
    snapshot: _Snapshot,
) -> str | None:
    """Compare each protected destination document to its source mandatory core.

    Source malformation is a fatal inventory error (``invalid_mapping``); a
    destination layout or mandatory-core violation is returned as a violation
    for the caller to report (check) or refuse (propose). Paths resolve only
    through the unit's ordinary file/tree member mappings.
    """
    for rule_document in _protected_rule_documents(catalog_unit):
        source_entry = upstream.file_entry(commit, rule_document, "invalid_mapping")
        _need(
            source_entry is not None,
            "invalid_mapping",
            f"{uid}: source rule document is missing: {rule_document}",
        )
        try:
            source_text = source_entry.content.decode("utf-8")
        except UnicodeDecodeError:
            _fail(
                "invalid_mapping",
                f"{uid}: source {rule_document} is not UTF-8 text",
            )
        source_layout, source_violation = _scan_rule_layout(source_text)
        _need(
            source_layout is not None,
            "invalid_mapping",
            f"{uid}: source rule document {rule_document} is malformed: "
            f"{source_violation}",
        )
        destination = _rule_document_destination(catalog_unit, decl_unit, rule_document)
        destination_entry = snapshot.file_entry(destination)
        if destination_entry is None:
            return f"{uid}: protected rule document is missing: {destination}"
        try:
            destination_text = destination_entry.content.decode("utf-8")
        except UnicodeDecodeError:
            return f"{uid}: protected rule document {destination} is not UTF-8 text"
        destination_layout, destination_violation = _scan_rule_layout(destination_text)
        if destination_layout is None:
            return f"{uid}: {destination}: {destination_violation}"
        if destination_layout.mandatory != source_layout.mandatory:
            return f"{uid}: {destination}: mandatory core differs from the source"
    return None

def _sibling_story_index(member_path: str) -> str:
    """Return the ``index.md`` path beside one story member path."""
    normalized = member_path.replace("\\", "/")
    if "/" not in normalized:
        return STORY_INDEX_NAME
    directory = normalized.rsplit("/", 1)[0]
    return f"{directory}/{STORY_INDEX_NAME}"


def _story_index_collisions(
    uid: str,
    catalog_unit: Mapping[str, object],
    decl_unit: Mapping[str, object],
    upstream: _GitRepo,
    commit: str,
    snapshot: _Snapshot,
) -> list[str]:
    """IO boundary: merge one applicable story unit's index in memory.

    The core index sits beside the unit's catalog member sources and the
    destination index beside the declared member destinations. The merged
    bytes stay in memory — this command path writes nothing.
    """
    declared = _declared_members(catalog_unit, decl_unit, uid)
    members = list(catalog_unit.get("members", []))
    _need(members, "invalid_mapping", f"{uid}: user-story unit must declare members")
    first = members[0]
    core_index_path = _sibling_story_index(str(_field(first, "source")))
    destination_index_path = _sibling_story_index(
        _normalize_destination(declared[str(_field(first, "id"))])
    )
    core_entry = upstream.file_entry(commit, core_index_path, "baseline_unavailable")
    destination_entry = snapshot.file_entry(destination_index_path)
    rows: list[StoryMergeMember] = [
        {
            "id": str(_field(member, "id")),
            "destination": declared[str(_field(member, "id"))],
            "collision_policy": _field(member, "collision_policy"),
        }
        for member in members
    ]
    _merged, collisions = merge_story_index(
        core_entry.content if core_entry is not None else b"",
        destination_entry.content if destination_entry is not None else None,
        rows,
    )
    return collisions


# ---------------------------------------------------------------------------
# check (protocol-v2 Section 4): read-only compliance report
# ---------------------------------------------------------------------------


def _member_digest_at(repo: _GitRepo, commit: str, source: str, projection: str) -> str:
    if _content_projection(projection) == "tree":
        return member_digest(repo.tree_entries(commit, source, "baseline_unavailable"))
    entry = repo.file_entry(commit, source, "baseline_unavailable")
    return member_digest([entry] if entry is not None else [])


def _unit_upstream_digest(
    repo: _GitRepo, commit: str, catalog_unit: Mapping[str, object]
) -> str:
    if catalog_unit.get("sync_projection") == "assertions":
        return assertion_list_digest(catalog_unit.get("assertions", []))
    projection = str(catalog_unit.get("sync_projection"))
    members = list(catalog_unit.get("members", []) or [])
    pairs = [
        (
            str(m.get("id")),
            _member_digest_at(repo, commit, str(m.get("source")), projection),
        )
        for m in members
    ]
    return unit_digest(pairs)


def _snapshot_member_digest(
    snapshot: _Snapshot, destination: str, projection: str
) -> str:
    if _content_projection(projection) == "tree":
        return member_digest(snapshot.tree_entries(destination))
    entry = snapshot.file_entry(destination)
    return member_digest([entry] if entry is not None else [])


def _destination_unit_digest(
    catalog_unit: Mapping[str, object],
    decl_unit: Mapping[str, object],
    snapshot: _Snapshot,
) -> str:
    """Digest the reviewed destination result in catalog member order."""
    if catalog_unit.get("sync_projection") == "assertions":
        stripped = _strip_comments(_fragment(snapshot, str(catalog_unit.get("destination"))))
        status = [
            (str(assertion.get("id")), str(assertion.get("contains")) in stripped)
            for assertion in catalog_unit.get("assertions", [])
        ]
        return assertion_status_digest(status)
    if decl_unit.get("mode") == "replacement":
        members = list(decl_unit.get("replacement_members", []) or [])
        projection_by_id = {
            str(member.get("id")): str(member.get("projection")) for member in members
        }
        pairs = [
            (
                str(member.get("id")),
                _snapshot_member_digest(
                    snapshot,
                    str(member.get("destination")),
                    projection_by_id[str(member.get("id"))],
                ),
            )
            for member in members
        ]
    else:
        declared = _declared_members(catalog_unit, decl_unit, str(catalog_unit.get("id")))
        pairs = [
            (
                str(member.get("id")),
                _snapshot_member_digest(
                    snapshot,
                    declared[str(member.get("id"))],
                    str(catalog_unit.get("sync_projection")),
                ),
            )
            for member in catalog_unit.get("members", [])
        ]
    return unit_digest(pairs)


def _target_destination_changed(
    catalog_unit: Mapping[str, object],
    decl_unit: Mapping[str, object],
    baseline_row: Mapping[str, object] | None,
    snapshot: _Snapshot,
    upstream: _GitRepo,
    target_revision: str,
) -> bool:
    """Compare target destinations to matching accepted members without deleting retired paths."""
    if baseline_row is None:
        if decl_unit.get("mode") == "mirror":
            if catalog_unit.get("sync_projection") == "assertions":
                return _destination_unit_digest(catalog_unit, decl_unit, snapshot) != assertion_status_digest(
                    [
                        (str(assertion.get("id")), True)
                        for assertion in catalog_unit.get("assertions", [])
                    ]
                )
            for member in catalog_unit.get("members", []) or []:
                destination = str(
                    _declared_members(catalog_unit, decl_unit, str(catalog_unit.get("id")))[
                        str(member.get("id"))
                    ]
                )
                source_digest = _member_digest_at(
                    upstream,
                    target_revision,
                    str(member.get("source")),
                    str(catalog_unit.get("sync_projection")),
                )
                if _snapshot_member_digest(
                    snapshot, destination, str(catalog_unit.get("sync_projection"))
                ) != source_digest:
                    return True
            return False
        return True
    if baseline_row.get("mode") != decl_unit.get("mode"):
        return True
    if catalog_unit.get("sync_projection") == "assertions":
        baseline_members = baseline_row.get("members", []) or []
        if len(baseline_members) != 1:
            return True
        current_digest = _destination_unit_digest(catalog_unit, decl_unit, snapshot)
        return current_digest != baseline_members[0].get("accepted_destination_digest")
    if decl_unit.get("mode") == "replacement":
        target_members = list(decl_unit.get("replacement_members", []) or [])
        baseline_members = {
            str(member.get("id")): member
            for member in baseline_row.get("replacement_members", []) or []
        }
        for member in target_members:
            member_id = str(member.get("id"))
            old = baseline_members.get(member_id)
            current = _snapshot_member_digest(
                snapshot,
                str(member.get("destination")),
                str(member.get("projection")),
            )
            if old is None or old.get("destination") != member.get("destination") or old.get(
                "projection"
            ) != member.get("projection") or old.get("accepted_destination_digest") != current:
                return True
        return False
    declared = _declared_members(catalog_unit, decl_unit, str(catalog_unit.get("id")))
    baseline_members = {
        str(member.get("id")): member for member in baseline_row.get("members", []) or []
    }
    projection = str(catalog_unit.get("sync_projection"))
    for member in catalog_unit.get("members", []) or []:
        member_id = str(member.get("id"))
        destination = declared[member_id]
        current = _snapshot_member_digest(snapshot, destination, projection)
        old = baseline_members.get(member_id)
        if old is None:
            if decl_unit.get("mode") != "mirror":
                return True
            target_upstream = _member_digest_at(
                upstream, target_revision, str(member.get("source")), projection
            )
            if current != target_upstream:
                return True
        elif (
            old.get("destination") != destination
            or old.get("accepted_destination_digest") != current
        ):
            return True
    return False


def _fragment(snapshot: _Snapshot, destination: str) -> str:
    entry = snapshot.file_entry(destination)
    return entry.content.decode("utf-8", "replace") if entry is not None else ""


