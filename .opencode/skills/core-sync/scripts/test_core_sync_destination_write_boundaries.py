"""Behavior tests keeping destination writes within its resolved root."""

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


class DestinationWriteBoundariesTests:
    """Verify destination payload and root writes cannot escape the root."""

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

    @pytest.mark.parametrize("command", ("apply", "init"))
    def test_rejects_destination_payload_symlink_escaping_destination(
        self, tmp_path: Path, command: str
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        outside = tmp_path / "outside"
        source_path = _write_file(source, "agent.md", SOURCE_MARKED)
        outside_payload = _write_file(outside, "payload.md", DEST_MARKED)
        destination.mkdir(parents=True)
        payload_path = destination / "agent.md"
        payload_path.symlink_to(outside_payload)
        root_path = _write_file(destination, "CLAUDE.md", "# Root unchanged\n")
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_A, "agent.md", ["agent.md"], root="CLAUDE.md"),
        )
        unchanged = self._snapshot(
            source_path, outside_payload, payload_path, root_path, bindings_path
        )

        result = self._run(command, source, destination, bindings_path)

        assert result == uc.EXIT_INVALID
        assert payload_path.is_symlink()
        assert self._snapshot(*unchanged) == unchanged

    @pytest.mark.parametrize("command", ("check", "apply", "init"))
    def test_rejects_root_blocker_symlink_escaping_destination(
        self, tmp_path: Path, command: str
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        outside = tmp_path / "outside"
        source_path = _write_file(source, "agent.md", SOURCE_MARKED)
        destination_path = _write_file(destination, "agent.md", DEST_MARKED)
        outside_root = _write_file(outside, "root.md", "# Outside root unchanged\n")
        root_path = destination / "CLAUDE.md"
        root_path.symlink_to(outside_root)
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(
                REV_A,
                "agent.md",
                ["agent.md"],
                pending=["agent.md"],
                root="CLAUDE.md",
            ),
        )
        unchanged = self._snapshot(
            source_path, destination_path, outside_root, root_path, bindings_path
        )

        result = self._run(command, source, destination, bindings_path)

        assert result == uc.EXIT_INVALID
        assert root_path.is_symlink()
        assert self._snapshot(*unchanged) == unchanged

    def test_duplicate_resolved_destinations_rejected_before_writes(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        source_path = _write_file(source, "agent.md", SOURCE_MARKED)
        real_destination = _write_file(destination, "real.md", DEST_MARKED)
        alias_destination = destination / "alias.md"
        alias_destination.symlink_to(real_destination)
        root_path = _write_file(destination, "CLAUDE.md", "# Root unchanged\n")
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(
                REV_A,
                "agent.md",
                ["real.md", "alias.md"],
                pending=["real.md"],
                root="CLAUDE.md",
            ),
        )
        unchanged = self._snapshot(
            source_path,
            real_destination,
            alias_destination,
            root_path,
            bindings_path,
        )

        result = self._run("apply", source, destination, bindings_path)

        assert result == uc.EXIT_INVALID
        assert alias_destination.is_symlink()
        assert alias_destination.resolve() == real_destination.resolve()
        assert self._snapshot(*unchanged) == unchanged
