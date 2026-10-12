"""Behavior tests for region-mode `init` pending/report lifecycle."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    DEST_PLAIN,
    REV_A,
    REV_B,
    SOURCE_NO_MARKERS,
    _bindings_document,
    _init_args,
    _write_file,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import (  # noqa: E402
    load_bindings,
    save_bindings,
)


class InitPendingTests:
    """Verify `init` records reconciliation reports and pending paths."""

    def _setup(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_NO_MARKERS)
        _write_file(destination, "agent.md", DEST_PLAIN)
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["agent.md"]),
        )
        return source, destination, bindings_path

    def test_init_records_report_and_pending(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        source, destination, bindings_path = self._setup(tmp_path)

        assert main(_init_args(source, destination, bindings_path, REV_A)) == 0
        assert capsys.readouterr().out == "initialized\n"

        updated = load_bindings(bindings_path)
        assert updated is not None
        assert updated["pending"] == ["agent.md"]

        report_path = bindings_path.parent / "reconciliation" / "init.yaml"
        assert report_path.is_file()
        report = yaml.safe_load(report_path.read_text(encoding="utf-8"))
        assert report["core_revision"] == REV_A
        assert report["entries"] == [
            {"destination": "agent.md", "source": "agent.md", "action": "initialized"}
        ]
