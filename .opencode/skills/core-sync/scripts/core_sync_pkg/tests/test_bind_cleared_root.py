"""End-to-end tests for `init --bind-cleared` root handling.

Destination instruction-root detection and override, plus skill-root clearance
expansion: files under a cleared skill root enroll automatically at each sync —
subset files region-bound, other files default-mode byte copies, interpreter
caches never shipped.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import NotRequired, TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import REV_A, _write_file  # noqa: E402
from core_sync_pkg.domain.constants import CLEARANCE_SCHEMA  # noqa: E402
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import load_bindings  # noqa: E402

CLEARANCE = "distribution-clearance.json"
SKILL_ROOT = ".opencode/skills/foo/"
SKILL_MARKED = (
    "---\nname: foo\n---\n"
    "<!-- core:begin -->\nSkill core\n<!-- core:end -->\n"
)
ROOT_MARKED = (
    "---\nname: agents\n---\n"
    "<!-- core:begin -->\nRoot core\n<!-- core:end -->\n"
)
NOTE_BYTES = b"note payload\n"
CACHE_BYTES = b"cache junk\n"
EXTRA_BYTES = b"extra payload\n"


class FileRecordShape(TypedDict):
    """Well-formed cleared file record as written by fixture sources."""

    mode: str
    role: NotRequired[str]


class RootRecordShape(TypedDict):
    """Well-formed skill-root record: default mode plus a region-file subset."""

    mode: str
    region_files: NotRequired[list[str]]


class ClearanceDocument(TypedDict):
    """Well-formed version-1 clearance document maintained by fixtures."""

    schema: int
    cleared: dict[str, FileRecordShape | RootRecordShape]


def _clearance_document(skill_root: bool) -> ClearanceDocument:
    """Build the fixture source's typed version-1 clearance document."""
    cleared: dict[str, FileRecordShape | RootRecordShape] = {
        "AGENTS.md": {"mode": "region", "role": "root"},
    }
    if skill_root:
        cleared[SKILL_ROOT] = {"mode": "raw", "region_files": ["SKILL.md"]}
    return {"schema": CLEARANCE_SCHEMA, "cleared": cleared}


def _destination_root() -> str:
    """Build one destination instruction-root file body."""
    return "---\nname: dest\n---\n# Dest\n"


def _write_payload(source: Path, relative: str, content: bytes) -> Path:
    """Write one raw source payload without per-file clearance bookkeeping."""
    path = source / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return path


def _source_with_skill_root(tmp_path: Path) -> Path:
    """Build the fixture source tree: root runtime plus one cleared skill root."""
    source = tmp_path / "source"
    _write_file(source, "AGENTS.md", ROOT_MARKED)
    _write_payload(source, SKILL_ROOT + "SKILL.md", SKILL_MARKED.encode())
    _write_payload(source, SKILL_ROOT + "note.md", NOTE_BYTES)
    _write_payload(source, SKILL_ROOT + "__pycache__/x.pyc", CACHE_BYTES)
    (source / CLEARANCE).write_text(
        json.dumps(_clearance_document(skill_root=True)) + "\n",
        encoding="utf-8",
    )
    return source


def _init_args(source: Path, destination: Path, bindings: Path) -> list[str]:
    """Build the `init --bind-cleared` CLI arguments for a fixture."""
    return [
        "init",
        "--source", str(source),
        "--destination", str(destination),
        "--bindings", str(bindings),
        "--source-revision", REV_A,
        "--bind-cleared",
    ]


