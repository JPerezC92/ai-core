"""End-to-end behavior test: `init --bind-cleared` seeds a brand-new project.

The destination is a genuinely empty directory, so every enrollment target is
absent — including the merge-mode `opencode.jsonc` that a merge alone cannot
create.

Run: uv run --frozen --group dev pytest \
    .opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_init_seed_new_project.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from _core_sync_testkit import (  # noqa: E402
    AGENT_MARKED,
    REV_A,
    ROOT_MARKED,
    _check_args,
    _qmd_index,
    _write_bytes_file,
    _write_clearance,
    _write_file,
)
from core_sync_pkg.domain.constants import (  # noqa: E402
    MODE_MERGE,
    MODE_RAW,
    MODE_REGION,
    ROLE_ROOT,
)
from core_sync_pkg.domain.jsonc import parse_object  # noqa: E402
from core_sync_pkg.infrastructure.composition import main  # noqa: E402
from core_sync_pkg.infrastructure.stores import (  # noqa: E402
    load_bindings,
    save_bindings,
)

ROOT_SOURCE = "AGENTS.md"
AGENT_SOURCE = ".opencode/agents/atrium.md"
NOTE_SOURCE = ".opencode/skills/foo/note.md"
MERGE_SOURCE = "opencode.jsonc"
NOTE_BYTES = b"note payload\n"
SOURCE_QMD_INDEX = "seed-core"
NEW_PROJECT = "new-project"
SEED_MERGE_SOURCE = (
    "{\n"
    '  "$schema": "https://opencode.ai/config.json",\n'
    '  "instructions": [\n'
    '    "knowledge/agents.md"\n'
    "  ],\n"
    '  "mcp": {\n'
    '    "servers": {\n'
    '      "qmd": {\n'
    '        "type": "local",\n'
    '        "command": [\n'
    '          "npx", "-y", "@tobilu/qmd@2.8.3",\n'
    f'          "--index", "{SOURCE_QMD_INDEX}", "mcp"\n'
    "        ]\n"
    "      }\n"
    "    }\n"
    "  }\n"
    "}\n"
)


def _seed_source(tmp_path: Path) -> Path:
    """Build a cleared source tree: root and agent regions, raw note, merge config."""
    source = tmp_path / "source"
    _write_file(source, ROOT_SOURCE, ROOT_MARKED)
    _write_file(source, AGENT_SOURCE, AGENT_MARKED)
    _write_bytes_file(source, NOTE_SOURCE, NOTE_BYTES)
    _write_bytes_file(
        source, MERGE_SOURCE, SEED_MERGE_SOURCE.encode(), mode=MODE_MERGE
    )
    _write_clearance(
        source,
        {
            ROOT_SOURCE: {"mode": MODE_REGION, "role": ROLE_ROOT},
            AGENT_SOURCE: {"mode": MODE_REGION},
            NOTE_SOURCE: {"mode": MODE_RAW},
            MERGE_SOURCE: {"mode": MODE_MERGE},
        },
    )
    return source


def _seed_args(source: Path, destination: Path, bindings: Path) -> list[str]:
    """Build the seeding `init --bind-cleared` arguments for an empty destination."""
    return [
        "init",
        "--source", str(source),
        "--destination", str(destination),
        "--bindings", str(bindings),
        "--source-revision", REV_A,
        "--bind-cleared",
        "--root", ROOT_SOURCE,
    ]


class SeedEmptyDestinationTests:
    """Seed a brand-new project into an empty destination directory."""

    def test_init_bind_cleared_seeds_every_target_and_checks_current(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        source = _seed_source(tmp_path)
        destination = tmp_path / NEW_PROJECT
        destination.mkdir()
        bindings = tmp_path / "bindings.yaml"

        assert main(_seed_args(source, destination, bindings)) == 0

        assert (destination / ROOT_SOURCE).is_file()
        assert (destination / AGENT_SOURCE).is_file()
        assert (destination / NOTE_SOURCE).read_bytes() == NOTE_BYTES
        merge_path = destination / MERGE_SOURCE
        written = merge_path.read_text(encoding="utf-8")
        assert set(parse_object(written)) == set(parse_object(SEED_MERGE_SOURCE))
        # The created document is what a merge would have produced: the source
        # project's qmd index is retargeted to this project's folder name.
        assert _qmd_index(written) == NEW_PROJECT
        assert json.dumps(SOURCE_QMD_INDEX) not in written

        # A later merge therefore writes nothing: the created file is already
        # merged, which is what keeps a refresh from diverging from a seed.
        created = merge_path.read_bytes()
        assert main(_seed_args(source, destination, bindings)) == 0
        assert merge_path.read_bytes() == created

        # A seeded project is not current until the reconciliation recorded for
        # its created region targets is resolved. The merge config is never
        # pending, because nothing in it is reconcilable project content.
        seeded = load_bindings(bindings)
        assert seeded is not None
        assert seeded["pending"]
        assert MERGE_SOURCE not in seeded["pending"]
        seeded["pending"] = []
        save_bindings(bindings, seeded)

        capsys.readouterr()
        assert main(_check_args(source, destination, bindings, REV_A)) == 0
        assert capsys.readouterr().out == "current\n"
