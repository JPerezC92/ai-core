"""Specify the closure check operation through deterministic port doubles."""

from __future__ import annotations

import sys
from pathlib import Path, PurePath

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPTS))

from feature_closure.application.check_feature_closure import execute  # noqa: E402
from feature_closure.domain.records import (  # noqa: E402
    NoFeatureDocumentsError,
    UnclosedFeatureError,
)
from feature_closure.test_support import (  # noqa: E402
    GIT_LIVE_BRANCH,
    GIT_REMOTE_NAME,
    GIT_REMOVED_BRANCH,
)
from feature_testkit import make_feature  # noqa: E402

FEATURES_DIR = "odd/tasks"
TEMPLATE_REFERENCE = "odd/tasks/_template.md"
CLOSED_REFERENCE = "odd/tasks/closed.md"
LIVE_REFERENCE = "odd/tasks/live.md"
REMOVED_REFERENCE = "odd/tasks/merged.md"
UNSET_REFERENCE = "odd/tasks/unset.md"


class ClosureSourceFake:
    """Supply factory-built documents and record reads without filesystem IO."""

    def __init__(
        self,
        documents: dict[str, str],
        references: tuple[str, ...],
        failing_reference: str | None = None,
        read_error: OSError | None = None,
    ) -> None:
        self.documents = documents
        self.references = references
        self.failing_reference = failing_reference
        self.read_error = read_error
        self.reads: list[str] = []
        self.targets: list[str] = []

    @classmethod
    def create(
        cls,
        *,
        no_features: bool = False,
        template_only: bool = False,
        later_read_failed: bool = False,
    ) -> ClosureSourceFake:
        """Build deliberately unsorted candidates covering every document disposition."""
        documents = {
            TEMPLATE_REFERENCE: make_feature(title="Feature name", branch=f"`{GIT_REMOVED_BRANCH}`"),
            CLOSED_REFERENCE: make_feature(
                status="closed", branch=f"`{GIT_REMOVED_BRANCH}`"
            ),
            LIVE_REFERENCE: make_feature(branch=f"`{GIT_LIVE_BRANCH}`"),
            REMOVED_REFERENCE: make_feature(branch=f"`{GIT_REMOVED_BRANCH}`"),
            UNSET_REFERENCE: make_feature(branch="N/A — no branch yet"),
        }
        if no_features:
            if template_only:
                return cls(
                    {TEMPLATE_REFERENCE: documents[TEMPLATE_REFERENCE]}, (TEMPLATE_REFERENCE,)
                )
            return cls({}, ())
        references = (
            UNSET_REFERENCE,
            REMOVED_REFERENCE,
            TEMPLATE_REFERENCE,
            CLOSED_REFERENCE,
            LIVE_REFERENCE,
        )
        return cls(
            documents,
            references,
            UNSET_REFERENCE if later_read_failed else None,
            OSError("later document cannot be read") if later_read_failed else None,
        )

    def discover(self, target: str) -> tuple[str, ...]:
        """Return references in source order rather than policy order."""
        self.targets.append(target)
        return self.references

    def read(self, reference: str) -> str:
        """Return text or propagate the configured later-read boundary error."""
        self.reads.append(reference)
        if reference == self.failing_reference and self.read_error is not None:
            raise self.read_error
        return self.documents[reference]


class RemoteBranchProbeFake:
    """Record each branch query and answer from a fixed presence set."""

    def __init__(self, present: frozenset[str]) -> None:
        self.present = present
        self.queries: list[tuple[str, str]] = []

    @classmethod
    def create(cls, *, present: tuple[str, ...] = (GIT_LIVE_BRANCH,)) -> RemoteBranchProbeFake:
        """Build a probe whose remote advertises exactly the supplied branches."""
        return cls(frozenset(present))

    def exists(self, remote: str, branch: str) -> bool:
        """Return presence and record the query the operation made."""
        self.queries.append((remote, branch))
        return branch in self.present


def test_candidates_are_read_in_host_path_order_and_never_include_the_template() -> None:
    source = ClosureSourceFake.create()

    list(execute(FEATURES_DIR, GIT_REMOTE_NAME, source, RemoteBranchProbeFake.create()))

    assert source.targets == [FEATURES_DIR]
    assert source.reads == [
        reference
        for reference in sorted(source.references, key=PurePath)
        if reference != TEMPLATE_REFERENCE
    ]
    assert TEMPLATE_REFERENCE not in source.reads


def test_only_checkable_active_branches_are_queried_on_the_selected_remote() -> None:
    probe = RemoteBranchProbeFake.create()

    list(execute(FEATURES_DIR, GIT_REMOTE_NAME, ClosureSourceFake.create(), probe))

    assert probe.queries == [
        (GIT_REMOTE_NAME, GIT_LIVE_BRANCH),
        (GIT_REMOTE_NAME, GIT_REMOVED_BRANCH),
    ]


def test_active_feature_whose_branch_disappeared_is_reported_with_path_and_branch() -> None:
    results = list(
        execute(FEATURES_DIR, GIT_REMOTE_NAME, ClosureSourceFake.create(), RemoteBranchProbeFake.create())
    )

    assert len(results) == 1
    report = results[0]
    assert isinstance(report, UnclosedFeatureError)
    assert report.code == "FEATURE_UNCLOSED"
    assert report.path == REMOVED_REFERENCE
    assert report.branch == GIT_REMOVED_BRANCH


def test_feature_whose_branch_still_exists_is_not_reported() -> None:
    results = list(
        execute(
            FEATURES_DIR,
            GIT_REMOTE_NAME,
            ClosureSourceFake.create(),
            RemoteBranchProbeFake.create(present=(GIT_LIVE_BRANCH, GIT_REMOVED_BRANCH)),
        )
    )

    assert results == []


@pytest.mark.parametrize("template_only", (False, True))
def test_empty_selection_returns_typed_error_without_reads_or_queries(
    template_only: bool,
) -> None:
    source = ClosureSourceFake.create(no_features=True, template_only=template_only)
    probe = RemoteBranchProbeFake.create()

    results = list(execute(FEATURES_DIR, GIT_REMOTE_NAME, source, probe))

    assert len(results) == 1
    assert isinstance(results[0], NoFeatureDocumentsError)
    assert results[0].code == "NO_FEATURE_DOCUMENTS"
    assert source.reads == []
    assert probe.queries == []


def test_earlier_report_is_yielded_before_a_later_read_failure() -> None:
    source = ClosureSourceFake.create(later_read_failed=True)
    results = iter(
        execute(FEATURES_DIR, GIT_REMOTE_NAME, source, RemoteBranchProbeFake.create())
    )

    first = next(results)

    assert isinstance(first, UnclosedFeatureError)
    assert first.path == REMOVED_REFERENCE
    with pytest.raises(OSError) as raised:
        next(results)
    assert raised.value is source.read_error
