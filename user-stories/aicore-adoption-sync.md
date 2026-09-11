# User story — aicore-adoption-sync

> **Created:** 2026-09-11
> **Title:** AICore adoption synchronization
> **Status:** active
> **Epic:** core-governance
> **Affected areas:** `.aicore/`, `.opencode/skills/sync-aicore-adoption/`, `.opencode/skills/migrate-core-to-project/`, `knowledge/`, `README.md`, `plans/`

## Persona

- A maintainer of a project that adopted AICore and needs upstream core updates without losing project-owned behavior.

## Goal

- **G:** Compare AICore and an independent adopter through independently verifiable upstream and destination evidence, reporting every update and explicit conflict without writing adopter files or embedding adopter details in AICore.
  - Done when: one upstream catalog, one adopter declaration, and one generated adoption lock let the read-only checker validate source identity and accepted evidence, track complete replacements, preserve unresolved unit baselines, and distinguish upstream changes, local drift, and conflicts deterministically.

## Scenario

- A maintainer has a newer committed AICore revision and an adopter project with accepted local adaptations. They run `check` against an explicit adopter Git snapshot and receive mode, upstream delta, destination delta, and disposition for every unit. When initializing, accepting, or retiring explicitly selected units, `propose-lock` emits a candidate lock to stdout while preserving every unresolved unit baseline for later review.

## Acceptance criteria

- ✅ One versioned machine catalog defines adopted unit/member identity, real content projections, canonical destinations, eligibility, and install strategy and is consumed by both upstream management skills. Evidence: `.aicore/core-catalog-v1.yaml` uses closed `kind`, `install_strategy`, and `sync_projection` values; the superseded human manifest was removed in PR #29.
- ✅ The declaration and lock schemas bind every unit to independently reproducible source identity, accepted upstream evidence, explicit destination snapshot evidence, and closed typed fields; malformed, unknown, or falsified values fail closed. Evidence: `sync_aicore_adoption.py` `verify_lock_evidence`/`require_repository_identity`; `test_falsified_accepted_digests_rejected`, `test_wrong_repository_identity_rejected`; protocol §§1-10; Bastion 🧱 (Backend & Scripts Architect) `[PASS]`.
- ✅ Replacement intent uses neutral named `file|tree` members and the checker reports independent accepted/current destination digests and deltas without claiming byte convergence with the upstream unit. Evidence: `replacement_members` schema in `references/`; `test_replacement_members_dispositions`, `test_missing_replacement_member_rejected`.
- ✅ `check` reports every current catalog change while incremental `propose-lock` advances selected declared units, retires selected prior lock rows omitted from the declaration, preserves every unselected row byte-for-byte, and rejects unknown selections or unselected intent changes. Evidence: `test_selected_retirement_drops_row_preserves_unrelated_and_remains_visible`, `test_selected_retirement_after_upstream_unit_removal`, `test_invalid_retirement_selections_rejected`, `test_unselected_intent_change_rejected`; Bastion 🧱 (Backend & Scripts Architect) `[PASS]`.
- ✅ Both commands read adopter content only from an explicit committed revision or staged index snapshot, never mutate either repository, and emit reports or candidate YAML only to stdout. Evidence: `--adopter-revision|--adopter-index`; `test_revision_and_index_snapshots_agree`, `test_unstaged_content_excluded_from_index`, `test_commands_write_nothing`.
- ✅ Neutral fixtures cover the existing hardened contract plus selected retirement, retirement after upstream removal, invalid retirement selections, unrelated-row preservation, post-retirement visibility, and stdout-only behavior; behavioral fixtures remain temporary, with one repository-catalog boundary test. Evidence: `test_sync_aicore_adoption.py` — `Ran 43 tests ... OK`; Crucible 🔥 (Test Architect) `[PASS]`.
- ✅ The skill uses the existing locked Python environment and stdlib `unittest`; no dependency or CI workflow is added. Evidence: `pyproject.toml`/`uv.lock` unchanged; `uv lock --check` passes; Crucible 🔥 (Test Architect) `[PASS]`; Bastion 🧱 (Backend & Scripts Architect) `[PASS]`; Warden 🔒 (Dependency Warden) `[PASS]`.
- ✅ Migration and synchronization engines remain upstream-only AICore management tools, adopted-content catalog units exclude those engines, no named-adopter reference or mapping exists in AICore feature surfaces, and README truthfully reports 11 discoverable skills, 9 adopted skill units, and 2 excluded management tools. Evidence: `test_catalog_excludes_management_tools`; README literal assertions; Vault 🔐 (Catalog Steward) `[PASS]`.

## Change log

- 2026-09-11 - aicore-adoption-sync-20260911: created the durable feature definition for baseline-aware upstream synchronization.
- 2026-09-11 - aicore-adoption-sync-20260911: replaced the insufficient three-way model with declaration/lock separation and accepted upstream plus destination baselines; moved real adopter onboarding to a destination-owned follow-up.
- 2026-09-11 - aicore-adoption-sync-hardening-20260911: reopened the incomplete evidence contract for explicit destination snapshots, replacement drift, selected-unit acceptance, repository identity, and adopter-agnostic management-tool ownership.
- 2026-09-11 - aicore-adoption-sync-hardening-20260911: implemented the hardened v1 contract, the 40-test neutral suite, and the management-tool catalog boundary; all feature acceptance criteria verified.
- 2026-09-11 - aicore-adoption-sync-hardening-20260911: reopened after PR #30 review exposed an unreachable retirement path and a current README catalog-boundary mismatch.
- 2026-09-11 - aicore-adoption-sync-hardening-20260911: implemented explicit selected lock-row retirement (declared∪locked selection), corrected the README catalog boundary, and extended the suite to 43 tests; all feature acceptance criteria verified.

## Resolved decisions

- 2026-09-11 - AICore is the upstream reusable core; adopter repositories keep independent files rather than sharing a physical file.
- 2026-09-11 - adopter intent lives in `.aicore/adoption.yaml`; generated acceptance evidence lives in `.aicore/adoption.lock.yaml`.
- 2026-09-11 - the first capability is read-only; automatic apply/merge behavior is deferred.
- 2026-09-11 - the user resolved the hardening collision by correcting this existing story instead of creating a competing feature story.
- 2026-09-11 - AICore contains only neutral fixtures and management engines; every real declaration, lock, mapping, and historical record is created in its owning adopter after the AICore source release.
- 2026-09-11 - explicit retirement selects a prior locked row omitted from the current declaration and removes only that row from candidate stdout; it does not delete adopter files or introduce a tombstone/schema change.
