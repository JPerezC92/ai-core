"""Pure model-catalog domain: immutable models, parsing, matching, and the source port."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

BLOCK_HEADER = re.compile(
    r"^([A-Za-z0-9][A-Za-z0-9_+.-]*)/([A-Za-z0-9][A-Za-z0-9_+.-]*)$", re.M
)

CODE_NO_MODELS = "no_models_available"
CODE_NO_MATCH = "no_matching_models"


@dataclass(frozen=True)
class Model:
    """One opencode model entry with its identity and per-1M-token costs."""

    config: str
    id: str
    provider: str
    name: str
    cost_in: float
    cost_out: float

    @classmethod
    def create(
        cls,
        config: str,
        id: str,
        provider: str,
        name: str,
        cost_in: float,
        cost_out: float,
    ) -> Model:
        """Build one immutable model entry from its identity and cost fields."""
        return cls(
            config=config,
            id=id,
            provider=provider,
            name=name,
            cost_in=cost_in,
            cost_out=cost_out,
        )


@dataclass(frozen=True)
class ParseIssue:
    """One skipped catalog block, identified by a stable code and a message."""

    code: str
    message: str


@dataclass(frozen=True)
class CatalogParseResult:
    """The parsed models plus the issues recorded while parsing the catalog."""

    models: tuple[Model, ...]
    issues: tuple[ParseIssue, ...]


@dataclass(frozen=True)
class NoModelsAvailable:
    """Business outcome: the source produced no usable model records."""

    code: str
    message: str

    @classmethod
    def create(cls) -> NoModelsAvailable:
        """Build the no-models outcome with its stable code and message."""
        return cls(
            code=CODE_NO_MODELS,
            message="No models parsed from `opencode models --verbose` output.",
        )


@dataclass(frozen=True)
class NoMatchingModels:
    """Business outcome: the query matched no usable model record."""

    code: str
    message: str
    query: str

    @classmethod
    def create(cls, query: str) -> NoMatchingModels:
        """Build the no-match outcome for `query` with its stable code and message."""
        return cls(
            code=CODE_NO_MATCH,
            message=(
                f"No match for {query} in `opencode models`. "
                "Run `<python> .opencode/skills/op-model/scripts/models.py` "
                "to see all available models."
            ),
            query=query,
        )


class ModelSourceFailure(Exception):
    """A boundary failure raised when the model source transport fails."""


class ModelSource(Protocol):
    """Port for fetching the available models as domain values."""

    def fetch(self) -> tuple[Model, ...]:
        """Return the parsed models, raising ModelSourceFailure on boundary failure."""
        ...


def parse_records(stdout: str) -> CatalogParseResult:
    """Parse `opencode models --verbose` output into models plus per-block issues.

    Blocks whose JSON body is malformed, is not a JSON object, or supplies an
    incompatible name or cost shape are skipped one by one; valid blocks around
    them survive. Missing or empty names fall back to the header model id, and
    missing or empty costs fall back to 0.0.
    """
    models: list[Model] = []
    issues: list[ParseIssue] = []
    for match in BLOCK_HEADER.finditer(stdout):
        provider, model_id = match.group(1), match.group(2)
        config = f"{provider}/{model_id}"
        body = stdout[match.end() :]
        next_header = BLOCK_HEADER.search(body)
        block = body[: next_header.start()] if next_header else body
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            issues.append(
                ParseIssue("malformed_json", f"{config}: block body is not valid JSON")
            )
            continue
        if not isinstance(data, dict):
            issues.append(
                ParseIssue(
                    "non_object_body", f"{config}: block body is not a JSON object"
                )
            )
            continue
        name_value = data.get("name")
        if name_value is not None and not isinstance(name_value, str):
            issues.append(
                ParseIssue("incompatible_name", f"{config}: name is not a string")
            )
            continue
        cost_value = data.get("cost")
        if cost_value is not None and not isinstance(cost_value, Mapping):
            issues.append(
                ParseIssue("incompatible_cost", f"{config}: cost is not a mapping")
            )
            continue
        cost: Mapping[object, object] = (
            cost_value if isinstance(cost_value, Mapping) else {}
        )
        name = name_value if isinstance(name_value, str) and name_value else model_id
        models.append(
            Model.create(
                config=config,
                id=model_id,
                provider=provider,
                name=name,
                cost_in=_to_cost(cost.get("input")),
                cost_out=_to_cost(cost.get("output")),
            )
        )
    return CatalogParseResult(models=tuple(models), issues=tuple(issues))


def _to_cost(value: object) -> float:
    """Convert one cost value to float, using 0.0 when it is not convertible."""
    try:
        return float(value)
    except (TypeError, ValueError, OverflowError):
        return 0.0


def normalize(text: str) -> str:
    """Lowercase `text` and strip every non-alphanumeric character."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def matches(query: str, record: Model) -> bool:
    """Return True when `query` normalizes to a substring of the config or name."""
    needle = normalize(query)
    if not needle:
        return True
    return needle in normalize(record.config) or needle in normalize(record.name)
