"""Compare supplied post-upload state with the exact intended review body."""

from pr_review.domain.records import PreparedBody, ReviewPreparationError, parse_metadata


def execute(*, expected: object, persisted: object, body: str) -> PreparedBody | ReviewPreparationError:
    """Return divergence without publishing, repairing, or retrying anything."""
    accepted = parse_metadata(expected)
    observed = parse_metadata(persisted)
    if isinstance(accepted, ReviewPreparationError):
        return accepted
    if isinstance(observed, ReviewPreparationError):
        return observed
    if any(accepted[key] != observed[key] for key in accepted if key != "body") or observed["body"] != body:
        return ReviewPreparationError("READBACK_DIVERGED", "persisted identity or body differs from intended publication")
    return PreparedBody(body)
