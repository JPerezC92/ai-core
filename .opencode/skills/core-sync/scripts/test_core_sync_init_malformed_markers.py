"""Behavior tests for malformed-marker handling during region-mode `init`."""

from __future__ import annotations

from pathlib import Path

import pytest

from _core_sync_testkit import (
    DEST_PLAIN,
    REV_A,
    REV_B,
    SOURCE_NO_MARKERS,
    _bindings_document,
    _init_args,
    _write_file,
    uc,
)


class InitMalformedMarkerTests:
    @pytest.mark.parametrize(
        "destination_content",
        [
            "<!-- core:begin -->\nbody\n",
            "<!-- core:end -->\nbody\n",
            "<!-- core:begin -->\n<!-- core:end -->\n<!-- core:begin -->\n",
            "<!-- core:begin -->\nbody\n<!-- core:end -->\n<!-- core:end -->\n",
            "<!-- core:end -->\n<!-- core:begin -->\n",
        ],
        ids=(
            "missing-end",
            "missing-begin",
            "duplicate-begin",
            "duplicate-end",
            "reversed",
        ),
    )
    def test_init_rejects_malformed_markers_without_writing_any_target(
        self, tmp_path: Path, destination_content: str
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_NO_MARKERS)
        first_destination_path = _write_file(destination, "first.md", DEST_PLAIN)
        destination_path = _write_file(
            destination, "agent.md", destination_content
        )
        root_path = _write_file(
            destination, "CLAUDE.md", "# Root remains unchanged\n"
        )
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(
                REV_B,
                "agent.md",
                ["first.md", "agent.md"],
                root="CLAUDE.md",
            ),
        )
        report_path = _write_file(
            tmp_path, "reconciliation/init.yaml", "report remains unchanged\n"
        )
        unchanged = {
            first_destination_path: first_destination_path.read_bytes(),
            destination_path: destination_path.read_bytes(),
            root_path: root_path.read_bytes(),
            bindings_path: bindings_path.read_bytes(),
            report_path: report_path.read_bytes(),
        }

        result = uc.main(_init_args(source, destination, bindings_path, REV_A))

        assert result == uc.EXIT_INVALID
        assert {path: path.read_bytes() for path in unchanged} == unchanged
