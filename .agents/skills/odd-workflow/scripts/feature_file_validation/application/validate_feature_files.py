"""Validate selected durable feature files through an injected source boundary."""

from collections.abc import Iterator

from feature_file_validation.domain.ports import FeatureFileSource
from feature_file_validation.domain.records import (
    FeatureFileValidationResult,
    InvalidFeatureFileError,
    NoFeatureFileDocumentsError,
    ValidFeatureFile,
)
from feature_file_validation.domain.rules import (
    assess_feature_file,
    is_template_reference,
    sort_feature_file_references,
)


def execute(target: str, source: FeatureFileSource) -> Iterator[FeatureFileValidationResult]:
    """Yield ordered validation outcomes, preserving lazy boundary failures."""
    references = tuple(
        reference
        for reference in sort_feature_file_references(source.discover(target))
        if not is_template_reference(reference)
    )
    if not references:
        yield NoFeatureFileDocumentsError()
        return

    for reference in references:
        assessment = assess_feature_file(source.read(reference))
        if assessment.findings or assessment.status is None:
            yield InvalidFeatureFileError(path=reference, findings=assessment.findings)
        else:
            yield ValidFeatureFile(path=reference, status=assessment.status)
