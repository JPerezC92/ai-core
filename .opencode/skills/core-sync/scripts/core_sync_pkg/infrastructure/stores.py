"""Infrastructure: YAML bindings store and JSON distribution-clearance adapters."""

from __future__ import annotations

import json
from pathlib import Path

from core_sync_pkg.domain.bindings import (
    Bindings,
    parse_bindings,
    serialize_bindings,
)
from core_sync_pkg.domain.constants import CLEARANCE_REL, SCHEMA_VERSION
from core_sync_pkg.domain.reconciliation import (
    ReconciliationEntry,
    reconciliation_report_path,
    render_reconciliation_report,
)

from .filesystem import read_text, write_text


def load_bindings(path: Path) -> Bindings | None:
    """Read and parse the bindings file at the IO boundary."""
    text = read_text(path)
    if text is None:
        return None
    return parse_bindings(text)


def save_bindings(path: Path, bindings: Bindings) -> None:
    """Serialize and write the bindings file at the IO boundary."""
    write_text(path, serialize_bindings(bindings))


def load_clearance(source_dir: Path) -> tuple[set[str] | None, bool]:
    """Read the source distribution-clearance file at the IO boundary.

    Returns `(None, False)` when the file is absent, `(None, True)` when it is
    present but malformed, or the cleared path set and `True` when valid.
    """
    path = source_dir / CLEARANCE_REL
    if not path.exists():
        return (None, False)
    text = read_text(path)
    if text is None:
        return (None, True)
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return (None, True)
    if (
        not isinstance(data, dict)
        or type(data.get("schema")) is not int
        or data.get("schema") != SCHEMA_VERSION
        or not isinstance(data.get("cleared"), list)
        or not all(isinstance(item, str) for item in data["cleared"])
    ):
        return (None, True)
    return (set(data["cleared"]), True)


class YamlBindingsStore:
    """Read and write the YAML bindings document and its reconciliation report."""

    def load(self, path: Path) -> Bindings | None:
        return load_bindings(path)

    def save(self, path: Path, bindings: Bindings) -> None:
        save_bindings(path, bindings)

    def write_report(
        self, bindings_path: Path, entries: list[ReconciliationEntry], revision: str
    ) -> None:
        path = reconciliation_report_path(bindings_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        write_text(path, render_reconciliation_report(entries, revision))


class JsonClearanceRecord:
    """Read the JSON distribution-clearance record."""

    def load(self, source_dir: Path) -> tuple[set[str] | None, bool]:
        return load_clearance(source_dir)


__all__ = [
    "load_bindings",
    "save_bindings",
    "load_clearance",
    "YamlBindingsStore",
    "JsonClearanceRecord",
]
