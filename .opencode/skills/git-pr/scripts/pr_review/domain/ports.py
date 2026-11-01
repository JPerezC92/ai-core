"""Declare the domain ports the review preparation operations depend on."""

from __future__ import annotations

from typing import Protocol


class GitInventoryPort(Protocol):
    """Declare the read-only Git inventory this operation depends on."""

    def resolve_commit(self, revision: str) -> str | None:
        """Return the object id a revision resolves to, or absence."""

    def merge_base(self, first: str, second: str) -> str | None:
        """Return the common ancestor of two revisions, or absence."""

    def list_commits(self, ancestor: str, head: str) -> list[str]:
        """Return the commit ids contained between an ancestor and a head commit."""

    def read_message(self, commit: str) -> str:
        """Return one commit message."""

    def list_changed_paths(self, ancestor: str, head: str) -> list[str]:
        """Return the exact changed path inventory, including deleted paths."""

    def list_deleted_paths(self, ancestor: str, head: str) -> list[str]:
        """Return the paths the range deletes, so no body is read for them."""

    def read_file(self, commit: str, path: str) -> str:
        """Return one file body as committed at the supplied commit."""
