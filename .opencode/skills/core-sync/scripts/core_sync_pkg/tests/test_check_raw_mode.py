"""Behavior tests for raw-mode `check`."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    REV_A,
    _check_args,
    _raw_setup,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402


class RawCheckTests:
    """Verify check compares raw-mode destination bytes to source bytes."""

    def test_check_current_when_bytes_equal(
        self, tmp_path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        source, destination, bindings_path = _raw_setup(tmp_path)
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 0
        assert capsys.readouterr().out == "current\n"

    def test_check_drift_when_bytes_differ(self, tmp_path) -> None:
        source, destination, bindings_path = _raw_setup(
            tmp_path, destination_content=b'{"other": true}\n'
        )
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1
