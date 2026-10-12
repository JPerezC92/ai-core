"""Behavior tests for the region-mode `apply` contract.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_apply.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    DEST_MARKED,
    REV_A,
    REV_B,
    SOURCE_MARKED,
    _apply_args,
    _bindings_document,
    _write_bytes_file,
    _write_file,
)
from core_sync_pkg.domain.regions import outside_bytes, split_regions  # noqa: E402
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import save_bindings  # noqa: E402


class ApplyContractTests:
    """Exercise region healing and byte-preservation behavior for `apply`."""

    def _setup(
        self,
        tmp_path: Path,
        *,
        destination_content: str = DEST_MARKED,
        pinned: str = REV_B,
    ) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", destination_content)
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(pinned, "agent.md", ["agent.md"]),
        )
        return source, destination, bindings_path

    def test_apply_heals_region_and_preserves_outside(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        destination_path = destination / "agent.md"

        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 0

        source_split = split_regions(SOURCE_MARKED)
        destination_split = split_regions(DEST_MARKED)
        healed_split = split_regions(destination_path.read_text(encoding="utf-8"))
        assert source_split is not None
        assert destination_split is not None
        assert healed_split is not None
        assert healed_split["region"] == source_split["region"]
        assert outside_bytes(healed_split) == outside_bytes(destination_split)
        assert destination_path.read_text(encoding="utf-8").endswith(
            "Destination project region\n"
        )

    def test_apply_preserves_lf_only_outside_region(
        self, tmp_path: Path
    ) -> None:
        source_bytes = (
            b"---\nname: source\n---\n"
            b"<!-- core:begin -->\n"
            b"Source core line one\nSource core line two\n"
            b"<!-- core:end -->\n"
        )
        destination_bytes = (
            b"---\nname: destination\n---\n"
            b"<!-- core:begin -->\n"
            b"Old core line\n"
            b"<!-- core:end -->\n"
            b"<!-- project:begin -->\n"
            b"Project line one\nProject line two\n"
            b"<!-- project:end -->\n"
            b"Outside trailing line\n"
        )
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_bytes_file(source, "agent.md", source_bytes, mode="region")
        destination_path = _write_bytes_file(
            destination, "agent.md", destination_bytes
        )
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["agent.md"]),
        )

        original_split = split_regions(destination_bytes.decode("utf-8"))
        source_split = split_regions(source_bytes.decode("utf-8"))
        assert original_split is not None
        assert source_split is not None
        original_outside = outside_bytes(original_split).encode("utf-8")

        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 0

        updated_bytes = destination_path.read_bytes()
        updated_split = split_regions(updated_bytes.decode("utf-8"))
        assert updated_split is not None
        assert updated_split["region"] == source_split["region"]
        assert outside_bytes(updated_split).encode("utf-8") == original_outside
        assert b"\r" not in updated_bytes
        assert (
            b"---\nname: destination\n---\n<!-- core:begin -->\n"
            in updated_bytes
        )
        assert b"Source core line one\nSource core line two\n" in updated_bytes
        assert (
            b"<!-- core:end -->\n<!-- project:begin -->\n"
            b"Project line one\nProject line two\n"
            in updated_bytes
        )
