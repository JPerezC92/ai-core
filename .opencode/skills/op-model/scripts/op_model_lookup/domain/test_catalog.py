"""Unit tests for catalog.parse_records mapping, fallbacks, skipping, and recovery."""

import json

import pytest

from op_model_lookup._test_support import literal_model, raw_block, raw_stdout
from op_model_lookup.domain.catalog import (
    CatalogParseResult,
    Model,
    ParseIssue,
    parse_records,
)


def test_valid_block_maps_to_exact_model() -> None:
    stdout = raw_block(
        "openai",
        "gpt-4o",
        '{"id": "gpt-4o", "provider": "openai", "name": "GPT-4o", "cost": {"input": 2.5, "output": 10}}',
    )
    result = parse_records(stdout)
    assert isinstance(result, CatalogParseResult)
    assert result.issues == ()
    assert isinstance(result.models, tuple)
    assert result.models == (
        literal_model(
            config="openai/gpt-4o",
            id="gpt-4o",
            provider="openai",
            name="GPT-4o",
            cost_in=2.5,
            cost_out=10.0,
        ),
    )
    model = result.models[0]
    assert isinstance(model, Model)
    assert isinstance(model.cost_in, float) and model.cost_in == 2.5
    assert isinstance(model.cost_out, float) and model.cost_out == 10.0


def test_missing_name_falls_back_to_header_model_id() -> None:
    result = parse_records(
        raw_block("openai", "gpt-4o", '{"cost": {"input": 2.5, "output": 10}}')
    )
    assert result.issues == ()
    assert result.models == (
        literal_model(
            config="openai/gpt-4o",
            id="gpt-4o",
            provider="openai",
            name="gpt-4o",
            cost_in=2.5,
            cost_out=10.0,
        ),
    )


def test_null_name_falls_back_to_header_model_id() -> None:
    result = parse_records(
        raw_block(
            "openai",
            "gpt-4o",
            '{"name": null, "cost": {"input": 2.5, "output": 10}}',
        )
    )
    assert result.issues == ()
    assert result.models == (
        literal_model(
            config="openai/gpt-4o",
            id="gpt-4o",
            provider="openai",
            name="gpt-4o",
            cost_in=2.5,
            cost_out=10.0,
        ),
    )


def test_empty_name_falls_back_to_header_model_id() -> None:
    result = parse_records(
        raw_block(
            "openai",
            "gpt-4o",
            '{"name": "", "cost": {"input": 2.5, "output": 10}}',
        )
    )
    assert result.issues == ()
    assert result.models == (
        literal_model(
            config="openai/gpt-4o",
            id="gpt-4o",
            provider="openai",
            name="gpt-4o",
            cost_in=2.5,
            cost_out=10.0,
        ),
    )


def test_missing_cost_falls_back_to_zero() -> None:
    result = parse_records(raw_block("openai", "gpt-4o", '{"name": "GPT-4o"}'))
    assert result.issues == ()
    assert result.models == (
        literal_model(
            config="openai/gpt-4o",
            id="gpt-4o",
            provider="openai",
            name="GPT-4o",
            cost_in=0.0,
            cost_out=0.0,
        ),
    )
    model = result.models[0]
    assert isinstance(model.cost_in, float) and model.cost_in == 0.0
    assert isinstance(model.cost_out, float) and model.cost_out == 0.0


def test_null_cost_falls_back_to_zero() -> None:
    result = parse_records(
        raw_block("openai", "gpt-4o", '{"name": "GPT-4o", "cost": null}')
    )
    assert result.issues == ()
    assert result.models == (
        literal_model(
            config="openai/gpt-4o",
            id="gpt-4o",
            provider="openai",
            name="GPT-4o",
            cost_in=0.0,
            cost_out=0.0,
        ),
    )


def test_empty_cost_mapping_falls_back_to_zero() -> None:
    result = parse_records(
        raw_block("openai", "gpt-4o", '{"name": "GPT-4o", "cost": {}}')
    )
    assert result.issues == ()
    assert result.models == (
        literal_model(
            config="openai/gpt-4o",
            id="gpt-4o",
            provider="openai",
            name="GPT-4o",
            cost_in=0.0,
            cost_out=0.0,
        ),
    )


