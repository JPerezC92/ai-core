"""Behavior tests for blocker markers embedded in fenced code blocks.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_blocker_fenced_code.py
"""

from __future__ import annotations

from core_sync_pkg.domain.constants import (
    RECONCILE_BEGIN,
    RECONCILE_BODY,
    RECONCILE_END,
)
from core_sync_pkg.domain.reconciliation import (
    find_reconcile_block,
    sync_reconciliation_blocker,
)


class BlockerFenceHandlingTests:
    """Verify blocker parsing ignores fenced marker examples."""

    def test_fenced_reconcile_block_is_ignored(self) -> None:
        fenced = (
            "# Root\n\n```markdown\n"
            + RECONCILE_BEGIN
            + "\n> STALE FENCED BODY\n"
            + RECONCILE_END
            + "\n```\n"
        )

        assert find_reconcile_block(fenced.splitlines(keepends=True)) is None
        assert sync_reconciliation_blocker(fenced, []) == fenced

        appended = sync_reconciliation_blocker(fenced, ["a.md"])
        assert appended.startswith(fenced)
        assert "STALE FENCED BODY" in appended
        assert appended.count(RECONCILE_BODY) == 1
        assert find_reconcile_block(appended.splitlines(keepends=True)) is not None
