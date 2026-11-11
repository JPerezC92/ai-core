"""Build offline review evidence inputs, an isolated Git fixture, and invalid variants."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Literal, TypedDict

import pytest

from attribution_scan.domain.records import AttributionPolicy, Snapshot, ScanResult

from pr_review.domain.records import LocalInventory

# The capture schema belongs to the content skill; this half builds opaque capture
# objects for the workflow comparison and never re-declares their fields.
Capture = dict[str, object]

InventoryDefect = Literal["missing", "extra", "duplicate"]
RemoteField = Literal["number", "headRefOid", "body"]


def create_body(**overrides: str) -> str:
    """Create a canonical passing body; overrides target named textual fields."""
    item = overrides.get("item", "Inspect the change and confirm the intended result")
    return (
        "## Summary\n- Preserve this unrelated explanation exactly.\n\n"
        f"## Test plan\n- [x] {item}\n"
        "- [x] Inspect the regression and confirm it is absent\n\n"
        "## Findings / blockers\nNo findings.\n\n"
        "## Test evidence\n- PR: `#80`\n"
        f"- Immutable head SHA: `{overrides.get('head', 'a' * 40)}`\n"
        "- Base: `origin/main`\n"
        f"- Scope command: `git diff \"origin/main\"...{'a' * 40}`\n\n"
        "| Test-plan item | Literal action/input | Observed result | Executor |\n"
        "|---|---|---|---|\n"
        f"| {item} | Inspect the change | Expected result observed | Reviewer |\n"
        "| Inspect the regression and confirm it is absent | Inspect regression | Absent | Reviewer |\n\n"
        "[PASS] — Required checks are recorded and no findings remain.\n"
    )


def create_metadata(*, number: int = 80, head: str = "a" * 40, body: str | None = None) -> Capture:
    """Create owner-supplied metadata with explicit typed overrides."""
    return {
        "number": number, "headRefOid": head, "baseRefName": "main",
        "headRefName": "feat/release/body", "state": "OPEN",
        "title": "feat(release): prepare review", "body": create_body() if body is None else body,
    }


def create_divergence(field: RemoteField) -> Capture:
    """Create a remote identity, head, or body change."""
    if field == "number":
        return create_metadata(number=81)
    if field == "headRefOid":
        return create_metadata(head="b" * 40)
    return create_metadata(body="Changed remotely")


def create_metadata_with_undeclared_key(*, field: str = "url") -> Capture:
    """Create owner-supplied metadata carrying a key outside the documented seven."""
    metadata: Capture = dict(create_metadata())
    metadata[field] = "https://example.invalid/JPerezC92/ai-core/pull/80"
    return metadata


def create_snapshot() -> Snapshot:
    """Create scanner-compatible complete content including a deleted path."""
    return {
        "schema": 1, "pr_number": 80, "head_sha": "a" * 40,
        "base": "origin/main",
        "artifacts": [
            {"surface": "pr-title", "source": "PR #80 title", "content": "feat(release): prepare review"},
            {"surface": "pr-body", "source": "PR #80 body", "content": create_body()},
            {"surface": "commit-message", "source": "a" * 40, "content": "feat(release): prepare review"},
        ],
        "changed_files": [
            {"path": "src/current.py", "content": "value = 1\n"},
            {"path": "src/deleted.py", "content": ""},
        ],
    }


def create_paths() -> list[str]:
    """Return the reconciled exact diff paths, including a deleted file."""
    return ["src/current.py", "src/deleted.py"]


def create_policy() -> AttributionPolicy:
    """Create synthetic scanner policy data rather than duplicating approved tokens."""
    return {
        "schema": 1, "self_excluded_file": "policy.json",
        "markers": ["Synthetic attribution:"], "identities": ["Synthetic author"],
    }


def create_invalid_inventory(defect: InventoryDefect) -> Snapshot:
    """Create a well-typed snapshot with a deliberately invalid inventory."""
    snapshot = create_snapshot()
    files = snapshot["changed_files"]
    if defect == "missing":
        files.pop()
    elif defect == "extra":
        files.append({"path": "src/unreviewed.py", "content": "unreviewed"})
    else:
        files.append(dict(files[0]))
    return snapshot


def create_snapshot_without_commits() -> Snapshot:
    """Create a deliberately incomplete snapshot missing commit artifacts."""
    snapshot = create_snapshot()
    snapshot["artifacts"] = snapshot["artifacts"][:2]
    return snapshot


def create_clean_scan_result() -> ScanResult:
    """Create the expected existing-scanner output for the complete fixture."""
    return {"pr_number": 80, "head_sha": "a" * 40, "base": "origin/main", "matches": [], "exclusions": []}


def create_initial_review_body() -> str:
    """Create an unchecked remote baseline before the canonical review join."""
    prefix = create_body().split("## Test evidence", 1)[0]
    return prefix.replace("- [x]", "- [ ]").replace("No findings.", "No review findings yet.")


def create_local_inventory() -> LocalInventory:
    """Reuse immutable content fixtures without requiring scanner artifact assembly."""
    snapshot = create_snapshot()
    return {"schema": 1, "pr_number": snapshot["pr_number"], "head_sha": snapshot["head_sha"],
            "base": snapshot["base"], "commit_messages": snapshot["artifacts"][2:],
            "changed_files": snapshot["changed_files"]}


def create_local_title() -> str:
    """Return authored local title distinct from the inventory commit subject."""
    return "feat(release): prepare local review"


def create_local_draft() -> str:
    """Build the local creation artifact, not a downloaded PR body."""
    return f"Title: {create_local_title()}\n\n---\n\n" + create_initial_review_body()


def create_local_snapshot() -> Snapshot:
    """Build expected scanner input from local authored title and working body."""
    snapshot = create_snapshot()
    snapshot["artifacts"][0]["content"] = create_local_title()
    return snapshot


GIT_SOURCE_PATH = "src/current.py"
GIT_REMOVED_PATH = "src/deleted.py"
GIT_METACHARACTER_PATH = "src/evil;touch injected.txt"
GIT_SIDE_EFFECT_NAME = "injected.txt"
GIT_RENAMED_FROM_PATH = "src/renamed-from.py"
GIT_RENAMED_TO_PATH = "src/renamed-to.py"
GIT_RENAMED_CONTENT = "renamed = 1\n"
GIT_BASE_ONLY_PATH = "src/base-only.py"
GIT_BASE_CONTENT = "value = 1\n"
GIT_CHANGED_CONTENT = "value = 2\n"
GIT_REMOVED_CONTENT = "gone = 1\n"
GIT_METACHARACTER_CONTENT = "value = 3\n"
GIT_BASE_ONLY_CONTENT = "side = 1\n"
GIT_BASE_ONLY_CHANGED_CONTENT = "side = 2\n"
GIT_BASE_MESSAGE = "feat: add source files"
GIT_CHANGED_MESSAGE = "feat: change source files"
GIT_BASE_ONLY_MESSAGE = "feat: change the base-only path"
GIT_ORPHAN_MESSAGE = "feat: start an unrelated history"
GIT_SIDE_BRANCH = "feature/base-side"
GIT_HEAD_BRANCH = "feature/head-side"
GIT_ORPHAN_BRANCH = "orphan-history"
GIT_BINARY_CONTENT = b"\xff\xfe\x00not text\n"
GIT_REDIRECTING_VARIABLES = ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")


class GitRepositoryFixture(TypedDict):
    """Carry one isolated two-commit repository and the values its readers must return."""

    directory: str
    base: str
    head: str
    message: str
    changed_paths: list[str]
    deleted_paths: list[str]
    bodies: dict[str, str]


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


def run_fixture_git(directory: Path, *arguments: str) -> str:
    """Run one fixture-only Git command inside the isolated temporary repository."""
    completed = subprocess.run(
        ["git", *arguments], cwd=directory, capture_output=True, check=False,
        shell=False, env=create_fixture_environment(),
    )
    assert completed.returncode == 0, completed.stderr.decode("utf-8", errors="replace")
    return completed.stdout.decode("utf-8", errors="replace")


def commit_fixture_tree(directory: Path, message: str) -> str:
    """Commit the staged fixture tree with local identity and return the new commit id."""
    run_fixture_git(
        directory, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
        "-c", "commit.gpgsign=false", "commit", "--quiet", "--message", message,
    )
    return run_fixture_git(directory, "rev-parse", "HEAD").strip()


def create_committed_repository(directory: Path) -> GitRepositoryFixture:
    """Build two commits whose second change adds, renames, and deletes one path each."""
    (directory / "src").mkdir(parents=True)
    run_fixture_git(directory, "init", "--quiet")
    (directory / GIT_SOURCE_PATH).write_text(GIT_BASE_CONTENT, encoding="utf-8", newline="")
    (directory / GIT_REMOVED_PATH).write_text(GIT_REMOVED_CONTENT, encoding="utf-8", newline="")
    (directory / GIT_RENAMED_FROM_PATH).write_text(GIT_RENAMED_CONTENT, encoding="utf-8", newline="")
    run_fixture_git(directory, "add", "--all")
    base = commit_fixture_tree(directory, GIT_BASE_MESSAGE)
    (directory / GIT_SOURCE_PATH).write_text(GIT_CHANGED_CONTENT, encoding="utf-8", newline="")
    (directory / GIT_REMOVED_PATH).unlink()
    (directory / GIT_METACHARACTER_PATH).write_text(GIT_METACHARACTER_CONTENT, encoding="utf-8", newline="")
    run_fixture_git(directory, "mv", GIT_RENAMED_FROM_PATH, GIT_RENAMED_TO_PATH)
    run_fixture_git(directory, "add", "--all")
    head = commit_fixture_tree(directory, GIT_CHANGED_MESSAGE)
    return {
        "directory": str(directory), "base": base, "head": head, "message": GIT_CHANGED_MESSAGE,
        "changed_paths": [GIT_SOURCE_PATH, GIT_REMOVED_PATH, GIT_METACHARACTER_PATH, GIT_RENAMED_TO_PATH],
        "deleted_paths": [GIT_REMOVED_PATH],
        "bodies": {
            GIT_SOURCE_PATH: GIT_CHANGED_CONTENT,
            GIT_METACHARACTER_PATH: GIT_METACHARACTER_CONTENT,
            GIT_RENAMED_TO_PATH: GIT_RENAMED_CONTENT,
        },
    }


def create_expected_git_snapshot(*, base: str, head: str) -> Snapshot:
    """Build the snapshot the assembled command must produce for the shared Git fixture."""
    local = create_local_snapshot()
    number = local["pr_number"]
    return {
        "schema": local["schema"], "pr_number": number, "head_sha": head, "base": base,
        "artifacts": [
            {"surface": "pr-title", "source": f"PR #{number} title", "content": local["artifacts"][0]["content"]},
            {"surface": "pr-body", "source": f"PR #{number} body", "content": create_body()},
            {"surface": "commit-message", "source": head, "content": GIT_CHANGED_MESSAGE},
        ],
        "changed_files": [
            {"path": GIT_SOURCE_PATH, "content": GIT_CHANGED_CONTENT},
            {"path": GIT_REMOVED_PATH, "content": ""},
            {"path": GIT_METACHARACTER_PATH, "content": GIT_METACHARACTER_CONTENT},
            {"path": GIT_RENAMED_TO_PATH, "content": GIT_RENAMED_CONTENT},
        ],
    }


def create_truncated_status_payload() -> str:
    """Return one NUL-separated rename entry whose destination field is missing."""
    return f"R100\0{GIT_RENAMED_FROM_PATH}\0"


class GitDivergentFixture(TypedDict):
    """Carry one repository whose base line holds a commit unreachable from its head."""

    directory: str
    ancestor: str
    base: str
    head: str
    head_path: str
    head_content: str
    base_only_path: str
    base_only_content: str


def create_divergent_repository(directory: Path) -> GitDivergentFixture:
    """Build a head line and a base line that diverge after their shared ancestor."""
    (directory / "src").mkdir(parents=True)
    run_fixture_git(directory, "init", "--quiet")
    (directory / GIT_SOURCE_PATH).write_text(GIT_BASE_CONTENT, encoding="utf-8", newline="")
    (directory / GIT_BASE_ONLY_PATH).write_text(GIT_BASE_ONLY_CONTENT, encoding="utf-8", newline="")
    run_fixture_git(directory, "add", "--all")
    ancestor = commit_fixture_tree(directory, GIT_BASE_MESSAGE)
    run_fixture_git(directory, "checkout", "--quiet", "-b", GIT_SIDE_BRANCH)
    (directory / GIT_BASE_ONLY_PATH).write_text(GIT_BASE_ONLY_CHANGED_CONTENT, encoding="utf-8", newline="")
    run_fixture_git(directory, "add", "--all")
    base = commit_fixture_tree(directory, GIT_BASE_ONLY_MESSAGE)
    run_fixture_git(directory, "checkout", "--quiet", "-b", GIT_HEAD_BRANCH, ancestor)
    (directory / GIT_SOURCE_PATH).write_text(GIT_CHANGED_CONTENT, encoding="utf-8", newline="")
    run_fixture_git(directory, "add", "--all")
    head = commit_fixture_tree(directory, GIT_CHANGED_MESSAGE)
    return {
        "directory": str(directory), "ancestor": ancestor, "base": base, "head": head,
        "head_path": GIT_SOURCE_PATH, "head_content": GIT_CHANGED_CONTENT,
        "base_only_path": GIT_BASE_ONLY_PATH, "base_only_content": GIT_BASE_ONLY_CHANGED_CONTENT,
    }


class GitOrphanFixture(TypedDict):
    """Carry one commit and a second history that shares no ancestor with it."""

    directory: str
    base: str
    orphan_head: str


def create_orphan_repository(directory: Path) -> GitOrphanFixture:
    """Build one commit and an orphan commit whose history includes no common ancestor."""
    (directory / "src").mkdir(parents=True)
    run_fixture_git(directory, "init", "--quiet")
    (directory / GIT_SOURCE_PATH).write_text(GIT_BASE_CONTENT, encoding="utf-8", newline="")
    run_fixture_git(directory, "add", "--all")
    base = commit_fixture_tree(directory, GIT_BASE_MESSAGE)
    run_fixture_git(directory, "checkout", "--quiet", "--orphan", GIT_ORPHAN_BRANCH)
    (directory / GIT_SOURCE_PATH).write_text(GIT_CHANGED_CONTENT, encoding="utf-8", newline="")
    run_fixture_git(directory, "add", "--all")
    orphan_head = commit_fixture_tree(directory, GIT_ORPHAN_MESSAGE)
    return {"directory": str(directory), "base": base, "orphan_head": orphan_head}
