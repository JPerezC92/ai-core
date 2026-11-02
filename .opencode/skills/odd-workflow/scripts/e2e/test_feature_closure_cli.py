"""Filesystem and command-line behavior of the assembled closure detector."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from check_feature_closure import main  # noqa: E402
from feature_closure.test_support import (  # noqa: E402
    GIT_LIVE_BRANCH,
    GIT_REMOVED_BRANCH,
    RemoteRepositoryFixture,
    create_remote_repository,
    isolate_fixture_environment,
)
from feature_testkit import make_feature  # noqa: E402

ENTRY = "check_feature_closure.py"


@pytest.fixture()
def remote_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> RemoteRepositoryFixture:
    """Expose one isolated local remote under machine-independent Git configuration."""
    isolate_fixture_environment(monkeypatch)
    return create_remote_repository(tmp_path / "closure")


def test_clean_selection_reports_nothing_and_exits_zero(
    tmp_path: Path, remote_repository: RemoteRepositoryFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "closed.md").write_text(
        make_feature(status="closed", branch=f"`{GIT_REMOVED_BRANCH}`"), encoding="utf-8"
    )
    (tmp_path / "open.md").write_text(
        make_feature(branch="N/A — no branch yet"), encoding="utf-8"
    )

    status = main([ENTRY, "--features-dir", str(tmp_path), "--remote", remote_repository["remote_uri"]])

    assert status == 0
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_active_feature_whose_branch_left_the_remote_is_reported_with_exit_one(
    tmp_path: Path, remote_repository: RemoteRepositoryFixture, capsys: pytest.CaptureFixture[str]
) -> None:
    offending = tmp_path / "delivered.md"
    offending.write_text(make_feature(branch=f"`{GIT_REMOVED_BRANCH}`"), encoding="utf-8")
    (tmp_path / "live.md").write_text(make_feature(branch=f"`{GIT_LIVE_BRANCH}`"), encoding="utf-8")
    remote = remote_repository["remote_uri"]

    status = main([ENTRY, "--features-dir", str(tmp_path), "--remote", remote])

    assert status == 1
    captured = capsys.readouterr()
    assert captured.out == (
        f"UNCLOSED {offending}: branch '{GIT_REMOVED_BRANCH}' no longer exists on '{remote}'\n"
    )
    assert captured.err == ""


def test_missing_document_directory_is_a_boundary_failure(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    status = main([ENTRY, "--features-dir", str(tmp_path / "absent")])

    assert status == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("error: ")


def test_unresolvable_remote_is_a_boundary_failure_not_an_unclosed_report(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    isolate_fixture_environment(monkeypatch)
    (tmp_path / "feature.md").write_text(
        make_feature(branch=f"`{GIT_LIVE_BRANCH}`"), encoding="utf-8"
    )
    unreachable = (tmp_path / "unreachable.git").as_uri()

    status = main([ENTRY, "--features-dir", str(tmp_path), "--remote", unreachable])

    assert status == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("error: ")


def test_directory_without_documents_is_never_a_clean_pass(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / "_template.md").write_text(
        make_feature(title="Feature name", created="date"), encoding="utf-8"
    )

    status = main([ENTRY, "--features-dir", str(tmp_path)])

    assert status == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "error: no feature documents found\n"


def test_default_document_directory_is_odd_tasks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    tasks = tmp_path / "odd" / "tasks"
    tasks.mkdir(parents=True)
    (tasks / "feature.md").write_text(make_feature(branch="N/A — no branch yet"), encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    status = main([ENTRY])

    assert status == 0
    assert capsys.readouterr().out == ""


def test_unknown_option_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as raised:
        main([ENTRY, "--not-an-option"])

    assert raised.value.code == 2
