# User story — aicore-adoption-sync

> **Created:** 2026-09-11
> **Title:** Core region synchronization
> **Status:** active
> **version:** 1.0.0
> **Epic:** core-governance
> **Affected areas:** `.opencode/agents/`, `.opencode/skills/core-sync/`, `agents/`, `README.md`, `AGENTS.md`

## Persona

- A maintainer on either side of the core/destination boundary: the destination maintainer who must receive every core update without losing project-owned behavior, and the AICore maintainer who ships the core by a deterministic copy-paste only.

## Goal

- **G:** AICore agent files ARE the core. A destination agent file = `frontmatter` + a `<!-- core:begin -->` … `<!-- core:end -->` region (the whole AICore body, byte-identical) + a blank line + a `<!-- project:begin -->` … `<!-- project:end -->` region (the destination's own content). The `core-sync` tool (`init` / `apply` / `check`) is the only writer: it inserts the markers and pastes the core, and never touches the `project` region. The core project never hand-edits destination files; the destination project reconciles its own `project` region, guided by a self-contained blocker the tool writes into the destination root.
  - Done when: `init` generates a markerless destination into core + project regions and sets `pending`; `apply` refreshes the core region; `check` exits 0 only when every core region byte-matches the source and `pending` is empty; the tool writes and clears the destination-root blocker.

## Scenario

- The core maintainer runs `core-sync init` from the AICore checkout against a clean, saved destination. The command generates each bound file (frontmatter + core region + a blank line + a project region holding the destination's existing content), sets `pending`, writes a reconciliation report, and writes a blocker into the destination root. The destination project then reconciles its `project` regions (adopting the permanent "never edit between the core markers" rule, pruning superseded core copies, keeping its own content), clears `pending`, and deletes the blocker; the next `check` reports `current`. Routine core updates run `apply` (refresh the core region) then `check`. The tool never edits the `project` region, and the core never hand-edits destination files.

## Acceptance criteria

- ✅ Region markers are project-agnostic: `<!-- core:begin -->` / `<!-- core:end -->` and `<!-- project:begin -->` / `<!-- project:end -->` (no project name; the tool's constants use exactly these). Evidence: `.opencode/skills/core-sync/scripts/core_sync.py`; `test_core_sync.py`.
- ✅ `core-sync init` generates a markerless destination deterministically (frontmatter + core region = the AICore body + a blank line + project region = the destination's existing body), sets `pending`, and writes the reconciliation report. Evidence: `test_core_sync.py::InitContractTests`.
- ✅ `core-sync apply` refreshes only the core region and proves the outside-marker bytes are unchanged; `check` exits 0 only when every core region byte-matches the source and `pending` is empty (0 current / 1 drift-stale-missing-pending / 2 malformed). Evidence: `test_core_sync.py::ApplyContractTests`, `::CheckContractTests`.
- ✅ The tool writes a self-contained, step-by-step reconciliation blocker into the destination root when `pending` is non-empty and removes it when `pending` clears; the blocker tells the destination to permanently adopt the core-region rule, reconcile, clear `pending`, and delete the blocker. Evidence: `test_core_sync.py::ReconcileBlockerTests`, `::BlockerWiringTests`.
- ✅ A migrated AICore core file (`lumen` spec + profile) is the whole-body core: no markers, no `## Project extensions` / `## Mandatory core` sectioning, no `two-section-v1` flag. Evidence: `.opencode/agents/lumen.md`, `agents/lumen/profile.md`.
- ✅ The migrated destination `lumen` spec/profile are command-generated and reconciled by the destination: one core region byte-identical to AICore's body, one project region holding the destination's own content (`## Tismart Support Context` / `## Tismart Context`), a blank line between the markers, `check` → `current`, destination config validator `ALL PASS`. Evidence: destination baseline `49bb06262cfe64570f97d45254122ffe27c7d43c`; `core-sync check` → `current` (exit 0); `cd /home/dexm76/projects-personal-tismart/tismart-support && python3 scripts/validate_opencode_config.py` → `ALL PASS`.
- ✅ The retired management tools are deleted: `sync-aicore-adoption` and `migrate-core-to-project` skill folders and `knowledge/aicore-adoption-design.md` are absent from the tree. Evidence: `ls .opencode/skills/` and `ls knowledge/` show none of the three paths.

## Change log

- 2026-10-06 — region-core-agent-pilot-20261006: replaced the sectioned catalog/attestation adoption with region-based core updates (`core-sync` `init`/`apply`/`check`, generic markers, a destination-root reconciliation blocker); piloted on `lumen`; deleted the retired management skills and design doc.
- 2026-10-06 — core-sync-rename-20261006: retitled the feature to "Core region synchronization" and repointed the title, evidence, and affected areas to the `core-sync` tool.
- before 2026-10-06 — earlier history: see git history for this file.

## Resolved decisions

- 2026-10-06 — An AICore agent file is the whole-file core (markerless); a destination file is a core region + a project region; the tool is the only writer and never touches the `project` region.
- 2026-10-06 — The core project provides the script and runs the copy-paste; the destination project owns its reconciliation, guided by the tool-written blocker.
- 2026-10-06 — The management skills that enforced catalog/attestation are deleted; the core region is immutable to the destination.
