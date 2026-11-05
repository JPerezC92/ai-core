"""Pure, IO-free top-level JSON object merge: source keys win, `mcp` by server name.

The `qmd` MCP server's `--index` argument is retargeted to the destination
project name, so each destination retrieves with its own index.
"""

from __future__ import annotations

import json

from core_sync_pkg.domain.jsonc import KeyValueSpan, ObjectSpans, parse_object_spans

_INDENT = "  "
_INDEX_FLAG = "--index"
_MCP_KEY = "mcp"
_QMD_SERVER_KEY = "qmd"
_SERVERS_KEY = "servers"


def merge_top_level(
    source_text: str, destination_text: str, *, project_name: str = ""
) -> str:
    """Merge the source object's top-level keys into the destination text.

    Each key already present in the destination has its value span replaced by
    the source's raw value, except `mcp`: when both sides hold `mcp.servers` as
    an object the `servers` members merge by name — a same-named server is
    core-wins, a source-only server is inserted, and every destination-only
    server and any non-`servers` child of the destination `mcp` survive.
    Source-only keys are inserted before the destination's closing brace. Bytes
    outside those spans are preserved verbatim. A non-object or malformed source
    or destination raises :class:`MalformedJsonc`.

    `project_name` retargets the `qmd` server on all three `mcp` write paths —
    the per-server merge, the wholesale `mcp` replacement, and the insertion of
    a source-only `mcp` key: the argument following `--index` becomes
    `project_name`, so every destination retrieves with its own index. An empty
    `project_name` leaves every value untouched.
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
            if key == _MCP_KEY:
                member_text = _retarget_mcp_member_text(
                    source_text, span, project_name
                )
            else:
                member_text = source_text[
                    span["member_start"] : span["value_end"]
                ]
            source_only.append(member_text)
            continue
        if key == _MCP_KEY and _merge_mcp_servers(
            source_text, span, destination_text, existing, edits, project_name
        ):
            continue
        if key == _MCP_KEY:
            raw_value = _retarget_mcp_value_text(source_text, span, project_name)
        else:
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


def is_merged(
    source_text: str, destination_text: str, *, project_name: str = ""
) -> bool:
    """Return whether every source top-level key is present with an equal value.

    Extra destination-only keys are allowed. For `mcp`, when both sides hold
    `mcp.servers` as an object the destination must contain every source server
    with an equal value plus any extra servers; otherwise `mcp` is compared
    exactly like any other key. Comparison is semantic, so formatting and
    comments in the destination do not affect the result. A non-object or
    malformed source or destination raises :class:`MalformedJsonc`.

    `project_name` applies the same `qmd` `--index` retargeting as
    :func:`merge_top_level` to the value it is compared against, so a
    destination that function produced reports as current.
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
        expected = value
        if key == _MCP_KEY:
            if _mcp_servers_contained(
                source_spans.get(key), destination_spans.get(key), project_name
            ):
                continue
            expected = _retarget_mcp_value(value, project_name)
        if destination_value[key] != expected:
            return False
    return True


