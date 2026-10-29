"""Unit tests for read-only merged-PR cleanup preflight policy."""

from __future__ import annotations

from dataclasses import dataclass, field, replace

import pytest

from verified_pr_cleanup_pkg.application.cleanup import execute
from verified_pr_cleanup_pkg.domain.models import (
    BoundaryFailure,
    GitGateway,
    PreflightResult,
    PullRequest,
    PullRequestReader,
    RepositoryIdentity,
    PreflightStatus,
    Worktree,
)
from verified_pr_cleanup_pkg.domain._test_support import CleanupTestData as Data

READ_ONLY_METHODS = frozenset({
    "validate_branch", "remote_identity", "remote_branch_oid", "local_branch_oid",
    "object_exists", "is_ancestor", "merge_base", "changed_paths", "paths_match",
    "inspect_worktrees",
})


@dataclass
class FakeGit:
    """Read-only port double with deterministic snapshots and command accounting."""

    repository: RepositoryIdentity = field(default_factory=Data.repository)
    remote_base_oid: str = Data.BASE_OID
    local_base_oid: str = Data.BASE_OID
    local_head_oid: str | None = Data.HEAD_OID
    remote_head_oid: str | None = Data.HEAD_OID
    head_is_ancestor: bool = True
    parity_matches: bool = True
    worktrees: tuple[Worktree, ...] = field(default_factory=lambda: (Data.worktree(),))
    commands: list[str] = field(default_factory=list)
    fail_at: str | None = None
    missing_oids: tuple[str, ...] = ()
    invalid_branches: tuple[str, ...] = ()

    def _record(self, operation: str) -> None:
        self.commands.append(operation)
        if self.fail_at == operation:
            raise BoundaryFailure(f"{operation} failed at the boundary")

    def remote_identity(self, remote: str) -> RepositoryIdentity:
        self._record("remote_identity")
        return self.repository

    def validate_branch(self, branch: str) -> bool:
        self._record("validate_branch")
        return bool(branch) and not branch.startswith("-") and branch not in self.invalid_branches

    def remote_branch_oid(self, remote: str, branch: str) -> str | None:
        self._record("remote_branch_oid")
        return self.remote_base_oid if branch == Data.BASE_BRANCH else self.remote_head_oid

    def local_branch_oid(self, branch: str) -> str | None:
        self._record("local_branch_oid")
        return self.local_base_oid if branch == Data.BASE_BRANCH else self.local_head_oid

    def object_exists(self, oid: str) -> bool:
        self._record("object_exists")
        return oid in {Data.BASE_OID, Data.HEAD_OID, Data.MERGE_OID, Data.MERGE_BASE_OID} and oid not in self.missing_oids

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        self._record("is_ancestor")
        return self.head_is_ancestor if ancestor == Data.HEAD_OID else True

    def merge_base(self, base_oid: str, head_oid: str) -> str:
        self._record("merge_base")
        return Data.MERGE_BASE_OID

    def changed_paths(self, merge_base_oid: str, head_oid: str) -> tuple[str, ...]:
        self._record("changed_paths")
        return (Data.PARITY_PATH,)

    def paths_match(self, base_oid: str, head_oid: str, paths: tuple[str, ...]) -> bool:
        self._record("paths_match")
        return self.parity_matches

    def inspect_worktrees(self) -> tuple[Worktree, ...]:
        self._record("inspect_worktrees")
        return self.worktrees


@dataclass
class FakePullRequests(PullRequestReader):
    """Return a fixed or sequential PR snapshot without network access."""

    response: PullRequest = field(default_factory=Data.create)
    responses: tuple[PullRequest, ...] = ()
    calls: int = 0

    def fetch(self, number: int, repository: RepositoryIdentity) -> PullRequest:
        self.calls += 1
        if self.responses:
            return self.responses[min(self.calls - 1, len(self.responses) - 1)]
        return self.response


