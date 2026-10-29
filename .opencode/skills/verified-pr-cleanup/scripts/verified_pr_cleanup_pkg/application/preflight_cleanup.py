"""Read-only preflight operation for merged pull-request branch cleanup."""

from __future__ import annotations

from dataclasses import dataclass

from verified_pr_cleanup_pkg.domain.guards import (
    is_full_oid,
    is_safe_remote_name,
    pull_request_identity_error,
)
from verified_pr_cleanup_pkg.domain.models import (
    CleanupIdentity,
    GitGateway,
    PreflightEvidence,
    PreflightResult,
    PreflightStatus,
    PullRequest,
    PullRequestReader,
    RepositoryIdentity,
    ValidationCheck,
)

REVALIDATION_STEPS = (
    "Re-read live PR number, canonical URL, MERGED state, base, head branch, and immutable head OID.",
    "Re-run ls-remote and confirm the local base still equals the remote base; fetch normally if stale.",
    "Re-read local and remote PR branch refs and confirm the feature branch is checked out in no worktree.",
    "Re-run merge-commit ancestry or exact changed-path parity immediately before each deletion operation.",
)


@dataclass(frozen=True)
class _Inspection:
    """Collected point-in-time evidence and all decidable safety checks."""

    evidence: PreflightEvidence
    checks: tuple[ValidationCheck, ...]
    reasons: tuple[str, ...]
    identity: CleanupIdentity | None


def execute(
    pull_request_number: int,
    base_remote: str,
    base_branch: str,
    observed_at: str,
    git: GitGateway,
    pull_requests: PullRequestReader,
) -> PreflightResult:
    """Return SAFE_TO_CLEAN or BLOCKED without invoking a mutating Git operation."""
    empty_evidence = _empty_evidence(pull_request_number, base_branch)
    if pull_request_number <= 0:
        return _blocked(observed_at, empty_evidence, (), "PR number must be positive.")
    if not is_safe_remote_name(base_remote):
        return _blocked(observed_at, empty_evidence, (), "Configured base remote is invalid.")
    if not base_branch or not git.validate_branch(base_branch):
        return _blocked(observed_at, empty_evidence, (), "Configured base branch/ref is invalid.")

    initial = _inspect(pull_request_number, base_remote, base_branch, git, pull_requests)
    if initial.reasons or initial.identity is None:
        return _result(observed_at, initial, PreflightStatus.BLOCKED)
    confirmed = _inspect(
        pull_request_number, base_remote, base_branch, git, pull_requests, initial.identity
    )
    checks = initial.checks + confirmed.checks
    reasons = list(confirmed.reasons)
    if initial.evidence != confirmed.evidence:
        reasons.append("Repository, PR, ref, or worktree state changed between preflight reads.")
        checks += (ValidationCheck("stable_snapshot", False, reasons[-1]),)
    else:
        checks += (ValidationCheck("stable_snapshot", True, "Two complete reads produced identical identities and ref state."),)
    inspection = _Inspection(confirmed.evidence, checks, tuple(reasons), initial.identity)
    status = PreflightStatus.BLOCKED if reasons else PreflightStatus.SAFE_TO_CLEAN
    return _result(observed_at, inspection, status)