def test_float_compatible_cost_values_convert_to_float() -> None:
    result = parse_records(
        raw_block(
            "openai",
            "gpt-4o-mini",
            '{"name": "GPT-4o mini", "cost": {"input": "1.5", "output": 4}}',
        )
    )
    assert result.issues == ()
    assert result.models == (
        literal_model(
            config="openai/gpt-4o-mini",
            id="gpt-4o-mini",
            provider="openai",
            name="GPT-4o mini",
            cost_in=1.5,
            cost_out=4.0,
        ),
    )
    model = result.models[0]
    assert isinstance(model.cost_in, float) and model.cost_in == 1.5
    assert isinstance(model.cost_out, float) and model.cost_out == 4.0


def test_unknown_cost_values_fall_back_to_zero() -> None:
    result = parse_records(
        raw_block(
            "openai",
            "gpt-4o",
            '{"name": "GPT-4o", "cost": {"input": "unknown", "output": null}}',
        )
    )
    assert result.issues == ()
    assert result.models == (
        literal_model(
            config="openai/gpt-4o",
            id="gpt-4o",
            provider="openai",
            name="GPT-4o",
            cost_in=0.0,
            cost_out=0.0,
        ),
    )


@pytest.mark.parametrize(
    ("cost_field", "expected_in", "expected_out"),
    [
        ("input", 0.0, 7.5),
        ("output", 2.5, 0.0),
    ],
)
def test_overflowing_integer_cost_falls_back_and_preserves_neighbour(
    cost_field: str, expected_in: float, expected_out: float
) -> None:
    huge_integer = 10**400
    stdout = raw_stdout(
        raw_block(
            "openai",
            "huge-cost",
            json.dumps(
                {
                    "name": "Huge cost",
                    "cost": {
                        "input": huge_integer if cost_field == "input" else 2.5,
                        "output": huge_integer if cost_field == "output" else 7.5,
                    },
                }
            ),
        ),
        raw_block(
            "anthropic",
            "claude-3",
            '{"name": "Claude 3", "cost": {"input": 3, "output": 15}}',
        ),
    )
    result = parse_records(stdout)
    assert result.issues == ()
    assert result.models == (
        literal_model(
            config="openai/huge-cost",
            id="huge-cost",
            provider="openai",
            name="Huge cost",
            cost_in=expected_in,
            cost_out=expected_out,
        ),
        literal_model(
            config="anthropic/claude-3",
            id="claude-3",
            provider="anthropic",
            name="Claude 3",
            cost_in=3.0,
            cost_out=15.0,
        ),
    )
    model = result.models[0]
    assert isinstance(model, Model)
    assert isinstance(model.cost_in, float)
    assert isinstance(model.cost_out, float)


def test_malformed_json_block_is_skipped_and_valid_neighbours_survive() -> None:
    stdout = raw_stdout(
        raw_block(
            "openai",
            "gpt-4o",
            '{"name": "GPT-4o", "cost": {"input": 2.5, "output": 10}}',
        ),
        raw_block("openai", "gpt-4o-mini", '{"name": "GPT-4o mini",'),
        raw_block(
            "anthropic",
            "claude-3",
            '{"name": "Claude 3", "cost": {"input": 3, "output": 15}}',
        ),
    )
    result = parse_records(stdout)
    assert result.models == (
        literal_model(
            config="openai/gpt-4o",
            id="gpt-4o",
            provider="openai",
            name="GPT-4o",
            cost_in=2.5,
            cost_out=10.0,
        ),
        literal_model(
            config="anthropic/claude-3",
            id="claude-3",
            provider="anthropic",
            name="Claude 3",
            cost_in=3.0,
            cost_out=15.0,
        ),
    )
    assert result.issues == (
        ParseIssue("malformed_json", "openai/gpt-4o-mini: block body is not valid JSON"),
    )


