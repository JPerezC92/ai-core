"""Behavior tests for missing `check` inputs."""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import (
    REV_A,
    SOURCE_MARKED,
    _bindings_document,
    _check_args,
    _raw_setup,
    _write_file,
    uc,
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
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_A, "agent.md", ["agent.md"], pending),
        )
        return source, destination, bindings_path

    def test_missing_destination_returns_one(self, tmp_path: Path) -> None:
        source, destination, bindings_path = self._setup(tmp_path)
        (destination / "agent.md").unlink()
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 1

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
        bindings = uc.load_bindings(bindings_path)
        assert bindings is not None
        bindings["root"] = "CLAUDE.md"
        uc.save_bindings(bindings_path, bindings)
        report_path = uc.reconciliation_report_path(bindings_path)
        unchanged = {
            destination / "agent.md": (destination / "agent.md").read_bytes(),
            bindings_path: bindings_path.read_bytes(),
            root_path: root_path.read_bytes(),
        }

        assert not report_path.exists()
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 1
        assert {path: path.read_bytes() for path in unchanged} == unchanged
        assert not report_path.exists()

    def test_check_missing_raw_destination_returns_one(self, tmp_path) -> None:
        source, destination, bindings_path = _raw_setup(
            tmp_path, destination_content=None
        )
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 1

    def test_check_missing_raw_source_returns_one_without_writing_targets(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = _raw_setup(tmp_path)
        (source / "opencode.jsonc").unlink()
        root_text = "# Root remains unchanged\n"
        root_path = _write_file(destination, "CLAUDE.md", root_text)
        bindings = uc.load_bindings(bindings_path)
        assert bindings is not None
        bindings["root"] = "CLAUDE.md"
        uc.save_bindings(bindings_path, bindings)
        report_path = uc.reconciliation_report_path(bindings_path)
        unchanged = {
            destination / "opencode.jsonc": (
                destination / "opencode.jsonc"
            ).read_bytes(),
            bindings_path: bindings_path.read_bytes(),
            root_path: root_path.read_bytes(),
        }

        assert not report_path.exists()
        assert uc.main(_check_args(source, destination, bindings_path, REV_A)) == 1
        assert {path: path.read_bytes() for path in unchanged} == unchanged
        assert not report_path.exists()
