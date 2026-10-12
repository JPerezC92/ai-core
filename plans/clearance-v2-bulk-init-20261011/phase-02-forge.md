# Phase 2 — migrate fixtures and prove the v2 contract

> **Owner:** Forge 🔨 (Implementer)
> **Goal:** G1, G2, G3, G4
> **Pre:** Phase 1 code gate `[PASS]`; source/data contract complete; current execution authorization and stash gate retained.
> **Reads:** `plan.md`; phase-01 Output in full; all testkit and affected tests in full; existing missing-input/write-boundary/marker/raw regressions; Crucible's concern-organization rulebook.
> **Writes:** `.opencode/skills/core-sync/scripts/_core_sync_testkit.py`; `.opencode/skills/core-sync/scripts/test_core_sync_clearance.py`; `.opencode/skills/core-sync/scripts/test_core_sync_apply.py`; `.opencode/skills/core-sync/scripts/test_core_sync_root_selection.py`; `.opencode/skills/core-sync/scripts/test_core_sync_root_raw_alias.py`; `.opencode/skills/core-sync/scripts/test_core_sync_init_raw_enrollment.py`; `.opencode/skills/core-sync/scripts/test_core_sync_binding_validation.py`; `.opencode/skills/core-sync/scripts/test_core_sync_binding_serialization.py`; `.opencode/skills/core-sync/scripts/test_core_sync_clearance_metadata.py`; `.opencode/skills/core-sync/scripts/test_core_sync_clearance_mode_gate.py`; `.opencode/skills/core-sync/scripts/test_core_sync_init_bind_cleared.py`; `.opencode/skills/core-sync/scripts/test_core_sync_init_fresh.py`

## Steps

1. Migrate fixture clearance to v2 records with an independent version constant. Text/byte fixture writers declare region/raw explicitly by their API, never by reading destination bindings or markers; preserve deliberately malformed metadata and declared root role. Bindings fixture shape remains independently versioned. Update the byte-written region source in test_core_sync_apply.py with an explicit region declaration.
2. Migrate clearance-gate fixtures/exact assertions, keeping missing/uncleared/malformed no-read/no-write cases. Extend binding validation/serialization for deferred absent modes and explicit mode annotations as assertions, not authority. Replace old tests that require missing parents for a newly registered raw target to fail; retain failures for missing stored targets and invalid/source-aliased paths.
3. Add test_core_sync_clearance_metadata.py for record/schema validation, explicit modes/roles, duplicates, unsafe keys, unknown fields, legacy rejection, and root-role count/raw constraints. Every rejection is a distinct behavior case with no production parser duplicated in tests.
4. Add test_core_sync_clearance_mode_gate.py for both mismatch directions across all commands, omitted binding mode with raw source, conflicting CLI assertions, a later invalid entry blocking earlier writes/reads, and raw marker-like bytes copied without region parsing. Prove no directories, payloads, bindings, reports or blockers appear on validation failure.
5. Add test_core_sync_init_bind_cleared.py for complete mixed-mode registration, source-root routing, source-declared modes, custom/multiple mapping preservation, idempotence, collisions and matching explicit declarations. No cleared record may be silently skipped.
6. Add test_core_sync_init_fresh.py for missing core.yaml, generated metadata/payload parents, new region/raw creation, source-core equality, approved seed metadata, excluded model/permission/tool overrides, one-time local-version initialization, and no writes on bad source inputs. Use existing supported instruction roots; no real repositories or environment resources.
7. Extend root selection and raw-alias tests for all three filename families/cases, explicit YAML/CLI selection, existing-route consistency, deterministic priority, same-name case collision, missing required root, and prospective raw creation shadowing the implicit root. Tests must distinguish actual files from directories and retain source/inode protections.
8. After each test edit return for parent-dispatched Crucible 🔥 (Test Architect) architecture review before the next step; parent also obtains applicable Bastion 🧱 (Backend & Scripts Architect) Python review. Parent dispatches the reviewed whole suite only after fixture migration/reviews finish. Do not add compatibility hacks merely to keep obsolete assertions green.

## Output

- **Artifact:** mode-aware testkit, migrated existing tests and four concern-focused v2 modules.
- **Schema / shape:** independent source-mode fixtures; happy/rejection paths for authority, fresh/full registration and discovery; no real-destination IO.
- **Evidence:** separate test/code architecture verdicts, literal whole-suite command/result, retained regression accounting and discarded obsolete expectation rationale.

## Verify commands

| Executor | Command |
|---|---|
| Crucible 🔥 (Test Architect) | `uv run --frozen --group dev pytest -q` |

## Gate

- ⬜ Metadata/mode/fresh/full/root cases and preserved byte/boundary/reconciliation regressions pass in temporary destinations.
- ⬜ Bastion 🧱 (Backend & Scripts Architect) Python review and Crucible 🔥 (Test Architect) test architecture `[PASS]`; execution exits 0 and is reported separately.
- ⬜ Stale source-schema/string-set fixtures and obsolete new-target restrictions are removed; no test obtains source policy from destination modes.

## Abort conditions

- Stop on any architecture or execution failure; no result is inferred from a prior version's passing suite.
- Stop if another test/implementation path requires changes; report exact evidence and let Cipher 🔓 (Lead Orchestrator) disposition the necessary scope under the user's authorization.
- Stop if a test requires real destination access, package installation, permission modification or an unapproved runner command.
