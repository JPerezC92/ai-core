"""Test binding-mode defaults and serialization round-trips.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_binding_serialization.py
"""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import REV_A, _bindings_document, uc


class BindingModeSerializationTests:
    """Verify default-region omission and raw-mode serialization round-trips."""

    def test_region_mode_is_omitted_from_serialized_bindings(
        self, tmp_path: Path
    ) -> None:
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_A, "agent.md", ["agent.md"]),
        )
        assert "mode:" not in bindings_path.read_text(encoding="utf-8")

    def test_raw_mode_round_trips_through_serialization(self, tmp_path: Path) -> None:
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(
                REV_A, "opencode.jsonc", ["opencode.jsonc"], mode="raw"
            ),
        )
        text = bindings_path.read_text(encoding="utf-8")
        assert "mode: raw" in text
        loaded = uc.load_bindings(bindings_path)
        assert loaded is not None
        assert loaded["bindings"][0]["mode"] == "raw"
