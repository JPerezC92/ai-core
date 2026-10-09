"""Behavior tests for blocker markers embedded in fenced code blocks.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_blocker_fenced_code.py
"""

from __future__ import annotations

from _core_sync_testkit import uc


class BlockerFenceHandlingTests:
    """Verify blocker parsing ignores fenced marker examples."""

    def test_fenced_reconcile_block_is_ignored(self) -> None:
        fenced = (
            "# Root\n\n```markdown\n"
            + uc.RECONCILE_BEGIN
            + "\n> STALE FENCED BODY\n"
            + uc.RECONCILE_END
            + "\n```\n"
        )

        assert uc.find_reconcile_block(fenced.splitlines(keepends=True)) is None
        assert uc.sync_reconciliation_blocker(fenced, []) == fenced

        appended = uc.sync_reconciliation_blocker(fenced, ["a.md"])
        assert appended.startswith(fenced)
        assert "STALE FENCED BODY" in appended
        assert appended.count(uc.RECONCILE_BODY) == 1
        assert uc.find_reconcile_block(appended.splitlines(keepends=True)) is not None
