"""Behavior tests for valid region decomposition and outside-byte extraction.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_regions.py
"""

from __future__ import annotations

from _core_sync_testkit import uc


class RegionDecompositionTests:
    def test_valid_markers_split_region_and_outside(self) -> None:
        content = "head\n<!-- core:begin -->\nbody\n<!-- core:end -->\ntail\n"
        split = uc.split_regions(content)
        assert split is not None
        assert split["before"] == "head\n"
        assert split["region"] == "body\n"
        assert split["after"] == "tail\n"
        assert (
            uc.outside_bytes(split)
            == "head\n<!-- core:begin -->\n<!-- core:end -->\ntail\n"
        )
