"""Pure, IO-free top-level JSON object merge: source keys win, `mcp` by server name."""

from __future__ import annotations

from core_sync_pkg.domain.jsonc import KeyValueSpan, ObjectSpans, parse_object_spans

_INDENT = "  "
_MCP_KEY = "mcp"
_SERVERS_KEY = "servers"


def merge_top_level(source_text: str, destination_text: str) -> str:
    """Merge the source object's top-level keys into the destination text.

    Each key already present in the destination has its value span replaced by
    the source's raw value, except `mcp`: when both sides hold `mcp.servers` as
    an object the `servers` members merge by name — a same-named server is
    core-wins, a source-only server is inserted, and every destination-only
    server and any non-`servers` child of the destination `mcp` survive.
    Source-only keys are inserted before the destination's closing brace. Bytes
    outside those spans are preserved verbatim. A non-object or malformed source
    or destination raises :class:`MalformedJsonc`.
    """
    source = parse_object_spans(source_text)
    destination = parse_object_spans(destination_text)
    source_spans: dict[str, KeyValueSpan] = {
        span["key"]: span for span in source["spans"]
    }
    destination_spans: dict[str, KeyValueSpan] = {
        span["key"]: span for span in destination["spans"]
    }

    edits: list[tuple[int, int, str]] = []
    source_only: list[str] = []
    for key, span in source_spans.items():
        existing = destination_spans.get(key)
        if existing is None:
            source_only.append(source_text[span["member_start"] : span["value_end"]])
            continue
        if key == _MCP_KEY and _merge_mcp_servers(
            source_text, span, destination_text, existing, edits
        ):
            continue
        raw_value = source_text[span["value_start"] : span["value_end"]]
        edits.append((existing["value_start"], existing["value_end"], raw_value))

    result = _apply_edits(destination_text, edits)
    if not source_only:
        return result

    inserted = ",\n".join(f"{_INDENT}{member}" for member in source_only)
    separator = "," if destination_spans and not destination["trailing_comma"] else ""
    close_index = _shifted_close_index(destination, edits)
    return (
        result[:close_index]
        + separator
        + "\n"
        + inserted
        + "\n"
        + result[close_index:]
    )


def is_merged(source_text: str, destination_text: str) -> bool:
    """Return whether every source top-level key is present with an equal value.

    Extra destination-only keys are allowed. For `mcp`, when both sides hold
    `mcp.servers` as an object the destination must contain every source server
    with an equal value plus any extra servers; otherwise `mcp` is compared
    exactly like any other key. Comparison is semantic, so formatting and
    comments in the destination do not affect the result. A non-object or
    malformed source or destination raises :class:`MalformedJsonc`.
    """
    source = parse_object_spans(source_text)
    destination = parse_object_spans(destination_text)
    source_spans: dict[str, KeyValueSpan] = {
        span["key"]: span for span in source["spans"]
    }
    destination_spans: dict[str, KeyValueSpan] = {
        span["key"]: span for span in destination["spans"]
    }
    destination_value = destination["value"]
    for key, value in source["value"].items():
        if key not in destination_value:
            return False
        if key == _MCP_KEY and _mcp_servers_contained(
            source_spans.get(key), destination_spans.get(key)
        ):
            continue
        if destination_value[key] != value:
            return False
    return True


def _merge_mcp_servers(
    source_text: str,
    source_span: KeyValueSpan,
    destination_text: str,
    destination_span: KeyValueSpan,
    edits: list[tuple[int, int, str]],
) -> bool:
    """Merge the source `mcp` value into the destination by server name.

    Appends the resulting edits and returns `True` when both sides hold
    `mcp.servers` as an object; returns `False` so the caller replaces the `mcp`
    value wholesale in every other case.
    """
    source_servers = _servers_object(source_span)
    destination_servers = _servers_object(destination_span)
    if source_servers is None or destination_servers is None:
        return False
    destination_members = {
        member["key"]: member for member in destination_servers["spans"]
    }
    inserted: list[str] = []
    for member in source_servers["spans"]:
        existing = destination_members.get(member["key"])
        raw_value = source_text[member["value_start"] : member["value_end"]]
        if existing is None:
            inserted.append(source_text[member["member_start"] : member["value_end"]])
        else:
            edits.append((existing["value_start"], existing["value_end"], raw_value))
    if inserted:
        indent = _member_indent(destination_text, destination_servers)
        close_indent = _close_line_indent(destination_text, destination_servers)
        body = ",\n".join(f"{indent}{member}" for member in inserted)
        separator = (
            ","
            if destination_servers["spans"] and not destination_servers["trailing_comma"]
            else ""
        )
        close_index = destination_servers["close_index"]
        edits.append((close_index, close_index, f"{separator}\n{body}\n{close_indent}"))
    return True


def _servers_object(span: KeyValueSpan | None) -> ObjectSpans | None:
    """Return the `servers` object body nested under an `mcp` value, if any."""
    if span is None:
        return None
    mcp_body = span["members"]
    if mcp_body is None:
        return None
    servers = {member["key"]: member for member in mcp_body["spans"]}.get(
        _SERVERS_KEY
    )
    if servers is None:
        return None
    return servers["members"]


def _mcp_servers_contained(
    source_span: KeyValueSpan | None, destination_span: KeyValueSpan | None
) -> bool:
    """Return whether the destination `mcp.servers` holds every source server."""
    source_servers = _servers_object(source_span)
    destination_servers = _servers_object(destination_span)
    if source_servers is None or destination_servers is None:
        return False
    destination_value = destination_servers["value"]
    return all(
        name in destination_value and destination_value[name] == value
        for name, value in source_servers["value"].items()
    )


def _apply_edits(text: str, edits: list[tuple[int, int, str]]) -> str:
    """Return `text` with each `(start, end, value)` edit applied in order.

    A zero-width `(index, index, value)` edit inserts `value` at `index`.
    """
    if not edits:
        return text
    parts: list[str] = []
    cursor = 0
    for start, end, value in sorted(edits, key=lambda item: (item[0], item[1])):
        parts.append(text[cursor:start])
        parts.append(value)
        cursor = end
    parts.append(text[cursor:])
    return "".join(parts)


def _member_indent(text: str, object_spans: ObjectSpans) -> str:
    """Return the indentation an object's inserted members should use."""
    spans = object_spans["spans"]
    if spans:
        prefix = _line_prefix(text, spans[-1]["member_start"])
        if not prefix.strip():
            return prefix
    close_prefix = _line_prefix(text, object_spans["close_index"])
    if not close_prefix.strip():
        return close_prefix + _INDENT
    return _INDENT * 2


def _close_line_indent(text: str, object_spans: ObjectSpans) -> str:
    """Return the whitespace an object's closing brace is indented with."""
    prefix = _line_prefix(text, object_spans["close_index"])
    return prefix if not prefix.strip() else ""


def _line_prefix(text: str, index: int) -> str:
    """Return the text between the previous newline and `index`."""
    return text[text.rfind("\n", 0, index) + 1 : index]


def _shifted_close_index(
    destination: ObjectSpans, edits: list[tuple[int, int, str]]
) -> int:
    """Return the destination's closing-brace offset after the edits."""
    shift = sum(
        len(value) - (end - start)
        for start, end, value in edits
        if end <= destination["close_index"]
    )
    return destination["close_index"] + shift
