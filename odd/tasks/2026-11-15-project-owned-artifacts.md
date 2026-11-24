# Project-owned artifact architecture

> **Status:** closed
> **Closed:** 2026-11-24
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-15
> **Objective:** Preserve project-owned records while separating them from managed infrastructure.
> **Branch:** `refactor/architecture/project-owned-artifacts`
> **Delivery:** Forecast over 400 authored changed lines; coherent reviewable slices, with migration, diagnostics and synchronization checks separated by risk and dependencies. Measured authored change: 893 additions and 78 deletions across 61 paths, excluding pure renames.
> **Runner:** `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks`; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts odd/features`; `pnpm --dir cli/aicore test`; incident-workflow skill suite; `pnpm --dir cli/aicore typecheck`.

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — Existing non-template ODD records are inventoried before relocation. Exact requirement: "Complete a file-by-file inventory before moving anything." Acceptance: compare the inventory with both existing ODD directories and observe every non-template record represented.
- S2 — Existing ODD records move without loss. Exact requirement: "Preserve all existing task and feature records." Acceptance: compare the inventoried records with their destination files and observe all required records and preservation evidence retained.
- S3 — Managed templates stay in place while project records use the new locations. Exact requirement: "Keep the distributed `_template.md` files in their existing managed locations." Acceptance: inspect the managed template paths and the record destinations and observe one authoritative record location.
- S4 — Incident cases use the requested root. Exact requirement: "`incidents/`: actual project-owned incident investigations and evidence." Acceptance: follow the incident folder convention and observe the requested root with the existing ticket lifecycle preserved.
- S5 — Project-owned diagnostic learning supports distinct identifiers. Exact requirement: "Shared baseline: `S-01`, `S-02`, etc." and "Destination-owned: `LOCAL:S-01`, `LOCAL:S-02`, etc." Acceptance: validate distinct baseline and local symptom references and observe both recognized without ambiguity.
- S6 — Invalid diagnostic knowledge fails safely. Exact requirement: "Missing or invalid required registers must not silently become `no_match`." Acceptance: validate a missing or invalid required register and observe a failure instead of a diagnostic verdict.
- S7 — Initialization preserves existing project records. Exact requirement: "Never overwrite existing project-owned files." Acceptance: initialize against an existing register and observe its content unchanged.
- S8 — Synchronization preserves project-owned artifacts. Exact requirement: "Regular AICore synchronization must not create, overwrite, or delete project-owned diagnostic records." Acceptance: run synchronization against an isolated synthetic fixture and observe project-owned records unchanged.
- S9 — The root navigation explains the architecture. Exact requirement: "Update the existing root `README.md` to explain and navigate the new architecture." Acceptance: read the root README and find the managed and project-owned locations.
- S10 — Existing application layouts remain flexible. Exact requirement: "Keep existing AICore application and tool sources such as `cli/` and `mcp-servers/` unchanged unless a demonstrated implementation dependency requires a narrow adjustment." Acceptance: inspect the delivered source locations and observe the existing application directories preserved.

## Tasks

- T1 | S1 | inline (coordinator-owned preservation inventory) — Cipher 🔓 (Lead Orchestrator) | done | commit: 6e6d19b
- T2 | S2, S3, S9 | delegated (record relocation and live contract updates) — Forge 🔨 (Implementer) | done | commit: b233484af917ceb8220dc67143ef5bef6945b97d
- T3 | S4, S5, S6, S7 | delegated (incident and diagnostic behavior) — Forge 🔨 (Implementer) | done | commit: 5346998
- T4 | S8, S10 | delegated (isolated synchronization verification) — Forge 🔨 (Implementer) | done | commit: 5346998
- T5 | S1, S2, S3, S4, S5, S6, S7, S8, S9, S10 | delegated (independent integrated acceptance) — Sentinel 🛡️ (Quality Guardian) | done | commit: 6e6d19b

## Log

- L1 — Original request, verbatim:

  # AICore — Implement the New Project-Owned Artifact Architecture

  ## Objective

  Implement the approved architectural direction in the **existing AICore source repository**, based on the previous read-only investigations and revised migration plan.

  This is an implementation request, not another broad architectural investigation.

  The goal is to separate **AICore-managed resources** from **project-owned development records, incident artifacts, and accumulated diagnostic knowledge**, while preserving existing workflows, validation, synchronization behavior, and historical records.

  **Important clarification about the current repository:**
  - AICore already contains real ODD development tasks and feature records. These must be migrated.
  - AICore currently has no application projects requiring relocation into a new `apps/` or `development/` directory.
  - AICore currently has no actual incident investigation records requiring migration.
  - Existing infrastructure such as `cli/` and `mcp-servers/` must remain in place.
  - Do not fabricate incident records, applications, diagnostic findings, or example data to populate the new structure.
  - Empty directories or local registers should only be created when required by an actual, authorized workflow.

  ## 1. Target architecture

  The intended logical structure is:

  ```text
  ai-core/
  ├── .aicore/
  │   └── core/
  │       ├── architecture/
  │       ├── knowledge/
  │       │   └── diagnostics/
  │       │       ├── symptoms.md
  │       │       ├── problems.md
  │       │       └── diagnostic-guidance.md
  │       └── odd/
  │           ├── features/_template.md
  │           └── tasks/_template.md
  │
  ├── odd/
  │   ├── features/
  │   └── tasks/
  │
  ├── incidents/
  │   ├── diagnostics/
  │   │   ├── symptoms.md
  │   │   └── problems.md
  │   └── <DATE> #ID/
  │       └── ticket_<id>.md
  │
  ├── .agents/
  ├── .opencode/
  ├── cli/
  ├── mcp-servers/
  └── docs/
  ```

  This is a **logical target**, not an instruction to create every illustrated directory or placeholder file.

  Preserve all other legitimate existing repository files and directories.

  ### Ownership rules
  - `.aicore/core/`: AICore-managed templates, methodology, shared definitions, and architecture contracts.
  - `odd/`: actual project-owned ODD tasks and features.
  - `incidents/`: actual project-owned incident investigations and evidence.
  - `incidents/diagnostics/`: project-owned symptoms and problem patterns.
  - Application source directories: determined by the application/project architecture, not imposed by AICore.
  - `docs/`: project technical documentation, not a substitute for ODD records.

  Development and Incident agents may consume shared knowledge regardless of which workflow produced it.

  ## 2. Migrate existing ODD records

  This is mandatory.

  Move actual non-template records from:
  - `.aicore/core/odd/tasks/` → `odd/tasks/`
  - `.aicore/core/odd/features/` → `odd/features/`

  Keep the distributed `_template.md` files in their existing managed locations.

  ### Requirements
  1. Complete a file-by-file inventory before moving anything.
  2. Preserve all existing task and feature records.
  3. Preserve statuses, requirement checkboxes, evidence, references, and lifecycle semantics.
  4. Update active authoritative references to the new root-level locations.
  5. Update the ODD workflow, associated skills, AGENTS.md, relevant agents, templates, validators' invocations, and Sentinel's audit scope.
  6. Preserve historical statements and evidence accurately; do not indiscriminately rewrite past records.
  7. Reconcile any live evidence links and verified mirror locators affected by the move.
  8. Ensure there is exactly one authoritative location for actual ODD records.
  9. Preserve the existing retirement, validation, and closure behavior.

  Respect the existing ODD bootstrap requirements. If the migration requires a governing task record, create it under the currently valid authority and move that same record during the transition. Do not create a competing tracker.

  A successful implementation must migrate the existing records, not merely update future creation instructions.

  ## 3. Adopt the new Incident directory convention

  Update AICore's incident workflow to use:

  `incidents/<DATE> #ID/`

  instead of:

  `tickets/<DATE> #ID/`

  Preserve the existing incident record format, analysis stages, screenshots, validations, evidence packs, and closure requirements.

  Update relevant instructions, scaffolding, validators, and references where required by the actual implementation.

  AICore currently has no actual incident cases to migrate.

  **Do not create fake cases or perform unnecessary data migration.**

  ## 4. Separate shared and project diagnostic knowledge

  ### AICore-managed definitions

  Keep these files under the existing managed path:
  - `.aicore/core/knowledge/diagnostics/symptoms.md`
  - `.aicore/core/knowledge/diagnostics/problems.md`
  - `.aicore/core/knowledge/diagnostics/diagnostic-guidance.md`

  These contain shared baseline classifications, diagnostic methodology, schemas, and admission rules.

  ### Project-owned learning

  The new destination-owned registers must use:
  - `incidents/diagnostics/symptoms.md`
  - `incidents/diagnostics/problems.md`

  They must be accessible to both Development and Incident workflows.

  Preserve the existing diagnostic relationships and semantics:
  - Symptom classification.
  - Known problem identification.
  - Team: `incident | dev`.
  - Discriminators and exclusions.
  - Lifecycle and matching eligibility.
  - `exact`, `structural`, and `no_match` verdicts.
  - `case:` and optional `pack:` evidence references.
  - Admission, user approval, and closure rules.

  Do not introduce per-problem files, a database, an index service, or generated combined registers.

  The local problem register must be the single authoritative source for project problem entries.

  ## 5. Support independent local learning safely

  Destination projects must be able to create new symptoms and problems without modifying AICore-managed content.

  Implement collision-safe symptom identifiers using the revised plan's namespaced approach:
  - Shared baseline: `S-01`, `S-02`, etc.
  - Destination-owned: `LOCAL:S-01`, `LOCAL:S-02`, etc.

  Finalize a consistent, maintainable numeric grammar without imposing an arbitrary small capacity.

  ### Required behavior
  1. Preserve existing baseline identifiers.
  2. Parse complete identifier tokens rather than substring matches.
  3. Validate local and baseline symptom references.
  4. Reject duplicate or ambiguous definitions.
  5. Prevent unknown symptom references from silently producing incorrect diagnostic results.
  6. Ensure both teams can use baseline and locally accumulated classifications.
  7. Preserve existing evidence relationships.
  8. Fail safely on invalid or ambiguous input.

  Do not silently renumber historical identifiers.

  If existing data presents an ambiguity that cannot be resolved safely, stop the affected operation and report the conflict.

  Avoid introducing a generalized identity-management subsystem.

  ## 6. Register initialization and validation

  Reuse the existing incident-workflow initialization/scaffolding capabilities where appropriate.

  Provide managed empty-register templates that allow authorized workflows to create valid destination-owned diagnostic files.

  ### Initialization rules
  - Create local registers only during an explicitly authorized initialization workflow.
  - Never overwrite existing project-owned files.
  - Validate existing files before using them.
  - Distinguish an intentionally empty register from a missing or malformed register.
  - Missing or invalid required registers must not silently become `no_match`.
  - Ordinary read operations must not create or modify files.
  - Regular AICore synchronization must not create, overwrite, or delete project-owned diagnostic records.

  The AICore repository itself does not need fabricated incident data or manually seeded example records.

  Update the incident validator and its tests to reflect the new authoritative paths and validation behavior.

  ## 7. Preserve application layout flexibility

  AICore must support both single-application and multi-application destination repositories.

  Do not mandate:
  - `apps/`
  - `development/`
  - A particular framework layout
  - A particular programming language

  Keep existing AICore application and tool sources such as `cli/` and `mcp-servers/` unchanged unless a demonstrated implementation dependency requires a narrow adjustment.

  Application documentation can live alongside its application, while repository-wide technical documentation can live under `docs/`.

  ODD remains dedicated to development workflow records.

  ## 8. Synchronization and distribution safety

  Preserve the current distribution-clearance architecture and its ownership guarantees.

  Verify that:
  1. Managed templates and shared definitions continue to synchronize correctly.
  2. Root-level `odd/` records are not distributed as managed framework content.
  3. Root-level `incidents/` records are not bound as managed framework content.
  4. Destination-owned diagnostic registers cannot be overwritten or deleted by normal AICore synchronization.
  5. Managed baseline updates do not invalidate existing local learning without explicit detection.
  6. The new architecture works with the existing supported OpenCode and Cursor integrations.

  Perform synchronization verification only against isolated, synthetic test fixtures under the AICore testing environment.

  **Do not access or run synchronization against real destination repositories.**

  ## 9. Implementation and testing

  Use AICore's existing ODD workflow and applicable architecture, testing, and review contracts.

  Organize the work into bounded stages:
  1. Baseline inventory and safety checks.
  2. Existing ODD record migration.
  3. ODD contracts, references, and validation updates.
  4. Diagnostic identifier and ownership contracts.
  5. Local register templates, initialization, and validation.
  6. Incident directory convention update.
  7. Synchronization regression testing.
  8. Independent integrated review.

  Stage boundaries may be adjusted when real dependencies require it, but do not expand scope unnecessarily.

  ### Required acceptance criteria
  - Every existing AICore ODD record is accounted for and preserved.
  - Existing ODD features retain their valid derived statuses.
  - New ODD records use the root-level `odd/`.
  - Existing incident lifecycle behavior remains intact.
  - New incident work uses `incidents/`.
  - Shared and local diagnostics can be read together without ID ambiguity.
  - Both Development and Incident problem entries remain supported.
  - Missing, malformed, or conflicting knowledge fails safely.
  - Authorized initialization never overwrites existing records.
  - Synchronization leaves destination-owned content untouched.
  - Relevant unit, integration, regression, and workflow tests pass.
  - Independent review reports no unresolved blocking findings.

  Do not claim successful migration based solely on documentation or directory presence.

  ## 10. Git/GitHub and authorization boundaries

  **Authorized scope: AICore source repository only.**

  No authorization is granted to inspect, modify, initialize, synchronize, migrate, or otherwise operate on existing destination repositories.

  All Git/GitHub operations must be performed exclusively by **Herald**, following its independent safety checks.

  Herald must assess repository state, branch freshness against main, change scope, and evidence before executing Git operations.

  Use the established PR workflow. Do not bypass independent review or introduce unrelated changes.

  Do not merge any pull request. The final merge decision belongs to me.

  Do not automatically deploy, install, or roll out this architecture to destination repositories.

  If an unexpected dependency creates a substantially larger implementation or ongoing maintenance burden than this plan anticipates, stop the affected expansion and present its scope, consequences, and simpler alternatives for my approval. Do not silently broaden the work.

  ## 11. Final deliverable

  When implementation and validation are complete, provide:
  1. Summary of the implemented architecture.
  2. Final actual AICore directory structure.
  3. Inventory of migrated ODD records and preservation results.
  4. Files and contracts modified.
  5. Diagnostic identifier and register initialization behavior.
  6. Incident workflow compatibility results.
  7. Synchronization safety test results.
  8. Independent review verdict and unresolved limitations.
  9. PR URL and reviewed head SHA, if a PR was authorized and created.
  10. Any remaining manual decisions or risks.

  Clearly distinguish implementation completed in AICore from architecture merely supported for future destinations.

  **Do not claim any existing destination repository was migrated or updated.**

  Stop before merge and report the verified result for my decision.
