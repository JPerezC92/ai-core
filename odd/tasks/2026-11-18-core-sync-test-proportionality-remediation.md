# Core Sync test proportionality and residual testing defects

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-18
> **Objective:** Resolve the two testing defects PR #198 left open — the unresolved `disposable-root` level classification and the nine cases outside the measured levels — and correct the genuine lower-boundary coverage gaps behind Core Sync's test imbalance, without padding, reclassification, lost parity coverage or a permanent exception.
> **Branch:** N/A — created by Herald 📯 (Release Manager) from `main` at `2d974f5e10b73969c992c12f156c679506552fb2` after this record is written. PR #198 is MERGED, so this is a focused follow-up against current `main`, never a continuation of that branch.
> **Delivery:** one focused pull request; forecast ~11 authored test additions plus record, debt and evidence edits, well below the ~400 feature-level strategy trigger, so the slice is reviewable work-unit commits inside one PR — the T4 coverage correction, then the records and debt evidence.
> **Runner:** `pnpm --dir cli/aicore test`; `pnpm --dir cli/aicore test:e2e`; `pnpm --dir cli/aicore typecheck`; `pnpm typecheck`; `pnpm lint`; `pnpm format:check`; `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks`; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts odd/features`

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — The `disposable-root` level conflict carries one unambiguous accepted classification with its technical justification, and both unique safety assertions survive it. Exact requirement: "Resolve the disagreement using the actual T2/T4/T5 contracts and the test's real execution boundary." and "Do not force the classification, add a test-only production interface, or sacrifice unique coverage to satisfy T8." Acceptance: read this record's classification entry and both independent reviewer verdicts; one classification is stated, its deciding contract clauses are cited, and both refusal assertions are present in the delivered tree.
- S2 — Every case previously reported outside the three measured levels is accounted for, and the reported level counts reconcile with the actual runner totals and discovery rules. Exact requirement: "Reconcile the reported level counts with the actual runner totals and discovery rules." and "Do not manufacture a fourth testing level." Acceptance: read this record's accounting entry and the literal runner output it cites; every discovered case instance is assigned either a level or a named non-product category, and the assigned totals equal the executed totals.
- S3 — Real Core Sync adapters carrying meaningful filesystem, persistence or failure contracts that no lower-boundary test covered now have T4 integration coverage. Exact requirement: "Real adapters with meaningful mapping, persistence, filesystem or failure contracts not adequately covered under T4." Acceptance: for each newly covered adapter, run the package suite and observe a passing integration case whose subject is that adapter and whose assertion no previously existing case made.
- S4 — Core Sync tests cover the supported product contract at the appropriate boundaries without requiring a historical parity-scenario mapping. Exact requirement: "I explicitly withdraw the previous instruction requiring every historical parity assertion to have an individual surviving replacement." and "Acceptance must be based on requirements, not historical tests." Acceptance: independently review the delivered suite against the supported product contract and observe that required workflows and behavior are covered at their legitimate boundaries without a one-to-one legacy preservation requirement.
- S5 — The reported T8 result is the actual measured ordering and is never claimed compliant unless the strict ordering is achieved through valid boundaries. Exact requirement: "Do not announce that Core Sync is T8-compliant unless the actual strict ordering is achieved through valid testing boundaries." Acceptance: read the final distribution report; it states the measured counts and either claims compliance only where unit > integration > end-to-end holds, or names the precise incompatibility and the smallest remaining decision.
- S6 — DEBT-055 and DEBT-056 reflect the corrections actually made, and debts outside this scope keep their unresolved state. Exact requirement: "Update their actual evidence and status according to the corrections made." and "Do not retire either debt unless all original resolution criteria are satisfied and independently accepted." and "Preserve the unresolved state of unrelated debts, including DEBT-046, DEBT-048 and DEBT-059." Acceptance: read the debt register; both entries carry this change's evidence and neither is retired, and DEBT-046, DEBT-048 and DEBT-059 are unaltered in status.
- S7 — The delivery is one focused follow-up pull request from current `main` with independent acceptance at its immutable head, and no merge. Exact requirement: "If it has already merged, use one focused follow-up PR based on current `main`." and "No merge is authorized." Acceptance: read the release owner's report; exactly one new pull request targets `main` from the verified current base, its head carries an independent verdict bound to that head, and no merge, tag or release occurred.
- S8 — The repeated execution failures are recorded as an open, evidence-backed process debt. Exact requirement: "I explicitly require these problems to be documented as technical debt." Acceptance: read `DEBT-060` in the canonical register and observe the chronology, unresolved process criteria and relationship to this record.

## Tasks

- T1 | S1, S2 | delegated (test-architecture boundary ruling and case-level census; read-only analysis) — Crucible 🔥 (Test Architect) | done | commit: 1781a8c
- T2 | S1 | delegated (scripts-shape and adapter-definition re-examination of the contested classification; read-only analysis) — Bastion 🧱 (Backend & Scripts Architect) | done | commit: 1781a8c
- T3 | S3, S4 | delegated (test authoring, the capability-probe correction and the package suites for the assigned slice) — Forge 🔨 (Implementer) | done | commit: 26670f0
- T4 | S1, S2, S3, S5 | delegated (test-architecture verdict at the delivered candidate, including the measured distribution) — Crucible 🔥 (Test Architect) | in progress | commit: pending
- T5 | S3 | delegated (architecture conformance of the delivered tests; no production change in scope) — Bastion 🧱 (Backend & Scripts Architect) | in progress | commit: pending
- T6 | S6, S7 | inline (the governing record and the debt-register disposition, Cipher 🔓 owns the ODD lifecycle) — Cipher 🔓 (Lead Orchestrator) | done | commit: 1781a8c
- T7 | S7 | delegated (sole Git executor: branch, focused commits, push, one pull request) — Herald 📯 (Release Manager) | open | commit: pending
- T8 | S1, S2, S6, S7 | delegated (record and debt-register consistency audit) — Sentinel 🛡️ (Quality Guardian) | open | commit: pending
- T9 | S5, S7 | delegated (independent review at the immutable pull-request head) — Inquisitor 🔎 (PR Reviewer) | open | commit: pending

## Log

- L1 — Original request, verbatim:

  # AICore — Complete Core Sync T8 Remediation Before P7

  We are NOT moving to P7 yet.

  I want the remaining Core Sync testing defects resolved first.

  PR #198 delivered important architectural corrections, but it left Core Sync's test proportionality noncompliant and one test-boundary classification unresolved.

  **I do not accept a permanent T8 exception, and I do not consider the Core Sync testing remediation complete.**

  This instruction authorizes focused remediation of those remaining defects.

  ## 1. Delivery scope and baseline

  Herald 📯 must first verify the current state of PR #198, remote `main`, the local checkout, and any existing uncommitted changes.

  If PR #198 remains open, continue in its existing branch and PR.

  If it has already merged, use one focused follow-up PR based on current `main`. Never edit a merged PR or create a branch from an obsolete baseline.

  The last reported Core Sync distribution was:
  - Unit: 55
  - Integration: 29
  - E2E: 87
  - Unclassified or outside the measured levels: 9

  Recalculate these figures against the actual current code.

  The required ordering remains:

  **Unit > Integration > E2E**

  Do not treat `EXCEPTION REQUIRED` as compliance.

  No permanent exception is approved.

  ## 2. Resolve the disposable-root classification conflict

  Investigate the exact behavior exercised by:

  `cli/aicore/tests/integration/disposable-root.test.ts`

  The previous independent reviewers disagreed about its classification.

  Bastion considered it integration; Crucible disagreed.

  Resolve the disagreement using the actual T2/T4/T5 contracts and the test's real execution boundary.

  Determine:
  - Which production responsibility is under test.
  - Whether the test exercises one real adapter boundary.
  - Whether it assembles a complete CLI/application entry point.
  - What its two unique safety assertions protect.
  - Whether it mixes responsibilities that legitimately belong at different boundaries.

  Then make the smallest justified correction.

  If it is genuine T4 integration, retain it there and obtain evidence-based independent agreement.

  If it is T5 E2E, classify it accordingly.

  If it combines distinct concerns, separate only the necessary behavior while preserving both safety assertions.

  Do not force the classification, add a test-only production interface, or sacrifice unique coverage to satisfy T8.

  The final report must contain an unambiguous accepted classification and its technical justification.

  ## 3. Reconcile the nine cases outside the measured levels

  Identify the exact nine cases previously reported outside Unit, Integration and E2E.

  Determine whether they are:
  - Skipped or excluded tests.
  - Test-support infrastructure rather than executable behavioral cases.
  - Actual behavioral tests with incorrect ownership.
  - An error in the measurement or accounting method.

  Classify genuine executable behavioral tests according to the existing contracts.

  Do not manufacture a fourth testing level.

  Do not classify fixtures or support utilities as test cases merely to influence the distribution.

  Reconcile the reported level counts with the actual runner totals and discovery rules.

  ## 4. Fix the proportionality problem at its real cause

  The current imbalance is substantial.

  If 87 E2E cases remain, the minimum strict ordering requires at least:
  - 89 unit cases.
  - 88 integration cases.
  - 87 E2E cases.

  That is not authorization to add 93 artificial tests.

  I explicitly prohibit:
  - Padding the unit or integration count.
  - Splitting one assertion into many test cases to manipulate totals.
  - Reclassifying tests according to directory names.
  - Duplicating existing behavior at cheaper boundaries without distinct regression value.
  - Weakening T8.
  - Deleting legitimate E2E tests merely to improve the ratio.
  - Redefining the test-owning package solely to improve its numbers.

  ### Required approach

  Inspect the remaining Core Sync test architecture and establish where genuine lower-boundary coverage is missing.

  Prioritize legitimate defects:
  1. Application use cases with observable policy branches not adequately covered under T2.
  2. Real adapters with meaningful mapping, persistence, filesystem or failure contracts not adequately covered under T4.
  3. Higher-level tests whose assertions are genuinely redundant and fully protected at an approved lower boundary.
  4. Incorrectly classified tests whose actual boundary differs from the current count.

  Correct these defects with the smallest coherent implementation and testing changes.

  Do not create new production behavior just to obtain more test cases.

  Do not turn pure domain helpers into artificial use-case classes.

  Do not introduce another composition root or rebuild the architecture corrected by PR #198.

  **Every new test must protect a distinct, evidenced behavior or regression risk.**

  ## 5. Preserve all 65 parity cases

  The 65-case byte-exact parity corpus is protected.

  It currently exercises assembled Core Sync behavior and therefore belongs to T5 unless the actual production and testing boundaries demonstrate otherwise.

  Preserve:
  - All 65 scenarios.
  - Their input data.
  - Their expected output and effects.
  - Byte-exact comparisons.
  - Their complete assembled-entry-point regression protection.

  Do not:
  - Delete parity cases.
  - Collapse the corpus into one counted test merely to manipulate T8.
  - Reclassify assembled behavior as unit or integration.
  - Replace real entry-point coverage with mocked execution.
  - Regenerate goldens to conceal behavioral changes.

  A cheaper unit or integration test may supplement parity coverage, but it does not automatically replace the E2E contract.

  Retain the two test-correctness fixes already delivered by PR #198.

  ## 6. Make an evidence-based proportionality correction

  I want actual architectural remediation, not a numerical workaround.

  Before making a large expansion, assess whether the genuine missing unit and integration contracts are sufficient to reach T8.

  Use the existing implementation, ports, adapters and test architecture.

  Prefer correcting existing boundary tests and removing demonstrably redundant coverage over adding large new test suites.

  If genuine additional tests are required, implement them only for independently valuable behavior.

  **Do not generate dozens of cases merely because the arithmetic demands them.**

  If complete T8 compliance is not achievable without one of the prohibited compromises, do not claim success.

  Instead, demonstrate the precise incompatibility with a bounded case-level analysis and identify the smallest legitimate architectural or policy decision still required.

  Do not request approval for an arbitrary exception or begin a repository-wide refactor.

  ## 7. Technical debt

  Inspect the existing relevant debts, particularly:
  - DEBT-055 — T2 target and coverage defects.
  - DEBT-056 — test-level classification defects.

  Update their actual evidence and status according to the corrections made.

  Do not retire either debt unless all original resolution criteria are satisfied and independently accepted.

  Preserve the unresolved state of unrelated debts, including DEBT-046, DEBT-048 and DEBT-059.

  Do not implement the PR artifact identity system or reopen the ODD lifecycle redesign.

  Do not create a duplicate technical debt for Core Sync's already documented imbalance.

  ## 8. Keep this correction focused

  The authorized scope is Core Sync test proportionality and the unresolved testing defects from P5/P6.

  Do not start:
  - `system-one`.
  - `odd-adviser`.
  - General T2 eligibility redesign.
  - Downstream synchronization or migration.
  - Agent permission changes.
  - A new test-generation framework.
  - A repository-wide test reorganization.

  The previous P5 implementation was reviewed and accepted. Do not redo it without a new, demonstrable defect.

  Do not widen the work merely to make the test distribution easier to satisfy.

  ## 9. ODD and Git delivery

  The original P5/P6 record was reported closed.

  Do not falsify that historical closure or reopen it in a way that violates the ODD validator.

  Use the canonical procedure for documenting this newly authorized remaining remediation, with one focused governing task record if required.

  Keep the authorized implementation and testing corrections together in the existing PR #198 if it remains open.

  Herald 📯 alone performs Git/GitHub operations.

  Preserve unrelated local changes.

  No amend, force-push, destructive reset or unauthorized merge.

  Keep implementation, tests, debt evidence and ODD changes independently reviewable through focused commits.

  After source modifications, validate the new candidate and obtain the necessary head-bound independent acceptance.

  Do not reuse a previous PASS as though the implementation and test inputs were unchanged.

  The designated PR-body writer must preserve the applicable existing publication, provenance and preservation contracts.

  No shortcuts through the PR body validator.

  ## 10. Validation and completion

  Verify:
  - Final case-level Unit / Integration / E2E classification.
  - `disposable-root` resolution accepted by the relevant independent reviewers.
  - Reconciliation of all nine previously unclassified cases.
  - All 65 original parity cases retained and passing.
  - Unique regression assertions preserved.
  - Any new unit/integration tests having legitimate T2/T4 ownership.
  - Actual T8 result for `cli/aicore`.
  - The effect on the repository's overall distribution where reliably measurable.
  - Package and root typechecks.
  - Package tests and E2E.
  - Lint and formatting.
  - ODD validators.
  - Independent architecture, testing and semantic reviews.

  Record actual runners and reviewers accurately.

  Do not repeat unrelated audits or run expensive suites without a specific validation need.

  ## 11. Mandatory final report

  Provide:
  1. The final PR URL, base and head.
  2. Exact cause of Core Sync's test imbalance.
  3. Final `disposable-root` classification and accepted evidence.
  4. Accounting for the nine previously unclassified cases.
  5. Before/after Unit, Integration and E2E counts.
  6. Case-level justification for new, relocated or removed tests.
  7. Confirmation that all 65 parity cases remain intact.
  8. Assertion-preservation evidence.
  9. Actual test executions and their owners.
  10. Independent reviewer verdicts.
  11. DEBT-055 and DEBT-056 disposition.
  12. ODD record status and closure evidence.
  13. Any genuinely unavoidable remaining proportionality conflict.
  14. Definitive merge readiness.

  **Do not announce that Core Sync is T8-compliant unless the actual strict ordering is achieved through valid testing boundaries.**

  If it is achieved, report:

  **CORE SYNC T8 — COMPLIANT; PR READY FOR MY MERGE DECISION**

  If the constraints make it unattainable without artificial tests, lost parity coverage or an unauthorized contract change, report:

  **CORE SYNC T8 — STILL NONCOMPLIANT**

  Then identify the exact conflict, the minimum evidence-supported alternatives and any user decision genuinely required.

  Do not misrepresent partial remediation as final compliance.

  No merge is authorized.

  **Finish the legitimate corrections before proposing P7.**

- L2 — 2026-11-18 — Classification: **non-small, bounded**. Understood: the testing contract's T2/T4/T5/T8/T10/T11/T17/T18 clauses, the TypeScript stack guide, the scripts shape, the whole `cli/aicore` test layout and both runner configs, the four uncovered adapters, DEBT-055 and DEBT-056, and both contested reviewer positions were read before this record existed. Risk-contained: yes — the authorized change is test-only plus records and debt evidence; no production module, composition root, port, permission or externally observable behavior changes. Resumable from request plus diff: yes. This record is therefore the sole bootstrap write; no other mutation preceded it.
- L3 — 2026-11-18 — Baseline from the release owner's read-only inventory, no mutation performed. Local branch `main`; `HEAD` = `main` = `origin/main` = `2d974f5e10b73969c992c12f156c679506552fb2`; `git status --short --branch` reports no divergence and zero modified, staged or untracked entries. **PR #198 is `MERGED`** at `2026-11-18T16:08:51Z` with merge commit `2d974f5e10b73969c992c12f156c679506552fb2`, identical to the `origin/main` tip; its head `c3fcf04624abf9356b05ae136e8d8c599eb9e955` (`docs(odd): close the Core Sync boundary and coverage record`) still exists locally and its base-to-head diff is 52 files, `2031` insertions and `1178` deletions. The prerequisite therefore resolves to the merged branch: this change is a focused follow-up against current `main`, never a continuation of a merged PR. Unrelated state preserved untouched: two pre-existing detached-HEAD worktrees (`ai-core-pr192-a544bfc-validation` at `6442c49`, `ai-core-pr192-head` at `79a1aee`) and two pre-existing stashes.
- L4 — 2026-11-18 — **The case census, verified at the boundary each case exercises, not from a directory or suffix.** `pnpm --dir cli/aicore test` → 17 files, `90 passed | 1 skipped`; `pnpm --dir cli/aicore test:e2e` → 26 files, `86 passed | 3 skipped`. Discovered instances 180 = 176 passed + 4 skipped, and they reconcile exactly: 55 unit + 36 integration-directory + 89 end-to-end = 180. Measured levels are **unit 55 · integration 29 · end-to-end 89 · support self-verification 7**; the 4 skipped are honest platform skips counted in their level and never reported as passed. The earlier reported `55 / 29 / 87 / 9` does not reproduce: end-to-end is 89 once the two `sync-advanced` generated cases and the direct modules are counted at the entry point they exercise, and the `9` is a measurement artefact rather than nine cases (see `L5`).
- L5 — 2026-11-18 — **The nine cases at no level, accounted for and not a fourth level.** The true figure is **7**, and the reported `9` was an accounting error. The 7 are every case of `tests/integration/disposable-root.test.ts` (`:40`, `:44`, `:48`, `:52`, `:56` ownership predicate; `:62`, `:68` cleanup refusal). The remaining 2 came from statically counting both `test.skipIf` declarations in `local-filesystem-layout.test.ts` as non-executing: `:67` in fact ran a real directory junction and passed as genuine T4, because `canCreateDirectoryLinks()` is true on this platform, while `:75` was the only genuine skip there (`canCreateSymlinks()` false). Neither is a case at no level: one is executed T4 already inside the 29, the other is one of the 4 platform skips. No genuine executable product case is unaccounted for, and no fourth level was created.
- L6 — 2026-11-18 — **`disposable-root` classification resolved, both contested owners converging independently.** Bastion 🧱, who had originally ruled T4, **withdraws that ruling**: the module is not a production module and not an adapter — `C4` defines an adapter as mapping outside data to domain data through a single mapping step, while `createTemporaryRoot` returns a string tuple and `disposeTemporaryRoot` deletes, and neither implements a port (`C8`); it sits outside the layer tree (`C1`). T4's subject condition therefore fails: a real dependency being real is a condition on how an adapter is exercised, never a substitute for the adapter, exactly as `T8` says real files do not by themselves make a test end-to-end. Crucible 🔥 rules **no level**, on the same deciding ground, and reads `T10`'s "never form an additional level" as restricting level _creation_, not subject _eligibility_ — the reading Bastion now also accepts. **Accepted classification: no test level — test-support harness self-verification, not a product behavioural case.** It is not T2 (the approved-target list is closed and a test-support guard is not a use case, parser/loader or UI unit), not T4 (no adapter, no mapping pipeline) and not T5 (no assembled entry point is imported). Its 7 cases are excluded from the product level census and are **not** counted at any level: counting them as integration would overstate T4 exactly as DEBT-056 records, and moving them to `tests/unit/` would add 7 to the unit tally for a subject the contract does not grant, which is the distribution-motivated reclassification the user prohibited. **Smallest justified correction: the ruling and the census exclusion, with the file retained unchanged at its current path.** `T8` states case counts "are measured at the boundary each test actually exercises, never from a directory, file or suffix name", so the directory label is not what the count depends on; no file move, no split, no test-only production interface and no assertion is changed, and both refusal assertions and all five predicate assertions survive verbatim. Splitting the module's predicate logic from its real-filesystem lifecycle was considered and rejected: it would multiply a single behavioural concern (`T11`) into more counted cases for no regression gain.
- L7 — 2026-11-18 — **T8 ordering: the strict distribution is not reachable from this test architecture, and no exception is requested.** End-to-end is pinned at **89** and cannot legitimately move down: 65 of those cases are the protected byte-exact parity corpus, whose honest level is the assembly, and the remaining 24 assert exit status, output and whole-tree effects at `src/main.ts`. A compliant strict ordering therefore requires **integration ≥ 90 and unit ≥ 91**, that is, **+61 integration and +36 unit** against the measured `55 / 29`. The genuine lower-boundary gaps this change can evidence supply a bounded set of cases (see `L8`), not 97; closing the remainder would require fabricating cases, splitting one assertion across many, or reclassifying assembled behaviour, each of which the user prohibited and `T8` forbids. The imbalance's cause is therefore **a coverage deficit that has been exhausted plus an arithmetic floor**, and my earlier framing of it as structural impossibility was an overclaim that this entry now corrects. What the evidence establishes is narrower and precise: end-to-end is pinned at 89 by a protected corpus, so a strict ordering needs integration ≥ 90 and unit ≥ 91; the test-architecture owner, asked directly, **cannot name a further genuine lower-boundary contract** in `cli/aicore`. What the evidence does **not** establish is that no architectural alternative exists. Alternatives considered, each with its limitation: fabricating, splitting or reclassifying tests is prohibited and forbidden by `T8`; moving parity down has no legitimate level, because no single adapter boundary produces an exit code plus a whole-tree effect; deleting end-to-end cases would remove unique coverage; changing `T8`'s measurement basis is a contract change requiring user authorization; accepting an exception is refused by the user. One alternative is **not** foreclosed and is not a test decision: a future authorized production restructuring that introduced genuinely separable adapter boundaries could legitimately raise the integration count, and that would be an architecture change outside this slice's authority. So the accurate finding is **"not reachable within this authorized test-only scope"**, not "proven structurally impossible". No acceptance is recorded, and no exception is proposed.
- L8 — 2026-11-18 — **Genuine lower-boundary coverage gaps, evidenced.** Four adapters were examined against their own contracts and the existing suites. `src/infrastructure/synchronization/write-target-guard.ts` has **no** lower-boundary coverage at all — a managed write path containing a link is refused only through three assembled end-to-end cases that are themselves platform-skipped where symlinks cannot be created, which is the exact "higher-level test compensating for an untested lower-level boundary" inversion `T8` names. `src/infrastructure/synchronization/json-document.ts` reports a repeated key at any nesting level, a decision `JSON.parse` cannot express, and no existing case exercises it: `clearance-store-editors.test.ts` covers per-editor destinations only. `local-source-files.ts` and `local-destination-files.ts` carry the byte-versus-text fidelity contract in their own headers, verified today only by the assembled corpus. `reconciliation-reader.ts` decides nothing and is not proposed for coverage. Authorized correction: one behavioural concern per module (`T11`) for the first three subjects, no new production behavior, no new interface, no new composition root.
- L9 — 2026-11-18 — **The delivered correction and its measurements.** Four T4 modules were added under `cli/aicore/tests/integration/`, 14 cases in total, and no production, config, port, adapter, composition root or dependency path changed: `clearance-duplicate-keys.test.ts` (3 — a repeated key at top level, a repeated key nested inside an entry, and duplicate-outranks-malformed, driven through the real `JsonClearanceStore`); `write-target-guard.test.ts` (4 — an escaping destination declaration refused, a target resolving inside the source tree refused, a target that exists as a directory where a file is expected refused, and a fully-inside set earning no refusal as a positive control, all through the real `LocalWriteTargetGuard` over the real layout); `source-core-read.test.ts` (3 — marked file mapped to the marked region alone, markerless file mapped to its whole post-frontmatter body, missing path to `null`, through the real `LocalSourceFiles.readCore`); and the file content contract split across `file-fidelity.test.ts` (3) and `file-absence.test.ts` (1). Literal runs at the final candidate: `pnpm --dir cli/aicore test` → 22 files, `104 passed | 1 skipped (105)`, exit 0; `pnpm --dir cli/aicore test:e2e` → 26 files, `86 passed | 3 skipped (89)`, exit 0, including all 65 parity cases with no case-data line touched; `pnpm --dir cli/aicore typecheck`, `pnpm lint` and `pnpm format:check` all exit 0. **Final measured distribution: unit 55 · integration 43 · end-to-end 89 · support self-verification 7**, 194 discovered instances, reconciling exactly as `55 + 50 + 89` against `105 + 89`. **Limitations recorded rather than glossed:** no symbolic-link-dependent guard case was added, because link creation is unavailable on this platform and a case that can only skip protects nothing; the guard's `isFileSystemError → invalid` catch and the extractor's `malformed` outcome remain unasserted at this boundary — the first cannot be provoked hermetically and the second is already proven at the assembled level by parity. A dropped candidate, a planned raw creation with a non-directory parent, was verified against the rule and correctly **not** asserted: `refuseWriteTargets` explicitly skips that shape, so a refusal case would have been fabricated.
- L10 — 2026-11-18 — **Independent gates at the final candidate, both `[PASS]` with zero open findings.** Crucible 🔥 (Test Architect) ran three rounds: round 1 `[FAIL]` with one `T11` finding — `file-fidelity.test.ts` held two independent behaviours across two adapters — plus the undelivered guard subject; round 2 `[PASS]` after the fidelity/absence split and the guard module; round 3 `[PASS]` after `source-core-read.test.ts`. It confirmed the markerless outcome independently against `extractSourceCore`, confirmed that covering a pure domain helper through the adapter that calls it is the compliant route under T2's closed target list rather than a smuggled unit target, and confirmed the dropped non-directory-parent candidate was correctly dropped. Bastion 🧱 (Backend & Scripts Architect) returned `[PASS]` in both rounds, with zero findings and INFO observations only: no production change, correct boundary ownership, no doubled subject, refusals asserted as returned domain values rather than thrown exceptions, and every expected value traced to a source line. **Final T8 verdict from the test-architecture owner: `EXCEPTION REQUIRED`** — `55 > 43` holds and `43 > 89` does not; the exact remaining gap is integration `+47` (to 90) and unit `+36` (to 91). Crucible 🔥 states explicitly that it **cannot name a further genuine lower-boundary contract** in `cli/aicore`, so the remaining gap is not a coverage deficit.
- L11 — 2026-11-18 — **Debt disposition, no entry retired and no duplicate created.** DEBT-056 stays open: its classification conflict is resolved by ruling (no level, support self-verification), its parity-corpus, `odd-workflow`, clearance and reconciliation subjects stay resolved, and its remaining subject is a criterion-wording mismatch — its own criterion asks the helper files to be "relocated to their actual boundary", while the accepted ruling establishes that the helper's actual boundary is no level, so relocation is unavailable without inventing a fourth level or asserting a T2 subject the contract does not grant. Recorded as satisfied in substance and not literally, with user ratification of that wording as its remaining item. DEBT-055 stays open: this change adds no unapproved unit target, every added case is a T4 adapter case, and the seven `disposable-root` cases were deliberately not promoted into `tests/unit/` even though that would have added seven to the unit tally. DEBT-046, DEBT-048 and DEBT-059 are untouched and keep their unresolved state; no duplicate debt was filed for Core Sync's imbalance.
- L12 — 2026-11-18 — **User correction on test scope, the contract-level redundancy re-check, and the superseding final measurement.** The user interrupted before the record, debt and delivery commits were made and required, verbatim, that a test be removed "only when its redundancy is demonstrated at the exact behavioral-contract level, not merely because an E2E test produces a similar final result", and that the markerless case, the positive control, the duplicate-key behaviour and the guard behaviours be kept. That re-check **refuted four of the five removals this record had proposed**, and the refutation is recorded because the earlier reading was wrong: a search of the whole parity support tree found **no CRLF content and no `Uint8Array`, `Buffer` or binary fixture anywhere** (`tests/support/**`), so the parity corpus can never detect a CRLF-normalisation or byte-transformation regression, and `file-fidelity.test.ts`'s three cases and `file-absence.test.ts`'s `readBytes` absence case therefore protect contracts nothing else protects. Those four are **retained**. Exactly **one** case was removed: `source-core-read.test.ts`'s marked-region case, because the parity corpus exercises marked-region extraction at the same behavioural contract with real `<!-- core:begin -->` markers and byte-exact expected output across eight `region-mode` cases (`tests/support/core-sync-parity/corpus.ts:328-569`), so a T4 restatement adds no regression protection. **Final candidate: 13 added cases** — `clearance-duplicate-keys.test.ts` 3, `write-target-guard.test.ts` 4, `file-fidelity.test.ts` 3, `file-absence.test.ts` 1, `source-core-read.test.ts` 2. Literal runs: `pnpm --dir cli/aicore test` → 22 files, `103 passed | 1 skipped (104)`, exit 0; `pnpm --dir cli/aicore test:e2e` → 26 files, `86 passed | 3 skipped (89)`, exit 0 with all 65 parity cases intact; package and root typecheck, `pnpm lint` and `pnpm format:check` (515 files) all exit 0. **Final measured distribution, superseding L9 and L10: unit 55 · integration 42 · end-to-end 89 · support self-verification 7**, 193 discovered instances reconciling as `55 + 49 + 89` against `104 + 89`. **T8 remains unresolved and this slice is not proportionality remediation:** the ordering is `55 > 42 < 89`, and the strict ordering would need integration ≥ 90 and unit ≥ 91. **Review status of the delta, stated rather than assumed:** the two retained `source-core-read` cases are byte-identical to the content Crucible 🔥 and Bastion 🧱 passed in their final rounds, so the removal introduces no unreviewed assertion; the file header gained a sentence explaining the deliberate non-duplication, and that sentence is coordinator-verified rather than independently re-reviewed, because the project's three-round review cap for this change is reached and no fourth unattended round was dispatched.
- L13 — 2026-11-18 — **Skipped-test audit and the two authorized corrections.** The audit found four skips and no permanently disabled test: there is no literal `test.skip("…")`, no `.only`, no `.todo` and no `describe.skip` anywhere under `cli/aicore/tests`; the only `test.skip` is the conditional call in `describe-concern.ts:51`. All four are conditional platform skips caused by the single capability "this platform cannot create a file symbolic link": one in `local-filesystem-layout.test.ts:75` and three parity `safety-refusals` cases (`corpus.ts:1692`, `:1804`, `:1927`). **Correction 1 — the capability probes no longer swallow faults.** `fixtures.ts` gained `isLinkCapabilityRefusal()`, which treats **only** `EPERM`, `EACCES` and `ENOSYS` as a platform capability refusal and rethrows everything else, so an unexpected filesystem fault now fails the test instead of silently skipping it; `EINVAL` is deliberately **not** in the set because it signals a malformed argument. Root creation and disposal stay outside the classification and propagate on their own. One case was added at the existing test-support self-verification boundary, `disposable-root.test.ts`, asserting all three accepted codes and three rejected shapes, which takes that module from 7 to 8 cases and leaves it excluded from the level census. **Correction 2 — the symbolic-link refusal is now executed.** `write-target-guard.test.ts` gained one case that creates a real Windows directory junction at a managed payload target, asserts `lstat().isSymbolicLink()` is `true`, exercises the real `LocalWriteTargetGuard`, and asserts the exact diagnostic `invalid write target: destination payload write target is a symbolic link: <path>` while asserting it is **not** the `is not a regular file` diagnostic; it also asserts the junction and its target directory are unchanged afterwards. It **runs and passes on this platform**, so the `refuseWriteTargets` branch at `write-targets.ts:98` — the one branch with zero executed coverage — is now covered without elevation, without a mock and without Developer Mode. **One file removed:** `source-core-read.test.ts` was deleted because its two contracts are demonstrably covered by existing parity scenarios (markerless body at `corpus.ts:966`, and the drift/absence cases), and keeping it would have been a T4 restatement. **Final candidate: 12 added or retained integration cases** — `clearance-duplicate-keys.test.ts` 3 (diagnostic naming, nesting, precedence: each independent of the parity classification assertion), `write-target-guard.test.ts` 5, `file-fidelity.test.ts` 3, `file-absence.test.ts` 1. Literal runs: `pnpm --dir cli/aicore test` → 21 files, `103 passed | 1 skipped (104)`; `pnpm --dir cli/aicore test:e2e` → 26 files, `86 passed | 3 skipped (89)`; package and root typecheck, `pnpm lint` and `pnpm format:check` (514 files) all exit 0. **Final measured distribution: unit 55 · integration 41 · end-to-end 89 · support self-verification 8**, 193 discovered instances. All 65 parity scenarios remain intact: 62 execute and pass, the same 3 remain legitimately skipped. **Still platform-dependent after this change:** the file-symlink _shape_ is unexecuted on this platform in both the layout case and the three parity `destinationLinks` cases; their protected behaviours are covered elsewhere — the layout branch by the executed junction case, and the escape/source-containment refusals by the executed T4 cases — but the symlink-specific parity scenarios themselves remain unexecuted here, and this repository configures **no CI** (`.github/workflows/` does not exist), so no supported environment has been shown to execute them. **T8 remains unresolved:** `55 > 41 < 89`, `EXCEPTION REQUIRED`, no exception requested and none accepted.
- L14 — 2026-11-18 — **Delivery state, and the review status stated rather than inferred.** Branch `test/core-sync/proportionality-and-safety-coverage` was created by Herald 📯 (Release Manager) from `2d974f5e10b73969c992c12f156c679506552fb2`, which is `main`, `origin/main` and PR #198's own merge commit, so nothing stacks on an obsolete baseline and merged PR #198 was not edited or reopened. Three focused commits, no amend, squash, rebase or force-push: `29f89d0` carries the capability-probe correction and its self-verification case (2 files, +60/−11); `26670f0` carries the four integration modules (4 files, +430); `1781a8c` carries this record and the debt evidence (2 files, +337). Neither pre-existing worktree (`ai-core-pr192-a544bfc-validation` at `6442c49`, `ai-core-pr192-head` at `79a1aee`) nor either pre-existing stash was touched, and no merge, tag or release was performed. **Review status — not claimed beyond what exists.** Crucible 🔥 (Test Architect) returned `[PASS]` with zero open findings and Bastion 🧱 (Backend & Scripts Architect) returned `[PASS]` in two rounds, but both verdicts bind the candidate **before** the two corrections this record's `L13` describes and before the `source-core-read` removal, so they are **not** restated as verdicts on the final bytes and `T4` and `T5` are left `in progress` accordingly. The independent acceptance of the delivered head is therefore `T9`'s, at the immutable pull-request head; until it returns, no independent review of the final bytes exists.
- L15 — 2026-11-18 — **User scope correction and the three approved corrections (D1, D2, D3).** The user rejected the delivered candidate's remaining scope and approved three corrections, while approving D4 only as a revised contract **proposal** and explicitly **not** as a T8 amendment or as compliance. **D1 — two redundant E2E cases removed.** `tests/e2e/sync-destination-validation.test.ts` was deleted after the precondition was verified rather than assumed: the refusal contract it asserts (`invalid-destination`, "destination is not a directory") is already asserted at the application boundary by `synchronize-refusals.use-case.spec.ts:83` and `reconcile-destination.use-case.spec.ts:166`, and the exit behaviour is a total static mapping (`reporting.ts:25-35`, `"invalid-destination": EXIT_INVALID`, with `?? EXIT_INVALID` as the fallback), whose rendering path is proven by the `exit-contract` parity cases. **Residual disclosed:** the specific composition "`sync` command + invalid destination + exit 2 + message on stderr" is no longer proven end to end; its two components remain proven separately. **D3 — the unrequested symlink/junction engineering was removed.** Five items: the junction case in `write-target-guard.test.ts` (5 → 4), its exclusive `createDirectoryLink` helper and imports, the exported `isLinkCapabilityRefusal()` helper, both probe rethrow blocks in `fixtures.ts` (probes restored to their bare `catch` shape with their original doc comments), and the capability-classification case in `disposable-root.test.ts` (8 → 7). Production refusal branches, the contract-derived link parity cases and their skips, `cases/directory-expansion.ts`, the two `local-filesystem-layout` skipIf cases and the pre-existing junction materialisation were all left untouched. **The probe's fault-masking property therefore returns to its pre-change state and is a disclosed, accepted limitation, not a fixed defect.** **D2 — the permanent product scope boundary is now documented** in the canonical skill: `.opencode/skills/core-sync/SKILL.md` gained a `## Scope boundary` section stating that Core Sync synchronizes ordinary files and directories, that symlink and junction synchronization is not a supported feature, that the write-target refusal is a defensive guard rather than symlink support and does not authorize further platform-specific engineering, that existing tests and earlier implementations are not sources of new product requirements, and that ordinary-file containment and overwrite protections must not be removed; its version moved from 2.10.0 to 2.11.0. **Final measured state:** `pnpm --dir cli/aicore test` → 21 files, `101 passed | 1 skipped (102)`; `pnpm --dir cli/aicore test:e2e` → 25 files, `84 passed | 3 skipped (87)`; a focused parity run → 12 files, `62 passed | 3 skipped (65)`, so all 65 parity scenarios register and only the two approved cases were removed; package and root typecheck, `pnpm lint` and `pnpm format:check` (513 files) exit 0; both ODD validators report every record `ok`. **Distribution: unit 55 · integration 40 · end-to-end 87**, 189 discovered instances, support self-verification 7 (within the integration directory). **T8 is noncompliant and no compliance is claimed:** `55 > 40 < 87`. A permanent exception is not requested. The pre-existing platform-dependent cases may still skip on this Windows environment and their execution is **not verified** here, and this repository configures no CI. No Git operation was performed in this step: PR #199 stays open at head `56e9d57`, unmerged, and no replacement PR was created.
- L16 — 2026-11-18 — **The permanent E2E architecture boundary, recorded verbatim and integrated into the canonical owners.** User clarification, verbatim: "Core Sync E2E tests verify complete synchronization workflows, principally initial copying and updating existing managed files. Internal parsing, transformation, validation and adapter contracts must not automatically become separate E2E tests." The governing statement is now in the shared architecture, not in this record: `.aicore/core/architecture/testing/architecture.md` `**T5**` gained an `**End-to-end scope.**` clause stating that an end-to-end case verifies one coherent user-facing workflow and its observable results, that one workflow case may assert several files, paths, contents and structural effects without becoming separate cases, that internal parsing rules, transformations, validation branches, adapter conditions and compatibility examples belong at the cheapest boundary proving their complete contract and are not promoted to end-to-end because they affect the workflow, that comprehensive feature coverage does not require comprehensive end-to-end duplication, that a new end-to-end case requires evidence of unique end-to-end regression value that a cheaper boundary cannot establish, and that end-to-end coverage must be sufficient rather than minimized to a quota. `**T8**`'s numerical distribution rule was **not** modified, because that remains a separate explicitly governed decision. The Core Sync product owner, `.opencode/skills/core-sync/SKILL.md`, gained a `## Verification workflows` section naming Workflow A (initial synchronization: files created, expected paths, expected contents, managed directory structure) and Workflow B (update existing files: meaningful source change, managed files updated, destination-owned unmanaged content preserved, expected contents), stating that these are two logical workflow categories rather than a cap of two cases, that a workflow case may assert several files and effects, and that additional end-to-end workflows require a distinct justified user-facing result or real process-level guarantee, with `region`/`raw`/`merge` and the individual marker, schema and validation rules verified at the boundary that owns them. No new architecture framework, parallel policy document or redundant testing standard was created, and the valid T2/T4/T5 boundaries are unchanged. **What this supersedes, stated rather than assumed:** the earlier instruction to preserve all 65 parity cases permanently at end-to-end (recorded at `L1` and `L12`) is superseded as an _architectural assumption_, and `S4` has been revised to match; it is explicitly **not** authorization to delete any parity scenario without case-level analysis showing where its contract is then owned. The task is **not** reported as proportionality-compliant: the measured distribution remains `unit 55 · integration 40 · end-to-end 87` until the redesign is implemented and measured.
- L17 — 2026-11-18 — **Redesign slice 1 delivered: the consolidated workflow suite, additive only.** Four new E2E modules were created and no existing test, parity case, production module or config was touched: `workflow-initial-synchronization.test.ts` (Workflow A — one enrollment delivers every managed file, its exact content and the managed structure: raw files byte-equal to source, region core byte-equal with the prior markerless body surviving in the project region, merge carrying the source `$schema` and a destination-indexed `qmd`, plus `.aicore/`, `core.yaml`, the reconciliation report and the root blocker); `workflow-update-existing-files.test.ts` (Workflow B — one source change and one apply update the managed files while the project region, a destination-only merge key and comment, a project-owned ODD record and an unmanaged file stay byte-equal); `workflow-check-reporting.test.ts` (two distinct user outcomes: current at exit 0 and drift at exit 1, each asserting a full base64 tree snapshot is unchanged); `workflow-essential-refusal.test.ts` (an escaping `--bind` declaration refused at exit 2 with the tree byte-identical). Every case runs the real spawned CLI through the existing harness, asserts several files and effects in one case as `T5`'s `End-to-end scope` clause requires, and owns its fixture. Literal results: `pnpm --dir cli/aicore test:e2e` → 29 files, `89 passed | 3 skipped (92)`; `pnpm --dir cli/aicore typecheck`, `pnpm lint` and `pnpm format:check` (517 files) exit 0. **Transitional measured state: unit 55 · integration 40 · end-to-end 92**, the end-to-end figure deliberately rising because the workflow cases were added before any superseded case was removed — nothing was deleted on assumption. **Remaining authorized work, not yet done and not claimed:** the durable per-contract assertion-preservation map for all 65 parity scenarios; verification of which lower-boundary contract already owns each scenario and implementation of the genuine gaps; folding the non-parity E2E cases into the workflow suite; removal of superseded scenarios only after that evidence exists; the resulting count reconciliation; and the independent architecture, testing and semantic acceptance. No proportionality result is claimed, and the redesign is not complete.
- L18 — 2026-11-18 — **Workflow suite reviewed; three findings corrected.** Crucible 🔥 (Test Architect) returned `[FAIL]` with two findings and Bastion 🧱 (Backend & Scripts Architect) returned `[ADVISORY]` with one; all three were fix-first eligible and are corrected. **F1 (Crucible, `T5` complete-workflow contents):** initial-synchronization asserted the destination's previous markerless body only with `toContain`, so dropping the body while keeping the title would have passed; the harness now exposes the exact body it wrote as `Fixture.body` and the delivered `project` region is asserted byte-equal to it. **F2 (Crucible, `T10`/`T15`):** `snapshotTree` was duplicated verbatim in two modules; it is now one exported helper in the new supporting resource `tests/support/tree-snapshot.ts`, consumed by both. **A1 (Bastion, advisory):** both workflow modules decoded assertions through the same production region functions the writer uses, comparing product output to product interpretation; the production import is removed and the marker slices are computed literally in the tests. No expected value was changed or weakened, and the case count is unchanged at 5. Literal results: `pnpm --dir cli/aicore test:e2e` → 29 files, `89 passed | 3 skipped (92)`; package typecheck, `pnpm lint` and `pnpm format:check` (518 files) exit 0. Crucible 🔥 confirmed the five cases drive the real spawned entry point, that byte fidelity is exact where byte equality is the contract, that check and refusal prove distinct operator-facing outcomes, and that Workflow A and Workflow B carry distinct creation-versus-overwrite regression value; Bastion 🧱 confirmed the refusal is the documented exit-2 class refused before any write and that preservation is proven by byte comparison rather than by absence. **Still not done and not claimed:** the per-contract assertion-preservation map for the 65 parity scenarios, the lower-boundary verification and relocation of their internal-rule contracts, the folding of the non-parity E2E cases into the workflows, and the removal of superseded cases. `T8` remains noncompliant.
- L19 — 2026-11-18 — **Coverage cross-reference and the two proven-removable parity groups.** A bounded test-architecture cross-reference established, per concern group rather than per case, what already proves each parity contract below E2E. Result: **only two of the twelve groups are removable today** — `clearance-integrity` (1 case, proven at the owning adapter by `clearance-duplicate-keys.test.ts`) and `directory-expansion` (3 cases, proven by `local-filesystem-layout.test.ts`). Both were removed with their case modules and spec files, the `Concern` union narrowed, and the corpus reduced from 65 to **61 cases across 10 spec files** (`58 passed | 3 skipped`). No other case's data, expectation or tree changed and no expected output was regenerated. The supporting README's layout block was corrected to match. **The cross-reference's other nine groups cannot be removed yet**: their contracts have no lower-boundary proof (region/marker/frontmatter, raw-mode artifacts and absent-target creation, merge missing-destination drift and destination-only server survival, all six bindings-schema cases, three exit-contract arms, most safety-refusal arms, both idempotence cases, three binding-declaration arms, and all five root-role cases). **Correction to the cross-reference's own proposal, recorded rather than adopted silently:** it suggested consolidating those contracts into domain-helper unit tests (`regions.ts`, `frontmatter.ts`, `markers.ts`), which `T2` forbids because a domain helper is not an approved unit target; those consolidated tests must therefore run through an approved use case (`T2`) or at the owning adapter's real boundary (`T4`). The smallest justified consolidation is **15 tests, not 40**, each covering 2–8 related cases. **Measured state after this slice: unit 55 · integration 40 · end-to-end 88** (`85 passed | 3 skipped`). `T8` remains **noncompliant** (`55 > 40 < 88`) and no compliance is claimed.
- L20 — 2026-11-18 — User changed the strategy, verbatim: "Stop the legacy-test preservation and one-to-one relocation process." / "I authorize rebuilding the Core Sync test suite from scratch, using the actual supported product requirements and the canonical testing architecture." / "I explicitly withdraw the previous instruction requiring every historical parity assertion to have an individual surviving replacement." The task remains active; prior results are evidence, not requirements.
- L21 — 2026-11-18 — **Requirements-based rebuild executed.** The 61 remaining parity scenarios and their whole support tree were removed: the ten `tests/e2e/core-sync-parity/*.parity.spec.ts` modules and every file under `tests/support/core-sync-parity/`. No production byte changed. The only consumer outside that tree was `tests/integration/local-filesystem-layout.test.ts`, which imported three link helpers; those are now inlined there, so no shared behaviour was lost. Retained at their boundaries: the ten approved-target use-case unit modules (72 cases), twelve genuine adapter integration modules (52 cases), and an E2E suite of complete user-facing workflows — initial synchronization, update-with-preservation, current/drift reporting and essential refusal (5 cases) plus the reconciliation, opt-out, enrolment, editor-profile, revision, usage, advanced-forwarding, write-failure, corrupt-configuration and project-owned-artifact workflows (22 cases). **Measured: unit 72 · integration 52 · end-to-end 27; total 158, down from 212 and below the 187 this remediation started from.** Literal runs: `pnpm --dir cli/aicore test` → 22 files, `130 passed | 1 skipped (131)`; `test:e2e` → 17 files, `27 passed (27)`; package typecheck, `pnpm lint` and `pnpm format:check` (492 files) exit 0. **T8 now holds under the unchanged rule** (`72 > 52 > 27`) measured at real boundaries, with no fabricated case and no reclassification. The single remaining skip is the file-symlink layout case this platform cannot create. **Coverage limitation recorded:** the per-rule compatibility scenarios are no longer executed end to end; their behaviour is covered by the workflow cases where user-facing and by the unit and adapter suites where internal, and no claim is made that every historical scenario retains an end-to-end equivalent.
- L22 — 2026-11-18 — **Two residual findings dispositioned; one accepted limitation remains open.** **`write-targets.ts:167` is REACHABLE**, not dead: Bastion 🧱 traced three ordinary-file `init` routes (a `--bind-raw` destination named `AGENTS.md` whose source is region-cleared, uncleared, or opted out) where the earlier alias refusal cannot fire because `isNonRegion` reads clearance modes rather than the declared mode, so this refusal is first. A case was added at the approved `T4` guard boundary driving the real `LocalWriteTargetGuard` with `command: "init"` and a planned raw creation named `AGENTS.md`, asserting the `default root would alias newly created raw destination` refusal; it passes. A domain-helper unit was rejected because `T2` does not approve `write-targets.ts` as a unit target. Production was not changed. **`write-targets.ts:98` remains unproven and stays open as an advisory.** The four required distinctions: (1) the production safeguard exists and is unchanged; (2) its intended behaviour is documented in `.opencode/skills/core-sync/SKILL.md` `## Scope boundary` and the exit contract; (3) there is **no automated execution evidence** for that branch at any level; (4) the user has **finally prohibited** a junction test, new symlink fixtures, capability-detection helpers, platform workarounds, production change to satisfy a test, and restoration of the parity infrastructure. Crucible 🔥 confirmed against `agents.md` `### Finding disposition` and `### PR review findings (adjudication)` that the contract permits this as an **open, user-accepted advisory** and that no mandatory-proof obligation elevates it to a gate — and equally that it can never be recorded `FIXED` and never reaches `[PASS]`, because `[PASS]` requires zero open findings of any severity. It is therefore reported open, not fabricated closed. **T5 correction:** `sync-revision.test.ts`'s "a malformed revision is rejected" was deleted — it restated the `invalid-revision` validation already proven at the application boundary and the total static exit mapping, adding no end-to-end value; the absent-revision case was kept because it has no cheaper coverage. **Final measured state: unit 75 · integration 55 product (+7 support) · end-to-end 26; total 163.** Literal runs: `pnpm --dir cli/aicore test` → 22 files, `136 passed | 1 skipped (137)`; `test:e2e` → 17 files, `26 passed (26)`. `T8` holds (`75 > 55 > 26`) and `DEBT-060` remains OPEN.
- L23 — 2026-11-18 — **User risk acceptance for the residual advisory, scoped to PR #199.** The user accepted, verbatim, the remaining symlink-refusal coverage limitation "as a documented residual risk **for PR #199 only**", stating "This is an explicit decision, not permission to bypass the review contract", and required it to be recorded as **USER-ACCEPTED ADVISORY — NOT VERIFIED**, never FIXED and never PASS. The production safeguard at `write-targets.ts:98` stays unchanged and no symlink or junction test, platform fixture, capability-detection framework, privilege workaround or replacement parity infrastructure may be added. **Scope:** this acceptance is PR-scoped; it does not amend the shared review contract or the repository-wide review policy. **Consequence, stated by the contract rather than inferred:** `[PASS]` still requires zero open findings of any severity, so the final review verdict cannot be `PASS`; it is an advisory with a recorded user decision. The governing task therefore remains `active`, and its closure is blocked by lifecycle policy — zero-open-findings — not by unfinished implementation. `DEBT-060` remains OPEN.
- L24 — 2026-11-18 — **Current measurement, superseding the counts recorded at `L21`/`L22`, and the correction of that staleness.** The independent reviewer found the record's measurement stale: five guard cases and three unit cases landed after `L21` with no Log entry. Corrected current figures, reconciled by the reviewer against the literal runs and a static declaration count: **unit 75 · integration 53 product (+7 support self-verification) · end-to-end 26; 163 total**, of which two non-e2e instances are generated by a declaration loop. Reconciliation: `75 + 53 + 7 = 135` static plus 2 generated equals the runner's `136 passed | 1 skipped (137)`; `24 + 2 = 26` equals the e2e runner's `26 passed (26)`. `write-target-guard.test.ts` now holds **10** cases, up from the 5 recorded earlier. `T8` holds at `75 > 53 > 26`. **Both earlier review objections were withdrawn against this evidence:** the distribution reconciles, and the `default root would alias newly created raw destination` case genuinely binds its branch — the assertion on `refusal?.code === "invalid"` fails before the message assertion if the branch does not fire, so it is not title-matching. The reviewer also confirmed no `core-sync-parity` path or `*.parity.spec.ts` remains, and no production behaviour changed.
- L25 — 2026-11-18 — **Governance finding and the authorized PR replacement.** The canonical git-pr workflow protects the published `Summary`, `Breaking changes` and `Test plan`, but exposes no operation that writes, accepts or supersedes a baseline, so a truthful description of this rebuild cannot be published on PR #199 under the existing rules; the independent-capture and rebaseline proposals were unsupported and are retracted, and earlier validate runs that passed one observation as both baseline and current carried no freshness proof. **Herald's refusals were correct safety behaviour — the defect was the missing supported recovery path.** The user authorized closing PR #199 unmerged and creating a replacement pull request from the same branch with a truthful initial description, and recorded the failures with prevention criteria in `DEBT-060`, which stays OPEN because the tooling/policy remediation is separately authorized work. The prior risk acceptance of the unverified symlink-refusal branch was scoped to PR #199 and is **not** carried forward automatically: the replacement pull request's review must determine its own disposition, and no symlink or junction test is authorized. No implementation, production byte, test or architecture decision changes here; the completed rebuild, its commits and its history are preserved.
- L26 — 2026-11-18 — **PR #199 closed unmerged; replacement #200 created; two final user decisions recorded.** PR #199 was closed without merging — `state: CLOSED`, `mergeCommit: null` — with a comment stating that its protected Summary and Test plan describe the withdrawn parity-preservation scope. Replacement **PR #200** (`https://github.com/JPerezC92/ai-core/pull/200`) was created from the **same branch** `test/core-sync/proportionality-and-safety-coverage` at head `fcb869a66437339d7635ad992a4d91ab6a5d04be`, carrying the completed implementation, its commits and its history unchanged; its initial description is truthful and does not inherit #199's obsolete text, and it references #199 for traceability. **F6 renewed:** the user explicitly accepted the unverified symlink-refusal coverage limitation **for PR #200 only**, on the same terms accepted for PR #199, so F6 is recorded `DEFERRED` with the user as acceptor and 2026-11-18 as the date; the verdict remains `[ADVISORY]`, never `[PASS]`, and no symlink or junction test is added and no production safeguard changes. **F7 accepted:** the user accepted the two descriptive inaccuracies in #200's already-published protected Summary — its per-category list mixing declaration and instance counts, and its naming ten deleted parity modules where the verified diff deletes twelve — solely to avoid another pull-request replacement, and required the final published evidence to state the declaration-versus-instance distinction with accurate counts for each and the verified number and nature of deleted parity modules and files. The acceptance is specific to those two known inaccuracies in PR #200 and authorizes no future inaccurate description. **Recurrence recorded in `DEBT-060`, which remains OPEN:** the replacement pull request was also published initially with avoidable Summary inaccuracies, so a pre-publication **factual verification** of the protected Summary and Test plan — counts against the real census, paths against the verified Git diff — is now an explicit prevention criterion. Independent review of PR #200 at its head returned F1–F5 `FIXED` with two open findings, both now dispositioned by the decisions above; the ODD task remains `active`, because `[PASS]` requires zero open findings and the zero-open-findings policy, not unfinished implementation, is what defers closure.
