# Verification contingency for distributed tooling failure

> **Status:** closed
> **Disposition:** completed
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-26
> **Closed:** 2026-11-26
> **Objective:** Govern what an agent may do when a required verification instrument cannot execute, so that a failure of distributed tooling establishes neither compliance nor breach, an equivalent procedure lets authorized work proceed without waiting for an upstream correction, and delivery readiness follows the guarantees rather than the instruments.
> **Branch:** governance/verification-contingency
> **Delivery:** single inline unit; forecast ~180 authored additions + deletions (generated files excluded); slice boundaries: (1) the authoritative contingency policy, (2) readiness, ownership, release-packet and ODD-stage alignment, (3) consistency and scenario validation evidence.
> **Runner:** node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks

## Specs

- S1 — Verification outcomes are distinguished as satisfied, violated and unavailable, and an unavailable result establishes neither compliance nor breach. Exact requirement: `The governance must distinguish between three fundamentally different outcomes:` verification passed, verification failed, verification unavailable. Acceptance: read the contingency policy; all three outcomes are named, and the unavailable outcome states that it establishes neither compliance nor breach.
- S2 — A check that cannot execute is resolved by naming the cause, separating a tooling failure from a detected violation, naming the guarantee the check exists to establish, evaluating permitted alternatives, using the simplest one that establishes it, and documenting the evidence, limitation and resulting status. Exact requirement: `When a verification tool cannot execute, the agent must:` identify the actual cause, distinguish a tooling failure from a detected implementation violation, identify the underlying verification objectives, evaluate whether existing alternative procedures can establish those objectives, use the simplest reliable alternative permitted by the governance, and document the evidence, limitations and resulting verification status. Acceptance: read the policy and confirm the six ordered obligations are stated with their observable effect.
- S3 — A prescribed instrument is substitutable by default, and only an explicit non-substitutability or an essential security or contractual requirement removes the contingency route. Exact requirement: `The fact that a workflow names a particular command or tool must not, by itself, eliminate the contingency route.` and `Do not assume that every prescribed instrument is inherently non-substitutable.` Acceptance: read the policy; it states that a named command, script or tool prescribes the instrument without making it non-substitutable, and names the two exceptions.
- S4 — An alternative that establishes the same guarantees to at least the same standard proceeds without additional user consultation, while a material deviation uses the existing user-owned decision or authorized-exception mechanism and no new approval system. Exact requirement: `When an alternative procedure establishes the same mandatory guarantees to at least the same standard, the agent should be authorized to proceed without additional user consultation` and `Do not introduce a new approval system.` Acceptance: read the policy; equivalent verification is authorized without consultation, and the four material-deviation conditions route to an already-existing mechanism only.
- S5 — An essential non-waivable guarantee that cannot be established leaves the affected operation blocked, and the report names the missing guarantee rather than the failed tool. Exact requirement: `If an essential guarantee cannot be established through any reliable alternative, the affected operation must remain blocked. The reason for blocking must be the missing guarantee, not simply the unavailability of a particular tool.` Acceptance: read the policy; blocking names the missing guarantee and never only the instrument.
- S6 — An unavailable check is never reported as passed, the instrument's execution status stays separate from the guarantee's verification status, and unavailability stays distinct from a check not yet executed. Exact requirement: `The original instrument must never be reported as passed merely because the alternative succeeded.` and `Also preserve the distinction between an unavailable check and a check that is genuinely pending execution.` Acceptance: read the policy and the readiness definition; both state the separation and the pending-versus-unavailable distinction.
- S7 — Delivery readiness follows the established guarantees rather than the executed instruments, and every delivery retains its own verification evidence. Exact requirement: `make delivery readiness guarantee-based rather than instrument-based.` Acceptance: read the readiness definition and the release-packet clause; readiness is conditioned on established guarantees and both name the alternative procedure and its evidence.
- S8 — A confirmed defect in a distributed file is disclosed with sufficient evidence to its owner, and no destination waits for acknowledgment, issue creation, correction, review, merge, release or synchronization before completing otherwise-verifiable authorized work. Exact requirement: `The obligation is to disclose and report the confirmed defect appropriately, not to make upstream resolution a prerequisite for delivery.` Acceptance: read the policy; the disclosure obligation is stated and the seven waiting conditions are excluded as prerequisites.
- S9 — A documented defect whose circumstances are materially unchanged reuses its existing reference and the still-authorized alternative without a duplicate report or repeated authorization, and a contingency never becomes a permanent substitute for correction. Exact requirement: `Reuse the existing defect reference rather than creating duplicate reports or technical debt entries.` Acceptance: read the policy; reuse of the existing reference is stated together with the no-timer, no-counter and no-deadline constraint.
- S10 — Contingency reporting uses the existing change record, verification evidence and release structures, states the seven named facts, and adds no form, artifact or verbose guarantee-by-guarantee reporting for ordinary passing checks. Exact requirement: `Do not introduce a new mandatory form, separate artifact, or large reporting template.` Acceptance: read the policy; the reporting duty names only existing structures and the seven facts.
- S11 — Policy precedence is explicit: equivalent substitution is permitted, a workflow restriction declaring non-substitutability or a fixed deviation remains binding, existing user-authorized exception mechanisms apply, and the operation stays blocked when the guarantee is missing. Exact requirement: `The general policy must clarify:` when equivalent substitution is permitted, when a workflow-specific restriction remains binding, when existing user-authorized exception mechanisms apply, and when an operation must genuinely remain blocked. Acceptance: read the policy; all four precedence cases are stated and no intentional security restriction is overridden.
- S12 — The correction is documentation-only and introduces no code, validator, schema, configuration, infrastructure, agent or workflow stage. Exact requirement: `Do not introduce new code, validators, schemas, configuration, infrastructure, agents, or workflow stages.` Acceptance: read the delivered file set; no path outside the authorized documentation surface and the governing records is changed.

