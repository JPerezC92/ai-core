"""Domain unit tests for root-path validation in core-sync binding documents.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/domain/test_root_binding_validation.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import REV_A  # noqa: E402
from core_sync_pkg.domain.bindings import parse_bindings  # noqa: E402


def _bindings_text(root: str) -> str:
    """Build one bindings document whose root field takes the given path."""
    return (
        "schema: 1\n"
        "core_revision: " + REV_A + "\n"
        f"root: '{root}'\n"
        "bindings:\n"
        "  - source: agent.md\n"
        "    destinations:\n"
        "      - agent.md\n"
        "pending: []\n"
    )


class RootBindingValidationTests:
    """Unsafe or escaping destination root paths are rejected as malformed."""

    def test_unsafe_or_escaping_root_paths_are_rejected(self) -> None:
        for root in (
            "../escape.md",
            "/abs.md",
            "a/../b.md",
            "dir//file.md",
            "sub\\file.md",
            "C:/root.md",
            "",
        ):
            assert parse_bindings(_bindings_text(root)) is None, root
