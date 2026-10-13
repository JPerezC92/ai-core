"""Domain unit tests for version-1 clearance document parsing and validation.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/domain/test_clearance_metadata.py
"""

from __future__ import annotations

import sys
from pathlib import Path, PurePosixPath, PureWindowsPath

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json  # noqa: E402
from typing import NotRequired, Sequence, TypedDict  # noqa: E402

from core_sync_pkg.domain.clearance import (  # noqa: E402
    ClearanceEntry,
    ClearanceRecord,
    SkillRootEntry,
    expand_clearance,
    parse_clearance,
)
from core_sync_pkg.domain.constants import (  # noqa: E402
    CLEARANCE_REL,
    CLEARANCE_SCHEMA,
    MODE_MERGE,
    MODE_RAW,
    MODE_REGION,
    ROLE_ROOT,
)
from core_sync_pkg.domain.errors import CODE_INVALID, DomainError  # noqa: E402


class FileRecordShape(TypedDict):
    """Well-formed cleared file record: mode plus an optional root role."""

    mode: str
    role: NotRequired[str]


class RootRecordShape(TypedDict):
    """Well-formed skill-root record: default mode plus an optional subset."""

    mode: str
    region_files: NotRequired[list[object]]


def _file_record(mode: str, role: str | None = None) -> FileRecordShape:
    """Build one well-formed cleared file record."""
    record: FileRecordShape = {"mode": mode}
    if role is not None:
        record["role"] = role
    return record


def _root_record(
    mode: str, region_files: Sequence[object] | None = None
) -> RootRecordShape:
    """Build one skill-root record; members are validated as strings at parse."""
    record: RootRecordShape = {"mode": mode}
    if region_files is not None:
        record["region_files"] = list(region_files)
    return record


def _document(cleared: object, schema: object = CLEARANCE_SCHEMA) -> str:
    """Render a clearance document with the given version label and entries."""
    return json.dumps({"schema": schema, "cleared": cleared})


class ClearanceDocumentTests:
    """Version-1 document gate and cleared file entries: modes and root role."""

    def test_valid_file_records_parse_with_modes(self) -> None:
        result = parse_clearance(
            _document(
                {
                    "AGENTS.md": _file_record("region", role="root"),
                    "opencode.jsonc": _file_record("raw"),
                }
            )
        )
        assert isinstance(result, dict)
        assert result["AGENTS.md"] == ClearanceRecord(mode="region", role="root")
        assert result["opencode.jsonc"] == ClearanceRecord(mode="raw", role=None)

    def test_merge_file_record_parses(self) -> None:
        result = parse_clearance(_document({"opencode.jsonc": _file_record("merge")}))
        assert isinstance(result, dict)
        assert result["opencode.jsonc"] == ClearanceRecord(mode="merge", role=None)

    def test_merge_root_role_is_invalid(self) -> None:
        result = parse_clearance(
            _document({"a.md": _file_record("merge", role="root")})
        )
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_unknown_mode_is_invalid(self) -> None:
        result = parse_clearance(_document({"a.md": {"mode": "bogus"}}))
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_missing_mode_is_invalid(self) -> None:
        result = parse_clearance(_document({"a.md": {"role": "root"}}))
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_root_role_must_be_region(self) -> None:
        result = parse_clearance(_document({"a.md": _file_record("raw", role="root")}))
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_multiple_roots_are_invalid(self) -> None:
        result = parse_clearance(
            _document(
                {
                    "a.md": _file_record("region", role="root"),
                    "b.md": _file_record("region", role="root"),
                }
            )
        )
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_unknown_field_is_invalid(self) -> None:
        result = parse_clearance(_document({"a.md": {"mode": "region", "extra": 1}}))
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_unsafe_path_is_invalid(self) -> None:
        result = parse_clearance(
            _document({"../escape.md": _file_record("region")})
        )
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_duplicate_key_is_invalid(self) -> None:
        raw = (
            f'{{"schema": {CLEARANCE_SCHEMA}, "cleared": '
            '{"a.md": {"mode": "region"}, "a.md": {"mode": "raw"}}}'
        )
        result = parse_clearance(raw)
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_cleared_must_be_object(self) -> None:
        result = parse_clearance(_document(["a.md"]))
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_unsupported_version_label_is_rejected(self) -> None:
        for label in (0, 2, 3, 9):
            result = parse_clearance(
                _document({"a.md": _file_record("region")}, schema=label)
            )
            assert isinstance(result, DomainError), label
            assert result.code == CODE_INVALID, label
            assert "unsupported clearance schema" in result.message, label