- L2 — 2026-11-15 — User restricted the current execution to creating this record and completing the preservation inventory; no relocation is authorized in this milestone. Full mirror reconciliation pending; no full-copy verification claimed.
- L3 — 2026-11-15 — Preservation inventory captured at `output/odd-preservation-inventory.md`; independent file-set, hash, lifecycle and completion-row comparison passed before this Log update. Reference classification and durable preservation remain pending, so relocation is blocked and this task is not complete. The inventory and comparison must be refreshed after this edit.
- L4 — 2026-11-15 — Milestone 1 preservation baseline. Baseline: `.aicore/core/odd/` holds **28** non-template records — **20 tasks** and **8 features** — each mapped to `odd/<kind>/<same-filename>`. Set identity is one digest over the sorted `kind/filename <sha256>` lines of the **27 records other than this governing record**, because this record is the mutable evidence carrier: `a3b1c2cbc9060f9ed4ccc67edd85141921bccb7bf691fa3b7f563eef1b886545`. Post-relocation verification recomputes that same digest at `odd/` and requires equality; this record's own preservation is proven by its move plus its recorded hash rather than by the digest. The working per-record inventory and the capture/verify/digest commands stay in gitignored `output/` as reproducible detail, never as the sole home of acceptance evidence.
  Reference classification from bounded repository search: **live authoritative, must change** — `AGENTS.md` L74, L162; `.aicore/core/knowledge/agent-workflow.md` L92, L165, L169; `.agents/skills/odd-workflow/SKILL.md` L16, L20, L21, L30; its `references/_checklist.md` L9, L56; `.opencode/agents/sentinel.md` L3, L69, L135; `.agents/skills/git-pr/SKILL.md` L18; `.agents/skills/op-skill-creator/SKILL.md` L18, L81; `README.md` L11, L74; `docs/README.md` L19; and the record-destination guidance inside both managed templates. **Live evidence dependencies that must stay resolvable** — `.aicore/core/knowledge/debt.md` L43, L59, L85, and `.aicore/core/odd/features/durable-feature-file.md` R1, whose path statement is itself the requirement and must be reworded with its tick re-verified. **Historical, left unchanged** — dated entries in `docs/architecture/odd-adoption-status.md`, `docs/research/`, and past task Logs that cite then-current locations. **Retired, pre-existing and unrelated** — `docs/architecture/odd-adoption-status.md` and `docs/research/` links to records that no longer exist (for example `odd-source-fidelity-alignment.md`, `gentle-ai-odd-blueprint-research.md`, `review-process-hardening.md`) and the already-removed `PROJECT-STRUCTURE.md`; these are recorded as limitations, not migration defects. Known limitation: historical records that depend on a retired record are not repairable by this move and are not counted as blocking; no unresolved live dependency blocks relocation.
