# User story — aicore-adoption-sync

> **Created:** 2026-09-11
> **Title:** AICore adoption synchronization
> **Status:** active
> **Epic:** core-governance
> **Affected areas:** `.aicore/`, `.opencode/skills/sync-aicore-adoption/`, `.opencode/skills/migrate-core-to-project/`, `knowledge/`, `plans/`

## Persona

- A maintainer of a project that adopted AICore and needs upstream core updates without losing project-owned behavior.

## Goal

- **G:** Compare AICore and an independent adopter through independently verifiable upstream and destination evidence, reporting every update and explicit conflict without writing adopter files or embedding adopter details in AICore.
  - Done when: one upstream catalog, one adopter declaration, and one generated adoption lock let the read-only checker validate source identity and accepted evidence, track complete replacements, preserve unresolved unit baselines, and distinguish upstream changes, local drift, and conflicts deterministically.

## Scenario

- A maintainer has a newer committed AICore revision and an adopter project with accepted local adaptations. They run `check` against an explicit adopter Git snapshot and receive mode, upstream delta, destination delta, and disposition for every unit. When initializing or accepting selected units, `propose-lock` emits a candidate lock to stdout while preserving every unresolved unit baseline for later review.

## Acceptance criteria

- ✅ One versioned machine catalog defines adopted unit/member identity, real content projections, canonical destinations, eligibility, and install strategy and is consumed by both upstream management skills. Evidence: `.aicore/core-catalog-v1.yaml` uses closed `kind`, `install_strategy`, and `sync_projection` values; the superseded human manifest was removed in PR #29.
- ✅ The declaration and lock schemas bind every unit to independently reproducible source identity, accepted upstream evidence, explicit destination snapshot evidence, and closed typed fields; malformed, unknown, or falsified values fail closed. Evidence: `sync_aicore_adoption.py` `verify_lock_evidence`/`require_repository_identity`; `test_falsified_accepted_digests_rejected`, `test_wrong_repository_identity_rejected`; protocol §§1-10; Bastion 🧱 (Backend & Scripts Architect) `[PASS]`.
- ✅ Replacement intent uses neutral named `file|tree` members and the checker reports independent accepted/current destination digests and deltas without claiming byte convergence with the upstream unit. Evidence: `replacement_members` schema in `references/`; `test_replacement_members_dispositions`, `test_missing_replacement_member_rejected`.
- ✅ `check` reports every current catalog change while incremental `propose-lock` updates only explicitly selected units, preserves unselected lock rows, and rejects unselected intent changes. Evidence: `test_selected_unit_lock_advancement_preserves_unselected`, `test_unselected_intent_change_rejected`, `test_changed_catalogs_reconcile_by_id`.
- ✅ Both commands read adopter content only from an explicit committed revision or staged index snapshot, never mutate either repository, and emit reports or candidate YAML only to stdout. Evidence: `--adopter-revision|--adopter-index`; `test_revision_and_index_snapshots_agree`, `test_unstaged_content_excluded_from_index`, `test_commands_write_nothing`.
- ✅ Hermetic neutral fixtures cover falsified evidence, wrong repository identity, explicit revision/index snapshots, replacement member drift and conflict, selected-unit acceptance, unresolved-row preservation, honest catalog-bearing bootstrap, schema rejection, and no filesystem/Git mutation. Evidence: `test_sync_aicore_adoption.py` — `Ran 40 tests ... OK`; Crucible 🔥 (Test Architect) `[PASS]`.
- ✅ The skill uses the existing locked Python environment and stdlib `unittest`; no dependency or CI workflow is added. Evidence: `pyproject.toml`/`uv.lock` unchanged; `uv lock --check` passes; Crucible 🔥 (Test Architect) `[PASS]`; Bastion 🧱 (Backend & Scripts Architect) `[PASS]`; Warden 🔒 (Dependency Warden) `[PASS]`.
- ✅ Migration and synchronization engines remain upstream-only AICore management tools, adopted-content catalog units exclude those engines, and no named-adopter reference or mapping exists in AICore feature surfaces. Evidence: `test_catalog_excludes_management_tools`; catalog documents both as upstream-only; Vault 🔐 (Catalog Steward) `[PASS]`; no real adopter identifier remains in tracked feature surfaces.

## Change log

- 2026-09-11 - aicore-adoption-sync-20260911: created the durable feature definition for baseline-aware upstream synchronization.
- 2026-09-11 - aicore-adoption-sync-20260911: replaced the insufficient three-way model with declaration/lock separation and accepted upstream plus destination baselines; moved real adopter onboarding to a destination-owned follow-up.
- 2026-09-11 - aicore-adoption-sync-hardening-20260911: reopened the incomplete evidence contract for explicit destination snapshots, replacement drift, selected-unit acceptance, repository identity, and adopter-agnostic management-tool ownership.
- 2026-09-11 - aicore-adoption-sync-hardening-20260911: implemented the hardened v1 contract, the 40-test neutral suite, and the management-tool catalog boundary; all feature acceptance criteria verified.

## Resolved decisions

- 2026-09-11 - AICore is the upstream reusable core; adopter repositories keep independent files rather than sharing a physical file.
- 2026-09-11 - adopter intent lives in `.aicore/adoption.yaml`; generated acceptance evidence lives in `.aicore/adoption.lock.yaml`.
- 2026-09-11 - the first capability is read-only; automatic apply/merge behavior is deferred.
- 2026-09-11 - the user resolved the hardening collision by correcting this existing story instead of creating a competing feature story.
- 2026-09-11 - AICore contains only neutral fixtures and management engines; every real declaration, lock, mapping, and historical record is created in its owning adopter after the AICore source release.
