# ODD workflow efficiency

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-27
> **Objective:** Simplify ODD while preserving task and durable feature semantics, safety, verification and retirement.
> **Branch:** `refactor/odd/workflow-efficiency`.
> **Delivery:** One bounded implementation; forecast exceeds 400 lines; strategy is coherent policy and validator units without commits until separately authorized.
> **Runner:** pnpm --dir .agents/skills/odd-workflow exec vitest run

## Specs

- S1 — ODD does not depend on full-record memory mirrors. Exact requirement: "Retirement of mandatory ODD mirror synchronization." Acceptance: inspect workflow and skill; no mandatory mirror remains.
- S2 — Active tasks preserve material authority and support resumption, while durable features describe enduring behavior. Exact requirement: "Feature files must not become" implementation plans or execution history. Acceptance: walk task, feature and retirement scenarios against authoring rules.
- S3 — Reporting and planning are proportionate without removing authorization or risk warnings. Exact requirement: "Retain the obligation to warn before large-scale or costly work." Acceptance: inspect workflow and verify the warning and meaningful progress rules.
- S4 — The validator accepts a structurally valid closed record without a fixed first-failure phrase. Exact requirement: "Removal of the validator's fixed first-failure phrase requirement." Acceptance: run the same valid input before and after; the prior diagnostic disappears.
- S5 — Existing safety, verification, retirement and ownership safeguards remain. Exact requirement: "Preserve existing retirement eligibility, timing, and deletion safeguards." Acceptance: compare the governing policy and focused validator regressions.
- S6 — System One invocation is optional. Exact requirement: "Making System One invocation optional." Acceptance: inspect the runtime contract and verify that availability is not an ODD prerequisite.

## Tasks

- T1 | S1, S2, S3, S5, S6 | inline (bounded policy and existing templates) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T2 | S4, S5 | inline (existing validator and focused regression) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T3 | S1, S2, S3, S4, S5, S6 | inline (verification and source-local alignment) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending

## Log

- L1 — 2026-11-27 — Original request, verbatim:

````
The bounded proposal is approved, with the following additional requirements and clarifications.

Proceed with the proposed implementation within the enumerated scope.

## 1. Explicit policy approvals

I authorize:

- Retirement of mandatory ODD mirror synchronization.
- Selective preservation of material request and correction wording.
- Removal of mandatory routine transition narration.
- Retirement of universal authored-line forecasts and running counts.
- Risk-based rollback planning.
- Removal of the validator's fixed first-failure phrase requirement.
- The narrow feature-reference policy adjustment.
- Making System One invocation optional.
- The documented local departures from upstream ODD behavior.

I accept the loss of a separately verified external recovery copy for uncommitted active task records.

Do not introduce a replacement backup or synchronization mechanism.

## 2. Critical additional requirement: document semantics

A recurring problem in this project is that agents write durable feature files as if they were temporary task records.

Correct this at the governing authoring rules, templates, and applicable existing guidance.

### Temporary task records

Task records describe a specific change and its execution.

They contain the authorized intent, scope, material decisions, acceptance conditions, execution state, verification evidence, blockers, and next action.

They remain temporary and are retired under the existing policy.

### Durable feature files

Feature files describe an enduring capability and its current functional contract.

Their requirements must express meaningful, verifiable properties, behaviors, guarantees, or constraints of the capability.

They must remain useful independently of the task that created or modified them.

Feature files must not become:

- Implementation plans.
- Task execution checklists.
- Lists of files to create or modify.
- Progress reports.
- Historical implementation logs.
- Collections of review findings.
- Transcripts of user conversations.
- Records of temporary execution authorization.
- Lists of tests performed or PR operations.

A feature requirement checkbox represents whether the enduring requirement is satisfied, not whether an implementation activity was completed.

Do not create a new durable requirement for every implementation step, modified file, executed test, or resolved review finding.

When a task changes implementation without changing the enduring contract, evaluate whether any feature content actually requires modification. Do not require meaningless feature mutations.

Preserve the existing feature ownership and applicability rules.

## 3. Durable knowledge and retirement

Preserve the temporary-task and durable-feature lifecycle.

Before retiring a task, ensure that genuinely enduring requirements, decisions, constraints, and required attestations survive in their appropriate durable owners.

Do not indiscriminately transfer task-specific authorizations, logs, implementation history, or execution evidence into feature files.

Distinguish enduring architectural decisions from temporary execution decisions.

