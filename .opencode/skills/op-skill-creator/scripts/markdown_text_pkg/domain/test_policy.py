"""Unit tests for schema v1 policy parse, classify, and editor-projection compare."""

from __future__ import annotations

import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from markdown_text_pkg.domain.models import (  # noqa: E402
    CODE_INPUT,
    CODE_POLICY,
    DomainError,
    EditorDriftFinding,
    Policy,
)
from markdown_text_pkg.domain.policy import (  # noqa: E402
    classify_codepoint,
    compare_editor_projection,
    parse_policy,
)

NON_INTEGERS = (True, False, 1.0, "1", None)
NON_STRINGS = (1, True, None, ["x"])
UNKNOWN_CODEPOINT = 65
SURROGATE = 0xD800
OUT_OF_RANGE = 0x110000


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
            },
            {
                "id": "ERR-C0",
                "severity": "error",
                "class": "c0_controls",
                "rationale": "C0",
                "ranges": [
                    {
                        "start": 1,
                        "end": 8,
                        "start_hex": "U+0001",
                        "end_hex": "U+0008",
                    }
                ],
            },
            {
                "id": "WARN-ZWSP",
                "severity": "warning",
                "class": "zero_width_space",
                "rationale": "ZWSP",
                "codepoints": [{"cp": 8203, "hex": "U+200B"}],
            },
        ],
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


def parsed(**overrides: object) -> Policy:
    """Parse a minimum policy, failing the test if the document is invalid."""

    result = parse_policy(create(**overrides))
    assert isinstance(result, Policy)
    return result


def create_settings(**overrides: object) -> dict[str, object]:
    """Return editor settings whose representable projection matches the min policy."""

    settings: dict[str, object] = {
        "[markdown]": {
            "gremlins.characters": {
                "2013": {"level": "none", "description": "en dash"},
            },
            "editor.wordWrap": "on",
        },
        "editor.tabSize": 4,
        "files.eol": "\n",
    }
    settings.update(copy.deepcopy(overrides))
    return settings


class PolicyDocumentParseTests:
    """Valid documents parse; closed schema and scalar types fail closed."""

    def test_minimum_policy_parses(self) -> None:
        policy = parsed()
        assert policy.version == 1
        assert policy.default_classification == "allow"
        assert policy.decoding.encoding == "utf-8"
        assert policy.decoding.invalid_sequence.id == "ERR-UTF8"
        assert len(policy.rules) == 3

    def test_non_object_root_fails(self) -> None:
        result = parse_policy([])
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_unknown_root_field_fails(self) -> None:
        result = parse_policy(create(suppressions=[]))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_missing_rules_fails(self) -> None:
        document = create()
        del document["rules"]
        result = parse_policy(document)
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_unsupported_version_fails(self) -> None:
        result = parse_policy(create(version=2))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_version_rejects_non_integers(self) -> None:
        for value in NON_INTEGERS:
            result = parse_policy(create(version=value))
            assert isinstance(result, DomainError)
            assert result.code == CODE_POLICY

    def test_id_rejects_non_strings(self) -> None:
        for value in NON_STRINGS:
            result = parse_policy(create(id=value))
            assert isinstance(result, DomainError)
            assert result.code == CODE_POLICY

    def test_empty_id_fails(self) -> None:
        result = parse_policy(create(id=""))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_default_classification_must_be_allow(self) -> None:
        result = parse_policy(create(default_classification="deny"))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_encoding_must_be_utf8(self) -> None:
        document = create()
        decoding = document["decoding"]
        assert isinstance(decoding, dict)
        decoding = copy.deepcopy(decoding)
        decoding["encoding"] = "latin-1"
        result = parse_policy(create(decoding=decoding))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_nested_unknown_invalid_sequence_field_fails(self) -> None:
        document = create()
        decoding = copy.deepcopy(document["decoding"])
        assert isinstance(decoding, dict)
        invalid_sequence = decoding["invalid_sequence"]
        assert isinstance(invalid_sequence, dict)
        invalid_sequence["extra"] = True
        result = parse_policy(create(decoding=decoding))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_missing_nested_encoding_fails(self) -> None:
        document = create()
        decoding = copy.deepcopy(document["decoding"])
        assert isinstance(decoding, dict)
        del decoding["encoding"]
        result = parse_policy(create(decoding=decoding))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_invalid_sequence_severity_must_be_error(self) -> None:
        document = create()
        decoding = copy.deepcopy(document["decoding"])
        assert isinstance(decoding, dict)
        invalid_sequence = decoding["invalid_sequence"]
        assert isinstance(invalid_sequence, dict)
        invalid_sequence["severity"] = "warning"
        result = parse_policy(create(decoding=decoding))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY


