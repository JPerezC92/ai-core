"""Report active feature documents whose branch no longer exists on the remote."""

from collections.abc import Iterator

from feature_closure.domain.ports import FeatureDocumentSource, RemoteBranchProbe
from feature_closure.domain.records import (
    ClosureCheckResult,
    NoFeatureDocumentsError,
    UnclosedFeatureError,
)
from feature_closure.domain.rules import (
    branch_to_check,
    is_template_reference,
    sort_feature_references,
)


def execute(
    target: str,
    remote: str,
    source: FeatureDocumentSource,
    branches: RemoteBranchProbe,
) -> Iterator[ClosureCheckResult]:
    """Yield one outcome per unclosed feature, preserving lazy boundary failures."""
    references = tuple(
        reference
        for reference in sort_feature_references(source.discover(target))
        if not is_template_reference(reference)
    )
    if not references:
        yield NoFeatureDocumentsError()
        return

    for reference in references:
        branch = branch_to_check(source.read(reference))
        if branch is None:
            continue
        if not branches.exists(remote, branch):
            yield UnclosedFeatureError(path=reference, branch=branch)
