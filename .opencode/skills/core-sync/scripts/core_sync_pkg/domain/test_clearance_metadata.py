"""Domain unit tests for schema-2 clearance parsing and validation."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json  # noqa: E402

from core_sync_pkg.domain.clearance import (  # noqa: E402
    ClearanceRecord,
    parse_clearance,
)
from core_sync_pkg.domain.errors import (  # noqa: E402
    CODE_INVALID,
    CODE_LEGACY_SCHEMA,
    DomainError,
)


def _doc(cleared: object, schema: int = 2) -> str:
    return json.dumps({"schema": schema, "cleared": cleared})


class ClearanceMetadataTests:
    """Validate schema-2 records: modes, root role, and rejection paths."""

    def test_valid_records_parse_with_modes(self) -> None:
        result = parse_clearance(
            _doc(
                {
                    "AGENTS.md": {"mode": "region", "role": "root"},
                    "opencode.jsonc": {"mode": "raw"},
                }
            )
        )
        assert isinstance(result, dict)
        assert result["AGENTS.md"] == ClearanceRecord(mode="region", role="root")
        assert result["opencode.jsonc"] == ClearanceRecord(mode="raw", role=None)

    def test_missing_mode_is_invalid(self) -> None:
        result = parse_clearance(_doc({"a.md": {"role": "root"}}))
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_root_role_must_be_region(self) -> None:
        result = parse_clearance(_doc({"a.md": {"mode": "raw", "role": "root"}}))
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_multiple_roots_are_invalid(self) -> None:
        result = parse_clearance(
            _doc(
                {
                    "a.md": {"mode": "region", "role": "root"},
                    "b.md": {"mode": "region", "role": "root"},
                }
            )
        )
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_unknown_field_is_invalid(self) -> None:
        result = parse_clearance(_doc({"a.md": {"mode": "region", "extra": 1}}))
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_unsafe_path_is_invalid(self) -> None:
        result = parse_clearance(_doc({"../escape.md": {"mode": "region"}}))
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_legacy_schema_one_is_rejected(self) -> None:
        result = parse_clearance(json.dumps({"schema": 1, "cleared": ["a.md"]}))
        assert isinstance(result, DomainError) and result.code == CODE_LEGACY_SCHEMA

    def test_duplicate_key_is_invalid(self) -> None:
        raw = '{"schema": 2, "cleared": {"a.md": {"mode": "region"}, "a.md": {"mode": "raw"}}}'
        result = parse_clearance(raw)
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_cleared_must_be_object(self) -> None:
        result = parse_clearance(_doc(["a.md"]))
        assert isinstance(result, DomainError) and result.code == CODE_INVALID
