"""Document loaders and file-reading helpers for adoption controls."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from adoption_contracts import (
    CatalogDocument,
    DeclarationDocument,
    LockDocument,
    RegistryDocument,
    ReviewDocument,
    _fail,
)
from adoption_digests import _sha256
from adoption_schema import (
    _parse_document_bytes,
    _validate_catalog_document,
    _validate_declaration_document,
    _validate_lock_document,
    _validate_registry_document,
    _validate_review_document,
)


def _read_document(path: str, code: str) -> dict[str, object]:
    """IO helper: read a YAML top-level mapping from ``path`` or fail with ``code``."""
    try:
        with open(path, "rb") as handle:
            return _parse_document_bytes(handle.read(), path, code)
    except FileNotFoundError:
        _fail(code, f"document not found: {path}")
    except OSError as exc:
        _fail(code, f"cannot read {path}: {exc}")


def load_catalog(path: str) -> CatalogDocument:
    """Parse and shape-validate a schema-v2 catalog document."""
    return _validate_catalog_document(
        _read_document(path, "invalid_mapping"), path
    )


def load_declaration(path: str) -> DeclarationDocument:
    """Parse and shape-validate a schema-v2 adopter declaration."""
    return _validate_declaration_document(
        _read_document(path, "invalid_declaration"), path
    )


def load_review(path: str) -> ReviewDocument:
    """Parse and shape-validate a schema-v2 reconciliation review."""
    return _validate_review_document(
        _read_document(path, "invalid_declaration"), path
    )


def load_lock(path: str) -> LockDocument:
    """Parse and shape-validate a schema-v2 generated lock."""
    return _validate_lock_document(_read_document(path, "invalid_lock"), path)


def _load_catalog_bytes(content: bytes, label: str) -> CatalogDocument:
    return _validate_catalog_document(
        _parse_document_bytes(content, label, "invalid_mapping"), label
    )


def load_registry(path: str) -> RegistryDocument:
    """Parse and shape-validate a schema-v2 adopter registry."""
    return _validate_registry_document(
        _read_document(path, "invalid_declaration"), path
    )


_ControlDocument = TypeVar(
    "_ControlDocument", DeclarationDocument, LockDocument, ReviewDocument
)


def _control_document_from_bytes(
    path: str,
    code: str,
    content: bytes,
    validate: Callable[[dict[str, object], str], _ControlDocument],
) -> tuple[_ControlDocument, str]:
    """Validate one captured control buffer and digest that same buffer.

    The document and digest both derive from ``content``. ``path`` is only the
    error label, so a later read of the file cannot disagree with the rows.
    """
    return (
        validate(_parse_document_bytes(content, path, code), path),
        _sha256(content),
    )


def _read_control_document(
    path: str,
    code: str,
    label: str,
    validate: Callable[[dict[str, object], str], _ControlDocument],
) -> tuple[_ControlDocument, str]:
    """Read one control file once, then parse and hash that captured buffer."""
    return _control_document_from_bytes(
        path, code, _read_path_bytes(path, code, label), validate
    )


def _read_path_bytes(path: str, code: str, label: str) -> bytes:
    """IO helper for exact control-byte hashing and snapshot comparison."""
    try:
        with open(path, "rb") as handle:
            return handle.read()
    except OSError as exc:
        _fail(code, f"cannot read {label} {path}: {exc}")


def _raw_file_digest(path: str) -> str:
    """IO helper: sha256 over the exact bytes of one input document."""
    with open(path, "rb") as handle:
        return _sha256(handle.read())
