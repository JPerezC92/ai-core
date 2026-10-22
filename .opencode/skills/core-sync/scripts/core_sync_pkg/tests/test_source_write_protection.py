"""Behavior tests preventing bindings and aliased writes into the source tree."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    DEST_MARKED,
    DEST_PLAIN,
    REV_A,
    SOURCE_MARKED,
    _apply_args,
    _bindings_document,
    _check_args,
    _init_args,
    _write_file,
)
from core_sync_pkg.domain.constants import EXIT_INVALID  # noqa: E402
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import save_bindings  # noqa: E402


class SourceWriteProtectionTests:
    """Verify no binding, payload, root, or report target can write into source."""

    def _run(
        self, command: str, source: Path, destination: Path, bindings: Path
    ) -> int:
        argument_builders = {
            "check": _check_args,
            "apply": _apply_args,
            "init": _init_args,
        }
        args = argument_builders[command](source, destination, bindings, REV_A)
        return main(args)

    def _snapshot(self, *paths: Path) -> dict[Path, bytes]:
        return {path: path.read_bytes() for path in paths}

    @pytest.mark.parametrize("command", ("apply", "init"))
    def test_rejects_bindings_file_under_source_before_writing(
        self, tmp_path: Path, command: str
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        source_path = _write_file(source, "agent.md", SOURCE_MARKED)
        destination_path = _write_file(destination, "agent.md", DEST_MARKED)
        root_path = _write_file(destination, "CLAUDE.md", "# Root unchanged\n")
        bindings_path = source / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_A, "agent.md", ["agent.md"], root="CLAUDE.md"),
        )
        report_path = _write_file(
            source, "reconciliation/init.yaml", "report unchanged\n"
        )
        unchanged = self._snapshot(
            source_path, destination_path, root_path, bindings_path, report_path
        )

        result = self._run(command, source, destination, bindings_path)

        assert result == EXIT_INVALID
        assert self._snapshot(*unchanged) == unchanged

    @pytest.mark.parametrize("command", ("apply", "init"))
    def test_rejects_symlinked_bindings_path_before_load(
        self, tmp_path: Path, command: str
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", DEST_MARKED)
        _write_file(destination, "CLAUDE.md", "# Root unchanged\n")
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_A, "agent.md", ["agent.md"], root="CLAUDE.md"),
        )
        original = Path.is_symlink

        def stub_is_symlink(self: Path) -> bool:
            if self == bindings_path:
                return True
            return original(self)

        with patch.object(Path, "is_symlink", stub_is_symlink), patch(
            "core_sync_pkg.infrastructure.composition.YamlBindingsStore.load"
        ) as load:
            result = self._run(command, source, destination, bindings_path)

        assert result == EXIT_INVALID
        load.assert_not_called()

    def test_hard_link_target_to_source_file_rejected_without_writes(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        source_path = _write_file(source, "agent.md", SOURCE_MARKED)
        destination.mkdir(parents=True)
        hard_link_path = destination / "agent.md"
        hard_link_path.hardlink_to(source_path)
        other_destination_path = _write_file(destination, "other.md", DEST_PLAIN)
        root_path = _write_file(destination, "CLAUDE.md", "# Root unchanged\n")
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(
                REV_A,
                "agent.md",
                ["agent.md", "other.md"],
                root="CLAUDE.md",
            ),
        )
        report_path = _write_file(
            tmp_path, "reconciliation/init.yaml", "report unchanged\n"
        )
        unchanged = self._snapshot(
            source_path,
            hard_link_path,
            other_destination_path,
            root_path,
            bindings_path,
            report_path,
        )

        result = self._run("init", source, destination, bindings_path)

        assert result == EXIT_INVALID
        assert hard_link_path.stat().st_ino == source_path.stat().st_ino
        assert self._snapshot(*unchanged) == unchanged

    def test_nested_source_hard_link_target_rejected_without_writes(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        source_path = _write_file(source, "nested/agent.md", SOURCE_MARKED)
        destination.mkdir(parents=True)
        hard_link_path = destination / "agent.md"
        hard_link_path.hardlink_to(source_path)
        root_path = _write_file(destination, "CLAUDE.md", "# Root unchanged\n")
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(
                REV_A,
                "nested/agent.md",
                ["agent.md"],
                root="CLAUDE.md",
            ),
        )
        report_path = _write_file(
            tmp_path, "reconciliation/init.yaml", "report unchanged\n"
        )
        unchanged = self._snapshot(
            source_path, hard_link_path, root_path, bindings_path, report_path
        )

        result = self._run("init", source, destination, bindings_path)

        assert result == EXIT_INVALID
        assert hard_link_path.stat().st_ino == source_path.stat().st_ino
        assert self._snapshot(*unchanged) == unchanged
