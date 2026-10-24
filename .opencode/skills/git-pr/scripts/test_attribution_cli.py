"""CLI and filesystem-boundary tests for the attribution scanner."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from attribution_testkit import (
    load_approved_policy,
    make_attribution_line,
    make_changed_file,
    make_changed_files,
    make_complete_snapshot,
    make_malformed_policy,
    make_malformed_snapshot,
    make_malformed_surface_snapshot,
    make_snapshot_with_artifact_content,
    write_json,
)
from scan_attribution import main


POLICY = load_approved_policy()


def _run_cli(
    directory: Path,
    policy: object,
    snapshot: object,
    capsys: pytest.CaptureFixture[str],
) -> tuple[int, str]:
    policy_path = write_json(directory / "policy.json", policy)
    snapshot_path = write_json(directory / "snapshot.json", snapshot)
    status = main(["--policy", str(policy_path), "--snapshot", str(snapshot_path)])
    return status, capsys.readouterr().out


def test_cli_prints_deterministic_json_and_uses_match_based_exit_codes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    clean_status, clean_output = _run_cli(tmp_path, POLICY, make_complete_snapshot(), capsys)
    repeat_status, repeat_output = _run_cli(tmp_path, POLICY, make_complete_snapshot(), capsys)
    assert clean_status == repeat_status == 0
    assert clean_output == repeat_output
    assert json.loads(clean_output)["matches"] == []

    matched_snapshot = make_snapshot_with_artifact_content(
        "pr-title", make_attribution_line(POLICY),
        changed_files=make_changed_files(make_changed_file()),
    )
    match_status, match_output = _run_cli(tmp_path, POLICY, matched_snapshot, capsys)
    assert match_status == 1
    assert len(json.loads(match_output)["matches"]) == 1


@pytest.mark.parametrize(
    ("policy", "snapshot"),
    [
        (POLICY, make_malformed_snapshot()),
        (make_malformed_policy(POLICY), make_complete_snapshot()),
    ],
)
def test_cli_returns_two_and_json_error_for_malformed_input(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    policy: object,
    snapshot: object,
) -> None:
    status, output = _run_cli(tmp_path, policy, snapshot, capsys)
    assert status == 2
    assert isinstance(json.loads(output).get("error"), str)


def test_cli_returns_two_when_an_input_file_cannot_be_read(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    policy_path = write_json(tmp_path / "policy.json", POLICY)
    status = main(
        ["--policy", str(policy_path), "--snapshot", str(tmp_path / "missing.json")]
    )
    assert status == 2
    assert json.loads(capsys.readouterr().out) == {"error": "unable to read input file"}


def test_cli_returns_two_for_an_unhashable_artifact_surface(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    snapshot = make_malformed_surface_snapshot()
    status, output = _run_cli(tmp_path, POLICY, snapshot, capsys)
    assert status == 2
    assert isinstance(json.loads(output).get("error"), str)
