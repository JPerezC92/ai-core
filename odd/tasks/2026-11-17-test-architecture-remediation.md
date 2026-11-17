# Test architecture prevention and the first remediation slice

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-17
> **Objective:** Land the permanent test-distribution rule in the canonical testing contract with its Crucible, Forge and Cipher enforcement, and deliver the first remediation slice — the corrected `op-model` application operation plus boundary-verified unit, integration and end-to-end coverage — in one pull request.
> **Branch:** `test/test-architecture-remediation` — authorized in this slice; created by Herald 📯 (Release Manager) from `main` at `0315063d1f7256c43601b454485ffb9ac57c0893` after this record is written.
> **Delivery:** one PR, no separate documentation PR; forecast ~700 authored additions + deletions (well above the ~400 feature-level trigger), delivered as three reviewable commits — P0 instruction surfaces, `op-model` production correction with its tests, then records and coverage evidence.
> **Runner:** `pnpm --dir .agents/skills/op-model exec vitest run`; `pnpm --dir .agents/skills/op-model typecheck`; `pnpm format:check`; `pnpm lint`; `pnpm typecheck`; `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks`; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts odd/features`

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — The canonical testing contract states the expected test distribution and its approval boundary. Exact requirement: "Add the test distribution expectation to canonical T8." Acceptance: read `.aicore/core/architecture/testing/architecture.md` `T8`; it states boundary-verified unit > integration > end-to-end ordering at each test-owning unit and at the repository aggregate, forbids fabricated, split and misleadingly reclassified tests, states that no fixed percentage applies, and reserves every exception to the user; no `T` identifier is added, so T27 parity evidence is unchanged.
- S2 — Crucible's review obligation returns a distribution verdict and cannot pass an unapproved deviation. Exact requirement: "Update Crucible's review obligation." Acceptance: read `.opencode/agents/crucible.md`; its review obligation requires a `COMPLIANT` / `EXCEPTION REQUIRED` / `UNVERIFIED` distribution verdict with the counting method and verified boundaries, reports `[FAIL]` for a deviation without recorded user acceptance, and references `T8` instead of restating it.
- S3 — Forge's applicable guidance accounts for test-distribution effects of its slices. Exact requirement: "Update Forge's applicable T8 verification guidance." Acceptance: read `.opencode/agents/forge.md`; its `T8` obligation requires reporting the affected unit's distribution when a slice changes test counts and treats an unapproved deviation as a blocker, by reference to `T8`.
- S4 — Cipher's adjudication procedure cannot turn an unapproved distribution exception into a pass, deferral or accepted advisory. Exact requirement: "Update Cipher's adjudication procedure." Acceptance: read `.aicore/core/knowledge/agents.md` `### PR review findings (adjudication)`; a row routes a distribution exception without recorded user approval to the user and forbids `FIXED`, `DEFERRED` and advisory acceptance.
- S5 — The two affected durable features record this change and each status derives from that file's own ticks. Exact requirement: "Update the existing durable feature and appropriate ODD record." Acceptance: run the feature-file validator over `odd/features/architecture-contract.md` and `odd/features/cheapest-test-boundary.md`; each file reports the status derived from its own ticks.
- S6 — `op-model`'s lookup operation is an application use case with its source port injected through the constructor. Exact requirement: "Correct the confirmed `FindModels` application operation if its source still supports the reported C3 finding." and "Use constructor injection through the existing source port." Acceptance: construct the operation with a doubled model source and call its single `execute()`; the same typed outcomes are returned and no module-level lookup function remains.
- S7 — `op-model`'s externally observable behavior is unchanged. Exact requirement: "Preserve its externally observable behavior." Acceptance: run the package suite; grouped listing, JSON-line selection, empty-catalog and unmatched-query messages, and the missing-executable diagnostic all report exactly what they reported before the correction.
- S8 — The child-process adapter is exercised against a controlled executable and never against a user's installed binary. Exact requirement: "Add appropriate integration tests for the real child-process adapter." and "Do not depend on a user's locally installed OpenCode binary." Acceptance: run the package suite with no `opencode` on `PATH`; the adapter's success mapping, failure classification and missing-executable behavior all pass.
- S9 — An absent or unusable setup cannot produce a silently passing run. Exact requirement: "Fix the non-hermetic E2E tests that currently pass without exercising the intended executable." and "Ensure tests fail meaningfully when their required setup cannot be established." Acceptance: with the controlled executable unavailable, the affected cases fail rather than pass.
- S10 — Every unique renderer and CLI assertion remains protected at a verified boundary. Exact requirement: "Preserve every unique behavioral assertion currently protected by the renderer and CLI tests." and "Do not delete ten cases simply because their current T2 classification is invalid." Acceptance: read the assertion-by-assertion coverage mapping and locate each behavior's assertion in the delivered tests; no behavior is unprotected.
- S11 — `op-model`'s measured distribution satisfies the expected ordering. Exact requirement: "The measured `op-model` distribution genuinely satisfies Unit > Integration > E2E." Acceptance: run the three levels; the measured unit, integration and end-to-end case counts satisfy unit > integration > end-to-end.
- S12 — The approved unit-test target rules are unchanged. Exact requirement: "Do not implement option B during this PR." and "Do not loosen the approved unit-test target rules." Acceptance: diff the testing contract between base and head; `T2` is textually unchanged.
- S13 — The change contains all and only the approved work. Exact requirement: "No unrelated files or work enter the PR." Acceptance: inspect the base-to-head diff; every changed path traces to this record.
- S14 — Every package whose distribution still violates the expected ordering is reported as unresolved. Exact requirement: "Other packages' violations remain transparently unresolved." Acceptance: read the delivered pull-request body; each such package is named as unresolved rather than compliant.