## Tasks

- T1 | S1, S2, S3, S5, S6, S8, S9, S10, S11 | inline (single authoritative policy, one owner file) — Cipher 🔓 (Lead Orchestrator) | done | commit: 0d72421d5dc9ecbb194e9e41b296836afe261de8
- T2 | S4, S6, S7 | inline (readiness alignment in the shared-rules owner) — Cipher 🔓 (Lead Orchestrator) | done | commit: 04834d951626b992d46a10f2fa338211dfeefb6e
- T3 | S7, S10, S11 | inline (concise references where an existing workflow restates check completion) — Cipher 🔓 (Lead Orchestrator) | done | commit: 04834d951626b992d46a10f2fa338211dfeefb6e
- T4 | S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12 | inline (consistency, precedence and scenario validation of the delivered text) — Cipher 🔓 (Lead Orchestrator) | done | commit: 0d72421d5dc9ecbb194e9e41b296836afe261de8

## Log

- L1 — original request, verbatim:

````
# AICore — Operational autonomy and tooling failure contingencies

I need you to evaluate and improve AICore's governance regarding failures of its distributed tools and verification workflows.

## 1. Problem statement

AICore distributes instructions, standards, skills, tools, and workflows to independent destination projects.

Currently, a defect in an AICore-distributed tool could prevent a destination project from completing its work, even when the project's implementation is correct.

If multiple projects encounter the same tooling defect, they could all become blocked until:

- The defect is corrected in AICore.
- The upstream correction is reviewed and merged.
- The corrected tooling is synchronized into each destination project.

This creates unacceptable operational coupling.

AICore must facilitate development, not become a centralized bottleneck.

## 2. Objective

Establish a governance policy that allows destination projects to continue operating when an AICore-distributed tool fails, provided the underlying verification objectives can still be satisfied through a reliable alternative procedure.

Correcting AICore and completing destination project work must be independent activities whenever technically and safely possible.

This must not become a general permission to bypass mandatory requirements.

## 3. Investigate the current governance

Before proposing changes, inspect the authoritative project instructions, governance contracts, and relevant skills.