class BindClearedRootRoutingTests:
    """`init --bind-cleared` routes the root source to the instruction root."""

    def test_root_source_routes_to_detected_destination_root(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        _write_file(source, "AGENTS.md", ROOT_MARKED)
        (source / CLEARANCE).write_text(
            json.dumps(_clearance_document(skill_root=False)) + "\n",
            encoding="utf-8",
        )
        destination = tmp_path / "destination"
        destination.mkdir()
        (destination / "AGENTS.md").write_text(_destination_root(), encoding="utf-8")
        bindings = tmp_path / "bindings.yaml"

        code = main(_init_args(source, destination, bindings))

        assert code == 0
        updated = load_bindings(bindings)
        assert updated is not None
        assert updated["root"] == "AGENTS.md"
        root_entry = next(
            entry
            for entry in updated["bindings"]
            if entry["source"] == "AGENTS.md"
        )
        assert root_entry["destinations"] == ["AGENTS.md"]

    def test_missing_root_without_override_returns_drift(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        _write_file(source, "AGENTS.md", ROOT_MARKED)
        (source / CLEARANCE).write_text(
            json.dumps(_clearance_document(skill_root=False)) + "\n",
            encoding="utf-8",
        )
        destination = tmp_path / "destination"
        destination.mkdir()
        bindings = tmp_path / "bindings.yaml"

        code = main(_init_args(source, destination, bindings))

        assert code == 1

    def test_explicit_root_override_routes_root_source(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        _write_file(source, "AGENTS.md", ROOT_MARKED)
        (source / CLEARANCE).write_text(
            json.dumps(_clearance_document(skill_root=False)) + "\n",
            encoding="utf-8",
        )
        destination = tmp_path / "destination"
        destination.mkdir()
        (destination / "CLAUDE.md").write_text(_destination_root(), encoding="utf-8")
        bindings = tmp_path / "bindings.yaml"

        code = main(
            [
                *_init_args(source, destination, bindings),
                "--root", "CLAUDE.md",
            ]
        )

        assert code == 0
        updated = load_bindings(bindings)
        assert updated is not None
        assert updated["root"] == "CLAUDE.md"


class BindClearedSkillRootTests:
    """Files under a cleared skill root enroll automatically; caches never ship."""

    def test_skill_root_enrolls_subset_region_and_default_raw_files(
        self, tmp_path: Path
    ) -> None:
        source = _source_with_skill_root(tmp_path)
        destination = tmp_path / "destination"
        destination.mkdir()
        (destination / "AGENTS.md").write_text(_destination_root(), encoding="utf-8")
        bindings = tmp_path / "bindings.yaml"

        code = main(_init_args(source, destination, bindings))

        assert code == 0
        skill_path = destination / (SKILL_ROOT + "SKILL.md")
        note_path = destination / (SKILL_ROOT + "note.md")
        skill_text = skill_path.read_text(encoding="utf-8")
        assert "<!-- core:begin -->\nSkill core\n<!-- core:end -->" in skill_text
        assert "<!-- project:begin -->" in skill_text
        assert note_path.read_bytes() == NOTE_BYTES
        assert not (destination / (SKILL_ROOT + "__pycache__")).exists()
        updated = load_bindings(bindings)
        assert updated is not None
        assert {entry["source"] for entry in updated["bindings"]} == {
            "AGENTS.md",
            SKILL_ROOT + "SKILL.md",
            SKILL_ROOT + "note.md",
        }

    def test_new_file_under_skill_root_joins_next_enrollment(
        self, tmp_path: Path
    ) -> None:
        source = _source_with_skill_root(tmp_path)
        destination = tmp_path / "destination"
        destination.mkdir()
        (destination / "AGENTS.md").write_text(_destination_root(), encoding="utf-8")
        bindings = tmp_path / "bindings.yaml"
        assert main(_init_args(source, destination, bindings)) == 0

        _write_payload(source, SKILL_ROOT + "extra.md", EXTRA_BYTES)

        assert main(_init_args(source, destination, bindings)) == 0
        extra_path = destination / (SKILL_ROOT + "extra.md")
        assert extra_path.read_bytes() == EXTRA_BYTES
        updated = load_bindings(bindings)
        assert updated is not None
        assert {entry["source"] for entry in updated["bindings"]} == {
            "AGENTS.md",
            SKILL_ROOT + "SKILL.md",
            SKILL_ROOT + "note.md",
            SKILL_ROOT + "extra.md",
        }
