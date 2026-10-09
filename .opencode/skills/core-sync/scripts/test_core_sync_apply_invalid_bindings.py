"""Tests for `apply` rejecting malformed bindings."""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import REV_A, _apply_args, uc


class ApplyInvalidBindingsTests:
    """Verify `apply` rejects malformed bindings."""

    def test_apply_malformed_bindings_returns_two(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        source.mkdir()
        destination.mkdir()
        bindings_path = tmp_path / "bindings.yaml"
        bindings_path.write_text("schema: 1\nbindings: nope\n", encoding="utf-8")
        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 2
