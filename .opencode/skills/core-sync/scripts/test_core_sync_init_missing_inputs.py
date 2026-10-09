"""Behavior tests for missing `init` inputs."""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import (
    DEST_PLAIN,
    REV_A,
    REV_B,
    SOURCE_NO_MARKERS,
    _bindings_document,
    _init_args,
    _raw_setup,
    _write_file,
    uc,
)


class InitMissingInputsTests:
    """Verify `init` leaves targets unchanged when region or raw inputs are missing."""

    def _setup(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_NO_MARKERS)
        _write_file(destination, "agent.md", DEST_PLAIN)
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(REV_B, "agent.md", ["agent.md"]),
        )
        return source, destination, bindings_path

    def test_init_missing_source_returns_one_without_writing_targets(
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
        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 1
        assert {path: path.read_bytes() for path in unchanged} == unchanged
        assert not report_path.exists()

    def test_init_missing_region_destination_returns_one_without_writing_targets(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_NO_MARKERS)
        present_path = _write_file(destination, "present.md", DEST_PLAIN)
        root_path = _write_file(
            destination, "CLAUDE.md", "# Root remains unchanged\n"
        )
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_document(
                REV_B,
                "agent.md",
                ["present.md", "missing.md"],
                root="CLAUDE.md",
            ),
        )
        report_path = _write_file(
            tmp_path,
            "reconciliation/init.yaml",
            "Existing report remains unchanged\n",
        )
        unchanged = {
            present_path: present_path.read_bytes(),
            bindings_path: bindings_path.read_bytes(),
            root_path: root_path.read_bytes(),
            report_path: report_path.read_bytes(),
        }

        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 1
        assert {path: path.read_bytes() for path in unchanged} == unchanged
        assert not (destination / "missing.md").exists()

    def test_init_missing_stored_raw_target_returns_one_without_writes(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = _raw_setup(
            tmp_path, destination_content=None
        )
        root_path = _write_file(
            destination, "CLAUDE.md", "# Root remains unchanged\n"
        )
        bindings = uc.load_bindings(bindings_path)
        assert bindings is not None
        bindings["root"] = "CLAUDE.md"
        uc.save_bindings(bindings_path, bindings)
        source_path = source / "opencode.jsonc"
        destination_path = destination / "opencode.jsonc"
        report_path = uc.reconciliation_report_path(bindings_path)
        unchanged = {
            source_path: source_path.read_bytes(),
            bindings_path: bindings_path.read_bytes(),
            root_path: root_path.read_bytes(),
        }
        args = _init_args(source, destination, bindings_path, REV_A)
        args.extend(["--bind-raw", "opencode.jsonc=opencode.jsonc"])

        assert not destination_path.exists()
        assert not report_path.exists()
        assert uc.main(args) == 1
        assert {path: path.read_bytes() for path in unchanged} == unchanged
        assert not destination_path.exists()
        assert not report_path.exists()

    def test_init_missing_raw_source_returns_one_without_writing_targets(
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
        assert uc.main(_init_args(source, destination, bindings_path, REV_A)) == 1
        assert {path: path.read_bytes() for path in unchanged} == unchanged
        assert not report_path.exists()
