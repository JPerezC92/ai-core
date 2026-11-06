"""End-to-end behavior test: an absent bound destination stays drift until repaired.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_recreate_absent_destination.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pytest  # noqa: E402

from _core_sync_testkit import (  # noqa: E402
    RAW_SOURCE_BYTES,
    REV_A,
    SOURCE_MARKED,
    created_region,
    _apply_args,
    _bindings_document,
    _check_args,
    _raw_setup,
    _write_file,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import save_bindings  # noqa: E402

CREATED_REGION = created_region(
    "---\nname: sample\n---\n",
    "\nCore body line one\nCore body line two\n",
)


class AbsentDestinationDriftAndRepairTests:
    """Report an absent bound destination as drift, then repair it with `apply`."""

    def test_region_destination_drifts_until_apply_recreates_it(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", SOURCE_MARKED)
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_A, "agent.md", ["agent.md", "created.md"]),
        )
        created_path = destination / "created.md"

        capsys.readouterr()
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1
        assert "missing destination" in capsys.readouterr().err

        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 0
        assert created_path.read_text(encoding="utf-8") == CREATED_REGION

        capsys.readouterr()
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 0
        assert capsys.readouterr().out == "current\n"

    def test_raw_destination_drifts_until_apply_recreates_it(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        source, destination, bindings_path = _raw_setup(
            tmp_path, destination_content=None
        )
        destination_path = destination / "opencode.jsonc"

        capsys.readouterr()
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1
        assert "missing destination" in capsys.readouterr().err

        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 0
        assert destination_path.read_bytes() == RAW_SOURCE_BYTES

        capsys.readouterr()
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 0
        assert capsys.readouterr().out == "current\n"
