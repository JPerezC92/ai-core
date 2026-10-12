"""Behavior tests for invalid bindings passed to region-mode `init`."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    DEST_PLAIN,
    REV_A,
    REV_B,
    SOURCE_NO_MARKERS,
    _init_args,
    _write_file,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402


class InitInvalidBindingsTests:
    """Verify malformed bindings are rejected before `init` changes targets."""

    def test_init_malformed_bindings_returns_two_without_writing_targets(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_NO_MARKERS)
        destination_path = _write_file(destination, "agent.md", DEST_PLAIN)
        root_path = _write_file(
            destination, "CLAUDE.md", "# Root remains unchanged\n"
        )
        bindings_path = tmp_path / "bindings.yaml"
        bindings_path.write_text(
            "schema: 2\ncore_revision: "
            + REV_B
            + "\nroot: CLAUDE.md\nbindings: []\npending: []\n",
            encoding="utf-8",
        )
        report_path = _write_file(
            tmp_path,
            "reconciliation/init.yaml",
            "Existing report remains unchanged\n",
        )
        unchanged = {
            destination_path: destination_path.read_bytes(),
            bindings_path: bindings_path.read_bytes(),
            root_path: root_path.read_bytes(),
            report_path: report_path.read_bytes(),
        }

        assert main(_init_args(source, destination, bindings_path, REV_A)) == 2
        assert {path: path.read_bytes() for path in unchanged} == unchanged
