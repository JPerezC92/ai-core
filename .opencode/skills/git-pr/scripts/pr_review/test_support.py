"""Build typed offline review inputs, an isolated Git fixture, and deliberately invalid variants."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Literal, TypedDict

import pytest

from attribution_scan.domain.records import Artifact, AttributionPolicy, ChangedFile, Snapshot, ScanResult


class ReviewMetadata(TypedDict):
    """Represent owner-supplied PR metadata, not independently authenticated facts."""

    number: int
    headRefOid: str
    baseRefName: str
    headRefName: str
    state: str
    title: str
    body: str


InventoryDefect = Literal["missing", "extra", "duplicate"]
BodyDefect = Literal["missing-row", "duplicate-row", "unchecked", "wrong-head", "changed-item"]
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


def create_metadata(*, number: int = 80, head: str = "a" * 40, body: str | None = None) -> ReviewMetadata:
    """Create externally supplied metadata with explicit typed overrides."""
    return {
        "number": number, "headRefOid": head, "baseRefName": "main",
        "headRefName": "feat/release/body", "state": "OPEN",
        "title": "feat(release): prepare review", "body": create_body() if body is None else body,
    }


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


def create_draft() -> str:
    """Create the existing title-wrapped creation artifact."""
    return "Title: feat(release): prepare review\n\n---\n\n" + create_body()


def create_policy() -> AttributionPolicy:
    """Create synthetic scanner policy data rather than duplicating approved tokens."""
    return {
        "schema": 1, "self_excluded_file": "policy.json",
        "markers": ["Synthetic attribution:"], "identities": ["Synthetic author"],
    }


def create_divergence(field: RemoteField) -> ReviewMetadata:
    """Create a remote identity, head, or body change."""
    if field == "number":
        return create_metadata(number=81)
    if field == "headRefOid":
        return create_metadata(head="b" * 40)
    return create_metadata(body="Changed remotely")


MetadataExtraSite = Literal["expected", "persisted", "both"]


def create_metadata_with_undeclared_key(*, field: str = "url") -> dict[str, object]:
    """Create owner-supplied metadata carrying a key outside the documented seven."""
    metadata: dict[str, object] = dict(create_metadata())
    metadata[field] = "https://example.invalid/JPerezC92/ai-core/pull/80"
    return metadata


MetadataDefect = Literal[
    "non-object", "zero-number", "negative-number", "string-number",
    "short-head", "non-hex-head", "long-head", "not-open-state",
    "blank-base", "blank-head-ref", "blank-title",
    "non-string-title", "non-string-base", "non-string-head-ref",
    "non-string-state", "non-string-body",
    "missing-field",
]


def create_invalid_metadata(defect: MetadataDefect) -> object:
    """Create one named metadata rejection variant, including non-object input."""
    if defect == "non-object":
        return tuple(create_metadata().items())
    if defect == "missing-field":
        incomplete = dict(create_metadata())
        del incomplete["body"]
        return incomplete
    rejections: dict[str, tuple[str, object]] = {
        "zero-number": ("number", 0),
        "negative-number": ("number", -1),
        "string-number": ("number", "80"),
        "short-head": ("headRefOid", "a" * 6),
        "non-hex-head": ("headRefOid", "z" * 40),
        "long-head": ("headRefOid", "a" * 65),
        "not-open-state": ("state", "MERGED"),
        "blank-base": ("baseRefName", "   "),
        "blank-head-ref": ("headRefName", ""),
        "blank-title": ("title", " "),
        "non-string-title": ("title", 7),
        "non-string-base": ("baseRefName", None),
        "non-string-head-ref": ("headRefName", ["feat/release/body"]),
        "non-string-state": ("state", True),
        "non-string-body": ("body", 0),
    }
    field, invalid = rejections[defect]
    metadata: dict[str, object] = dict(create_metadata())
    metadata[field] = invalid
    return metadata


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


def create_invalid_body(defect: BodyDefect) -> str:
    """Create one named structural evidence defect without implying semantic truth."""
    body = create_body()
    row = next(line for line in body.splitlines() if line.startswith("| Inspect the change"))
    if defect == "missing-row":
        return body.replace(row + "\n", "")
    if defect == "duplicate-row":
        return body.replace(row, row + "\n" + row)
    if defect == "unchecked":
        return body.replace("- [x]", "- [ ]", 1)
    if defect == "wrong-head":
        return create_body(head="b" * 40)
    return body.replace("- [x] Inspect the change", "- [x] Recheck the change", 1)


def create_clean_scan_result() -> ScanResult:
    """Create the expected existing-scanner output for the complete fixture."""
    return {"pr_number": 80, "head_sha": "a" * 40, "base": "origin/main", "matches": [], "exclusions": []}


FindingStatus = Literal["FIXED", "REJECTED", "OPEN", "IN PROGRESS", "DEFERRED"]
ProtectedChange = Literal["summary", "item"]
HistoryChange = Literal["removed", "renumbered", "severity"]


def create_truncated_evidence_body() -> str:
    """Keep the expected section names but end at a heading without a newline."""
    return create_body().split("## Test evidence", 1)[0] + "## Test evidence"


def create_findings_body(status: FindingStatus = "FIXED") -> str:
    """Create canonical finding rows with explicit resolution or refutation text."""
    evidence = "output/audits/fix.md — corrected result verified"
    resolution = "Implementer — parser corrected; verified by Reviewer"
    if status == "REJECTED":
        evidence = "output/audits/refutation.md — exact comparison returned equal"
        resolution = "Reviewer — mechanically refuted by exact comparison"
    elif status in ("OPEN", "IN PROGRESS"):
        resolution = "Implementer — correct parser and request verification"
    elif status == "DEFERRED":
        resolution = "knowledge/debt.md#fixture — user authorized deferral on 2026-10-31"
    findings = (
        "| ID | Severity | Status | Evidence | Owner / resolution |\n"
        "|---|---|---|---|---|\n"
        f"| F1 | `ADVISORY` | `{status}` | {evidence} | {resolution} |"
    )
    body = create_body().replace("No findings.", findings)
    if status == "DEFERRED":
        body = body.replace(
            "[PASS] —", "## Open debt\n- F1 — knowledge/debt.md#fixture, authorized by user on 2026-10-31\n\n[PASS] —",
        )
    return body


def create_initial_review_body() -> str:
    """Create an unchecked remote baseline before the canonical review join."""
    prefix = create_body().split("## Test evidence", 1)[0]
    return prefix.replace("- [x]", "- [ ]").replace("No findings.", "No review findings yet.")


def create_protected_content_change(change: ProtectedChange) -> str:
    """Create a candidate that changes protected prose or an exact test-item key."""
    if change == "summary":
        return create_body().replace("Preserve this unrelated explanation exactly.", "Unauthorized replacement.")
    return create_body(item="Inspect a different change and confirm its result")


def create_changed_history(change: HistoryChange) -> str:
    """Create a candidate that loses or changes an existing finding identity."""
    body = create_findings_body()
    if change == "removed":
        return create_body()
    if change == "renumbered":
        return body.replace("| F1 |", "| F2 |")
    return body.replace("`ADVISORY`", "`BLOCK`")


class DecisionEvidence(TypedDict):
    """Carry supplied decision provenance without certifying its authenticity."""

    target: str
    actor: str
    date: str
    statement: str
    evidence: str
    destination: str


class ReviewDecisions(TypedDict):
    """Bind supplied N/A, acceptance and debt decisions to one review context."""

    pr_number: int
    head_sha: str
    not_applicable: list[DecisionEvidence]
    acceptance: list[DecisionEvidence]
    debt: list[DecisionEvidence]


OutcomeKind = Literal["na", "advisory", "debt"]
DecisionDefect = Literal["head", "provenance"]


class LocalInventory(TypedDict):
    """Contain only owner-supplied immutable content, never remote PR prose."""

    schema: int
    pr_number: int
    head_sha: str
    base: str
    commit_messages: list[Artifact]
    changed_files: list[ChangedFile]


def create_decision(target: str, *, destination: str = "") -> DecisionEvidence:
    """Create explicit supplied provenance for a fixture decision."""
    return {"target": target, "actor": "user", "date": "2026-10-31",
            "statement": "approved", "evidence": "feature Log L15", "destination": destination}


def create_review_decisions(kind: Literal["none", "na", "advisory", "debt"] = "none") -> ReviewDecisions:
    """Create typed decision inputs separately from the rendered body."""
    value: ReviewDecisions = {"pr_number": 80, "head_sha": "a" * 40,
                              "not_applicable": [], "acceptance": [], "debt": []}
    if kind == "na":
        value["not_applicable"] = [create_decision("Inspect the regression and confirm it is absent")]
    if kind in ("advisory", "debt"):
        value["acceptance"] = [create_decision("F1")]
    if kind == "debt":
        value["debt"] = [create_decision("F1", destination="knowledge/debt.md#fixture")]
    return value


def create_invalid_decisions(defect: DecisionDefect) -> ReviewDecisions:
    """Create deliberately invalid supplied decision binding or provenance."""
    value = create_review_decisions("na")
    if defect == "head":
        value["head_sha"] = "b" * 40
    else:
        value["not_applicable"][0]["evidence"] = ""
    return value


def create_outcome_body(kind: OutcomeKind) -> str:
    """Render canonical outcomes with exact item keys and the existing columns."""
    if kind == "na":
        body = create_body().replace("- [x] Inspect the regression", "- [ ] Inspect the regression")
        row = next(line for line in body.splitlines() if line.startswith("| Inspect the regression"))
        return body.replace(row + "\n", "")
    body = create_findings_body("DEFERRED" if kind == "debt" else "OPEN")
    return body.replace("[PASS] — Required checks are recorded and no findings remain.",
                        "[ADVISORY] — user accepted F1 on 2026-10-31; required checks are recorded.")


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


FollowupDefect = Literal["missing", "target", "destination", "provenance"]


def create_pipe_item_body(*, mismatched: bool = False) -> str:
    """Keep the checkbox literal while escaping its table-cell pipe for Markdown."""
    item = "Inspect A | B and confirm equality"
    body = create_body(item=item)
    table_item = "Inspect A \\| C and confirm equality" if mismatched else "Inspect A \\| B and confirm equality"
    return body.replace(f"| {item} |", f"| {table_item} |")


def create_followup_decisions(*, advisory: bool = False) -> ReviewDecisions:
    """Authorize a separate follow-up without manufacturing a deferred finding."""
    decisions = create_review_decisions("advisory" if advisory else "none")
    decisions["debt"] = [create_decision("Follow-up: improve diagnostics", destination="knowledge/debt.md#diagnostics")]
    return decisions


def create_followup_body(*, advisory: bool = False) -> str:
    """Render an independently authorized follow-up using canonical debt syntax."""
    body = create_outcome_body("advisory") if advisory else create_body()
    marker = "[ADVISORY] —" if advisory else "[PASS] —"
    debt = ("## Open debt\n"
            "- Follow-up: improve diagnostics — knowledge/debt.md#diagnostics, authorized by user on 2026-10-31\n\n")
    return body.replace(marker, debt + marker)


def create_invalid_followup_decisions(defect: FollowupDefect) -> ReviewDecisions:
    """Create missing or inconsistent supplied follow-up authority."""
    decisions = create_followup_decisions()
    if defect == "missing":
        decisions["debt"] = []
    elif defect == "target":
        decisions["debt"][0]["target"] = "Follow-up: different work"
    elif defect == "destination":
        decisions["debt"][0]["destination"] = "knowledge/debt.md#different"
    else:
        decisions["debt"][0]["evidence"] = ""
    return decisions


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
