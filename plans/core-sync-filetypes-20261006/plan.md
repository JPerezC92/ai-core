# Plan — core-sync: raw mode + root runtime spec

> **Status:** active
> **Started:** 2026-10-06 23:23
> **Subject:** Add a raw whole-file binding mode for `opencode.jsonc` and bring the root runtime spec (`AGENTS.md` / `CLAUDE.md`) into the region model, keeping AICore-personal content out of the delivered core
> **Layout:** subfolder pattern

## Context

- Prompted by: the user's request to grow `core-sync` by two file types — `opencode.jsonc` (raw whole-file copy, no regions) and the root runtime spec `AGENTS.md` (regions, with AICore's personalized content excluded from delivery). The rule: **AICore-personalized rules are never delivered to a destination.**
- User story: `user-stories/aicore-adoption-sync.md` — Core region synchronization.
- `AGENTS.md` analysis: the `## Project extensions` block (project identity, reuse guide, destination bindings, environment, memory system) is AICore-specific and must not be delivered; the `## Mandatory core` block (lead-orchestration contract, roster, shared rules, conventions, hard rules) is the reusable core.
- Scope now: exactly these two file types; no agent-spec audit.

## Goals

Phase verification checkboxes record phase gates; goal checkboxes remain unchecked until the independent completion audit, per `plan-enforce`.

- ⬜ **G1:** `core-sync` supports per-binding **raw** mode, preserves byte-exact copies, rejects malformed source/destination markers, proves it cannot write into the source tree, and reports write failures without tracebacks.
  - Issue: the tool only understands the region model; `opencode.jsonc` has no regions and must be copied verbatim.
  - How: add an optional `mode` field to bindings (`region` default, `raw`) and script-managed `init --bind SOURCE=DEST` / `--bind-raw SOURCE=DEST` declarations so destination bindings need no hand edit; require canonical safe relative paths so textual aliases cannot claim one resolved destination twice; preserve byte-exact raw reads/writes and outside-marker bytes without newline translation; accept a markerless source only when no exact core markers occur outside matching backtick/tilde fences (with valid ≤3-space closers), and reject malformed source/destination marker sets; preflight resolved roots and all write targets (including symlinks) so no command writes inside the source tree; reject any binding where the root runtime file aliases a raw destination; convert filesystem write failures to a concise exit-1 diagnostic.
  - Files: `.opencode/skills/core-sync/scripts/core_sync.py`, `.opencode/skills/core-sync/scripts/_core_sync_testkit.py`, `.opencode/skills/core-sync/scripts/test_core_sync_*.py`, `.opencode/skills/core-sync/SKILL.md`, `user-stories/aicore-adoption-sync.md`.
  - Done when: raw-mode, script-managed binding declarations/conflicts, canonical-path validation, LF outside-region preservation, valid fence-close parsing, malformed-source/destination-marker, init-refresh, command missing-source/destination, source-read-only, root/raw-alias, and write-error diagnostic tests pass; `uv run --frozen --group dev pytest -q` exits 0; Bastion 🧱 (Backend & Scripts Architect) + Crucible 🔥 (Test Architect) `[PASS]`.
- ⬜ **G2:** AICore's `AGENTS.md` is region-native with AICore-personal content excluded from the core.
  - Issue: `AGENTS.md` uses the old two-section layout and carries AICore-only identity/reuse-guide/environment; the whole file would be delivered as core.
  - How: give `AGENTS.md` one `<!-- core:begin -->`/`<!-- core:end -->` pair around the `## Mandatory core` block and one `<!-- project:begin -->`/`<!-- project:end -->` pair around the `## Project extensions` block, with the core region FIRST (leading the file), then the project region — matching the generated destination layout; drop the retired `> **Rule layout:** two-section-v1` line; replace the obsolete recorded-collision-notice Hard Rule with the region-model verification obligation.
  - Files: `AGENTS.md`, `user-stories/aicore-adoption-sync.md`.
  - Done when: `AGENTS.md` carries exactly one core pair (wrapping the Mandatory-core content) and one project pair (wrapping the Project-extensions content); the flag line is gone; `## Mandatory core` obligations unweakened.
- ⬜ **G3:** The two file types are piloted on tismart-support, command-generated, with no AICore identity delivered.
  - Issue: no destination currently binds `opencode.jsonc` or its root spec.
  - How: run `core-sync init` with `--bind AGENTS.md=CLAUDE.md` and `--bind-raw opencode.jsonc=opencode.jsonc`; the script adds these idempotently to `.aicore/core.yaml` and syncs all bound content/blocker without hand-editing destination files. `init` also refreshes any already-bound source files that have changed. Confirm the destination root's `core` region holds the Mandatory-core bytes, its project region is preserved for destination reconciliation, and no AICore name/reuse-guide is delivered.
  - Files: `/home/dexm76/projects-personal-tismart/tismart-support/.aicore/core.yaml`, `/home/dexm76/projects-personal-tismart/tismart-support/opencode.jsonc`, `/home/dexm76/projects-personal-tismart/tismart-support/CLAUDE.md`, `/home/dexm76/projects-personal-tismart/tismart-support/.aicore/reconciliation/init.yaml`, any already-bound destination files refreshed by the same script run, and `user-stories/aicore-adoption-sync.md`.
  - Done when: `check` exits 0; the destination root contains no AICore identity/reuse-guide; the destination `opencode.jsonc` is byte-identical to AICore's.

