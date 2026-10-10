"""Tests for reconciliation-blocker state transitions."""

from __future__ import annotations

from _core_sync_testkit import ROOT_TEXT, uc


def _exact_marker_line_count(text: str, marker: str) -> int:
    """Count lines whose stripped content equals the marker exactly."""
    return sum(1 for line in text.splitlines() if line.strip() == marker)


class ReconcileBlockerLifecycleTests:
    def test_block_appended_when_pending_nonempty(self) -> None:
        result = uc.sync_reconciliation_blocker(ROOT_TEXT, ["a.md"])
        assert result == (
            ROOT_TEXT
            + "\n"
            + uc.RECONCILE_BEGIN
            + "\n"
            + uc.RECONCILE_BODY
            + "\n"
            + uc.RECONCILE_END
            + "\n"
        )
        assert _exact_marker_line_count(result, uc.RECONCILE_BEGIN) == 1
        assert _exact_marker_line_count(result, uc.RECONCILE_END) == 1
        assert uc.find_reconcile_block(result.splitlines(keepends=True)) is not None

    def test_block_updated_in_place_on_rerun(self) -> None:
        first = uc.sync_reconciliation_blocker(ROOT_TEXT, ["a.md"])
        stale = first.replace(uc.RECONCILE_BODY, "STALE BODY")
        assert "STALE BODY" in stale
        repaired = uc.sync_reconciliation_blocker(stale, ["a.md", "b.md"])
        assert repaired == first
        assert "STALE BODY" not in repaired
        assert _exact_marker_line_count(repaired, uc.RECONCILE_BEGIN) == 1
        assert _exact_marker_line_count(repaired, uc.RECONCILE_END) == 1

    def test_block_removed_when_pending_empty(self) -> None:
        blocked = uc.sync_reconciliation_blocker(ROOT_TEXT, ["a.md"])
        assert uc.sync_reconciliation_blocker(blocked, []) == ROOT_TEXT

    def test_removal_is_noop_without_block(self) -> None:
        assert uc.sync_reconciliation_blocker(ROOT_TEXT, []) == ROOT_TEXT

    def test_idempotent_add_and_remove(self) -> None:
        once = uc.sync_reconciliation_blocker(ROOT_TEXT, ["a.md"])
        assert uc.sync_reconciliation_blocker(once, ["a.md"]) == once
        second = uc.sync_reconciliation_blocker(
            uc.sync_reconciliation_blocker(once, []), []
        )
        assert second == ROOT_TEXT
