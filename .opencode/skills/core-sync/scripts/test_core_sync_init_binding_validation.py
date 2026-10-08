"""Syntax and path validation tests for `init` binding declarations."""

from __future__ import annotations

from pathlib import Path

from _core_sync_testkit import (
    DEST_PLAIN,
    REV_A,
    REV_B,
    SOURCE_MARKED,
    _binding_entry,
    _bindings_with_entries,
    _init_args,
    _write_file,
    uc,
)


class InitBindingValidationTests:
    """Verify malformed, noncanonical, and unsafe binding declarations."""

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

    def test_malformed_and_noncanonical_specs_return_two_without_writes(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        source_path = _write_file(source, "agent.md", SOURCE_MARKED)
        destination_path = _write_file(destination, "agent.md", DEST_PLAIN)
        root_path = _write_file(
            destination,
            "CLAUDE.md",
            uc.sync_reconciliation_blocker("# Root\n", ["agent.md"]),
        )
        bindings_path = tmp_path / "bindings.yaml"
        uc.save_bindings(
            bindings_path,
            _bindings_with_entries(
                REV_B,
                [_binding_entry("agent.md", ["agent.md"])],
                ["agent.md"],
                "CLAUDE.md",
            ),
        )
        report_path = tmp_path / "reconciliation" / "init.yaml"
        _write_file(tmp_path, "reconciliation/init.yaml", "unchanged report\n")
        unchanged = self._snapshot(
            [bindings_path, destination_path, root_path, report_path, source_path]
        )
        invalid_options = [
            ("--bind", "missing-equals"),
            ("--bind", "agent.md=dest.md=extra"),
            ("--bind", "=dest.md"),
            ("--bind", "agent.md="),
            ("--bind", "../source.md=dest.md"),
            ("--bind", "source.md=../dest.md"),
            ("--bind-raw", "/source.md=dest.md"),
            ("--bind-raw", "source\x00name=dest.md"),
        ]
        noncanonical_paths = (
            ".",
            "./agent.md",
            "docs/./file.md",
            "docs//file.md",
            "docs/file.md/",
            "docs\\file.md",
            "/docs/file.md",
            "\\docs\\file.md",
            "C:/docs/file.md",
            "C:docs/file.md",
            "//server/share/file.md",
        )
        invalid_options.extend(
            ("--bind", f"{path}=agent.md") for path in noncanonical_paths
        )
        invalid_options.extend(
            ("--bind", f"agent.md={path}") for path in noncanonical_paths
        )

        for option, spec in invalid_options:
            assert self._run_init(
                source, destination, bindings_path, [(option, spec)]
            ) == 2
            assert self._snapshot(list(unchanged)) == unchanged

    def test_canonical_relative_posix_paths_remain_valid(self) -> None:
        valid_mappings = (
            ("AGENTS.md", ".opencode/agents/lumen.md"),
            (".opencode/agents/lumen.md", "docs/file.md"),
        )

        for source, destination in valid_mappings:
            assert uc._parse_init_binding_spec(
                f"{source}={destination}", uc.MODE_REGION
            ) == (source, destination, uc.MODE_REGION)