class PolicyRuleConstraintTests:
    """Rule coverage, hex, uniqueness, and exclusivity constraints."""

    def test_codepoint_bool_is_not_an_integer(self) -> None:
        rules = [
            {
                "id": "ERR-BOOL",
                "severity": "error",
                "class": "nul",
                "rationale": "bool",
                "codepoints": [{"cp": True, "hex": "U+0001"}],
            }
        ]
        result = parse_policy(create(rules=rules))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_codepoint_float_is_rejected(self) -> None:
        rules = [
            {
                "id": "ERR-FLOAT",
                "severity": "error",
                "class": "nul",
                "rationale": "float",
                "codepoints": [{"cp": 1.0, "hex": "U+0001"}],
            }
        ]
        result = parse_policy(create(rules=rules))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_hex_mismatch_fails(self) -> None:
        rules = [
            {
                "id": "ERR-HEX",
                "severity": "error",
                "class": "nul",
                "rationale": "hex",
                "codepoints": [{"cp": 0, "hex": "U+0001"}],
            }
        ]
        result = parse_policy(create(rules=rules))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_lowercase_hex_fails(self) -> None:
        rules = [
            {
                "id": "ERR-HEX-CASE",
                "severity": "error",
                "class": "nul",
                "rationale": "hex",
                "codepoints": [{"cp": 10, "hex": "U+000a"}],
            }
        ]
        result = parse_policy(create(rules=rules))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_surrogate_codepoint_fails(self) -> None:
        rules = [
            {
                "id": "ERR-SUR",
                "severity": "error",
                "class": "sur",
                "rationale": "sur",
                "codepoints": [{"cp": SURROGATE, "hex": "U+D800"}],
            }
        ]
        result = parse_policy(create(rules=rules))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_codepoint_above_max_scalar_fails(self) -> None:
        rules = [
            {
                "id": "ERR-MAX",
                "severity": "error",
                "class": "max",
                "rationale": "max",
                "codepoints": [{"cp": OUT_OF_RANGE, "hex": "U+110000"}],
            }
        ]
        result = parse_policy(create(rules=rules))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_empty_codepoints_fail(self) -> None:
        rules = [
            {
                "id": "ERR-EMPTY",
                "severity": "error",
                "class": "empty",
                "rationale": "empty",
                "codepoints": [],
            }
        ]
        result = parse_policy(create(rules=rules))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_empty_ranges_fail(self) -> None:
        rules = [
            {
                "id": "ERR-EMPTY-R",
                "severity": "error",
                "class": "empty",
                "rationale": "empty",
                "ranges": [],
            }
        ]
        result = parse_policy(create(rules=rules))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_both_codepoints_and_ranges_fail(self) -> None:
        rules = [
            {
                "id": "ERR-BOTH",
                "severity": "error",
                "class": "both",
                "rationale": "both",
                "codepoints": [{"cp": 0, "hex": "U+0000"}],
                "ranges": [
                    {
                        "start": 1,
                        "end": 1,
                        "start_hex": "U+0001",
                        "end_hex": "U+0001",
                    }
                ],
            }
        ]
        result = parse_policy(create(rules=rules))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_neither_codepoints_nor_ranges_fail(self) -> None:
        rules = [
            {
                "id": "ERR-NEITHER",
                "severity": "error",
                "class": "neither",
                "rationale": "neither",
            }
        ]
        result = parse_policy(create(rules=rules))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_range_start_after_end_fails(self) -> None:
        rules = [
            {
                "id": "ERR-ORDER",
                "severity": "error",
                "class": "order",
                "rationale": "order",
                "ranges": [
                    {
                        "start": 8,
                        "end": 1,
                        "start_hex": "U+0008",
                        "end_hex": "U+0001",
                    }
                ],
            }
        ]
        result = parse_policy(create(rules=rules))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_overlapping_ranges_fail(self) -> None:
        rules = [
            {
                "id": "ERR-A",
                "severity": "error",
                "class": "a",
                "rationale": "a",
                "ranges": [
                    {
                        "start": 1,
                        "end": 8,
                        "start_hex": "U+0001",
                        "end_hex": "U+0008",
                    }
                ],
            },
            {
                "id": "ERR-B",
                "severity": "error",
                "class": "b",
                "rationale": "b",
                "ranges": [
                    {
                        "start": 8,
                        "end": 8,
                        "start_hex": "U+0008",
                        "end_hex": "U+0008",
                    }
                ],
            },
        ]
        result = parse_policy(create(rules=rules))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_adjacent_non_overlapping_ranges_parse(self) -> None:
        rules = [
            {
                "id": "ERR-A",
                "severity": "error",
                "class": "a",
                "rationale": "a",
                "ranges": [
                    {
                        "start": 1,
                        "end": 8,
                        "start_hex": "U+0001",
                        "end_hex": "U+0008",
                    }
                ],
            },
            {
                "id": "ERR-B",
                "severity": "error",
                "class": "b",
                "rationale": "b",
                "ranges": [
                    {
                        "start": 9,
                        "end": 9,
                        "start_hex": "U+0009",
                        "end_hex": "U+0009",
                    }
                ],
            },
        ]
        result = parse_policy(create(rules=rules))
        assert isinstance(result, Policy)

    def test_duplicate_rule_ids_fail(self) -> None:
        rules = [
            {
                "id": "ERR-DUP",
                "severity": "error",
                "class": "a",
                "rationale": "a",
                "codepoints": [{"cp": 0, "hex": "U+0000"}],
            },
            {
                "id": "ERR-DUP",
                "severity": "error",
                "class": "b",
                "rationale": "b",
                "codepoints": [{"cp": 1, "hex": "U+0001"}],
            },
        ]
        result = parse_policy(create(rules=rules))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_rule_id_matching_invalid_sequence_fails(self) -> None:
        rules = [
            {
                "id": "ERR-UTF8",
                "severity": "error",
                "class": "dup",
                "rationale": "dup",
                "codepoints": [{"cp": 0, "hex": "U+0000"}],
            }
        ]
        result = parse_policy(create(rules=rules))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_unknown_rule_field_fails(self) -> None:
        rules = [
            {
                "id": "ERR-EXTRA",
                "severity": "error",
                "class": "extra",
                "rationale": "extra",
                "codepoints": [{"cp": 0, "hex": "U+0000"}],
                "note": "no",
            }
        ]
        result = parse_policy(create(rules=rules))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_allow_severity_fails(self) -> None:
        rules = [
            {
                "id": "ALLOW-X",
                "severity": "allow",
                "class": "allow",
                "rationale": "allow",
                "codepoints": [{"cp": 0, "hex": "U+0000"}],
            }
        ]
        result = parse_policy(create(rules=rules))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_duplicate_editor_gremlins_key_fails(self) -> None:
        projection = {
            "scope": "[markdown]",
            "setting_key": "gremlins.characters",
            "overrides": [
                {
                    "codepoint": 8211,
                    "hex": "U+2013",
                    "gremlins_key": "2013",
                    "severity": "none",
                    "description": "en dash",
                },
                {
                    "codepoint": 8211,
                    "hex": "U+2013",
                    "gremlins_key": "2013",
                    "severity": "none",
                    "description": "en dash again",
                },
            ],
        }
        result = parse_policy(create(editor_projection=projection))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_editor_gremlins_key_must_match_codepoint(self) -> None:
        projection = {
            "scope": "[markdown]",
            "setting_key": "gremlins.characters",
            "overrides": [
                {
                    "codepoint": 8211,
                    "hex": "U+2013",
                    "gremlins_key": "2014",
                    "severity": "none",
                    "description": "en dash",
                }
            ],
        }
        result = parse_policy(create(editor_projection=projection))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY

    def test_editor_severity_must_be_none(self) -> None:
        projection = {
            "scope": "[markdown]",
            "setting_key": "gremlins.characters",
            "overrides": [
                {
                    "codepoint": 8211,
                    "hex": "U+2013",
                    "gremlins_key": "2013",
                    "severity": "warning",
                    "description": "en dash",
                }
            ],
        }
        result = parse_policy(create(editor_projection=projection))
        assert isinstance(result, DomainError)
        assert result.code == CODE_POLICY


