"""Validate root paths in core-sync binding documents.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_root_binding_validation.py
"""

from __future__ import annotations

from _core_sync_testkit import REV_A, uc


class RootBindingValidationTests:
    def test_invalid_root_escapes_are_rejected(self) -> None:
        text = (
            "schema: 1\n"
            "core_revision: " + REV_A + "\n"
            "root: ../escape.md\n"
            "bindings:\n"
            "  - source: agent.md\n"
            "    destinations:\n"
            "      - agent.md\n"
            "pending: []\n"
        )
        assert uc.parse_bindings(text) is None
