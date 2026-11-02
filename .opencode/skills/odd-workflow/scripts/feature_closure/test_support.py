"""Build an isolated local Git remote for closure-check adapter and entry-point tests."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import TypedDict

import pytest

GIT_LIVE_BRANCH = "feature/still-on-the-remote"
GIT_REMOVED_BRANCH = "feature/merged-and-deleted"
GIT_PREFIX_BRANCH = "feature/still"
GIT_REMOTE_NAME = "origin"
GIT_UNKNOWN_REMOTE = "origin-not-configured"
GIT_SEED_PATH = "seed.txt"
GIT_SEED_CONTENT = "seed\n"
GIT_SEED_MESSAGE = "chore: seed the closure fixture"
GIT_REDIRECTING_VARIABLES = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")


class RemoteRepositoryFixture(TypedDict):
    """Carry one isolated working repository and its local bare remote."""

    directory: str
    remote_uri: str
    live_branch: str
    removed_branch: str


def create_fixture_environment() -> dict[str, str]:
    """Return an environment without machine Git configuration or repository redirection."""
    environment = os.environ.copy()
    environment["GIT_CONFIG_GLOBAL"] = os.devnull
    environment["GIT_CONFIG_NOSYSTEM"] = "1"
    environment["GIT_OPTIONAL_LOCKS"] = "0"
    for variable in GIT_REDIRECTING_VARIABLES:
        environment.pop(variable, None)
    return environment


def isolate_fixture_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove machine Git configuration and repository redirection for one test."""
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for variable in GIT_REDIRECTING_VARIABLES:
        monkeypatch.delenv(variable, raising=False)


def run_fixture_git(directory: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    """Run one fixture-only Git command inside the isolated temporary directory."""
    completed = subprocess.run(
        ["git", *arguments],
        cwd=directory,
        capture_output=True,
        check=False,
        shell=False,
        text=True,
        env=create_fixture_environment(),
    )
    assert completed.returncode == 0, completed.stderr
    return completed


def commit_fixture_tree(directory: Path, message: str) -> None:
    """Commit the staged fixture tree with a local identity and no commit signing."""
    run_fixture_git(
        directory,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "-c",
        "commit.gpgsign=false",
        "commit",
        "--quiet",
        "--message",
        message,
    )


def create_remote_repository(directory: Path) -> RemoteRepositoryFixture:
    """Build a working repository whose bare remote keeps one branch and deleted another."""
    directory.mkdir(parents=True, exist_ok=True)
    remote = directory / "remote.git"
    working = directory / "work"
    run_fixture_git(directory, "init", "--quiet", "--bare", str(remote))
    run_fixture_git(directory, "init", "--quiet", str(working))
    (working / GIT_SEED_PATH).write_text(GIT_SEED_CONTENT, encoding="utf-8", newline="")
    run_fixture_git(working, "add", "--all")
    commit_fixture_tree(working, GIT_SEED_MESSAGE)
    remote_uri = remote.as_uri()
    run_fixture_git(working, "remote", "add", GIT_REMOTE_NAME, remote_uri)
    run_fixture_git(working, "push", "--quiet", GIT_REMOTE_NAME, f"HEAD:refs/heads/{GIT_LIVE_BRANCH}")
    run_fixture_git(
        working, "push", "--quiet", GIT_REMOTE_NAME, f"HEAD:refs/heads/{GIT_REMOVED_BRANCH}"
    )
    run_fixture_git(working, "push", "--quiet", GIT_REMOTE_NAME, "--delete", GIT_REMOVED_BRANCH)
    return {
        "directory": str(working),
        "remote_uri": remote_uri,
        "live_branch": GIT_LIVE_BRANCH,
        "removed_branch": GIT_REMOVED_BRANCH,
    }
