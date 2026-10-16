"""End-to-end tests for `init --bind-cleared` bulk and merge enrollment."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import NotRequired, TypedDict

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    MERGE_DESTINATION,
    MERGE_SOURCE,
    REV_A,
    _write_bytes_file,
    _write_file,
)
from core_sync_pkg.domain.constants import CLEARANCE_SCHEMA  # noqa: E402
from core_sync_pkg.domain.jsonc import parse_object  # noqa: E402
from core_sync_pkg.domain.reconciliation import (  # noqa: E402
    reconciliation_report_path,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import load_bindings  # noqa: E402

CLEARANCE = "distribution-clearance.json"
AGENT_MARKED = (
    "---\nname: atrium\nversion: 1.0.0\n---\n"
    "<!-- core:begin -->\nAgent core\n<!-- core:end -->\n"
)
ROOT_MARKED = (
    "---\nname: agents\n---\n"
    "<!-- core:begin -->\nRoot core\n<!-- core:end -->\n"
)


class FileRecordShape(TypedDict):
    """Well-formed cleared file record as written by fixture sources."""

    mode: str
    role: NotRequired[str]


class ClearanceDocument(TypedDict):
    """Well-formed version-1 clearance document maintained by fixtures."""

    schema: int
    cleared: dict[str, FileRecordShape]


def _clearance_document() -> ClearanceDocument:
    """Build the fixture source's typed version-1 clearance document."""
    return {
        "schema": CLEARANCE_SCHEMA,
        "cleared": {
            ".opencode/agents/atrium.md": {"mode": "region"},
            ".opencode/skills/foo/note.md": {"mode": "raw"},
            "opencode.jsonc": {"mode": "raw"},
            "AGENTS.md": {"mode": "region", "role": "root"},
        },
    }


def _destination_root() -> str:
    """Build one destination instruction-root file body."""
    return "---\nname: dest\n---\n# Dest\n"


def _source_with_clearance(tmp_path: Path) -> Path:
    """Build the fixture source tree with its clearance document."""
    source = tmp_path / "source"
    _write_file(source, ".opencode/agents/atrium.md", AGENT_MARKED)
    _write_bytes_file(source, ".opencode/skills/foo/note.md", b"note bytes\n")
    _write_bytes_file(source, "opencode.jsonc", b"{\n}\n")
    _write_file(source, "AGENTS.md", ROOT_MARKED)
    (source / CLEARANCE).write_text(
        json.dumps(_clearance_document()) + "\n",
        encoding="utf-8",
    )
    return source


class BindClearedBulkEnrollmentTests:
    """`init --bind-cleared` enrolls every cleared source; merge sources merge."""

    def test_bulk_enrollment_creates_region_and_raw_targets(
        self, tmp_path: Path
    ) -> None:
        source = _source_with_clearance(tmp_path)
        destination = tmp_path / "destination"
        destination.mkdir()
        (destination / "AGENTS.md").write_text(_destination_root(), encoding="utf-8")
        bindings = tmp_path / "bindings.yaml"

        code = main(
            [
                "init",
                "--source", str(source),
                "--destination", str(destination),
                "--bindings", str(bindings),
                "--source-revision", REV_A,
                "--bind-cleared",
            ]
        )

        assert code == 0
        assert (destination / ".opencode/agents/atrium.md").read_text(
            encoding="utf-8"
        )
        assert (destination / "opencode.jsonc").read_bytes() == b"{\n}\n"
        assert (destination / ".opencode/skills/foo").is_dir()
        assert (destination / ".opencode/skills/foo/note.md").read_bytes() == (
            b"note bytes\n"
        )
        assert bindings.is_file()
        updated = load_bindings(bindings)
        assert updated is not None
        assert {entry["source"] for entry in updated["bindings"]} == {
            "AGENTS.md",
            ".opencode/agents/atrium.md",
            ".opencode/skills/foo/note.md",
            "opencode.jsonc",
        }

    def test_cleared_merge_source_enrolled_in_bulk(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_bytes_file(
            source, "opencode.jsonc", MERGE_SOURCE.encode(), mode="merge"
        )
        _write_file(destination, "opencode.jsonc", MERGE_DESTINATION)
        bindings = tmp_path / "bindings.yaml"

        code = main(
            [
                "init",
                "--source", str(source),
                "--destination", str(destination),
                "--bindings", str(bindings),
                "--source-revision", REV_A,
                "--bind-cleared",
            ]
        )

        assert code == 0
        written = (destination / "opencode.jsonc").read_text(encoding="utf-8")
        assert parse_object(written) == {
            "theme": "dark",
            "shared": "source",
            "custom": 42,
        }
        updated = load_bindings(bindings)
        assert updated is not None
        assert updated["pending"] == []
        assert not reconciliation_report_path(bindings).exists()
