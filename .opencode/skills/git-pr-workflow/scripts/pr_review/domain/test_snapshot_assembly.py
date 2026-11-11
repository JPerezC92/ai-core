"""Specify complete offline scanner snapshot assembly and exact path reconciliation."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from pr_review.domain.snapshot_assembly import assemble_snapshot
from pr_review.domain.records import ReviewPreparationError
from pr_review.test_support import (
    InventoryDefect, create_invalid_inventory, create_paths, create_snapshot,
    create_snapshot_without_commits,
)


def test_complete_snapshot_preserves_deleted_path() -> None:
    collected = create_snapshot()
    result = assemble_snapshot(collected, create_paths())
    assert result == collected


@pytest.mark.parametrize("change", ["missing", "extra", "duplicate"])
def test_snapshot_rejects_nonexact_file_inventory(change: InventoryDefect) -> None:
    collected = create_invalid_inventory(change)
    result = assemble_snapshot(collected, create_paths())
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "SNAPSHOT_PATHS_MISMATCH"


def test_snapshot_rejects_missing_commit_messages() -> None:
    collected = create_snapshot_without_commits()
    result = assemble_snapshot(collected, create_paths())
    assert isinstance(result, ReviewPreparationError)
    assert result.code == "SNAPSHOT_INVALID"
