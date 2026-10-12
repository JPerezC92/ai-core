"""Test mixed region/raw bindings in one synchronization operation.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_binding_coexistence.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    DEST_PLAIN,
    RAW_SOURCE_BYTES,
    REV_A,
    SOURCE_NO_MARKERS,
    _apply_args,
    _binding_entry,
    _bindings_with_entries,
    _check_args,
    _init_args,
    _write_bytes_file,
    _write_file,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import (  # noqa: E402
    load_bindings,
    save_bindings,
)


class BindingModeCoexistenceTests:
    """Verify region and raw entries coexist with their distinct contracts."""

    def test_region_and_raw_coexist(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_NO_MARKERS)
        _write_file(destination, "agent.md", DEST_PLAIN)
        _write_bytes_file(source, "opencode.jsonc", RAW_SOURCE_BYTES)
        _write_bytes_file(destination, "opencode.jsonc", RAW_SOURCE_BYTES)
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_with_entries(
                REV_A,
                [
                    _binding_entry("agent.md", ["agent.md"], "region"),
                    _binding_entry("opencode.jsonc", ["opencode.jsonc"], "raw"),
                ],
            ),
        )

        assert main(_init_args(source, destination, bindings_path, REV_A)) == 0
        updated = load_bindings(bindings_path)
        assert updated is not None
        assert updated["pending"] == ["agent.md"]
        assert (destination / "opencode.jsonc").read_bytes() == RAW_SOURCE_BYTES

        # The region entry's pending still forces drift; the raw entry adds none.
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1

        updated["pending"] = []
        save_bindings(bindings_path, updated)
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 0
