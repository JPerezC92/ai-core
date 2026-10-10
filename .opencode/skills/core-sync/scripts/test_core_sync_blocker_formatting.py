"""Tests for blocker insertion formatting and root-content preservation."""

from __future__ import annotations

from _core_sync_testkit import ROOT_TEXT, uc


class ReconcileBlockerFormattingTests:
    def test_other_root_content_preserved(self) -> None:
        blocked = uc.sync_reconciliation_blocker(ROOT_TEXT, ["a.md"])
        removed = uc.sync_reconciliation_blocker(blocked, [])
        assert removed == ROOT_TEXT
        assert "# Root runtime" in removed
        assert "Last line." in removed

    def test_empty_root_text_gets_block_without_leading_blank(self) -> None:
        result = uc.sync_reconciliation_blocker("", ["a.md"])
        assert result == (
            uc.RECONCILE_BEGIN
            + "\n"
            + uc.RECONCILE_BODY
            + "\n"
            + uc.RECONCILE_END
            + "\n"
        )

    def test_root_without_trailing_newline_gains_separator(self) -> None:
        result = uc.sync_reconciliation_blocker("no newline", ["a.md"])
        assert result.startswith("no newline\n\n" + uc.RECONCILE_BEGIN)
