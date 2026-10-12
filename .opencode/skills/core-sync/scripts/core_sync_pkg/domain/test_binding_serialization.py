"""Test binding-mode defaults and serialization round-trips.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_binding_serialization.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import REV_A  # noqa: E402
from core_sync_pkg.domain.bindings import parse_bindings, serialize_bindings  # noqa: E402


class BindingModeSerializationTests:
    """Verify default-region omission and raw-mode serialization round-trips."""

    def test_region_mode_is_omitted_from_serialized_bindings(self) -> None:
        text = serialize_bindings(
            {
                "schema": 1,
                "core_revision": REV_A,
                "bindings": [
                    {
                        "source": "agent.md",
                        "destinations": ["agent.md"],
                        "mode": "region",
                    }
                ],
                "pending": [],
                "root": None,
            }
        )
        assert "mode:" not in text

    def test_binding_mode_is_not_persisted(self) -> None:
        text = serialize_bindings(
            {
                "schema": 1,
                "core_revision": REV_A,
                "bindings": [
                    {
                        "source": "opencode.jsonc",
                        "destinations": ["opencode.jsonc"],
                        "mode": "raw",
                    }
                ],
                "pending": [],
                "root": None,
            }
        )
        assert "mode" not in text
        loaded = parse_bindings(text)
        assert loaded is not None
        assert loaded["bindings"][0]["mode"] == "region"
