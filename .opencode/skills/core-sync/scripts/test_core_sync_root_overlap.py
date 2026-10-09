"""Behavior tests for rejecting overlapping source and destination roots."""

from __future__ import annotations

from pathlib import Path

import pytest

from _core_sync_testkit import (
    DEST_MARKED,
    REV_A,
    SOURCE_MARKED,
    _apply_args,
    _bindings_document,
    _check_args,
    _init_args,
    _write_file,
    uc,
)


class RootOverlapTests:
    """Verify root overlap is rejected without changing protected files."""

    def _run(
        self, command: str, source: Path, destination: Path, bindings: Path
    ) -> int:
        argument_builders = {
            "check": _check_args,
            "apply": _apply_args,
            "init": _init_args,
        }
        args = argument_builders[command](source, destination, bindings, REV_A)
        return uc.main(args)

    def _snapshot(self, *paths: Path) -> dict[Path, bytes]:
        return {path: path.read_bytes() for path in paths}

    @pytest.mark.parametrize("command", ("check", "apply", "init"))
    def test_rejects_overlapping_roots_before_writing(
        self, tmp_path: Path, command: str
    ) -> None:
        source = tmp_path / "source"
        destination = source / "destination"
        source_path = _write_file(source, "agent.md", SOURCE_MARKED)
        destination_path = _write_file(destination, "agent.md", DEST_MARKED)
        root_path = _write_file(destination, "CLAUDE.md", "# Root unchanged\n")
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_A, "agent.md", ["agent.md"], root="CLAUDE.md"),
        )
        report_path = _write_file(
            tmp_path, "reconciliation/init.yaml", "report unchanged\n"
        )
        unchanged = self._snapshot(
            source_path, destination_path, root_path, bindings_path, report_path
        )

        result = self._run(command, source, destination, bindings_path)

        assert result == uc.EXIT_INVALID
        assert self._snapshot(*unchanged) == unchanged