Determine:

- Whether an existing contingency or exception mechanism already exists.
- Whether the current contracts distinguish verification failures from tool execution failures.
- Whether existing instructions could unnecessarily block destination projects.
- Which authoritative document should own this policy.
- Which existing workflows require alignment.
- Whether overlapping or contradictory rules exist.

Do not assume that the entire governance system requires modification.

If an adequate mechanism already exists, determine whether the problem is its wording, discoverability, application, or precedence.

## 4. Required distinction

The governance must distinguish between three fundamentally different outcomes:

| Outcome | Meaning |
|---|---|
| Verification passed | The verification executed and its requirements were satisfied. |
| Verification failed | The verification executed and detected a violation. |
| Verification unavailable | The verification could not complete because of a tool defect, infrastructure failure, or unavailable dependency. |

A tool execution failure is not proof that the verified implementation is defective.

Equally, it is not proof that the implementation satisfies the verification requirements.

These distinctions must be reflected in agent behavior and reporting.

Do not introduce new programmatic statuses, enums, schemas, or validators merely to express this conceptual distinction.

## 5. Contingency principles

When a verification tool cannot execute, the agent must:

1. Identify the actual cause of the execution failure.
2. Distinguish a tooling failure from a detected implementation violation.
3. Identify the underlying verification objectives.
4. Evaluate whether existing alternative procedures can establish those objectives.
5. Use the simplest reliable alternative permitted by the governance.
6. Document the evidence, limitations, and resulting verification status.

A destination project must not be required to wait for an AICore correction when a reliable and permitted alternative exists.

The upstream defect can be reported, registered, and corrected independently.

## 6. Safety and non-negotiable requirements

Operational autonomy does not mean unrestricted exceptions.

The policy must preserve:

- Security requirements.
- Data integrity.
- User authorization boundaries.
- Git and GitHub governance.
- Required independent review.
- Accurate evidence and reporting.
- Existing architectural and functional contracts.

An alternative procedure must not:

- Conceal an actual verification failure.
- Ignore a confirmed security violation.
- Fabricate evidence.
- Claim that an automated check passed when it did not execute.
- Silently weaken mandatory guarantees.
- Convert a genuine implementation defect into a tooling exception.

If an essential guarantee cannot be established through any reliable alternative, the affected operation must remain blocked.

The reason for blocking must be the missing guarantee, not simply the unavailability of a particular tool.

## 7. Authorization and agent autonomy

Evaluate how contingency authorization should work under the existing decision and governance contracts.

My preference is to avoid unnecessary user intervention.

If an alternative procedure is already authorized by the governance and preserves the required guarantees, the agent should be able to proceed without requesting additional approval.

User consultation should be necessary only when:

- An essential guarantee cannot be fully established.
- The proposed contingency changes an existing contract.
- A material residual risk requires acceptance.
- A security or authorization boundary is affected.
- The decision exceeds the agent's delegated authority.

Do not establish a new mandatory approval ceremony for every tool execution failure.

Challenge this preference if the current security or governance model requires a different boundary, and explain the practical consequences.

## 8. Destination project autonomy

The resulting policy must make clear that:

- Destination projects are not operationally subordinate to AICore's release cycle.
- An upstream defect does not automatically block all destination work.
- Destination agents should not independently modify AICore-distributed files merely to bypass a tooling failure.
- Upstream remediation and destination delivery can proceed independently.
- Synchronization is not automatically a prerequisite for completing an otherwise verifiable operation.
- Contingencies must not become permanent substitutes for correcting confirmed tooling defects.

Do not introduce a centralized exception service, shared runtime dependency, or additional coordination infrastructure.

## 9. Scope and simplicity

This is primarily a governance and documentation improvement.

Do not automatically introduce:

- New scripts.
- New validators.
- New skills.
- New agents or subagents.
- New workflow engines.
- New configuration files.
- New schemas.
- New infrastructure.
- Additional mandatory workflow stages.

Prefer correcting the existing authoritative contract and adding concise references where necessary.

