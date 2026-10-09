"""Registration behavior tests for script-managed `init` bindings."""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import (
    DEST_PLAIN,
    REV_A,
    REV_B,
    SOURCE_MARKED,
    SOURCE_NO_MARKERS,
    _binding_entry,
    _bindings_with_entries,
    _init_args,
    _write_bytes_file,
    _write_file,
    uc,
)


class InitBindingRegistrationTests:
    """Verify init binding options enroll and register safely."""

    def _run_init(
        self,
        source: Path,
        destination: Path,
        bindings_path: Path,
        options: list[tuple[str, str]],
    ) -> int:
        args = _init_args(source, destination, bindings_path, REV_A)
        for option, spec in options:
            args.extend([option, spec])
        return uc.main(args)

    def _snapshot(self, paths: list[Path]) -> dict[Path, bytes]:
        return {path: path.read_bytes() for path in paths}

    def test_mixed_region_and_raw_enrollment_is_idempotent(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "existing.md", SOURCE_MARKED)
        _write_file(source, "new-agent.md", SOURCE_NO_MARKERS)
        raw_bytes = b'{"setting": "raw"}\n\xff'
        _write_bytes_file(source, "raw/opencode.jsonc", raw_bytes)
        _write_file(destination, "existing.md", SOURCE_MARKED)
        _write_file(destination, "new-agent.md", DEST_PLAIN)
        _write_bytes_file(destination, "opencode.jsonc", b"stale raw bytes\n")
        root_path = _write_file(destination, "CLAUDE.md", "# Destination root\n")
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_with_entries(
                REV_B,
                [_binding_entry("existing.md", ["existing.md"])],
                ["existing.md", "opencode.jsonc", "legacy.md"],
                "CLAUDE.md",
            ),
        )
        options = [
            ("--bind", "new-agent.md=new-agent.md"),
            ("--bind", "new-agent.md=new-agent.md"),
            ("--bind-raw", "raw/opencode.jsonc=opencode.jsonc"),
            ("--bind-raw", "raw/opencode.jsonc=opencode.jsonc"),
        ]

        assert self._run_init(source, destination, bindings_path, options) == 0

        updated = uc.load_bindings(bindings_path)
        assert updated is not None
        assert updated["bindings"] == [
            _binding_entry("existing.md", ["existing.md"]),
            _binding_entry("new-agent.md", ["new-agent.md"]),
            _binding_entry("raw/opencode.jsonc", ["opencode.jsonc"], "raw"),
        ]
        assert len(updated["bindings"]) == 3
        assert updated["pending"] == ["existing.md", "legacy.md", "new-agent.md"]
        serialized = bindings_path.read_text(encoding="utf-8")
        assert serialized.count("source:") == 3
        assert serialized.count("mode: raw") == 1
        assert "mode: region" not in serialized
        assert (destination / "opencode.jsonc").read_bytes() == raw_bytes
        assert uc.RECONCILE_BEGIN in root_path.read_text(encoding="utf-8")
        report_path = tmp_path / "reconciliation" / "init.yaml"
        report = report_path.read_text(encoding="utf-8")
        assert "destination: new-agent.md" in report
        assert "destination: opencode.jsonc" not in report
        assert report.count("action: initialized") == 1

        first_state = self._snapshot(
            [
                bindings_path,
                root_path,
                report_path,
                source / "existing.md",
                source / "new-agent.md",
                source / "raw/opencode.jsonc",
                destination / "new-agent.md",
                destination / "opencode.jsonc",
            ]
        )
        assert self._run_init(source, destination, bindings_path, options) == 0
        assert self._snapshot(list(first_state)) == first_state
