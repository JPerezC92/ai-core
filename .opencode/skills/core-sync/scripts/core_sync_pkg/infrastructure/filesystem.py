"""Infrastructure: local filesystem IO adapters and the write-target preflight."""

from __future__ import annotations

import os
import stat
from pathlib import Path

from core_sync_pkg.domain.bindings import Bindings
from core_sync_pkg.domain.constants import (
    DEFAULT_ROOT_CANDIDATES,
    MODE_RAW,
    CommandName,
)
from core_sync_pkg.domain.reconciliation import (
    reconciliation_report_path,
    sync_reconciliation_blocker,
)
from core_sync_pkg.domain.regions import _path_is_within, extract_source_core


def read_text(path: Path) -> str | None:
    """Read UTF-8 text from a path at the IO boundary."""
    try:
        with path.open("r", encoding="utf-8", newline="") as file:
            return file.read()
    except (OSError, UnicodeError):
        return None


def write_text(path: Path, content: str) -> None:
    """Write UTF-8 text to a path at the IO boundary."""
    with path.open("w", encoding="utf-8", newline="") as file:
        file.write(content)


def read_bytes(path: Path) -> bytes | None:
    """Read raw bytes from a path at the IO boundary, or None when unreadable."""
    try:
        return path.read_bytes()
    except OSError:
        return None


def write_bytes(path: Path, content: bytes) -> None:
    """Write raw bytes to a path at the IO boundary."""
    path.write_bytes(content)


def read_source_raw(path: Path) -> bytes | None:
    """Read a source file's bytes verbatim at the IO boundary (raw mode)."""
    return read_bytes(path)


def read_source_core(path: Path) -> str | None:
    """Read a source file's core at the IO boundary.

    Raises `MalformedSourceMarkers` when the source has exact core or project
    marker lines outside fences but no single ordered core pair.
    """
    content = read_text(path)
    if content is None:
        return None
    return extract_source_core(content)


def resolve_root_path(destination_dir: Path, bindings: Bindings) -> Path:
    """Resolve the destination root runtime file at the IO boundary.

    Uses the explicit `root` bindings field when present; otherwise defaults to
    `AGENTS.md` when it exists in the destination, else `CLAUDE.md`.
    """
    root = bindings.get("root")
    if root is not None:
        return destination_dir / root
    for candidate in DEFAULT_ROOT_CANDIDATES:
        path = destination_dir / candidate
        if path.is_file():
            return path
    return destination_dir / DEFAULT_ROOT_CANDIDATES[-1]


def _source_regular_file_inodes(source_dir: Path) -> set[tuple[int, int]]:
    """Collect regular-file device/inode identities reachable under the source root."""
    try:
        root_stat = source_dir.stat()
    except FileNotFoundError:
        return set()
    if stat.S_ISREG(root_stat.st_mode):
        return {(root_stat.st_dev, root_stat.st_ino)}
    if not stat.S_ISDIR(root_stat.st_mode):
        return set()

    inodes: set[tuple[int, int]] = set()
    visited_directories = {(root_stat.st_dev, root_stat.st_ino)}
    directories = [source_dir]
    while directories:
        directory = directories.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                try:
                    entry_stat = entry.stat(follow_symlinks=True)
                except FileNotFoundError:
                    if entry.is_symlink():
                        continue
                    raise
                identity = (entry_stat.st_dev, entry_stat.st_ino)
                if stat.S_ISDIR(entry_stat.st_mode):
                    if identity not in visited_directories:
                        visited_directories.add(identity)
                        directories.append(Path(entry.path))
                elif stat.S_ISREG(entry_stat.st_mode):
                    inodes.add(identity)
    return inodes