## Tasks

- T1 | S1, S2, S3, S4, S5 | inline (shared instruction surfaces and the two durable features, Cipher 🔓 owns the ODD lifecycle) — Cipher 🔓 (Lead Orchestrator) | done | commit: 6f105e4
- T2 | S6, S7 | delegated (production source under Forge 🔨 ownership; one application module and its composition root) — Forge 🔨 (Implementer) | done | commit: 6924dba
- T3 | S8, S9, S10, S11 | delegated (test authoring and routine execution under Forge 🔨 ownership; new integration level, rewritten E2E, renderer coverage migration) — Forge 🔨 (Implementer) | done | commit: 6924dba
- T4 | S8, S10 | delegated (test-architecture risk: new integration level, fixture lifecycle, coverage equivalence) — Crucible 🔥 (Test Architect) | done | commit: 6924dba
- T5 | S6, S7 | delegated (C3 conformance of the corrected application operation and its composition) — Bastion 🧱 (Backend & Scripts Architect) | done | commit: 6924dba
- T6 | S1, S2, S3, S4, S5, S13 | delegated (agent documents, shared testing rule and ODD record consistency) — Sentinel 🛡️ (Quality Guardian) | done | commit: 6f105e4
- T7 | S13, S14 | delegated (sole Git executor: branch, commits, push, one PR) — Herald 📯 (Release Manager) | in progress | commit: pending
- T8 | S13, S14 | delegated (independent review at the immutable PR head) — Inquisitor 🔎 (PR Reviewer) | open | commit: pending

## Log

