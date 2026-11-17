# Implementation and testing alignment

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-17
> **Objective:** Correct the one confirmed C3 application-use-case violation in the odd-adviser plugin, align its affected tests, repair and retain the already-authored cheapest-boundary test optimizations, and retire only the technical debts whose resolution criteria are fully evidenced — all in one independently reviewed pull request.
> **Branch:** `fix/architecture/implementation-testing-alignment` (created by Herald 📯 at `e7002448f5af3d369c6aa97f63e1b8e7ae265fbf`, base `main`)
> **Delivery:** one PR, mandatory by user instruction; forecast ~750 authored additions + deletions, above the ~400 feature-level trigger, so the strategy is executed as three reviewable commits — implementation correction, direct use-case tests, test-boundary repairs plus optimization and record/debt evidence — each committed separately inside the one PR
> **Runner:** `pnpm --dir .opencode/plugins/odd-adviser test`; `pnpm --dir .opencode/plugins/odd-adviser typecheck`; `pnpm --dir cli/aicore test`; `pnpm --dir .agents/skills/git-pr-workflow test`; `pnpm --dir cli/aicore exec vitest run --config vitest.e2e.config.ts`; `pnpm format:check`; `pnpm lint`; `pnpm typecheck`; `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks`; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts odd/features`

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — The odd-adviser evidence evaluation is an application use case implemented as a class with one `execute()`. Exact requirement: "Introduce the appropriate `EvaluateEvidence` use-case class with its `execute()` contract and constructor-injected dependencies." and "Correct the confirmed C3 violation in `odd-adviser`." Acceptance: read the application module and construct the operation; one class named for the operation exposes exactly one `execute()`, receives its evaluator and deadline collaborators through its constructor, and no module-level evaluation operation remains exported from it.
- S2 — The five affected application tests keep asserting the same observable behavior after the correction. Exact requirement: "Align the affected tests with the corrected implementation." and "Preserve existing behavior and the established composition boundaries." and "Before modifying the five affected application tests, read their actual contents and determine the minimal required changes." Acceptance: run the package suite and read the five specs; deadline cleanup, evidence confidentiality, port invocation, outcome mapping and timeout still assert the same returned advisories and the same deadline observations.
- S3 — Genuinely pure helpers stay module-level functions and no new abstraction is introduced for them. Exact requirement: "Keep `toUnavailableAdvisory`, `answersNoQuestion`, and other genuinely pure helpers as functions." and "Do not introduce unnecessary new ports, wrappers, interfaces, or factories." Acceptance: read the module; both helpers remain exported functions consumed by their existing callers, and no class, port, wrapper, interface or factory was added for them or for composition.
- S4 — The two named CLI application use cases each have a T2 unit exercising their real `execute()`. Exact requirement: "Add the two missing T2 use-case test suites:" — "`ReconcileDestination`" — "`RunAdvancedCommand`" — "Use their real `execute()` contracts and appropriate injected test doubles." and "Do not manufacture additional unit-test targets." Acceptance: run the package unit suite; two specs each construct the real use-case class with doubled port collaborators, call `execute()`, and assert returned business values and returned domain failures, and no unit target beyond those two is added.
- S5 — The real-Git `mergeBase` disjoint-history behavior is proved again at no additional repository cost. Exact requirement: "Restore the unique real-Git `mergeBase` disjoint-history assertion." and "Reuse the existing collapsed fixture where possible." and "Do not create another expensive repository fixture solely for this assertion." Acceptance: run the git-pr-workflow suite; one integration test observes `mergeBase` returning `null` for a revision whose history shares no ancestor, and the suite builds no additional committed repository for it.
- S6 — The assembled `prepare-local` command is exercised once as a real entry point. Exact requirement: "Restore one minimal representative E2E test exercising the actual assembled `prepare-local` command." and "The test must validate real command behavior, not merely call the application use case directly." and "Use the cheapest fixture that still proves the actual entry-point contract." and "Avoid duplicating the migrated EEXIST assertion unnecessarily." Acceptance: run the e2e suite; one spawned `prepare-local` invocation against one committed repository is observed to exit 0 and write the expected snapshot, and no existing-output assertion is duplicated.
- S7 — The existing Core Sync representative-source optimization is retained with its end-to-end coverage intact. Exact requirement: "Retain the previously written Core Sync representative-source optimization." and "Preserve valid integration and E2E boundaries." Acceptance: run the Core Sync e2e suite; enrollment against the real checkout is still exercised and the opt-out, cursor and project-owned scenarios run against the smaller representative source.
- S8 — Only the two eligible debts are retired; the other three stay open. Exact requirement: "**DEBT-047:** Close only after the C3 correction, affected consumers, tests, and architectural acceptance are verified." and "**DEBT-053:** Close only after the efficiency improvement and preserved real-Git/CLI regression coverage are demonstrated." and "Must remain open:" — "**DEBT-055**" — "**DEBT-056**" — "**DEBT-046**". Acceptance: read the debt register; the DEBT-047 and DEBT-053 entries are absent with their resolution evidence recorded in the governing records, and the DEBT-046, DEBT-055 and DEBT-056 entries are still present.
- S9 — The architecture-contract feature's requirement marks state the verified truth. Exact requirement: "Reverify `architecture-contract` R1 after completing and testing the C3 correction." and "R1 must not be considered satisfied merely because its checkbox was previously marked." and "If those tests violate R10, mark the requirement unsatisfied and record the existing DEBT-046 as the reason." and "Do not weaken or reinterpret R10 just to preserve `achieved`." Acceptance: read the durable feature file and run its validator; R1 is ticked only against the verified correction, R10 carries no tick with its cause recorded in this record, and the reported derived status is `partial`.
- S10 — The DEBT-056 file count states the measured value and test routing is untouched. Exact requirement: "Correct the DEBT-056 count from thirteen to twelve if the measured count remains twelve." and "Do not change test routing or classification in this PR." Acceptance: read the debt register and the suite layout; the entry states twelve parity spec files and no test file changed level or directory.
- S11 — The cheapest-boundary record names the branch that actually carries its work. Exact requirement: "Update `cheapest-test-boundary` to reference the actual branch and delivery evidence." and "Do not retain the obsolete branch attribution." Acceptance: read that record's header and Log; the `Branch` field names the dedicated branch and no obsolete branch attribution remains.
- S12 — The delivered range contains this work and nothing else. Exact requirement: "Do not include unrelated files merely because they are locally modified." and "Do not publish if any unrelated work has entered the commit range or if required architecture validation has failed." and "Do not create separate PRs for implementation, tests, ODD, or technical debt." Acceptance: inspect the base-to-head diff and open exactly one pull request; every changed path traces to S1–S13 and exactly one PR exists against `main`.
- S13 — The instruction surfaces that carry the least-expensive-boundary obligation state it once and keep their original obligations. Exact requirement: "Pay particular attention to existing changes associated with:" — "Shared agent guidance and testing architecture files." and "Preserve and repair the existing uncommitted testing optimizations." Acceptance: read the testing contract's T8 and the two agent runtimes plus this change's accounting; the obligation appears in T8 and in exactly one Crucible review bullet and one Forge authoring bullet, every obligation the accounting lists as retained is present in the candidate text, no new `T` identifier was added so stack-guide parity is unchanged, and the accounting names the runtime versions that actually ship.

## Tasks

- T1 | S1, S2, S3 | delegated (production source under Forge 🔨 ownership; plugin application module and its consumers) — Forge 🔨 (Implementer) | done | commit: 50344ea
- T2 | S4 | delegated (test authoring under Forge 🔨 ownership; two new CLI use-case specs) — Forge 🔨 (Implementer) | done | commit: 1838cf7
- T3 | S5, S6, S7 | delegated (test source under Forge 🔨 ownership; git-pr-workflow and Core Sync suites) — Forge 🔨 (Implementer) | done | commit: 20e58d4
- T4 | S8, S9, S10, S11 | inline (ODD records and the debt register, Cipher 🔓 owns the lifecycle) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T5 | S4, S5, S6, S7 | delegated (test-architecture risk: new and reorganized suites, fixture lifecycle) — Crucible 🔥 (Test Architect) | done | commit: 20e58d4
- T6 | S1, S3 | delegated (C3 conformance of the corrected application operation) — Bastion 🧱 (Backend & Scripts Architect) | done | commit: 20e58d4
- T7 | S9, S11, S13 | delegated (agent documents, shared testing rule and ODD record consistency) — Sentinel 🛡️ (Quality Guardian) | in progress | commit: pending
- T10 | S13 | inline (shared instruction surfaces and their accounting, Cipher 🔓 owns the ODD lifecycle) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T8 | S12 | delegated (only Git executor; commits, push, one PR) — Herald 📯 (Release Manager) | in progress | commit: pending
- T9 | S12 | delegated (review at the immutable PR head) — Inquisitor 🔎 (PR Reviewer) | open | commit: pending

## Log

- L1 — Original request, verbatim:

  # AICore — Implementation Architecture Remediation and Testing Alignment

  We are starting a completely new AICore development session.

  ## Objective

  I want to correct the confirmed implementation architecture violations first, then align the affected tests with the corrected implementation.

  **All implementation fixes, corresponding test corrections, validation evidence, and eligible technical debt closures must be delivered together in ONE pull request.**

  There are already uncommitted local changes from previous testing investigations and optimizations.

  These changes may provide useful implementation work and evidence, but their ownership and correctness must be verified before they are reused.

  **Do not discard, overwrite, automatically commit, or blindly carry forward these existing changes.**

  The final result must respect AICore's actual architecture, established ODD workflow, and Git safety boundaries.

  ---

  ## 1. Inspect the actual repository before acting

  Start by examining the current AICore checkout.

  Read the authoritative architecture and workflow contracts, particularly:
  - `.aicore/core/architecture/implementation/architecture.md`
  - `.aicore/core/architecture/testing/architecture.md`
  - Applicable TypeScript architecture and testing guides.
  - `.aicore/core/knowledge/agent-workflow.md`
  - `.aicore/core/knowledge/debt.md`
  - `.agents/skills/odd-workflow/SKILL.md`
  - Existing relevant durable features and active ODD task records.
  - Existing technical debts associated with implementation and testing.

  Inspect the actual production code, test suites, and configuration relevant to the identified findings.

  **Repository evidence is authoritative. Previous ChatGPT recommendations and agent reports are not substitutes for source inspection.**

  Do not invent architectural requirements or use generic testing conventions in place of AICore's established contracts.

  ## 2. Protect and inventory all existing uncommitted work

  Before creating a branch or editing any file, have Herald 📯 establish the complete Git state.

  Identify:
  - Current branch and HEAD.
  - Current local and remote `main`.
  - Whether relevant previous PRs have actually been merged.
  - All staged and unstaged modifications.
  - All untracked files.
  - All intentional deletions.
  - Existing worktrees and their ownership.
  - Relevant shared-file modifications.

  Record an evidence baseline sufficient to establish that no existing work is lost or unintentionally changed.

  Classify each modified file and, where necessary, each changed section as:
  1. Relevant implementation correction.
  2. Relevant testing correction.
  3. Relevant ODD/debt documentation.
  4. Unrelated work that must remain untouched.
  5. Uncertain ownership requiring evidence.

  Pay particular attention to existing changes associated with:
  - `2026-11-17-cheapest-test-boundary.md`
  - DEBT-053
  - DEBT-055
  - DEBT-056
  - Shared agent guidance and testing architecture files.

  **Do not assume every uncommitted change belongs to this new PR.**

  Do not use `git stash`, destructive resets, forced checkout, unsafe worktree manipulation, or symlinks/junctions to move work.

  If a safe branch transition requires an additional operation, identify the exact operation and its preservation guarantees before executing it.

  ## 3. Determine the correct scope

  Review the confirmed architecture findings and technical debts.

  Relevant candidates include:
  - **DEBT-046:** Test placement and organization.
  - **DEBT-047:** Application/use-case architecture violations.
  - **DEBT-053:** Redundant and expensive Git test fixtures.
  - **DEBT-055:** Missing T2 use-case coverage and unapproved unit-test targets.
  - **DEBT-056:** Incorrect integration/E2E boundary classification.
  - Existing `cheapest-test-boundary` implementation and test optimizations.

  Verify each debt's actual current contents, status, ownership, and resolution criteria.

  Do not infer current debt IDs solely from earlier conversations.

  Determine which corrections are genuinely related and should be included in this one implementation/testing PR.

  **Do not automatically include every open architecture debt in the repository.**

  If resolving the complete candidate scope would require a large, independent architectural migration, provide a prominent scope warning and recommend the smallest coherent delivery.

  Do not expand implementation without explicit approval.

  ## 4. Correct implementation architecture FIRST

  For each confirmed implementation violation, identify the intended architecture before editing tests.

  Follow AICore's existing contracts.

  In particular:
  - Application use cases must follow the required C3 structure.
  - Use cases must expose their established `execute()` contract.
  - Dependencies must be injected through the appropriate ports.
  - Domain, application, infrastructure, and delivery responsibilities must remain correctly separated.
  - Infrastructure-specific types must not leak into domain ports without architectural justification.
  - Composition belongs to the established composition boundary.
  - Existing externally observable behavior must be preserved unless a behavioral correction is explicitly authorized.

  **Prefer removing unnecessary complexity over relocating it.**

  Do not introduce additional ports, adapters, factories, interfaces, wrappers, or layers unless the existing architecture genuinely requires them.

  Do not convert every helper or function into a use-case class.

  First establish which components are actual application use cases under AICore's contracts.

  For every confirmed implementation violation, identify:
  - Current behavior.
  - Violated contract.
  - Smallest necessary correction.
  - Dependencies and affected consumers.
  - Existing regression protection.
  - Expected observable behavior after correction.

  Then implement the minimal correction.

  ## 5. Align tests with the corrected implementation

  After establishing the appropriate implementation boundary, correct the corresponding tests.

  Tests must follow AICore's actual T2, T4, T5, T8, T9, T10 and T21 requirements.

  ### Unit tests — T2

  Prioritize direct testing of actual application use cases through their `execute()` methods with doubled collaborating ports.

  Verify observable success, failure and boundary behavior.

  Do not write tests for arbitrary helpers, entities, adapters or individual production files merely to increase the unit-test count.

  Respect the explicit parser/loader and other exceptions in AICore's contract.

  ### Integration tests — T4

  Exercise real isolated adapter boundaries where their behavior matters.

  Do not replace meaningful integration coverage with mocks solely for speed.

  Do not classify a composed multi-adapter workflow as a single-adapter integration test merely because it runs in a filesystem fixture.

  ### E2E tests — T5

  Preserve verification of actual assembled entry points and relevant process or distribution contracts.

  Eliminate redundant, expensive execution only when unique regression protection remains.

  Do not classify tests solely by folder name.

  ### Test efficiency

  The expected test-pyramid tendency is:

  **Unit tests > Integration tests > E2E tests**

  This is a design heuristic, not a numerical acceptance requirement.

  Never manufacture tests, delete valuable coverage or manipulate classifications to achieve a desired percentage.

  Prefer the cheapest sufficient test boundary while preserving the actual contract.

  ### Important

  Implementation-first does not prohibit writing a focused regression test before changing production code.

  Protecting existing behavior is mandatory.

  **Do not rewrite tests merely to make incorrect production behavior pass.**

  ## 6. Reconcile the previous testing optimizations

  Inspect the already-written changes from `cheapest-test-boundary`.

  Determine:
  - Which optimizations are correct.
  - Whether their unique regression coverage is preserved.
  - Whether the GitReader integration boundary remains valid.
  - Whether Core Sync retains its required E2E contracts.
  - Whether the removal of `prepare-local-cli.test.ts` is justified by actual boundary coverage.
  - Whether any implementation correction requires adjusting those changes.

  Reuse valid existing work rather than implementing equivalent changes again.

  Do not assume an earlier optimization is correct merely because its tests passed.

  Do not restart an unrestricted performance investigation.

  ## 7. Technical debt closure — mandatory

  The same PR must contain the validation and closure evidence for every debt it actually resolves.

  Use AICore's existing technical debt lifecycle.

  For each in-scope debt:
  1. Verify the exact original resolution criteria.
  2. Implement the necessary correction.
  3. Verify the corrected behavior.
  4. Verify architectural conformance independently of test pass counts.
  5. Preserve evidence in the appropriate ODD record and Log.
  6. Obtain the required independent review.
  7. Remove the debt from the open register only when all closure requirements are satisfied.

  Do not remove a debt merely because:
  - Tests pass.
  - The source file was moved.
  - A class was renamed.
  - A workaround exists.
  - A reviewer assumes the problem is fixed.

  Do not create a new validation framework just for debt removal.

  Use existing architecture validators and test infrastructure where possible.

  Leave unrelated or incompletely resolved debts open.

  Do not mix Warden/agent-permission debts into this PR unless an actual dependency is established and separately authorized.

  ## 8. Deliver in ONE dedicated branch and ONE PR

  The implementation, related tests, applicable ODD changes and debt closures must form **one coherent PR**.

  Use a dedicated branch based on the correct current `main`.

  Suggested branch name:

  `fix/architecture/implementation-testing-alignment`

  The name is a proposal; use the actual repository naming conventions.

  Before branch creation, verify that existing uncommitted changes can be transferred or preserved safely.

  **Never move all working-tree modifications blindly into the new branch.**

  All changes belonging to this workstream must be kept together, while unrelated changes remain untouched.

  Where files contain modifications from multiple workstreams, isolate the authorized changes at the appropriate granularity.

  Do not stage whole shared files if that would include unrelated work.

  Do not silently change unrelated version fields or ODD records.

  A single PR may contain several focused commits if required by AICore's established review and delivery workflow.

  Herald 📯 is the only agent authorized to perform Git/GitHub operations.

  ### Authorization boundary

  For this initial phase, I authorize repository inspection, evidence preservation, and a safe delivery proposal.

  **Do not create the new branch, commits, push or PR until you have established the exact scope and safe handling of the existing uncommitted changes and obtained my approval.**

  Once authorized, the final PR must contain all and only the approved implementation/testing work.

  Merge remains my decision.

  ## 9. Preserve other repositories and existing work

  Work exclusively within the AICore source repository.

  Do not modify:
  - Downstream destination repositories.
  - The TISMART reference repository.
  - Unrelated agent implementations.
  - Unrelated security or permission configurations.
  - Already delivered Warden/Forge corrections.
  - Any file outside the authorized implementation/testing scope.

  Do not perform automatic downstream synchronization.

  No commits, pushes, PRs or merges outside Herald's separately authorized workflow.

  ## 10. Validation strategy

  Validate in this order:
  1. Correct application architecture.
  2. Direct use-case behavior.
  3. Relevant adapter integration.
  4. Assembled entry-point behavior.
  5. Test organization and classification.
  6. Test efficiency and regression protection.
  7. Relevant ODD and architecture validators.
  8. Required package verification.
  9. Debt resolution criteria.
  10. Independent semantic acceptance.

  Reuse valid existing evidence when relevant inputs have not changed.

  Avoid unnecessary full-suite repetition.

  Do not accept green tests as proof that C3, T2, T4 or T5 are satisfied.

  Do not claim complete verification if the working tree contains unrelated changes that affect the result.

  ## 11. First-session deliverable and stop condition

  Before implementation or branch creation, provide a concise evidence-based report:
  1. Current Git state, including all relevant uncommitted changes.
  2. Exact ownership of the existing modifications.
  3. Confirmed implementation architecture violations.
  4. Related testing violations and already-written corrections.
  5. Technical debts actually in scope.
  6. Technical debts explicitly excluded.
  7. Smallest coherent implementation/testing scope.
  8. Expected affected packages and files.
  9. Warning if the work is materially large or complex.
  10. Safe strategy for creating the dedicated branch without losing or mixing changes.
  11. Proposed implementation order.
  12. One-PR delivery plan.
  13. Exact authorization required to proceed.

  **Do not begin a broad audit or unrelated refactoring.**

  Do not make architectural recommendations without first inspecting the actual repository.

  Do not manufacture additional requirements or complexity.

  If the existing uncommitted work is valid and safely reusable, preserve it and incorporate it into the proposed delivery.

  If parts are invalid, identify them with evidence before proposing any replacement.

  **The goal is to correct implementation architecture, then align testing, and finally close the relevant debts—all in one isolated PR.**

  Finish the initial evidence and scope assessment, then stop for my authorization.

  Notify me definitively when that phase is complete, including any limitations.

- L2 — 2026-11-17 — User approval and decisions, verbatim:

  # AICore — Approved Implementation and Testing Alignment

  I reviewed your seven findings and scope assessment.

  **I approve the bounded implementation/testing remediation in ONE dedicated branch and ONE pull request.**

  The objective remains:
  1. Correct the confirmed application architecture violation.
  2. Align the affected tests with the corrected implementation.
  3. Preserve and repair the existing uncommitted testing optimizations.
  4. Validate the corresponding technical-debt resolution criteria.
  5. Deliver everything in one independently reviewed PR.

  Do not turn this into a repository-wide architecture migration.

  ## 1. Decisions on your findings

  **F1 — APPROVED**

  Correct the confirmed C3 violation in `odd-adviser`.

  Introduce the appropriate `EvaluateEvidence` use-case class with its `execute()` contract and constructor-injected dependencies.

  Preserve existing behavior and the established composition boundaries.

  Keep `toUnavailableAdvisory`, `answersNoQuestion`, and other genuinely pure helpers as functions.

  Do not introduce unnecessary new ports, wrappers, interfaces, or factories.

  Before modifying the five affected application tests, read their actual contents and determine the minimal required changes.

  **F2 — APPROVED CONDITIONALLY**

  Reverify `architecture-contract` R1 after completing and testing the C3 correction.

  R1 must not be considered satisfied merely because its checkbox was previously marked.

  Keep its final status consistent with verified implementation evidence.

  **F3 — RESTORE COVERAGE**

  Restore the unique real-Git `mergeBase` disjoint-history assertion.

  Reuse the existing collapsed fixture where possible.

  Do not create another expensive repository fixture solely for this assertion.

  Do not weaken the original behavior contract.

  **F4 — PRESERVE THE E2E BOUNDARY**

  Restore one minimal representative E2E test exercising the actual assembled `prepare-local` command.

  The test must validate real command behavior, not merely call the application use case directly.

  Use the cheapest fixture that still proves the actual entry-point contract.

  Avoid duplicating the migrated EEXIST assertion unnecessarily.

  DEBT-053 cannot close if this unique coverage is lost.

  **F5 — CORRECT THE FACTUAL COUNT**

  Correct the DEBT-056 count from thirteen to twelve if the measured count remains twelve.

  This is a documentation correction, not authorization to resolve or remove DEBT-056.

  Do not expand into the full parity-test migration.

  **F6 — CORRECT THE FEATURE STATUS**

  Reverify the actual R10 contract and the 30 reported tests under production source trees.

  If those tests violate R10, mark the requirement unsatisfied and record the existing DEBT-046 as the reason.

  Allow `architecture-contract` to become `partial` if that is its truthful derived status.

  Do not migrate those 30 tests in this PR.

  Do not weaken or reinterpret R10 just to preserve `achieved`.

  **F7 — CORRECT THE BRANCH RECORD**

  Update `cheapest-test-boundary` to reference the actual branch and delivery evidence.

  Do not retain the obsolete branch attribution.

  ## 2. Technical debt disposition

  Authorized closure candidates:
  - **DEBT-047:** Close only after the C3 correction, affected consumers, tests, and architectural acceptance are verified.
  - **DEBT-053:** Close only after the efficiency improvement and preserved real-Git/CLI regression coverage are demonstrated.

  Must remain open:
  - **DEBT-055:** Add the missing T2 units for the identified use cases, but do not retire the debt while its remaining classification issues are unresolved.
  - **DEBT-056:** Correct the factual count only. Do not change test routing or classification in this PR.
  - **DEBT-046:** Preserve as open and reconcile R10's truthful status.

  Do not touch unrelated debts.

  For every debt actually resolved, apply AICore's existing debt-retirement procedure in this same PR, preserving evidence in its ODD records.

  Do not develop a new debt validation framework.

  ## 3. Authorize the dedicated working branch

  Herald 📯 is authorized to create:

  `fix/architecture/implementation-testing-alignment`

  from the verified current `main` revision.

  All existing uncommitted changes belong to the assessed cheapest-test-boundary workstream, according to your inventory.

  Before the branch transition:
  - Capture the current status, tracked changes, intentional deletion, and untracked file inventory.
  - Preserve the two existing stashes and unrelated detached worktrees.
  - Verify the target branch name is unused.

  Because the new branch begins at the same commit, use the minimal safe branch operation without rewriting files.

  Immediately verify that the tracked and untracked working-tree state is byte-identical to the pre-branch baseline.

  If any modification is lost, unexpectedly changed, or unaccounted for, stop.

  Do not use stash, reset, clean, worktree removal, forced checkout, symlinks, or junctions.

  Herald remains the sole Git/GitHub executor.

  ## 4. Implementation order

  Follow this order:

  **Phase A — Implementation**

  Correct the `EvaluateEvidence` use case and update only necessary production consumers.

  Preserve externally observable behavior.

  **Phase B — Direct application tests**

  Update the existing affected `odd-adviser` tests.

  Add the two missing T2 use-case test suites:
  - `ReconcileDestination`
  - `RunAdvancedCommand`

  Use their real `execute()` contracts and appropriate injected test doubles.

  Do not manufacture additional unit-test targets.

  **Phase C — Existing test optimizations**

  Retain the previously written Core Sync representative-source optimization.

  Repair F3 and F4 before accepting the `git-pr-workflow` test reduction.

  Preserve valid integration and E2E boundaries.

  **Phase D — Documentation and debt closure**

  Update the relevant ODD records, R1/R10 truthfulness, branch attribution, and eligible debt closures.

  Keep DEBT-046/055/056 open.

  ## 5. Scope and complexity limit

  I acknowledge your warning that this delivery is larger than AICore's usual 400-line feature strategy threshold.

  This is an explicit approval for the bounded scope you identified, including the previously authored changes.

  It is **not** authorization for a broader refactor.

  Do not expand into:
  - Migrating the 30 colocated tests.
  - Reclassifying all Core Sync parity suites.
  - Redesigning Vitest configuration.
  - Creating new application abstractions.
  - Modifying Warden, Herald, or other agent permissions.
  - Refactoring other application operations that already satisfy C3.
  - Adding new development dependencies or frameworks.

  If actual implementation exposes a materially larger independent problem, report it instead of silently expanding scope.

  ## 6. Validation and acceptance

  Validate the corrected code and its affected tests.

  Use the established package commands and architecture validation contracts.

  Verify the following explicitly:
  - C3 compliance of the corrected application use case.
  - Preservation of the five affected application-test behaviors.
  - T2 coverage for both identified CLI use cases.
  - Real-Git `mergeBase` disjoint-history behavior.
  - A real `prepare-local` CLI E2E scenario.
  - Existing Core Sync E2E coverage with reduced fixture cost.
  - Correct and nonduplicated test classification.
  - Relevant lint, formatting, typecheck, package tests, and ODD validators.
  - DEBT-047 and DEBT-053 resolution criteria.
  - Accurate remaining status of DEBT-046/055/056.

  Do not treat passing tests as proof of architectural compliance.

  Reuse unchanged evidence where valid.

  Use Crucible 🔥 and Sentinel 🛡️ for their established responsibilities and obtain the required independent semantic acceptance from Inquisitor 🔎 according to the actual repository workflow.

  Resolve concrete findings without starting unrelated audits.

  ## 7. ONE PR delivery

  Once implementation, tests, architecture evidence, and review are satisfactory, Herald is authorized to:
  1. Stage only the exact authorized files.
  2. Create focused commits separating the implementation correction, direct use-case tests, and testing-boundary improvements as appropriate.
  3. Include the corresponding ODD records and debt evidence.
  4. Verify the complete base-to-head diff for unrelated changes.
  5. Push the dedicated branch.
  6. Open exactly ONE PR against `main`.

  All reviewed work belongs in that one PR.

  Do not create separate PRs for implementation, tests, ODD, or technical debt.

  Do not include unrelated files merely because they are locally modified.

  Do not publish if any unrelated work has entered the commit range or if required architecture validation has failed.

  **No merge is authorized. I retain the final merge decision.**

  ## 8. Mandatory final completion report

  When the authorized work is complete, provide:
  1. Branch name, base and head SHA.
  2. The exact implementation correction.
  3. Tests added, restored, removed, or reorganized.
  4. Proof that F3 and F4 coverage gaps are resolved.
  5. Relevant validation results.
  6. DEBT-047/053 resolution and retirement evidence.
  7. Remaining DEBT-046/055/056 status.
  8. `architecture-contract` R1 and R10 status.
  9. ODD lifecycle and review evidence.
  10. The single PR URL and final independent review verdict.
  11. Any remaining limitations.

  Notify me definitively when everything authorized is completed.

  Do not stop with an ambiguous progress update or reopen already-settled decisions.

  **Expected result: one PR with the confirmed C3 implementation correction, aligned tests, repaired existing testing optimizations, and evidence-backed debt retirement—without expanding into unrelated architecture migrations.**

- L3 — 2026-11-17 — Classification: non-small. Three packages' source and tests plus the debt register and two durable feature files cannot be resumed from a request plus a diff. Durable feature files: no new file is created — the affected capabilities already own files. `odd/features/architecture-contract.md` owns the use-case and test-placement requirements this change re-verifies (R1, R10), and `odd/features/cheapest-test-boundary.md` owns the boundary requirements the retained optimization delivers (R1–R4); `odd/features/typescript-testing.md` is unaffected because no runner changes. Creating a third durable file named for this change would name the change rather than a capability, which the feature-file rule forbids.
- L4 — 2026-11-17 — Branch created. Herald 📯 created `fix/architecture/implementation-testing-alignment` from `e7002448f5af3d369c6aa97f63e1b8e7ae265fbf` with the minimal `git switch -c` operation; pre/post `git status --porcelain=v1 -uall` and `git diff --numstat` were byte-identical, both untracked ODD files retained their line and byte counts, and both stashes and the two detached PR-192 worktrees were unchanged. No stash, reset, clean, worktree removal or forced checkout was used.
- L5 — 2026-11-17 — F1 preparation. The five affected application specs were read in body before any edit: `evaluate-deadline-cleanup`, `evaluate-evidence-leak`, `evaluate-invocation`, `evaluate-outcome` and `evaluate-timeout`. All five call the operation positionally as `evaluateEvidence(message, evaluator, options, deadline)`, so the minimal test delta is one call expression per test; no assertion, fixture or `describe` group needs to change. The deadline port is documented as a per-evaluation capability supplied by composition (`domain/deadline.ts:1-7`), which makes it a constructor collaborator alongside the evaluator port rather than an `execute()` argument.
- L6 — 2026-11-17 — Durable feature `architecture-contract`: R1 is re-verified by this change after the C3 correction lands. R10 is found **unsatisfied at the start of this change**: 23 test files live under `.opencode/plugins/odd-adviser/src/**` and 7 under `mcp-servers/system-one/src/**`, both production source trees, which R10 forbids; DEBT-046 already records the same subject as open. Per the feature-file rule R10's tick is removed and its cause recorded in this record rather than the requirement being reinterpreted; that feature's derived status becomes `partial`. No test file is migrated by this change.
- L7 — 2026-11-17 — Durable feature `cheapest-test-boundary`: this change delivers R1–R4 through the retained Core Sync and git-pr-workflow optimizations plus the repaired F3 and F4 coverage; each requirement is re-verified by the change that delivers it before its tick is set, and the evidence lives in this record's task rows and commits.
- L8 — 2026-11-17 — Independent review round 1 on the uncommitted candidate: Crucible 🔥 `[PASS]` (zero findings), Bastion 🧱 `[PASS]` (zero findings, four INFO observations none created by this change), Sentinel 🛡️ `[FAIL]` with four findings. All four were remediated before round 2: the accounting identity, the missing instruction-surface spec (now S13/T10), the retirement-evidence ordering (now L9 bound to commits), and the task-row statuses. Round 2 confirmed the first, second and fourth fixed and left the retirement evidence open, which L9 now supplies. Detail: the reviewers' returns and the PR body evidence rows.
- L9 — 2026-11-17 — DEBT-047 and DEBT-053 retired in this delivering work unit. **DEBT-047** criterion: the affected operation becomes a class in its existing application module with one `execute()` and constructor-injected collaborators, no base class/forwarding wrapper/invented framework class, the composition site constructs it and calls `execute()`, the package's approved suite passes, and the change is reviewed under the implementation gate. Result: `EvaluateEvidence` is a class in the module that already held the operation, with `execute(message, options)` and `{ evaluator, deadline }` injected; composition at the plugin entry and the host adapter constructs and calls it; no base class, interface, factory, forwarding wrapper or new port was added; `pnpm --dir .opencode/plugins/odd-adviser exec vitest run` reports 24 files / 73 tests passing and the package typecheck is clean; Bastion 🧱 returned `[PASS]` on C3 conformance. The entry's Python and skill-utility subjects were already recorded historical, so the plugin was its only current subject. Delivered by commit `50344ea`. **DEBT-053** criterion: share one deterministic committed fixture per file where the tests only read it, or an equivalent measurable reduction, without weakening any assertion and without replacing real-Git coverage with mocks; a mutating test keeps its own fixture; the suite passes and the measured duration and fixture cost are re-recorded. Result: one committed fixture serves the real-Git consumer, the redundant per-test rebuilds are gone, and `pnpm --dir .agents/skills/git-pr-workflow exec vitest run` reports 12 files / 66 tests passing in **2.36 s** against the **20.97 s** package wall clock measured when the debt was recorded; no assertion was weakened — the single real-Git smoke still maps commits, rename destination, metacharacter path, unresolved revision, disjoint-history `mergeBase` and a failing read, with the disjoint-history observation restored at two object-only `git` spawns on the fixture that already existed, and the assembled `prepare-local` entry point keeps its own end-to-end scenario; the exclusive-create case remains on a Git-free CLI test rather than being duplicated; the test count rose from 65 to 66 because coverage was restored, not reduced; Crucible 🔥 returned `[PASS]`. Delivered by commit `20e58d4`. Both entries were removed from `.aicore/core/knowledge/debt.md` in the commit that carries this evidence.
- L10 — 2026-11-17 — Remaining status recorded, not closed. `architecture-contract` R1 was re-verified true after the correction by reading every subject — the six `cli/aicore` operations, `system-one`'s `EvaluateOddEvidence`, the skill utilities' application modules and the corrected plugin — so its tick stands; R10 was found unsatisfied at the start of this change (23 colocated plugin test files and 7 colocated `system-one` test files), its tick was removed and DEBT-046 records the cause, which makes that feature `partial` by its own derivation. DEBT-056's count was corrected from thirteen to twelve against a measured count of twelve `*.parity.spec.ts` files with no test moved between levels. DEBT-055 keeps a state note recording the delivered `ReconcileDestination` and `RunAdvancedCommand` units and the classification work it still owes. T4, T7, T8 and T10 remain `in progress` and T9 remains `open`: the records and register land with this commit, and the push, the pull-request publication and the independent verdict at the immutable head are still outstanding, so this record stays `active` — closing it is not delivery.