def _merge_mcp_servers(
    source_text: str,
    source_span: KeyValueSpan,
    destination_text: str,
    destination_span: KeyValueSpan,
    edits: list[tuple[int, int, str]],
    project_name: str,
) -> bool:
    """Merge the source `mcp` value into the destination by server name.

    Appends the resulting edits and returns `True` when both sides hold
    `mcp.servers` as an object; returns `False` so the caller replaces the `mcp`
    value wholesale in every other case. The `qmd` server's `--index` argument
    is retargeted to `project_name` on both the replaced and inserted paths.
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
        if member["key"] == _QMD_SERVER_KEY:
            raw_value = _retarget_index_literal(
                raw_value, member["value"], project_name
            )
        if existing is None:
            prefix = source_text[member["member_start"] : member["value_start"]]
            inserted.append(prefix + raw_value)
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
    source_span: KeyValueSpan | None,
    destination_span: KeyValueSpan | None,
    project_name: str,
) -> bool:
    """Return whether the destination `mcp.servers` holds every source server."""
    source_servers = _servers_object(source_span)
    destination_servers = _servers_object(destination_span)
    if source_servers is None or destination_servers is None:
        return False
    destination_value = destination_servers["value"]
    expected = {
        name: _retarget_server_value(name, value, project_name)
        for name, value in source_servers["value"].items()
    }
    return all(
        name in destination_value and destination_value[name] == value
        for name, value in expected.items()
    )


def _retarget_server_value(name: str, value: object, project_name: str) -> object:
    """Return a source server value with its `--index` argument retargeted."""
    if name != _QMD_SERVER_KEY:
        return value
    return _retarget_qmd_server(value, project_name)


def _retarget_mcp_value(value: object, project_name: str) -> object:
    """Return an `mcp` value whose `qmd` server index is retargeted.

    Returns `value` itself when nothing changes, so a comparison of a source
    without a retargetable `qmd` server is unaffected.
    """
    if project_name == "" or not isinstance(value, dict):
        return value
    servers = value.get(_SERVERS_KEY)
    if not isinstance(servers, dict):
        return value
    qmd = servers.get(_QMD_SERVER_KEY)
    if qmd is None:
        return value
    retargeted = _retarget_qmd_server(qmd, project_name)
    if retargeted is qmd:
        return value
    return {
        **value,
        _SERVERS_KEY: {**servers, _QMD_SERVER_KEY: retargeted},
    }


def _retarget_qmd_server(server_value: object, project_name: str) -> object:
    """Return a server value with the argument following `--index` replaced."""
    if project_name == "" or not isinstance(server_value, dict):
        return server_value
    command = server_value.get("command")
    if not isinstance(command, list):
        return server_value
    position = _index_argument_position(command)
    if position is None:
        return server_value
    retargeted = list(command)
    retargeted[position] = project_name
    return {**server_value, "command": retargeted}


def _index_argument_position(command: list[object]) -> int | None:
    """Return the command position holding the index name after `--index`."""
    for position, item in enumerate(command[:-1]):
        if item == _INDEX_FLAG and isinstance(command[position + 1], str):
            return position + 1
    return None


def _qmd_index_name(server_value: object) -> str | None:
    """Return the string argument following `--index` in a parsed server value."""
    if not isinstance(server_value, dict):
        return None
    command = server_value.get("command")
    if not isinstance(command, list):
        return None
    position = _index_argument_position(command)
    if position is None:
        return None
    index_name = command[position]
    return index_name if isinstance(index_name, str) else None


def _retarget_mcp_member_text(
    source_text: str, source_span: KeyValueSpan, project_name: str
) -> str:
    """Return an `mcp` member's raw text with its `qmd` index retargeted."""
    return (
        source_text[source_span["member_start"] : source_span["value_start"]]
        + _retarget_mcp_value_text(source_text, source_span, project_name)
    )


def _retarget_mcp_value_text(
    source_text: str, source_span: KeyValueSpan, project_name: str
) -> str:
    """Return an `mcp` value's raw text with its `qmd` index retargeted.

    Only the `qmd` server's own span is rewritten, so an equal literal held by
    another server is never touched.
    """
    value_text = source_text[source_span["value_start"] : source_span["value_end"]]
    member = _server_member(source_span, _QMD_SERVER_KEY)
    if member is None:
        return value_text
    start = member["value_start"] - source_span["value_start"]
    end = member["value_end"] - source_span["value_start"]
    server_text = _retarget_index_literal(
        value_text[start:end], member["value"], project_name
    )
    return value_text[:start] + server_text + value_text[end:]


def _retarget_index_literal(
    server_text: str, server_value: object, project_name: str
) -> str:
    """Return a `qmd` server's raw text with its `--index` literal replaced.

    The literals come from :func:`json.dumps`, so their quoting and escaping
    follow the JSON grammar instead of hand-written quotes.
    """
    if project_name == "":
        return server_text
    index_name = _qmd_index_name(server_value)
    if index_name is None or index_name == project_name:
        return server_text
    return server_text.replace(json.dumps(index_name), json.dumps(project_name), 1)


def _server_member(span: KeyValueSpan, name: str) -> KeyValueSpan | None:
    """Return one named server member under an `mcp` value, if present."""
    servers = _servers_object(span)
    if servers is None:
        return None
    return next((item for item in servers["spans"] if item["key"] == name), None)


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
