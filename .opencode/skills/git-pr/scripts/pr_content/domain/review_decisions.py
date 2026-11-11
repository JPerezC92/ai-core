"""Validate explicit supplied decision binding and provenance without authenticating it."""

from __future__ import annotations

from datetime import date

from .records import DecisionEvidence, ReviewDecisions, ReviewPreparationError, parse_metadata


def _parse_entries(value: object, *, debt: bool) -> tuple[DecisionEvidence, ...] | ReviewPreparationError:
    error = ReviewPreparationError("DECISIONS_INVALID", "complete unique decision provenance required")
    if not isinstance(value, list):
        return error
    entries: list[DecisionEvidence] = []
    fields = ("target", "actor", "date", "statement", "evidence", "destination")
    for entry in value:
        if not isinstance(entry, dict) or set(entry) != set(fields):
            return error
        if any(not isinstance(entry[field], str) for field in fields):
            return error
        if any(not entry[field].strip() for field in fields if field != "destination"):
            return error
        try:
            date.fromisoformat(entry["date"])
        except ValueError:
            return error
        if debt and not entry["destination"].strip():
            return error
        entries.append(DecisionEvidence(**entry))
    if len({entry.target for entry in entries}) != len(entries):
        return error
    return tuple(entries)


def parse_decisions(value: object, metadata: object) -> ReviewDecisions | ReviewPreparationError:
    """Check supplied records match the PR/head; owners verify actual authority."""
    context = parse_metadata(metadata)
    if isinstance(context, ReviewPreparationError):
        return ReviewPreparationError("DECISIONS_INVALID", context.message)
    if value is None:
        return ReviewDecisions()
    error = ReviewPreparationError("DECISIONS_INVALID", "decision PR/head binding required")
    if not isinstance(value, dict) or set(value) != {"pr_number", "head_sha", "not_applicable", "acceptance", "debt"}:
        return error
    if type(value["pr_number"]) is not int or value["pr_number"] != context["number"] or value["head_sha"] != context["headRefOid"]:
        return error
    na = _parse_entries(value["not_applicable"], debt=False)
    acceptance = _parse_entries(value["acceptance"], debt=False)
    debt = _parse_entries(value["debt"], debt=True)
    for result in (na, acceptance, debt):
        if isinstance(result, ReviewPreparationError):
            return result
    return ReviewDecisions(not_applicable=na, acceptance=acceptance, debt=debt)
