"""Behavior tests for missing `apply` inputs."""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import (
    DEST_MARKED,
    REV_A,
    REV_B,
    SOURCE_MARKED,
    _apply_args,
    _bindings_document,
    _raw_setup,
    _write_file,
    uc,
)


class ApplyMissingInputsTests:
    """Verify `apply` fails closed when a region or raw input is missing."""

    def _setup(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", DEST_MARKED)
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
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
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["present.md", "absent.md"]),
        )

        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 1
        assert present.read_text(encoding="utf-8") == DEST_MARKED
        assert not (destination / "absent.md").exists()
        updated = uc.load_bindings(bindings_path)
        assert updated is not None
        assert updated["core_revision"] == REV_B

    def test_apply_missing_raw_destination_returns_one(self, tmp_path: Path) -> None:
        source, destination, bindings_path = _raw_setup(
            tmp_path, destination_content=None
        )
        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 1

    def test_apply_missing_raw_source_returns_one_without_writing_targets(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = _raw_setup(tmp_path)
        (source / "opencode.jsonc").unlink()
        root_path = _write_file(
            destination, "CLAUDE.md", "# Root remains unchanged\n"
        )
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
        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 1
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
        bindings = uc.load_bindings(bindings_path)
        assert bindings is not None
        bindings["root"] = "CLAUDE.md"
        bindings["pending"] = ["agent.md"]
        uc.save_bindings(bindings_path, bindings)
        report_path = uc.reconciliation_report_path(bindings_path)
        unchanged = {
            destination / "agent.md": (destination / "agent.md").read_bytes(),
            bindings_path: bindings_path.read_bytes(),
            root_path: root_path.read_bytes(),
        }

        assert not report_path.exists()
        assert uc.main(_apply_args(source, destination, bindings_path, REV_A)) == 1
        assert {path: path.read_bytes() for path in unchanged} == unchanged
        assert not report_path.exists()
