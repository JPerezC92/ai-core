# Phase 1 — add the raw binding mode

> **Owner:** Forge 🔨 (Implementer)
> **Goal:** G1
> **Pre:** Plan confirmed; independent audit `[PASS]` recorded in `plan.md`; stash gate clean.
> **Reads:** `plans/core-sync-filetypes-20261006/plan.md`; `.opencode/skills/core-sync/scripts/core_sync.py`; `.opencode/skills/core-sync/scripts/_core_sync_testkit.py`; `.opencode/skills/core-sync/scripts/test_core_sync_*.py`; `.opencode/skills/core-sync/SKILL.md`; `.opencode/agents/bastion.md`; `.opencode/agents/crucible.md`.
> **Writes:** `.opencode/skills/core-sync/scripts/core_sync.py`; `.opencode/skills/core-sync/scripts/test_core_sync.py`; `.opencode/skills/core-sync/scripts/_core_sync_testkit.py`; `.opencode/skills/core-sync/scripts/test_core_sync_markers.py`; `.opencode/skills/core-sync/scripts/test_core_sync_source_core.py`; `.opencode/skills/core-sync/scripts/test_core_sync_source_marker_validation.py`; `.opencode/skills/core-sync/scripts/test_core_sync_check.py`; `.opencode/skills/core-sync/scripts/test_core_sync_check_raw_mode.py`; `.opencode/skills/core-sync/scripts/test_core_sync_check_stale_raw_pending.py`; `.opencode/skills/core-sync/scripts/test_core_sync_apply.py`; `.opencode/skills/core-sync/scripts/test_core_sync_apply_raw_mode.py`; `.opencode/skills/core-sync/scripts/test_core_sync_multi_destination.py`; `.opencode/skills/core-sync/scripts/test_core_sync_init.py`; `.opencode/skills/core-sync/scripts/test_core_sync_init_refresh.py`; `.opencode/skills/core-sync/scripts/test_core_sync_init_raw_mode.py`; `.opencode/skills/core-sync/scripts/test_core_sync_init_malformed_markers.py`; `.opencode/skills/core-sync/scripts/test_core_sync_reconcile_blocker.py`; `.opencode/skills/core-sync/scripts/test_core_sync_blocker_wiring.py`; `.opencode/skills/core-sync/scripts/test_core_sync_binding_validation.py`; `.opencode/skills/core-sync/scripts/test_core_sync_root_binding_validation.py`; `.opencode/skills/core-sync/scripts/test_core_sync_binding_serialization.py`; `.opencode/skills/core-sync/scripts/test_core_sync_root_binding_serialization.py`; `.opencode/skills/core-sync/scripts/test_core_sync_binding_coexistence.py`; `.opencode/skills/core-sync/scripts/test_core_sync_pending_normalization.py`; `.opencode/skills/core-sync/scripts/test_core_sync_root_overlap.py`; `.opencode/skills/core-sync/scripts/test_core_sync_source_write_protection.py`; `.opencode/skills/core-sync/scripts/test_core_sync_destination_write_boundaries.py`; `.opencode/skills/core-sync/scripts/test_core_sync_root_raw_alias.py`; `.opencode/skills/core-sync/SKILL.md`; `user-stories/aicore-adoption-sync.md`

`test_core_sync.py` is in the phase write set because this phase deletes it; the manifest records that action as `Delete`.

> **Writes:** `.opencode/skills/core-sync/scripts/test_core_sync_apply_revision.py`; `.opencode/skills/core-sync/scripts/test_core_sync_apply_invalid_input.py`; `.opencode/skills/core-sync/scripts/test_core_sync_apply_missing_inputs.py`; `.opencode/skills/core-sync/scripts/test_core_sync_check_invalid_input.py`; `.opencode/skills/core-sync/scripts/test_core_sync_check_missing_inputs.py`; `.opencode/skills/core-sync/scripts/test_core_sync_init_pending.py`; `.opencode/skills/core-sync/scripts/test_core_sync_init_idempotence.py`; `.opencode/skills/core-sync/scripts/test_core_sync_init_check_postcondition.py`; `.opencode/skills/core-sync/scripts/test_core_sync_init_invalid_bindings.py`; `.opencode/skills/core-sync/scripts/test_core_sync_init_missing_inputs.py`
> **Writes:** `.opencode/skills/core-sync/scripts/test_core_sync_regions.py`; `.opencode/skills/core-sync/scripts/test_core_sync_blocker_lifecycle.py`
> **Writes:** `.opencode/skills/core-sync/scripts/test_core_sync_check_revision.py`; `.opencode/skills/core-sync/scripts/test_core_sync_check_pending.py`; `.opencode/skills/core-sync/scripts/test_core_sync_check_markerless_source.py`; `.opencode/skills/core-sync/scripts/test_core_sync_check_blocker_wiring.py`; `.opencode/skills/core-sync/scripts/test_core_sync_apply_blocker_wiring.py`; `.opencode/skills/core-sync/scripts/test_core_sync_init_blocker_wiring.py`; `.opencode/skills/core-sync/scripts/test_core_sync_init_fenced_markers.py`
> **Writes:** `.opencode/skills/core-sync/scripts/test_core_sync_root_selection.py`
> **Writes:** `.opencode/skills/core-sync/scripts/test_core_sync_apply_invalid_bindings.py`; `.opencode/skills/core-sync/scripts/test_core_sync_apply_invalid_destination_markers.py`; `.opencode/skills/core-sync/scripts/test_core_sync_check_invalid_bindings.py`; `.opencode/skills/core-sync/scripts/test_core_sync_check_invalid_destination_markers.py`
> **Writes:** `.opencode/skills/core-sync/scripts/test_core_sync_blocker_fenced_code.py`
> **Writes:** `.opencode/skills/core-sync/scripts/test_core_sync_io_errors.py`
> **Writes:** `.opencode/skills/core-sync/scripts/test_core_sync_init_binding_options.py`
> **Writes:** `.opencode/skills/core-sync/scripts/test_core_sync_init_binding_conflicts.py`; `.opencode/skills/core-sync/scripts/test_core_sync_init_binding_validation.py`

