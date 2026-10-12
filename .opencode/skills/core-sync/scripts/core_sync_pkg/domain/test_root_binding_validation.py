"""Validate root paths in core-sync binding documents.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/domain/test_root_binding_validation.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import REV_A  # noqa: E402
from core_sync_pkg.domain.bindings import parse_bindings  # noqa: E402


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
        assert parse_bindings(text) is None
