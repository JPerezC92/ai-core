"""End-to-end tests for `init --bind-cleared` bulk and merge enrollment."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    MERGE_DESTINATION,
    MERGE_SOURCE,
    REV_A,
    _cleared_source,
    _destination_root,
    _write_bytes_file,
    _write_file,
)
from core_sync_pkg.domain.jsonc import parse_object  # noqa: E402
from core_sync_pkg.domain.reconciliation import (  # noqa: E402
    reconciliation_report_path,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import load_bindings  # noqa: E402


class BindClearedBulkEnrollmentTests:
    """`init --bind-cleared` enrolls every cleared source; merge sources merge."""

    def test_bulk_enrollment_creates_region_and_raw_targets(
        self, tmp_path: Path
    ) -> None:
        source = _cleared_source(
            tmp_path,
            raw_payloads={
                ".opencode/skills/foo/note.md": b"note bytes\n",
                "opencode.jsonc": b"{\n}\n",
            },
        )
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
        created = (destination / ".opencode/agents/atrium.md").read_text(
            encoding="utf-8"
        )
        # S1 entry point: a created region target leads with the source
        # document's frontmatter, ahead of the core begin marker.
        assert created.startswith(
            "---\nname: atrium\nversion: 1.0.0\n---\n<!-- core:begin -->\n"
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
        # The existing destination is merged, never overwritten: its own comment
        # and its destination-only key survive while the source keys win.
        assert "// destination-only comment" in written
        assert parse_object(written) == {
            "theme": "dark",
            "shared": "source",
            "custom": 42,
        }
        updated = load_bindings(bindings)
        assert updated is not None
        assert updated["pending"] == []
        assert not reconciliation_report_path(bindings).exists()
