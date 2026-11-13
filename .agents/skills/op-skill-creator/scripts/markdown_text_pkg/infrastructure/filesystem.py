"""Filesystem adapters: policy load, Markdown discovery, and JSON object reads."""

from __future__ import annotations

import json
import os
import stat
from pathlib import Path

from markdown_text_pkg.domain.models import (
    CODE_INPUT,
    CODE_IO,
    CODE_POLICY,
    DiscoverResult,
    DomainError,
    FileTarget,
    Policy,
)
from markdown_text_pkg.domain.policy import parse_policy

EXCLUDED_DIRECTORY_NAMES = frozenset(
    {
        ".git",
        ".secrets",
        "secrets",
        "output",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
    }
)


class DuplicateJsonKeyError(ValueError):
    """JSON object contained a duplicate key; not valid policy or editor input."""

    def __init__(self, key: str) -> None:
        self.key = key
        super().__init__(f"duplicate JSON key: {key}")


class NonFiniteJsonConstantError(ValueError):
    """JSON text used NaN, Infinity, or -Infinity, which are not JSON values."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"non-finite JSON constant: {name}")


class PolicyLoader:
    """Load a caller-supplied policy path without following symlinks or defaulting a location."""

    def load(self, path: str) -> Policy | DomainError:
        """Read, decode, and validate a policy document."""

        display = _posix_display(path)
        inspected = _inspect_regular_file(path, display, CODE_POLICY, "policy")
        if isinstance(inspected, DomainError):
            return inspected
        raw = _read_bytes(inspected, display, CODE_POLICY)
        if isinstance(raw, DomainError):
            return raw
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            return DomainError(CODE_POLICY, f"policy is not valid UTF-8: {display}")
        decoded = _decode_json_object(text, CODE_POLICY, "policy")
        if isinstance(decoded, DomainError):
            return decoded
        return parse_policy(decoded)


class MarkdownFilesystem:
    """Discover Markdown files and read bytes/JSON without following symlinks."""

    def discover(self, roots: tuple[str, ...]) -> DiscoverResult:
        """Inspect explicit roots, enter real directories, and skip excluded descendants."""

        targets: list[FileTarget] = []
        failures: list[DomainError] = []
        seen_roots: set[str] = set()
        seen_files: set[str] = set()
        for raw in sorted(roots, key=_posix_display):
            display = _posix_display(raw)
            abs_norm = _abs_norm(raw)
            if abs_norm in seen_roots:
                continue
            seen_roots.add(abs_norm)
            result = _inspect_explicit_root(raw, display, abs_norm)
            if isinstance(result, DomainError):
                failures.append(result)
                continue
            if isinstance(result, FileTarget):
                if result.abs_norm not in seen_files:
                    seen_files.add(result.abs_norm)
                    targets.append(result)
                continue
            _walk_directory(result, display, seen_files, targets, failures)
        return DiscoverResult(targets=tuple(targets), failures=tuple(failures))

    def read_bytes(self, target: FileTarget) -> bytes | DomainError:
        """Read a discovered Markdown file as raw bytes."""

        return _read_bytes(target.abs_norm, target.display_path, CODE_IO)

    def load_json_object(self, path: str) -> dict[str, object] | DomainError:
        """Load editor settings JSON without following symlinks."""

        display = _posix_display(path)
        inspected = _inspect_regular_file(path, display, CODE_INPUT, "editor")
        if isinstance(inspected, DomainError):
            return inspected
        raw = _read_bytes(inspected, display, CODE_IO)
        if isinstance(raw, DomainError):
            return raw
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            return DomainError(CODE_INPUT, f"editor is not valid UTF-8: {display}")
        return _decode_json_object(text, CODE_INPUT, "editor")


def _posix_display(path: str) -> str:
    """Normalize separators for display and sort without following the target."""

    return path.replace("\\", "/")


def _abs_norm(path: str) -> str:
    """Absolute normalized path identity without resolving or following links."""

    return os.path.normpath(os.path.abspath(path))


def _inspect_explicit_root(
    raw: str, display: str, abs_norm: str
) -> FileTarget | str | DomainError:
    """Classify an explicit user-supplied root without following links."""

    try:
        info = os.lstat(abs_norm)
    except FileNotFoundError:
        return DomainError(CODE_INPUT, f"missing path: {display}")
    except OSError:
        return DomainError(CODE_IO, f"unreadable path: {display}")
    if stat.S_ISLNK(info.st_mode):
        return DomainError(CODE_INPUT, f"symlink not followed: {display}")
    if stat.S_ISREG(info.st_mode):
        if Path(raw).suffix.lower() != ".md":
            return DomainError(CODE_INPUT, f"not a markdown file: {display}")
        return FileTarget(display_path=display, abs_norm=abs_norm)
    if stat.S_ISDIR(info.st_mode):
        return abs_norm
    return DomainError(CODE_INPUT, f"not a markdown file or directory: {display}")


def _inspect_regular_file(
    raw: str, display: str, error_code: str, label: str
) -> str | DomainError:
    """Require a real regular file at path; symlinks and directories fail closed."""

    abs_norm = _abs_norm(raw)
    try:
        info = os.lstat(abs_norm)
    except FileNotFoundError:
        return DomainError(error_code, f"missing {label} path: {display}")
    except OSError:
        return DomainError(CODE_IO, f"unreadable {label} path: {display}")
    if stat.S_ISLNK(info.st_mode):
        return DomainError(error_code, f"symlink not followed: {display}")
    if not stat.S_ISREG(info.st_mode):
        return DomainError(error_code, f"{label} path is not a regular file: {display}")
    return abs_norm


def _walk_directory(
    dir_abs: str,
    display: str,
    seen_files: set[str],
    targets: list[FileTarget],
    failures: list[DomainError],
) -> None:
    """Recurse into an entered real directory; skip excluded child directory names."""

    try:
        entries = list(os.scandir(dir_abs))
    except OSError:
        failures.append(DomainError(CODE_IO, f"unreadable path: {display}"))
        return
    entries.sort(key=lambda entry: entry.name)
    for entry in entries:
        child_display = f"{display.rstrip('/')}/{entry.name}"
        try:
            if entry.is_symlink():
                continue
            if entry.is_dir(follow_symlinks=False):
                if entry.name.lower() in EXCLUDED_DIRECTORY_NAMES:
                    continue
                _walk_directory(
                    entry.path, child_display, seen_files, targets, failures
                )
                continue
            if not entry.is_file(follow_symlinks=False):
                continue
            if Path(entry.name).suffix.lower() != ".md":
                continue
            child_abs = _abs_norm(entry.path)
            if child_abs in seen_files:
                continue
            seen_files.add(child_abs)
            targets.append(FileTarget(display_path=child_display, abs_norm=child_abs))
        except OSError:
            failures.append(DomainError(CODE_IO, f"unreadable path: {child_display}"))


def _read_bytes(abs_norm: str, display: str, error_code: str) -> bytes | DomainError:
    """Read raw bytes; map OS errors to a typed IO/policy failure."""

    try:
        with open(abs_norm, "rb") as handle:
            return handle.read()
    except OSError:
        return DomainError(error_code, f"unreadable path: {display}")


def _decode_json_object(
    text: str, error_code: str, label: str
) -> dict[str, object] | DomainError:
    """Decode a JSON object, rejecting duplicate keys and non-finite constants."""

    try:
        decoded: object = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_nonfinite_constant,
        )
    except DuplicateJsonKeyError as exc:
        return DomainError(error_code, f"invalid {label} JSON: duplicate key {exc.key}")
    except json.JSONDecodeError as exc:
        return DomainError(error_code, f"invalid {label} JSON: {exc.msg}")
    except NonFiniteJsonConstantError as exc:
        return DomainError(error_code, f"invalid {label} JSON: {exc}")
    if not isinstance(decoded, dict):
        return DomainError(error_code, f"{label} JSON root must be an object")
    return decoded


def _reject_nonfinite_constant(name: str) -> object:
    """Reject NaN, Infinity, and -Infinity; they are not JSON values."""

    raise NonFiniteJsonConstantError(name)


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Fail closed when a JSON object repeats a key at the same level."""

    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJsonKeyError(key)
        result[key] = value
    return result
