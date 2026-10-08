"""Behavior tests for malformed region-mode source marker sets."""

from __future__ import annotations

from pathlib import Path

import pytest

from _core_sync_testkit import (
    DEST_MARKED,
    REV_A,
    _apply_args,
    _bindings_document,
    _check_args,
    _init_args,
    _write_file,
    uc,
)


@pytest.mark.parametrize("command", ["check", "apply", "init"])
@pytest.mark.parametrize(
    "source_content",
    [
        pytest.param("<!-- core:begin -->\nCore body\n", id="missing-end"),
        pytest.param("<!-- core:end -->\nCore body\n", id="missing-begin"),
        pytest.param(
            "<!-- core:begin -->\n<!-- core:begin -->\n"
            "Core body\n<!-- core:end -->\n",
            id="duplicate-begin",
        ),
        pytest.param(
            "<!-- core:begin -->\nCore body\n"
            "<!-- core:end -->\n<!-- core:end -->\n",
            id="duplicate-end",
        ),
        pytest.param(
            "<!-- core:end -->\nCore body\n<!-- core:begin -->\n",
            id="reversed",
        ),
    ],
)
def test_commands_reject_malformed_source_without_writing(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    command: str,
    source_content: str,
) -> None:
    source_dir = tmp_path / "source"
    destination_dir = tmp_path / "destination"
    source_path = _write_file(source_dir, "agent.md", source_content)
    destination_path = _write_file(destination_dir, "agent.md", DEST_MARKED)
    root_content = (
        "# Root runtime\n\n"
        f"{uc.RECONCILE_BEGIN}\n"
        "> existing blocker body\n"
        f"{uc.RECONCILE_END}\n"
    )
    root_path = _write_file(destination_dir, "root.md", root_content)

    bindings_path = tmp_path / ".aicore" / "core.yaml"
    bindings_path.parent.mkdir(parents=True, exist_ok=True)
    uc.save_bindings(
        bindings_path,
        _bindings_document(
            REV_A,
            "agent.md",
            ["agent.md"],
            pending=["agent.md"],
            root="root.md",
        ),
    )
    report_path = _write_file(
        tmp_path,
        ".aicore/reconciliation/init.yaml",
        "existing reconciliation report\n",
    )
    protected_paths = [destination_path, root_path, bindings_path, report_path]
    before = {path: path.read_bytes() for path in protected_paths}

    args_by_command = {
        "check": _check_args(source_dir, destination_dir, bindings_path, REV_A),
        "apply": _apply_args(source_dir, destination_dir, bindings_path, REV_A),
        "init": _init_args(source_dir, destination_dir, bindings_path, REV_A),
    }

    assert uc.main(args_by_command[command]) == uc.EXIT_INVALID

    captured = capsys.readouterr()
    assert "invalid source markers" in captured.err
    assert str(source_path) in captured.err
    assert {path: path.read_bytes() for path in protected_paths} == before
