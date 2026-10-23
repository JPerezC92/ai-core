"""Task and feature lifecycle tests for ODD feature documents."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from feature_testkit import make_feature  # noqa: E402
from validate_feature import validate_feature  # noqa: E402


def test_open_and_in_progress_tasks_allow_pending_commit() -> None:
    assert validate_feature(make_feature(task_status="open", commit="pending")) == []
    assert validate_feature(make_feature(task_status="in progress", commit="pending")) == []


@pytest.mark.parametrize("task_status", ("open", "in progress"))
@pytest.mark.parametrize("commit", ("", "   ", "not-a-hash", "abc123", "g" * 7, "a" * 65))
def test_open_and_in_progress_tasks_reject_malformed_commits(
    task_status: str, commit: str
) -> None:
    findings = validate_feature(make_feature(task_status=task_status, commit=commit))
    assert any("commit" in finding for finding in findings)


def test_done_task_with_pending_commit_is_rejected() -> None:
    findings = validate_feature(make_feature(task_status="done", commit="pending"))
    assert any("done task must have" in finding for finding in findings)


def test_done_task_with_valid_hex_commit_is_accepted() -> None:
    assert validate_feature(make_feature(task_status="done", commit="a1b2c3d")) == []


@pytest.mark.parametrize("commit", ("", "   ", "not-a-hash", "abc123", "g" * 7, "a" * 65))
def test_done_task_with_blank_or_malformed_commit_is_rejected(commit: str) -> None:
    findings = validate_feature(make_feature(task_status="done", commit=commit))
    assert any("done task must have" in finding for finding in findings)


@pytest.mark.parametrize("commit", ("pending", "", "not-a-hash", "abc123"))
def test_closed_feature_rejects_pending_blank_or_malformed_commit(commit: str) -> None:
    findings = validate_feature(
        make_feature(status="closed", task_status="done", commit=commit)
    )
    assert findings


def test_closed_feature_with_done_committed_task_is_accepted() -> None:
    assert validate_feature(
        make_feature(status="closed", task_status="done", commit="a1b2c3d")
    ) == []


@pytest.mark.parametrize("task_status", ("open", "in progress"))
def test_closed_feature_requires_every_task_done(task_status: str) -> None:
    findings = validate_feature(
        make_feature(status="closed", task_status=task_status, commit="a1b2c3d")
    )
    assert any(f"closed feature has a {task_status} task" in finding for finding in findings)


def test_closed_feature_rejects_non_done_task_with_pending_commit() -> None:
    findings = validate_feature(make_feature(status="closed", task_status="open"))
    assert any("closed feature task must have" in finding for finding in findings)


def test_closed_feature_requires_closed_date() -> None:
    findings = validate_feature(make_feature(status="closed", include_closed_date=False))
    assert any("Closed date" in finding for finding in findings)


def test_closed_feature_requires_close_log_entry() -> None:
    findings = validate_feature(
        make_feature(status="closed", include_close_entry=False)
    )
    assert any("Close:" in finding for finding in findings)


def test_active_feature_rejects_close_log_entry() -> None:
    findings = validate_feature(
        make_feature(status="active", log_entries=("- L1 — original request", "- L2 — Close: done"))
    )
    assert any("active feature" in finding for finding in findings)
