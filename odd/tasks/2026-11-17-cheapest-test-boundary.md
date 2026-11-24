# Cheapest proving test boundary

> **Status:** closed
> **Closed:** 2026-11-24
> **Disposition:** cancelled
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-17
> **Objective:** Simplify expensive git-pr-workflow and Core Sync tests, and put cheapest-boundary discipline into existing testing guidance and agent review so those mistakes are challenged before implementation.
> **Branch:** `fix/architecture/implementation-testing-alignment` — the dedicated branch Herald 📯 (Release Manager) created for the implementation/testing alignment change, which is the delivery vehicle for T1–T4
> **Delivery:** chained PR slice if the running authored count exceeds about 400; three work units — guidance/agents, git-pr-workflow tests, Core Sync E2E — each committed separately
> **Runner:** `pnpm --dir .agents/skills/git-pr-workflow test`; `pnpm --dir cli/aicore exec vitest run --config vitest.e2e.config.ts`; `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks/2026-11-17-cheapest-test-boundary.md`; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts odd/features/cheapest-test-boundary.md`

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — A test uses the cheapest boundary that still proves its contract. Exact requirement: "The test must exercise the least expensive boundary that still proves the intended contract." Acceptance: inspect the testing guidance and the changed git-pr-workflow and Core Sync tests; observe unit tests for deterministic logic, integration tests only when the real external boundary is the subject, and E2E tests only when composition, process, distribution, or system-level contracts cannot be established more cheaply.
- S2 — Expensive integration or E2E work is justified before it is added. Exact requirement: "Before adding or substantially expanding an integration/E2E test involving real external operations, the testing agent must determine: 1. Which exact contract is being tested? 2. What concrete regression would the test detect? 3. Is this regression already covered by existing tests? 4. Why would a unit test, mock, smaller fixture, or narrower integration test be insufficient? 5. What expensive operations will the test perform? 6. Can repeated setup or operations be eliminated? 7. Does the test require a real external dependency, or only its observable outputs? 8. What isolation and cleanup guarantees exist? This should be a concise design check, not a mandatory document for every trivial test." Acceptance: read Crucible 🔥 (Test Architect) and Forge 🔨 (Implementer) runtimes plus the testing contract; observe that the eight-question check is required for those expansions and is not a new artifact type.
- S3 — Unique regression coverage is kept; redundant execution is not. Exact requirement: "Do not repeat identical assertions across unit, integration, and E2E layers unless the different boundary provides additional regression protection." and "Preserving unique regression coverage is mandatory. Preserving redundant execution is not." Acceptance: inspect the changed suites; each remaining expensive test protects a contract a cheaper test does not, and deleted tests leave that unique contract covered elsewhere.
- S4 — git-pr-workflow stops paying for unnecessary real Git. Exact requirement: "Implement the approved simplification of the Git tests." and "Reduce unnecessary repository initialization and Git subprocess execution. Prefer the existing GitReader boundary, recording fakes, captured Git output." Acceptance: run `pnpm --dir .agents/skills/git-pr-workflow test`; observe one real committed-repository integration smoke that still maps commits, rename, metacharacter path, unresolved revision, and a failing read; observe the truncated name-status and missing-executable tests unchanged; observe prepare-local real-Git E2E gone; observe EEXIST covered by a CLI test that does not create a Git repository; observe the 17 synthetic CLI E2E tests and isolated-copy tests retained.
- S5 — Core Sync E2E does not repeatedly synchronize the whole cleared set when a representative source proves the same contract. Exact requirement: "I do not want to synchronize 298 files repeatedly when ten representative files could prove the same behavior, unless you demonstrate that the real dataset is essential." and "Do not replace every E2E test with mocks. Preserve meaningful end-to-end verification of the actual distribution and synchronization contracts." Acceptance: run the Core Sync E2E suite; observe enrollment against the real checkout still present; observe opt-out, cursor, and project-owned scenarios using a smaller representative source; observe redundant extra synchronization passes removed; observe cheap wrapper E2E tests unchanged.
- S6 — Critical integration boundaries are not mocked only to go faster. Exact requirement: "do not replace critical integration boundaries with mocks simply to make tests faster." and "However, do not replace critical integration boundaries with mocks simply to make tests faster." Acceptance: inspect remaining GitReader and Core Sync engine tests; observe real Git still used for the GitReader smoke and the real engine still used for remaining Core Sync E2E.
- S7 — No publication occurs without separate authorization. Exact requirement: implied by standing Git boundary; the request authorizes targeted improvements, not push or PR. Acceptance: inspect Herald 📯 (Release Manager) reports; observe no push, PR, merge, or destination-repository modification.

## Tasks

- T1 | S1, S2, S3, S6 | inline (instruction surfaces Cipher 🔓 (Lead Orchestrator) owns: testing contract clarification and agent runtimes) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T2 | S3, S4, S6 | delegated (test source under Forge 🔨 (Implementer) ownership) — Forge 🔨 (Implementer) | in progress | commit: pending
- T3 | S3, S5, S6 | delegated (Core Sync E2E under Forge 🔨 (Implementer) ownership; depends on T1 guidance being in the record) — Forge 🔨 (Implementer) | in progress | commit: pending
- T4 | S7 | delegated (local commits only, after each accepted slice) — Herald 📯 (Release Manager) | open | commit: pending

## Log

- L1 — Original request, verbatim:

  I want to correct the existing test inefficiencies in AICore **and prevent our coding/testing agents from repeating these design mistakes**.

  The previous investigations revealed a recurring problem: tests were accepted because they passed, without sufficiently questioning their execution cost, duplicate coverage, fixture complexity, and choice of testing level.

  I do not want another prolonged investigation. We have enough evidence to proceed with targeted improvements.

  This work has two objectives:

  **A. Simplify the expensive tests in `git-pr-workflow` and Core Sync.**

  **B. Improve the existing testing-agent and review workflow so that unnecessary testing complexity is challenged before implementation.**

  The solution must remain minimal, maintainable, and consistent with AICore's established architecture.

  # 1. Testing design principles

  Apply these principles to the current optimization and incorporate them into the appropriate existing testing guidance.

  ### Choose the cheapest test boundary that proves the contract

  Use:
  - **Unit tests** for deterministic logic, validation, transformations, error mapping, and decisions that can be verified without external systems.
  - **Integration tests** when the interaction with an actual external boundary is the subject of the test.
  - **E2E tests** when real composition, process behavior, distribution, or system-level contracts cannot be adequately established at cheaper levels.

  Do not classify a test as E2E merely because it launches a CLI or uses real files.

  Do not use real Git repositories, external processes, large datasets, or repeated synchronization operations by default.

  However, do not replace critical integration boundaries with mocks simply to make tests faster.

  **The test must exercise the least expensive boundary that still proves the intended contract.**

  ### Require justification for expensive tests

  Before adding or substantially expanding an integration/E2E test involving real external operations, the testing agent must determine:
  1. Which exact contract is being tested?
  2. What concrete regression would the test detect?
  3. Is this regression already covered by existing tests?
  4. Why would a unit test, mock, smaller fixture, or narrower integration test be insufficient?
  5. What expensive operations will the test perform?
  6. Can repeated setup or operations be eliminated?
  7. Does the test require a real external dependency, or only its observable outputs?
  8. What isolation and cleanup guarantees exist?

  This should be a concise design check, not a mandatory document for every trivial test.

  ### Avoid coverage duplication

  Do not repeat identical assertions across unit, integration, and E2E layers unless the different boundary provides additional regression protection.

  Test count is not a quality metric.

  Adding more tests is not automatically better.

  Deleting tests is not automatically an optimization.

  **Preserving unique regression coverage is mandatory. Preserving redundant execution is not.**

  # 2. Optimize git-pr-workflow

  Implement the approved simplification of the Git tests.

  The existing investigation identified nine real Git repository constructions, including three E2E scenarios.

  Reduce unnecessary repository initialization and Git subprocess execution.

  Prefer the existing `GitReader` boundary, recording fakes, captured Git output, and Vit

  (message ended truncated at "and Vit")

- L2 — 2026-11-17 — Classification: non-small. Two packages' test suites plus testing-contract and agent-runtime instruction changes cannot be resumed from a request plus a diff. Durable file `odd/features/cheapest-test-boundary.md` created; `odd/features/typescript-testing.md` stays the Vitest-runner capability and is not this contract. New `T` identifiers are not added in this change so stack-guide parity is not reopened; T8 is clarified and Crucible 🔥 (Test Architect) plus Forge 🔨 (Implementer) carry the eight-question check. Truncation: section 2 of the request ends at "and Vit"; S4 uses the already-approved git-pr-workflow simplification from the prior decision (one real-Git smoke, remove duplicate GitReader cases and prepare-local real-Git E2E, move EEXIST onto a Git-free CLI test). S5 uses the already-approved Core Sync plan named in objective A. No new debt entry: DEBT-053 is the git-pr-workflow fixture duplication this T2 retires. L1 is the complete captured original: the inbound message ended at "and Vit".
- L3 — 2026-11-17 — T1 rewrite accounting. Originals: `.aicore/core/architecture/testing/architecture.md` T8 two-sentence body; `.opencode/agents/crucible.md` 1.18.1 review-scope bullets; `.opencode/agents/forge.md` 3.4.0 per-step item 5. Candidates: the same three files as edited this turn (T8 expanded; crucible.md 1.19.0; forge.md 3.5.0). Disposition of valid original obligations: T8's two sentences retained as the opening of T8; T6–T7 and T9–T36 retained unedited; Crucible's remaining review-scope, contract, pyramid, and file-type obligations retained; Forge 🔨 (Implementer) steps 1–4 and 6–8 retained; no original obligation retired. Added from this request (S1–S3, S6): cheapest-boundary sentences on T8; eight-question design check on Crucible 🔥 (Test Architect) (review) and Forge 🔨 (Implementer) (authoring), not a new `T` identifier and not a new artifact type. Stack-guide T8 citations retained without restating the new sentences. Source-neutral: no destination runner, pin, or local policy value. Verdict: accounting complete; rewrite acceptable. Detail: the committed diffs of those three files.
- L4 — 2026-11-17 — Verified progress, not closure. T1 authored; Sentinel 🛡️ [PASS] after L3 accounting. T2 authored; Crucible 🔥 [PASS]; `pnpm --dir .agents/skills/git-pr-workflow test` 12 files, 65 passed, 1.54s. T3 authored; `pnpm --dir cli/aicore exec vitest run --config vitest.e2e.config.ts` 10 files, 18 passed, 13.32s; T3 has no independent Crucible 🔥 fixture-lifecycle verdict yet. Durable file KEEP (2026-11-17 naming review). Work sits uncommitted on `feat/tooling/lint-and-format-adoption` (HEAD `3e77449`), mixed with the tooling branch. T1–T3 remain `in progress` because `done` requires a commit id. T4 unstarted. Independent whole-feature semantic acceptance not obtained. DEBT-053 still open until T2 is committed and its resolution criteria are evidenced. Architectural findings F1–F5 deferred as DEBT-054 and DEBT-055; F6 is DEBT-046/047; F7 is a T8 exception, not debt.
- L5 — Blocked: user 2026-11-17 stopped expansion and forbade implementing the T2/T4/T5 corrections now. Remaining for this feature: separate branch or isolated commits via Herald 📯; T3 architecture review; T4 commits; independent semantic acceptance. Not closed.
- L6 — 2026-11-17 — Branch attribution corrected (alignment finding F7). L4's claim that the work sat on `feat/tooling/lint-and-format-adoption` at `3e77449` is obsolete: that branch was merged and no longer exists locally, and the work was found uncommitted on `main` at `e700244` when the alignment change started. Herald 📯 created `fix/architecture/implementation-testing-alignment` from `e700244` with a byte-identical working tree, and T1–T4 are delivered there. Also repaired in that delivery: the lost real-Git `mergeBase` disjoint-history assertion and the lost assembled `prepare-local` end-to-end scenario, both restored at the cheapest boundary available, so T2's reduction no longer drops unique coverage. Evidence: `odd/tasks/2026-11-17-implementation-testing-alignment.md` and the commits on the dedicated branch.
- L7 — 2026-11-17 — Candidate identity corrected for L3's rewrite accounting. L3 named its candidates as "the same three files as edited this turn (T8 expanded; crucible.md 1.19.0; forge.md 3.5.0)". Those version identities are no longer the content that ships: PR #193 (`e700244`) advanced the two runtimes to `crucible.md` 1.20.0 and `forge.md` 3.6.0 before this branch was created, and the uncommitted T8 change on `fix/architecture/implementation-testing-alignment` is the candidate that delivers it. The delivering candidates are therefore `architecture.md` T8 with its expanded least-expensive-boundary clause, `crucible.md` 1.20.0, and `forge.md` 3.6.0. L3's disposition list is unchanged and still holds for those candidates: T8's two original sentences remain its opening clause, T6–T7 and T9–T36 are unedited, Crucible's remaining review-scope, contract, pyramid and file-type obligations remain, Forge steps 1–4 and 6–8 remain, no original obligation is retired, and no `T` identifier was added. L3 keeps its original wording as dated history; this entry binds the accounting to the shipping candidate. Verified by reading the three candidate files.
- L8 — Close: 2026-11-24 — Cancelled under explicit user authorization, verbatim: "For cheapest-test-boundary, preserve my explicit stop instruction. Do not resume its implementation." The user stopped this work on 2026-11-17 and forbade implementing the remaining corrections (`L5`), and that instruction authorizes its terminal cancellation rather than its completion. `T1`–`T3` remain `in progress` and `T4` remains `open`; they are preserved exactly as recorded and are **not** presented as complete or accepted, and no per-requirement verdict exists for them. Historical evidence retained unchanged: the candidate identities, the obligation accounting and the scope decisions at `L2`–`L7`. No implementation is resumed and no requirement is retired as met.
