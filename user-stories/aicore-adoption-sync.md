# User story — aicore-adoption-sync

> **Created:** 2026-09-11
> **Title:** AICore adoption synchronization
> **Status:** active
> **Epic:** core-governance
> **Affected areas:** `.aicore/`, `.aicore/adopters.yaml`, `.opencode/skills/sync-aicore-adoption/`, `.opencode/skills/migrate-core-to-project/`, `knowledge/`, `README.md`, `AGENTS.md`, `plans/`

## Persona

- A maintainer of a project that adopted AICore and must receive every applicable upstream core change without losing project-owned behavior, and an AICore maintainer who must confirm that no registered adopter is running stale rules.

## Goal

- **G:** AICore and each registered adopter synchronize as one atomic transaction — the complete applicable set at one accepted AICore revision — and AICore can verify every registered adopter against the trusted revision.
  - Done when: every catalog unit is adopted or explicitly `not_applicable` under a machine-checked rule at one lock baseline, `check` exits 0 only when the whole adopter is complete/current/resolved (nonzero otherwise), v1 documents are upgrade-only, and `verify-all` blocks on any registered adopter that is missing, unreachable, stale, or not current.

## Scenario

- A maintainer brings a project under the atomic contract with `migrate-core-to-project`, then runs `sync-aicore-adoption check` on an explicit adopter snapshot. If any applicable unit is stale, drifted, conflicted, or an adapted/replacement/destination_owned unit changed upstream without a review decision, the check exits nonzero and lists the blockers; only a complete, current, reviewed adopter exits 0. The AICore maintainer runs `verify-all`, which checks every repository in `.aicore/adopters.yaml` and fails when any registered adopter is not current.

## Acceptance criteria

- ✅ One machine catalog `.aicore/core-catalog-v2.yaml` defines unit identity, logical members, machine `applicability` (`always`/`requires`/`any_of`), projections (`file`/`tree`/`assertions`), and the deterministic config assertions; both management tools and `verify-all` consume it. Evidence: `.aicore/core-catalog-v2.yaml` (35 units, 2 assertion units); `sync_aicore_adoption.py` `load_catalog`.
- ✅ The lock schema v2 binds the whole adopter to exactly one top-level `accepted_source_commit`; per-unit source commits are rejected; v1 declarations/locks are upgrade-only and fail with `schema_upgrade_required` (exit 2). Evidence: `references/protocol-v2.md` §§4,14; suite `test_lock_row_with_source_commit_is_invalid_lock`, `test_mixed_baseline_lock_is_rejected`, `test_v1_documents_require_upgrade`.
- ✅ `check` enforces the exit contract: 0 only when the declaration is complete, every declared unit is `current`/`not_applicable` (or the non-blocking `unmanaged` `destination_owned` steady state), and all non-mirror changes are reviewed; blocking dispositions exit 1; fatal input exits 2; `--diagnostic-revision` can never exit 0. Evidence: suite `ExitContractTests`, `test_destination_owned_steady_state_is_unmanaged_exit_0`, `test_diagnostic_never_exit_0`.
- ✅ Applicability is machine-checked: every catalog unit is adopted or `not_applicable` under the declared `profile`; a missing applicable unit is `declaration_incomplete` and an `always` unit marked `not_applicable` is `invalid_applicability` (both exit 2). Evidence: suite `DeclarationValidationTests`; `evaluate_applicability`.
- ✅ The two previously excluded config surfaces are deterministic assertions, and the investigator persona profile is a projectable member: a missing required permission gate or ignore entry is blocking drift, and `propose-lock` refuses to bless it. Evidence: catalog v2 `opencode-config`/`gitignore-config`; suite `AssertionTests`; engine `assertion_status_digest`.
- ✅ Changed adapted/replacement/destination_owned units require tracked reconciliation evidence in `.aicore/adoption-review.yaml`, whose raw digest is bound into the lock; a missing decision is `review_changed` (exit 2), and `destination_owned` with changed upstream is `review_required` while the unchanged steady state is the non-blocking `unmanaged`. Evidence: `references/protocol-v2.md` §3; suite `ReviewEvidenceTests` and the `destination_owned` cases.
- ✅ Migration (`migrate-core-to-project` 2.0.0) bootstraps a complete applicable-set enrollment and delegates lock generation and verification to the sync engine; there is no selective or deferred copy. Evidence: `.opencode/skills/migrate-core-to-project/SKILL.md` 2.0.0; no `Select items`/`deferred` language remains.
- ✅ `.aicore/adopters.yaml` is the single AICore surface allowed to name external projects, and `verify-all` blocks on ANY registered adopter that is missing, unreachable, stale, or not current (no `required` exemption). Evidence: `.aicore/adopters.yaml`; suite `VerifyAllTests`, `test_registry_entries_have_no_required_field`.
- ✅ Both commands remain read-only: `check`/`verify-all` write nothing to adopter or upstream Git state, and `propose-lock` writes only to stdout; adopter content is read only from an explicit commit or staged index. Evidence: suite `ReadOnlyTests`, `SnapshotExplicitnessTests`.
- ✅ The v2 suite is stdlib `unittest` with no new dependency or CI workflow, and the engine passes the Python/script architecture gate. Evidence: 35 tests OK; Bastion 🧱 (Backend & Scripts Architect) `[PASS]`; Crucible 🔥 (Test Architect) `[PASS]`; `pyproject.toml`/`uv.lock` unchanged.
- ✅ The two management tools remain upstream-only adopted-content-excluded engines (never catalog units, never copied into an adopter). Evidence: catalog v2 has no management-tool units; `knowledge/aicore-adoption-design.md` §2.