def _preflight(git: FakeGit, prs: FakePullRequests) -> PreflightResult:
    """Run the operation with a deterministic point-in-time timestamp."""
    return execute(Data.PR_NUMBER, Data.REMOTE_NAME, Data.BASE_BRANCH, Data.OBSERVED_AT, git, prs)


def test_safe_result_pins_and_reports_complete_state_without_capability() -> None:
    """A safe report is point-in-time evidence and the port exposes reads only."""
    git = FakeGit()
    prs = FakePullRequests()
    result = _preflight(git, prs)
    assert result.status is PreflightStatus.SAFE_TO_CLEAN
    assert prs.calls == 2
    assert result.evidence.pr_number == Data.PR_NUMBER
    assert result.evidence.head_oid == Data.HEAD_OID
    assert result.evidence.local_base_oid == Data.BASE_OID
    assert result.evidence.remote_base_oid == Data.BASE_OID
    assert result.revalidate_before_each_mutation
    assert set(git.commands) <= READ_ONLY_METHODS
    assert all(check.passed for check in result.checks)
    assert "head_proof" in {check.name for check in result.checks}
    assert "head_ancestry" not in {check.name for check in result.checks}
    assert not hasattr(git, "delete_local")
    assert not hasattr(git, "delete_remote")
    assert not hasattr(git, "switch_to")


def test_git_port_has_no_file_state_or_stash_operation() -> None:
    """Branch-deletion safety depends on PR/ref/occupancy evidence, not local files."""
    port_operations = {name for name in dir(GitGateway) if not name.startswith("_")}
    assert port_operations == READ_ONLY_METHODS


@pytest.mark.parametrize(
    "overrides",
    (
        {"state": Data.OPEN_PR_STATE},
        {"url": Data.INVALID_PR_URLS[0]},
        {"base_branch": Data.WRONG_BASE_BRANCH},
        {"head_repository": Data.OTHER_REPOSITORY},
        {"head_oid": Data.DIVERGENT_OID},
    ),
)
def test_invalid_pr_identity_or_merge_state_is_blocked(overrides: dict[str, str]) -> None:
    """Reject unmerged PRs and mismatched repository, URL, or base identity."""
    result = _preflight(FakeGit(), FakePullRequests(response=Data.create(**overrides)))
    assert result.status is PreflightStatus.BLOCKED
    assert result.reasons


def test_second_read_must_match_the_initial_pinned_identity() -> None:
    """Block if a fresh PR read changes immutable head identity."""
    initial = Data.create()
    changed = replace(initial, head_oid=Data.DIVERGENT_OID)
    result = _preflight(FakeGit(), FakePullRequests(responses=(initial, changed)))
    assert result.status is PreflightStatus.BLOCKED
    assert any("changed" in reason.lower() for reason in result.reasons)


def test_head_branch_change_between_reads_is_blocked() -> None:
    """Pin the initial head branch as well as the head OID."""
    initial = Data.create()
    changed = replace(initial, head_branch=Data.CHANGED_HEAD_BRANCH)
    result = _preflight(FakeGit(), FakePullRequests(responses=(initial, changed)))
    assert result.status is PreflightStatus.BLOCKED
    assert any("identity" in reason.lower() or "changed" in reason.lower() for reason in result.reasons)


def test_invalid_head_branch_ref_is_blocked_before_branch_inventory() -> None:
    """Reject a malformed live head ref before using it in Git inventory."""
    pull_request = Data.create(head_branch=Data.INVALID_HEAD_BRANCH)
    git = FakeGit(invalid_branches=(Data.INVALID_HEAD_BRANCH,))
    result = _preflight(git, FakePullRequests(response=pull_request))
    assert result.status is PreflightStatus.BLOCKED
    assert any("branch ref" in reason for reason in result.reasons)
    assert git.commands.count("remote_branch_oid") == 0


