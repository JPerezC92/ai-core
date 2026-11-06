"""End-to-end test for `init --bind-cleared` creating a missing bindings parent.

The fixture mirrors the observed failure: the destination already carries current
marked files but has no `.aicore/` directory, so no reconciliation report is
written and the bindings write is the first `.aicore/` writer.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    AGENT_MARKED,
    CLEARED_AGENT_AND_ROOT,
    REV_A,
    ROOT_MARKED,
    _cleared_source,
)
from core_sync_pkg.domain.reconciliation import (  # noqa: E402
    reconciliation_report_path,
)
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import load_bindings  # noqa: E402

BINDINGS_REL = ".aicore/core.yaml"


def _enrolled_destination(destination: Path) -> None:
    """Seed a destination that is already enrolled and therefore needs no write."""
    for relative, content in (
        ("AGENTS.md", ROOT_MARKED),
        (".opencode/agents/atrium.md", AGENT_MARKED),
    ):
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")


class BindingsParentCreationTests:
    """`init --bind-cleared` creates the bindings parent when it is absent."""

    def test_init_creates_the_missing_bindings_parent(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        source = _cleared_source(tmp_path)
        destination = tmp_path / "destination"
        destination.mkdir()
        _enrolled_destination(destination)
        bindings = destination / BINDINGS_REL
        assert not bindings.parent.exists()

        code = main(
            [
                "init",
                "--source", str(source),
                "--destination", str(destination),
                "--bindings", str(bindings),
                "--source-revision", REV_A,
                "--bind-cleared",
            ]
        )

        captured = capsys.readouterr()
        assert code == 0, captured.err
        assert captured.out == "initialized\n"
        assert captured.err == ""
        # The bindings write is the only `.aicore/` writer here, so its presence
        # proves the parent directory was created by the bindings save.
        assert not reconciliation_report_path(bindings).exists()
        saved = load_bindings(bindings)
        assert saved is not None
        assert {entry["source"] for entry in saved["bindings"]} == set(
            CLEARED_AGENT_AND_ROOT
        )
