"""Unit tests for canonical pull-request identity guards."""

from __future__ import annotations

from dataclasses import replace

from verified_pr_cleanup_pkg.domain.guards import pull_request_identity_error
from verified_pr_cleanup_pkg.domain._test_support import CleanupTestData as Data


def test_pr_identity_requires_canonical_url_and_exact_repository_number() -> None:
    """Accept the exact PR identity and reject adversarial URL/repository bindings."""
    repository = Data.repository()
    pull_request = Data.create()
    assert pull_request_identity_error(
        pull_request, Data.PR_NUMBER, repository, Data.BASE_BRANCH
    ) is None
    for url in Data.INVALID_PR_URLS:
        invalid = replace(pull_request, url=url)
        assert pull_request_identity_error(
            invalid, Data.PR_NUMBER, repository, Data.BASE_BRANCH
        ) is not None


def test_pr_identity_rejects_wrong_number_repository_base_and_merge_state() -> None:
    """Refuse mismatched PR number, head repository, base, and merged predicate."""
    repository = Data.repository()
    pull_request = Data.create()
    invalid_records = (
        (pull_request, Data.PR_NUMBER + 1, repository, Data.BASE_BRANCH),
        (replace(pull_request, head_repository=Data.OTHER_REPOSITORY), Data.PR_NUMBER, repository, Data.BASE_BRANCH),
        (replace(pull_request, base_branch=Data.WRONG_BASE_BRANCH), Data.PR_NUMBER, repository, Data.BASE_BRANCH),
        (replace(pull_request, state=Data.OPEN_PR_STATE), Data.PR_NUMBER, repository, Data.BASE_BRANCH),
    )
    for candidate, number, expected_repository, base_branch in invalid_records:
        assert pull_request_identity_error(candidate, number, expected_repository, base_branch) is not None
