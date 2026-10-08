"""Behavior tests preventing bindings and symlink writes into the source tree."""

from __future__ import annotations

from pathlib import Path

import pytest

from _core_sync_testkit import (
    DEST_MARKED,
    DEST_PLAIN,
    REV_A,
    SOURCE_MARKED,
    _apply_args,
    _bindings_document,
    _check_args,
    _init_args,
    _write_file,
    uc,
)


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
        return uc.main(args)

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
        uc.save_bindings(
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

        assert result == uc.EXIT_INVALID
        assert self._snapshot(*unchanged) == unchanged

    @pytest.mark.parametrize("command", ("apply", "init"))
    def test_rejects_destination_bindings_symlink_into_source_before_writing(
        self, tmp_path: Path, command: str
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        source_path = _write_file(source, "agent.md", SOURCE_MARKED)
        destination_path = _write_file(destination, "agent.md", DEST_MARKED)
        root_path = _write_file(destination, "CLAUDE.md", "# Root unchanged\n")
        bindings_target = source / "bindings.yaml"
        uc.save_bindings(
            bindings_target,
            _bindings_document(REV_A, "agent.md", ["agent.md"], root="CLAUDE.md"),
        )
        bindings_path = destination / "bindings.yaml"
        bindings_path.symlink_to(bindings_target)
        report_path = _write_file(
            destination, "reconciliation/init.yaml", "report unchanged\n"
        )
        unchanged = self._snapshot(
            source_path,
            destination_path,
            root_path,
            bindings_target,
            bindings_path,
            report_path,
        )

        result = self._run(command, source, destination, bindings_path)

        assert result == uc.EXIT_INVALID
        assert bindings_path.is_symlink()
        assert bindings_path.resolve() == bindings_target.resolve()
        assert self._snapshot(*unchanged) == unchanged

    @pytest.mark.parametrize("command", ("apply", "init"))
    def test_rejects_destination_payload_symlink_into_source(
        self, tmp_path: Path, command: str
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        source_path = _write_file(source, "agent.md", SOURCE_MARKED)
        payload_target = _write_file(source, "protected.md", DEST_MARKED)
        destination.mkdir(parents=True)
        payload_path = destination / "agent.md"
        payload_path.symlink_to(payload_target)
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
            source_path,
            payload_target,
            payload_path,
            root_path,
            bindings_path,
            report_path,
        )

        result = self._run(command, source, destination, bindings_path)

        assert result == uc.EXIT_INVALID
        assert payload_path.is_symlink()
        assert self._snapshot(*unchanged) == unchanged

    @pytest.mark.parametrize("command", ("check", "apply", "init"))
    def test_rejects_root_blocker_symlink_into_source(
        self, tmp_path: Path, command: str
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        source_path = _write_file(source, "agent.md", SOURCE_MARKED)
        root_target = _write_file(
            source, "protected-root.md", "# Source root unchanged\n"
        )
        destination_path = _write_file(destination, "agent.md", DEST_MARKED)
        root_path = destination / "CLAUDE.md"
        root_path.symlink_to(root_target)
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
        report_path = _write_file(
            tmp_path, "reconciliation/init.yaml", "report unchanged\n"
        )
        unchanged = self._snapshot(
            source_path,
            root_target,
            destination_path,
            root_path,
            bindings_path,
            report_path,
        )

        result = self._run(command, source, destination, bindings_path)

        assert result == uc.EXIT_INVALID
        assert root_path.is_symlink()
        assert self._snapshot(*unchanged) == unchanged

    def test_init_rejects_report_symlink_into_source_before_writing(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        source_path = _write_file(source, "agent.md", SOURCE_MARKED)
        report_target = _write_file(
            source, "protected-report.yaml", "source unchanged\n"
        )
        destination_path = _write_file(destination, "agent.md", DEST_PLAIN)
        root_path = _write_file(destination, "CLAUDE.md", "# Root unchanged\n")
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_A, "agent.md", ["agent.md"], root="CLAUDE.md"),
        )
        report_path = tmp_path / "reconciliation" / "init.yaml"
        report_path.parent.mkdir(parents=True)
        report_path.symlink_to(report_target)
        unchanged = self._snapshot(
            source_path,
            report_target,
            destination_path,
            root_path,
            bindings_path,
            report_path,
        )

        result = uc.main(_init_args(source, destination, bindings_path, REV_A))

        assert result == uc.EXIT_INVALID
        assert report_path.is_symlink()
        assert self._snapshot(*unchanged) == unchanged
