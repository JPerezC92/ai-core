# Skill implementation and testing alignment, and ODD lifecycle closure

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-17
> **Objective:** Correct the confirmed application-responsibility defects in `incident-workflow`, align the three affected skill packages' test boundaries so each genuinely satisfies the canonical test distribution without losing regression protection, and establish one unambiguous ODD completion procedure — all in exactly one pull request.
> **Branch:** `fix/architecture/skill-implementation-testing-alignment` — created by Herald 📯 (Release Manager) from `main` at `2d7be82410aaddc8b1668a5d48fb52cb7a4ce94d` after this record is written.
> **Delivery:** one PR, mandatory by user instruction; forecast ~750 authored additions + deletions excluding the ODD lifecycle work, above the ~400 feature-level trigger, so the strategy is reviewable work-unit commits inside the one PR — P3 `incident-workflow` production correction, P3 `incident-workflow` tests, P4 `odd-workflow` tests, P4 `git-pr-workflow` tests, then records and debt evidence.
> **Runner:** `pnpm --dir .agents/skills/incident-workflow exec vitest run`; `pnpm --dir .agents/skills/incident-workflow typecheck`; `pnpm --dir .agents/skills/odd-workflow exec vitest run`; `pnpm --dir .agents/skills/odd-workflow typecheck`; `pnpm --dir .agents/skills/git-pr-workflow exec vitest run`; `pnpm --dir .agents/skills/git-pr-workflow typecheck`; `pnpm format:check`; `pnpm lint`; `pnpm typecheck`; `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks`; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts odd/features`

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — `incident-workflow`'s genuine application decisions are owned by the application boundary, not by the delivery entry point. Exact requirement: "Move genuine application decisions into the appropriate existing application boundary." and "Follow C3 for actual application operations:" and "Move genuine application decisions into the appropriate existing application boundary." Acceptance: read the package's domain, application and delivery modules; each confirmed application decision is owned by an application operation or a domain rule, the delivery entry point only composes adapters and binds returned results to output and exit status, and no delivery module decides a business outcome.
- S2 — The close-out skip outcome has exactly one owner and the validator's observable behavior is unchanged. Exact requirement: "My preference is to **preserve current externally observable behavior** unless a genuine specification defect requires changing it." and "consolidate ownership of the skip outcome while preserving the existing CLI output and exit status." and "Do not delete a domain rule or its unique regression coverage until its role and consumers are verified." Acceptance: run the package suite; a close-out with no durable ticket record still writes exactly `CLOSE-SKIPPED: ticket_<id>.md not found at <dir>` to stderr with exit status 2, the rule for the missing durable ticket record still exists with its own coverage at its owning boundary, and the condition is owned by one layer only.
- S3 — `incident-workflow`'s behaviors are proven at the boundary that owns each one. Exact requirement: "Move application decisions to legitimate T2 use-case tests." and "Keep genuine T4 adapter integration coverage." and "Reduce E2E to the smallest sufficient set proving assembled CLI behavior." and "Preserve exit codes, diagnostics, filesystem effects and unique regression assertions." Acceptance: run the package suite and measure the boundary counts; every relocated assertion names the boundary that now protects it, no unique assertion is lost, and the exit codes, diagnostics and filesystem effects report exactly what they reported before.
- S4 — `odd-workflow`'s contracts are separated and its adapters carry real coverage. Exact requirement: "Separate the contracts being tested:" and "Where behavior is already covered by valid unit tests, avoid repeating the same assertions through the assembled CLI unless the higher boundary provides distinct regression protection." and "Add real adapter integration coverage only where a legitimate adapter contract exists." and "Do not manufacture integration tests." Acceptance: run the package suite; each test file exercises the boundary it claims, the filesystem adapters carry real-filesystem coverage, and no behavior is asserted at two boundaries without distinct regression protection.
- S5 — `git-pr-workflow`'s contracts are separated, its real-Git coverage survives, and confirmed duplicate production units are removed. Exact requirement: "Preserve:" and "Reduce duplicate E2E assertions only when their behavior remains proven at an appropriate cheaper boundary." and "Maintain meaningful real-Git integration tests." and "Do not create new repository fixtures unless their unique regression value is demonstrated." and "Remove duplicated production validation only if its duplication is confirmed and its removal preserves behavior." Acceptance: run the package suite; the real-Git merge-base and disjoint-history behavior, the evidence-body assembly, the attribution scan, the packaging and dependency-closure behavior and the CLI input/output contracts remain proven, and a removed production unit is replaced only where the duplication is confirmed and every observable byte and exit status is preserved.
- S6 — The coverage-preservation gate holds for all three packages. Exact requirement: "For each removed or relocated assertion, demonstrate: 1. The original behavior protected. 2. Its actual architectural owner. 3. Its replacement assertion or existing equivalent. 4. The boundary at which it is now proven. 5. Any higher-level regression protection that remains necessary. 6. Whether observable behavior is unchanged." and "Do not merely move tests between directories to improve distribution." and "Do not split tests artificially to increase unit counts." and "Do not remove unique E2E or integration coverage." Acceptance: read the delivered assertion-preservation mapping; every removed or relocated assertion carries all six facts and no assertion count drops without a named replacement.
- S7 — Each affected package is evaluated individually and the distribution is measured at real boundaries. Exact requirement: "Each affected package must be evaluated individually." and "No unrelated package's distribution may worsen." and "Outstanding repository violations remain visible." and "No agent may approve an exception." and "No repository-wide compliance may be claimed prematurely." and "Test counts must never be optimized at the expense of coverage." Acceptance: read the delivered report and the package diffs; each package's measured counts are stated at their verified boundaries, no other test-owning unit changed, the remaining violations are named, and no exception is recorded anywhere.
- S8 — The ODD completion stages are stated once, in order, in their existing owner. Exact requirement: "Establish an unambiguous completion procedure using existing AICore infrastructure." and "It must distinguish:" and "Implementation completed." and "Tests and reviews completed." and "PR published." and "ODD task closed." and "PR merged." and "Post-merge cleanup completed." and "Do not create a new status framework, new agent, new dependency or another general-purpose validation subsystem." Acceptance: read the odd-workflow skill; one statement names the stages in order and assigns each precondition to its stage, closure requires no merge evidence, the merge stays user-only, merge proof belongs to retirement, and no new status value, validator, agent, service, tracker or framework is introduced.
- S9 — A report cannot claim definitive completion while a mandatory closure remains outstanding. Exact requirement: "The procedure must not announce all work as complete when mandatory closure requirements are outstanding." and "Ensure Cipher and the relevant delivery workflow cannot claim definitive completion while an authorized mandatory closure remains unfinished." and "A task is not closed merely because its implementation passed tests or its PR was merged." Acceptance: read the shared message-presentation rule and the delivery workflow; the completion status separates the pull-request-ready state from the fully-closed state, and no rule lets a delivery claim completion while a closure action is outstanding.
- S10 — Eligible existing records are closed on evidence and ineligible ones are left open. Exact requirement: "For records whose implementation and required evidence are already complete:" and "Verify their actual commit references." and "Verify their independent acceptance." and "Satisfy the existing closure contract." and "Mark tasks done only with valid evidence." and "Record the appropriate closure entry and date." and "Preserve their history and ownership." and "Do not mark genuinely unfinished records as closed." and "If a record cannot close legitimately, state the exact missing requirement instead of leaving an ambiguous status." Acceptance: read every record that changed state; each closed record's task rows are `done` with valid commit references, it carries a `Close:` entry and a `Closed:` date, and every record left active names its open prerequisite.
- S11 — The debt register reflects only the criteria that are actually met. Exact requirement: "Before editing the debt register, inspect the actual open entries and their criteria." and "Reuse relevant existing debts." and "Do not duplicate DEBT-048 or create a new debt for every test classification finding." and "Retire debts only when their complete original resolution criteria have been met and the required evidence is recorded." and "Do not automatically close DEBT-046, DEBT-055 or DEBT-056 merely because these three packages become compliant." Acceptance: read the debt register; DEBT-048's entry states its disposition and its met or unmet criteria with the evidence, DEBT-046, DEBT-055 and DEBT-056 are still present, and no duplicate entry was added.
- S12 — One branch carries the whole delivery in exactly one pull request. Exact requirement: "**Publish exactly ONE PR targeting `main`.**" and "Do not create separate PRs for each package." and "Do not include unrelated uncommitted changes." and "No merge is authorized." Acceptance: inspect the base-to-head diff and the pull-request list; exactly one pull request targets `main`, every changed path traces to this record, and no merge was performed.
- S13 — The authorized scope boundaries hold. Exact requirement: "Do not begin:" and "Core Sync P5/P6." and "`system-one` or `odd-adviser` P7." and "A general T2 contract redesign." and "Warden or permissions changes." and "Downstream repository synchronization." Acceptance: inspect the base-to-head diff; no path under `cli/aicore/`, `mcp-servers/`, `.opencode/plugins/`, the shared testing contract's rule identifiers, the unrelated debt entries or any downstream repository changed.

## Tasks

- T1 | S1, S2 | delegated (production source under Forge 🔨 ownership; the `incident-workflow` domain, application and delivery modules) — Forge 🔨 (Implementer) | open | commit: pending
- T2 | S3, S6 | delegated (test authoring and routine execution under Forge 🔨 ownership; the `incident-workflow` unit, integration and end-to-end levels) — Forge 🔨 (Implementer) | open | commit: pending
- T3 | S1, S2 | delegated (C3, C4, C5, C7 and P2 conformance of the corrected `incident-workflow` modules) — Bastion 🧱 (Backend & Scripts Architect) | open | commit: pending
- T4 | S3, S6, S7 | delegated (test-architecture risk: restructured levels, boundary re-classification, assertion-preservation equivalence) — Crucible 🔥 (Test Architect) | open | commit: pending
- T5 | S4 | delegated (`odd-workflow` test boundary separation and real-filesystem adapter coverage) — Forge 🔨 (Implementer) | open | commit: pending
- T6 | S5 | delegated (`git-pr-workflow` test boundary separation and confirmed duplicate production unit removal) — Forge 🔨 (Implementer) | open | commit: pending
- T7 | S4, S5 | delegated (C3, C7 and P2 conformance of the touched `odd-workflow` and `git-pr-workflow` modules) — Bastion 🧱 (Backend & Scripts Architect) | open | commit: pending
- T8 | S8, S9 | inline (the ODD lifecycle owner surfaces, Cipher 🔓 owns the ODD lifecycle) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T9 | S10 | inline (record closure: commit references and independent acceptance verified per eligible record) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T10 | S11 | inline (debt register disposition) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T11 | S8, S9, S10, S11, S13 | delegated (agent documents, shared rules, ODD records and debt register consistency) — Sentinel 🛡️ (Quality Guardian) | open | commit: pending
- T12 | S12 | delegated (sole Git executor: branch, focused commits, push, one pull request) — Herald 📯 (Release Manager) | open | commit: pending
- T13 | S6, S7, S12 | delegated (independent review at the immutable pull-request head) — Inquisitor 🔎 (PR Reviewer) | open | commit: pending

## Log

- L1 — Original request, verbatim:

  # AICore — P3 + P4 Architecture and Testing Remediation, ODD Lifecycle Closure

  We are starting a completely NEW OpenCode session.

  ## Objective

  Continue the approved AICore architecture and testing remediation initiative.

  PR #195 and PR #196 have been merged.

  The previous deliveries established:
  - Permanent T8 test-distribution requirements.
  - Explicit user-only approval for distribution exceptions.
  - Progressive remediation without accepting existing violations.
  - Corrected `op-model` implementation and tests.
  - Corrected `git-pr` implementation and tests.

  Do not reopen those completed implementations.

  **This session combines P3 and P4, plus narrowly scoped ODD lifecycle remediation, into exactly ONE pull request.**

  The primary objective is architectural correctness with appropriate test coverage, not test-count manipulation.

  ---

  ## 1. Verify the actual repository state

  Before implementation, inspect the actual AICore checkout.

  Herald 📯 is the sole Git/GitHub executor.

  Verify:
  - Current branch and HEAD.
  - Local and remote `main`.
  - That PR #195 and PR #196 are merged.
  - Staged, unstaged and untracked changes.
  - Relevant existing worktrees and their ownership.
  - Applicable repository architecture, testing and ODD contracts.

  Read the actual contracts for:
  - Domain, application, infrastructure and delivery boundaries.
  - C3, C4 and C7.
  - T2, T4, T5, T8, T9, T10 and T21.
  - Durable feature files and ODD task lifecycles.
  - Technical debt retirement.
  - Git/GitHub execution authority.

  Do not rely on previous agent reports instead of inspecting the current source.

  However, do not repeat completed repository-wide audits without evidence of changed inputs.

  Protect all unrelated work.

  ## 2. Approved scope — P3: incident-workflow

  Package:

  `.agents/skills/incident-workflow/`

  Previous measured distribution:
  - Unit: 91
  - Integration: 10
  - E2E: 21

  The earlier investigation identified application decisions inside the delivery entry point.

  Relevant findings included:
  - Mode-to-operation selection performed in `entry.ts`.
  - Register and parsing decisions performed too close to the entry point.
  - Close-skip exit handling duplicated or reinterpreted across layers.
  - A forwarding function that may be unnecessary.
  - Application behavior tested through expensive CLI boundaries.

  ### Required implementation correction

  Inspect and confirm each violation.

  Move genuine application decisions into the appropriate existing application boundary.

  Follow C3 for actual application operations:
  - Class with `execute()`.
  - Constructor-injected collaborators.
  - Correct domain and application responsibilities.
  - Infrastructure isolated behind the proper ports.
  - Delivery responsible for input/output and composition.

  Do not introduce artificial use cases for pure functions.

  Prefer removing unnecessary forwarding code over relocating it.

  ### CLOSE-0 / CLOSE-SKIPPED discrepancy

  The previous investigation reported:
  - Domain rule: CLOSE-0, exit 1.
  - CLI behavior: CLOSE-SKIPPED, exit 2.

  My preference is to **preserve current externally observable behavior** unless a genuine specification defect requires changing it.

  Investigate the actual source and contracts.

  If the previous BC-1a proposal remains valid, consolidate ownership of the skip outcome while preserving the existing CLI output and exit status.

  Do not delete a domain rule or its unique regression coverage until its role and consumers are verified.

  Any externally observable behavioral change requires my separate authorization.

  ### Testing correction

  After correcting the implementation:
  - Move application decisions to legitimate T2 use-case tests.
  - Keep genuine T4 adapter integration coverage.
  - Reduce E2E to the smallest sufficient set proving assembled CLI behavior.
  - Preserve exit codes, diagnostics, filesystem effects and unique regression assertions.

  Prior forecast: 112 unit / 11 integration / 2 E2E.

  This is a planning estimate, not a mandatory numerical target.

  Do not weaken coverage to reach it.

  ## 3. Approved scope — P4: odd-workflow

  Package:

  `.agents/skills/odd-workflow/`

  Previous measured distribution:
  - Unit: 32
  - Integration: 0
  - E2E: 23

  The investigation found that several tests labeled integration exercise assembled CLI entry points.

  Verify their actual behavior before changing them.

  ### Required correction

  Separate the contracts being tested:
  - Domain and application behavior at approved unit targets.
  - Real filesystem-source adapter behavior at T4.
  - Minimal assembled-script behavior at T5.

  Where behavior is already covered by valid unit tests, avoid repeating the same assertions through the assembled CLI unless the higher boundary provides distinct regression protection.

  Add real adapter integration coverage only where a legitimate adapter contract exists.

  Do not manufacture integration tests.

  Preserve representative CLI execution, output, error handling and distribution/import behavior.

  Previous forecast: 38 unit / 8 integration / 4 E2E.

  Again, this is a forecast, not a count quota.

  Avoid production changes unless a confirmed architectural defect requires them.

  ## 4. Approved scope — P4: git-pr-workflow

  Package:

  `.agents/skills/git-pr-workflow/`

  Previous measured distribution:
  - Unit: 40
  - Integration: 7
  - E2E: 19

  The earlier investigation identified redundant higher-level assertions and potentially duplicated CLI validation logic.

  ### Required correction

  Inspect the actual implementation.

  Preserve:
  - Real-Git merge-base and disjoint-history behavior.
  - Evidence-body assembly.
  - Attribution scanning.
  - CLI input and output contracts.
  - Packaging and dependency-closure behavior.
  - The optimizations previously delivered under DEBT-053.

  Reduce duplicate E2E assertions only when their behavior remains proven at an appropriate cheaper boundary.

  Maintain meaningful real-Git integration tests.

  Do not create new repository fixtures unless their unique regression value is demonstrated.

  Remove duplicated production validation only if its duplication is confirmed and its removal preserves behavior.

  Previous forecast: 46 unit / 12 integration / 8 E2E.

  Do not force those exact counts.

  ## 5. Mandatory coverage-preservation gate

  For all three packages, establish the existing assertion baseline before removing or reorganizing tests.

  For each removed or relocated assertion, demonstrate:
  1. The original behavior protected.
  2. Its actual architectural owner.
  3. Its replacement assertion or existing equivalent.
  4. The boundary at which it is now proven.
  5. Any higher-level regression protection that remains necessary.
  6. Whether observable behavior is unchanged.

  Do not merely move tests between directories to improve distribution.

  Do not split tests artificially to increase unit counts.

  Do not remove unique E2E or integration coverage.

  Do not replace meaningful real-adapter testing with mocks solely for speed.

  If a proposed reduction loses a unique contract, preserve the test and report the architectural blocker.

  ## 6. Enforce T8 correctly

  The expected test architecture is:

  **Unit > Integration > E2E**

  Use counts derived from actual behavioral boundaries, not filenames or directories.

  No permanent exceptions are approved.

  This remediation is expressly authorized to proceed under the established progressive-remediation rule.

  Requirements:
  - Each affected package must be evaluated individually.
  - No unrelated package's distribution may worsen.
  - Outstanding repository violations remain visible.
  - No agent may approve an exception.
  - No repository-wide compliance may be claimed prematurely.
  - Test counts must never be optimized at the expense of coverage.

  The target outcome for this delivery is genuine T8 compliance in all three affected packages.

  If a package cannot comply honestly, report the actual architectural blocker rather than fabricating tests or accepting an exception.

  ## 7. ODD lifecycle — address the recurring incomplete-closure problem

  We have repeatedly encountered agents reporting "ALL FINISHED" while the governing ODD task remains active with unfinished task rows.

  This must be addressed systematically.

  ### A. Inventory pending records

  Inspect the existing ODD task records and identify which are still active.

  Distinguish:
  - Implementation completed and merged, administrative closure pending.
  - Implementation delivered in a PR but not merged.
  - Genuinely incomplete work.
  - Work blocked by an explicit dependency or decision.

  Pay particular attention to records associated with the recently merged PRs #194, #195 and #196.

  Do not assume every active record should be closed.

  Do not rewrite historical ODD evidence.

  ### B. Verify existing DEBT-048

  Inspect the actual DEBT-048 definition and its resolution criteria.

  Determine whether it already covers:
  - Ambiguity about closure before or after PR merge.
  - Agents reporting delivery complete while the task remains active.
  - Missing commit references or acceptance evidence.
  - Repeated failure to apply the canonical closure procedure.

  If the existing debt covers these problems, update its evidence rather than creating a duplicate.

  If the recurring "ALL FINISHED" issue is genuinely distinct, identify the uncovered requirement before proposing an additional debt.

  ### C. Correct the lifecycle procedure minimally

  Establish an unambiguous completion procedure using existing AICore infrastructure.

  It must distinguish:
  - Implementation completed.
  - Tests and reviews completed.
  - PR published.
  - ODD task closed.
  - PR merged.
  - Post-merge cleanup completed.

  The procedure must not announce all work as complete when mandatory closure requirements are outstanding.

  **A task is not closed merely because its implementation passed tests or its PR was merged.**

  At the same time, do not demand evidence that cannot exist before merge unless the repository's actual contract requires that ordering.

  Use the existing ODD validators, workflow documentation and agent responsibilities.

  Do not create a new status framework, new agent, new dependency or another general-purpose validation subsystem.

  ### D. Close eligible records

  For records whose implementation and required evidence are already complete:
  - Verify their actual commit references.
  - Verify their independent acceptance.
  - Satisfy the existing closure contract.
  - Mark tasks done only with valid evidence.
  - Record the appropriate closure entry and date.
  - Preserve their history and ownership.

  Do not mark genuinely unfinished records as closed.

  Do not close technical debts automatically.

  If a record cannot close legitimately, state the exact missing requirement instead of leaving an ambiguous status.

  ### E. Prevent recurrence

  Ensure Cipher and the relevant delivery workflow cannot claim definitive completion while an authorized mandatory closure remains unfinished.

  If closure must occur after merge, require an explicit truthful handoff and completion step.

  Do not implement another extensive review process.

  **This correction should reduce repeated administrative work, not create more of it.**

  ## 8. Technical debt

  Before editing the debt register, inspect the actual open entries and their criteria.

  Reuse relevant existing debts.

  Do not duplicate DEBT-048 or create a new debt for every test classification finding.

  Retire debts only when their complete original resolution criteria have been met and the required evidence is recorded.

  Do not automatically close DEBT-046, DEBT-055 or DEBT-056 merely because these three packages become compliant.

  Do not mix unrelated Warden, dependency or security remediation into this PR.

  ## 9. Keep the scope controlled

  This is a consolidated delivery, not permission for a repository-wide refactor.

  The approved implementation scope is:
  - `incident-workflow`
  - `odd-workflow`
  - `git-pr-workflow`
  - Minimal ODD lifecycle corrections and evidence-backed closure of eligible existing records.

  Do not begin:
  - Core Sync P5/P6.
  - `system-one` or `odd-adviser` P7.
  - A general T2 contract redesign.
  - Warden or permissions changes.
  - Downstream repository synchronization.

  The prior estimate for P3 + P4 was roughly 750 authored lines, excluding ODD cleanup.

  I explicitly acknowledge that this is a larger-than-usual change.

  Keep changes small and directly tied to confirmed defects.

  If the actual scope expands materially beyond this or the ODD lifecycle work becomes a separate significant implementation, report that before proceeding.

  Do not invent architecture abstractions to make the test pyramid look correct.

  ## 10. One branch, one PR

  Herald 📯 remains the sole Git/GitHub executor.

  After verifying a safe baseline, Herald is authorized to create one dedicated branch from current `main`.

  Use the repository's actual branch naming convention.

  Implement P3 and P4 as separate reviewable work units inside that branch.

  Include associated ODD records and the narrowly scoped lifecycle correction in the same delivery, provided their ownership and dependencies remain coherent.

  Create focused commits rather than unrelated large mixed commits.

  **Publish exactly ONE PR targeting `main`.**

  Do not create separate PRs for each package.

  Do not include unrelated uncommitted changes.

  Do not use destructive cleanup, stash, reset, forced checkout or unsafe worktree manipulation to isolate work.

  No merge is authorized.

  I retain the final merge decision.

  ## 11. Validation and independent review

  Use the existing package test runners and repository verification commands.

  Validate:
  - Real application-operation boundaries.
  - Approved T2 unit targets.
  - Genuine T4 adapter boundaries.
  - Representative T5 assembled entry points.
  - Assertion preservation.
  - Real filesystem and Git behavior where applicable.
  - Exact CLI diagnostics and exit statuses.
  - Final boundary-verified test counts per package.
  - T8 compliance.
  - Root typecheck, lint and formatting.
  - Relevant ODD validators.
  - Correct ODD lifecycle statuses.
  - Applicable independent architecture and test reviews.

  Reuse evidence when its inputs remain unchanged.

  Do not restart repository-wide audits.

  Resolve concrete findings, but avoid repeated reviews that add no new information.

  Independent acceptance must correspond to the actual final PR head.

  ## 12. Final completion requirement

  The recurring incomplete-closure problem is a major concern.

  Before reporting "ALL FINISHED", reconcile the governing task record with the actual delivery state.

  Complete every closure action that is currently possible and authorized.

  Where merge-dependent work remains, distinguish clearly between:

  **PR READY FOR MY MERGE DECISION**

  and

  **ALL AUTHORIZED WORK FULLY CLOSED**

  Do not use the second status when a mandatory closure action remains outstanding.

  Your final report must include:
  1. Single PR URL, base and reviewed head SHA.
  2. Exact implementation changes in the three packages.
  3. Previous and final Unit / Integration / E2E counts.
  4. Assertion-preservation evidence.
  5. Validation results and independent reviewer verdicts.
  6. Remaining T8 violations outside this PR.
  7. ODD records found active and which were legitimately closed.
  8. DEBT-048 disposition and remaining criteria.
  9. Other debts resolved or still open.
  10. Governing ODD task status, with exact closure requirements outstanding.
  11. Confirmation that P5–P7 remain untouched.
  12. A definitive statement of merge readiness and any remaining blockers.

  **The objective is to deliver three architecturally correct, proportionate test suites and stop the recurring ODD closure failures, all within one reviewable PR.**

  Finish the authorized work, provide the required evidence and notify me definitively.

  Do not silently expand scope or begin another remediation phase.

  Merge remains my decision.

- L2 — 2026-11-17 — Classification: **non-small**. Understood: the `incident-workflow` domain, application, infrastructure and delivery modules, the `odd-workflow` and `git-pr-workflow` script zones with their three-level suites, the shared testing and implementation contracts, the odd-workflow skill's lifecycle procedures, the shared message-presentation rule, the debt register and all 28 ODD records were read before this record existed. Risk-contained: no — the slice changes a shipped skill's application boundary, restructures three test levels and edits shared lifecycle rules. Resumable from request plus diff: no. This record is therefore the sole bootstrap write; no other mutation preceded it.
- L3 — 2026-11-17 — Baseline. Herald 📯 reported branch `main`, `HEAD` = local `main` = `origin/main` = `2d7be82410aaddc8b1668a5d48fb52cb7a4ce94d`, an empty `git status --porcelain --untracked-files=all` (0 staged, 0 unstaged, 0 untracked) and three worktrees — the main one plus two clean detached leftovers from PR #192. PRs #194, #195 and #196 are all `MERGED` with merge commits `0315063d`, `8c1ed8dc` and `2d7be824`. One stale local branch `fix/git-pr/implementation-testing-alignment` remains at PR #196's head with no remote counterpart, and no remote branch other than `main` exists. No unrelated work exists in the working tree, so nothing has to be preserved or isolated.
- L4 — 2026-11-17 — Measured test baseline at the verified boundary each case exercises, not by directory. `incident-workflow` 91 unit / 10 integration / 21 end-to-end (Vitest totals 85 / 16 / 21 by directory — the 6 `register-initialization` cases execute a doubled-port application operation and are misfiled under `tests/integration/`). `odd-workflow` 32 unit / 0 integration / 23 end-to-end (Vitest totals 32 / 14 / 9 by directory — the 14 cases under `tests/integration/` call the assembled `main()` of the three entry points and are end-to-end at their verified boundary). `git-pr-workflow` 40 unit / 7 integration / 19 end-to-end (Vitest totals identical). All three suites pass with no failures, skips or warnings; the total case count of each package is unchanged between the two attributions, so the differences are level attribution, not coverage loss. This corrects the `incident-workflow` and `odd-workflow` figures the request quotes.
- L5 — 2026-11-17 — Independent architecture analysis by Bastion 🧱 (Backend & Scripts Architect) over the 51 production files of the three packages, read against C1–C10, P1–P4 and T25: `incident-workflow` `[FAIL]` with five confirmed findings — the close-out "no durable ticket record" condition owned twice (`entry.ts:62-65` returns 2 before `ValidateCloseOut` runs, so domain `CLOSE-0` at `domain/rules.ts:272` is unreachable from the CLI); the delivery edge deciding "register absent therefore empty row set" at `entry.ts:49` against the domain rule at `application/validate_diagnostic_knowledge.ts:9-11`; an application module importing `infrastructure/records.ts` at `application/validate_diagnostic_knowledge.ts:16` against C1; a pass-through wrapper and a constructed collaborator in `application/initialize_local_registers.ts:12,16-24,76`; and the exception-as-result wrapper `parseRecord` at `entry.ts:30-37` against C5. It **refuted** the reported mode-selection finding — C3 expressly allows a composition root or CLI router to wire several operations — and confirmed the close-out correction can preserve the `CLOSE-0` identifier as the domain-side stable code while the stderr prefix stays `CLOSE-SKIPPED`. `odd-workflow` `[PASS]`: no C3 violation, each zone holds domain, one application class with one `execute()` and an infrastructure filesystem adapter, and the entry points only wire and bind. `git-pr-workflow` `[ADVISORY]`: the duplicated CLI units are delivery plumbing, not a rule violation; `escapeNonAscii`, `compactJson`, `printOut`, `printError` and `isDirectExecution` are exact duplicates whose removal preserves every stdout and stderr byte and exit status, while `UsageError` and `parseArguments` diverge and cannot be shared.
- L6 — 2026-11-17 — Independent test-architecture analysis by Crucible 🔥 (Test Architect) over every test file of the three packages: all three are `EXCEPTION REQUIRED` under T8, and the unapproved unit targets are named — `domain/symptom-id.ts` in `incident-workflow` (8 cases, owner `ValidateDiagnosticKnowledge.execute`), `retirement_check/domain/rules.ts` (15 cases, owner `CheckRetirements.execute`) and `feature_validation/domain/rules.ts` (8 cases, owner `ValidateFeatures.execute`) in `odd-workflow`, and `pr_review/domain/snapshot_assembly.ts` (2 cases, owner `PrepareLocalSnapshot.execute`) and `attribution_scan/domain/validation.ts` (9 cases, owner `ScanAttribution.execute`) in `git-pr-workflow`. DEBT-056 is confirmed and extended: all three files under `odd-workflow/tests/integration/` exercise the assembled entry point, not one adapter. It also reports that the three packages each hold a genuine structural tension between a thin adapter surface and a fat delivery edge, and that honest compliance is not reachable in `odd-workflow` and `git-pr-workflow` without either manufacturing cases or extracting CLI-owned decoding and rendering behind an adapter — a production change this slice is not authorized to invent. That residual tension is carried as an explicit deliverable obligation rather than resolved by a quota.
- L7 — 2026-11-17 — P3 `incident-workflow` delivered, in two work units. **Production correction**, covering the five findings Bastion 🧱 confirmed against C1–C10, P1–P4 and T25: the close-out "no durable ticket record" condition had two owners — `domain/rules.ts` emitted `CLOSE-0` as a violation while `entry.ts` short-circuited before the operation ran and printed `CLOSE-SKIPPED: …` with exit 2 — and now has one, because `evaluateCloseOut` returns a discriminated evaluation carrying the condition's stable code `CLOSE-0` and its reason, `ValidateCloseOut.execute()` returns a typed `skipped` outcome, and `entry.ts` only renders it, so the CLI output and exit status are byte-identical and the domain rule survives with its own coverage at the boundary that now owns it; the register's absent-to-empty mapping moved out of the delivery layer into the infrastructure adapter's new port methods `loadProblemRegister` and `loadProblemRows`; the application no longer imports infrastructure, so `ProblemRow` moved to the domain and `ValidateDiagnosticKnowledge` receives the register rows through its input contract; `InitializeLocalRegisters` lost its module-level `validateDiagnosticKnowledge` pass-through wrapper and receives the operation through its constructor; and `parseStateHeader`/`parseTicketRecord` return the domain `ParsedRecord<T>`, deleting the delivery layer's `parseRecord` exception-as-result wrapper. **Tests:** the four files that pinned the old shapes were realigned, `register-initialization` moved to `tests/unit/` because it exercises a doubled-port application operation, the eight `symptom-identifiers` cases were re-expressed through `ValidateDiagnosticKnowledge.execute()`, the six argument-only end-to-end cases moved to a unit test of the argv loader, three new integration modules cover `loadProblemRegister`, `loadProblemRows` and `loadStepFiles` against a real temporary filesystem, and the two help cases consolidated into one. **Measured distribution T2 92 / T4 21 / T5 14 (127 cases), against a baseline of T2 91 / T4 10 / T5 21 — the ordering now holds**; the five loader cases were placed at T4, not T2, because they reach the real, undoubled `yaml` library. `pnpm --dir .agents/skills/incident-workflow exec vitest run` reports 21 files and 127 cases passing, the package typecheck is clean, and `pnpm lint` and `pnpm format:check` report no diagnostics.
- L8 — 2026-11-17 — P4 `odd-workflow` delivered, with no production change: Bastion 🧱 found no confirmed C3 violation in this package, so its application boundaries are untouched. The corrections are boundary corrections — the three files under `tests/integration/` exercised the assembled `main()` of the three entry points and are therefore T5, so they moved to `tests/e2e/`, which confirms and extends DEBT-056's `odd-workflow` finding to all three of them; the 23 assertions that had targeted the pure rule modules `retirement_check/domain/rules.ts` and `feature_validation/domain/rules.ts` were re-expressed through their approved owners `CheckRetirements.execute()` and `ValidateFeatures.execute()`; and the three filesystem adapters, which had zero coverage, now carry real-temporary-filesystem integration coverage of their discovery, normalization, strict-UTF-8 and failure contracts. No test case was removed and no assertion was lost. **Measured distribution T2 35 / T4 20 / T5 17 (72 cases), against a baseline of T2 32 / T4 0 / T5 23 — the ordering now holds.** `pnpm --dir .agents/skills/odd-workflow exec vitest run` reports 12 files and 83 cases passing and the package typecheck is clean.
- L9 — 2026-11-17 — P4 `git-pr-workflow` delivered, and its remaining distribution violation reported rather than manufactured away. **Production:** the five byte-identical delivery units duplicated between the two entry points — `escapeNonAscii`, `compactJson`, `printOut`, `printError` and `isDirectExecution` — were extracted once into `scripts/cli_delivery.ts`, with `isDirectExecution` taking the caller's module URL so direct execution still sets the exit code; the divergent `UsageError` and `parseArguments` were correctly left alone, as was `isRecord`, whose duplication crosses a layer boundary. **Tests:** the 11 assertions that had targeted the rule modules `pr_review/domain/snapshot_assembly.ts` and `attribution_scan/domain/validation.ts` were re-expressed through `PrepareLocalSnapshot.execute()` and `ScanAttribution.execute()`; five new real-adapter cases cover the `GitReader` and filesystem gaps against a real repository and a real temporary filesystem, reusing the existing committed-repository fixture rather than creating another; and the three command-line diagnostic cases consolidated into one table-driven case. The real-Git `mergeBase` disjoint-history assertion, the attribution scan, the evidence-body assembly, the persisted-body verification, the exclusive-create effect, the sorted-JSON output format and the three exit statuses all remain proven, and both CLIs' stdout bytes, stderr bytes and exit statuses are unchanged. **Measured distribution T2 40 / T4 18 / T5 17 (75 cases), against a baseline of T2 40 / T4 7 / T5 19 — the ordering now holds.** The blocker described above was resolved by relocating the duplicated end-to-end assertions to the boundary that owns each of them and by adding five genuinely unverified adapter contracts, not by adding cases to reach a number: the path-inventory rejection moved to the use case that decides it, the missing-file detail moved to the filesystem adapter that raises it, and the CLI keeps only its own rendering, exit statuses and artifact effects. A residual structural limit remains and is not a count violation: the two argv loaders and the scan CLI's file-to-text decoder are private delivery functions, so the CLI's argument diagnostics and input-failure diagnostics have no T2 or T4 home. An authorized production change would have to export the argv loaders into a loader module, as `incident-workflow` does in its `infrastructure/arguments.ts`, and route the attribution CLI's decoding through a named infrastructure adapter. No exception is recorded, no count was manufactured, and no repository-wide compliance is claimed. `pnpm --dir .agents/skills/git-pr-workflow exec vitest run` reports 17 files and 75 cases passing and the package typecheck is clean.
- L10 — 2026-11-17 — The ODD lifecycle correction, delivered in the rules' existing owners. The odd-workflow skill gained one `### Completion stages` statement naming implementation delivered, verification complete, pull request published, record closed, pull request merged and post-merge cleanup in order, assigning each precondition to its stage, stating that closure and the merge are independent of each other and that closure requires no merge evidence, keeping retirement on the record's own closure date, and pointing the report that distinguishes a merge decision from a finished delivery to `.aicore/core/knowledge/agents.md` → `### Message presentation`. That shared rule now reserves `ALL FINISHED` for work whose governing record is closed, distinguishes `PR READY FOR MY MERGE DECISION` from `ALL AUTHORIZED WORK FULLY CLOSED`, and names the outstanding closure action; `AGENTS.md` `### Stop and next-step reporting` points to it rather than restating it. `odd/features/organic-driven-development.md` gained `R26` and `R27`. No new status value, validator, agent, service, tracker or framework was introduced. **DEBT-048 stays open with its evidence updated** rather than duplicated: its ordering gap is closed in its existing owner, and its criterion "merge proof belongs to retirement" cannot be met as written, because the retirement rule's eligibility — exactly `closed` plus seven complete calendar days, with nothing else a condition — was established by the user's own instruction of 2026-11-14 quoted in `odd/tasks/2026-11-14-odd-upstream-fidelity-and-python-retirement.md` L1; the translation is recorded with that authority rather than counted as met, and the entry's remaining open item is the user's ratification of it. The separate reporting duty — an agent announcing delivery complete while its governing record is still active — was verified to be distinct from DEBT-048's ordering scope and is corrected in its own owner by this change, so no duplicate entry was filed. **DEBT-055 and DEBT-046 are untouched**, addressing `cli/aicore`, `system-one` and the `odd-adviser` plugin that this scope excludes, and **DEBT-056 stays open** with a state note recording that its `odd-workflow` subject is resolved while its `cli/aicore` parity corpus and helper files remain.
- L11 — 2026-11-17 — The record inventory, and the closures made on evidence. Fourteen records were `active` before this delivery's record existed. One is now closed on evidence and four more name their open prerequisite; the remaining nine keep open task rows or an existing `Blocked:` entry and are left as they are. **Closed:** `2026-11-17-test-architecture-remediation.md` (PR #195) — `T8` moves from `open` to `done` against the immutable head `f3cc11736fdb695e924f4dc41fc166b8a4febb7d` its `[PASS]` verdict names, the header carries `Status: closed` with a `Closed:` date, and L13 records the delivered scope, the verification, the independent acceptance and the merge proof. `2026-11-17-git-pr-implementation-testing.md` (PR #196) — the earlier uncommitted closure edit had set every task row to `done` and the header to `closed` but left no `Close:` entry, so the record claimed a closure its Log did not evidence and `validate_feature.ts` failed it with `closed feature needs a Log 'Close:' entry`; L12 supplies that evidence, resolves the header's dangling `(see L12)` reference, and corrects the forward-looking closure date to the date the closure is actually recorded, without rewriting L11. **Not closed, with the missing requirement named:** `2026-11-17-implementation-testing-alignment.md` (PR #194) — the pull request's body carries a head-bound `[PASS]` with zero open findings but names no independent reviewer and no submitted GitHub review exists, and five task rows still lack completion evidence; `2026-11-02-ticket-runbook-image-folders.md`, `2026-11-13-independent-skill-utilities-typescript.md` and `2026-11-14-root-contract-suite-retirement.md` — each had all task rows `done` with neither a closure entry nor a `Blocked:` entry, which the closure-consistency rule forbids, so each now names its open prerequisite. The remaining active records — the `odd-adviser` feature, the ODD core simplification, the TypeScript/Vitest migration, the upstream-fidelity and Python retirement, the scoped dependency admission, the project-owned artifacts, DEBT-050, DEBT-051 and the cheapest-test-boundary record — keep open task rows or an existing `Blocked:` entry and are left as they are. `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks` now reports every one of the 29 records `ok`.
- L12 — 2026-11-17 — The independent gates, and the rounds they forced. **Bastion 🧱 (Backend & Scripts Architect)** audited the delivered production changes against C1–C10 and P1–P4 and returned `[PASS]` with zero open findings, confirming that the close-out condition has one owner, that the register's absent-to-empty mapping sits at the infrastructure step, that no application imports infrastructure, that the operation receives its collaborator through the constructor, that the parsers return a domain result rather than an exception the delivery layer converts, and that the five duplicated delivery units now live once in `scripts/cli_delivery.ts` with the divergent units correctly left alone. **Crucible 🔥 (Test Architect)** returned `[FAIL]` on its first round with two MEDIUM and two LOW findings, all now closed: the five `state-header-scalars` cases were placed at T4 because they reach the real, undoubled `yaml` library; the nine `FilesystemFeatureFileSource` cases that re-executed a byte-identical implementation were removed, leaving the one case that proves the distinct port and composition — that removal made the package's real adapter surface smaller than its assembled surface, which the following round then closed honestly by relocating the duplicated CLI assertions to their owning boundary; the inline symptom-register literals moved to a shared factory; and six files holding several behavioural concerns were split by concern. Crucible's own independent analysis confirmed the `git-pr-workflow` blocker was real, and the relocation round closed it at the boundaries that own the behaviour. **Sentinel 🛡️ (Quality Guardian)** audited the ODD lifecycle surfaces and returned `[FAIL]` on round one with four findings — the report rule owned twice with diverging preconditions, the closure-and-merge relation surviving only as list numbering, a durable requirement repeating another, and the compact ready path admitting no precedence over the new clause — all four closed on the same surfaces; its round two returned `[FAIL]` with two further findings, both closed: the compact ready path's `Blockers: none` line is replaced by the outstanding closure prerequisite when one remains, and the record count is corrected. **No exception is recorded anywhere and no repository-wide compliance is claimed.** The three affected packages comply at their own measured boundaries; the repository aggregate still does not, because `cli/aicore`, `system-one` and the `odd-adviser` plugin are outside this scope, and their violations stay visible in the delivered pull-request body.