class PolicyClassifyTests:
    """Default allow plus unique rule coverage."""

    def test_unknown_codepoint_is_allowed(self) -> None:
        assert classify_codepoint(parsed(), UNKNOWN_CODEPOINT) is None

    def test_nul_matches_error_rule(self) -> None:
        rule = classify_codepoint(parsed(), 0)
        assert rule is not None
        assert rule.id == "ERR-NUL"
        assert rule.severity == "error"

    def test_range_member_matches(self) -> None:
        rule = classify_codepoint(parsed(), 8)
        assert rule is not None
        assert rule.id == "ERR-C0"

    def test_tab_is_allowed_when_absent_from_ranges(self) -> None:
        assert classify_codepoint(parsed(), 9) is None

    def test_zwsp_matches_warning_rule(self) -> None:
        rule = classify_codepoint(parsed(), 8203)
        assert rule is not None
        assert rule.id == "WARN-ZWSP"
        assert rule.severity == "warning"

    def test_en_dash_is_not_a_scan_rule(self) -> None:
        assert classify_codepoint(parsed(), 8211) is None


class PolicyEditorProjectionCompareTests:
    """Representable projection compare; unrelated settings are ignored."""

    def test_matching_projection_is_not_drift(self) -> None:
        assert compare_editor_projection(parsed(), create_settings(), "settings.json") is None

    def test_unrelated_settings_are_ignored(self) -> None:
        settings = create_settings()
        assert compare_editor_projection(parsed(), settings, "settings.json") is None
        assert "editor.tabSize" in settings
        markdown = settings["[markdown]"]
        assert isinstance(markdown, dict)
        assert "editor.wordWrap" in markdown

    def test_extra_gremlins_key_is_drift(self) -> None:
        settings = create_settings()
        markdown = settings["[markdown]"]
        assert isinstance(markdown, dict)
        characters = markdown["gremlins.characters"]
        assert isinstance(characters, dict)
        characters["200b"] = {"level": "error", "description": "zwsp"}
        result = compare_editor_projection(parsed(), settings, "s.json")
        assert isinstance(result, EditorDriftFinding)
        assert result.extra == ("200b",)
        assert result.missing == ()
        assert result.mismatched == ()

    def test_missing_gremlins_key_is_drift(self) -> None:
        settings = create_settings()
        markdown = settings["[markdown]"]
        assert isinstance(markdown, dict)
        markdown["gremlins.characters"] = {}
        result = compare_editor_projection(parsed(), settings, "s.json")
        assert isinstance(result, EditorDriftFinding)
        assert result.missing == ("2013",)

    def test_mismatched_level_is_drift(self) -> None:
        settings = create_settings()
        markdown = settings["[markdown]"]
        assert isinstance(markdown, dict)
        characters = markdown["gremlins.characters"]
        assert isinstance(characters, dict)
        characters["2013"] = {"level": "error", "description": "en dash"}
        result = compare_editor_projection(parsed(), settings, "s.json")
        assert isinstance(result, EditorDriftFinding)
        assert result.mismatched == ("2013",)

    def test_mismatched_description_is_drift(self) -> None:
        settings = create_settings()
        markdown = settings["[markdown]"]
        assert isinstance(markdown, dict)
        characters = markdown["gremlins.characters"]
        assert isinstance(characters, dict)
        characters["2013"] = {"level": "none", "description": "other"}
        result = compare_editor_projection(parsed(), settings, "s.json")
        assert isinstance(result, EditorDriftFinding)
        assert result.mismatched == ("2013",)

    def test_missing_scope_lists_all_overrides_missing(self) -> None:
        result = compare_editor_projection(parsed(), {"editor.tabSize": 2}, "s.json")
        assert isinstance(result, EditorDriftFinding)
        assert result.missing == ("2013",)

    def test_non_object_settings_are_input_failure(self) -> None:
        result = compare_editor_projection(parsed(), [], "s.json")
        assert isinstance(result, DomainError)
        assert result.code == CODE_INPUT

    def test_non_object_scope_is_input_failure(self) -> None:
        result = compare_editor_projection(
            parsed(), {"[markdown]": "nope"}, "s.json"
        )
        assert isinstance(result, DomainError)
        assert result.code == CODE_INPUT
