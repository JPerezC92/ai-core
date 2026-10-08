"""Destination and declaration conflict tests for `init` bindings."""

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
    _write_file,
    uc,
)


class InitBindingConflictTests:
    """Verify conflicting binding metadata/mappings for one destination (different source or mode) are rejected without writes."""

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

    def test_conflicting_or_aliased_destination_claims_return_two_without_writes(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        old_source_path = _write_file(source, "old-source.md", SOURCE_NO_MARKERS)
        new_source_path = _write_file(source, "new-source.md", SOURCE_NO_MARKERS)
        destination_path = _write_file(destination, "claimed.md", DEST_PLAIN)
        duplicate_source_path = _write_file(
            destination, "duplicate-source.md", DEST_PLAIN
        )
        duplicate_mode_path = _write_file(destination, "duplicate-mode.md", DEST_PLAIN)
        aliased_destination_path = _write_file(
            destination, "docs/a.md", DEST_PLAIN
        )
        root_path = _write_file(
            destination,
            "CLAUDE.md",
            uc.sync_reconciliation_blocker("# Root\n", ["kept.md"]),
        )
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_with_entries(
                REV_B,
                [_binding_entry("old-source.md", ["claimed.md"])],
                ["kept.md"],
                "CLAUDE.md",
            ),
        )
        report_path = tmp_path / "reconciliation" / "init.yaml"
        _write_file(tmp_path, "reconciliation/init.yaml", "unchanged report\n")
        unchanged = self._snapshot(
            [
                bindings_path,
                destination_path,
                duplicate_source_path,
                duplicate_mode_path,
                aliased_destination_path,
                root_path,
                report_path,
                old_source_path,
                new_source_path,
            ]
        )

        conflicting_declarations = [
            [("--bind", "new-source.md=claimed.md")],
            [("--bind-raw", "old-source.md=claimed.md")],
            [
                ("--bind", "old-source.md=duplicate-source.md"),
                ("--bind", "new-source.md=duplicate-source.md"),
            ],
            [
                ("--bind", "new-source.md=duplicate-mode.md"),
                ("--bind-raw", "new-source.md=duplicate-mode.md"),
            ],
            [
                ("--bind", "new-source.md=docs/a.md"),
                ("--bind", "new-source.md=docs/./a.md"),
            ],
        ]
        for declarations in conflicting_declarations:
            assert self._run_init(
                source, destination, bindings_path, declarations
            ) == 2
            assert self._snapshot(list(unchanged)) == unchanged
