"""Behavior tests for the region-mode `init` contract.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_init.py
"""

from __future__ import annotations

from pathlib import Path

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
        uc.save_bindings(
            bindings_path,
            _bindings_document(pinned, "agent.md", ["agent.md"]),
        )
        return source, destination, bindings_path

    def test_init_generates_both_regions_and_wraps_old_body(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = self._setup(tmp_path)

        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 0

        content = (destination / "agent.md").read_text(encoding="utf-8")
        assert content.startswith("---\nname: dest\n---\n<!-- core:begin -->\n")
        split = uc.split_regions(content)
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

        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 0

        content = (destination / "agent.md").read_text(encoding="utf-8")
        lines = content.splitlines()
        end_index = lines.index(uc.END)
        begin_index = lines.index(uc.PROJECT_BEGIN)
        assert lines[end_index + 1] == ""
        assert begin_index == end_index + 2
        assert "<!-- core:end -->\n\n<!-- project:begin -->" in content
        assert "<!-- core:end -->\n\n\n<!-- project:begin -->" not in content

        split = uc.split_regions(content)
        assert split is not None
        assert split["region"] == "\nCore body one\nCore body two\n"
        assert split["after"].startswith("\n<!-- project:begin -->\n")
        project_body = content.split("<!-- project:begin -->\n", 1)[1].split(
            "<!-- project:end -->", 1
        )[0]
        assert project_body == "\n# Old title\n\nOld body line\n"
