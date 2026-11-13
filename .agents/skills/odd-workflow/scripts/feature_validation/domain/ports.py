"""Declare the source boundary for discovering and reading feature documents."""

from typing import Protocol


class FeatureSource(Protocol):
    """Provide document references and text to the validation operation."""

    def discover(self, target: str) -> tuple[str, ...]:
        """Return candidate document references for a target."""
        ...

    def read(self, reference: str) -> str:
        """Return document text, allowing boundary exceptions to propagate."""
        ...
