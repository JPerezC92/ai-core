"""Behavior tests for the source distribution-clearance gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from _core_sync_testkit import (
    RAW_SOURCE_BYTES,
    REV_A,
    SOURCE_MARKED,
    _apply_args,
    _binding_entry,
    _bindings_document,
    _bindings_with_entries,
    _check_args,
    _init_args,
    _write_bytes_file,
    _write_file,
    uc,
)

COMMANDS = ("check", "apply", "init")


def _command_args(
    command: str, source: Path, destination: Path, bindings: Path
) -> list[str]:
    """Build the requested command's standard fixture arguments."""
    builders = {
        "check": _check_args,
        "apply": _apply_args,
        "init": _init_args,
    }
    return builders[command](source, destination, bindings, REV_A)


def _region_fixture(
    tmp_path: Path, pending: list[str] | None = None
) -> tuple[Path, Path, Path]:
    """Build marked region files plus root, bindings, and report fixtures."""
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    _write_file(source, "agent.md", SOURCE_MARKED)
    _write_file(destination, "agent.md", SOURCE_MARKED)
    _write_file(destination, "root.md", "# Root runtime\n")
    bindings_path = tmp_path / ".aicore" / "core.yaml"
    bindings_path.parent.mkdir(parents=True, exist_ok=True)
    uc.save_bindings(
        bindings_path,
        _bindings_document(
            REV_A,
            "agent.md",
            ["agent.md"],
            pending=pending,
            root="root.md",
        ),
    )
    _write_file(
        tmp_path,
        ".aicore/reconciliation/init.yaml",
        "existing reconciliation report\n",
    )
    return source, destination, bindings_path


def _raw_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Build raw source/destination files and a stale-blocker root fixture."""
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    _write_bytes_file(source, "payload.bin", RAW_SOURCE_BYTES)
    _write_bytes_file(destination, "payload.bin", RAW_SOURCE_BYTES)
    root_text = uc.sync_reconciliation_blocker("# Root runtime\n", ["payload.bin"])
    _write_file(destination, "root.md", root_text)
    bindings_path = tmp_path / ".aicore" / "core.yaml"
    bindings_path.parent.mkdir(parents=True, exist_ok=True)
    uc.save_bindings(
        bindings_path,
        _bindings_with_entries(
            REV_A,
            [_binding_entry("payload.bin", ["payload.bin"], "raw")],
            pending=["payload.bin"],
            root="root.md",
        ),
    )
    _write_file(
        tmp_path,
        ".aicore/reconciliation/init.yaml",
        "existing reconciliation report\n",
    )
    return source, destination, bindings_path


def _set_clearance(source: Path, paths: list[str]) -> Path:
    """Write a valid schema-1 clearance file for a fixture source."""
    clearance_path = source / uc.CLEARANCE_REL
    clearance_path.write_text(
        json.dumps({"schema": 1, "cleared": paths}, indent=2) + "\n",
        encoding="utf-8",
    )
    return clearance_path


def _raw_success_fixture(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Build cleared identical raw payloads without a bound root or blocker."""
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    _write_bytes_file(source, "payload.bin", RAW_SOURCE_BYTES)
    _write_bytes_file(destination, "payload.bin", RAW_SOURCE_BYTES)
    _set_clearance(source, ["payload.bin"])

    bindings_path = tmp_path / ".aicore" / "core.yaml"
    bindings_path.parent.mkdir(parents=True, exist_ok=True)
    uc.save_bindings(
        bindings_path,
        _bindings_with_entries(
            REV_A,
            [_binding_entry("payload.bin", ["payload.bin"], "raw")],
            pending=[],
        ),
    )
    return source, destination, bindings_path


def _protected_paths(
    source: Path, destination: Path, bindings: Path, payload: str
) -> list[Path]:
    """Return payload and metadata targets whose bytes must remain unchanged."""
    return [
        destination / payload,
        destination / "root.md",
        bindings,
        uc.reconciliation_report_path(bindings),
        source / uc.CLEARANCE_REL,
    ]


