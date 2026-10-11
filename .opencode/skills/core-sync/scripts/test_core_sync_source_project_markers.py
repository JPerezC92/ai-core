"""Behavior tests for project-marker validation on region-mode sources."""

from __future__ import annotations

from pathlib import Path

import pytest

from _core_sync_testkit import (
    DEST_MARKED,
    REV_A,
    _apply_args,
    _bindings_document,
    _check_args,
    _init_args,
    _write_file,
    uc,
)


PROJECT_ONLY_SOURCE = (
    "---\n"
    "name: sample\n"
    "---\n"
    "<!-- project:begin -->\n"
    "AICORE-ONLY source content\n"
    "<!-- project:end -->\n"
)


class SourceProjectMarkerTests:
    def test_extract_source_core_rejects_project_only_source(self) -> None:
        with pytest.raises(uc.MalformedSourceMarkers):
            uc.extract_source_core(PROJECT_ONLY_SOURCE)

    @pytest.mark.parametrize("command", ["check", "apply", "init"])
    def test_cleared_project_only_source_still_fails_marker_validation(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        command: str,
    ) -> None:
        source_dir = tmp_path / "source"
        destination_dir = tmp_path / "destination"
        source_path = _write_file(source_dir, "agent.md", PROJECT_ONLY_SOURCE)
        destination_path = _write_file(destination_dir, "agent.md", DEST_MARKED)
        root_path = _write_file(destination_dir, "root.md", "# Root runtime\n")

        bindings_path = tmp_path / ".aicore" / "core.yaml"
        bindings_path.parent.mkdir(parents=True, exist_ok=True)
        uc.save_bindings(
            bindings_path,
            _bindings_document(
                REV_A,
                "agent.md",
                ["agent.md"],
                pending=["agent.md"],
                root="root.md",
            ),
        )
        report_path = _write_file(
            tmp_path,
            ".aicore/reconciliation/init.yaml",
            "existing reconciliation report\n",
        )
        protected_paths = [destination_path, root_path, bindings_path, report_path]
        before = {path: path.read_bytes() for path in protected_paths}
        args_by_command = {
            "check": _check_args(
                source_dir, destination_dir, bindings_path, REV_A
            ),
            "apply": _apply_args(
                source_dir, destination_dir, bindings_path, REV_A
            ),
            "init": _init_args(
                source_dir, destination_dir, bindings_path, REV_A
            ),
        }

        assert uc.main(args_by_command[command]) == uc.EXIT_INVALID

        captured = capsys.readouterr()
        assert "invalid source markers" in captured.err
        assert str(source_path) in captured.err
        assert {path: path.read_bytes() for path in protected_paths} == before

    def test_source_with_both_pairs_returns_only_core_bytes(self) -> None:
        source = (
            "---\nname: sample\n---\n"
            "<!-- core:begin -->\nCORE-ONLY\n<!-- core:end -->\n"
            "<!-- project:begin -->\nAICORE-ONLY\n<!-- project:end -->\n"
        )

        assert uc.extract_source_core(source) == "CORE-ONLY\n"

    def test_source_with_neither_pair_still_returns_post_frontmatter_body(
        self,
    ) -> None:
        body = "\nMarkerless core line one\nMarkerless core line two\n"
        source = f"---\nname: sample\n---\n{body}"

        assert uc.extract_source_core(source) == body

    def test_project_marker_lines_inside_fenced_code_do_not_trigger_rejection(
        self,
    ) -> None:
        body = (
            "```markdown\n"
            "<!-- project:begin -->\n"
            "example only\n"
            "<!-- project:end -->\n"
            "```\n"
            "ordinary source body\n"
        )
        source = f"---\nname: sample\n---\n{body}"

        assert uc.extract_source_core(source) == body
