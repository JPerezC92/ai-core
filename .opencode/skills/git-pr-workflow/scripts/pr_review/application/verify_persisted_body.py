"""Compare supplied post-upload state with the exact intended review body."""

from pr_review.domain.records import PreparedBody, ReviewPreparationError

MISSING = object()


def execute(*, expected: object, persisted: object, body: str) -> PreparedBody | ReviewPreparationError:
    """Return divergence without publishing, repairing, or retrying anything."""
    if not isinstance(expected, dict) or not isinstance(persisted, dict):
        return ReviewPreparationError("READBACK_DIVERGED", "baseline and persisted captures must be objects")
    unmatched = sorted({str(key) for key in expected} ^ {str(key) for key in persisted})
    if unmatched:
        return ReviewPreparationError(
            "READBACK_DIVERGED",
            "persisted capture field set differs from the intended publication: "
            + ", ".join(unmatched),
        )
    divergent = [
        key for key in expected
        if key != "body" and persisted.get(key, MISSING) != expected[key]
    ]
    if divergent:
        return ReviewPreparationError(
            "READBACK_DIVERGED",
            "persisted capture fields differ from the intended publication: "
            + ", ".join(sorted(str(key) for key in divergent)),
        )
    if persisted.get("body") != body:
        return ReviewPreparationError(
            "READBACK_DIVERGED", "persisted body differs from the intended publication"
        )
    return PreparedBody(body)
