"""Define typed review inputs, successful bodies, and returned business failures."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import TypedDict, cast

from attribution_scan.domain.records import Artifact, ChangedFile


class ReviewMetadata(TypedDict):
    """Describe externally authenticated PR metadata supplied by its owner."""

    number: int
    headRefOid: str
    baseRefName: str
    headRefName: str
    state: str
    title: str
    body: str


METADATA_FIELDS = ("number", "headRefOid", "baseRefName", "headRefName", "state", "title", "body")


class LocalInventory(TypedDict):
    """Carry validated immutable content independently of locally authored prose."""

    schema: int
    pr_number: int
    head_sha: str
    base: str
    commit_messages: list[Artifact]
    changed_files: list[ChangedFile]


@dataclass(frozen=True)
class ReviewPreparationError:
    """Return a stable rejection code and explanation without raising it."""

    code: str
    message: str


@dataclass(frozen=True)
class Finding:
    """Carry validated finding columns by name across review rules."""

    id: str
    severity: str
    status: str
    evidence: str
    resolution: str


@dataclass(frozen=True)
class DecisionEvidence:
    """Carry supplied provenance, never independently authenticated authority."""

    target: str
    actor: str
    date: str
    statement: str
    evidence: str
    destination: str


@dataclass(frozen=True)
class ReviewDecisions:
    """Carry parsed decision records bound to supplied review metadata."""

    not_applicable: tuple[DecisionEvidence, ...] = ()
    acceptance: tuple[DecisionEvidence, ...] = ()
    debt: tuple[DecisionEvidence, ...] = ()


@dataclass(frozen=True)
class PreparedBody:
    """Preserve a structurally checked body without claiming evidence truth."""

    body: str


def parse_metadata(value: object) -> ReviewMetadata | ReviewPreparationError:
    """Validate decoded metadata without authenticating its external provenance."""
    if not isinstance(value, dict):
        return ReviewPreparationError("METADATA_INVALID", "metadata must be an object")
    if set(value) != set(METADATA_FIELDS):
        return ReviewPreparationError(
            "METADATA_INVALID",
            "metadata must contain exactly the documented fields: " + ", ".join(METADATA_FIELDS),
        )
    if type(value.get("number")) is not int or value["number"] < 1:
        return ReviewPreparationError("METADATA_INVALID", "positive PR number required")
    fields = ("headRefOid", "baseRefName", "headRefName", "state", "title", "body")
    if any(not isinstance(value.get(field), str) for field in fields):
        return ReviewPreparationError("METADATA_INVALID", "metadata string fields required")
    if re.fullmatch(r"[0-9a-fA-F]{7,64}", value["headRefOid"]) is None:
        return ReviewPreparationError("METADATA_INVALID", "immutable head required")
    if value["state"] != "OPEN" or any(not value[field].strip() for field in ("baseRefName", "headRefName", "title")):
        return ReviewPreparationError("METADATA_INVALID", "open PR and nonempty identity required")
    return cast(ReviewMetadata, value)
