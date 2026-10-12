"""Tests for blocker insertion formatting and root-content preservation."""

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
    sync_reconciliation_blocker,
)


class ReconcileBlockerFormattingTests:
    def test_other_root_content_preserved(self) -> None:
        blocked = sync_reconciliation_blocker(ROOT_TEXT, ["a.md"])
        removed = sync_reconciliation_blocker(blocked, [])
        assert removed == ROOT_TEXT
        assert "# Root runtime" in removed
        assert "Last line." in removed

    def test_empty_root_text_gets_block_without_leading_blank(self) -> None:
        result = sync_reconciliation_blocker("", ["a.md"])
        assert result == (
            RECONCILE_BEGIN
            + "\n"
            + RECONCILE_BODY
            + "\n"
            + RECONCILE_END
            + "\n"
        )

    def test_root_without_trailing_newline_gains_separator(self) -> None:
        result = sync_reconciliation_blocker("no newline", ["a.md"])
        assert result.startswith("no newline\n\n" + RECONCILE_BEGIN)
