"""Test root-field preservation through bindings serialization.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/infrastructure/test_root_binding_serialization.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import REV_A, _bindings_document  # noqa: E402
from core_sync_pkg.infrastructure.stores import (  # noqa: E402
    load_bindings,
    save_bindings,
)


class RootBindingSerializationTests:
    def test_bindings_round_trip_preserves_root(self, tmp_path: Path) -> None:
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_A, "agent.md", ["agent.md"], [], "CLAUDE.md"),
        )
        loaded = load_bindings(bindings_path)
        assert loaded is not None
        assert loaded["root"] == "CLAUDE.md"
