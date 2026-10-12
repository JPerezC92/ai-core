"""Validate binding mode values in core-sync binding entries.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_binding_validation.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import REV_A  # noqa: E402
from core_sync_pkg.domain.bindings import parse_bindings  # noqa: E402


class BindingModeValidationTests:
    """Reject invalid binding modes during parsing."""

    def test_unknown_mode_rejected_by_parser(self) -> None:
        text = (
            "schema: 1\n"
            "core_revision: " + REV_A + "\n"
            "bindings:\n"
            "  - source: opencode.jsonc\n"
            "    destinations:\n"
            "      - opencode.jsonc\n"
            "    mode: bogus\n"
            "pending: []\n"
        )
        assert parse_bindings(text) is None
