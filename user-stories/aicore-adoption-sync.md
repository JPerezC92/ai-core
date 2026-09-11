# User story — aicore-adoption-sync

> **Created:** 2026-09-11
> **Title:** AICore adoption synchronization
> **Status:** active
> **Epic:** core-governance
> **Affected areas:** `.aicore/`, `.opencode/skills/sync-aicore-adoption/`, `.opencode/skills/migrate-core-to-project/`, `knowledge/`, `plans/`

## Persona

- A maintainer of a project that adopted AICore and needs upstream core updates without losing project-owned behavior.

## Goal

- **G:** Compare AICore and an independent adopter repository through accepted upstream and destination baselines, reporting safe updates and explicit conflicts without writing adopter files.
  - Done when: one upstream catalog, one adopter declaration, and one generated adoption lock let the read-only checker distinguish upstream changes, accepted adaptation, later local drift, replacements, and conflicts deterministically.

## Scenario

- A maintainer has a newer committed AICore revision and an adopter project with accepted local adaptations. They run `check` and receive mode, upstream delta, destination delta, and disposition per unit; when initializing or accepting a baseline, `propose-lock` emits a candidate lock to stdout for review and commit in the adopter repository.

## Acceptance criteria

- ✅ One versioned machine catalog defines upstream unit/member identity, real content projections, canonical destinations, eligibility, and install strategy for both adoption skills. Evidence: `.aicore/core-catalog-v1.yaml` (36 units: 10 skills / 17 agents / 6 infra / 3 config; closed `kind`, `install_strategy`, `sync_projection`) is read by `migrate-core-to-project` `1.3.0` and `sync-aicore-adoption`; the superseded `references/core-manifest.md` was removed. Vault 🔐 (Catalog Steward) `[PASS]`.
- ✅ A versioned adopter declaration defines `mirror`, `adapted`, `replacement`, and `destination_owned` intent and destination mappings without storing generated digests. Evidence: `.opencode/skills/sync-aicore-adoption/references/adoption-declaration-v1.yaml` and protocol §2.
- ✅ A generated adoption lock records the full accepted source commit, catalog/declaration digests, and accepted upstream and destination digests per declared unit. Evidence: `references/adoption-lock-v1.yaml` and protocol §3; `propose-lock` emits it to stdout only.
- ✅ The checker reconciles accepted/current catalogs, compares accepted/current upstream and accepted/current destination states, and reports orthogonal declared-or-undeclared mode, delta, and disposition values; mirror baselines with unequal source/destination digests are invalid. Evidence: `sync_aicore_adoption.py`; protocol §§4-7; `test_rejected_mirror_mismatch`, `test_changed_catalogs_reconcile_by_id`, `test_renamed_adapted_root_convergence`.
- ✅ `check` is read-only; `propose-lock` writes only to stdout; unavailable/non-ancestor baselines, malformed mappings, and unsupported projections fail closed. Evidence: `test_commands_write_nothing` (whole-worktree + `git status` equality), `test_unknown_accepted_commit_is_baseline_unavailable`, `test_non_ancestor_accepted_commit_is_baseline_unavailable`, `test_accepted_catalog_digest_binding`, `test_rejected_mappings`.
- ✅ Hermetic temporary-repository tests cover mirror file/tree and invalid mirror baselines, renamed adapted root, split-role replacement, destination-owned catalog and undeclared units, catalog additions/removals, convergence, conflicts, control-path/mapping rejection, line endings, exclusions, a golden digest vector, and pre/post whole-worktree plus Git-state equality. Evidence: `test_sync_aicore_adoption.py` — `Ran 32 tests ... OK`.
- ✅ The skill uses the existing locked Python environment and stdlib `unittest`; no dependency or CI workflow is added. Evidence: `pyproject.toml`/`uv.lock` unchanged; `uv lock --check` passes; Crucible 🔥 (Test Architect) `[PASS]`; Bastion 🧱 (Backend & Scripts Architect) `[PASS]`; Warden 🔒 (Dependency Warden) `[PASS]`.
- ✅ Neutral fixtures prove the shapes required for tismart without committing tismart-specific configuration to AICore. Evidence: `output/audits/aicore-adoption-sync-20260911-compatibility.md` maps each neutral scenario to a tismart shape; no tismart name/path/credential exists under `.aicore/` or the skill.
- ⬜ Tismart Support commits its own `.aicore/adoption.yaml` and `.aicore/adoption.lock.yaml` and completes the first real adoption check after the AICore capability is merged. This destination-owned follow-up is intentionally deferred from the AICore implementation plan.

## Change log

- 2026-09-11 - aicore-adoption-sync-20260911: created the durable feature definition for baseline-aware upstream synchronization.
- 2026-09-11 - aicore-adoption-sync-20260911: replaced the insufficient three-way model with declaration/lock separation and accepted upstream plus destination baselines; moved real tismart onboarding to a destination-owned follow-up.

## Resolved decisions

- 2026-09-11 - AICore is the upstream reusable core; adopter repositories keep independent files rather than sharing a physical file.
- 2026-09-11 - adopter intent lives in `.aicore/adoption.yaml`; generated acceptance evidence lives in `.aicore/adoption.lock.yaml`.
- 2026-09-11 - the first capability is read-only; automatic apply/merge behavior is deferred.
- 2026-09-11 - AICore contains only neutral fixtures; the first real tismart declaration and lock are created in tismart after the AICore source release.
