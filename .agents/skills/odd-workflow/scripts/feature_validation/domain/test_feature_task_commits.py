"""Test commit-reference requirements for ODD feature tasks."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from feature_testkit import make_feature  # noqa: E402
from feature_validation.domain.rules import validate_feature  # noqa: E402


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

