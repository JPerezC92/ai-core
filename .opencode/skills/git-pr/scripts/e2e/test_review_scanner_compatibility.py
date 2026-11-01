"""Exercise offline snapshot CLI output through the existing scanner CLI."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from prepare_pr_review import main
from scan_attribution import main as scan_main
from pr_review.test_support import (
    create_clean_scan_result, create_paths, create_policy, create_snapshot,
)


def test_prepared_snapshot_is_accepted_by_existing_scanner(
    tmp_path: Path, capsys: pytest.CaptureFixture[str],
) -> None:
    collected = tmp_path / "collected.json"
    paths = tmp_path / "paths.json"
    snapshot = tmp_path / "snapshot.json"
    policy = tmp_path / "policy.json"
    collected.write_text(json.dumps(create_snapshot()), encoding="utf-8")
    paths.write_text(json.dumps(create_paths()), encoding="utf-8")
    policy.write_text(json.dumps(create_policy()), encoding="utf-8")
    assert main([
        "snapshot", "--input", str(collected), "--paths", str(paths),
        "--output", str(snapshot),
    ]) == 0
    capsys.readouterr()
    assert json.loads(snapshot.read_text(encoding="utf-8")) == create_snapshot()
    assert scan_main(["--policy", str(policy), "--snapshot", str(snapshot)]) == 0
    assert json.loads(capsys.readouterr().out) == create_clean_scan_result()