## Current state

| Area | Current behavior | Evidence |
|---|---|---|
| Tool | region mode + per-binding raw whole-file copy; source-marker and write-boundary guards are verified | `.opencode/skills/core-sync/scripts/core_sync.py` |
| AICore `AGENTS.md` | reusable Mandatory-core region followed by AICore-owned Project-extensions region | `AGENTS.md` markers |
| Destination root | `CLAUDE.md` (no `AGENTS.md`); not yet bound | tismart-support root |
| Destination `opencode.jsonc` | present, not yet bound; user confirmed raw replacement is intentional | tismart-support |
| Destination bindings `pending` | `[]` at the last read-only inspection; must be rechecked before script execution | tismart-support `.aicore/core.yaml` |

## Behavior change

| Goal | Before | After | Interface contracts | Do-not-break |
|---|---|---|---|---|
| G1 | region-only | raw whole-file copy | bindings `mode: raw`; `check` byte-equality; no `pending` | existing region mode unchanged |
| G2 | two-section layout | core + project regions | across `AGENTS.md` markers | `## Mandatory core` obligations unchanged |
| G3 | root + jsonc unbound | bound and synced | `core-sync init`/`check` exit 0 | destination's own project region preserved |

## Design decisions

- **Two binding modes:** `region` (default) and `raw` (whole-file, no markers). Raw is per binding, not a separate command.
- **AICore-personal content is never delivered:** the source `AGENTS.md` core region holds only the reusable `## Mandatory core` block; the `## Project extensions` block lives in the source's `project` region, which the tool never copies.
- **Raw config replacement is intentional:** the user confirmed the raw sync of AICore's `opencode.jsonc` must replace the destination file byte-for-byte, including its current project-specific settings.
- **Root runtime spec is a normal region file:** `AGENTS.md` has no YAML frontmatter; the core region begins before `## Mandatory core` below the technical framing, and the tool needs no new logic for region mode.
- **Pilot target:** tismart-support; its root is `CLAUDE.md`, bound to AICore `AGENTS.md` as the source. Its `opencode.jsonc` is bound raw.

## Write/delete manifest

| Action | Path |
|---|---|
| Modify | `.opencode/skills/core-sync/scripts/core_sync.py` |
| Delete | `.opencode/skills/core-sync/scripts/test_core_sync.py` |
| Add | `.opencode/skills/core-sync/scripts/_core_sync_testkit.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_markers.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_source_core.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_source_marker_validation.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_check.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_check_raw_mode.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_check_stale_raw_pending.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_apply.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_apply_raw_mode.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_multi_destination.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_init.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_apply_revision.py` |
| Delete | `.opencode/skills/core-sync/scripts/test_core_sync_apply_invalid_input.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_apply_invalid_bindings.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_apply_invalid_destination_markers.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_apply_missing_inputs.py` |
| Delete | `.opencode/skills/core-sync/scripts/test_core_sync_check_invalid_input.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_check_invalid_bindings.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_check_invalid_destination_markers.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_check_missing_inputs.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_init_pending.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_init_idempotence.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_init_check_postcondition.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_init_invalid_bindings.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_init_missing_inputs.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_init_refresh.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_init_raw_mode.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_reconcile_blocker.py` |
| Delete | `.opencode/skills/core-sync/scripts/test_core_sync_blocker_wiring.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_check_revision.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_check_pending.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_check_markerless_source.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_check_blocker_wiring.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_apply_blocker_wiring.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_init_blocker_wiring.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_init_fenced_markers.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_binding_validation.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_root_binding_validation.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_binding_serialization.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_root_binding_serialization.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_binding_coexistence.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_pending_normalization.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_init_malformed_markers.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_root_overlap.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_source_write_protection.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_destination_write_boundaries.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_root_raw_alias.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_root_selection.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_blocker_fenced_code.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_io_errors.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_init_binding_options.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_init_binding_conflicts.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_init_binding_validation.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_regions.py` |
| Add | `.opencode/skills/core-sync/scripts/test_core_sync_blocker_lifecycle.py` |
| Modify | `.opencode/skills/core-sync/SKILL.md` |
| Modify | `AGENTS.md` |
| Modify | `user-stories/aicore-adoption-sync.md` |
| Modify | `/home/dexm76/projects-personal-tismart/tismart-support/.aicore/core.yaml` |
| Modify | `/home/dexm76/projects-personal-tismart/tismart-support/opencode.jsonc` |
| Modify | `/home/dexm76/projects-personal-tismart/tismart-support/CLAUDE.md` |
| Modify | `/home/dexm76/projects-personal-tismart/tismart-support/.aicore/reconciliation/init.yaml` |
| Modify | `/home/dexm76/projects-personal-tismart/tismart-support/.opencode/agents/lumen.md` |
| Modify | `/home/dexm76/projects-personal-tismart/tismart-support/.opencode/skills/git-branch-name/SKILL.md` |
| Modify | `/home/dexm76/projects-personal-tismart/tismart-support/.opencode/skills/git-commit/SKILL.md` |
| Modify | `/home/dexm76/projects-personal-tismart/tismart-support/.opencode/skills/git-pr/SKILL.md` |