- L1 — Original request, verbatim:

  # AICore — Approve First Test Architecture Remediation Slice

  I reviewed your architecture reconciliation and remediation plan.

  The root-cause direction is accepted.

  **All six distribution exceptions remain rejected.**

  I want to start implementation now, but I am narrowing the first delivery to one coherent PR combining P0 and P1.

  ## 1. Approved scope: P0 + P1 in ONE PR

  This PR must contain:

  **P0 — Permanent test architecture prevention**
  - Add the test distribution expectation to canonical T8.
  - Update Crucible's review obligation.
  - Update Forge's applicable T8 verification guidance.
  - Update Cipher's adjudication procedure.
  - Update the existing durable feature and appropriate ODD record.

  **P1 — op-model implementation and tests**
  - Correct the confirmed `FindModels` application operation if its source still supports the reported C3 finding.
  - Use constructor injection through the existing source port.
  - Preserve its externally observable behavior.
  - Add appropriate integration tests for the real child-process adapter.
  - Fix the non-hermetic E2E tests that currently pass without exercising the intended executable.
  - Retain only the necessary representative assembled CLI E2E coverage.
  - Preserve every unique behavioral assertion currently protected by the renderer and CLI tests.

  **These changes belong in one PR.**

  Do not create a documentation-only P0 PR followed by a separate P1 PR.

  ## 2. Strict test-pyramid policy

  The expected architecture is:

  **Unit > Integration > E2E**

  Measure actual test cases at their verified behavioral boundaries.

  No artificial tests, misleading reclassification, arbitrary percentages, or removal of unique regression coverage.

  No permanent exceptions have been approved.

  The six previously reported noncompliant packages remain noncompliant until their defects are genuinely corrected.

  A successful PR must never be interpreted as approval of the repository's remaining violations.

  ## 3. Progressive remediation without automatic exceptions

  The repository currently contains pre-existing distribution violations.

  The new review procedure must distinguish:
  - A genuinely compliant package.
  - An unresolved existing violation.
  - An explicitly authorized remediation change addressing that violation.
  - A new regression introduced by a change.

  An authorized remediation PR may proceed while unrelated existing violations remain open, provided:
  - It does not falsely declare repository-wide compliance.
  - It does not worsen unrelated distributions.
  - It preserves existing unique coverage.
  - It provides evidence of the architectural defect being corrected.
  - Its outstanding violations remain visible.
  - It does not approve or waive any final exception.

  This is a limited delivery procedure, not authorization to retain a disproportionate final architecture.

  Do not use an ODD record to imply that I have approved P2–P7.

  Those are proposed future slices, not yet authorized implementation work.

  Do not impose a rule requiring numerical improvement in every intermediate PR if a necessary architectural correction must precede test migration.

  Such a prerequisite must be explicitly identified and must not be misreported as completed proportionality remediation.

  ## 4. Validate op-model carefully

  Before changing tests, inspect the actual implementation and source contracts.

  Confirm that `FindModels` is a genuine application use case under C3.

  Do not introduce an unnecessary class merely to increase the unit-test count.

  For the subprocess adapter:
  - Exercise the real adapter behavior against a controlled executable substitute where appropriate.
  - Do not depend on a user's locally installed OpenCode binary.
  - Do not create a custom framework to manage subprocess fixtures.
  - Preserve executable-not-found and failure behavior.
  - Ensure tests fail meaningfully when their required setup cannot be established.

  For the existing renderer tests:

  **Do not delete ten cases simply because their current T2 classification is invalid.**

  First produce an assertion-by-assertion coverage mapping.

  Each unique behavior must remain protected by a valid test at the appropriate boundary.

  Do not transfer ten detailed renderer assertions into two broad E2E cases unless equivalence is actually demonstrated.

  The projected 25 / 4 / 2 distribution is a forecast, not an acceptance target that permits loss of coverage.

  If the valid final distribution differs, report the verified result.

  ## 5. No changes to T2 yet

  Do not implement option B during this PR.

  Do not loosen the approved unit-test target rules.

  Do not accept option D-2 or permanently exempt `odd-adviser`.

  The T2 policy-module question must be resolved through a separate evidence-based architecture decision before the relevant later remediation.

  Do not use an unresolved T2 decision to block this first `op-model` correction if it does not depend on it.

  ## 6. Boundaries and delivery

  Do not modify:
  - Core Sync's 65-case parity corpus.
  - `odd-adviser` production policies.
  - `system-one` test organization.
  - Other skill-package implementations.
  - DEBT-046/055/056 beyond directly necessary and authorized records.
  - Warden or unrelated agent permissions.
  - Downstream repositories.

  Herald remains the sole Git/GitHub executor.

  First confirm the actual current Git state, main revision and ownership of any uncommitted changes.

  Preserve all unrelated work.

  For this approved P0 + P1 slice, Herald is authorized to create a dedicated branch, make focused commits, push, and publish **one PR targeting main**, provided the implementation, coverage, architecture verification and required independent review pass.

  Do not create a second PR for P0.

  No merge is authorized.

  ## 7. Acceptance criteria

  The first PR must demonstrate:
  1. The confirmed `op-model` application violation is corrected.
  2. Its actual unit, integration and E2E boundaries satisfy the architecture.
  3. No valuable renderer or CLI regression coverage was lost.
  4. The child-process tests are hermetic and cannot silently pass without executing their target.
  5. The measured `op-model` distribution genuinely satisfies Unit > Integration > E2E.
  6. T8 documents the permanent rule.
  7. Crucible, Forge and Cipher can enforce it without duplicating the architecture contract.
  8. Other packages' violations remain transparently unresolved.
  9. No unrelated files or work enter the PR.
  10. Required validation and independent review pass with zero blocking findings.

  Reuse existing valid evidence and do not restart the repository-wide test audit.

  ## 8. Final report

  Report:
  - PR URL, base and head SHA.
  - Exact implementation changes.
  - Complete assertion-preservation evidence.
  - Previous and final verified op-model test counts.
  - Validation results.
  - Permanent T8 enforcement changes.
  - Remaining noncompliant packages.
  - ODD status.
  - Independent review verdict.
  - Any limitations or blockers.

  **Complete this first authorized remediation slice and notify me definitively when it is done.**

  Do not start P2–P7 automatically.

  Do not request the previously rejected six exceptions again.

  The objective is architectural correctness and meaningful test coverage, not manufactured pyramid statistics.

