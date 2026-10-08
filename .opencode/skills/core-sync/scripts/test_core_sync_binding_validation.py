"""Validate binding mode values in core-sync binding entries.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/test_core_sync_binding_validation.py
"""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import REV_A, _check_args, uc


class BindingModeValidationTests:
    """Reject invalid binding modes during parsing and CLI validation."""

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
        assert uc.parse_bindings(text) is None

    def test_unknown_mode_bindings_return_two(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        source.mkdir()
        destination.mkdir()
        bindings_path = tmp_path / "bindings.yaml"
        bindings_path.write_text(
            "schema: 1\n"
            "core_revision: " + REV_A + "\n"
            "bindings:\n"
            "  - source: opencode.jsonc\n"
            "    destinations:\n"
            "      - opencode.jsonc\n"
            "    mode: bogus\n"
            "pending: []\n",
            encoding="utf-8",
        )
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 2
