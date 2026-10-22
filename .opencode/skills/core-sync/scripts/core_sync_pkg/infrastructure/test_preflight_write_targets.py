"""Integration tests for write-target preflight against a real filesystem."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    REV_A,
    SOURCE_MARKED,
    _binding_entry,
    _bindings_document,
    _bindings_with_entries,
    _write_file,
)
from core_sync_pkg.domain.constants import CommandName  # noqa: E402
from core_sync_pkg.infrastructure.filesystem import (  # noqa: E402
    preflight_write_targets,
)
from core_sync_pkg.domain.bindings import Bindings  # noqa: E402
from core_sync_pkg.infrastructure.stores import save_bindings  # noqa: E402


def _preflight(
    command: CommandName,
    source: Path,
    destination: Path,
    bindings_path: Path,
    bindings: Bindings,
    *,
    mode_of: dict[str, str] | None = None,
) -> str | None:
    return preflight_write_targets(
        command,
        source,
        destination,
        bindings_path,
        bindings,
        mode_of=mode_of,
    )


class PreflightWriteTargetsTests:
    """Reject aliased, escaped, and non-regular write targets before mutation."""

    def test_payload_escape_by_parent_segments(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", SOURCE_MARKED)
        _write_file(destination, "CLAUDE.md", "# root\n")
        bindings_path = tmp_path / "bindings.yaml"
        bindings = _bindings_document(
            REV_A, "agent.md", ["../escaped.md"], root="CLAUDE.md"
        )

        error = _preflight("apply", source, destination, bindings_path, bindings)

        assert error is not None
        assert "escapes destination root" in error

    def test_root_escape_by_parent_segments(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", SOURCE_MARKED)
        bindings_path = tmp_path / "bindings.yaml"
        bindings = _bindings_document(
            REV_A, "agent.md", ["agent.md"], root="../root.md"
        )

        error = _preflight("check", source, destination, bindings_path, bindings)

        assert error is not None
        assert "escapes destination root" in error

    def test_payload_resolves_inside_source_tree(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "CLAUDE.md", "# root\n")
        bindings_path = tmp_path / "bindings.yaml"
        bindings = _bindings_document(
            REV_A,
            "agent.md",
            [os.path.relpath(source / "agent.md", destination)],
            root="CLAUDE.md",
        )

        error = _preflight("apply", source, destination, bindings_path, bindings)

        assert error is not None
        assert "resolves inside source tree" in error

    def test_root_resolves_inside_source_tree(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(destination, "agent.md", SOURCE_MARKED)
        bindings_path = tmp_path / "bindings.yaml"
        bindings = _bindings_document(
            REV_A,
            "agent.md",
            ["agent.md"],
            root=os.path.relpath(source / "agent.md", destination),
        )

        error = _preflight("check", source, destination, bindings_path, bindings)

        assert error is not None
        assert "resolves inside source tree" in error

    def test_two_canonical_destinations_resolve_to_one_target(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "a.md", SOURCE_MARKED)
        _write_file(source, "b.md", SOURCE_MARKED)
        _write_file(destination, "same.md", SOURCE_MARKED)
        _write_file(destination, "CLAUDE.md", "# root\n")
        bindings_path = tmp_path / "bindings.yaml"
        bindings = _bindings_with_entries(
            REV_A,
            [
                _binding_entry("a.md", ["same.md"]),
                _binding_entry("b.md", ["./same.md"]),
            ],
            root="CLAUDE.md",
        )

        error = _preflight("apply", source, destination, bindings_path, bindings)

        assert error is not None
        assert "distinct write targets alias after resolution" in error

    def test_existing_directory_is_not_a_regular_file(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        (destination / "agent.md").mkdir(parents=True)
        _write_file(destination, "CLAUDE.md", "# root\n")
        bindings_path = tmp_path / "bindings.yaml"
        bindings = _bindings_document(
            REV_A, "agent.md", ["agent.md"], root="CLAUDE.md"
        )

        error = _preflight("apply", source, destination, bindings_path, bindings)

        assert error is not None
        assert "not a regular file" in error

    def test_zero_identity_does_not_alias_ordinary_or_root_raw_pair(
        self, tmp_path: Path
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        _write_file(source, "settings.jsonc", "{}\n")
        _write_file(destination, "agent.md", SOURCE_MARKED)
        _write_file(destination, "settings.jsonc", "{}\n")
        _write_file(destination, "CLAUDE.md", "# root\n")
        bindings_path = tmp_path / "bindings.yaml"
        bindings = _bindings_with_entries(
            REV_A,
            [
                _binding_entry("agent.md", ["agent.md"]),
                _binding_entry("settings.jsonc", ["settings.jsonc"], "raw"),
            ],
            root="CLAUDE.md",
        )
        real_stat = os.stat

        def zero_stat(path: str | os.PathLike[str], *, follow_symlinks: bool = True) -> Any:
            result = real_stat(path, follow_symlinks=follow_symlinks)
            return SimpleNamespace(
                st_mode=result.st_mode,
                st_dev=0,
                st_ino=0,
            )

        with patch("os.stat", side_effect=zero_stat), patch.object(
            Path, "stat", lambda self, *args, **kwargs: zero_stat(self)
        ):
            error = _preflight(
                "apply",
                source,
                destination,
                bindings_path,
                bindings,
                mode_of={"settings.jsonc": "raw"},
            )

        assert error is None

    @pytest.mark.parametrize(
        ("command", "kind"),
        (
            ("check", "root"),
            ("apply", "destination payload"),
            ("apply", "bindings"),
            ("init", "report"),
        ),
    )
    def test_stubbed_symlink_rejected_for_each_target_kind(
        self, tmp_path: Path, command: CommandName, kind: str
    ) -> None:
        source = tmp_path / "source"
        destination = tmp_path / "destination"
        _write_file(source, "agent.md", SOURCE_MARKED)
        payload = _write_file(destination, "agent.md", SOURCE_MARKED)
        root_path = _write_file(destination, "CLAUDE.md", "# root\n")
        bindings_path = tmp_path / "bindings.yaml"
        bindings = _bindings_document(
            REV_A, "agent.md", ["agent.md"], root="CLAUDE.md"
        )
        save_bindings(bindings_path, bindings)
        report_path = tmp_path / "reconciliation" / "init.yaml"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text("report\n", encoding="utf-8", newline="\n")
        kind_paths = {
            "root": root_path,
            "destination payload": payload,
            "bindings": bindings_path,
            "report": report_path,
        }
        linked = kind_paths[kind]
        original = Path.is_symlink

        def stub_is_symlink(self: Path) -> bool:
            if self == linked:
                return True
            return original(self)

        with patch.object(Path, "is_symlink", stub_is_symlink):
            error = _preflight(command, source, destination, bindings_path, bindings)

        assert error is not None
        assert "symbolic link" in error
        assert kind in error
