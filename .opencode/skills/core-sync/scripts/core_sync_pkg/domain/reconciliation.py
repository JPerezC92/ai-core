"""Pure reconciliation artifacts: report rendering, path derivation, and blocker text."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import yaml

from core_sync_pkg.domain.constants import (
    RECONCILE_BEGIN,
    RECONCILE_BODY,
    RECONCILE_END,
    RECONCILIATION_DIRNAME,
    RECONCILIATION_FILENAME,
    SCHEMA_VERSION,
)
from core_sync_pkg.domain.markers import _exact_marker_line_indices


class ReconciliationEntry(TypedDict):
    """One destination that `init` generated or refreshed for review."""

    destination: str
    source: str
    action: str


def render_reconciliation_report(
    entries: list[ReconciliationEntry], revision: str
) -> str:
    """Render the reconciliation report for an `init` run to YAML."""
    data = {
        "schema": SCHEMA_VERSION,
        "core_revision": revision,
        "entries": [
            {
                "destination": entry["destination"],
                "source": entry["source"],
                "action": entry["action"],
            }
            for entry in entries
        ],
    }
    return yaml.safe_dump(data, sort_keys=False, default_flow_style=False)


def reconciliation_report_path(bindings_path: Path) -> Path:
    """Return the reconciliation report path derived from the bindings file."""
    return bindings_path.parent / RECONCILIATION_DIRNAME / RECONCILIATION_FILENAME


def _reconcile_block_lines() -> list[str]:
    """Return the reconciliation blocker block as newline-terminated lines."""
    return [
        RECONCILE_BEGIN + "\n",
        RECONCILE_BODY + "\n",
        RECONCILE_END + "\n",
    ]


def find_reconcile_block(lines: list[str]) -> tuple[int, int] | None:
    """Return the (begin, end) line indices of the single reconcile marker pair.

    A marker counts only as an exact stripped line outside a fenced code block.
    Returns None when the markers are missing, duplicated, or reversed.
    """
    begins = _exact_marker_line_indices(lines, RECONCILE_BEGIN)
    ends = _exact_marker_line_indices(lines, RECONCILE_END)
    if len(begins) != 1 or len(ends) != 1:
        return None
    if begins[0] > ends[0]:
        return None
    return (begins[0], ends[0])


def _append_reconcile_block(root_text: str, block_lines: list[str]) -> str:
    """Append the blocker block after a single blank separator line."""
    base = root_text
    if base and not base.endswith("\n"):
        base += "\n"
    separator = "\n" if base else ""
    return base + separator + "".join(block_lines)


def sync_reconciliation_blocker(root_text: str, pending: list[str]) -> str:
    """Add, refresh, or remove the reconciliation blocker block in root text.

    Pure transform. A non-empty `pending` ensures the marker-delimited blocker
    block exists — its body is replaced in place when present, otherwise the block
    is appended after one blank line. An empty `pending` removes the block and its
    one-line blank separator. The transform is idempotent.
    """
    lines = root_text.splitlines(keepends=True)
    block = find_reconcile_block(lines)
    if pending:
        block_lines = _reconcile_block_lines()
        if block is not None:
            begin_index, end_index = block
            return "".join(lines[:begin_index] + block_lines + lines[end_index + 1 :])
        return _append_reconcile_block(root_text, block_lines)
    if block is None:
        return root_text
    begin_index, end_index = block
    start = begin_index
    if start > 0 and lines[start - 1].strip() == "":
        start -= 1
    stop = end_index + 1
    if stop < len(lines) and lines[stop].strip() == "":
        stop += 1
    return "".join(lines[:start] + lines[stop:])