Avoid duplicating the same policy across multiple documents.

Do not redesign the Git workflow or any other workflow simply because it is affected by this principle.

If implementation changes are genuinely necessary, demonstrate why documentation alone is insufficient before proposing them.

## 10. Preserve existing functionality

Preserve existing functionality, architecture, security boundaries, and observable contracts except for the explicitly approved governance correction.

Do not remediate unrelated technical debt.

Do not modify destination repositories or synchronize changes into them.

Follow the current AICore architecture, skills-first workflow, ODD workflow, and Git governance.

Herald remains the exclusive authority for Git and GitHub operations.

## 11. Required initial deliverable

Perform a read-only investigation and present a concise proposal containing:

1. Confirmed weaknesses in the current governance.
2. Exact authoritative files and sections involved.
3. Existing contingency mechanisms, if any.
4. Contradictions or duplicated responsibilities.
5. Recommended contingency policy.
6. Proposed authorization boundaries.
7. Exact files requiring modification.
8. Expected effects on existing workflows.
9. Risks and trade-offs.
10. Decisions genuinely requiring my approval.

Include examples demonstrating how the proposed policy handles:

- A verification tool crashing.
- An automated check detecting an actual violation.
- A tooling defect with an equivalent alternative procedure.
- A tooling defect without a reliable alternative.
- An upstream AICore defect affecting multiple destination projects.

Be critical of your own proposal.

Do not manufacture complexity, introduce unnecessary approval gates, or propose new automation without a demonstrated need.

Do not begin implementation until I review the proposal.

The 
````

- L2 — user review of the proposal, verbatim (dated 2026-11-26):

````
I have reviewed your proposal. The direction is approved, subject to the following clarifications.

## 1. Decisions A, B and C

- A — Approved: adopt the guarantee/instrument distinction and the proposed authoritative contingency policy.
- B — Approved: make delivery readiness guarantee-based rather than instrument-based.
- C — No ADR. Use the authoritative documentation and existing ODD records. Do not introduce an ADR solely for this clarification.

The proposed documentation-only approach is appropriate.

Do not introduce new code, validators, schemas, configuration, infrastructure, agents, or workflow stages.

## 2. Correct an important limitation in the proposed policy

Your draft states:

"A substitution is permitted only where the governance fixes the guarantee rather than the instrument."

This could reproduce the operational coupling that this correction is intended to eliminate.

A workflow may explicitly prescribe a particular instrument, command, script, or verification procedure. If that instrument contains a defect, the destination project must have a legitimate contingency route.

Distinguish between:

- A mandatory verification objective.
- A prescribed instrument used to establish that objective.
- An explicitly non-substitutable instrument whose use is itself an essential security or contractual requirement.

Do not assume that every prescribed instrument is inherently non-substitutable.

The new policy must define how an instrument-specific requirement can be handled when that instrument cannot execute.

### Equivalent verification

When an alternative procedure establishes the same mandatory guarantees to at least the same standard, the agent should be authorized to proceed without additional user consultation, provided no explicitly non-substitutable requirement is violated.

The fact that a workflow names a particular command or tool must not, by itself, eliminate the contingency route.

### Material deviations

When the alternative:

- Provides weaker verification guarantees.
- Cannot establish part of the original requirement.
- Changes an essential contractual or security boundary.
- Requires acceptance of material residual risk.

The agent must use the existing user-owned decision or authorized-exception mechanism.

Do not introduce a new approval system.

### Non-waivable guarantees

If an essential, non-waivable guarantee cannot be established, the affected operation remains blocked.

The report must identify the missing guarantee, not merely state that a particular tool failed.

## 3. Establish policy precedence

The contingency policy must be operationally effective, not merely descriptive.

Verify that existing workflow-specific instructions do not contradict or silently override the new policy.

In particular, evaluate workflows that explicitly prescribe mandatory verification instruments or state that alternative procedures cannot replace them.

The general policy must clarify:

- When equivalent substitution is permitted.
- When a workflow-specific restriction remains binding.
- When existing user-authorized exception mechanisms apply.
- When an operation must genuinely remain blocked.