def _inspect(
    number: int,
    remote: str,
    base_branch: str,
    git: GitGateway,
    pull_requests: PullRequestReader,
    pinned: CleanupIdentity | None = None,
) -> _Inspection:
    """Read fresh Git/GitHub state and check each required preflight condition."""
    checks: list[ValidationCheck] = []
    reasons: list[str] = []

    def record(name: str, passed: bool, detail: str) -> None:
        checks.append(ValidationCheck(name, passed, detail))
        if not passed:
            reasons.append(detail)

    repository = git.remote_identity(remote)
    repository_ok = pinned is None or _same_repository(repository, pinned.repository)
    record("repository_identity", repository_ok, "Configured remote matches pinned repository." if repository_ok else "Configured remote repository changed after initial read.")
    request_repository = pinned.repository if pinned is not None else repository
    pull_request = pull_requests.fetch(number, request_repository)
    identity_error = pull_request_identity_error(pull_request, number, request_repository, base_branch)
    record("pr_identity", identity_error is None, identity_error or "Canonical URL, repository, PR number, MERGED state, base, and head fields match.")
    pinned_ok = pinned is None or (
        pull_request.number == pinned.number
        and pull_request.head_branch == pinned.head_branch
        and pull_request.head_oid.lower() == pinned.head_oid.lower()
        and pull_request.base_branch == pinned.base_branch
        and _same_repository(request_repository, pinned.repository)
    )
    record("pinned_identity", pinned_ok, "PR number, repository, head branch/OID, and base match the first read." if pinned_ok else "PR identity changed after the first read.")
    if identity_error is not None or not repository_ok or not pinned_ok:
        return _inspection_result(number, base_branch, repository, pull_request, None, None, None, None, checks, reasons, None)

    head_branch = pinned.head_branch if pinned is not None else pull_request.head_branch
    head_oid = pinned.head_oid if pinned is not None else pull_request.head_oid
    merge_oid = pull_request.merge_commit_oid
    base_ref_valid = git.validate_branch(base_branch)
    head_ref_valid = git.validate_branch(head_branch)
    record("base_ref_format", base_ref_valid, "Configured base is a valid branch ref." if base_ref_valid else "Configured base is not a valid branch ref.")
    record("head_ref_format", head_ref_valid, "PR head is a valid branch ref." if head_ref_valid else "PR head is not a valid branch ref.")
    if not base_ref_valid or not head_ref_valid:
        return _inspection_result(number, base_branch, repository, pull_request, None, None, None, None, checks, reasons, None)

    remote_base_oid = git.remote_branch_oid(remote, base_branch)
    local_base_oid = git.local_branch_oid(base_branch)
    base_present = remote_base_oid is not None and local_base_oid is not None
    record("base_refs_present", base_present, "Remote and local configured base refs are present." if base_present else "Configured base ref is missing locally or remotely.")
    base_current = base_present and remote_base_oid == local_base_oid
    base_detail = (
        f"Local base {local_base_oid} equals remote base {remote_base_oid}."
        if base_current
        else f"fetch needed: local base {local_base_oid or 'absent'} differs from remote base {remote_base_oid or 'absent'}; validator did not fetch."
    )
    record("base_ref_current", base_current, base_detail)

    local_head_oid = git.local_branch_oid(head_branch)
    remote_head_oid = git.remote_branch_oid(remote, head_branch)
    refs_valid = all(value is None or is_full_oid(value) for value in (local_head_oid, remote_head_oid))
    record("head_ref_oids", refs_valid, "Observed head ref OIDs are full-length or absent." if refs_valid else "A local or remote PR head ref has an invalid OID.")
    refs_match = refs_valid and all(value is None or value.lower() == head_oid.lower() for value in (local_head_oid, remote_head_oid))
    record("head_refs_match", refs_match, "Local and remote PR refs are absent or match the immutable PR head." if refs_match else "A local or remote PR head ref differs from the immutable PR head.")

    worktrees = git.inspect_worktrees()
    occupied_paths = tuple(worktree.path for worktree in worktrees if worktree.branch == head_branch)
    head_unchecked = not occupied_paths
    record(
        "head_not_checked_out",
        head_unchecked,
        "PR head is not checked out in any worktree."
        if head_unchecked
        else "PR head is checked out in worktree(s): " + ", ".join(occupied_paths) + "; Herald must resolve it before deletion.",
    )

    base_objects_available = (
        remote_base_oid is not None and git.object_exists(remote_base_oid)
        and local_base_oid is not None and git.object_exists(local_base_oid)
    )
    record("base_objects_available", base_objects_available, "Verified base commit objects are already local." if base_objects_available else "fetch needed: required base commit object is unavailable locally; validator did not fetch.")
    head_available = git.object_exists(head_oid)
    record("head_object_available", head_available, "Pinned PR head commit object is already local." if head_available else "fetch needed: pinned PR head object is unavailable locally; validator did not fetch.")
    merge_available = merge_oid is not None and git.object_exists(merge_oid)
    record("merge_object_available", merge_available, "PR merge commit object is already local." if merge_available else "fetch needed: PR merge commit object is unavailable locally; validator did not fetch.")

    if base_current and base_objects_available and head_available and merge_available and remote_base_oid is not None and merge_oid is not None:
        merge_ancestor = git.is_ancestor(merge_oid, remote_base_oid)
        record("merge_commit_ancestry", merge_ancestor, "PR merge commit is an ancestor of the verified base." if merge_ancestor else "PR merge commit is not an ancestor of the verified base.")
        head_is_ancestor = git.is_ancestor(head_oid, remote_base_oid)
        head_proof = head_is_ancestor
        if not head_is_ancestor:
            merge_base_oid = git.merge_base(remote_base_oid, head_oid)
            merge_base_ok = is_full_oid(merge_base_oid)
            record("merge_base", merge_base_ok, "Merge-base was resolved from verified base and pinned head." if merge_base_ok else "Git returned an invalid merge-base; fetch or inspect required objects.")
            if merge_base_ok:
                paths = git.changed_paths(merge_base_oid, head_oid)
                head_proof = git.paths_match(remote_base_oid, head_oid, paths)
                record("changed_path_parity", head_proof, "Herald NUL-path parity proof passed." if head_proof else "Herald changed-path parity proof failed.")
        record(
            "head_proof",
            head_proof,
            "Pinned head is an ancestor of the verified base."
            if head_is_ancestor
            else (
                "Pinned head matches the verified base by exact changed-path parity."
                if head_proof
                else "Pinned head is neither an ancestor nor changed-path equal to the verified base."
            ),
        )
    else:
        record("merge_proof", False, "Merge proof is inconclusive until base/head/merge objects are available and base refs match.")

    evidence = PreflightEvidence(
        repository, number, pull_request.url, pull_request.state, pull_request.merged_at,
        head_branch, head_oid, merge_oid, base_branch, remote_base_oid, local_base_oid,
        local_head_oid, remote_head_oid, worktrees,
    )
    identity = CleanupIdentity(request_repository, number, head_branch, head_oid, base_branch)
    return _Inspection(evidence, tuple(checks), tuple(reasons), identity)


