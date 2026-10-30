"""Define typed outcomes for feature-document validation without transport policy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class ValidFeature:
    """Identify a feature document with no validation findings."""

    path: str


@dataclass(frozen=True)
class InvalidFeatureError:
    """Return the ordered validation findings for a rejected feature document."""

    path: str
    findings: tuple[str, ...]
    code: ClassVar[str] = "FEATURE_INVALID"
    message: ClassVar[str] = "feature document is invalid"


@dataclass(frozen=True)
class NoFeatureDocumentsError:
    """Report that selection produced no feature documents to validate."""

    code: ClassVar[str] = "NO_FEATURE_DOCUMENTS"
    message: ClassVar[str] = "no feature documents found"


FeatureValidationResult = ValidFeature | InvalidFeatureError | NoFeatureDocumentsError