Durable references must remain meaningful and accessible after the temporary task is deleted.

References to authoritative documentation may supplement a self-contained functional requirement but must not replace it with an opaque link or duplicate another document's normative content.

Preserve the existing retirement eligibility, timing, and deletion safeguards.

## 4. Authoring guidance

Include concise examples that demonstrate the difference between:

- A temporary task acceptance criterion.
- An incorrectly written durable feature requirement that describes an implementation activity.
- A correctly written durable feature requirement that describes enduring system behavior.

Keep these examples at the appropriate existing rule owner.

Do not duplicate the same examples and normative rules across every template, skill, checklist, and workflow document.

Apply the accepted skill-authoring principles: concise instructions, clear ownership, conditional loading, and minimal cumulative context.

## 5. Validation boundaries

Do not introduce a semantic validator, keyword blacklist, mandatory phrasing convention, or new automated gate to enforce document quality.

Correct semantic document authoring through clear instructions, appropriate templates, and the existing author self-review.

Preserve useful structural validation.

Removing the fixed first-failure phrase must not remove the obligation to provide actual RED/GREEN evidence when applicable.

Do not claim that structural validators establish semantic correctness, truthful evidence, or actual functional achievement.

Keep validation proportionate and reuse existing evidence.

Perform the proposed focused previous/current validator comparison without expanding it into a general validator rewrite.

## 6. Scope restrictions

The enumerated implementation paths and the necessary governing ODD task record are authorized.

Do not:

- Rewrite or migrate the existing feature catalog.
- Perform historical task cleanup.
- Modify the accepted op-skill-creator implementation or its open task.
- Change harness configuration in this phase.
- Modify destination repositories.
- Change synchronization behavior.
- Introduce scripts, validators, plugins, MCP servers, agents, or new infrastructure.
- Call or troubleshoot System One.

Preserve existing local changes.

If additional live consumers require modifications outside the approved scope, explain the concrete dependency and request authorization.

## 7. Safety and workflow guarantees

Preserve user authorization, scope boundaries, risk warnings, protection of unrelated work, applicable testing, honest evidence reporting, author self-review, optional independent review, and Herald's exclusive Git and GitHub authority.

Retain the obligation to warn before large-scale or costly work.

Do not remove legitimate safeguards merely to reduce document size or token consumption.

## 8. Completion and reporting

Proceed with the approved implementation units.

Avoid repeating the completed audit or introducing unnecessary intermediate reports.

Report material blockers, unexpected contract changes, and decisions requiring approval.

The final report must include:

- Changed paths.
- Implemented policy changes.
- Preserved and retired obligations.
- Temporary-task and durable-feature semantic guarantees.
- Validator and scenario verification results.
- Before-and-after instruction-loading estimates.
- Remaining limitations and explicit completion status.

Distinguish static estimates from measured runtime savings.

No Git operations, commits, pushes, PRs, or independent reviews are authorized at this stage.

