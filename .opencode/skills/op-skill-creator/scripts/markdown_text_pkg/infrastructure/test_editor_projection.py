"""Integration tests for editor settings JSON IO and representable projection drift."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from markdown_text_pkg.domain.models import (  # noqa: E402
    CODE_INPUT,
    DomainError,
    Policy,
)
from markdown_text_pkg.domain.policy import (  # noqa: E402
    compare_editor_projection,
    parse_policy,
)
from markdown_text_pkg.infrastructure.filesystem import (  # noqa: E402
    MarkdownFilesystem,
    PolicyLoader,
)

CANONICAL_POLICY = (
    Path(__file__).resolve().parents[6] / "knowledge" / "unicode-policy.json"
)
CANONICAL_SETTINGS = (
    Path(__file__).resolve().parents[6] / ".vscode" / "settings.json"
)
UNRELATED_TAB_SIZE = 4


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
        "rules": [],
        "editor_projection": {
            "scope": "[markdown]",
            "setting_key": "gremlins.characters",
            "overrides": [
                {
                    "codepoint": 8211,
                    "hex": "U+2013",
                    "gremlins_key": "2013",
                    "severity": "none",
                    "description": "en dash",
                }
            ],
        },
    }
    document.update(copy.deepcopy(overrides))
    return document


def create_settings(**overrides: object) -> dict[str, object]:
    """Return settings whose representable projection matches the min policy."""

    settings: dict[str, object] = {
        "[markdown]": {
            "gremlins.characters": {
                "2013": {"level": "none", "description": "en dash"},
            }
        },
        "editor.tabSize": UNRELATED_TAB_SIZE,
    }
    settings.update(copy.deepcopy(overrides))
    return settings


def parsed() -> Policy:
    """Parse the minimum policy used by editor-projection cases."""

    result = parse_policy(create())
    assert isinstance(result, Policy)
    return result


def _write_json(path: Path, payload: object) -> Path:
    """Write a JSON document to an isolated path."""

    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


class EditorSettingsLoadTests:
    """load_json_object maps editor files and preserves unrelated keys."""

    def test_unrelated_settings_are_preserved(self, tmp_path: Path) -> None:
        path = _write_json(tmp_path / "settings.json", create_settings())
        loaded = MarkdownFilesystem().load_json_object(str(path))
        assert isinstance(loaded, dict)
        assert loaded["editor.tabSize"] == UNRELATED_TAB_SIZE
        result = compare_editor_projection(parsed(), loaded, str(path))
        assert result is None

    def test_invalid_json_fails(self, tmp_path: Path) -> None:
        path = tmp_path / "settings.json"
        path.write_text("{", encoding="utf-8")
        result = MarkdownFilesystem().load_json_object(str(path))
        assert isinstance(result, DomainError)
        assert result.code == CODE_INPUT

    def test_duplicate_keys_fail(self, tmp_path: Path) -> None:
        path = tmp_path / "settings.json"
        path.write_text(
            '{"editor.tabSize": 2, "editor.tabSize": 4}', encoding="utf-8"
        )
        result = MarkdownFilesystem().load_json_object(str(path))
        assert isinstance(result, DomainError)
        assert result.code == CODE_INPUT
        assert "duplicate key" in result.message

    def test_missing_editor_file_fails(self, tmp_path: Path) -> None:
        result = MarkdownFilesystem().load_json_object(str(tmp_path / "gone.json"))
        assert isinstance(result, DomainError)
        assert result.code == CODE_INPUT

    def test_symlink_editor_file_fails(self, tmp_path: Path) -> None:
        real = _write_json(tmp_path / "settings.json", create_settings())
        link = tmp_path / "link.json"
        try:
            link.symlink_to(real)
        except OSError as exc:
            pytest.skip(f"symlinks unsupported on this OS/user: {exc}")
        result = MarkdownFilesystem().load_json_object(str(link))
        assert isinstance(result, DomainError)
        assert result.code == CODE_INPUT


class EditorProjectionDriftTests:
    """Canonical editor settings match the isolated canonical policy copy."""

    def test_canonical_settings_match_canonical_policy(self, tmp_path: Path) -> None:
        policy_path = tmp_path / "unicode-policy.json"
        settings_path = tmp_path / "settings.json"
        policy_path.write_bytes(CANONICAL_POLICY.read_bytes())
        settings_path.write_bytes(CANONICAL_SETTINGS.read_bytes())
        policy = PolicyLoader().load(str(policy_path))
        loaded = MarkdownFilesystem().load_json_object(str(settings_path))
        assert isinstance(policy, Policy)
        assert isinstance(loaded, dict)
        assert compare_editor_projection(policy, loaded, str(settings_path)) is None
