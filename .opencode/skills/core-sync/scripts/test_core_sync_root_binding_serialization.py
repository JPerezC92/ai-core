"""Test root-field preservation through bindings serialization.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_root_binding_serialization.py
"""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import REV_A, _bindings_document, uc


class RootBindingSerializationTests:
    def test_bindings_round_trip_preserves_root(self, tmp_path: Path) -> None:
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_A, "agent.md", ["agent.md"], [], "CLAUDE.md"),
        )
        loaded = uc.load_bindings(bindings_path)
        assert loaded is not None
        assert loaded["root"] == "CLAUDE.md"
