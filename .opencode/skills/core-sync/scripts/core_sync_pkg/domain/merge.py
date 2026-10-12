"""Pure top-level JSON object merge: source keys win; destination extras and comments survive."""

from __future__ import annotations

from core_sync_pkg.domain.jsonc import KeyValueSpan, ObjectSpans, parse_object_spans

_INDENT = "  "


def merge_top_level(source_text: str, destination_text: str) -> str:
    """Merge the source object's top-level keys into the destination text.

    Each key already present in the destination has its value span replaced by
    the source's raw value; source-only keys are inserted before the
    destination's closing brace. Bytes outside those spans are preserved
    verbatim. A non-object or malformed source or destination raises
    :class:`MalformedJsonc`.
    """
    source = parse_object_spans(source_text)
    destination = parse_object_spans(destination_text)
    source_spans: dict[str, KeyValueSpan] = {
        span["key"]: span for span in source["spans"]
    }
    destination_spans: dict[str, KeyValueSpan] = {
        span["key"]: span for span in destination["spans"]
    }

    replacements: list[tuple[int, int, str]] = []
    source_only: list[str] = []
    for key, span in source_spans.items():
        raw_value = source_text[span["value_start"] : span["value_end"]]
        existing = destination_spans.get(key)
        if existing is None:
            source_only.append(source_text[span["member_start"] : span["value_end"]])
        else:
            replacements.append(
                (existing["value_start"], existing["value_end"], raw_value)
            )

    result = _apply_replacements(destination_text, replacements)
    if not source_only:
        return result

    inserted = ",\n".join(f"{_INDENT}{member}" for member in source_only)
    separator = "," if destination_spans and not destination["trailing_comma"] else ""
    close_index = _shifted_close_index(destination, replacements)
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

    Extra destination-only keys are allowed. Comparison is semantic, so
    formatting and comments in the destination do not affect the result. A
    non-object or malformed source or destination raises :class:`MalformedJsonc`.
    """
    source = parse_object_spans(source_text)
    destination = parse_object_spans(destination_text)
    destination_value = destination["value"]
    return all(
        key in destination_value and destination_value[key] == value
        for key, value in source["value"].items()
    )


def _apply_replacements(text: str, replacements: list[tuple[int, int, str]]) -> str:
    """Return `text` with each `(start, end, value)` span replaced by `value`."""
    if not replacements:
        return text
    parts: list[str] = []
    cursor = 0
    for start, end, value in sorted(replacements, key=lambda item: item[0]):
        parts.append(text[cursor:start])
        parts.append(value)
        cursor = end
    parts.append(text[cursor:])
    return "".join(parts)


def _shifted_close_index(
    destination: ObjectSpans, replacements: list[tuple[int, int, str]]
) -> int:
    """Return the destination's closing-brace offset after the replacements."""
    shift = sum(
        len(value) - (end - start)
        for start, end, value in replacements
        if end <= destination["close_index"]
    )
    return destination["close_index"] + shift
