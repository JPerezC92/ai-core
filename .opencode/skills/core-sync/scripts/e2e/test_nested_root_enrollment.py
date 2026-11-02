"""Exercise generic nested raw-root enrollment through the core-sync CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

from _test_support import NestedRootData, create


def _create_fixture(tmp_path: Path, data: NestedRootData) -> tuple[Path, Path, Path]:
    """Create a cleared generic root and isolated source and destination trees."""
    source = tmp_path / "source"
    destination = tmp_path / "destination"
    source.mkdir()
    destination.mkdir()
    for relative, content in (data["payloads"] | data["excluded"]).items():
        path = source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    (source / "distribution-clearance.json").write_text(
        json.dumps(data["clearance"]),
        encoding="utf-8",
    )
    return source, destination, tmp_path / "bindings.yaml"


def _arguments(command: str, source: Path, destination: Path, bindings: Path) -> list[str]:
    """Create CLI arguments against the isolated fixture."""
    return [
        sys.executable, str(Path(__file__).resolve().parent.parent / "core_sync.py"),
        command,
        "--source", str(source),
        "--destination", str(destination),
        "--bindings", str(bindings),
        "--source-revision", "a" * 40,
    ]


def test_nested_root_enrollment_requires_init_for_new_files(tmp_path: Path) -> None:
    data = create()
    source, destination, bindings = _create_fixture(tmp_path, data)
    payloads = data["payloads"]
    init = _arguments("init", source, destination, bindings) + ["--bind-cleared"]
    clearance = json.loads((source / "distribution-clearance.json").read_text(encoding="utf-8"))
    assert clearance == data["clearance"]

    assert subprocess.run(init, capture_output=True, check=False).returncode == 0
    for relative, content in payloads.items():
        assert (destination / relative).read_bytes() == content
    for relative in data["excluded"]:
        assert not (destination / relative).exists()
    initial = yaml.safe_load(bindings.read_text(encoding="utf-8"))
    assert {entry["source"] for entry in initial["bindings"]} == set(payloads)

    later, later_bytes = data["later_path"], data["later_bytes"]
    later_source = source / later
    later_source.parent.mkdir(parents=True, exist_ok=True)
    later_source.write_bytes(later_bytes)

    apply = _arguments("apply", source, destination, bindings)
    assert subprocess.run(apply, capture_output=True, check=False).returncode == 0
    assert not (destination / later).exists()
    after_apply = yaml.safe_load(bindings.read_text(encoding="utf-8"))
    assert {entry["source"] for entry in after_apply["bindings"]} == set(payloads)

    assert subprocess.run(init, capture_output=True, check=False).returncode == 0
    assert (destination / later).read_bytes() == later_bytes
    updated = yaml.safe_load(bindings.read_text(encoding="utf-8"))
    assert {entry["source"] for entry in updated["bindings"]} == set(payloads) | {later}
    for relative in data["excluded"]:
        assert not (destination / relative).exists()
