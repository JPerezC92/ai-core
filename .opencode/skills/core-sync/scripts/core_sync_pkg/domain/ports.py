"""Domain ports (role-named Protocols) and the shared use-case result value."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from core_sync_pkg.domain.bindings import Bindings
from core_sync_pkg.domain.clearance import ClearanceRecord
from core_sync_pkg.domain.constants import CommandName
from core_sync_pkg.domain.reconciliation import ReconciliationEntry


@dataclass(frozen=True)
class UseCaseResult:
    """The successful outcome of a use case: the CLI confirmation message."""

    message: str


class BindingsStore(Protocol):
    """Read, write, and report against the bindings document."""

    def load(self, path: Path) -> Bindings | None: ...

    def save(self, path: Path, bindings: Bindings) -> None: ...

    def write_report(
        self, bindings_path: Path, entries: list[ReconciliationEntry], revision: str
    ) -> None: ...


class SourceCoreReader(Protocol):
    """Read a source file's core region or raw bytes."""

    def read_core(self, path: Path) -> str | None: ...

    def read_raw(self, path: Path) -> bytes | None: ...


class DestinationWriter(Protocol):
    """Read and write destination file content."""

    def read_text(self, path: Path) -> str | None: ...

    def read_bytes(self, path: Path) -> bytes | None: ...

    def write_text(self, path: Path, content: str) -> None: ...

    def write_bytes(self, path: Path, content: bytes) -> None: ...


class ClearanceStore(Protocol):
    """Read the source distribution-clearance metadata."""

    def load(self, source_dir: Path) -> tuple[dict[str, ClearanceRecord] | None, bool]: ...


class RootRuntimeFile(Protocol):
    """Resolve the destination root runtime file and sync its blocker block."""

    def resolve(self, destination_dir: Path, bindings: Bindings) -> Path: ...

    def write_blocker(self, root_path: Path, pending: list[str]) -> bool: ...


class FilesystemPaths(Protocol):
    """Answer filesystem path questions and preflight write targets."""

    def is_file(self, path: Path) -> bool: ...

    def is_dir(self, path: Path) -> bool: ...

    def exists(self, path: Path) -> bool: ...

    def is_symlink(self, path: Path) -> bool: ...

    def detect_root(self, destination_dir: Path) -> str | None: ...

    def ensure_dir(self, path: Path) -> None: ...

    def preflight_write_targets(
        self,
        command: CommandName,
        source_dir: Path,
        destination_dir: Path,
        bindings_path: Path,
        bindings: Bindings,
        new_raw_destinations: set[str] | None = None,
        mode_of: dict[str, str] | None = None,
    ) -> str | None: ...