## Steps

1. Read `core_sync.py`, the current split `test_core_sync_*.py` modules and `_core_sync_testkit.py`, and `SKILL.md` in full; read `bastion.md`/`crucible.md`.
2. Add an optional `mode` field to each bindings entry (`region` default, `raw`) and idempotent `init --bind SOURCE=DEST` / `--bind-raw SOURCE=DEST` declarations; validate modes/paths and serialize the resulting binding metadata.
3. Keep region mode unchanged; accept a source as markerless only when no exact core markers occur outside matching backtick/tilde fences; a closer must match the opening fence character/length and use at most three leading spaces. Reject malformed source marker sets in `check`/`apply`/`init`, and malformed destination core-marker sets during region-mode `init`.
4. Require canonical safe relative paths and preflight resolved source/destination roots plus every write target (bindings, destination files, blocker, reports, symlinks). Reject path aliases, overlapping roots, a root runtime path that aliases a raw destination, or any target resolving into the source before writes.
5. Raw mode semantics:
   - `read_source_raw(path)`: read raw bytes; do not decode or normalize line endings, and do not parse markers.
   - `check`: compare raw destination bytes directly to source bytes; missing/different → exit 1. Raw destinations create no regions, report, or reconciliation `pending`.
   - `apply`/`init`: byte-preserving writes only; no decoding/re-encoding, line-ending normalization, marker handling, project region, `pending`, or report for raw files.
6. Tests in behavior-specific modules (`*Tests`, `tmp_path`) cover idempotent/conflicting CLI binding declarations, noncanonical path-alias rejection, region init refresh/preservation, malformed bindings and missing source/destination for check/apply/init in region/raw modes, raw copy, LF-only outside-region byte preservation, matching/mismatched fence closers, invalid source/destination markers, overlapping roots, binding paths under source, symlinked destination/root/report targets, destination escapes, root/raw aliases, and concise exit handling for filesystem write failures; assert no source writes on rejection.
7. Update `SKILL.md` with byte-level source read-only and target-preflight guarantees; run the whole suite and fix until green.

## Output

- **Artifact:** updated tool, tests, and skill doc.
- **Schema / shape:** bindings entry `{source, destinations[], mode?}` with `mode ∈ {region, raw}`; region behavior unchanged.

## Verify commands

| Executor | Command |
|---|---|
| Crucible 🔥 (Test Architect) | `uv run --frozen --group dev pytest -q` |
| Bastion 🧱 (Backend & Scripts Architect) | `uv run --frozen python3 -m py_compile .opencode/skills/core-sync/scripts/core_sync.py .opencode/skills/core-sync/scripts/_core_sync_testkit.py .opencode/skills/core-sync/scripts/test_core_sync_*.py` |

- Python `test_*.py` edits: whole-suite command with Crucible 🔥 (Test Architect); Crucible 🔥 (Test Architect) test-architecture `[PASS]` for the current `test_core_sync_*.py` behavior-module set; Bastion 🧱 (Backend & Scripts Architect) `[PASS]` on implementation and source-write preflight.

## Gate

- ✅ `uv run --frozen --group dev pytest -q` → exit 0.
- ✅ Bastion 🧱 (Backend & Scripts Architect) `[PASS]` on `core_sync.py`; Crucible 🔥 (Test Architect) test-architecture `[PASS]` on all 51 current `test_core_sync_*.py` modules.
- ✅ LF-only outside-region byte preservation, raw-byte, malformed-source/destination-marker, source-write-boundary, filesystem-error reporting, script-managed binding declaration, canonical path rejection, and focused command-path cases pass; region mode unchanged.

## Abort conditions

- Halt if a raw change alters region-mode behavior or the exit contract.
- Halt if the suite fails after one correction pass.

## Tool whitelist / blacklist

- Whitelist: edit `core_sync.py`, `SKILL.md`, and the test module set (split into `_core_sync_testkit.py` plus concern-specific behavior modules).
- Blacklist: `AGENTS.md` (phase 2); destination files (phase 3); git mutations.
