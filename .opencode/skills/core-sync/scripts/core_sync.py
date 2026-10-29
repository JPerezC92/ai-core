"""Core update tool with three per-binding modes: `region`, `raw`, and `merge`.

In `region` mode (the default), `check` verifies that each destination file's
`core` region byte-matches the pinned source core; `apply` splices the source
core into each destination between its markers; `init` enrolls markerless
destinations (frontmatter kept verbatim, source core pasted between the core
markers, the previous body moved into a new project region) and refreshes
already-marked destinations. In `raw` mode, the binding has no markers: `init`
and `apply` write the source file to the destination byte-for-byte, and `check`
verifies byte-equality. In `merge` mode, the binding has no markers either:
`init` and `apply` merge the top-level keys of a JSON/JSONC object source into
the destination (source keys win; destination-only keys, comments, and
formatting outside replaced or inserted keys are preserved), and `check`
verifies that every source top-level key is present in the destination with the
source value. Raw and merge destinations carry no project region, no `pending`
entry, and no reconciliation report; a raw target is created only for a newly
registered mapping (via `--bind-raw` or `--bind-cleared`) when its parent
directory exists; a merge target is never created.

The source tree is read-only; the only writes are the destination files, a
reconciliation report, the bindings file, and the destination root runtime
file's reconciliation blocker.

While the bindings `pending` list contains region-mode paths, `check`/`apply`/
`init` keep a marker-delimited blocker block in the destination root runtime file
(the `root` bindings field, else `AGENTS.md` when present, else `CLAUDE.md`)
telling the destination project to reconcile its `project` region and clear
`pending`. `apply` and `init` remove non-region-mode paths (raw or merge) from
persisted `pending`; `check` excludes them from the blocker and rejects stale
non-region entries without changing bindings.

Usage:
    uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py check --source DIR --destination DIR \
        --bindings FILE --source-revision <40-hex>
    uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py apply --source DIR --destination DIR \
        --bindings FILE --source-revision <40-hex>
    uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py init --source DIR --destination DIR \
        --bindings FILE --source-revision <40-hex>

Exit codes:
    0 — current (check), applied (apply), or initialized (init)
    1 — drift (stale revision, region/raw/merge mismatch, missing destination)
    2 — malformed input (bad bindings, invalid markers, malformed JSONC)

This module is the documented entry point and public facade. The layered
implementation lives in `core_sync_pkg` (domain / application / infrastructure
with `infrastructure/composition.main`); the names below are re-exported so existing importers
of `core_sync` keep working unchanged.
"""

from __future__ import annotations

import sys

from core_sync_pkg.infrastructure.composition import main
from core_sync_pkg.domain.bindings import (
    BindingEntry,
    Bindings,
    parse_bindings,
    parse_init_binding_spec,
    serialize_bindings,
)
from core_sync_pkg.domain.constants import (
    BEGIN,
    CLEARANCE_REL,
    END,
    EXIT_INVALID,
    EXIT_OK,
    FENCE_OPEN_RE,
    MODE_REGION,
    PROJECT_BEGIN,
    PROJECT_END,
    RECONCILE_BEGIN,
    RECONCILE_BODY,
    RECONCILE_END,
    SCHEMA_VERSION,
    BindingMode,
)
from core_sync_pkg.domain.errors import MalformedSourceMarkers
from core_sync_pkg.domain.markers import find_markers
from core_sync_pkg.domain.reconciliation import (
    find_reconcile_block,
    reconciliation_report_path,
    sync_reconciliation_blocker,
)
from core_sync_pkg.domain.regions import (
    extract_source_core,
    outside_bytes,
    split_frontmatter,
    split_regions,
)
from core_sync_pkg.infrastructure.filesystem import write_text
from core_sync_pkg.infrastructure.stores import load_bindings, save_bindings

__all__ = [
    "BEGIN",
    "END",
    "PROJECT_BEGIN",
    "PROJECT_END",
    "FENCE_OPEN_RE",
    "SCHEMA_VERSION",
    "CLEARANCE_REL",
    "RECONCILE_BEGIN",
    "RECONCILE_BODY",
    "RECONCILE_END",
    "MODE_REGION",
    "EXIT_OK",
    "EXIT_INVALID",
    "MalformedSourceMarkers",
    "BindingEntry",
    "BindingMode",
    "Bindings",
    "extract_source_core",
    "find_markers",
    "find_reconcile_block",
    "load_bindings",
    "main",
    "outside_bytes",
    "parse_bindings",
    "parse_init_binding_spec",
    "reconciliation_report_path",
    "save_bindings",
    "serialize_bindings",
    "split_frontmatter",
    "split_regions",
    "sync_reconciliation_blocker",
    "write_text",
]


if __name__ == "__main__":
    sys.exit(main())
