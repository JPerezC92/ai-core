"""Domain IO ports: policy loading and Markdown filesystem access."""

from __future__ import annotations

from typing import Protocol

from markdown_text_pkg.domain.models import (
    DiscoverResult,
    DomainError,
    FileTarget,
    Policy,
)


class PolicyPort(Protocol):
    """Load and validate a caller-supplied policy document."""

    def load(self, path: str) -> Policy | DomainError:
        """Return a Policy or a typed policy/input/IO failure."""

        ...


class FilePort(Protocol):
    """Discover Markdown targets, read bytes, and load editor settings JSON."""

    def discover(self, roots: tuple[str, ...]) -> DiscoverResult:
        """Inspect explicit roots without following symlinks and walk entered directories."""

        ...

    def read_bytes(self, target: FileTarget) -> bytes | DomainError:
        """Read a discovered Markdown file as raw bytes."""

        ...

    def load_json_object(self, path: str) -> dict[str, object] | DomainError:
        """Load a JSON object from an editor settings path without following symlinks."""

        ...
