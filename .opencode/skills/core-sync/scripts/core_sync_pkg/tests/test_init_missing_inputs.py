"""Behavior tests for missing `init` inputs."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    DEST_PLAIN,
    RAW_SOURCE_BYTES,
    REV_A,
    REV_B,
    SOURCE_NO_MARKERS,
    created_region,
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
    """Verify `init` recreates declared destinations absent from disk.

    The repair is scoped to the bindings file: a mapping whose source is not
    distributable is refused and nothing is created.
    """

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

    def test_init_recreates_an_absent_region_destination(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_NO_MARKERS)
        _write_file(destination, "present.md", DEST_PLAIN)
        _write_file(destination, "CLAUDE.md", "# Root remains unchanged\n")
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

        assert main(_init_args(source, destination, bindings_path, REV_A)) == 0
        assert (destination / "missing.md").read_text(encoding="utf-8") == (
            created_region(
                "---\nname: src\n---\n",
                "\nCore body one\nCore body two\n",
            )
        )
        updated = load_bindings(bindings_path)
        assert updated is not None
        assert updated["pending"] == ["present.md", "missing.md"]

    def test_init_recreates_an_absent_stored_raw_target(
        self, tmp_path: Path
    ) -> None:
        source, destination, bindings_path = _raw_setup(
            tmp_path, destination_content=None
        )
        _write_file(destination, "CLAUDE.md", "# Root remains unchanged\n")
        bindings = load_bindings(bindings_path)
        assert bindings is not None
        bindings["root"] = "CLAUDE.md"
        save_bindings(bindings_path, bindings)
        destination_path = destination / "opencode.jsonc"
        args = _init_args(source, destination, bindings_path, REV_A)
        args.extend(["--bind-raw", "opencode.jsonc=opencode.jsonc"])

        assert not destination_path.exists()
        assert main(args) == 0
        assert destination_path.read_bytes() == RAW_SOURCE_BYTES

    def test_init_creates_a_missing_parent_for_an_absent_raw_target(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_bytes_file(source, "payload.bin", b"\x00raw\xff\r\n")
        destination.mkdir()
        _write_file(destination, "CLAUDE.md", "# Root remains unchanged\n")
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(
            bindings_path,
            _bindings_with_entries(
                REV_B,
                [_binding_entry("payload.bin", ["nested/payload.bin"], "raw")],
                root="CLAUDE.md",
            ),
        )
        destination_path = destination / "nested" / "payload.bin"

        assert not (destination / "nested").exists()
        assert main(_init_args(source, destination, bindings_path, REV_A)) == 0
        assert destination_path.read_bytes() == b"\x00raw\xff\r\n"

    def test_init_refuses_an_absent_destination_without_a_cleared_source(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_bytes_file(source, "payload.bin", b"\x00raw\xff\r\n")
        destination.mkdir()
        bindings_path = tmp_path / "bindings.yaml"
        save_bindings(bindings_path, _bindings_with_entries(REV_B, []))
        args = _init_args(source, destination, bindings_path, REV_A)
        args.extend(["--bind", "other.md=other.md"])

        assert main(args) == 1
        assert not (destination / "other.md").exists()
        updated = load_bindings(bindings_path)
        assert updated is not None
        assert updated["bindings"] == []

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
