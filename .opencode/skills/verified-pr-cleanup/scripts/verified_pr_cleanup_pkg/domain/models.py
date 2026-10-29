"""Typed records and read-only ports for merged-branch cleanup preflight."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol


@dataclass(frozen=True)
class RepositoryIdentity:
    """Canonical GitHub repository identity."""

    owner: str
    name: str

    @property
    def full_name(self) -> str:
        """Return owner/repository form used by GitHub CLI."""
        return f"{self.owner}/{self.name}"


@dataclass(frozen=True)
class PullRequest:
    """One machine-readable live pull-request record."""

    number: int
    state: str
    merged_at: str | None
    merge_commit_oid: str | None
    head_branch: str
    head_oid: str
    head_repository: str
    head_owner: str
    base_branch: str
    url: str


@dataclass(frozen=True)
class Worktree:
    """One linked worktree and the branch it has checked out."""

    path: str
    branch: str | None


@dataclass(frozen=True)
class CleanupIdentity:
    """PR repository, number, head, and base pinned by the first live read."""

    repository: RepositoryIdentity
    number: int
    head_branch: str
    head_oid: str
    base_branch: str


class PreflightStatus(Enum):
    """Read-only validator result; never an execution capability."""

    SAFE_TO_CLEAN = "SAFE_TO_CLEAN"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class ValidationCheck:
    """One named validation condition and its observed result."""

    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class PreflightEvidence:
    """Exact identities and ref/branch state observed by the validator."""

    repository: RepositoryIdentity | None
    pr_number: int
    pr_url: str | None
    pr_state: str | None
    merged_at: str | None
    head_branch: str | None
    head_oid: str | None
    merge_commit_oid: str | None
    base_branch: str
    remote_base_oid: str | None
    local_base_oid: str | None
    local_head_oid: str | None
    remote_head_oid: str | None
    worktrees: tuple[Worktree, ...]


@dataclass(frozen=True)
class PreflightResult:
    """Point-in-time decision, failed checks, evidence, and mandatory rechecks."""

    status: PreflightStatus
    observed_at: str
    reasons: tuple[str, ...]
    checks: tuple[ValidationCheck, ...]
    evidence: PreflightEvidence
    revalidate_before_each_mutation: tuple[str, ...]


class BoundaryFailure(Exception):
    """An IO/process boundary failure; it remains an exception until delivery."""


class PullRequestReader(Protocol):
    """Port for fresh machine-readable GitHub PR metadata."""

    def fetch(self, number: int, repository: RepositoryIdentity) -> PullRequest:
        """Read the requested PR or raise a boundary exception."""
        ...


class GitGateway(Protocol):
    """Read-only Git identity, ref, occupancy, and merge-proof port."""

    def remote_identity(self, remote: str) -> RepositoryIdentity:
        """Map singular fetch/push URLs to the same GitHub repository."""
        ...

    def validate_branch(self, branch: str) -> bool:
        """Check whether a value is one valid local branch name."""
        ...

    def remote_branch_oid(self, remote: str, branch: str) -> str | None:
        """Read the exact remote ref using ls-remote; None means absent."""
        ...

    def local_branch_oid(self, branch: str) -> str | None:
        """Read the exact local ref; None means absent."""
        ...

    def object_exists(self, oid: str) -> bool:
        """Check whether a commit object is already available locally."""
        ...

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        """Check commit ancestry; process errors remain boundary exceptions."""
        ...

    def merge_base(self, base_oid: str, head_oid: str) -> str:
        """Read the merge-base of the verified local base and pinned head."""
        ...

    def changed_paths(self, merge_base_oid: str, head_oid: str) -> tuple[str, ...]:
        """Read changed paths using checked NUL-delimited diff output."""
        ...

    def paths_match(self, base_oid: str, head_oid: str, paths: tuple[str, ...]) -> bool:
        """Run diff --quiet on only the supplied changed paths."""
        ...

    def inspect_worktrees(self) -> tuple[Worktree, ...]:
        """Read every linked worktree and its checked-out branch without changing them."""
        ...
