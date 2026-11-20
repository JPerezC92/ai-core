# ODD work-unit commit policy and lifecycle enforcement

> **Status:** closed
> **Closed:** 2026-11-20
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-20
> **Objective:** Adopt the official ODD reviewable work-unit commit policy and make the ODD lifecycle complete, be independently accepted, and be committed before PR management begins.
> **Branch:** `docs/odd/work-unit-commit-policy`, created by Herald 📯 (Release Manager) from fetched `origin/main` at `af9dc6068d85a832f57e43d8ea43a04ab10aa01a`.
> **Delivery:** One consolidated PR. Thirteen paths, documentation and contract only, no code. Strategy `single-pr`; authored additions forecast roughly 350–450 lines across four work units plus the closure edit, at or below the ~400-line review budget per unit, so no chained delivery is needed.
> **Runner:** `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks`; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts odd/features`.

## Specs

- S1 — A commit represents one coherent, reviewable work unit rather than one task, and related tasks may share a commit. Exact requirement: "One commit per coherent, reviewable work unit, not necessarily per task." Acceptance: read the feature-document task-row rule and the delivery forecast; observe that a single commit may evidence several tasks and that no rule requires one commit per task.
- S2 — A high-risk work unit receives its own commit. Exact requirement: "High-risk units must have independent commits." Acceptance: read the task-row rule; observe a mandatory, not permissive, requirement that each high-risk unit carries its own commit.
- S3 — Tests and documentation accompany the behaviour they serve within the same work unit. Exact requirement: "Tests and documentation accompany their corresponding behavior." Acceptance: read the implementation rule; observe that a work unit ships its own tests and documentation.
- S4 — Every completed task records the real commit containing its work. Exact requirement: "Each completed task records the real commit containing its work." Acceptance: run the task-record validator over a `done` row; observe a 7–64 character hexadecimal reference is required and that a pending reference is rejected.
- S5 — The review budget is advisory and never justifies deleting useful material. Exact requirement: "Review budgets are advisory and must not encourage deleting useful material." Acceptance: read the delivery-forecast rule; observe the budget is advisory and that removing tests, documentation, comments or blank lines to fit it is forbidden.
- S6 — A commit message describes the delivered outcome, not a file inventory. Exact requirement: "Commit messages describe delivered outcomes." Acceptance: read the commit-message body rule; observe that bullets state outcomes and are not grouped as a path list.
- S7 — A work unit carries a meaningful rollback boundary. Exact requirement: "Work units have meaningful rollback boundaries." Acceptance: read the delivery-forecast rule; observe each planned unit records the files and behaviour removable without unrelated work.
- S8 — Independent semantic acceptance precedes closure, is tied to immutable commit evidence, and is never substituted by test results. Exact requirement: "Independent semantic acceptance before ODD closure." Acceptance: read the closure rule; observe the independence basis, the pinned-commit evidence and an explicit statement that specialist gates and passing suites are inputs, not acceptance.
- S9 — The ODD record is closed and its closure committed before PR management begins, with no post-publication closure stage. Exact requirement: "The ODD record must be completed, independently accepted, closed, and committed before PR management begins." Acceptance: read the completion-stage rule; observe closure and its commit precede PR publication and that no stage closes the record after publication.
- S10 — A pre-PR guard refuses PR management on an absent, incomplete or uncommitted closure, and permits the artifact-free path only through the existing small-work classification. Exact requirement: "Reject a missing record when ODD is required." and "Never accept an agent's unsupported claim that ODD is not applicable." Acceptance: read the release-manager guard; observe the three outcomes, the three required classification tests, and refusal of a bare not-applicable claim.
- S11 — The PR reviewer verifies the governing record at the immutable PR head. Exact requirement: "Inquisitor must verify the governing ODD record against the actual immutable PR HEAD." Acceptance: read the reviewer contract; observe a duty to establish the applicable record and verify its closure at head, and to withhold a passing verdict otherwise.
- S12 — Post-publication remediation reopens and recloses under the same conditions and cannot become a scope licence. Exact requirement: "This is an exceptional remediation path, not the normal ODD lifecycle." Acceptance: read the completion-stage reopen rule; observe the finding-bound authorization, the limited work scope, the removed closure entry, the repeated acceptance and closure, and the fresh head review.
- S13 — DEBT-048, DEBT-060 and DEBT-062 are aligned without being marked resolved. Exact requirement: "Updates to DEBT-048, DEBT-060, and DEBT-062 without prematurely marking them resolved." Acceptance: read the register; observe each entry records the correction and remains open.
- S14 — The merge decision remains the user's alone. Exact requirement: "Do not merge the PR. The merge decision belongs exclusively to me." Acceptance: inspect the PR state; observe it open and unmerged.

## Tasks

- T1 | S1, S2, S3, S5, S6, S7 | inline (single-author documentation unit across two skill files) — Cipher 🔓 (Lead Orchestrator) | done | commit: cc8a575
- T2 | S8, S9, S12 | inline (lifecycle ordering in the canonical ODD owner plus the durable requirement) — Cipher 🔓 (Lead Orchestrator) | done | commit: b8a2870
- T3 | S10, S11 | delegated (agent-runtime contract change, independently audited) — Sentinel 🛡️ (Quality Guardian) | done | commit: 0da3edaf6b5d535131514bf77d477714cc2257be
- T4 | S13 | inline (register state alignment) — Cipher 🔓 (Lead Orchestrator) | done | commit: 05688ea7bcb0cfee9a6f00c2dc247a7f3b64f74c
- T5 | S8, S9, S12, S14 | delegated (independent semantic acceptance at the committed candidate) — Sentinel 🛡️ (Quality Guardian) | done | commit: 05688ea7bcb0cfee9a6f00c2dc247a7f3b64f74c
- T6 | S4 | delegated (Git execution and the work-unit commits) — Herald 📯 (Release Manager) | done | commit: 05688ea7bcb0cfee9a6f00c2dc247a7f3b64f74c

## Log

- L1 — Original request, verbatim:

  # AICore — Adopt Official ODD Work-Unit Commit Policy and Fix Recurring Lifecycle Failures

  **Mode: PLAN — Investigation and design only. No implementation authorized.**

  I reviewed your investigation into PR #207 and identified an additional requirement.

  **AICore must adopt the current official Organic Driven Development (ODD) commit policy maintained by Alan Buscaglia in Gentle AI.**

  This is an explicit architectural policy decision. Your responsibility is to investigate how to integrate it correctly into AICore's existing workflow while fixing the recurring ODD lifecycle failures.

  ## 1. Official ODD policy — authoritative references

  Review these sources directly:

  - https://github.com/Gentleman-Programming/gentle-ai/issues/5529
  - https://github.com/Gentleman-Programming/gentle-ai/blob/main/internal/assets/skills/work-unit-commits/SKILL.md

  Issue #5529, approved October 15, 2026, changed ODD from per-task commits to reviewable work-unit commits.

  Adopt the following principles:

  1. Commit by coherent, reviewable work unit, not mechanically by individual task.
  2. A single commit may contain multiple related ODD tasks.
  3. A work unit must represent a meaningful behavior, fix, migration, or documentation outcome.
  4. Keep relevant tests and documentation alongside the behavior they verify or explain.
  5. Use Conventional Commit messages.
  6. Treat approximately 400 authored changed lines as a review-budget guideline, not a strict limit.
  7. Give high-risk units their own commits.
  8. Each completed ODD task must identify the commit containing its implementation.
  9. Review candidates must correspond to actual commit or PR-slice boundaries, not arbitrary TODO checkboxes.
  10. Preserve independently understandable commits and reasonable rollback boundaries.

  Do not introduce unnecessary commits, artificial splits, or unrelated work merely to satisfy a numerical target.

  The official policy is the baseline. Preserve AICore-specific restrictions where they are stricter and compatible with it.

  ## 2. Investigate AICore's existing commit discipline

  Inspect the current ODD workflow, including:

  - `.agents/skills/odd-workflow/SKILL.md`
  - `.agents/skills/git-pr/`
  - `.opencode/agents/herald.md`
  - Relevant ODD feature/task validators.
  - Relevant PR publication and review contracts.

  Determine:

  - Which official ODD commit requirements AICore already satisfies.
  - Which requirements are missing.
  - Which local rules contradict the official policy.
  - Which existing components own work-unit planning, commit execution, task evidence, and lifecycle transitions.
  - Whether work-unit boundaries are established before or during implementation.
  - How task-to-commit evidence is maintained.

  Do not copy Gentle AI's implementation wholesale.

  Adapt the policy to AICore's established architecture and execution model.

  **Herald remains the only agent authorized to execute Git/GitHub operations.**

  Other agents may plan work units and prepare evidence, but must not directly execute commits.

  ## 3. Investigate the PR #207 failure

  The investigation established that PR #207 was published with seven task rows still showing:

  `in progress | commit: pending`

  The governing ODD record remained active, although the implementation had been committed and the PR was independently reviewed.

  Address these failures separately:

  **A. Work-unit commit discipline**

  How should AICore ensure completed work units are committed at the appropriate boundaries?

  **B. Task-to-commit traceability**

  How should every completed ODD task receive a valid reference to the commit containing its work?

  **C. Task-state synchronization**

  How should the workflow prevent implemented work from remaining indefinitely marked `in progress` with `commit: pending`?

  **D. ODD record closure**

  How should the workflow complete all required closure steps without incorrectly postponing them until after merge?

  **E. PR readiness**

  How should the workflow prevent a PR from being declared fully ready while mandatory lifecycle obligations remain incomplete?

  Do not assume that these five requirements must be enforced by one component.

  Identify their existing canonical owners.

  ## 4. Design reliable enforcement

  Your previous proposal relied primarily on documentation changes and a new mandatory checklist item.

  That is not enough without proof of enforcement.

  Investigate whether existing validators, PR gates, or review mechanisms can reliably detect these failures.

  You must explain:

  1. What checks run mechanically today.
  2. What checks depend only on agent compliance.
  3. How an agent could bypass or misreport each requirement.
  4. Which existing enforcement owner can prevent that failure.
  5. Whether a minimal code change is necessary.
  6. How to prevent unnecessary duplicate validation.

  Prefer extending existing canonical enforcement rather than introducing new scripts, validators, layers, or state machines.

  Any proposed mechanical check must validate authoritative evidence rather than merely trusting a checkbox.

  A task marked `in progress` can legitimately be unfinished during implementation. Do not introduce a rule that rejects normal intermediate states.

  Enforcement must occur at the correct lifecycle boundary.

  ## 5. Resolve the review and closure sequence

  Your investigation identified this existing sequence:

  - Stage 3: PR publication.
  - Stage 4: ODD closure.
  - Stage 5: Merge.

  Preserve the principle that closure does not depend on merge evidence.

  However, investigate how to make PR readiness reflect the completion of all mandatory pre-merge obligations.

  Resolve these questions:

  - Which independent review satisfies the semantic acceptance prerequisite for closure?
  - When is the closure commit created?
  - Does closure advance the PR head?
  - When is head-bound review required again?
  - What happens if that review identifies findings?
  - Can the record remain closed if new implementation work becomes necessary?
  - Can the process avoid unnecessary repeated full reviews without weakening verification?
  - How should the agent report a published PR that is not yet ready?

  Do not reorder lifecycle stages arbitrarily.

  Distinguish PR publication, PR readiness, ODD closure, and user-authorized merge.

  ## 6. Respect work-unit boundaries and evidence integrity

  Design the expected flow for a normal multi-task feature.

  For example:

  - Tasks T1 and T2 form one coherent work unit.
  - Task T3 forms a separate high-risk work unit.
  - Task T4 is a related documentation or integration unit.

  Explain how the official commit policy applies, including which tasks may share commit references and when Herald performs the commits.

  This is a conceptual walkthrough only.

  Do not create synthetic repositories, branches, commits, agent tasks, or PRs.

  The design must ensure that commit references correspond to real commits containing the specified work.

  Do not fabricate commit references, prematurely mark tasks complete, or create bookkeeping commits solely to disguise missing evidence.

  ## 7. Complete inspection of existing enforcement ownership

  Before proposing modifications, read:

  `.agents/skills/git-pr/references/_pr-evidence-format.md`

  Identify its actual consumers.

  Inspect the existing implementation responsible for:

  - Work-unit commit planning.
  - ODD task status validation.
  - Commit reference validation.
  - ODD record closure.
  - PR publication.
  - Required evidence verification.
  - Inquisitor's head-bound review.
  - Herald's readiness reporting.

  Your file-change proposal must be based on verified ownership.

  Do not modify a file merely because its name suggests responsibility.

  ## 8. Compare minimal implementation approaches

  Evaluate:

  **Option A — Documentation and process correction**

  Correct the existing instructions and execution sequence without changing code.

  **Option B — Documentation plus targeted enforcement**

  Correct the instructions and add the minimum necessary checks inside the existing canonical enforcement mechanisms.

  For each option explain:

  - Which failure modes it prevents.
  - Which failure modes remain possible.
  - Implementation complexity.
  - Review and runtime overhead.
  - Maintenance cost.
  - Compatibility with official ODD.
  - Compatibility with AICore's existing architecture.

  Recommend the smallest approach that actually addresses recurrence.

  Do not create unnecessary infrastructure.

  ## 9. Technical debt disposition

  Inspect the existing debt register, particularly:

  - DEBT-048
  - DEBT-060
  - Related entries only where directly applicable.

  Determine whether the official-policy adoption and recurring execution failures should update these existing entries or require a distinct debt entry.

  Avoid duplicates.

  Do not mark existing debt resolved until remediation is implemented and independently verified.

  ## 10. Required final investigation report

  Return the following:

  1. **Official ODD policy:** exact requirements and source references.
  2. **AICore compatibility matrix:** compliant, missing, conflicting, or unverified.
  3. **PR #207 root cause:** confirmed evidence, not assumptions.
  4. **Commit-discipline design:** reviewable work units, risk exceptions, and task mapping.
  5. **Lifecycle design:** exact sequence from implementation through PR readiness and closure.
  6. **Enforcement design:** canonical owners and specific checks.
  7. **Alternatives:** Option A versus Option B.
  8. **Exact change inventory:** files to create, modify, or delete, with justification.
  9. **Validation plan:** focused tests and existing evidence-based walkthroughs.
  10. **Debt disposition:** reuse versus new entry.
  11. **Risks and limitations:** including additional review or commit overhead.
  12. **Authorization boundary:** exact implementation scope requiring my approval.

  ## Non-negotiable restrictions

  - PLAN mode only.
  - Do not modify files.
  - Do not perform Git/GitHub mutations.
  - No commits, branches, PRs, pushes, or merges.
  - Do not modify PR #207 retroactively.
  - Do not modify the active ODD task record on main.
  - Do not change destination repositories.
  - Do not place unrelated functionality in `cli/aicore`; it is exclusively for Core Sync.
  - Do not create new validators or scripts without proving existing mechanisms are insufficient.
  - Do not create synthetic agent tasks or PRs to reproduce historical failures.
  - Do not introduce mandatory per-task commits.
  - Do not weaken Herald's exclusive Git authority.
  - Do not weaken Inquisitor's independent review responsibility.
  - Do not treat investigation as implementation authorization.

  **The user has decided to adopt the official ODD commit policy. The implementation design, specific file changes, and remediation scope still require explicit approval.**

- L2 — 2026-11-20 — User correction, verbatim:

  # Critical Correction — ODD Must Be Closed Before PR Management Begins

  Your previous lifecycle proposal is based on an incorrect premise.

  **In AICore, the entire ODD task lifecycle must be completed and closed BEFORE initiating Pull Request management.**

  This is an explicit user requirement and overrides the proposed publication → review → closure → re-review sequence.

  Do not design the workflow around publishing a PR with an active ODD record.

  ## 1. Correct the lifecycle sequence

  The required order is:

  1. Plan coherent, reviewable work units according to the current official ODD policy.
  2. Implement each authorized work unit with its relevant tests and documentation.
  3. Have Herald create the appropriate work-unit commits.
  4. Update every completed ODD task with the real commit containing its implementation.
  5. Complete all required technical verification, evidence, and independent semantic acceptance.
  6. Close the governing ODD record, including its required completion evidence.
  7. Have Herald commit the completed closure record.
  8. Only after the closure is committed, begin the GitHub Pull Request management workflow.
  9. Prepare, publish, and independently review the PR at its actual HEAD.
  10. Report PR readiness only after all required PR checks pass.
  11. Leave the merge decision exclusively to the user.

  **An active ODD record must prevent the start of PR management, not merely prevent a final readiness announcement.**

  Do not add a normal post-publication closure stage.

  ## 2. Resolve independent acceptance before PR publication

  Your earlier proposal assumed that independent semantic acceptance must occur through review of a published PR.

  That assumption must be investigated and corrected.

  Determine:

  - Which existing actor provides semantic acceptance.
  - Whether independent acceptance can be performed against immutable local commit evidence before publishing a PR.
  - Which existing contracts currently couple ODD closure to PR review.
  - Whether the current process contains an actual dependency cycle.
  - How to resolve it without weakening independent review.
  - How the closure commit is verified before PR management begins.

  Do not invent acceptance evidence.

  Do not automatically treat passing tests as equivalent to independent semantic acceptance.

  Preserve Inquisitor's independent PR-review responsibilities.

  ## 3. Enforce ODD closure at the correct boundary

  Your proposed change to `validatePublication()` may still be useful, but it is not sufficient as the primary enforcement mechanism.

  That validator runs within PR management.

  The requirement is stronger:

  **PR management must not begin unless the governing ODD record has already been closed and its closure committed.**

  Inspect the existing entry point of the PR workflow and identify its canonical enforcement owner.

  Determine the smallest reliable mechanism to reject:

  - An active governing ODD record.
  - Unfinished task rows.
  - Missing or pending commit references.
  - Missing required closure evidence.
  - A closure edit that exists only in the working tree but has not been committed.
  - A record whose closed status does not correspond to the commit being processed.

  Ensure the control checks the appropriate authoritative repository state.

  Do not create a new validator or parallel workflow if an existing entry-point guard can enforce this.

  Do not rely exclusively on agents remembering instructions.

  ## 4. Adopt the official ODD work-unit commit policy completely

  Retain the approved policy direction:

  - One commit per coherent, reviewable work unit, not necessarily per task.
  - Related tasks may share one commit.
  - High-risk units must have independent commits.
  - Tests and documentation accompany their corresponding behavior.
  - Each completed task records the real commit containing its work.
  - Review budgets are advisory and must not encourage deleting useful material.
  - Commit messages describe delivered outcomes.
  - Work units have meaningful rollback boundaries.

  Herald remains the exclusive Git/GitHub executor.

  Do not create unnecessary commits or artificial task boundaries.

  The final ODD closure commit must be completed before PR management starts.

  ## 5. Reevaluate the proposed enforcement

  Your previous design proposed a mandatory lifecycle item in `git-pr/scripts/pr_content/domain/validation.ts`.

  Reevaluate whether that is the correct primary enforcement location.

  Distinguish:

  **Pre-PR entry gate**

  Prevents PR management from starting with an incomplete or uncommitted ODD closure.

  **PR review gate**

  Verifies the actual PR HEAD, evidence integrity, required checks, and review findings.

  Do not duplicate the same validation unnecessarily.

  If a secondary PR gate is justified as defense in depth, explain why.

  ## 6. Update the lifecycle contract

  The existing stage ordering must be reconciled with the new mandatory sequence.

  Do not preserve an incorrect stage order simply to avoid renumbering.

  Identify the exact canonical lifecycle document and every directly dependent instruction or validator that requires correction.

  The lifecycle must be internally consistent.

  ## 7. Revise the change inventory

  Your previous 14-path proposal was based on closure after PR publication.

  Reevaluate the inventory based on closure BEFORE PR management.

  For every proposed modification, explain:

  - Existing owner and exact location.
  - Required change.
  - Why the change is necessary.
  - Whether it adds enforcement or only documentation.
  - How it will be verified.

  Remove obsolete changes related to post-publication closure and repeated review cycles.

  Do not expand into unrelated refactoring.

  Keep DEBT-048, DEBT-060, and any directly relevant existing debt aligned with the corrected design.

  Do not retroactively repair PR #207 or modify its active ODD record on main. That remains separate.

  ## 8. Required final report

  Provide only:

  1. Corrected end-to-end lifecycle, with the ODD closure committed before PR management.
  2. Resolution of the independent-acceptance dependency.
  3. Exact pre-PR enforcement owner and proposed guard.
  4. PR review responsibilities after closure.
  5. Updated minimal file inventory.
  6. Focused validation plan, using existing tests and evidence.
  7. Remaining risks or limitations.
  8. Explicit implementation authorization request.

  ## Restrictions

  PLAN mode only.

  No file modifications, Git/GitHub mutations, commits, branches, PRs, pushes, or merges.

  No destination-repository changes.

  No new scripts, validators, agents, or architectural layers without demonstrated necessity.

  No unrelated functionality in `cli/aicore`.

  Do not weaken Herald's exclusive Git authority or the user's merge authority.

  **Do not implement anything until I explicitly approve the corrected design.**

  The fundamental invariant is:

  **No PR management begins until the ODD lifecycle is fully completed, independently accepted, closed, and committed.**

- L3 — 2026-11-20 — User correction, verbatim:

  # Final Adjustments Before Implementation Authorization

  Your corrected lifecycle design is accepted in principle.

  The governing invariant is now correct:

  **The ODD record must be completed, independently accepted, closed, and committed before PR management begins.**

  The official ODD work-unit commit policy must also be adopted completely.

  I have three final corrections to the proposed design.

  Remain in PLAN mode. No modifications or Git/GitHub mutations.

  ## 1. Scope the pre-PR guard correctly

  Your Herald guard currently refuses when the governing record is absent.

  Determine how the existing AICore contracts classify work that legitimately does not require an ODD governing record.

  The guard must:

  - Reject a missing record when ODD is required.
  - Reject incomplete or uncommitted closure.
  - Permit documented exceptions only when existing classification rules authorize them.
  - Avoid restricting unrelated GitHub operations beyond the relevant PR workflow.
  - Never accept an agent's unsupported claim that ODD is not applicable.

  Do not create new classification rules.

  ## 2. Define independent semantic acceptance precisely

  Verify that the selected pre-PR reviewer:

  - Is independent of the implementation author and evidence author.
  - Has authority and sufficient scope to evaluate the delivered feature.
  - Evaluates the actual committed implementation against the governing requirements.
  - Produces an explicit acceptance verdict tied to immutable commit evidence.
  - Does not merely substitute specialist test results for semantic acceptance.

  Preserve Inquisitor's separate independent PR-review responsibility.

  Do not introduce another agent or duplicate the complete PR-review process.

  ## 3. Specify post-publication remediation

  If Inquisitor identifies a defect after PR publication:

  - The existing PR remains the review vehicle.
  - The ODD record is reopened when implementation work invalidates its closure.
  - Additional authorized work follows the same work-unit commit discipline.
  - Task-to-commit evidence is updated accurately.
  - Independent acceptance and closure are repeated as required.
  - Herald commits the corrected closure before the PR can return to ready status.
  - Inquisitor reviews the updated immutable HEAD.
  - The user retains the exclusive merge decision.

  This is an exceptional remediation path, not the normal ODD lifecycle.

  Identify any additional restrictions needed to prevent agents from treating reopening as permission for unrelated changes.

  ## 4. Final implementation scope

  Preserve the existing 13-path proposal unless one of these three corrections demonstrably requires a change.

  Do not reintroduce the abandoned `git-pr` validator changes.

  Do not add scripts, validators, agents, or architectural layers without demonstrated necessity.

  Preserve Herald's exclusive Git/GitHub authority.

  Do not modify `cli/aicore`, destination repositories, PR #207, or its active governing record.

  Provide a concise final delta to your design:

  1. How the three corrections are addressed.
  2. Whether the 13-path inventory changes.
  3. Any remaining limitations.
  4. The exact scope ready for explicit implementation authorization.

  Do not repeat the prior investigation.

  **Stop after this final design correction. Do not implement until explicitly authorized.**

- L4 — 2026-11-20 — Implementation authorization, verbatim:

  # Implementation Authorization — AICore ODD Lifecycle and Work-Unit Commit Policy

  Your final design is approved for implementation, subject to the two clarifications below.

  ## Authorized scope

  Implement the agreed 13-path proposal, including:

  - Adoption of the current official ODD reviewable work-unit commit policy.
  - Mandatory independent commits for high-risk units.
  - Accurate task-to-commit references.
  - Independent semantic acceptance before ODD closure.
  - Complete ODD closure and its commit before PR management begins.
  - The pre-PR closure guard owned by Herald.
  - Independent PR-head verification by Inquisitor.
  - Controlled reopening and reclosure when post-publication findings require implementation changes.
  - Updates to DEBT-048, DEBT-060, and DEBT-062 without prematurely marking them resolved.
  - Correction of R26 and the relevant canonical lifecycle instructions.

  ## Clarification 1 — NOT APPLICABLE

  The absence of `odd/tasks/` files in a diff is not sufficient to establish that ODD is inapplicable.

  Herald must apply the existing authoritative small-work classification criteria and refuse unsupported exceptions.

  Do not invent new classification rules.

  ## Clarification 2 — Inquisitor verification

  Inquisitor must verify the governing ODD record against the actual immutable PR HEAD.

  Do not rely exclusively on whether the record appears in the PR diff.

  If the applicable record cannot be established or its closure cannot be verified, do not report PASS.

  ## Execution requirements

  1. Create the governing ODD record according to the authorized bootstrap procedure.
  2. Implement the approved changes in coherent, reviewable work units.
  3. Keep tests and documentation with their corresponding units.
  4. Use focused tests and existing evidence-based walkthroughs.
  5. Have Herald alone execute the required Git operations and work-unit commits.
  6. Update task rows with their actual commit references.
  7. Obtain independent semantic acceptance.
  8. Complete and commit the governing ODD closure.
  9. Verify that the closure precondition passes before beginning PR management.
  10. Proceed through the existing PR publication and independent review workflow.
  11. Report the final PR status and evidence.

  Do not create artificial commits merely to increase commit count.

  Do not expand the approved scope, introduce unrelated tooling, or modify destination repositories.

  `cli/aicore` remains exclusively dedicated to Core Sync.

  Do not retroactively modify PR #207 or `odd/tasks/2026-11-20-debt-review.md`.

  Do not merge the PR. The merge decision belongs exclusively to me.

  If an unexpected architectural conflict or scope change is required, stop and request authorization rather than improvising.

  ## Completion criteria

  The implementation is complete only when:

  - All authorized changes are delivered.
  - Required focused validations pass.
  - The governing ODD record is closed and committed.
  - The pre-PR lifecycle guard has been verified against the existing real acceptance and rejection examples.
  - The PR is published and reviewed at the final immutable HEAD.
  - Inquisitor returns PASS with zero open findings.
  - Required checks pass.
  - No unauthorized changes remain.

  Provide an explicit **FINALIZED** or **BLOCKED** report, including the final HEAD, completed work units, validation evidence, PR URL if published, and any remaining limitations.

  Do not report completion merely because implementation commits or PR publication have occurred.

  **The PR must not be merged without my explicit decision.**

- L5 — 2026-11-20 — Classification: non-small. The scope spans two canonical lifecycle contracts, four enforcement and reporting contracts, a durable requirement, a debt-register alignment and this record; it changes cross-cutting behavioural rules and cannot be resumed from a request plus a diff. Bootstrap: this record is the sole authorized write before implementation. Branch `docs/odd/work-unit-commit-policy` created by Herald 📯 (Release Manager) from fetched `origin/main` at `af9dc6068d85a832f57e43d8ea43a04ab10aa01a` with a clean tree and no divergence; that branch was created before this record, so this file is the first content write. Mirror status: pending recovery, not synchronized — project `github.com-personal/JPerezC92/ai-core`, feature `odd-work-unit-commit-policy`, locator `odd/tasks/2026-11-20-odd-work-unit-commit-policy.md`; no stored copy exists and no backend identity was established.
- L6 — Work units planned before implementation, per S1–S3: **WU1** the official commit policy in `odd-workflow/SKILL.md` (delivery forecast, feature-document task rows, implement-and-verify) plus `git-commit/SKILL.md` body rules; **WU2** the lifecycle reordering and acceptance definition in `odd-workflow/SKILL.md` (completion stages, close) plus the durable requirement; **WU3** the enforcement and reporting contracts (`herald.md`, `inquisitor.md`, `release.md`, `agents.md`); **WU4** the register alignment. Each unit carries its own rollback boundary: WU1 and WU2 are separable by section within one skill file; WU3 separates cleanly from WU1/WU2 and is the only unit touching agent runtimes; WU4 touches only the register. No unit is high-risk under the risk triggers except WU3, which changes agent-runtime contracts and therefore receives its own commit and an independent Sentinel audit.
- L7 — 2026-11-20 — Work units delivered, each with its own focused check and rollback boundary. **WU1** `cc8a575` — official commit policy in `odd-workflow/SKILL.md` and `git-commit/SKILL.md`; rollback: those two files revert independently. **WU2** `b8a2870` — lifecycle reordering in `### Completion stages`, the acceptance definition in `### Close`, and the durable requirement; rollback: independently of WU1's text. **WU3** `0da3edaf6b5d535131514bf77d477714cc2257be` — the enforcement and reporting contracts; this is the high-risk unit and therefore carries its own commit, with an independent Sentinel 🛡️ (Quality Guardian) audit that returned `[FAIL]` in round 1 on five findings and `[PASS]` in round 2 with `fixed 5 · open 0`. **WU4** `05688ea7bcb0cfee9a6f00c2dc247a7f3b64f74c` — register alignment. Verification: `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks` reports every record `ok`; `validate_feature_file.ts odd/features` reports `ok odd\features\organic-driven-development.md — status: partial`. No task row referenced a commit before that commit existed, and no reference commit was manufactured.
- L8 — 2026-11-20 — Inventory disclosure and task-row correction. Two deviations from the approved thirteen-path list, both recorded rather than absorbed: `.agents/skills/odd-workflow/package.json` was version-aligned `2.7.0 → 2.8.0` so the skill frontmatter and its package marker do not diverge (WU1), making fourteen paths; and the former T6 covering "Git, closure commit and PR publication" was reduced to the work-unit commits, because pull-request publication is delivery under `### Delivery boundary` and not an ODD task, and a task row cannot reference the commit that carries it. S14 therefore has no task row and is verified from the published pull request instead. T5 remains `in progress` until independent acceptance returns.
- L9 — S1 — pass at `05688ea` — `### Create a feature document` now states that one authorized coherent work-unit commit may evidence several tasks and that no commit per task is required; `### Completion stages` stage 2 commits work in work-unit commits.
- L10 — S2 — pass at `05688ea` — the same rule makes a high-risk unit's own commit mandatory ("must carry"), and stage 2 repeats that binding, replacing the earlier permissive "may use".
- L11 — S3 — pass at `05688ea` — `### Implement and verify` binds tests and documentation to the work unit that changes the behaviour, and forbids deferring that material to a later unit to keep a diff small.
- L12 — S4 — pass at `05688ea` — `### Create a feature document` and `### Completion stages` require every `done` task to name the commit that actually carries its work, and the existing validator enforces the 7–64 character hexadecimal reference mechanically.
- L13 — S5 — pass at `05688ea` — `### Delivery forecast` keeps the ~400-line budget advisory and forbids deleting or compressing tests, documentation, comments or blank lines to fit it, requiring a slice or a reported overage instead.
- L14 — S6 — pass at `05688ea` — `git-commit` `### Body` requires the body to state what the change delivers and explicitly forbids making the changed-path list the body.
- L15 — S7 — pass at `05688ea` — `### Delivery forecast` requires every planned work unit to record its rollback boundary together with its own focused check and observed result.
- L16 — S8 — pass at `05688ea` — `### Close` defines the acceptor's independence, its authority by content domain, evaluation at a pinned commit against the record's own requirements, an explicit verdict naming that commit, and the rule that a specialist gate, green suite or validator pass is an input and never acceptance. Recorded limitation: authenticity of that verdict remains documentary, not mechanically distinguishable from an authored claim.
- L17 — S9 — pass at `05688ea` — `### Completion stages` now orders record closure and the closure commit ahead of pull-request publication, states that pull-request management may not begin before the closure stage, and states that no post-publication closure stage exists.
- L18 — S10 — pass at `05688ea` — the release-manager specification carries `#### Pull-request closure precondition`: delivery-route scoping, a committed-state closure proof, refusal of an open record, an unfinished task row, a pending reference and an uncommitted-only closure, and a not-applicable path restricted to the existing small-work classification with all three tests evidenced and a bare claim refused.
- L19 — S11 — pass at `05688ea` — the reviewer specification requires establishing the applicable record and verifying its closure at the immutable reviewed head, returning a blocking verdict otherwise, and its report anatomy carries a governing-record line.
- L20 — S12 — pass at `05688ea` — `### Completion stages` bounds reopening to a finding at the current head, limits new work to that finding, forbids replacement pull requests and history resets, removes the closure entry, and repeats verification, acceptance and closure before the pull request may return to ready.
- L21 — S13 — pass at `05688ea` — DEBT-048, DEBT-060 and DEBT-062 each gained a 2026-11-20 state entry and each explicitly remains open with no resolution claimed.
- L22 — S14 — pass at `05688ea` — no rule in the diff grants an agent merge authority; `### Completion stages` stage 9 and `### Delivery boundary` keep the merge user-only, and the release-manager and reviewer specifications are unchanged on that point. The record-level observation that the pull request is open and unmerged is deferred to the published head, which is delivery rather than closure.
- L23 — Independent semantic acceptance, and the first failure. Sentinel 🛡️ (Quality Guardian) returned **ACCEPT** at the pinned candidate `05688ea7bcb0cfee9a6f00c2dc247a7f3b64f74c`, with no requirement failed and two observations carried forward: the closure guard is agent-enforced rather than mechanically executed, and a task whose own deliverable is the record edit cannot name the commit that carries it. The **first failure** in this change was the WU3 edit-triggered audit, which returned `[FAIL]` in round 1 with five findings against `0da3eda` — an incorrect version-bump class, a surviving "close the record" instruction in step 8 that contradicted the new ordering, a stage-precondition restatement in the message-presentation rule, two undefined named states, and a missing governing-record line in the reviewer's report anatomy; all five were corrected and round 2 returned `[PASS]`. Independence: the acceptor authored none of the changes or evidence, and the green validator runs and passed audits were treated as inputs, not acceptance. T5 names `05688ea` because that is the candidate the acceptance evaluated; the entry recording it is carried by this closure commit. Mirror status remains pending recovery as recorded at L5.
- L24 — Close: the authorized scope is delivered across four work units on `docs/odd/work-unit-commit-policy`, independently accepted at `05688ea7bcb0cfee9a6f00c2dc247a7f3b64f74c`, and this record is closed so that pull-request management may begin. Delivered: the official reviewable work-unit commit policy in its canonical owners; the lifecycle reordered so closure and its commit precede pull-request publication with no post-publication closure stage; independent semantic acceptance defined at a pinned commit; the release-manager closure guard; the reviewer's head-bound record verification; the bounded reopen path; and the register alignment for DEBT-048, DEBT-060 and DEBT-062, all of which remain open. Deferred and disclosed rather than absorbed: the fourteen-path inventory deviation recorded at L8, the agent-enforced rather than mechanical nature of the closure guard, and the documentary nature of acceptance authenticity. Not delivered and not claimed: any `cli/aicore` change, any new script or validator, and any repair of PR #207 or its own record.
