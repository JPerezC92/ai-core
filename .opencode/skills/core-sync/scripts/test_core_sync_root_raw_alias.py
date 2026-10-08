"""Behavior tests rejecting a root path that aliases a raw destination."""

from __future__ import annotations

from pathlib import Path

import pytest

from _core_sync_testkit import (
    DEST_MARKED,
    REV_A,
    SOURCE_MARKED,
    _apply_args,
    _binding_entry,
    _bindings_with_entries,
    _check_args,
    _init_args,
    _write_bytes_file,
    _write_file,
    uc,
)


class RootRawAliasTests:
    """Verify a root runtime file cannot alias a raw destination path."""

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
    def test_rejects_root_aliasing_raw_destination_before_writing(
        self, tmp_path: Path, command: str
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        source_raw_path = _write_bytes_file(
            source, "settings.jsonc", b'{"source": "unchanged"}\x00\n'
        )
        source_region_path = _write_file(source, "agent.md", SOURCE_MARKED)
        root_path = _write_bytes_file(
            destination, "CLAUDE.md", b"raw root target unchanged\x00\n"
        )
        raw_destination_path = destination / "settings.jsonc"
        raw_destination_path.symlink_to(root_path)
        other_destination_path = _write_file(destination, "agent.md", DEST_MARKED)
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_with_entries(
                REV_A,
                [
                    _binding_entry("settings.jsonc", ["settings.jsonc"], "raw"),
                    _binding_entry("agent.md", ["agent.md"]),
                ],
                pending=["agent.md"],
                root="CLAUDE.md",
            ),
        )
        report_path = _write_file(
            tmp_path, "reconciliation/init.yaml", "report unchanged\n"
        )
        unchanged = self._snapshot(
            source_raw_path,
            source_region_path,
            root_path,
            raw_destination_path,
            other_destination_path,
            bindings_path,
            report_path,
        )

        result = self._run(command, source, destination, bindings_path)

        assert result == uc.EXIT_INVALID
        assert raw_destination_path.is_symlink()
        assert self._snapshot(*unchanged) == unchanged
