"""Tests for the completed-plan audit gate and accepted verdict set."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import validate_plan as vp  # noqa: E402
from _validate_plan_testkit import (  # noqa: E402
    AUDIT_FAIL,
    AUDIT_PASS,
    AUDIT_PENDING,
    AUDIT_UNKNOWN,
    PHASE_AWARE_PLAN,
    build_single_file_plan,
)


class ValidatePlanAuditGateTests:
    def test_audit_gate_pending_active_passes(self) -> None:
        assert vp.check_audit_gate(PHASE_AWARE_PLAN + AUDIT_PENDING, "active") == []

    def test_audit_gate_absent_on_active_passes(self) -> None:
        assert vp.check_audit_gate(PHASE_AWARE_PLAN, "active") == []

    def test_audit_gate_completed_without_audit_flagged(self) -> None:
        assert vp.check_audit_gate(PHASE_AWARE_PLAN, "completed") == [
            "AUDIT: completed plan is missing the ## Audit section"
        ]

    def test_audit_gate_completed_fail_flagged(self) -> None:
        assert vp.check_audit_gate(PHASE_AWARE_PLAN + AUDIT_FAIL, "completed") == [
            "AUDIT: completed plan Verdict must be [PASS], found '[FAIL]'"
        ]

    def test_audit_gate_unknown_verdict_flagged(self) -> None:
        assert vp.check_audit_gate(PHASE_AWARE_PLAN + AUDIT_UNKNOWN, "active") == [
            "AUDIT: Verdict '[MAYBE]' not in ['[FAIL]', '[PASS]', '[PENDING]']"
        ]

    def test_audit_gate_completed_pass_passes(self) -> None:
        assert vp.check_audit_gate(PHASE_AWARE_PLAN + AUDIT_PASS, "completed") == []

    def test_completed_plan_snapshot_missing_audit_flagged(self) -> None:
        content = build_single_file_plan(
            status="completed", completed="2026-09-15"
        )
        assert vp.check_plan_snapshot({"path": "plan.md", "content": content}) == [
            "AUDIT: completed plan is missing the ## Audit section"
        ]

    def test_completed_plan_snapshot_fail_flagged(self) -> None:
        content = build_single_file_plan(
            status="completed",
            completed="2026-09-15",
            auditor="Sentinel (Quality Guardian)",
            verdict="[FAIL]",
            findings="2",
            date="2026-09-15",
        )
        assert vp.check_plan_snapshot({"path": "plan.md", "content": content}) == [
            "AUDIT: completed plan Verdict must be [PASS], found '[FAIL]'"
        ]

    def test_completed_plan_snapshot_pending_flagged(self) -> None:
        content = build_single_file_plan(
            status="completed",
            completed="2026-09-15",
            auditor="Sentinel (Quality Guardian)",
            verdict="[PENDING]",
            findings="0",
            date="2026-09-15",
        )
        assert vp.check_plan_snapshot({"path": "plan.md", "content": content}) == [
            "AUDIT: completed plan Verdict must be [PASS], found '[PENDING]'"
        ]

    def test_completed_plan_snapshot_unknown_verdict_flagged(self) -> None:
        content = build_single_file_plan(
            status="completed",
            completed="2026-09-15",
            auditor="Sentinel (Quality Guardian)",
            verdict="[MAYBE]",
            findings="0",
            date="2026-09-15",
        )
        assert vp.check_plan_snapshot({"path": "plan.md", "content": content}) == [
            "AUDIT: Verdict '[MAYBE]' not in ['[FAIL]', '[PASS]', '[PENDING]']",
            "AUDIT: completed plan Verdict must be [PASS], found '[MAYBE]'",
        ]

    def test_completed_plan_snapshot_empty_auditor_flagged(self) -> None:
        content = build_single_file_plan(
            status="completed",
            completed="2026-09-15",
            auditor="",
            verdict="[PASS]",
            findings="0",
            date="2026-09-15",
        )
        assert vp.check_plan_snapshot({"path": "plan.md", "content": content}) == [
            "AUDIT: completed plan has an empty Auditor"
        ]

    def test_completed_plan_snapshot_empty_date_flagged(self) -> None:
        content = build_single_file_plan(
            status="completed",
            completed="2026-09-15",
            auditor="Sentinel (Quality Guardian)",
            verdict="[PASS]",
            findings="0",
            date="",
        )
        assert vp.check_plan_snapshot({"path": "plan.md", "content": content}) == [
            "AUDIT: completed plan has no Date"
        ]

    def test_completed_plan_snapshot_pass_passes(self) -> None:
        content = build_single_file_plan(
            status="completed",
            completed="2026-09-15",
            auditor="Sentinel (Quality Guardian)",
            verdict="[PASS]",
            findings="0",
            date="2026-09-15",
        )
        assert vp.check_plan_snapshot({"path": "plan.md", "content": content}) == []

    def test_active_plan_snapshot_absent_audit_passes(self) -> None:
        content = build_single_file_plan()
        assert vp.check_plan_snapshot({"path": "plan.md", "content": content}) == []

    def test_active_plan_snapshot_unknown_verdict_flagged(self) -> None:
        content = build_single_file_plan(
            auditor="Sentinel (Quality Guardian)",
            verdict="[MAYBE]",
            findings="0",
            date="2026-09-15",
        )
        assert vp.check_plan_snapshot({"path": "plan.md", "content": content}) == [
            "AUDIT: Verdict '[MAYBE]' not in ['[FAIL]', '[PASS]', '[PENDING]']"
        ]
