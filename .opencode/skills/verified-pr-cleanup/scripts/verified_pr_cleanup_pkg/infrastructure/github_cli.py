"""GitHub CLI adapter mapping validated JSON into typed pull-request data."""

from __future__ import annotations

import json
import shutil
import subprocess
from typing import TypedDict, cast

from verified_pr_cleanup_pkg.domain.models import (
    BoundaryFailure,
    PullRequest,
    RepositoryIdentity,
)

COMMAND_TIMEOUT_SECONDS = 60
PR_JSON_FIELDS = (
    "number,state,mergedAt,mergeCommit,headRefName,headRefOid,headRepository,"
    "headRepositoryOwner,baseRefName,url"
)


class _MergeCommitPayload(TypedDict):
    """Validated `mergeCommit` object returned by GitHub CLI."""

    oid: str


class _HeadRepositoryPayload(TypedDict):
    """Validated head repository object returned by GitHub CLI."""

    nameWithOwner: str


class _HeadOwnerPayload(TypedDict):
    """Validated head owner object returned by GitHub CLI."""

    login: str


class _PullRequestPayload(TypedDict):
    """Runtime-validated GitHub CLI PR payload."""

    number: int
    state: str
    mergedAt: str | None
    mergeCommit: _MergeCommitPayload | None
    headRefName: str
    headRefOid: str
    headRepository: _HeadRepositoryPayload | None
    headRepositoryOwner: _HeadOwnerPayload | None
    baseRefName: str
    url: str


class GitHubCli:
    """Read one live PR through `gh pr view`; no caller-supplied merge assertions."""

    def __init__(self) -> None:
        executable = shutil.which("gh")
        if executable is None:
            raise BoundaryFailure("GitHub CLI executable was not found on PATH.")
        self._executable = executable

    def fetch(self, number: int, repository: RepositoryIdentity) -> PullRequest:
        """Fetch and validate the required JSON fields for one repository PR."""
        if number <= 0:
            raise BoundaryFailure("Refused a non-positive PR number.")
        completed = self._run(
            [
                self._executable,
                "pr",
                "view",
                str(number),
                "--repo",
                repository.full_name,
                "--json",
                PR_JSON_FIELDS,
            ]
        )
        if completed.returncode != 0:
            raise BoundaryFailure("GitHub CLI could not read the requested PR.")
        try:
            raw: object = json.loads(
                completed.stdout.decode("utf-8", errors="strict"),
                object_pairs_hook=_reject_duplicate_keys,
            )
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            raise BoundaryFailure("GitHub CLI returned malformed PR JSON.") from exc
        payload = _validated_pull_request_payload(raw)
        if payload["number"] != number:
            raise BoundaryFailure("GitHub CLI returned a different pull-request number.")
        merge_commit = payload["mergeCommit"]
        head_repository = payload["headRepository"]
        head_owner = payload["headRepositoryOwner"]
        return PullRequest(
            number=payload["number"],
            state=payload["state"],
            merged_at=payload["mergedAt"],
            merge_commit_oid=None if merge_commit is None else merge_commit["oid"],
            head_branch=payload["headRefName"],
            head_oid=payload["headRefOid"],
            head_repository=(
                "" if head_repository is None else head_repository["nameWithOwner"]
            ),
            head_owner="" if head_owner is None else head_owner["login"],
            base_branch=payload["baseRefName"],
            url=payload["url"],
        )

    def _run(self, arguments: list[str]) -> subprocess.CompletedProcess[bytes]:
        """Execute one GitHub CLI request without shell interpolation."""
        try:
            return subprocess.run(
                arguments,
                capture_output=True,
                check=False,
                shell=False,
                timeout=COMMAND_TIMEOUT_SECONDS,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise BoundaryFailure("GitHub CLI process could not be completed safely.") from exc


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Reject duplicate JSON keys while retaining unknown values as untrusted objects."""
    mapped: dict[str, object] = {}
    for key, value in pairs:
        if key in mapped:
            raise ValueError("Duplicate JSON key.")
        mapped[key] = value
    return mapped


def _validated_pull_request_payload(raw: object) -> _PullRequestPayload:
    """Narrow the untrusted JSON boundary into its runtime-validated TypedDict."""
    values = _string_keyed_mapping(raw, "GitHub CLI PR response")
    number = values.get("number")
    if isinstance(number, bool) or not isinstance(number, int) or number <= 0:
        raise BoundaryFailure("GitHub CLI PR response omitted a valid number.")
    state = _required_string(values.get("state"), "state")
    merged_at_value = values.get("mergedAt")
    if merged_at_value is not None and not isinstance(merged_at_value, str):
        raise BoundaryFailure("GitHub CLI returned an invalid mergedAt value.")
    merge_commit = _optional_object(values.get("mergeCommit"), "mergeCommit")
    head_repository = _optional_object(values.get("headRepository"), "headRepository")
    head_owner = _optional_object(values.get("headRepositoryOwner"), "headRepositoryOwner")
    return {
        "number": number,
        "state": state,
        "mergedAt": merged_at_value,
        "mergeCommit": None if merge_commit is None else {
            "oid": _required_string(merge_commit.get("oid"), "mergeCommit.oid")
        },
        "headRefName": _required_string(values.get("headRefName"), "headRefName"),
        "headRefOid": _required_string(values.get("headRefOid"), "headRefOid"),
        "headRepository": None if head_repository is None else {
            "nameWithOwner": _required_string(
                head_repository.get("nameWithOwner"), "headRepository.nameWithOwner"
            )
        },
        "headRepositoryOwner": None if head_owner is None else {
            "login": _required_string(head_owner.get("login"), "headRepositoryOwner.login")
        },
        "baseRefName": _required_string(values.get("baseRefName"), "baseRefName"),
        "url": _required_string(values.get("url"), "url"),
    }


def _optional_object(value: object, label: str) -> dict[str, object] | None:
    """Allow JSON null; GitHub returns null for these fields on non-merged PRs."""
    if value is None:
        return None
    return _string_keyed_mapping(value, label)


def _string_keyed_mapping(value: object, label: str) -> dict[str, object]:
    """Validate a JSON object and narrow its keys before reading any field."""
    if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
        raise BoundaryFailure(f"GitHub CLI {label} was not a string-keyed object.")
    return cast(dict[str, object], value)


def _required_string(value: object, label: str) -> str:
    """Require one non-empty string from the external PR payload."""
    if not isinstance(value, str) or not value:
        raise BoundaryFailure(f"GitHub CLI PR field {label} is missing or invalid.")
    return value