@pytest.mark.parametrize("missing_oid", (Data.BASE_OID, Data.HEAD_OID, Data.MERGE_OID))
def test_missing_base_head_or_merge_object_requests_fetch_without_fetching(
    missing_oid: str,
) -> None:
    """Block with an exact fetch-needed reason when proof objects are unavailable."""
    git = FakeGit(missing_oids=(missing_oid,))
    result = _preflight(git, FakePullRequests())
    assert result.status is PreflightStatus.BLOCKED
    assert any("fetch needed" in reason for reason in result.reasons)
    assert "fetch_base" not in git.commands
    assert not hasattr(git, "fetch_base")


def test_stale_or_missing_local_base_reports_fetch_needed_without_fetching() -> None:
    """Request a normal fetch when remote base differs from the local verified base."""
    git = FakeGit(local_base_oid=Data.DIVERGENT_OID)
    result = _preflight(git, FakePullRequests())
    assert result.status is PreflightStatus.BLOCKED
    assert any("fetch needed" in reason for reason in result.reasons)
    assert "fetch" not in git.commands
    assert set(git.commands) <= READ_ONLY_METHODS


@pytest.mark.parametrize("parity_matches", (True, False))
def test_non_fast_forward_merge_requires_herald_changed_path_parity(parity_matches: bool) -> None:
    """Use merge-base and changed-path parity when head ancestry is absent."""
    git = FakeGit(head_is_ancestor=False, parity_matches=parity_matches)
    result = _preflight(git, FakePullRequests())
    assert (result.status is PreflightStatus.SAFE_TO_CLEAN) is parity_matches
    assert "merge_base" in git.commands
    assert "changed_paths" in git.commands
    assert "paths_match" in git.commands
    proof_checks = [check for check in result.checks if check.name == "head_proof"]
    assert proof_checks
    assert all(check.passed is parity_matches for check in proof_checks)
    assert all(check.passed for check in result.checks) is parity_matches


@pytest.mark.parametrize("field", ("local_head_oid", "remote_head_oid"))
def test_changed_head_ref_is_blocked(field: str) -> None:
    """A local or remote branch ref must be absent or equal to the pinned head."""
    result = _preflight(FakeGit(**{field: Data.DIVERGENT_OID}), FakePullRequests())
    assert result.status is PreflightStatus.BLOCKED
    assert any("differs" in reason for reason in result.reasons)


def test_head_branch_checked_out_in_any_worktree_blocks() -> None:
    """A target branch owned by any linked worktree blocks deletion."""
    current = Data.worktree()
    linked_head = Data.worktree(
        path=Data.LINKED_WORKTREE_PATH, branch=Data.HEAD_BRANCH
    )
    result = _preflight(FakeGit(worktrees=(current, linked_head)), FakePullRequests())
    assert result.status is PreflightStatus.BLOCKED
    assert any("checked out" in reason for reason in result.reasons)
    assert Data.LINKED_WORKTREE_PATH in " ".join(result.reasons)


def test_linked_worktree_on_another_branch_does_not_block() -> None:
    """Occupying a different branch is unrelated to deleting the feature branch."""
    current = Data.worktree()
    linked_other = Data.worktree(
        path=Data.LINKED_WORKTREE_PATH, branch=Data.LINKED_WORKTREE_BRANCH
    )
    git = FakeGit(worktrees=(current, linked_other))
    result = _preflight(git, FakePullRequests())
    assert result.status is PreflightStatus.SAFE_TO_CLEAN
    assert result.evidence.worktrees == (current, linked_other)
    assert set(git.commands) <= READ_ONLY_METHODS


def test_remote_base_inspection_failure_propagates() -> None:
    """An unavailable remote inspection remains a boundary exception."""
    with pytest.raises(BoundaryFailure):
        _preflight(FakeGit(fail_at="remote_branch_oid"), FakePullRequests())


def test_boundary_failures_propagate_as_exceptions() -> None:
    """Do not convert infrastructure failures into normal domain result values."""
    with pytest.raises(BoundaryFailure):
        _preflight(FakeGit(fail_at="remote_identity"), FakePullRequests())
