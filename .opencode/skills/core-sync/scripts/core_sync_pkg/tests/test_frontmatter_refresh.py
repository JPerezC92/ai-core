"""Behavior tests for frontmatter refresh across `check` and `apply`.

A stale identity key must make `check` drift, and `apply` must refresh it while
the destination-only `local-version` survives byte-identically.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_frontmatter_refresh.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    REV_A,
    _apply_args,
    _bindings_document,
    _check_args,
    _write_file,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import save_bindings  # noqa: E402

SOURCE_SKILL = (
    "---\n"
    "name: odd-workflow\n"
    "description: Current description.\n"
    "metadata:\n"
    "  version: 2.2.0\n"
    "---\n"
    "<!-- core:begin -->\n"
    "Core body\n"
    "<!-- core:end -->\n"
)

DESTINATION_SKILL = (
    "---\n"
    "name: odd-workflow\n"
    "description: Stale description.\n"
    "metadata:\n"
    "  version: 1.0.2\n"
    "  category: workflow\n"
    "local-version: 1.0.1\n"
    "---\n"
    "<!-- core:begin -->\n"
    "Core body\n"
    "<!-- core:end -->\n"
)

STYLED_DESTINATION_SKILL = (
    "---\n"
    "name: odd-workflow\n"
    "description: Current description.\n"
    "metadata:\n"
    "  version: 2.2.0\n"
    '  reviewed: "2026-11-05"\n'
    "local-version: '1.0.1'\n"
    "---\n"
    "<!-- core:begin -->\n"
    "Core body\n"
    "<!-- core:end -->\n"
)


def _declaring_line(document: str, prefix: str) -> str:
    """Return the exact line, terminator included, that starts with `prefix`."""
    for line in document.splitlines(keepends=True):
        if line.strip().startswith(prefix):
            return line
    raise AssertionError(f"no line starts with {prefix}")


class FrontmatterRefreshTests:
    """`check` and `apply` agree on the frontmatter a sync would write."""

    def _setup(
        self,
        tmp_path: Path,
        destination_content: str = DESTINATION_SKILL,
    ) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "SKILL.md", SOURCE_SKILL)
        _write_file(destination, "SKILL.md", destination_content)
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_A, "SKILL.md", ["SKILL.md"]),
        )
        return source, destination, bindings_path

    def test_check_reports_frontmatter_drift_for_a_stale_description(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        source, destination, bindings_path = self._setup(tmp_path)

        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1

        captured = capsys.readouterr()
        assert "frontmatter drift" in captured.err
        assert str(destination / "SKILL.md") in captured.err

    def test_apply_refreshes_the_identity_keys_and_keeps_local_version(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        source, destination, bindings_path = self._setup(tmp_path)

        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 0

        written = (destination / "SKILL.md").read_text(encoding="utf-8")
        assert "description: Current description.\n" in written
        assert "Stale description" not in written
        assert "  version: 2.2.0\n" in written
        assert "  category: workflow\n" in written
        assert _declaring_line(DESTINATION_SKILL, "local-version:") in (
            written.splitlines(keepends=True)
        )
        assert written.endswith(
            "<!-- core:begin -->\nCore body\n<!-- core:end -->\n"
        )
        capsys.readouterr()
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 0
        assert capsys.readouterr().out == "current\n"

    def test_check_is_current_when_untouched_keys_keep_another_style(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        # The destination's own keys use quoting the source never defines; a
        # merge that re-serialised them would report drift on a current file.
        source, destination, bindings_path = self._setup(
            tmp_path, STYLED_DESTINATION_SKILL
        )

        assert main(_check_args(source, destination, bindings_path, REV_A)) == 0

        assert capsys.readouterr().out == "current\n"
