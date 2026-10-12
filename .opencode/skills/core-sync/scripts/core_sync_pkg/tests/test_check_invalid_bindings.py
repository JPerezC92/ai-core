"""Tests for `check` rejecting malformed bindings."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import REV_A, _check_args  # noqa: E402
from core_sync_pkg.infrastructure.composition import main  # noqa: E402


class CheckInvalidBindingsTests:
    """Verify `check` rejects malformed bindings."""

    def test_malformed_bindings_returns_two(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        source.mkdir()
        destination.mkdir()
        bindings_path = tmp_path / "bindings.yaml"
        bindings_path.write_text(
            "schema: 2\nbindings: []\npending: []\n", encoding="utf-8"
        )
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 2

    def test_unknown_binding_mode_returns_two(self, tmp_path: Path) -> None:
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
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 2
