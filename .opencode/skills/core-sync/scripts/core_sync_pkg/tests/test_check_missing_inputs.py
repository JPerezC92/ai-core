"""Behavior tests for missing `check` inputs."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    REV_A,
    SOURCE_MARKED,
    _bindings_document,
    _check_args,
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


class CheckMissingInputsTests:
    """Verify `check` reports drift when region or raw inputs are missing."""

    def _setup(
        self, tmp_path: Path, *, pending: list[str] | None = None
    ) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", SOURCE_MARKED)
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_document(REV_A, "agent.md", ["agent.md"], pending),
        )
        return source, destination, bindings_path

    def test_missing_destination_returns_one(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        (destination / "agent.md").unlink()
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1

    def test_missing_source_returns_one_without_writing_targets(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = self._setup(
            tmp_path, pending=["agent.md"]
        )
        (source / "agent.md").unlink()
        root_path = _write_file(
            destination, "CLAUDE.md", "# Root remains unchanged\n"
        )
        bindings = load_bindings(bindings_path)
        assert bindings is not None
        bindings["root"] = "CLAUDE.md"
        save_bindings(bindings_path, bindings)
        report_path = reconciliation_report_path(bindings_path)
        unchanged = {
            destination / "agent.md": (destination / "agent.md").read_bytes(),
            bindings_path: bindings_path.read_bytes(),
            root_path: root_path.read_bytes(),
        }

        assert not report_path.exists()
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1
        assert {path: path.read_bytes() for path in unchanged} == unchanged
        assert not report_path.exists()

    def test_check_missing_raw_destination_returns_one(self, tmp_path) -> None:
        source, destination, bindings_path = _raw_setup(
            tmp_path, destination_content=None
        )
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1

    def test_check_missing_raw_source_returns_one_without_writing_targets(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = _raw_setup(tmp_path)
        (source / "opencode.jsonc").unlink()
        root_text = "# Root remains unchanged\n"
        root_path = _write_file(destination, "CLAUDE.md", root_text)
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
        assert main(_check_args(source, destination, bindings_path, REV_A)) == 1
        assert {path: path.read_bytes() for path in unchanged} == unchanged
        assert not report_path.exists()