Do not silently override intentional security restrictions.

If a specific workflow needs a concise reference to the authoritative contingency policy to eliminate a contradiction, propose or implement the minimum necessary alignment within this task.

Do not rewrite affected workflows wholesale.

## 4. Separate execution status from verification status

Your proposed distinction is correct, but ensure that the original check's execution status and the underlying guarantee's verification status are not confused.

For example:

- Original instrument: unavailable.
- Alternative procedure: executed successfully.
- Underlying guarantee: established.
- Delivery readiness: determined from the established guarantee and remaining requirements.

The original instrument must never be reported as passed merely because the alternative succeeded.

Reuse existing terminology and reporting structures.

Do not introduce programmatic statuses, new enums, or additional tracking systems.

Also preserve the distinction between an unavailable check and a check that is genuinely pending execution.

## 5. Operational independence and upstream reporting

I approve the proposed destination autonomy principle.

However, upstream reporting must not become another operational gate.

A destination agent should record a confirmed distributed-tool defect and provide sufficient evidence for its authoritative owner to investigate.

The destination project must not be required to wait for:

- Acknowledgment of the defect.
- Creation of an upstream issue.
- Upstream implementation.
- Upstream review.
- Upstream merge.
- A new AICore release.
- Synchronization.

Do not require unauthorized external operations merely to report the defect.

Use existing reporting and ownership mechanisms.

The obligation is to disclose and report the confirmed defect appropriately, not to make upstream resolution a prerequisite for delivery.

## 6. Repeated contingencies

I agree that contingencies must not become an excuse to ignore confirmed tooling defects permanently.

However, a destination project may legitimately encounter the same unresolved defect again before the corrected implementation becomes available.

Do not require repeated user authorization or duplicate defect reports when:

- The defect is already documented.
- The circumstances remain materially unchanged.
- The alternative procedure remains authorized.
- The required guarantees can still be established.

Each delivery must retain its own verification evidence.

Reuse the existing defect reference rather than creating duplicate reports or technical debt entries.

Do not introduce expiration timers, mandatory synchronization deadlines, usage counters, or additional approval stages.

A previously authorized equivalent alternative remains usable while its conditions continue to hold.

## 7. Reporting proportionality

Keep contingency reporting concise.

Use the existing change record, verification evidence, and release reporting structures.

Record the information necessary to establish:

- The unavailable instrument and its failure.
- The underlying verification objective.
- The alternative procedure.
- The observed result.
- Any remaining limitation.
- Applicable authorization, where required.
- The existing upstream defect reference, where applicable.

Do not introduce a new mandatory form, separate artifact, or large reporting template.

Do not require verbose guarantee-by-guarantee reporting for ordinary successful checks when the existing evidence is sufficient.

## 8. Approved implementation scope

The proposed files are approved:

- `.aicore/core/knowledge/agent-workflow.md`
- `.aicore/core/knowledge/agents.md`
- `.aicore/core/knowledge/release.md`
- `.agents/skills/odd-workflow/SKILL.md`

Use one authoritative policy and concise references.

A minimal additional workflow alignment is authorized only where you establish a direct contradiction with the new policy.

Report any such additional file and the reason it is necessary.

Do not modify unrelated documentation or implementation code.

Preserve the existing tooling exception mechanism, technical debt rules, ownership boundaries, security requirements, architecture standards, and independent review requirements.

Do not modify destination repositories or trigger synchronization.

## 9. Validate the governance through representative scenarios

Validate the resulting instructions against these cases:

1. A test wrapper fails, but the underlying test runner executes successfully.
2. A mandatory evidence preparation script crashes, but an equivalent verification procedure exists.
3. A prescribed instrument is unavailable and the alternative provides weaker guarantees.
4. An essential security guarantee cannot be established.
5. A verification executes successfully and detects an actual violation.
6. Multiple destination projects encounter the same distributed tooling defect.
7. A destination encounters an already-reported defect again before upstream correction or synchronization.
8. One operation is genuinely blocked, but other authorized work can continue independently.

