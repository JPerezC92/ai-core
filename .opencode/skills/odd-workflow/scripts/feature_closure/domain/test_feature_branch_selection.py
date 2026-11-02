"""Specify which remote branch an active feature document requires checking."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from feature_closure.domain.rules import branch_to_check  # noqa: E402
from feature_testkit import make_feature  # noqa: E402


@pytest.mark.parametrize(
    ("declared", "expected"),
    (("docs/odd/plain", "docs/odd/plain"), ("`docs/odd/quoted`", "docs/odd/quoted")),
)
def test_active_feature_requires_checking_its_declared_branch(declared: str, expected: str) -> None:
    assert branch_to_check(make_feature(branch=declared)) == expected


@pytest.mark.parametrize(
    "declared",
    ("N/A — not created yet", "N/A", "`N/A — no branch: Herald opens it at first commit`"),
)
def test_active_feature_without_a_branch_requires_no_check(declared: str) -> None:
    assert branch_to_check(make_feature(branch=declared)) is None


def test_document_without_a_branch_line_requires_no_check() -> None:
    assert branch_to_check(make_feature()) is None


def test_closed_feature_requires_no_check_even_with_a_declared_branch() -> None:
    assert branch_to_check(make_feature(status="closed", branch="`docs/odd/merged`")) is None


def test_document_without_a_status_line_requires_no_check() -> None:
    assert branch_to_check(make_feature(include_status=False, branch="`docs/odd/unknown`")) is None


def test_unrecognized_status_value_requires_no_check() -> None:
    assert branch_to_check(make_feature(status="Active", branch="`docs/odd/case`")) is None


def test_prose_after_a_quoted_branch_still_resolves_the_branch() -> None:
    document = make_feature(
        branch="`docs/architecture/whole-file-distribution` — created by the release owner; "
        "the branch was deleted after merge."
    )
    assert branch_to_check(document) == "docs/architecture/whole-file-distribution"


def test_prose_after_an_unquoted_branch_resolves_the_branch_name() -> None:
    document = make_feature(
        branch="fix/core-sync/frontmatter-parsing — created at the first work-unit commit"
    )
    assert branch_to_check(document) == "fix/core-sync/frontmatter-parsing"