def _snapshot(paths: list[Path]) -> dict[Path, bytes | None]:
    """Capture existing bytes or absence for protected fixture paths."""
    return {
        path: path.read_bytes() if path.exists() else None for path in paths
    }


def _assert_unchanged(paths: list[Path], before: dict[Path, bytes | None]) -> None:
    """Assert that protected files and their existence remain unchanged."""
    assert _snapshot(paths) == before


def _install_payload_read_spies(
    monkeypatch: pytest.MonkeyPatch,
) -> list[str]:
    """Make any bound-source payload read fail and return invocation records."""
    invoked: list[str] = []

    def fail_core(path: Path) -> str | None:
        invoked.append(f"region:{path}")
        raise AssertionError("region payload read before clearance gate")

    def fail_raw(path: Path) -> bytes | None:
        invoked.append(f"raw:{path}")
        raise AssertionError("raw payload read before clearance gate")

    monkeypatch.setattr(uc, "read_source_core", fail_core)
    monkeypatch.setattr(uc, "read_source_raw", fail_raw)
    return invoked


class DistributionClearanceTests:
    @pytest.mark.parametrize("command", COMMANDS)
    def test_uncleared_region_source_is_rejected_without_writes(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        command: str,
    ) -> None:
        source, destination, bindings = _region_fixture(
            tmp_path, pending=["agent.md"]
        )
        _set_clearance(source, [])
        protected = _protected_paths(source, destination, bindings, "agent.md")
        before = _snapshot(protected)

        assert uc.main(_command_args(command, source, destination, bindings)) == 1

        assert "source not cleared for distribution: agent.md" in capsys.readouterr().err
        _assert_unchanged(protected, before)

    def test_raw_binding_source_omitted_from_clearance_is_rejected(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        source, destination, bindings = _raw_fixture(tmp_path)
        _set_clearance(source, [])
        protected = _protected_paths(source, destination, bindings, "payload.bin")
        before = _snapshot(protected)

        assert uc.main(_check_args(source, destination, bindings, REV_A)) == 1

        assert "source not cleared for distribution: payload.bin" in capsys.readouterr().err
        _assert_unchanged(protected, before)

    def test_multiple_uncleared_sources_are_reported_once_in_binding_order(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        source, destination, bindings = _region_fixture(tmp_path)
        bound_sources = [
            "zulu.md",
            "allowed.md",
            "alpha.md",
            "zulu.md",
            "mu.md",
            "alpha.md",
        ]
        for source_name in ("zulu.md", "allowed.md", "alpha.md", "mu.md"):
            _write_file(source, source_name, SOURCE_MARKED)

        entries = [
            _binding_entry(source_name, [f"destination-{index}.md"])
            for index, source_name in enumerate(bound_sources, start=1)
        ]
        for entry in entries:
            _write_file(
                destination, entry["destinations"][0], SOURCE_MARKED
            )
        uc.save_bindings(
            bindings,
            _bindings_with_entries(REV_A, entries, pending=[], root="root.md"),
        )
        _set_clearance(source, ["allowed.md"])

        assert uc.main(_check_args(source, destination, bindings, REV_A)) == 1

        error = capsys.readouterr().err
        assert error == (
            "source not cleared for distribution: zulu.md, alpha.md, mu.md\n"
        )
        reported_sources = error.removeprefix(
            "source not cleared for distribution: "
        ).strip().split(", ")
        assert reported_sources == ["zulu.md", "alpha.md", "mu.md"]
        assert len(reported_sources) == len(set(reported_sources))

    @pytest.mark.parametrize("command", COMMANDS)
    def test_cleared_region_source_proceeds_past_gate(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        command: str,
    ) -> None:
        source, destination, bindings = _region_fixture(tmp_path)

        assert uc.main(_command_args(command, source, destination, bindings)) == 0
        assert capsys.readouterr().out == {
            "check": "current\n",
            "apply": "applied\n",
            "init": "initialized\n",
        }[command]

    @pytest.mark.parametrize("command", COMMANDS)
    def test_cleared_raw_source_proceeds_past_gate(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        command: str,
    ) -> None:
        source, destination, bindings = _raw_success_fixture(tmp_path)
        assert (source / "payload.bin").read_bytes() == (
            destination / "payload.bin"
        ).read_bytes()
        assert json.loads(
            (source / uc.CLEARANCE_REL).read_text(encoding="utf-8")
        ) == {"schema": 1, "cleared": ["payload.bin"]}

        assert uc.main(_command_args(command, source, destination, bindings)) == 0
        assert capsys.readouterr().out == {
            "check": "current\n",
            "apply": "applied\n",
            "init": "initialized\n",
        }[command]

    @pytest.mark.parametrize("command", COMMANDS)
    @pytest.mark.parametrize("mode", ["region", "raw"])
    def test_uncleared_source_is_rejected_before_payload_read(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
        command: str,
        mode: str,
    ) -> None:
        if mode == "region":
            source, destination, bindings = _region_fixture(
                tmp_path, pending=["agent.md"]
            )
            payload = "agent.md"
        else:
            source, destination, bindings = _raw_fixture(tmp_path)
            payload = "payload.bin"
        _set_clearance(source, [])
        protected = _protected_paths(source, destination, bindings, payload)
        before = _snapshot(protected)
        invoked = _install_payload_read_spies(monkeypatch)

        assert uc.main(_command_args(command, source, destination, bindings)) == 1

        assert f"source not cleared for distribution: {payload}" in capsys.readouterr().err
        assert invoked == []
        _assert_unchanged(protected, before)

    @pytest.mark.parametrize("command", COMMANDS)
    @pytest.mark.parametrize("mode", ("region", "raw"))
    def test_missing_clearance_is_rejected_before_payload_read_or_write(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
        command: str,
        mode: str,
    ) -> None:
        if mode == "region":
            source, destination, bindings = _region_fixture(
                tmp_path, pending=["agent.md"]
            )
            payload = "agent.md"
        else:
            source, destination, bindings = _raw_fixture(tmp_path)
            payload = "payload.bin"
        clearance_path = source / uc.CLEARANCE_REL
        clearance_path.unlink()
        protected = _protected_paths(source, destination, bindings, payload)
        before = _snapshot(protected)
        invoked = _install_payload_read_spies(monkeypatch)

        assert uc.main(_command_args(command, source, destination, bindings)) == 1

        assert (
            f"missing clearance file: {clearance_path}"
            in capsys.readouterr().err
        )
        assert invoked == []
        _assert_unchanged(protected, before)

    @pytest.mark.parametrize("command", COMMANDS)
    @pytest.mark.parametrize("mode", ("region", "raw"))
    @pytest.mark.parametrize(
        "malformed",
        [
            pytest.param("{not-json\n", id="invalid-json"),
            pytest.param('{"schema":2,"cleared":[]}\n', id="invalid-schema"),
            pytest.param('{"schema":1,"cleared":[7]}\n', id="non-string-path"),
        ],
    )
    def test_malformed_clearance_is_rejected_before_payload_read_or_write(
        self,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
        monkeypatch: pytest.MonkeyPatch,
        command: str,
        mode: str,
        malformed: str,
    ) -> None:
        if mode == "region":
            source, destination, bindings = _region_fixture(
                tmp_path, pending=["agent.md"]
            )
            payload = "agent.md"
        else:
            source, destination, bindings = _raw_fixture(tmp_path)
            payload = "payload.bin"
        clearance_path = source / uc.CLEARANCE_REL
        clearance_path.write_text(malformed, encoding="utf-8")
        protected = _protected_paths(source, destination, bindings, payload)
        before = _snapshot(protected)
        invoked = _install_payload_read_spies(monkeypatch)

        assert uc.main(_command_args(command, source, destination, bindings)) == 2

        assert (
            f"invalid clearance file: {clearance_path}"
            in capsys.readouterr().err
        )
        assert invoked == []
        _assert_unchanged(protected, before)
