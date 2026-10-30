"""Validate selected feature documents through an injected source boundary."""

from collections.abc import Iterator

from feature_validation.domain.ports import FeatureSource
from feature_validation.domain.records import (
    FeatureValidationResult,
    InvalidFeatureError,
    NoFeatureDocumentsError,
    ValidFeature,
)
from feature_validation.domain.rules import (
    is_template_reference,
    sort_feature_references,
    validate_feature,
)


def execute(target: str, source: FeatureSource) -> Iterator[FeatureValidationResult]:
    """Yield ordered validation outcomes, preserving lazy boundary failures."""
    references = tuple(
        reference
        for reference in sort_feature_references(source.discover(target))
        if not is_template_reference(reference)
    )
    if not references:
        yield NoFeatureDocumentsError()
        return

    for reference in references:
        findings = validate_feature(source.read(reference))
        if findings:
            yield InvalidFeatureError(path=reference, findings=tuple(findings))
        else:
            yield ValidFeature(path=reference)
