"""Declare the document and remote-branch boundaries for the closure check."""

from typing import Protocol


class FeatureDocumentSource(Protocol):
    """Provide candidate document references and text to the closure check."""

    def discover(self, target: str) -> tuple[str, ...]:
        """Return candidate document references for a target."""
        ...

    def read(self, reference: str) -> str:
        """Return document text, allowing boundary exceptions to propagate."""
        ...


class RemoteBranchProbe(Protocol):
    """Report whether a branch still exists on a remote."""

    def exists(self, remote: str, branch: str) -> bool:
        """Return True when the remote still advertises the branch."""
        ...