def _inspection_result(
    number: int,
    base_branch: str,
    repository: RepositoryIdentity | None,
    pull_request: PullRequest,
    remote_base_oid: str | None,
    local_base_oid: str | None,
    local_head_oid: str | None,
    remote_head_oid: str | None,
    checks: list[ValidationCheck],
    reasons: list[str],
    identity: CleanupIdentity | None,
) -> _Inspection:
    """Preserve partial identity evidence when validation stops early."""
    evidence = PreflightEvidence(
        repository, number, pull_request.url, pull_request.state, pull_request.merged_at,
        pull_request.head_branch, pull_request.head_oid, pull_request.merge_commit_oid,
        base_branch, remote_base_oid, local_base_oid, local_head_oid, remote_head_oid, (),
    )
    return _Inspection(evidence, tuple(checks), tuple(reasons), identity)


def _empty_evidence(number: int, base_branch: str) -> PreflightEvidence:
    """Create a typed empty evidence record for an invalid request."""
    return PreflightEvidence(None, number, None, None, None, None, None, None, base_branch, None, None, None, None, ())


def _same_repository(left: RepositoryIdentity, right: RepositoryIdentity) -> bool:
    """Compare GitHub owner/repository names case-insensitively."""
    return left.full_name.casefold() == right.full_name.casefold()


def _blocked(
    observed_at: str,
    evidence: PreflightEvidence,
    checks: tuple[ValidationCheck, ...],
    reason: str,
) -> PreflightResult:
    """Build a blocked result with an explicit failed check."""
    return PreflightResult(
        PreflightStatus.BLOCKED, observed_at, (reason,),
        checks + (ValidationCheck("request_valid", False, reason),), evidence,
        REVALIDATION_STEPS,
    )


def _result(observed_at: str, inspection: _Inspection, status: PreflightStatus) -> PreflightResult:
    """Bind one inspection's evidence and required future checks to its verdict."""
    return PreflightResult(
        status, observed_at, inspection.reasons, inspection.checks,
        inspection.evidence, REVALIDATION_STEPS,
    )
