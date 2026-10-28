"""End-to-end CLI results through concrete adapters and controlled processes."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from verified_pr_cleanup_pkg.domain._test_support import CleanupTestData as Data
from verified_pr_cleanup_pkg.entry import main
from verified_pr_cleanup_pkg.infrastructure._test_support import (
    create_e2e_fixture,
    install_fake_process_boundaries,
    is_allowed_read_only_git_argv,
)

MALFORMED_BASE_BRANCH = "a..b"


def test_assembled_cli_reports_safe_to_clean_with_concrete_adapters(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Report SAFE_TO_CLEAN using concrete adapters and isolated local/fake processes."""
    fixture, payload = create_e2e_fixture(tmp_path, Data.MERGED_PR_STATE)
    observed_git_argv = install_fake_process_boundaries(monkeypatch, fixture.bare, payload)
    monkeypatch.chdir(fixture.local)

    exit_code = main((
        str(Data.PR_NUMBER), "--base-remote", Data.REMOTE_NAME,
        "--base-branch", Data.BASE_BRANCH,
    ))
    output = json.loads(capsys.readouterr().out)
    assert exit_code == 0
    assert output["status"] == "SAFE_TO_CLEAN"
    assert output["point_in_time_only"] is True
    assert output["evidence"]["head_oid"] == payload["headRefOid"]
    assert output["evidence"]["merge_commit_oid"] == payload["mergeCommit"]["oid"]
    assert output["evidence"]["remote_base_oid"] == output["evidence"]["local_base_oid"]
    assert output["revalidate_before_each_mutation"]
    assert all(is_allowed_read_only_git_argv(arguments) for arguments in observed_git_argv)


def test_assembled_cli_reports_blocked_pr_with_reason_and_exit_code(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Expose an unmerged PR as observable BLOCKED output without mutation."""
    fixture, payload = create_e2e_fixture(tmp_path, Data.OPEN_PR_STATE)
    assert payload["mergedAt"] is None
    assert payload["mergeCommit"] is None
    observed_git_argv = install_fake_process_boundaries(monkeypatch, fixture.bare, payload)
    monkeypatch.chdir(fixture.local)

    exit_code = main((
        str(Data.PR_NUMBER), "--base-remote", Data.REMOTE_NAME,
        "--base-branch", Data.BASE_BRANCH,
    ))
    output = json.loads(capsys.readouterr().out)
    assert exit_code == 1
    assert output["status"] == "BLOCKED"
    assert any("not verifiably MERGED" in reason for reason in output["reasons"])
    assert output["evidence"]["pr_state"] == Data.OPEN_PR_STATE
    assert output["evidence"]["merged_at"] is None
    assert output["evidence"]["merge_commit_oid"] is None
    assert all(is_allowed_read_only_git_argv(arguments) for arguments in observed_git_argv)


def test_assembled_cli_rejects_malformed_base_branch_before_inspection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Reject an invalid --base-branch with argparse status 2 and no repository state."""
    monkeypatch.chdir(tmp_path)

    with pytest.raises(SystemExit) as exit_info:
        main((
            str(Data.PR_NUMBER), "--base-remote", Data.REMOTE_NAME,
            "--base-branch", MALFORMED_BASE_BRANCH,
        ))
    captured = capsys.readouterr()
    assert exit_info.value.code == 2
    assert captured.out == ""
    assert "base branch is invalid." in captured.err
    assert list(tmp_path.iterdir()) == []


def test_assembled_cli_reports_github_boundary_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Route a failed fake GitHub CLI boundary to stderr without a validator decision."""
    fixture, payload = create_e2e_fixture(tmp_path, Data.MERGED_PR_STATE)
    observed_git_argv = install_fake_process_boundaries(
        monkeypatch, fixture.bare, payload, Data.GITHUB_FAILURE_EXIT_CODE
    )
    monkeypatch.chdir(fixture.local)

    exit_code = main((
        str(Data.PR_NUMBER), "--base-remote", Data.REMOTE_NAME,
        "--base-branch", Data.BASE_BRANCH,
    ))
    captured = capsys.readouterr()
    assert exit_code != 0
    # A boundary failure keeps an error channel: no SAFE_TO_CLEAN/BLOCKED decision JSON.
    assert captured.out == ""
    assert captured.err.startswith("Preflight boundary failure: ")
    assert "GitHub CLI could not read the requested PR" in captured.err
    assert "SAFE_TO_CLEAN" not in captured.err
    assert "BLOCKED" not in captured.err
    assert all(
        is_allowed_read_only_git_argv(arguments) for arguments in observed_git_argv
    ), observed_git_argv
