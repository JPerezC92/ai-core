"""Specify the assembled prepare-local command and its fail-closed behaviour."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import TypedDict

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from attribution_scan.domain.records import Snapshot
from prepare_pr_review import main
from pr_review.test_support import (
    GIT_BINARY_CONTENT, GIT_SOURCE_PATH, GitDivergentFixture, commit_fixture_tree,
    create_body, create_committed_repository, create_divergent_repository,
    create_expected_git_snapshot, create_local_draft, create_local_snapshot,
    isolate_fixture_environment, run_fixture_git,
)


class LocalRepository(TypedDict):
    """Carry one isolated repository, its commits, and the expected snapshot."""

    directory: str
    number: int
    base: str
    head: str
    expected: Snapshot


@pytest.fixture()
def local_repository(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> LocalRepository:
    """Expose one isolated repository read under machine-independent Git configuration."""
    isolate_fixture_environment(monkeypatch)
    repository = create_committed_repository(tmp_path / "repository")
    monkeypatch.chdir(repository["directory"])
    return {
        "directory": repository["directory"], "number": create_local_snapshot()["pr_number"],
        "base": repository["base"], "head": repository["head"],
        "expected": create_expected_git_snapshot(base=repository["base"], head=repository["head"]),
    }


@pytest.fixture()
def divergent_repository(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> GitDivergentFixture:
    """Expose one repository whose base line holds a commit unreachable from its head."""
    isolate_fixture_environment(monkeypatch)
    divergent = create_divergent_repository(tmp_path / "divergent-repository")
    monkeypatch.chdir(divergent["directory"])
    return divergent


@pytest.fixture()
def local_inputs(tmp_path: Path) -> tuple[Path, Path]:
    """Write the local draft and the local working body that the command must read."""
    draft = tmp_path / "pr-draft.md"
    body = tmp_path / "pr-working-body.md"
    draft.write_text(create_local_draft(), encoding="utf-8", newline="")
    body.write_text(create_body(), encoding="utf-8", newline="")
    return draft, body


def create_arguments(
    number: int, *, base: str, draft: Path, body: Path, output: Path
) -> list[str]:
    """Build the documented prepare-local command line for one case."""
    return [
        "prepare-local", "--pr", str(number), "--base", base,
        "--draft", str(draft), "--working-body", str(body), "--output", str(output),
    ]


class PrepareLocalCommandTests:
    """Compose the snapshot from the local draft, local body, and real local Git data."""

    def test_prepare_local_publishes_the_local_snapshot(
        self,
        local_repository: LocalRepository,
        local_inputs: tuple[Path, Path],
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        draft, body = local_inputs
        output = tmp_path / "snapshot.json"
        arguments = create_arguments(
            local_repository["number"], base=local_repository["base"],
            draft=draft, body=body, output=output,
        )
        assert main(arguments) == 0
        assert json.loads(output.read_text(encoding="utf-8")) == local_repository["expected"]
        assert json.loads(capsys.readouterr().out) == {"status": "prepared", "command": "prepare-local"}
        assert draft.read_text(encoding="utf-8") == create_local_draft()
        assert body.read_text(encoding="utf-8") == create_body()

    def test_prepare_local_creates_no_output_for_an_unresolved_base_ref(
        self,
        local_repository: LocalRepository,
        local_inputs: tuple[Path, Path],
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        draft, body = local_inputs
        output = tmp_path / "snapshot.json"
        arguments = create_arguments(
            local_repository["number"], base="refs/heads/unresolved",
            draft=draft, body=body, output=output,
        )
        assert main(arguments) == 1
        assert not output.exists()
        assert json.loads(capsys.readouterr().out)["code"] == "GIT_REVISION_UNRESOLVED"

    def test_prepare_local_creates_no_output_for_an_empty_commit_range(
        self,
        local_repository: LocalRepository,
        local_inputs: tuple[Path, Path],
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        draft, body = local_inputs
        output = tmp_path / "snapshot.json"
        arguments = create_arguments(
            local_repository["number"], base=local_repository["head"],
            draft=draft, body=body, output=output,
        )
        assert main(arguments) == 1
        assert not output.exists()
        assert json.loads(capsys.readouterr().out)["code"] == "GIT_COMMIT_RANGE_EMPTY"

    def test_prepare_local_leaves_an_existing_output_untouched(
        self,
        local_repository: LocalRepository,
        local_inputs: tuple[Path, Path],
        tmp_path: Path,
    ) -> None:
        draft, body = local_inputs
        output = tmp_path / "snapshot.json"
        output.write_text("existing\n", encoding="utf-8")
        arguments = create_arguments(
            local_repository["number"], base=local_repository["base"],
            draft=draft, body=body, output=output,
        )
        assert main(arguments) == 2
        assert output.read_text(encoding="utf-8") == "existing\n"


class PrepareLocalMergeBaseTests:
    """Build the range from the merge base, so base-side-only work stays out of the snapshot."""

    def test_prepare_local_excludes_a_path_only_the_base_side_changed(
        self,
        divergent_repository: GitDivergentFixture,
        local_inputs: tuple[Path, Path],
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        draft, body = local_inputs
        output = tmp_path / "snapshot.json"
        arguments = create_arguments(
            create_local_snapshot()["pr_number"], base=divergent_repository["base"],
            draft=draft, body=body, output=output,
        )
        assert main(arguments) == 0
        snapshot = json.loads(output.read_text(encoding="utf-8"))
        assert snapshot["head_sha"] == divergent_repository["head"]
        assert [entry["path"] for entry in snapshot["changed_files"]] == [divergent_repository["head_path"]]
        assert snapshot["changed_files"][0]["content"] == divergent_repository["head_content"]
        assert divergent_repository["base_only_path"] not in {
            entry["path"] for entry in snapshot["changed_files"]
        }
        assert json.loads(capsys.readouterr().out) == {"status": "prepared", "command": "prepare-local"}


class PrepareLocalGitBoundaryTests:
    """Route an unreadable Git value to the boundary exit code without creating output."""

    def test_prepare_local_reports_unreadable_git_content_as_exit_two(
        self,
        local_repository: LocalRepository,
        local_inputs: tuple[Path, Path],
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        draft, body = local_inputs
        directory = Path(local_repository["directory"])
        (directory / GIT_SOURCE_PATH).write_bytes(GIT_BINARY_CONTENT)
        run_fixture_git(directory, "add", "--all")
        commit_fixture_tree(directory, "feat: add binary content")
        output = tmp_path / "snapshot.json"
        arguments = create_arguments(
            local_repository["number"], base=local_repository["base"],
            draft=draft, body=body, output=output,
        )
        assert main(arguments) == 2
        assert not output.exists()
        assert "git read failure" in capsys.readouterr().err
