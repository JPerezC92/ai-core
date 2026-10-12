"""Tests for reconciliation-blocker state transitions."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import ROOT_TEXT  # noqa: E402
from core_sync_pkg.domain.constants import (  # noqa: E402
    RECONCILE_BEGIN,
    RECONCILE_BODY,
    RECONCILE_END,
)
from core_sync_pkg.domain.reconciliation import (  # noqa: E402
    find_reconcile_block,
    sync_reconciliation_blocker,
)


def _exact_marker_line_count(text: str, marker: str) -> int:
    """Count lines whose stripped content equals the marker exactly."""
    return sum(1 for line in text.splitlines() if line.strip() == marker)


class ReconcileBlockerLifecycleTests:
    def test_block_appended_when_pending_nonempty(self) -> None:
        result = sync_reconciliation_blocker(ROOT_TEXT, ["a.md"])
        assert result == (
            ROOT_TEXT
            + "\n"
            + RECONCILE_BEGIN
            + "\n"
            + RECONCILE_BODY
            + "\n"
            + RECONCILE_END
            + "\n"
        )
        assert _exact_marker_line_count(result, RECONCILE_BEGIN) == 1
        assert _exact_marker_line_count(result, RECONCILE_END) == 1
        assert find_reconcile_block(result.splitlines(keepends=True)) is not None

    def test_block_updated_in_place_on_rerun(self) -> None:
        first = sync_reconciliation_blocker(ROOT_TEXT, ["a.md"])
        stale = first.replace(RECONCILE_BODY, "STALE BODY")
        assert "STALE BODY" in stale
        repaired = sync_reconciliation_blocker(stale, ["a.md", "b.md"])
        assert repaired == first
        assert "STALE BODY" not in repaired
        assert _exact_marker_line_count(repaired, RECONCILE_BEGIN) == 1
        assert _exact_marker_line_count(repaired, RECONCILE_END) == 1

    def test_block_removed_when_pending_empty(self) -> None:
        blocked = sync_reconciliation_blocker(ROOT_TEXT, ["a.md"])
        assert sync_reconciliation_blocker(blocked, []) == ROOT_TEXT

    def test_removal_is_noop_without_block(self) -> None:
        assert sync_reconciliation_blocker(ROOT_TEXT, []) == ROOT_TEXT

    def test_idempotent_add_and_remove(self) -> None:
        once = sync_reconciliation_blocker(ROOT_TEXT, ["a.md"])
        assert sync_reconciliation_blocker(once, ["a.md"]) == once
        second = sync_reconciliation_blocker(
            sync_reconciliation_blocker(once, []), []
        )
        assert second == ROOT_TEXT
