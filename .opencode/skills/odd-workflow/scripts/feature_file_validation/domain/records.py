"""Define typed domain data for durable feature-file validation without transport policy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Literal

# The closed status vocabulary the derivation rule produces.
FeatureStatus = Literal["achieved", "partial", "not started"]


@dataclass(frozen=True)
class FeatureRequirement:
    """Carry one parsed feature-file requirement and its tick."""

    number: str
    mark: str
    wording: str
    ticked: bool


@dataclass(frozen=True)
class FeatureFileAssessment:
    """Carry the ordered findings and the status derived from the ticks."""

    findings: tuple[str, ...]
    status: FeatureStatus | None


@dataclass(frozen=True)
class ValidFeatureFile:
    """Identify a feature file with no validation findings and its derived status."""

    path: str
    status: FeatureStatus


@dataclass(frozen=True)
class InvalidFeatureFileError:
    """Return the ordered validation findings for a rejected feature file."""

    path: str
    findings: tuple[str, ...]
    code: ClassVar[str] = "FEATURE_FILE_INVALID"
    message: ClassVar[str] = "feature file is invalid"


@dataclass(frozen=True)
class NoFeatureFileDocumentsError:
    """Report that selection produced no feature files to validate."""

    code: ClassVar[str] = "NO_FEATURE_FILE_DOCUMENTS"
    message: ClassVar[str] = "no feature files found"


FeatureFileValidationResult = (
    ValidFeatureFile | InvalidFeatureFileError | NoFeatureFileDocumentsError
)
