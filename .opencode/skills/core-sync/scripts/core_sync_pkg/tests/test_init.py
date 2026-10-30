"""Behavior tests for the region-mode `init` contract.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_init.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    CRLF_DEST_PLAIN,
    CRLF_SOURCE_NO_MARKERS,
    DEST_PLAIN,
    REV_A,
    REV_B,
    SOURCE_NO_MARKERS,
    _bindings_document,
    _init_args,
    _write_file,
)
from core_sync_pkg.domain.constants import END, PROJECT_BEGIN  # noqa: E402
from core_sync_pkg.domain.regions import split_regions  # noqa: E402
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import save_bindings  # noqa: E402


class InitContractTests:
    """Verify markerless region enrollment and generated region spacing."""

    def _setup(
        self,
        tmp_path: Path,
        *,
        source_content: str = SOURCE_NO_MARKERS,
        destination_content: str = DEST_PLAIN,
        pinned: str = REV_B,
    ) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", source_content)
        _write_file(destination, "agent.md", destination_content)
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(pinned, "agent.md", ["agent.md"]),
        )
        return source, destination, bindings_path

    def test_init_generates_both_regions_and_wraps_old_body(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = self._setup(tmp_path)

        assert main(_init_args(source, destination, bindings_path, REV_A)) == 0

        content = (destination / "agent.md").read_text(encoding="utf-8")
        assert content.startswith("---\nname: dest\n---\n<!-- core:begin -->\n")
        split = split_regions(content)
        assert split is not None
        assert split["region"] == "\nCore body one\nCore body two\n"
        assert "<!-- project:begin -->\n" in content
        project_body = content.split("<!-- project:begin -->\n", 1)[1].split(
            "<!-- project:end -->", 1
        )[0]
        assert project_body == "\n# Old title\n\nOld body line\n"
        assert content.endswith("<!-- project:end -->\n")

    def test_init_separates_core_end_and_project_begin_with_one_blank_line(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = self._setup(tmp_path)

        assert main(_init_args(source, destination, bindings_path, REV_A)) == 0

        content = (destination / "agent.md").read_text(encoding="utf-8")
        lines = content.splitlines()
        end_index = lines.index(END)
        begin_index = lines.index(PROJECT_BEGIN)
        assert lines[end_index + 1] == ""
        assert begin_index == end_index + 2
        assert "<!-- core:end -->\n\n<!-- project:begin -->" in content
        assert "<!-- core:end -->\n\n\n<!-- project:begin -->" not in content

        split = split_regions(content)
        assert split is not None
        assert split["region"] == "\nCore body one\nCore body two\n"
        assert split["after"].startswith("\n<!-- project:begin -->\n")
        project_body = content.split("<!-- project:begin -->\n", 1)[1].split(
            "<!-- project:end -->", 1
        )[0]
        assert project_body == "\n# Old title\n\nOld body line\n"

    def test_init_writes_lf_only_output_from_crlf_inputs(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = self._setup(
            tmp_path,
            source_content=CRLF_SOURCE_NO_MARKERS,
            destination_content=CRLF_DEST_PLAIN,
        )

        assert main(_init_args(source, destination, bindings_path, REV_A)) == 0

        written = (destination / "agent.md").read_bytes()
        assert b"\r" not in written
        assert written == (
            b"---\n"
            b"name: dest\n"
            b"---\n"
            b"<!-- core:begin -->\n"
            b"\n"
            b"Core body one\n"
            b"Core body two\n"
            b"<!-- core:end -->\n"
            b"\n"
            b"<!-- project:begin -->\n"
            b"\n"
            b"# Old title\n"
            b"\n"
            b"Old body line\n"
            b"<!-- project:end -->\n"
        )