For each scenario, establish whether the agent proceeds, consults the user, or blocks the affected operation.

Use documentation consistency checks and scenario-based evaluation.

Do not build automated policy-testing infrastructure.

## 10. Execution and delivery

You are authorized to implement the governance correction under these conditions.

Follow the current skills-first ODD workflow and existing project standards.

Do not request additional confirmation for decisions already resolved in this message.

Be proportionate when establishing the governing records, validation evidence, and independent review.

Herald remains the exclusive authority for Git and GitHub operations.

Create one dedicated branch and one PR for this correction.

Preserve unrelated existing local changes. Do not include them in this PR without authorization.

Do not merge the PR.

## 11. Final report

Provide:

1. Exact governance changes.
2. Authoritative policy location.
3. Resolution of the identified readiness contradiction.
4. Policy precedence and authorization boundaries.
5. Exact changed files and justification.
6. Representative scenario validation results.
7. Confirmation that essential guarantees remain protected.
8. Confirmation that no new tooling or workflow stages were introduced.
9. Independent review findings and dispositions.
10. Final branch, PR URL, and head SHA.
11. Remaining limitations or blockers.
12. Explicit final completion status.

The governing principle is:

Destination projects must remain operationally autonomous. AICore must enforce mandatory guarantees, not unnecessary dependence on particular verification instruments or its upstream release cycle.

Proceed with the authorized implementation.
````

