"""Provide deterministic data for generic nested-root enrollment tests."""

from __future__ import annotations

from typing import NotRequired, TypedDict, Unpack


class ClearanceRecord(TypedDict):
    """Describe the configured mode of a cleared directory root."""

    mode: str


class ClearanceDocument(TypedDict):
    """Represent source clearance data for a filesystem fixture."""

    schema: int
    cleared: dict[str, ClearanceRecord]


class NestedRootData(TypedDict):
    """Collect raw files, excluded files, clearance, and a later raw file."""

    payloads: dict[str, bytes]
    excluded: dict[str, bytes]
    clearance: ClearanceDocument
    later_path: str
    later_bytes: bytes


class NestedRootOverrides(TypedDict):
    """Permit individual fixture data values to be replaced by a caller."""

    payloads: NotRequired[dict[str, bytes]]
    excluded: NotRequired[dict[str, bytes]]
    clearance: NotRequired[ClearanceDocument]
    later_path: NotRequired[str]
    later_bytes: NotRequired[bytes]


def create(**overrides: Unpack[NestedRootOverrides]) -> NestedRootData:
    """Build independent nested-root data with optional explicit overrides."""
    return {
        "payloads": overrides.get(
            "payloads",
            {
                "resources/one/two/three/payload.bin": b"\x00\xffnested\r\n",
                "resources/one/other.txt": b"another\r\nfile\n",
            },
        ),
        "excluded": overrides.get(
            "excluded",
            {
                "resources/one/two/__pycache__/ignored.txt": b"excluded",
                "resources/one/two/ignored.pyc": b"excluded",
            },
        ),
        "clearance": overrides.get(
            "clearance", {"schema": 1, "cleared": {"resources/": {"mode": "raw"}}}
        ),
        "later_path": overrides.get(
            "later_path", "resources/one/two/three/four/later.bin"
        ),
        "later_bytes": overrides.get("later_bytes", b"later\x00\xff\r\n"),
    }
