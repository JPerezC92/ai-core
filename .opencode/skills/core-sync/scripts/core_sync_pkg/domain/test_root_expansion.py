"""Domain unit tests for the pure skill-root expansion over enumerated paths.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/domain/test_root_expansion.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json  # noqa: E402
from typing import NotRequired, Sequence, TypedDict  # noqa: E402

from core_sync_pkg.domain.clearance import (  # noqa: E402
    SkillRootEntry,
    expand_clearance,
    expand_skill_root,
    parse_clearance,
)
from core_sync_pkg.domain.constants import CLEARANCE_SCHEMA  # noqa: E402
from core_sync_pkg.domain.errors import DomainError  # noqa: E402

ROOT = ".opencode/skills/foo/"


class FileRecordShape(TypedDict):
    """Well-formed cleared file record: mode plus an optional root role."""

    mode: str
    role: NotRequired[str]


class RootRecordShape(TypedDict):
    """Well-formed skill-root record: default mode plus an optional subset."""

    mode: str
    region_files: NotRequired[list[object]]


def _skill_root(mode: str, region_files: Sequence[str] = ()) -> SkillRootEntry:
    """Build one parsed skill-root entry with a region-file subset."""
    return SkillRootEntry(mode=mode, region_files=tuple(region_files))


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


def _enumeration(root: str, files: Sequence[str]) -> dict[str, list[str]]:
    """Build one root-keyed enumeration mapping as passed to the expansion."""
    return {root: list(files)}


class RootExpansionTests:
    """Map enumerated root-relative paths to modes purely, caches excluded."""

    def test_subset_member_resolves_region_and_default_covers_rest(self) -> None:
        entry = _skill_root("raw", ["SKILL.md"])
        modes = expand_skill_root(ROOT, entry, ["SKILL.md", "README.md"])
        assert modes == {
            ROOT + "SKILL.md": "region",
            ROOT + "README.md": "raw",
        }

    def test_nested_paths_resolve_through_the_same_rule(self) -> None:
        entry = _skill_root("raw", ["scripts/deep/SKILL.md"])
        modes = expand_skill_root(
            ROOT, entry, ["scripts/deep/run.py", "scripts/deep/SKILL.md"]
        )
        assert modes == {
            ROOT + "scripts/deep/run.py": "raw",
            ROOT + "scripts/deep/SKILL.md": "region",
        }

    def test_interpreter_caches_never_enter_the_expansion(self) -> None:
        entry = _skill_root("raw", ["__pycache__/listed.pyc"])
        modes = expand_skill_root(
            ROOT,
            entry,
            [
                "__pycache__/m.pyc",
                "pkg/__pycache__/m.py",
                "pkg/mod.pyc",
                "pkg/mod.py",
            ],
        )
        assert modes == {ROOT + "pkg/mod.py": "raw"}

    def test_region_files_escape_members_are_rejected_at_parse(self) -> None:
        for member in ("../escape.md", "/abs.md", "dir/../escape.md"):
            result = parse_clearance(
                _document({"skill/": _root_record("raw", region_files=[member])})
            )
            assert isinstance(result, DomainError), member

    def test_mixed_file_and_root_document_expands_both(self) -> None:
        result = parse_clearance(
            _document(
                {
                    "AGENTS.md": _file_record("region", role="root"),
                    "opencode.jsonc": _file_record("merge"),
                    ROOT: _root_record("raw", region_files=["SKILL.md"]),
                }
            )
        )
        assert isinstance(result, dict)
        modes = expand_clearance(
            result,
            _enumeration(ROOT, ["SKILL.md", "data.json", "__pycache__/m.pyc"]),
        )
        assert modes == {
            "AGENTS.md": "region",
            "opencode.jsonc": "merge",
            ROOT + "SKILL.md": "region",
            ROOT + "data.json": "raw",
        }

    def test_root_without_enumeration_contributes_no_paths(self) -> None:
        entry = _skill_root("raw")
        assert expand_skill_root(ROOT, entry, []) == {}
        assert expand_clearance({ROOT: entry}, {}) == {}