class SkillRootEntryTests:
    """Skill-root entries: default mode with an optional region-file subset."""

    def test_root_entry_parses_with_default_mode_and_region_files(self) -> None:
        result = parse_clearance(
            _document(
                {
                    ".opencode/skills/foo/": _root_record(
                        "raw", region_files=["SKILL.md"]
                    )
                }
            )
        )
        assert isinstance(result, dict)
        assert result[".opencode/skills/foo/"] == SkillRootEntry(
            mode="raw", region_files=("SKILL.md",)
        )

    def test_root_entry_without_region_files_parses_empty_subset(self) -> None:
        result = parse_clearance(
            _document({".opencode/skills/foo/": _root_record("raw")})
        )
        assert isinstance(result, dict)
        assert result[".opencode/skills/foo/"] == SkillRootEntry(
            mode="raw", region_files=()
        )

    def test_root_entry_with_empty_region_files_parses(self) -> None:
        result = parse_clearance(
            _document({".opencode/skills/foo/": _root_record("region", region_files=[])})
        )
        assert isinstance(result, dict)
        assert result[".opencode/skills/foo/"] == SkillRootEntry(
            mode="region", region_files=()
        )

    def test_root_entry_without_mode_is_rejected(self) -> None:
        result = parse_clearance(
            _document({"skill/": {"region_files": ["SKILL.md"]}})
        )
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_root_entry_with_unknown_field_is_rejected(self) -> None:
        result = parse_clearance(
            _document(
                {
                    "skill/": {
                        "mode": "raw",
                        "region_files": [],
                        "role": "root",
                    }
                }
            )
        )
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_non_list_region_files_is_rejected(self) -> None:
        result = parse_clearance(
            _document({"skill/": {"mode": "raw", "region_files": "SKILL.md"}})
        )
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_empty_string_region_files_member_is_rejected(self) -> None:
        result = parse_clearance(
            _document({"skill/": _root_record("raw", region_files=[""])})
        )
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_non_string_region_files_member_is_rejected(self) -> None:
        result = parse_clearance(
            _document({"skill/": _root_record("raw", region_files=[7])})
        )
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_region_files_member_with_dot_dot_is_rejected(self) -> None:
        result = parse_clearance(
            _document(
                {"skill/": _root_record("raw", region_files=["../escape.md"])}
            )
        )
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_absolute_region_files_member_is_rejected(self) -> None:
        result = parse_clearance(
            _document({"skill/": _root_record("raw", region_files=["/abs.md"])})
        )
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_region_files_member_not_under_root_is_rejected(self) -> None:
        result = parse_clearance(
            _document(
                {"skill/": _root_record("raw", region_files=["dir//file.md"])}
            )
        )
        assert isinstance(result, DomainError) and result.code == CODE_INVALID

    def test_unsafe_root_key_is_rejected(self) -> None:
        result = parse_clearance(
            _document({"../skill/": _root_record("raw", region_files=[])})
        )
        assert isinstance(result, DomainError) and result.code == CODE_INVALID


def _registry_text() -> str:
    """Load the repo-root distribution-clearance registry document as text."""
    for parent in Path(__file__).resolve().parents:
        candidate = parent / CLEARANCE_REL
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8")
    raise AssertionError(f"{CLEARANCE_REL} not found above {Path(__file__).resolve()}")


def _registry_entries() -> dict[str, ClearanceEntry]:
    """Parse the repo-root registry into version-1 clearance entries."""
    result = parse_clearance(_registry_text())
    assert isinstance(result, dict), result
    return result


def _keep_pairs(pairs: list[tuple[str, object]]) -> list[tuple[str, object]]:
    """Preserve JSON object pairs so repeated keys stay visible as entries."""
    return pairs


