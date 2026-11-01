"""Specify body-only initialization using isolated files and the assembled CLI."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from prepare_pr_review import main
from pr_review.test_support import create_body, create_draft


def test_initialize_preserves_creation_draft_and_writes_one_working_body(tmp_path: Path) -> None:
    draft = tmp_path / "pr-draft.md"
    working = tmp_path / "pr-working-body.md"
    draft.write_text(create_draft(), encoding="utf-8")
    status = main(["initialize", "--draft", str(draft), "--working-body", str(working)])
    assert status == 0
    assert draft.read_text(encoding="utf-8") == create_draft()
    assert working.read_text(encoding="utf-8") == create_body()
    assert set(tmp_path.iterdir()) == {draft, working}


def test_initialize_refuses_to_overwrite_existing_working_body(tmp_path: Path) -> None:
    draft = tmp_path / "pr-draft.md"
    working = tmp_path / "pr-working-body.md"
    draft.write_text(create_draft(), encoding="utf-8")
    working.write_text(create_body(), encoding="utf-8")
    status = main(["initialize", "--draft", str(draft), "--working-body", str(working)])
    assert status != 0
    assert working.read_text(encoding="utf-8") == create_body()
