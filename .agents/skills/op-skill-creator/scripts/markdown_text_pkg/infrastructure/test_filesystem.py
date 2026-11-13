"""Integration tests for Markdown discovery, policy load, and IO mapping."""

from __future__ import annotations

import copy
import json
import os
import stat
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from markdown_text_pkg.domain.models import (  # noqa: E402
    CODE_INPUT,
    CODE_IO,
    CODE_POLICY,
    DomainError,
    FileTarget,
    Policy,
)
from markdown_text_pkg.infrastructure.filesystem import (  # noqa: E402
    MarkdownFilesystem,
    PolicyLoader,
)

CANONICAL_POLICY = (
    Path(__file__).resolve().parents[6] / "knowledge" / "unicode-policy.json"
)
MARKDOWN_BODY = "ok\n"
NON_MARKDOWN_BODY = "not markdown\n"
DUPLICATE_VERSION_PREFIX = '{"version": 1, "version": 2, '
NONFINITE_CONSTANTS = ("NaN", "Infinity", "-Infinity")
CONTRACT_EXCLUDED_DIRECTORY_NAMES = (
    ".git",
    ".secrets",
    "secrets",
    "output",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
)


def create(**overrides: object) -> dict[str, object]:
    """Return the fixed minimum valid schema v1 policy document."""

    document: dict[str, object] = {
        "version": 1,
        "id": "min-markdown-text",
        "default_classification": "allow",
        "decoding": {
            "encoding": "utf-8",
            "invalid_sequence": {
                "id": "ERR-UTF8",
                "severity": "error",
                "class": "invalid_utf8",
                "rationale": "ill-formed UTF-8",
            },
        },
        "rules": [
            {
                "id": "ERR-NUL",
                "severity": "error",
                "class": "nul",
                "rationale": "NUL",
                "codepoints": [{"cp": 0, "hex": "U+0000"}],
            }
        ],
        "editor_projection": {
            "scope": "[markdown]",
            "setting_key": "gremlins.characters",
            "overrides": [],
        },
    }
    document.update(copy.deepcopy(overrides))
    return document


