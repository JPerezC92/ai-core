"""Behavior tests for fenced marker-looking destination enrollment in `init`."""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import (
    REV_A,
    REV_B,
    SOURCE_NO_MARKERS,
    _bindings_document,
    _init_args,
    _write_file,
    uc,
)


class InitFencedMarkerTests:
    def test_marker_looking_lines_inside_fences_enroll_as_markerless_content(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_NO_MARKERS)
        destination_path = _write_file(
            destination,
            "agent.md",
            "# Existing content\n\n```markdown\n"
            "<!-- core:begin -->\n<!-- core:end -->\n```\n",
        )
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["agent.md"]),
        )

        result = uc.main(_init_args(source, destination, bindings_path, REV_A))

        assert result == uc.EXIT_OK
        content = destination_path.read_text(encoding="utf-8")
        split = uc.split_regions(content)
        assert split is not None
        assert split["region"] == "\nCore body one\nCore body two\n"
        assert "```markdown\n<!-- core:begin -->\n<!-- core:end -->\n```\n" in split[
            "after"
        ]