- L3 — Bootstrap: governing record `odd/tasks/2026-11-26-verification-contingency.md` and durable feature file `odd/features/verification-contingency.md` created as the sole bootstrap write; both ODD validators exit 0.
- L4 — T1–T3 delivered, T4 validated. Authoritative policy: `agent-workflow.md` → new `### Verification contingency` (instrument vs guarantee, three outcomes, five-step procedure, prescribed-instrument default, authorization boundary, non-waivable block, execution/verification separation, precedence, distribution independence, repetition, proportionate reporting). Alignment: `agents.md` readiness, `### Finding disposition` blocker line, check definition, round-summary line and ready message; `release.md` packet and verdict-line rule; `odd-workflow` stage 3. Consistency check found six readiness statements that equated an unavailable instrument with an unresolved guarantee (`agent-workflow.md` diagram node W and its W/X legend, `agents.md` readiness and Finding-disposition blocker, `release.md` verdict-line rule, `agents.md` ready-message precondition); each was translated to guarantee-based wording and re-read, and no site now blocks on availability alone. Precedence check: `AGENTS.md` "`core-sync check` exit 0 is that proof" prescribes an instrument for a byte-equality guarantee that any equivalent comparison establishes, so the prescribed-instrument default covers it with the guarantee intact and the root rule is unmodified; `architecture/testing/stacks/typescript.md` "the only execution path" fixes which reviewed configuration is authoritative, so changing it is a material deviation routed to the existing authorized-exception mechanism — also unmodified; permission denies, the tooling authorized-exception route and the debt-deferral authority are preserved verbatim. Scenario evaluation (documentation consistency, no harness): (1) wrapper fails / runner succeeds → proceeds, both facts recorded, ready message names the alternative; (2) evidence script crashes with an equivalent procedure → proceeds, or user when the alternative weakens the guarantee; (3) weaker alternative → user via the existing mechanism; (4) essential security guarantee unestablished → blocked, guarantee named; (5) executed check detects a violation → failed, contingency does not apply, never reclassified; (6) several destinations, one defect → independent local contingencies plus disclosure, no waiting; (7) documented defect re-encountered → same reference and alternative reused, own evidence per delivery; (8) one operation blocked → other authorized work continues. Checks: `pnpm format:check` 457 files, no fixes; `pnpm lint` clean; `pnpm typecheck` all projects plus `mcp-servers/system-one` clean; both ODD validators exit 0. Obligation accounting (retained / translated / retired): translated — "unavailable ⇒ pending or justified N/A" → unavailable leaves the guarantee unestablished and the policy owns permission; the three readiness statements → guarantee-based; "check is passed, failed or pending" → passed, failed or unavailable, with pending retained for not-yet-attempted; packet and stage-3 "checks have run and are recorded" → plus the guarantee and alternative for a check that could not execute; ready message → guarantee-based precondition naming an alternative. Retained verbatim — permission-denial prohibition, independent review optionality, tooling authorized-exception authority, debt deferral authority, ownership boundary, no-new-stage rule. Retired — "justified N/A" as an unavailable-check route, because it read as a waiver and no rule defined its effect on readiness. One additional file was aligned under the authorized minimal-contradiction route: `.agents/skills/git-pr/references/_pr-evidence-format.md` used instrument-level "unresolved required verification" as a `[BLOCK]` trigger, which would block a guarantee a permitted alternative had established; its PASS, ADVISORY and BLOCK conditions now state the guarantee that must be established, with no other change to that file and no change to its generator or tests, which key on finding status rather than on this prose.
- L6 — 2026-11-26 — Requested independent review (Mode B, fresh context) judged candidate `bf3b7ac` and returned `[BLOCK]` with one finding. F1: the new policy's ownership-boundary sentence was scoped to "a `core` region", narrower than the distributed surface both the approved requirement and durable R7 claim — `README.md` records that `.aicore/core/knowledge/agent-workflow.md` and `release.md` ship whole-file in raw mode without regions, as do the architecture, tooling and skill roots, so those distributed files fell outside the sentence while the prescribed-instrument default left a locally patched copy of a defective distributed script within reach. The premise was verified against `distribution-clearance.json` and the README distribution description before the finding was accepted. Status: FIXED (round 1). The record reopens for this finding's bounded remediation only. The reviewer also reported one pre-existing wording weakness outside this PR's changed lines — `_pr-evidence-format.md:107` says "failed or unresolved check" while the new vocabulary distinguishes unavailable from unestablished — routed to its owner, not corrected here. Counts: fixed 1 · open 0 · deferred 0 · rejected 0 (of 1).
- L7 — 2026-11-26 — F1 remediation and targeted verification. The sentence now names the whole distributed surface — a `core` region, a raw distributed file, a distributed skill or script, a merge-managed configuration and a managed instance — and forbids editing, patching, shadowing or replacing any of it with a locally maintained copy to route around a defect, while leaving `project`-region and destination-owned content to the destination and placing correction with the upstream owner. Targeted re-read against the review's seven prohibited actions: modifying distributed core files, modifying core-managed regions, patching distributed scripts locally, overriding distributed governance rules, introducing local shadow implementations, disabling mandatory safeguards, and bypassing Core Sync ownership are each refused by the clause itself or by the unchanged precedence paragraph, which holds that a permission denial, authorization boundary, security control or governance gate is not a tool defect and is never substituted. Durability is unchanged: R7 is untouched in wording and now matches the operative text. Re-run checks after the correction are recorded in the delivery evidence.
- L8 — Close: the finding's remediation is delivered at `0d72421` and every `S#` remains verified — S1–S11 by the re-read of the delivered statements, with the ownership sentence now covering the whole distributed surface, and S12 by the change set, which is documentation and records only. The first failure this change produced remains the readiness contradiction recorded at L4; no applicable executable failure exists because a prose governance change has no runnable test, and the post-correction evidence is the re-run of `pnpm format:check` (457 files, no fixes), `pnpm lint` and `pnpm typecheck` (every project clean) together with both ODD validators. Independent review: one requested review ran on candidate `bf3b7ac` and returned F1, now `FIXED`; no further review was authorized, so no new verdict is invented and none is claimed for the corrected candidate. Durable feature `odd/features/verification-contingency.md` R1–R9 remain ticked, and R7 now matches the operative text. Full feature mirror: pending recovery, not synchronized — a record line exceeds the 2,000-character readable limit, so a byte-exact readback cannot be established and no unverifiable mirror write was made; the repository file remains authoritative and complete.
