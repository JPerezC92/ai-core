"""Behavior tests for stale raw-bound pending paths in `check`."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    RAW_SOURCE_BYTES,
    REV_A,
    ROOT_TEXT,
    SOURCE_MARKED,
    _binding_entry,
    _bindings_with_entries,
    _check_args,
    _write_bytes_file,
    _write_file,
)
from core_sync_pkg.domain.constants import RECONCILE_BEGIN  # noqa: E402
from core_sync_pkg.domain.reconciliation import (  # noqa: E402
    reconciliation_report_path,
    sync_reconciliation_blocker,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import save_bindings  # noqa: E402


class StaleRawPendingCheckTests:
    """Reject stale raw-bound pending paths without mutating project state."""

    def _setup(
        self,
        tmp_path: Path,
        *,
        pending: list[str],
        pinned: str = REV_A,
        preexisting_raw_block: bool = False,
    ) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", SOURCE_MARKED)
        _write_bytes_file(source, "opencode.jsonc", RAW_SOURCE_BYTES)
        _write_bytes_file(destination, "opencode.jsonc", RAW_SOURCE_BYTES)
        root_text = ROOT_TEXT
        if preexisting_raw_block:
            root_text = sync_reconciliation_blocker(
                root_text, ["opencode.jsonc"]
            )
        _write_file(destination, "AGENTS.md", root_text)

        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_with_entries(
                pinned,
                [
                    _binding_entry("agent.md", ["agent.md"], "region"),
                    _binding_entry("opencode.jsonc", ["opencode.jsonc"], "raw"),
                ],
                pending,
                root="AGENTS.md",
            ),
        )
        return source, destination, bindings_path

    def test_check_rejects_raw_pending_without_mutation_or_reconciliation(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        source, destination, bindings_path = self._setup(
            tmp_path,
            pending=["opencode.jsonc"],
            preexisting_raw_block=True,
        )
        bindings_before = bindings_path.read_text(encoding="utf-8")

        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1

        diagnostic = capsys.readouterr().err
        assert "stale raw-bound pending paths" in diagnostic
        assert "opencode.jsonc" in diagnostic
        assert "run apply or init" in diagnostic
        assert bindings_path.read_text(encoding="utf-8") == bindings_before
        assert not reconciliation_report_path(bindings_path).exists()
        root_text = (destination / "AGENTS.md").read_text(encoding="utf-8")
        assert RECONCILE_BEGIN not in root_text
        assert root_text == ROOT_TEXT
