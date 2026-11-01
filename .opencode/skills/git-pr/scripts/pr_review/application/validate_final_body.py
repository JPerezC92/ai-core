"""Validate supplied remote freshness and a conservative completed review body."""

from pr_review.domain.body_validation import validate_body
from pr_review.domain.review_content_preservation import validate_preservation
from pr_review.domain.records import PreparedBody, ReviewPreparationError, parse_metadata
from pr_review.domain.review_decisions import parse_decisions


def execute(*, baseline: object, current: object, body: str, decisions: object = None) -> PreparedBody | ReviewPreparationError:
    """Reject stale supplied metadata before checking body structure."""
    accepted = parse_metadata(baseline)
    observed = parse_metadata(current)
    if isinstance(accepted, ReviewPreparationError):
        return accepted
    if isinstance(observed, ReviewPreparationError):
        return observed
    if accepted != observed:
        return ReviewPreparationError("REMOTE_DIVERGED", "remote metadata differs from accepted baseline")
    supplied = parse_decisions(decisions, observed)
    if isinstance(supplied, ReviewPreparationError):
        return supplied
    failure = validate_body(body, observed, supplied)
    if failure is not None:
        return failure
    failure = validate_preservation(accepted["body"], body)
    return failure if failure is not None else PreparedBody(body)
