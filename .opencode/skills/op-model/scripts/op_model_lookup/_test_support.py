"""Independent fixture builders for op_model_lookup tests.

Builds raw `opencode models --verbose` stdout blocks and literal Model values
from hand-written field literals. Expected values are never derived by running
production parsing, and importing this module performs no work.
"""

from op_model_lookup.domain.catalog import Model


def raw_block(provider: str, model_id: str, body: str) -> str:
    """Return one raw stdout block: the `provider/model_id` header line plus body."""
    return f"{provider}/{model_id}\n{body}\n"


def raw_stdout(*blocks: str) -> str:
    """Return one raw stdout payload concatenating the given blocks as-is."""
    return "".join(blocks)


def literal_model(
    config: str,
    id: str,
    provider: str,
    name: str,
    cost_in: float,
    cost_out: float,
) -> Model:
    """Return one Model built from the given literal field values, un-parsed."""
    return Model(
        config=config,
        id=id,
        provider=provider,
        name=name,
        cost_in=cost_in,
        cost_out=cost_out,
    )
