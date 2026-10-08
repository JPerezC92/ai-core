"""Behavior tests for currentness and region drift in region-mode `check`."""

from __future__ import annotations

from pathlib import Path

import pytest

from _core_sync_testkit import (
    DEST_MARKED,
    REV_A,
    SOURCE_MARKED,
    _bindings_document,
    _check_args,
    _write_file,
    uc,
)


class CheckContractTests:
    """Verify current and drift statuses for region bindings."""

    def _setup(
        self,
        tmp_path: Path,
        *,
        destination_content: str = SOURCE_MARKED,
    ) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", destination_content)
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_A, "agent.md", ["agent.md"]),
        )
        return source, destination, bindings_path

    def test_current_returns_zero_and_prints_current(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 0
        assert capsys.readouterr().out == "current\n"

    def test_region_drift_returns_one(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(
            tmp_path, destination_content=DEST_MARKED
        )
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 1
