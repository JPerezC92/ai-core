"""End-to-end tests for `init --bind-cleared` bulk enrollment and root detection."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest  # noqa: E402

from _core_sync_testkit import (  # noqa: E402
    REV_A,
    _write_bytes_file,
    _write_file,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402

CLEARANCE = "distribution-clearance.json"
AGENT_MARKED = (
    "---\nname: atrium\nversion: 1.0.0\n---\n"
    "<!-- core:begin -->\nAgent core\n<!-- core:end -->\n"
)
ROOT_MARKED = (
    "---\nname: agents\n---\n"
    "<!-- core:begin -->\nRoot core\n<!-- core:end -->\n"
)


def _source_with_clearance(tmp_path: Path) -> Path:
    source = tmp_path / "source"
    _write_file(source, ".opencode/agents/atrium.md", AGENT_MARKED)
    _write_bytes_file(source, "opencode.jsonc", b"{\n}\n")
    _write_file(source, "AGENTS.md", ROOT_MARKED)
    (source / CLEARANCE).write_text(
        json.dumps(
            {
                "schema": 2,
                "cleared": {
                    ".opencode/agents/atrium.md": {"mode": "region"},
                    "opencode.jsonc": {"mode": "raw"},
                    "AGENTS.md": {"mode": "region", "role": "root"},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )
    return source


class BindClearedEnrollmentTests:
    """`init --bind-cleared` enrolls every cleared source and detects the root."""

    def test_fresh_enrollment_creates_targets_and_detects_root(
        self, tmp_path: Path
    ) -> None:
        source = _source_with_clearance(tmp_path)
        destination = tmp_path / "destination"
        destination.mkdir()
        (destination / "AGENTS.md").write_text(
            "---\nname: dest\n---\n# Dest\n", encoding="utf-8"
        )
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
        assert bindings.is_file()
        assert "AGENTS.md" in bindings.read_text(encoding="utf-8")

    def test_missing_root_without_override_returns_drift(
        self, tmp_path: Path
    ) -> None:
        source = _source_with_clearance(tmp_path)
        destination = tmp_path / "destination"
        destination.mkdir()
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

        assert code == 1

    def test_explicit_root_override_routes_root_source(
        self, tmp_path: Path
    ) -> None:
        source = _source_with_clearance(tmp_path)
        destination = tmp_path / "destination"
        destination.mkdir()
        (destination / "CLAUDE.md").write_text(
            "---\nname: dest\n---\n# Dest\n", encoding="utf-8"
        )
        bindings = tmp_path / "bindings.yaml"

        code = main(
            [
                "init",
                "--source", str(source),
                "--destination", str(destination),
                "--bindings", str(bindings),
                "--source-revision", REV_A,
                "--bind-cleared",
                "--root", "CLAUDE.md",
            ]
        )

        assert code == 0
        assert "CLAUDE.md" in bindings.read_text(encoding="utf-8")
