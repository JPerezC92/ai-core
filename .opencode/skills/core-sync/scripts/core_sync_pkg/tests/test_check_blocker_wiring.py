"""Behavior tests for reconciliation blocker wiring in `check`."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    REV_A,
    _check_args,
    _region_fixture,
)
from core_sync_pkg.domain.constants import (  # noqa: E402
    RECONCILE_BEGIN,
    RECONCILE_BODY,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402


class CheckBlockerWiringTests:
    def test_check_writes_block_and_returns_one_when_pending(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = _region_fixture(
            tmp_path, pending=["agent.md"], root="CLAUDE.md", root_file="CLAUDE.md"
        )
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1
        text = (destination / "CLAUDE.md").read_text(encoding="utf-8")
        assert RECONCILE_BEGIN in text
        assert RECONCILE_BODY in text

    def test_check_removes_block_and_returns_zero_when_pending_cleared(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = _region_fixture(
            tmp_path,
            pending=[],
            root="CLAUDE.md",
            root_file="CLAUDE.md",
            preexisting_block=True,
        )
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 0
        text = (destination / "CLAUDE.md").read_text(encoding="utf-8")
        assert RECONCILE_BEGIN not in text
        assert text == "# Root\n\nContent.\n"