- L5 — 2026-11-15 — Milestone 1 verified. Source set **28 records: 20 tasks, 8 features**, mapped one-to-one to `odd/<kind>/<same-filename>`. Recorded commands: `node output/odd-inventory-capture.cjs` → 28 records written; `node output/odd-inventory-verify.cjs` → `{actual:28, inventoried:28, tasks:20, features:8, errors:[]}`; `node output/odd-baseline-digest.cjs .aicore/core/odd 2026-11-15-project-owned-artifacts.md` → `digest a3b1c2cbc9060f9ed4ccc67edd85141921bccb7bf691fa3b7f563eef1b886545` reproducing the value in L4; `node .agents/skills/odd-workflow/scripts/validate_feature.ts .aicore/core/odd/tasks` → `ok` for all 20 records; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts .aicore/core/odd/features` → `ok` for all 8, derived statuses seven `achieved` and `organic-driven-development` `partial`. Milestone 1 passes: exactly one authoritative location still holds the records, no record was relocated, and no unresolved live dependency blocks relocation. T1 stays `in progress` because task completion requires a delivery commit reference and none exists yet.
- L6 — 2026-11-15 — Records relocated to root `odd/tasks/` and `odd/features/`; both managed templates remain at `.aicore/core/odd/`. The 27 non-governing records moved with no content change: recomputing the L4 digest at `odd/` returned `a3b1c2cbc9060f9ed4ccc67edd85141921bccb7bf691fa3b7f563eef1b886545`, identical to the baseline. This record moved in the same operation and is authoritative only at its new path.
- L7 — 2026-11-15 — Implementation delivered. **ODD:** 28 records now live under `odd/`; templates stay managed; 36 live path references updated across `AGENTS.md`, `agent-workflow.md`, `agents.md`, `debt.md`, the `odd-workflow` skill and checklist, `sentinel.md`, `git-pr`, `op-skill-creator`, `README.md`, `docs/README.md` and the durable-feature requirement. Historical records and source-local research keep their original wording. **Incident:** case root is `incidents/<DATE> #ID/`. **Diagnostics:** managed catalogs keep the baseline classes, model and rules and ship without rows; the project registers are `incidents/diagnostics/{symptoms,problems}.md`, with `LOCAL:S-xx` for project classes, complete-token parsing, duplicate/unknown-reference detection and fail-closed missing-register reporting (`ValidateDiagnosticKnowledge` in the incident skill); empty-register templates ship inside the incident skill. **Verification:** `pnpm --dir cli/aicore test` 150 passed, 4 skipped; `pnpm --dir cli/aicore typecheck` exit 0; incident skill 107 passed and typecheck exit 0; `odd-workflow` skill 55 passed; `validate_feature.ts odd/tasks` and `validate_feature_file.ts odd/features` all `ok`. Synchronization safety is asserted by `tests/integration/project-owned-artifacts.test.ts`: nothing under `odd/` or `incidents/` is cleared, and an expansion of the incident skill binds no project register. T2–T4 await a delivery commit reference; independent review is outstanding.
- L8 — 2026-11-15 — User correction, verbatim: "Acknowledged. Proceed with the previously authorized AICore architecture implementation." and, in the same instruction, "Update the existing root `README.md` to explain and navigate the new architecture. Do not create a competing architecture overview." and "Migrate AICore's actual ODD records to root `odd/`; do not merely update instructions." S9's quoted requirement comes from this correction, not from L1. Independent document audit round 1 returned `[FAIL]` with eight findings: stale validator paths in the ODD skill and checklist, three stale register labels, a mis-sourced S9 quote, task rows that lagged delivery, an unset delivery count, and four re-anchored debt citations. All eight were remediated on this candidate. Round 2 confirmed the eight closed and returned three more, all remediated: the `debt.md` characterisation of the retired-record section and its delivery sentence were re-cited to `.agents/skills/odd-workflow/SKILL.md:162`, `AGENTS.md` now names `odd/features/` and `incidents/` beside `odd/tasks/`, and the Sentinel audit scope gained an `odd/features/*.md` bucket, which closes round 1's coverage advisory. Durable-requirement re-verification: `odd/features/durable-feature-file.md` R1 now names `odd/features/durable-feature-file.md`, that file exists, R6 permits a path that is itself the behaviour, all seven requirements remain ticked and the derived status is still `achieved`; no other requirement was re-verified. Path-reference count: the reproducible figure is the 36 replacements reported by the batch update across 12 files, which includes template-path-preserving edits; the earlier "36 live path references" wording overstated it as live references alone.
- L9 — 2026-11-15 — Delivery published as PR #191, head `b233484af917ceb8220dc67143ef5bef6945b97d`, on branch `refactor/architecture/project-owned-artifacts` based on the verified `origin/main` at `5f35dd5c86cbebf42ececa3a63d9d8c0ef1131f5`. Herald 📯 (Release Manager) verified branch identity, zero divergence from `origin/main` before push, and that the change set contains only AICore source paths, with nothing under the ignored trees and no destination repository accessed. Commits: `dff244f` relocated the records, `5346998` split the diagnostic registers and the incident code, `b233484` updated the ODD contracts, documentation and this record. Measured authored change: 893 additions, 78 deletions, 61 paths. T2–T4 are now `done` against those commits. The PR is not merged; merge remains the user's decision.
- L10 — 2026-11-15 — Review findings B2 and A3 closed with executable evidence. **B2:** `cli/aicore/tests/e2e/sync-project-owned-artifacts.test.ts` enrolls a disposable destination with the real `init --bind-cleared`, plants destination-owned ODD records, two diagnostic registers and an incident case, then runs the real `apply` twice and asserts byte-identical preservation after each run, that the destination's bindings record no `odd/` or `incidents/` source, and that managed payloads (the ODD skill and the managed `_template.md`) still arrive. Observed: `pnpm --dir cli/aicore test:e2e` → 10 files, 19 passed, including both new cases; no real destination repository was touched. **A3:** `InitializeLocalRegisters` is now the only creating operation, and `tests/integration/register-initialization.test.ts` records six observed results — creation of both missing registers from their templates, an existing register kept byte-for-byte, both existing registers untouched, a duplicated local id reported as `KNOWLEDGE-3` without repair, a baseline-form id reported as `KNOWLEDGE-7` without repair, and a read-only validation creating nothing. Observed: incident skill 114 passed; `typecheck` exit 0. Regression at this candidate: `pnpm --dir cli/aicore test` 150 passed, 4 skipped; `pnpm --dir cli/aicore typecheck` exit 0; ODD validators `ok`. T5 independent acceptance remains open pending review at the delivered head.
- L11 — 2026-11-15 — Review findings A4, A5 and A6 closed. **A4:** the end-to-end test now invokes the real `check` command after the two `apply` runs and asserts an accepted status plus unchanged project records; its own comment records why enrollment leaves reconciliation pending. **A5:** the sixth initialization case now calls the read-only validation and asserts both reported violations and that no file or directory was created, instead of asserting a seed map. **A6:** `scripts/init_local_registers.ts` is the runnable entry point, composing `InitializeLocalRegisters` over the real filesystem with `usage: init_local_registers.ts <repo-root>`, exit 1 on a reported defect; `SKILL.md` step 0 names it. Observed at this candidate: incident skill 114 passed, `typecheck` exit 0, `init_local_registers.ts --help` printed its usage line, and the target e2e file passed both cases. L10's earlier "six observed results" wording is corrected by this entry: five were asserted and the sixth is now genuinely observed.
- L12 — 2026-11-15 — Review finding A7 closed. `init_local_registers.ts` resolved its ports inconsistently: the repo-relative register paths were joined with the repo root while the shipped template paths were already absolute, so a joined absolute segment was not reset and the create path failed. The script now resolves a port path against the repo root only when it is relative, and the new `tests/e2e/init-registers-cli.test.ts` runs the real entry point over three disposable roots: creation of both registers, a second run keeping an authored register byte-identical, and a malformed register reported with exit 1 and left untouched. Observed at this candidate: incident skill 117 passed, `typecheck` exit 0.
- L13 — Close: 2026-11-24 — `T5`'s open integrated acceptance is discharged. PR #191 merged as `6e6d19b`; independent semantic acceptance at that squash commit was obtained from Sentinel 🛡️ (Quality Guardian) as the content authority for records and agent documents: `[PASS]` with `S1`–`S10` verified and none unverified, reading the relocated root `odd/` records with managed templates still under `.aicore/core/odd/`, the `LOCAL:S-xx` complete-token parsing, the fail-closed duplicate/unknown-reference reporting, the create-only register initialization, the synchronization-preservation end-to-end case, and the managed-versus-project-owned mapping in `README.md`. `T1` and `T5` now name the squash commit. L1–L12 are unchanged by this closure.
