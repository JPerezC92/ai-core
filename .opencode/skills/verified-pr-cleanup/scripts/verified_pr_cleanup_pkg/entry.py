"""Read-only CLI composition and JSON delivery for cleanup preflight."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Sequence
from datetime import datetime, timezone

from verified_pr_cleanup_pkg.application.cleanup import execute
from verified_pr_cleanup_pkg.domain.guards import is_safe_remote_name
from verified_pr_cleanup_pkg.domain.models import (
    BoundaryFailure,
    PreflightEvidence,
    PreflightResult,
    PreflightStatus,
)
from verified_pr_cleanup_pkg.infrastructure.git_cli import GitCli
from verified_pr_cleanup_pkg.infrastructure.github_cli import GitHubCli

PR_NUMBER_PATTERN = re.compile(r"^[1-9][0-9]{0,8}$")


def main(arguments: Sequence[str] | None = None) -> int:
    """Run one point-in-time validator and return its CLI status."""
    parser = argparse.ArgumentParser(
        prog="verified_pr_cleanup.py",
        description="Read-only preflight for independently authorized branch cleanup.",
    )
    parser.add_argument("pr_number", help="positive GitHub pull-request number")
    parser.add_argument("--base-remote", required=True, help="configured base Git remote")
    parser.add_argument("--base-branch", required=True, help="configured base branch")
    parsed = parser.parse_args(arguments)
    if PR_NUMBER_PATTERN.fullmatch(parsed.pr_number) is None:
        parser.error("PR number must be a positive decimal integer.")
    if not is_safe_remote_name(parsed.base_remote):
        parser.error("base remote is invalid.")
    try:
        git = GitCli()
        base_branch_valid = git.validate_branch(parsed.base_branch)
    except BoundaryFailure as exc:
        print(f"Preflight boundary failure: {exc}", file=sys.stderr)
        return 1
    if not base_branch_valid:
        parser.error("base branch is invalid.")
    observed_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        result = execute(
            int(parsed.pr_number), parsed.base_remote, parsed.base_branch,
            observed_at, git, GitHubCli(),
        )
    except BoundaryFailure as exc:
        print(f"Preflight boundary failure: {exc}", file=sys.stderr)
        return 1
    _render_result(result)
    return 0 if result.status is PreflightStatus.SAFE_TO_CLEAN else 1


def _render_result(result: PreflightResult) -> None:
    """Serialize the validator report at the CLI edge; never expose an action token."""
    payload: dict[str, object] = {
        "status": result.status.value,
        "observed_at": result.observed_at,
        "point_in_time_only": True,
        "reasons": list(result.reasons),
        "checks": [
            {"name": check.name, "passed": check.passed, "detail": check.detail}
            for check in result.checks
        ],
        "evidence": _serialize_evidence(result.evidence),
        "revalidate_before_each_mutation": list(result.revalidate_before_each_mutation),
        "authorization": "This result is not permission or capability to mutate Git state.",
    }
    print(json.dumps(payload, sort_keys=True))


def _serialize_evidence(evidence: PreflightEvidence) -> dict[str, object]:
    """Map typed evidence to JSON data outside the business operation."""
    return {
        "repository": evidence.repository.full_name if evidence.repository else None,
        "pr_number": evidence.pr_number,
        "pr_url": evidence.pr_url,
        "pr_state": evidence.pr_state,
        "merged_at": evidence.merged_at,
        "head_branch": evidence.head_branch,
        "head_oid": evidence.head_oid,
        "merge_commit_oid": evidence.merge_commit_oid,
        "base_branch": evidence.base_branch,
        "remote_base_oid": evidence.remote_base_oid,
        "local_base_oid": evidence.local_base_oid,
        "local_head_oid": evidence.local_head_oid,
        "remote_head_oid": evidence.remote_head_oid,
        "worktrees": [
            {"path": worktree.path, "branch": worktree.branch}
            for worktree in evidence.worktrees
        ],
    }
