"""Tests for safe enrollment of new raw-mode binding targets."""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import (
    DEST_PLAIN,
    REV_A,
    REV_B,
    SOURCE_NO_MARKERS,
    _binding_entry,
    _bindings_with_entries,
    _init_args,
    _write_bytes_file,
    _write_file,
    uc,
)


class RawInitEnrollmentTests:
    def test_new_raw_declaration_creates_missing_target_byte_exactly(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        raw_bytes = b'{\r\n  "payload": "raw"\r\n}\n\xff\x00'
        _write_bytes_file(source, "git-pr-drafting.md", raw_bytes)
        (destination / "user-stories").mkdir(parents=True)
        root_path = _write_file(destination, "CLAUDE.md", "# Root remains unchanged\n")
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_with_entries(REV_B, [], root="CLAUDE.md"),
        )
        destination_path = destination / "user-stories/git-pr-drafting.md"
        report_path = uc.reconciliation_report_path(bindings_path)
        args = _init_args(source, destination, bindings_path, REV_A)
        args.extend(
            [
                "--bind-raw",
                "git-pr-drafting.md=user-stories/git-pr-drafting.md",
                "--bind-raw",
                "git-pr-drafting.md=user-stories/git-pr-drafting.md",
            ]
        )

        assert not destination_path.exists()
        assert uc.main(args) == 0

        updated = uc.load_bindings(bindings_path)
        assert updated is not None
        assert updated["bindings"] == [
            _binding_entry(
                "git-pr-drafting.md", ["user-stories/git-pr-drafting.md"], "raw"
            )
        ]
        assert updated["pending"] == []
        assert destination_path.read_bytes() == raw_bytes
        assert root_path.read_bytes() == b"# Root remains unchanged\n"
        assert not report_path.exists()

    def test_new_raw_destination_parent_missing_returns_one_without_writes(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        source_region = _write_file(source, "agent.md", SOURCE_NO_MARKERS)
        source_raw = _write_bytes_file(source, "payload.bin", b"\x00raw\xff\r\n")
        destination_region = _write_file(destination, "agent.md", DEST_PLAIN)
        root_path = _write_file(
            destination, "CLAUDE.md", "# Root remains unchanged\n"
        )
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_with_entries(
                REV_B,
                [_binding_entry("agent.md", ["agent.md"])],
                root="CLAUDE.md",
            ),
        )
        report_path = uc.reconciliation_report_path(bindings_path)
        missing_parent = destination / "new-stories"
        destination_path = missing_parent / "payload.bin"
        unchanged = {
            source_region: source_region.read_bytes(),
            source_raw: source_raw.read_bytes(),
            destination_region: destination_region.read_bytes(),
            root_path: root_path.read_bytes(),
            bindings_path: bindings_path.read_bytes(),
        }
        args = _init_args(source, destination, bindings_path, REV_A)
        args.extend(["--bind-raw", "payload.bin=new-stories/payload.bin"])

        assert not missing_parent.exists()
        assert not report_path.exists()
        assert uc.main(args) == 1
        assert {path: path.read_bytes() for path in unchanged} == unchanged
        assert not missing_parent.exists()
        assert not destination_path.exists()
        assert not report_path.exists()
