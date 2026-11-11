"""Protect baseline prose, exact test items and persistent finding identities."""

import re

from .body_validation import parse_findings, parse_sections
from .records import ReviewPreparationError


def validate_preservation(baseline: str, candidate: str) -> ReviewPreparationError | None:
    """Allow review-section updates without granting authority to rewrite prose.

    Evidence and resolution text may change under the designated writer's authority;
    this function does not establish that authority or verify the asserted facts.
    """
    error = ReviewPreparationError("BODY_INVALID", "protected baseline review content changed")
    before = parse_sections(baseline)
    after = parse_sections(candidate)
    if isinstance(before, ReviewPreparationError):
        return before
    if isinstance(after, ReviewPreparationError):
        return after
    for heading in ("Summary", "Breaking changes"):
        if before.get(heading) != after.get(heading):
            return error
    old_plan = re.sub(r"(?m)^- \[[ x]\] ", "- [ ] ", before["Test plan"])
    new_plan = re.sub(r"(?m)^- \[[ x]\] ", "- [ ] ", after["Test plan"])
    if old_plan != new_plan:
        return error
    previous = parse_findings(re.split(r"(?m)^\[(?:PASS|ADVISORY|BLOCK)\] —", before["Findings / blockers"])[0])
    updated = parse_findings(re.split(r"(?m)^\[(?:PASS|ADVISORY|BLOCK)\] —", after["Findings / blockers"])[0])
    if isinstance(previous, ReviewPreparationError):
        return previous
    if isinstance(updated, ReviewPreparationError):
        return updated
    if len(updated) < len(previous):
        return error
    for original, current in zip(previous, updated):
        if original.id != current.id or original.severity != current.severity:
            return error
    return None