def _write_md(path: Path) -> Path:
    """Write one Markdown file with the shared body."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(MARKDOWN_BODY, encoding="utf-8")
    return path


def _write_min_policy(path: Path) -> Path:
    """Write the minimum policy JSON to an isolated path."""

    path.write_text(json.dumps(create()), encoding="utf-8")
    return path


def create_nonfinite_root(constant: str) -> str:
    """Return a JSON object whose top-level version is a non-finite constant."""

    return '{"version": ' + constant + "}"


def create_nonfinite_nested(constant: str) -> str:
    """Return a JSON object with a nested non-finite constant."""

    return '{"decoding": {"encoding": ' + constant + "}}"


def _try_symlink(target: Path, link: Path) -> None:
    """Create a symlink or skip when the OS/user cannot."""

    try:
        link.symlink_to(target, target_is_directory=target.is_dir())
    except OSError as exc:
        pytest.skip(f"symlinks unsupported on this OS/user: {exc}")


def _try_make_unreadable(path: Path) -> None:
    """Revoke owner read, or skip when the OS ignores chmod for the owner."""

    os.chmod(path, 0)
    if os.access(path, os.R_OK):
        os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)
        pytest.skip("OS does not revoke owner read via chmod")


class PolicyLoaderTests:
    """PolicyLoader maps bytes and JSON failures without following links."""

    def test_minimum_policy_file_loads(self, tmp_path: Path) -> None:
        policy_path = _write_min_policy(tmp_path / "policy.json")
        result = PolicyLoader().load(str(policy_path))
        assert isinstance(result, Policy)
        assert result.id == "min-markdown-text"

    def test_canonical_policy_loads_via_isolated_copy(self, tmp_path: Path) -> None:
        dest = tmp_path / "unicode-policy.json"
        dest.write_bytes(CANONICAL_POLICY.read_bytes())
        result = PolicyLoader().load(str(dest))
        assert isinstance(result, Policy)
        assert result.version == 1
        assert result.default_classification == "allow"
        assert result.decoding.invalid_sequence.id == "ERR-UTF8"

    def test_duplicate_json_keys_fail(self, tmp_path: Path) -> None:
        body = DUPLICATE_VERSION_PREFIX + json.dumps(create())[len('{"version": 1, ') :]
        path = tmp_path / "dup.json"
        path.write_text(body, encoding="utf-8")
        result = PolicyLoader().load(str(path))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY
        assert "duplicate key" in result.message

    def test_nonfinite_json_constants_fail(self, tmp_path: Path) -> None:
        for constant in NONFINITE_CONSTANTS:
            path = tmp_path / f"root-{constant}.json"
            path.write_text(create_nonfinite_root(constant), encoding="utf-8")
            result = PolicyLoader().load(str(path))
            assert isinstance(result, DomainError)
            assert result.code == CODE_POLICY
            nested = tmp_path / f"nested-{constant}.json"
            nested.write_text(create_nonfinite_nested(constant), encoding="utf-8")
            nested_result = PolicyLoader().load(str(nested))
            assert isinstance(nested_result, DomainError)
            assert nested_result.code == CODE_POLICY

    def test_missing_policy_fails(self, tmp_path: Path) -> None:
        result = PolicyLoader().load(str(tmp_path / "missing.json"))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_symlink_policy_fails(self, tmp_path: Path) -> None:
        real = _write_min_policy(tmp_path / "policy.json")
        link = tmp_path / "link.json"
        _try_symlink(real, link)
        result = PolicyLoader().load(str(link))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY


class MarkdownDiscoveryTests:
    """Explicit roots, suffix, exclusions, dot-directories, and symlink skips."""

    def test_explicit_markdown_file_is_a_target(self, tmp_path: Path) -> None:
        path = _write_md(tmp_path / "note.md")
        result = MarkdownFilesystem().discover((str(path),))
        assert result.failures == ()
        assert len(result.targets) == 1
        assert result.targets[0].display_path.replace("\\", "/").endswith("note.md")

    def test_uppercase_md_suffix_is_accepted(self, tmp_path: Path) -> None:
        path = _write_md(tmp_path / "NOTE.MD")
        result = MarkdownFilesystem().discover((str(path),))
        assert result.failures == ()
        assert len(result.targets) == 1

    def test_explicit_non_markdown_file_fails(self, tmp_path: Path) -> None:
        path = tmp_path / "note.txt"
        path.write_text(NON_MARKDOWN_BODY, encoding="utf-8")
        result = MarkdownFilesystem().discover((str(path),))
        assert result.targets == ()
        assert len(result.failures) == 1
        assert result.failures[0].code == CODE_INPUT

    def test_missing_path_fails(self, tmp_path: Path) -> None:
        result = MarkdownFilesystem().discover((str(tmp_path / "gone.md"),))
        assert result.failures[0].code == CODE_INPUT
        assert "missing path" in result.failures[0].message

    def test_directory_walk_is_deterministic_and_includes_dot_dirs(
        self, tmp_path: Path
    ) -> None:
        _write_md(tmp_path / "b.md")
        _write_md(tmp_path / "a.md")
        _write_md(tmp_path / ".hidden" / "z.md")
        result = MarkdownFilesystem().discover((str(tmp_path),))
        names = [Path(item.display_path).name for item in result.targets]
        assert names == ["z.md", "a.md", "b.md"]
        assert result.failures == ()

    def test_excluded_descendant_directories_are_skipped(self, tmp_path: Path) -> None:
        for name in CONTRACT_EXCLUDED_DIRECTORY_NAMES:
            _write_md(tmp_path / name / "secret.md")
        _write_md(tmp_path / "output.md")
        result = MarkdownFilesystem().discover((str(tmp_path),))
        names = [Path(item.display_path).name for item in result.targets]
        assert names == ["output.md"]

    def test_explicit_excluded_directory_name_is_entered(self, tmp_path: Path) -> None:
        nested = tmp_path / "output"
        _write_md(nested / "kept.md")
        result = MarkdownFilesystem().discover((str(nested),))
        names = [Path(item.display_path).name for item in result.targets]
        assert names == ["kept.md"]

    def test_discovered_symlink_file_is_skipped(self, tmp_path: Path) -> None:
        real = _write_md(tmp_path / "real.md")
        link = tmp_path / "link.md"
        _try_symlink(real, link)
        result = MarkdownFilesystem().discover((str(tmp_path),))
        names = [Path(item.display_path).name for item in result.targets]
        assert names == ["real.md"]

    def test_explicit_symlink_file_fails(self, tmp_path: Path) -> None:
        real = _write_md(tmp_path / "real.md")
        link = tmp_path / "link.md"
        _try_symlink(real, link)
        result = MarkdownFilesystem().discover((str(link),))
        assert result.targets == ()
        assert result.failures[0].code == CODE_INPUT

    def test_explicit_symlink_directory_fails(self, tmp_path: Path) -> None:
        real_dir = tmp_path / "docs"
        _write_md(real_dir / "note.md")
        link = tmp_path / "docs-link"
        _try_symlink(real_dir, link)
        result = MarkdownFilesystem().discover((str(link),))
        assert result.targets == ()
        assert result.failures[0].code == CODE_INPUT

    def test_unreadable_file_maps_to_io_error(self, tmp_path: Path) -> None:
        path = _write_md(tmp_path / "locked.md")
        _try_make_unreadable(path)
        try:
            result = MarkdownFilesystem().read_bytes(
                FileTarget(display_path="locked.md", abs_norm=str(path))
            )
            assert isinstance(result, DomainError)
            assert result.code == CODE_IO
        finally:
            os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)

    def test_duplicate_roots_dedupe_by_abs_norm(self, tmp_path: Path) -> None:
        path = _write_md(tmp_path / "note.md")
        result = MarkdownFilesystem().discover((str(path), str(path)))
        assert len(result.targets) == 1
