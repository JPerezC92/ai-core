"""Typed core-sync domain errors: stable codes returned as values, plus the raised marker and JSONC errors."""

from __future__ import annotations

from dataclasses import dataclass

CODE_DRIFT = "drift"
CODE_INVALID = "invalid"


@dataclass(frozen=True)
class DomainError:
    """A business failure carried as a value with a stable code and a message."""

    code: str
    message: str


class MalformedSourceMarkers(ValueError):
    """A region-mode source has core or project marker lines without one valid core pair."""

    code: str = CODE_INVALID


class MalformedJsonc(ValueError):
    """A JSON/JSONC document is malformed or its top level is not an object."""

    code: str = CODE_INVALID