def preflight_write_targets(
    command: CommandName,
    source_dir: Path,
    destination_dir: Path,
    bindings_path: Path,
    bindings: Bindings,
    new_raw_destinations: set[str] | None = None,
) -> str | None:
    """Reject unsafe, aliased, or source-inode write targets before mutation."""
    try:
        resolved_source = source_dir.resolve()
        resolved_destination = destination_dir.resolve()
    except (OSError, RuntimeError) as error:
        return f"could not resolve source or destination root: {error}"

    if _path_is_within(resolved_source, resolved_destination) or _path_is_within(
        resolved_destination, resolved_source
    ):
        return "source and destination roots overlap"

    try:
        source_file_inodes = _source_regular_file_inodes(source_dir)
    except OSError as error:
        return f"could not inspect source tree for write protection: {error}"

    root_path = resolve_root_path(destination_dir, bindings)
    raw_destination_paths = [
        destination_dir / destination
        for entry in bindings["bindings"]
        if entry["mode"] == MODE_RAW
        for destination in entry["destinations"]
    ]
    targets: list[tuple[Path, str]] = [(root_path, "root")]
    if command in ("apply", "init"):
        targets.extend(
            (destination_dir / destination, "destination payload")
            for entry in bindings["bindings"]
            for destination in entry["destinations"]
        )
        targets.append((bindings_path, "bindings"))
    if command == "init":
        targets.append((reconciliation_report_path(bindings_path), "report"))

    resolved_root: Path | None = None
    resolved_targets: dict[Path, tuple[Path, Path, str]] = {}
    target_inodes: dict[tuple[int, int], tuple[Path, Path, str]] = {}
    for target, target_kind in targets:
        try:
            resolved_target = target.resolve()
        except (OSError, RuntimeError) as error:
            return (
                f"could not resolve {target_kind} write target {target}: {error}"
            )
        lexical_target = Path(os.path.abspath(target))
        previous_target = resolved_targets.get(resolved_target)
        if previous_target is not None:
            previous_path, previous_lexical, previous_kind = previous_target
            if (
                previous_kind == "root"
                and target_kind == "destination payload"
                and target in raw_destination_paths
            ):
                return f"root write target aliases raw destination: {target}"
            same_root_region_target = (
                lexical_target == previous_lexical
                and {target_kind, previous_kind} == {"root", "destination payload"}
                and target not in raw_destination_paths
            )
            if not same_root_region_target:
                return (
                    "distinct write targets alias after resolution: "
                    f"{previous_path} and {target}"
                )
        else:
            resolved_targets[resolved_target] = (
                target,
                lexical_target,
                target_kind,
            )
        if _path_is_within(resolved_target, resolved_source):
            return f"{target_kind} write target resolves inside source tree: {target}"
        if target_kind in ("root", "destination payload") and not _path_is_within(
            resolved_target, resolved_destination
        ):
            return f"{target_kind} write target escapes destination root: {target}"
        try:
            target_stat = target.stat()
        except FileNotFoundError:
            target_stat = None
        except OSError as error:
            return f"could not inspect {target_kind} write target {target}: {error}"
        if target_stat is not None and stat.S_ISREG(target_stat.st_mode):
            target_inode = (target_stat.st_dev, target_stat.st_ino)
            if target_inode in source_file_inodes:
                return (
                    f"{target_kind} write target shares a source-tree file inode: "
                    f"{target}"
                )
            previous_inode_target = target_inodes.get(target_inode)
            if previous_inode_target is not None:
                previous_path, previous_lexical, previous_kind = previous_inode_target
                same_root_region_target = (
                    lexical_target == previous_lexical
                    and {target_kind, previous_kind}
                    == {"root", "destination payload"}
                )
                if not same_root_region_target:
                    return (
                        "distinct write targets share a filesystem inode: "
                        f"{previous_path} and {target}"
                    )
            else:
                target_inodes[target_inode] = (
                    target,
                    lexical_target,
                    target_kind,
                )
        if target_kind == "root":
            resolved_root = resolved_target

    for raw_destination_path in raw_destination_paths:
        try:
            resolved_raw_destination = raw_destination_path.resolve()
        except (OSError, RuntimeError) as error:
            return (
                "could not resolve raw destination write target "
                f"{raw_destination_path}: {error}"
            )
        if resolved_root == resolved_raw_destination:
            return (
                "root write target aliases raw destination: "
                f"{raw_destination_path}"
            )
        try:
            root_stat = root_path.stat()
            raw_stat = raw_destination_path.stat()
        except FileNotFoundError:
            continue
        except OSError as error:
            return (
                "could not inspect root/raw destination alias targets: "
                f"{error}"
            )
        if (
            stat.S_ISREG(root_stat.st_mode)
            and stat.S_ISREG(raw_stat.st_mode)
            and (root_stat.st_dev, root_stat.st_ino)
            == (raw_stat.st_dev, raw_stat.st_ino)
        ):
            return (
                "root write target aliases raw destination: "
                f"{raw_destination_path}"
            )

    if command == "init" and bindings.get("root") is None:
        agents_path = destination_dir / DEFAULT_ROOT_CANDIDATES[0]
        if not agents_path.is_file():
            try:
                resolved_agents_path = agents_path.resolve()
            except (OSError, RuntimeError) as error:
                return f"could not resolve default root candidate {agents_path}: {error}"
            for destination in new_raw_destinations or set():
                raw_path = destination_dir / destination
                if (
                    raw_path.exists()
                    or raw_path.is_symlink()
                    or not raw_path.parent.is_dir()
                ):
                    continue
                try:
                    resolved_raw_path = raw_path.resolve()
                except (OSError, RuntimeError) as error:
                    return (
                        "could not resolve planned raw destination "
                        f"{raw_path}: {error}"
                    )
                if resolved_raw_path == resolved_agents_path:
                    return (
                        "default root would alias newly created raw destination: "
                        f"{raw_path}"
                    )

    return None


