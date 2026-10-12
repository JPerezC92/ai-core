"""Behavior tests for concise filesystem-error reporting."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    REV_A,
    _apply_args,
    _check_args,
    _raw_setup,
    _region_fixture,
)
from core_sync_pkg.infrastructure import filesystem as core_sync_filesystem  # noqa: E402
from core_sync_pkg.infrastructure.composition import main  # noqa: E402


class FilesystemErrorTests:
    def test_raw_write_error_returns_drift_without_traceback(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        source, destination, bindings_path = _raw_setup(
            tmp_path, destination_content=b"stale\n"
        )

        def fail_write_bytes(path: Path, content: bytes) -> int:
            raise OSError("raw target denied")

        monkeypatch.setattr(Path, "write_bytes", fail_write_bytes)

        result = main(_apply_args(source, destination, bindings_path, REV_A))

        captured = capsys.readouterr()
        assert result == 1
        assert captured.err == "core-sync I/O error: raw target denied\n"
        assert "Traceback" not in captured.err

    def test_blocker_write_error_returns_drift_without_traceback(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        source, destination, bindings_path = _region_fixture(
            tmp_path,
            pending=["agent.md"],
            root=None,
            root_file="CLAUDE.md",
        )
        root_path = destination / "CLAUDE.md"
        write_text = core_sync_filesystem.write_text

        def fail_blocker_write(path: Path, content: str) -> None:
            if path == root_path:
                raise OSError("blocker target denied")
            write_text(path, content)

        monkeypatch.setattr(core_sync_filesystem, "write_text", fail_blocker_write)

        result = main(_check_args(source, destination, bindings_path, REV_A))

        captured = capsys.readouterr()
        assert result == 1
        assert captured.err == "core-sync I/O error: blocker target denied\n"
        assert "Traceback" not in captured.err