def _raw_cleared_keys() -> list[str]:
    """Return the registry's cleared keys in file order, duplicates preserved."""
    document = json.loads(_registry_text(), object_pairs_hook=_keep_pairs)
    for key, value in document:
        if key == "cleared":
            return [name for name, _ in value]
    raise AssertionError("registry document has no 'cleared' member")


def _is_repo_relative(key: str) -> bool:
    """Return True when a registry key is repo-relative: no absolute path or '..'."""
    windows_path = PureWindowsPath(key)
    return (
        not key.startswith("/")
        and not windows_path.drive
        and not windows_path.root
        and ".." not in PurePosixPath(key).parts
    )


def _is_under_root(root: str, member: str) -> bool:
    """Return True when a region-file member is root-relative and stays under root."""
    parts = member.split("/")
    if not parts or "" in parts or "." in parts or ".." in parts:
        return False
    if member.startswith("/") or PureWindowsPath(member).drive:
        return False
    return PurePosixPath(root, member).as_posix().startswith(root)


def _payload_paths() -> list[str]:
    """Synthetic root-relative payload files that must join the expansion."""
    return ["SKILL.md", "scripts/run.py"]


def _enumeration_with_caches() -> list[str]:
    """Synthetic enumeration mixing payload files with interpreter caches."""
    return [
        *_payload_paths(),
        "__pycache__/mod.pyc",
        "pkg/mod.pyc",
        "pkg/__pycache__/mod.py",
    ]


class RegistryDefinitionConformanceTests:
    """The real registry document satisfies the distribution-clearance definition.

    One behavior only: registry entries conform to the format definition the
    sync tool enforces — accepted at version one, unique repo-relative keys,
    skill-root and file rows in their declared shapes, a single root role on
    ``AGENTS.md``, no clearance for the sync tool's own skill, and cache-free
    root expansion. Synthetic inputs come from factories; the registry itself
    is the real repo-root document.
    """

    def test_registry_document_is_accepted_at_version_one(self) -> None:
        result = parse_clearance(_registry_text())
        assert isinstance(result, dict)

    def test_registry_keys_are_unique_and_repo_relative(self) -> None:
        entries = _registry_entries()
        raw_keys = _raw_cleared_keys()
        assert len(raw_keys) == len(set(raw_keys))
        assert list(entries) == raw_keys
        for key in raw_keys:
            assert _is_repo_relative(key), key

    def test_skill_root_rows_match_definition_shape(self) -> None:
        entries = _registry_entries()
        roots = {key: entry for key, entry in entries.items() if key.endswith("/")}
        assert roots
        for key, entry in roots.items():
            assert isinstance(entry, SkillRootEntry), key
            assert entry.mode in (MODE_RAW, MODE_REGION), key
            for member in entry.region_files:
                assert _is_under_root(key, member), (key, member)

    def test_file_rows_use_only_definition_modes(self) -> None:
        entries = _registry_entries()
        files = {key: entry for key, entry in entries.items() if not key.endswith("/")}
        assert files
        for key, entry in files.items():
            assert isinstance(entry, ClearanceRecord), key
            assert entry.mode in (MODE_REGION, MODE_RAW, MODE_MERGE), key

    def test_root_role_is_unique_to_agents_md(self) -> None:
        entries = _registry_entries()
        root_keys = [
            key
            for key, entry in entries.items()
            if isinstance(entry, ClearanceRecord) and entry.role == ROLE_ROOT
        ]
        assert root_keys == ["AGENTS.md"]

    def test_sync_tool_skill_is_never_cleared(self) -> None:
        entries = _registry_entries()
        assert not [key for key in entries if ".opencode/skills/core-sync/" in key]

    def test_root_expansion_drops_interpreter_caches(self) -> None:
        entries = _registry_entries()
        roots = {
            key: entry
            for key, entry in entries.items()
            if isinstance(entry, SkillRootEntry)
        }
        assert roots
        enumerated = {root: _enumeration_with_caches() for root in roots}
        modes = expand_clearance(roots, enumerated)
        assert set(modes) == {
            root + name for root in roots for name in _payload_paths()
        }
