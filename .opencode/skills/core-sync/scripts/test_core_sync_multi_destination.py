"""Behavior tests for applying one source to multiple destinations.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_multi_destination.py
"""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import (
    DEST_MARKED,
    REV_A,
    REV_B,
    SOURCE_MARKED,
    _apply_args,
    _bindings_document,
    _check_args,
    _write_file,
    uc,
)


class MultiDestinationTests:
    def test_one_source_two_destinations_both_healed(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        first = _write_file(destination, "one.md", DEST_MARKED)
        second = _write_file(
            destination,
            "two.md",
            DEST_MARKED.replace("Destination old body", "Second old body").replace(
                "Destination project region", "Second project region"
            ),
        )
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["one.md", "two.md"]),
        )

        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 0
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 0

        source_split = uc.split_regions(SOURCE_MARKED)
        assert source_split is not None
        for path in (first, second):
            split = uc.split_regions(path.read_text(encoding="utf-8"))
            assert split is not None
            assert split["region"] == source_split["region"]
