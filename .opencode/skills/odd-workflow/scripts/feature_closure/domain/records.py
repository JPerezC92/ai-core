"""Define typed closure-check outcomes without transport policy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class UnclosedFeatureError:
    """Report a feature still active after its branch disappeared from the remote."""

    path: str
    branch: str
    code: ClassVar[str] = "FEATURE_UNCLOSED"
    message: ClassVar[str] = (
        "feature is still active after its branch disappeared from the remote"
    )


@dataclass(frozen=True)
class NoFeatureDocumentsError:
    """Report that selection produced no feature document to check."""

    code: ClassVar[str] = "NO_FEATURE_DOCUMENTS"
    message: ClassVar[str] = "no feature documents found"


ClosureCheckResult = UnclosedFeatureError | NoFeatureDocumentsError
