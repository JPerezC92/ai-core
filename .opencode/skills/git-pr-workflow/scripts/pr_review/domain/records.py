"""Define the workflow-side inventory record, prepared body, and returned failures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from attribution_scan.domain.records import Artifact, ChangedFile


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
class PreparedBody:
    """Preserve a structurally checked body without claiming evidence truth."""

    body: str
