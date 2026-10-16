"""E2E: the public `models.py` command contract through real composition."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Callable

# Independent fixture catalogs: fake `opencode models --verbose` stdout payloads.
CATALOG_TWO_PROVIDERS = """zeta/zeta-two
{
  "id": "zeta-two",
  "name": "Zeta Two",
  "cost": { "input": 3.5, "output": 4.25 }
}
alpha/alpha-two
{
  "id": "alpha-two",
  "name": "Alpha Two",
  "cost": { "input": 2, "output": 3 }
}
alpha/alpha-one
{
  "id": "alpha-one",
  "name": "Alpha One",
  "cost": { "input": 1, "output": 0.5 }
}
"""

CATALOG_MIXED = """good/one
{
  "id": "one",
  "name": "Good One",
  "cost": { "input": 1, "output": 2 }
}

bad/json
{"name": "Broken"

good/two
{
  "id": "two",
  "name": "Good Two",
  "cost": { "input": 0.25, "output": 0.75 }
}

bad/array
[1, 2, 3]

good/three
{
  "id": "three",
  "name": "Good Three",
  "cost": { "input": 5, "output": 6 }
}

bad/name
{"name": ["not", "a", "string"], "cost": { "input": 1, "output": 2 }}

bad/cost
{"name": "Bad Cost", "cost": "expensive"}
"""

CATALOG_ALL_INVALID = """bad/json
{"name": "Broken"

bad/array
[1, 2, 3]

bad/name
{"name": ["not", "a", "string"], "cost": { "input": 1, "output": 2 }}
"""

# Independent expected outputs, hand-written from the contract.
RECORD_FIELDS = ["config", "id", "provider", "name", "cost_in", "cost_out"]

EXPECTED_GROUPED_LISTING = (
    "## alpha\n"
    "  alpha/alpha-one | Alpha One | in:1.0 per 1M | out:0.5 per 1M\n"
    "  alpha/alpha-two | Alpha Two | in:2.0 per 1M | out:3.0 per 1M\n"
    "\n"
    "## zeta\n"
    "  zeta/zeta-two | Zeta Two | in:3.5 per 1M | out:4.25 per 1M\n"
    "\n"
)

EXPECTED_ALPHA_TWO = (
    '{"config": "alpha/alpha-two", "id": "alpha-two", "provider": "alpha", '
    '"name": "Alpha Two", "cost_in": 2.0, "cost_out": 3.0}'
)
EXPECTED_ALPHA_ONE = (
    '{"config": "alpha/alpha-one", "id": "alpha-one", "provider": "alpha", '
    '"name": "Alpha One", "cost_in": 1.0, "cost_out": 0.5}'
)
EXPECTED_GOOD_ONE = (
    '{"config": "good/one", "id": "one", "provider": "good", '
    '"name": "Good One", "cost_in": 1.0, "cost_out": 2.0}'
)
EXPECTED_GOOD_TWO = (
    '{"config": "good/two", "id": "two", "provider": "good", '
    '"name": "Good Two", "cost_in": 0.25, "cost_out": 0.75}'
)
EXPECTED_GOOD_THREE = (
    '{"config": "good/three", "id": "three", "provider": "good", '
    '"name": "Good Three", "cost_in": 5.0, "cost_out": 6.0}'
)
EXPECTED_NO_MODELS_STDERR = "No models parsed from `opencode models --verbose` output.\n"
EXPECTED_NO_MATCH_STDERR = (
    "No match for no-such-model in `opencode models`. "
    "Run `<python> .opencode/skills/op-model/scripts/models.py` "
    "to see all available models.\n"
)


def test_no_query_lists_models_grouped_by_provider_and_config(
    run_models: Callable[..., subprocess.CompletedProcess[str]],
) -> None:
    """No-query run groups all models by sorted provider and config, showing both costs per 1M."""
    result = run_models(CATALOG_TWO_PROVIDERS)
    assert result.returncode == 0
    assert result.stdout == EXPECTED_GROUPED_LISTING
    assert result.stderr == ""


def test_query_returns_six_field_json_lines_in_encounter_order(
    run_models: Callable[..., subprocess.CompletedProcess[str]],
) -> None:
    """A nonempty query emits one JSON line per match: six contract fields in order, in encounter order."""
    result = run_models(CATALOG_TWO_PROVIDERS, "alpha")
    assert result.returncode == 0
    assert result.stdout == f"{EXPECTED_ALPHA_TWO}\n{EXPECTED_ALPHA_ONE}\n"
    assert result.stderr == ""
    for line in result.stdout.splitlines():
        assert list(json.loads(line)) == RECORD_FIELDS


def test_mixed_valid_and_malformed_blocks_keep_valid_records(
    run_models: Callable[..., subprocess.CompletedProcess[str]],
) -> None:
    """Malformed, non-object and shape-incompatible blocks are skipped; surrounding valid records survive."""
    result = run_models(CATALOG_MIXED, "good")
    assert result.returncode == 0
    assert result.stdout == (
        f"{EXPECTED_GOOD_ONE}\n{EXPECTED_GOOD_TWO}\n{EXPECTED_GOOD_THREE}\n"
    )
    assert result.stderr == ""


def test_all_invalid_catalog_reports_no_models(
    run_models: Callable[..., subprocess.CompletedProcess[str]],
) -> None:
    """A catalog with only invalid blocks is a truthful nonzero no-models outcome with no stdout."""
    result = run_models(CATALOG_ALL_INVALID)
    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == EXPECTED_NO_MODELS_STDERR


def test_no_match_query_reports_no_match_on_stderr(
    run_models: Callable[..., subprocess.CompletedProcess[str]],
) -> None:
    """A query matching nothing exits 1 with a 'No match for' message on stderr and no stdout."""
    result = run_models(CATALOG_TWO_PROVIDERS, "no-such-model")
    assert result.returncode == 1
    assert result.stdout == ""
    assert "No match for" in result.stderr
    assert result.stderr == EXPECTED_NO_MATCH_STDERR
