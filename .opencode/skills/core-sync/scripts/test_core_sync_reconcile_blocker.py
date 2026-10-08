"""Behavior tests for static destination reconciliation blocker content.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_reconcile_blocker.py
"""

from __future__ import annotations

from _core_sync_testkit import EXPECTED_RECONCILE_BODY, uc


class ReconcileBlockerContentTests:
    def test_block_body_is_the_self_contained_action_required_text(self) -> None:
        assert uc.RECONCILE_BODY == EXPECTED_RECONCILE_BODY

    def test_block_body_is_step_by_step_and_self_contained(self) -> None:
        body = uc.RECONCILE_BODY
        assert "ACTION REQUIRED" in body
        assert "self-contained" in body
        assert "This block is self-contained; no other context is required." in body
        assert "project region" in body
        assert "core region" in body
        assert (
            "> 2. If `.aicore/reconciliation/init.yaml` exists, read it. It records the "
            "core revision and each affected destination path, source, and action as "
            "metadata; it does not contain the displaced content. Use that metadata to "
            "locate and review each destination file, then inspect the displaced "
            "content there, in its `<!-- project:begin -->` … `<!-- project:end -->` "
            "region."
        ) in body
        for step in (
            "1. Open the file.",
            "5. Delete that file's entry",
        ):
            assert step in body
        assert "delete this entire blocker block" in body
