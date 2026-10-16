"""Behavior tests for missing `init` inputs."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    DEST_PLAIN,
    REV_A,
    REV_B,
    SOURCE_NO_MARKERS,
    _binding_entry,
    _bindings_document,
    _bindings_with_entries,
    _init_args,
    _raw_setup,
    _write_bytes_file,
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


class InitMissingInputsTests:
    """Verify `init` leaves targets unchanged when region or raw inputs are missing."""

    def _setup(self, tmp_path: Path) -> tuple[Path, Path, Path]:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_NO_MARKERS)
        _write_file(destination, "agent.md", DEST_PLAIN)
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
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
        assert main(_init_args(source, destination, bindings_path, REV_A)) == 1
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
        save_bindings(
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

        assert main(_init_args(source, destination, bindings_path, REV_A)) == 1
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
        bindings = load_bindings(bindings_path)
        assert bindings is not None
        bindings["root"] = "CLAUDE.md"
        save_bindings(bindings_path, bindings)
        source_path = source / "opencode.jsonc"
        destination_path = destination / "opencode.jsonc"
        report_path = reconciliation_report_path(bindings_path)
        unchanged = {
            source_path: source_path.read_bytes(),
            bindings_path: bindings_path.read_bytes(),
            root_path: root_path.read_bytes(),
        }
        args = _init_args(source, destination, bindings_path, REV_A)
        args.extend(["--bind-raw", "opencode.jsonc=opencode.jsonc"])

        assert not destination_path.exists()
        assert not report_path.exists()
        assert main(args) == 1
        assert {path: path.read_bytes() for path in unchanged} == unchanged
        assert not destination_path.exists()
        assert not report_path.exists()

    def test_init_missing_raw_destination_parent_returns_one_without_creating_tree(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_bytes_file(source, "payload.bin", b"\x00raw\xff\r\n")
        destination.mkdir()
        root_path = _write_file(
            destination, "CLAUDE.md", "# Root remains unchanged\n"
        )
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_with_entries(
                REV_B,
                [_binding_entry("payload.bin", ["nested/payload.bin"], "raw")],
                root="CLAUDE.md",
            ),
        )
        missing_parent = destination / "nested"
        destination_path = missing_parent / "payload.bin"
        report_path = reconciliation_report_path(bindings_path)
        unchanged = {
            root_path: root_path.read_bytes(),
            bindings_path: bindings_path.read_bytes(),
        }

        assert not missing_parent.exists()
        assert not report_path.exists()
        assert main(_init_args(source, destination, bindings_path, REV_A)) == 1
        assert {path: path.read_bytes() for path in unchanged} == unchanged
        assert sorted(path.name for path in destination.iterdir()) == ["CLAUDE.md"]
        assert not missing_parent.exists()
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
        assert main(_init_args(source, destination, bindings_path, REV_A)) == 1
        assert {path: path.read_bytes() for path in unchanged} == unchanged
        assert not report_path.exists()