Do not automatically resume or close the previous mirror-blocked task.
````
- L2 — Bootstrap: mirror pending under the pre-change contract; no replacement synchronization or recovery operation is authorized. Existing feature owners are `odd/features/organic-driven-development.md` and `odd/features/durable-feature-file.md`. Next: focused RED, then the authorized policy and validator units.
- L3 — The focused `pnpm --dir .agents/skills/odd-workflow exec vitest run tests/unit/feature-closure.test.ts` failed with the expected first-failure diagnostic before the validator edit (one failing test), then passed 18 tests after it. The rule removal and selected runtime guidance are partial only: the skill, checklist, templates, durable features, reporting contract, adoption summary, command comparison, full checks and obligation accounting remain pending. The task stays active; no Git operation or System One call was made. Next: finish those authorized paths and verify consistency before claiming completion.
- L4 — Policy implementation and author self-review: original inputs were the pre-change `AGENTS.md`, `.aicore/core/knowledge/{agent-workflow,agents}.md`, the ODD skill and checklist, both templates, `odd/features/{organic-driven-development,durable-feature-file}.md` and `docs/architecture/odd-adoption-status.md`; candidate inputs are those same paths plus this record. Retained: the seven-step authority and scope route, small-work classification, pre-write tracking, enduring-feature ownership and tick rules, material user authority and risk decisions, risk warning, reviewable/high-risk commits, relevant RED/GREEN and regression evidence, truthful check status, author self-review, opt-in independent review, conditional verification alternatives, Herald's Git exclusivity, user-only merge, retention eligibility/timing/deletion safeguards and durable-evidence preservation. Translated: full messages to selective material exact wording and resumable state; step-by-step narration to meaningful progress; line forecasts and universal rollback boundaries to coherent units and risk-based rollback; absolute no-reference feature rule to accessible supplementary authoritative references; first-failure keyword gate to actual applicable RED/GREEN evidence; mandatory System One invocation to optional invocation with unchanged directive handling when used. Retired by the explicit L1 authorization: mandatory mirror creation/readback and its recovery-copy guarantee, full-message duplication, routine transition reports, authored-line forecast/count threshold and fixed first-failure phrases. No server, configuration, destination, synchronization behavior, retention period, previous skill-authoring task or independent-review gate was changed. The existing feature owners were updated: ODD R3/R8/R25/R26/R28 reworded and verified as source-policy statements; durable-feature R6 reworded and verified; unaffected requirements were not reverified. Source-policy alignment is not runtime adoption.
- L5 — Observable scenario walkthrough by Cipher: (1) a read-only request creates no task; (2) an interrupted active change resumes from its task and relevant files without memory and retains exact material scope/approvals; (3) a feature requirement expresses durable behavior, not the task's activity; an accessible authoritative reference supplements but does not replace it; (4) before retirement, enduring requirements and required attestations survive at appropriate durable owners while temporary history is not copied indiscriminately; eligibility and seven-day policy remain unchanged; (5) costly work triggers warning, alternatives and required approval; (6) a changed deterministic rule retains actual RED/GREEN evidence, while a missing check is not passed; (7) System One is optional and independent review needs explicit user authorization. These are static readings of the candidate, not observed runtime agent executions.
- L6 — Focused previous/current CLI comparison by Cipher on the same isolated fixture and commands, using the pre-change rule reconstructed from the earlier inspected source: without the first-failure phrase, prior status 1 and stdout `FAIL` with the first-failure diagnostic changed to status 0 and stdout `ok`; stderr was empty both times. An existing valid closed record stayed status 0 with identical stdout and empty stderr; a nonexistent file stayed status 1 with the same ENOENT stderr and empty stdout; missing arguments stayed status 2 with identical usage stdout and empty stderr. Node v24.22.1. The restored prior implementation was behaviorally reconstructed from the inspected source, not obtained from Git; no Git operation occurred. The test RED/GREEN at L3 remains valid. Verification and delivery state are recorded below when completed; no independent review was authorized.
- L7 — Author verification by Cipher: `pnpm --dir .agents/skills/odd-workflow exec vitest run` reported 18 files and 177 tests passed; the skill `typecheck`, `pnpm lint`, `pnpm format:check` and `pnpm typecheck` completed without failure, and both ODD validators reported all task and feature files ok. The first format check identified one missing blank line in the edited skill; it was corrected and the check rerun successfully. The validators establish structure, not semantic correctness or runtime adoption. Author self-review used the code-review rubric; no independent review ran. S1–S6 are supported at the uncommitted candidate by L3–L6 and these checks; task rows remain unfinished because Git and commits are unauthorized. The record is active, not closed or delivered; next action after separate Git authorization is commit-bound verification and ordinary closure under the applicable policy. The previous mirror-blocked task was not resumed or modified.
- L8 — 2026-11-27 — User authorized combined delivery, applying the revised ODD policy to both records, commit-bound closure, one PR and focused independent review; no merge, tagging, branch deletion, System One, destination synchronization or unrelated work. Herald verified fetched `origin/main` and created `refactor/odd/workflow-efficiency` from `5bf17d081b07f2a95f6510929c08efa5b256e6f4` without changing the worktree inventory. Authentic validator comparison supersedes L6's baseline limitation: Herald verified the restored original file and HEAD blob both hash to `1e6e0def45f461ab4cfbc3791d5f57b3ab7e10f3`. Cipher ran both versions under Node v24.22.1 against the same four inputs: no-phrase closed fixture changed from exit 1 diagnostic on stdout to exit 0 `ok`, both with empty stderr; an existing valid record stayed exit 0 with identical stdout/stderr; a missing file stayed exit 1 with identical empty stdout and ENOENT stderr; no arguments stayed exit 2 with identical usage stdout and empty stderr. The prior implementation was restored only for comparison and the candidate was restored afterward. The candidate policy removes the mirror prerequisite; no synchronization is claimed, and adoption on main is not claimed.
