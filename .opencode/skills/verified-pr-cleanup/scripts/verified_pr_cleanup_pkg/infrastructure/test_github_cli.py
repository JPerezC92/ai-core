"""Integration tests for mapping fake GitHub CLI JSON into domain PR data."""

from __future__ import annotations

import json
import subprocess

import pytest

from verified_pr_cleanup_pkg.domain.guards import pull_request_identity_error
from verified_pr_cleanup_pkg.domain.models import BoundaryFailure
from verified_pr_cleanup_pkg.domain._test_support import CleanupTestData as Data
from verified_pr_cleanup_pkg.infrastructure.github_cli import GitHubCli


def _client(
    monkeypatch: pytest.MonkeyPatch, payload: dict[str, object], exit_code: int = 0
) -> GitHubCli:
    """Build a GitHub adapter with a local fake process response."""
    client = GitHubCli.__new__(GitHubCli)
    client._executable = Data.GH_FAKE_EXECUTABLE
    completed = subprocess.CompletedProcess(
        [Data.GH_FAKE_EXECUTABLE], exit_code,
        json.dumps(payload).encode("utf-8"), Data.GH_FAKE_STDERR,
    )

    def fake_run(arguments: list[str]) -> subprocess.CompletedProcess[bytes]:
        return completed

    monkeypatch.setattr(client, "_run", fake_run)
    return client


def test_fake_github_response_maps_exact_pr_number_and_repository(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Read mapped metadata through the argument-array GitHub CLI boundary."""
    client = _client(monkeypatch, Data.github_payload())
    pull_request = client.fetch(Data.PR_NUMBER, Data.repository())
    assert pull_request.number == Data.PR_NUMBER
    assert pull_request.head_oid == Data.HEAD_OID
    assert pull_request.head_repository == Data.repository().full_name


@pytest.mark.parametrize("number", Data.INVALID_GITHUB_PR_NUMBERS)
def test_fake_github_response_rejects_invalid_pr_number(
    monkeypatch: pytest.MonkeyPatch, number: object
) -> None:
    """Reject malformed or mismatched response identity without external network."""
    payload = Data.github_payload(number=number)
    client = _client(monkeypatch, payload)
    with pytest.raises(BoundaryFailure):
        client.fetch(Data.PR_NUMBER, Data.repository())


def test_fake_github_open_payload_accepts_null_merge_and_head_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Accept live OPEN-PR nulls without a boundary failure and let the guard block."""
    payload = Data.github_payload(state=Data.OPEN_PR_STATE)
    assert payload["mergedAt"] is None
    assert payload["mergeCommit"] is None
    payload["headRepository"] = None
    payload["headRepositoryOwner"] = None
    client = _client(monkeypatch, payload)
    pull_request = client.fetch(Data.PR_NUMBER, Data.repository())
    assert pull_request.state == Data.OPEN_PR_STATE
    assert pull_request.merged_at is None
    assert pull_request.merge_commit_oid is None
    assert pull_request.head_repository == ""
    assert pull_request.head_owner == ""
    assert pull_request_identity_error(
        pull_request, Data.PR_NUMBER, Data.repository(), Data.BASE_BRANCH
    ) == "The pull request is not verifiably MERGED."


def test_fake_github_null_head_identity_blocks_instead_of_raising(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Map a null head repository/owner to empty strings the identity guard rejects."""
    payload = Data.github_payload()
    payload["headRepository"] = None
    payload["headRepositoryOwner"] = None
    client = _client(monkeypatch, payload)
    pull_request = client.fetch(Data.PR_NUMBER, Data.repository())
    assert pull_request.head_repository == ""
    assert pull_request.head_owner == ""
    assert pull_request_identity_error(
        pull_request, Data.PR_NUMBER, Data.repository(), Data.BASE_BRANCH
    ) == "The pull-request head repository does not match the configured repository."


def test_fake_github_cli_failure_remains_a_boundary_exception(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Do not convert a failed external CLI boundary into a domain result."""
    client = _client(monkeypatch, Data.github_payload(), exit_code=Data.GITHUB_FAILURE_EXIT_CODE)
    with pytest.raises(BoundaryFailure):
        client.fetch(Data.PR_NUMBER, Data.repository())


@pytest.mark.parametrize(
    "field,value",
    Data.MALFORMED_GITHUB_PAYLOAD_FIELDS,
)
def test_fake_github_payload_runtime_validates_nested_shapes(
    monkeypatch: pytest.MonkeyPatch, field: str, value: object
) -> None:
    """Reject malformed nested GitHub JSON before constructing domain data."""
    payload = Data.github_payload()
    payload[field] = value
    client = _client(monkeypatch, payload)
    with pytest.raises(BoundaryFailure):
        client.fetch(Data.PR_NUMBER, Data.repository())


def test_fake_github_payload_rejects_a_different_positive_pr_number(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Bind adapter output to the requested PR even when the returned number is valid."""
    client = _client(monkeypatch, Data.github_payload(number=Data.WRONG_PR_NUMBER))
    with pytest.raises(BoundaryFailure, match="different pull-request number"):
        client.fetch(Data.PR_NUMBER, Data.repository())
