"""Declare the source boundary for discovering and reading durable feature files."""

from typing import Protocol


class FeatureFileSource(Protocol):
    """Provide feature-file references and text to the validation operation."""

    def discover(self, target: str) -> tuple[str, ...]:
        """Return candidate feature-file references for a target."""
        ...

    def read(self, reference: str) -> str:
        """Return feature-file text, allowing boundary exceptions to propagate."""
        ...