- L2 — 2026-11-17 — Classification: **non-small**. Understood: the four instruction surfaces, the durable feature and all nine `op-model` files were read in full before this record existed. Risk-contained: no — the slice changes shared testing law, three agent runtimes, one shipped skill's production module and its test levels. Resumable from request plus diff: no. This record is therefore the sole bootstrap write; no other mutation preceded it.
- L3 — 2026-11-17 — Baseline. Herald 📯 reported `main` = `origin/main` = `0315063d1f7256c43601b454485ffb9ac57c0893` with an empty `git status --porcelain=v1 -uall`, two pre-existing stashes (`stash@{0}`, `stash@{1}`) and two pre-existing detached-HEAD worktrees, all of which this change leaves untouched. `.agents/skills/op-model/package.json` is tracked and no local branch exists under the `docs/*`, `feat/*`, `chore/*`, `test/*` or `fix/*` prefixes.
- L4 — 2026-11-17 — Durable-feature ownership corrected. `R5` was withdrawn from `odd/features/cheapest-test-boundary.md`: that file owns boundary selection, not a review-and-approval procedure. The permanent capability is recorded in `odd/features/architecture-contract.md` as `R17`, because that file already owns the language-agnostic test-level requirements (`R9`, `R12`–`R15`) and is therefore the canonical durable owner of test-architecture conformance; the normative rule stays in `T8`. `R17` is unticked and both features remain `partial`, because six packages still violate the ordering.
- L5 — 2026-11-17 — `cheapest-test-boundary` re-verified requirement by requirement. `R1` ("A test exercises the least expensive boundary that still proves its intended contract") is **unticked**: the distribution investigation confirmed tests running above the boundary that owns their contract in `cli/aicore` (65 composed-engine cases whose decisions are pure domain policies), in the six skill packages, and in `op-model` before this slice. `R2`, `R3` and `R4` keep their ticks: the expensive-level justification duty is carried by `T8` and was applied in this slice, no confirmed finding established a repeated identical assertion across levels, and no critical integration boundary was replaced with a double. The failure and its evidence are recorded here, not by rewriting the requirement.
- L6 — 2026-11-17 — First review round. Bastion 🧱 `[PASS]`, zero findings, two INFO notes (failure text still names `opencode` literally under a composition-bound executable; `infrastructure/process.ts` predates the `infrastructure/adapters/` convention) — both recorded as limitations, neither actionable in this slice. Sentinel 🛡️ `[FAIL]` with four findings: `F1` (T8 per-unit ordering unattainable for a unit with no approved unit target) is **rejected** — the user's own governing instruction requires such a unit to be reported and submitted for explicit exception approval rather than exempted, so the clause is faithful; `F2` (Crucible restating the measurement rule) fixed by citing `T8`; `F3` (`S5`/`S13` acceptance naming two actions) fixed, and `S14` added for the remaining-packages duty; `F4` (no full-mirror Log entry) closed by `L8`. Crucible 🔥 `[FAIL]` with three findings: the two `T11` describe-group findings fixed by regrouping `find-models.test.ts`, `process.test.ts` and `models-cli.test.ts` into one concern per group, and `T15` fixed by adding `tests/support/model.factory.ts` consumed by all four modules. Crucible's request to split the two-outcome end-to-end case into two cases was **not applied**: `T11` constrains modules and describe groups, not case bodies, so the case is one concern (business-outcome reporting) with two data instances, and splitting it would change the case count without an architectural reason. The verified distribution is unchanged at 13 / 5 / 4.
- L7 — 2026-11-17 — Verified result after remediation: 22 cases pass — unit 13 (8 use-case, 5 parser), integration 5 (one adapter across its real spawn boundary), end-to-end 4 (assembled entry point). Unit > integration > end-to-end holds for this test-owning unit and Crucible 🔥 returned `COMPLIANT` for it. `pnpm --dir .agents/skills/op-model exec vitest run` 22 passed; `typecheck` clean for the package and for the whole tree; `lint` and `format:check` clean.
- L8 — 2026-11-17 — Full-feature mirror: **pending recovery**, not synchronized. This project's recorded binding states that the first source-contract slice authorized no real feature mirror, that exact-mirror acceptance was retired, and that runtime adoption of full mirroring remains unverified; the backend also lacks exact-key upsert and compare-and-swap, so a complete payload readback cannot be proven. The authoritative record is therefore this repository file, and the next bounded recovery action is a separately authorized mirror probe against the documented tool limits.
- L9 — 2026-11-17 — Governing instruction invoked by `L6`, recorded verbatim from the 2026-11-17 audit request that preceded this slice: "A package with no applicable approved unit targets must not be forced to create artificial unit tests. However, if its distribution deviates from the expected rule, it must still be reported transparently and submitted for my explicit exception approval." It governs the `T8` wording and the rejection of Sentinel finding F1; it changes no spec, task or requirement in this record.
- L10 — 2026-11-17 — Second review round. Crucible 🔥 `[PASS]`, zero findings: it accepted the `T11` reading and retracted its split request, and its assertion-level comparison of the old 33 cases to the new 22 records each old assertion's new location or its reason for retirement — the four end-to-end live-source cases are preserved and now hermetic, six renderer assertions live at the entry point, and four renderer assertions plus one use-case case are unreachable under the current adapter (`parseRecords` always yields `costIn=0, costOut=0` and `name === id`). Sentinel 🛡️ `[FAIL]` on two record findings, both fixed: the governing instruction behind the `F1` rejection is now `L9` (verbatim), and `S5` plus the `T1` scope now name both durable files instead of "the durable feature".
- L11 — 2026-11-17 — Delivery state. Branch `test/testing/test-architecture-remediation` was created from `main` at `0315063` (Herald 📯 applied the repository's `type/scope/description` branch convention to the dispatched name). Commit `6f105e4` carries the four instruction surfaces and both durable features; commit `6924dba` carries the `op-model` production correction and its tests. Push and the single pull request are still outstanding, so `T7` and `T8` remain open and this record stays `active`; closing it is not delivery.