## Change log

- 2026-09-11 - aicore-adoption-sync-20260911: created the durable feature definition for baseline-aware upstream synchronization.
- 2026-09-11 - aicore-adoption-sync-20260911: replaced the insufficient three-way model with declaration/lock separation and accepted upstream plus destination baselines; moved real adopter onboarding to a destination-owned follow-up.
- 2026-09-11 - aicore-adoption-sync-hardening-20260911: reopened the incomplete evidence contract for explicit destination snapshots, replacement drift, selected-unit acceptance, repository identity, and adopter-agnostic management-tool ownership.
- 2026-09-11 - aicore-adoption-sync-hardening-20260911: implemented the hardened v1 contract, the 40-test neutral suite, and the management-tool catalog boundary; all feature acceptance criteria verified.
- 2026-09-11 - aicore-adoption-sync-hardening-20260911: reopened after PR #30 review exposed an unreachable retirement path and a current README catalog-boundary mismatch.
- 2026-09-11 - aicore-adoption-sync-hardening-20260911: implemented explicit selected lock-row retirement (declared∪locked selection), corrected the README catalog boundary, and extended the suite to 43 tests; all feature acceptance criteria verified.
- 2026-09-12 - atomic-adoption-v2-20260912: superseded the incremental v1 contract with the atomic v2 protocol — one accepted revision per adopter, machine applicability, deterministic config assertions, reconciliation evidence, the fail-closed exit contract, the adopter registry, and `verify-all`; v1 is retained only as upgrade input. All v1 incremental-acceptance and no-named-adopter criteria were replaced.

## Resolved decisions

- 2026-09-11 - AICore is the upstream reusable core; adopter repositories keep independent files rather than sharing a physical file.
- 2026-09-11 - adopter intent lives in `.aicore/adoption.yaml`; generated acceptance evidence lives in `.aicore/adoption.lock.yaml`.
- 2026-09-11 - the first capability is read-only; automatic apply/merge behavior is deferred.
- 2026-09-11 - the user resolved the hardening collision by correcting this existing story instead of creating a competing feature story.
- 2026-09-11 - AICore contains only neutral fixtures and management engines; every real declaration, lock, mapping, and historical record is created in its owning adopter after the AICore source release.
- 2026-09-11 - explicit retirement selects a prior locked row omitted from the current declaration and removes only that row from candidate stdout; it does not delete adopter files or introduce a tombstone/schema change.
- 2026-09-12 - Adoption is atomic: one locked AICore revision; per-unit mixed baselines and partial acceptance are forbidden (v1's selected-unit acceptance is superseded).
- 2026-09-12 - Applicability is machine-checked, not judged: units are adopted or `not_applicable` under the declared profile; atomicity applies to the applicable set, so a project is never forced to carry an unrelated team.
- 2026-09-12 - Non-mirror upstream changes require tracked reconciliation evidence; a byte digest alone cannot prove a prose rule was incorporated.
- 2026-09-12 - `.aicore/adopters.yaml` is the single AICore surface allowed to name external projects; `verify-all` blocks on any registered adopter that is not current.