def write_reconciliation_blocker(root_path: Path, pending: list[str]) -> bool:
    """Sync the reconciliation blocker block into the root file at the IO boundary.

    Reads the root file, applies `sync_reconciliation_blocker`, and writes it back
    only when the text changed. Returns False when the root file is missing or
    unreadable so the caller can skip it silently.
    """
    root_text = read_text(root_path)
    if root_text is None:
        return False
    new_text = sync_reconciliation_blocker(root_text, pending)
    if new_text != root_text:
        write_text(root_path, new_text)
    return True


class LocalFilesystemPaths:
    """Local filesystem path queries and write-target preflight."""

    def is_file(self, path: Path) -> bool:
        return path.is_file()

    def is_dir(self, path: Path) -> bool:
        return path.is_dir()

    def exists(self, path: Path) -> bool:
        return path.exists()

    def is_symlink(self, path: Path) -> bool:
        return path.is_symlink()

    def preflight_write_targets(
        self,
        command: CommandName,
        source_dir: Path,
        destination_dir: Path,
        bindings_path: Path,
        bindings: Bindings,
        new_raw_destinations: set[str] | None = None,
    ) -> str | None:
        return preflight_write_targets(
            command,
            source_dir,
            destination_dir,
            bindings_path,
            bindings,
            new_raw_destinations,
        )


class LocalSourceCoreReader:
    """Read source cores and raw source bytes from the local filesystem."""

    def read_core(self, path: Path) -> str | None:
        return read_source_core(path)

    def read_raw(self, path: Path) -> bytes | None:
        return read_source_raw(path)


class LocalDestinationWriter:
    """Read and write destination content on the local filesystem."""

    def read_text(self, path: Path) -> str | None:
        return read_text(path)

    def read_bytes(self, path: Path) -> bytes | None:
        return read_bytes(path)

    def write_text(self, path: Path, content: str) -> None:
        write_text(path, content)

    def write_bytes(self, path: Path, content: bytes) -> None:
        write_bytes(path, content)


class LocalRootRuntimeFile:
    """Resolve and sync the destination root runtime file's blocker block."""

    def resolve(self, destination_dir: Path, bindings: Bindings) -> Path:
        return resolve_root_path(destination_dir, bindings)

    def write_blocker(self, root_path: Path, pending: list[str]) -> bool:
        return write_reconciliation_blocker(root_path, pending)


__all__ = [
    "read_text",
    "write_text",
    "read_bytes",
    "write_bytes",
    "read_source_raw",
    "read_source_core",
    "resolve_root_path",
    "preflight_write_targets",
    "write_reconciliation_blocker",
    "LocalFilesystemPaths",
    "LocalSourceCoreReader",
    "LocalDestinationWriter",
    "LocalRootRuntimeFile",
]
