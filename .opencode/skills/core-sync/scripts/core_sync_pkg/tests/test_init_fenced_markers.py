"""Behavior tests for fenced marker-looking destination enrollment in `init`."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    REV_A,
    REV_B,
    SOURCE_NO_MARKERS,
    _bindings_document,
    _init_args,
    _write_file,
)
from core_sync_pkg.domain.constants import EXIT_OK  # noqa: E402
from core_sync_pkg.domain.regions import split_regions  # noqa: E402
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import save_bindings  # noqa: E402


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
        save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["agent.md"]),
        )

        result = main(_init_args(source, destination, bindings_path, REV_A))

        assert result == EXIT_OK
        content = destination_path.read_text(encoding="utf-8")
        split = split_regions(content)
        assert split is not None
        assert split["region"] == "\nCore body one\nCore body two\n"
        assert "```markdown\n<!-- core:begin -->\n<!-- core:end -->\n```\n" in split[
            "after"
        ]
