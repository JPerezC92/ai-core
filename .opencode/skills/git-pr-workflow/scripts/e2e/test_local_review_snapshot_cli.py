"""Prepare scanner input from local authored prose and supplied immutable content."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from prepare_pr_evidence import main
from pr_review.test_support import (
    create_body, create_local_draft, create_local_inventory, create_local_snapshot, create_paths,
)


def test_prepare_snapshot_uses_only_local_title_and_working_body(tmp_path: Path) -> None:
    draft = tmp_path / "pr-draft.md"
    body = tmp_path / "pr-working-body.md"
    inventory = tmp_path / "inventory.json"
    paths = tmp_path / "paths.json"
    output = tmp_path / "snapshot.json"
    draft.write_text(create_local_draft(), encoding="utf-8", newline="")
    body.write_text(create_body(), encoding="utf-8", newline="")
    inventory.write_text(json.dumps(create_local_inventory()), encoding="utf-8")
    paths.write_text(json.dumps(create_paths()), encoding="utf-8")
    arguments = ["prepare-snapshot", "--draft", str(draft), "--working-body", str(body),
                 "--input", str(inventory), "--paths", str(paths), "--output", str(output)]
    assert main(arguments) == 0
    assert json.loads(output.read_text(encoding="utf-8")) == create_local_snapshot()
    assert draft.read_text(encoding="utf-8") == create_local_draft()
    assert body.read_text(encoding="utf-8") == create_body()
    assert main(arguments) != 0
    assert json.loads(output.read_text(encoding="utf-8")) == create_local_snapshot()