## Phase index — dispatch table

| # | Phase | Owner | Runbook | Output | Goals |
|---|---|---|---|---|---|
| 1 | add the raw binding mode | Forge 🔨 (Implementer) | `phase-01-forge.md` | tool + tests + SKILL.md | G1 |
| 2 | regionize AICore `AGENTS.md` | Forge 🔨 (Implementer) | `phase-02-forge.md` | `AGENTS.md` core + project regions | G2 |
| 3 | pilot the two types on tismart-support | Forge 🔨 (Implementer) | `phase-03-forge.md` | bindings + synchronized root and `opencode.jsonc`, refreshing changed existing bindings via script | G3 |

## Critical files / tools

- `.opencode/skills/core-sync/scripts/core_sync.py` — the tool.
- `AGENTS.md` — the root runtime spec (core + project regions).
- `user-stories/aicore-adoption-sync.md` — acceptance evidence for core behavior, source root regions, and the destination pilot.
- tismart-support `.aicore/core.yaml`, `opencode.jsonc`, `CLAUDE.md` — the pilot; `init` also refreshes changed existing bindings.

## Verification

- ✅ Phase 1 (G1): `uv run --frozen --group dev pytest -q` → exit 0; Bastion 🧱 (Backend & Scripts Architect) `[PASS]` on source marker, byte-preserving IO, and write-boundary code; Crucible 🔥 (Test Architect) architecture `[PASS]` on all 51 focused modules.
- ✅ Phase 2 (G2): marker loop exit 0; root source-core extraction excludes AICore-only Project extensions; Sentinel 🛡️ (Quality Guardian) document audit `[PASS]` on the current AICore agent/root/shared-rule snapshot.
- ⬜ Phase 3 (G3): `core-sync check` against the destination → exit 0; destination root has no AICore identity; destination `opencode.jsonc` byte-identical to AICore's.

## Audit

- Auditor: Sentinel 🛡️ (Quality Guardian)
- Verdict: [PASS]
- Findings: 0 (round 11 — re-audited the LF-only G1 fixture correction and final G1/G2 evidence; goal completion and destination verification remain pending)
- Date: 2026-10-07

## Out of scope / Do-not-touch

- Auditing the remaining 15 agent specs / 17 profiles for AICore-specific content (scale-up wave); the already-bound `.opencode/agents/lumen.md` file is refreshed by the phase-3 script run.
- Adding any new binding type beyond raw `opencode.jsonc` and the root runtime spec; changed already-bound paths are refreshed by `init`.
- The destination's non-bound files; `local-version` handling; any git push/PR.

## Resolved decisions

- 2026-10-06 — AICore-personalized rules are never delivered; the core region holds reusable content only.
- 2026-10-06 — Raw mode is per binding (`mode: raw`), whole-file, no regions, no `pending`.
- 2026-10-06 — Scope is exactly `AGENTS.md` + `opencode.jsonc`; the agent-spec audit is deferred.
- 2026-10-06 — Core region FIRST (user correction, applied post-hoc): every region file leads with the `core` region, then the `project` region, matching the generated destination layout. `AGENTS.md` was reordered so `<!-- core:begin -->`…`<!-- core:end -->` precedes `<!-- project:begin -->`…`<!-- project:end -->`.
- 2026-10-07 — The user confirmed raw `opencode.jsonc` synchronization intentionally replaces the destination file byte-for-byte; every mirrored destination file and the reconciliation blocker are written by `core-sync`.
- 2026-10-07 — The user requested a strict subagent dispatch/report contract; `AGENTS.md` carries the exact-scope/output/≤60-line/finish-or-stop dispatch rules, with shared task-matched report discipline in `knowledge/agents.md`.
- 2026-10-07 — Raw mode clears stale pending paths when `apply`/`init` reconcile a region-to-raw binding change; `check` rejects the stale binding state and excludes raw paths from the destination reconciliation blocker.
- 2026-10-07 — Phase verification gates may pass before goal checkboxes; goal checkboxes remain deferred until the independent completion audit per `plan-enforce`.
