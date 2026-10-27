"""Integration tests for the completed-plan audit contract at validator entry points."""

from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import validate_plan as vp  # noqa: E402
from _validate_plan_testkit import (  # noqa: E402
    AUDIT_PASS,
    VALID_PHASE,
    VALID_PLAN,
    build_single_file_plan,
    write_fixture,
)

_MISSING_AUDIT = "AUDIT: completed plan is missing the ## Audit section"
_COMPLETED_PLAN = VALID_PLAN.replace(
    "> **Status:** active",
    "> **Status:** completed\n> **Completed:** 2026-09-15",
)


class ValidatePlanAuditIntegrationTests:
    def test_validate_single_file_completed_missing_audit_returns_one(
        self, tmp_path: Path
    ) -> None:
        plan_file = write_fixture(
            tmp_path,
            "plan.md",
            build_single_file_plan(status="completed", completed="2026-09-15"),
        )
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = vp.validate_single_file(str(plan_file))
        assert result == 1
        assert stderr.getvalue() == f"{_MISSING_AUDIT}\n"
        assert stdout.getvalue() == ""

    def test_validate_single_file_completed_pass_outputs_success(
        self, tmp_path: Path
    ) -> None:
        plan_file = write_fixture(
            tmp_path,
            "plan.md",
            build_single_file_plan(
                status="completed",
                completed="2026-09-15",
                auditor="Sentinel (Quality Guardian)",
                verdict="[PASS]",
                findings="0",
                date="2026-09-15",
            ),
        )
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = vp.validate_single_file(str(plan_file))
        assert result == 0
        assert stdout.getvalue() == f"ok  single-file plan: {plan_file}\n"

    def test_validate_single_file_active_absent_audit_outputs_success(
        self, tmp_path: Path
    ) -> None:
        plan_file = write_fixture(tmp_path, "plan.md", build_single_file_plan())
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = vp.validate_single_file(str(plan_file))
        assert result == 0
        assert stdout.getvalue() == f"ok  single-file plan: {plan_file}\n"

    def test_validate_single_file_active_unknown_verdict_returns_one(
        self, tmp_path: Path
    ) -> None:
        plan_file = write_fixture(
            tmp_path,
            "plan.md",
            build_single_file_plan(
                auditor="Sentinel (Quality Guardian)",
                verdict="[MAYBE]",
                findings="0",
                date="2026-09-15",
            ),
        )
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            result = vp.validate_single_file(str(plan_file))
        assert result == 1
        assert stderr.getvalue() == (
            "AUDIT: Verdict '[MAYBE]' not in ['[FAIL]', '[PASS]', '[PENDING]']\n"
        )

    def test_validate_plan_dir_completed_pass_outputs_success(
        self, tmp_path: Path
    ) -> None:
        write_fixture(tmp_path, "plan.md", _COMPLETED_PLAN + AUDIT_PASS)
        write_fixture(tmp_path, "phase-01-owner.md", VALID_PHASE)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = vp.validate_plan_dir(str(tmp_path))
        assert result == 0
        assert stdout.getvalue() == f"ok  plan: {tmp_path}  phases: 1\n"

    def test_validate_plan_dir_completed_missing_audit_diagnostic_once(
        self, tmp_path: Path
    ) -> None:
        write_fixture(tmp_path, "plan.md", _COMPLETED_PLAN)
        write_fixture(tmp_path, "phase-01-owner.md", VALID_PHASE)
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = vp.validate_plan_dir(str(tmp_path))
        assert result == 1
        assert stderr.getvalue() == f"{_MISSING_AUDIT}\n"
        assert stdout.getvalue() == ""