def test_non_object_bodies_are_skipped_and_valid_neighbours_survive() -> None:
    stdout = raw_stdout(
        raw_block(
            "openai",
            "gpt-4o",
            '{"name": "GPT-4o", "cost": {"input": 2.5, "output": 10}}',
        ),
        raw_block("openai", "list-body", "[1, 2]"),
        raw_block("openai", "null-body", "null"),
        raw_block("openai", "scalar-body", "42"),
        raw_block(
            "anthropic",
            "claude-3",
            '{"name": "Claude 3", "cost": {"input": 3, "output": 15}}',
        ),
    )
    result = parse_records(stdout)
    assert result.models == (
        literal_model(
            config="openai/gpt-4o",
            id="gpt-4o",
            provider="openai",
            name="GPT-4o",
            cost_in=2.5,
            cost_out=10.0,
        ),
        literal_model(
            config="anthropic/claude-3",
            id="claude-3",
            provider="anthropic",
            name="Claude 3",
            cost_in=3.0,
            cost_out=15.0,
        ),
    )
    assert result.issues == (
        ParseIssue(
            "non_object_body", "openai/list-body: block body is not a JSON object"
        ),
        ParseIssue(
            "non_object_body", "openai/null-body: block body is not a JSON object"
        ),
        ParseIssue(
            "non_object_body", "openai/scalar-body: block body is not a JSON object"
        ),
    )


def test_name_zero_is_skipped() -> None:
    result = parse_records(raw_block("openai", "gpt-4o", '{"name": 0}'))
    assert result.models == ()
    assert result.issues == (
        ParseIssue("incompatible_name", "openai/gpt-4o: name is not a string"),
    )


def test_name_false_is_skipped() -> None:
    result = parse_records(raw_block("openai", "gpt-4o", '{"name": false}'))
    assert result.models == ()
    assert result.issues == (
        ParseIssue("incompatible_name", "openai/gpt-4o: name is not a string"),
    )


def test_name_empty_list_is_skipped() -> None:
    result = parse_records(raw_block("openai", "gpt-4o", '{"name": []}'))
    assert result.models == ()
    assert result.issues == (
        ParseIssue("incompatible_name", "openai/gpt-4o: name is not a string"),
    )


def test_name_empty_dict_is_skipped() -> None:
    result = parse_records(raw_block("openai", "gpt-4o", '{"name": {}}'))
    assert result.models == ()
    assert result.issues == (
        ParseIssue("incompatible_name", "openai/gpt-4o: name is not a string"),
    )


def test_cost_zero_is_skipped() -> None:
    result = parse_records(
        raw_block("openai", "gpt-4o", '{"name": "GPT-4o", "cost": 0}')
    )
    assert result.models == ()
    assert result.issues == (
        ParseIssue("incompatible_cost", "openai/gpt-4o: cost is not a mapping"),
    )


def test_cost_false_is_skipped() -> None:
    result = parse_records(
        raw_block("openai", "gpt-4o", '{"name": "GPT-4o", "cost": false}')
    )
    assert result.models == ()
    assert result.issues == (
        ParseIssue("incompatible_cost", "openai/gpt-4o: cost is not a mapping"),
    )


def test_cost_empty_list_is_skipped() -> None:
    result = parse_records(
        raw_block("openai", "gpt-4o", '{"name": "GPT-4o", "cost": []}')
    )
    assert result.models == ()
    assert result.issues == (
        ParseIssue("incompatible_cost", "openai/gpt-4o: cost is not a mapping"),
    )


def test_cost_empty_string_is_skipped() -> None:
    result = parse_records(
        raw_block("openai", "gpt-4o", '{"name": "GPT-4o", "cost": ""}')
    )
    assert result.models == ()
    assert result.issues == (
        ParseIssue("incompatible_cost", "openai/gpt-4o: cost is not a mapping"),
    )


def test_all_invalid_blocks_yield_empty_models_and_all_issues() -> None:
    stdout = raw_stdout(
        raw_block("openai", "broken-json", '{"name": "Broken",'),
        raw_block("openai", "list-body", "[1, 2]"),
        raw_block("openai", "bad-name", '{"name": 0}'),
        raw_block("openai", "bad-cost", '{"name": "GPT-4o", "cost": []}'),
    )
    result = parse_records(stdout)
    assert isinstance(result.models, tuple) and result.models == ()
    assert isinstance(result.issues, tuple)
    assert result.issues == (
        ParseIssue("malformed_json", "openai/broken-json: block body is not valid JSON"),
        ParseIssue(
            "non_object_body", "openai/list-body: block body is not a JSON object"
        ),
        ParseIssue("incompatible_name", "openai/bad-name: name is not a string"),
        ParseIssue("incompatible_cost", "openai/bad-cost: cost is not a mapping"),
    )
    assert all(isinstance(issue, ParseIssue) for issue in result.issues)
