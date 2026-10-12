"""Behavior tests for missing `apply` inputs."""

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
    _raw_setup,
    _write_file,
)
from core_sync_pkg.domain.reconciliation import (  # noqa: E402
    reconciliation_report_path,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import (  # noqa: E402
    load_bindings,
    save_bindings,
)


class ApplyMissingInputsTests:
    """Verify `apply` fails closed when a region or raw input is missing."""

    def _setup(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", DEST_MARKED)
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["agent.md"]),
        )
        return source, destination, bindings_path

    def test_apply_missing_destination_returns_one_and_writes_nothing(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        present = _write_file(destination, "present.md", DEST_MARKED)
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["present.md", "absent.md"]),
        )

        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 1
        assert present.read_text(encoding="utf-8") == DEST_MARKED
        assert not (destination / "absent.md").exists()
        updated = load_bindings(bindings_path)
        assert updated is not None
        assert updated["core_revision"] == REV_B

    def test_apply_missing_raw_destination_returns_one(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _raw_setup(
            tmp_path, destination_content=None
        )
        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 1

    def test_apply_missing_raw_source_returns_one_without_writing_targets(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = _raw_setup(tmp_path)
        (source / "opencode.jsonc").unlink()
        root_path = _write_file(
            destination, "CLAUDE.md", "# Root remains unchanged\n"
        )
        bindings = load_bindings(bindings_path)
        assert bindings is not None
        bindings["root"] = "CLAUDE.md"
        save_bindings(bindings_path, bindings)
        report_path = reconciliation_report_path(bindings_path)
        unchanged = {
            destination / "opencode.jsonc": (
                destination / "opencode.jsonc"
            ).read_bytes(),
            bindings_path: bindings_path.read_bytes(),
            root_path: root_path.read_bytes(),
        }

        assert not report_path.exists()
        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 1
        assert {path: path.read_bytes() for path in unchanged} == unchanged
        assert not report_path.exists()

    def test_apply_missing_source_returns_one_without_writing_targets(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        (source / "agent.md").unlink()
        root_path = _write_file(
            destination, "CLAUDE.md", "# Root remains unchanged\n"
        )
        bindings = load_bindings(bindings_path)
        assert bindings is not None
        bindings["root"] = "CLAUDE.md"
        bindings["pending"] = ["agent.md"]
        save_bindings(bindings_path, bindings)
        report_path = reconciliation_report_path(bindings_path)
        unchanged = {
            destination / "agent.md": (destination / "agent.md").read_bytes(),
            bindings_path: bindings_path.read_bytes(),
            root_path: root_path.read_bytes(),
        }

        assert not report_path.exists()
        assert main(_apply_args(source, destination, bindings_path, REV_A)) == 1
        assert {path: path.read_bytes() for path in unchanged} == unchanged
        assert not report_path.exists()
