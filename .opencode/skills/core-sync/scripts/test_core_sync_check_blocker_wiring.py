"""Behavior tests for reconciliation blocker wiring in `check`."""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import REV_A, _check_args, _region_fixture, uc


class CheckBlockerWiringTests:
    def test_check_writes_block_and_returns_one_when_pending(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = _region_fixture(
            tmp_path, pending=["agent.md"], root="CLAUDE.md", root_file="CLAUDE.md"
        )
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 1
        text = (destination / "CLAUDE.md").read_text(encoding="utf-8")
        assert uc.RECONCILE_BEGIN in text
        assert uc.RECONCILE_BODY in text

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
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 0
        text = (destination / "CLAUDE.md").read_text(encoding="utf-8")
        assert uc.RECONCILE_BEGIN not in text
        assert text == "# Root\n\nContent.\n"
