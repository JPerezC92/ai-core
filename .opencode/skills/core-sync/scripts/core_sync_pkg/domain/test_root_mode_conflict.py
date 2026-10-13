"""Domain unit tests for root-derived mode resolution and mode conflicts.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/domain/test_root_mode_conflict.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json  # noqa: E402
from typing import NotRequired, Sequence, TypedDict  # noqa: E402

from core_sync_pkg.domain.bindings import (  # noqa: E402
    BindingEntry,
    binding_mode_conflict,
    resolve_source_mode,
)
from core_sync_pkg.domain.clearance import expand_clearance, parse_clearance  # noqa: E402
from core_sync_pkg.domain.constants import CLEARANCE_SCHEMA, BindingMode  # noqa: E402
from core_sync_pkg.domain.errors import CODE_INVALID, DomainError  # noqa: E402

ROOT = ".opencode/skills/foo/"


class FileRecordShape(TypedDict):
    """Well-formed cleared file record: mode plus an optional root role."""

    mode: str
    role: NotRequired[str]


class RootRecordShape(TypedDict):
    """Well-formed skill-root record: default mode plus an optional subset."""

    mode: str
    region_files: NotRequired[list[object]]


def _file_record(mode: str, role: str | None = None) -> FileRecordShape:
    """Build one well-formed cleared file record."""
    record: FileRecordShape = {"mode": mode}
    if role is not None:
        record["role"] = role
    return record


def _root_record(
    mode: str, region_files: Sequence[object] | None = None
) -> RootRecordShape:
    """Build one skill-root record; members are validated as strings at parse."""
    record: RootRecordShape = {"mode": mode}
    if region_files is not None:
        record["region_files"] = list(region_files)
    return record


def _document(cleared: object) -> str:
    """Render a version-1 clearance document with the given entries."""
    return json.dumps({"schema": CLEARANCE_SCHEMA, "cleared": cleared})


def _binding(
    source: str, destination: str, mode: BindingMode
) -> BindingEntry:
    """Build one binding entry with an explicit declaration mode."""
    return {"source": source, "destinations": [destination], "mode": mode}


def _expanded_modes() -> dict[str, str]:
    """Expand a mixed file-plus-root clearance document purely."""
    entries = parse_clearance(
        _document(
            {
                "skill.md": _file_record("region"),
                ROOT: _root_record("raw", region_files=["SKILL.md"]),
            }
        )
    )
    assert isinstance(entries, dict)
    return expand_clearance(entries, {ROOT: ["SKILL.md", "README.md"]})


class RootDerivedModeConflictTests:
    """Root-derived modes resolve and conflict exactly like per-file modes."""

    def test_resolve_source_mode_reads_root_derived_modes(self) -> None:
        modes = _expanded_modes()
        assert resolve_source_mode(ROOT + "SKILL.md", modes) == "region"
        assert resolve_source_mode(ROOT + "README.md", modes) == "raw"
        assert resolve_source_mode("skill.md", modes) == "region"
        assert resolve_source_mode("absent.md", modes) is None

    def test_root_derived_region_mode_conflicts_with_raw_binding(self) -> None:
        modes = _expanded_modes()
        conflict = binding_mode_conflict(
            _binding(ROOT + "SKILL.md", ROOT + "SKILL.md", "raw"), modes
        )
        assert isinstance(conflict, DomainError)
        assert conflict.code == CODE_INVALID
        assert conflict.message == (
            "binding mode 'raw' conflicts with source clearance mode "
            f"'region' for {ROOT}SKILL.md"
        )

    def test_root_derived_default_mode_conflicts_like_per_file_mode(self) -> None:
        modes = _expanded_modes()
        root_conflict = binding_mode_conflict(
            _binding(ROOT + "SKILL.md", "out.md", "raw"), modes
        )
        file_conflict = binding_mode_conflict(
            _binding("skill.md", "skill.md", "raw"), modes
        )
        assert isinstance(root_conflict, DomainError)
        assert isinstance(file_conflict, DomainError)
        assert root_conflict.code == file_conflict.code == CODE_INVALID
        prefix = "binding mode 'raw' conflicts with source clearance mode "
        assert root_conflict.message.startswith(prefix)
        assert file_conflict.message.startswith(prefix)

    def test_root_derived_raw_default_accepts_raw_binding(self) -> None:
        modes = _expanded_modes()
        conflict = binding_mode_conflict(
            _binding(ROOT + "README.md", "README.md", "raw"), modes
        )
        assert conflict is None

    def test_region_declaration_never_conflicts(self) -> None:
        modes = _expanded_modes()
        conflict = binding_mode_conflict(
            _binding(ROOT + "README.md", "README.md", "region"), modes
        )
        assert conflict is None

    def test_uncleared_source_raises_no_conflict(self) -> None:
        modes = _expanded_modes()
        conflict = binding_mode_conflict(
            _binding("absent.md", "absent.md", "raw"), modes
        )
        assert conflict is None
