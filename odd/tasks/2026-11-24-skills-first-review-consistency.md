# Skills-first review consistency

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-24
> **Objective:** Make the approved skills-first architecture unambiguous in every active instruction: self-review is the normal route performed directly, an independent review runs only on explicit user authorization, and no retired autonomous-review or parent-acceptance gate survives in active text.
> **Branch:** `fix/skills-first/review-consistency`, to be created by Herald 📯 (Release Manager) from verified `main`.
> **Delivery:** Strategy `single-pr` with separately revertible work units, so no chained slices are needed either way the forecast lands. WU1 — root and shared workflow rules. WU2 — the two rewired skills. WU3 — the adoption-status correction. Forecast: roughly 130 authored additions and 40 deletions across the eight authorized files, plus roughly 200–260 lines for this record dominated by the verbatim authorization block; that total is at or above the ~400-line strategy trigger, which the declared strategy already satisfies.
> **Runner:** `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks`; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts odd/features`; `pnpm format:check`; `pnpm lint`.

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — No active instruction authorizes an independent review without explicit user authorization covering that review, and a declared high-risk item yields only a recommendation. Exact requirement: "No active instruction requires autonomous independent code-review dispatch." / "No high-risk recommendation is expressed as implicit delegation authorization." Acceptance: read every active instruction that names independent review and observe that the only dispatch condition is explicit user authorization, with the prohibition stated rather than inferred.
- S2 — The implementation step hands closure to outcome verification rather than to a separate context's verification. Exact requirement: "Step 7 requires verification of the observable outcome, not verification by a separate agent." Acceptance: read the implementation step and observe that it advances to outcome verification, while the separate-from-tests requirement remains in the closure step.
- S3 — Reporting rules name real pauses only, and no retired independent acceptance gate survives under generic terminology. Exact requirement: "Do not retain obsolete independent acceptance gates under generic terminology." Acceptance: read the shared reporting rules and the step-reporting rules and observe that a combined report is withheld only by an authorization pause, an unresolved prerequisite, a pending check or a blocker.
- S4 — The code-review skill is discoverable for an ordinary request to review, verify, check or confirm correctness, and states its normal self-review use. Exact requirement: "The code-review skill is discoverable for normal self-review." / "The description must make it clear that: Cipher uses the skill directly for applicable self-review." Acceptance: read the skill's frontmatter description and observe that an ordinary review request selects it, without any independent-review or high-risk condition being required.
- S5 — The code-review skill documents two explicit execution modes over one shared rubric, and the self-review mode preserves the author's correction authority. Exact requirement: "Refactor the instructional structure of the existing skill to make the following two execution modes explicit." / "The act of reviewing may be observational, but loading the skill must not revoke the primary agent's existing authority to correct findings afterward." Acceptance: read the skill and observe one rubric, a self-review mode that keeps direct correction, rerun and continuation, and no reviewer packet, verdict artifact or handoff in that mode.
- S6 — The independent-review mode stays read-only, non-authoritative and explicitly authorized, and reviewer-specific input, output and restriction requirements are scoped to it. Exact requirement: "The separate reviewer: Remains read-only. Does not become an approval authority or universal delivery prerequisite." Acceptance: read the skill and observe the read-only input, output and limit rules attached to the independent mode only, with no Git grant and no authority change.
- S7 — The canonical diagram and its interpretation contain no unrequested reviewer dispatch and no recursive review cycle, and a correction does not renew a review authorization. Exact requirement: "Ensure this does not automatically reuse the original review request as authorization for repeated independent reviews." / "Correct the Mermaid diagram and its interpretation so that the optional review branch cannot create an unrequested recursive review cycle." Acceptance: read the diagram and its interpretation and observe that the review branch is entered only on authorization of the named candidate, and that a corrected candidate is reviewed again only under covered authorization.
- S8 — The incident workflow's default route is direct execution, with no imaginary parent acceptance, no self-redispatch and no acceptance-only dispatch. Exact requirement: "Ensure the default route is direct execution by Cipher." / "Cipher does not return AWAITING_REVIEW to an imaginary parent." Acceptance: read the incident skill and its affected references and observe that direct execution owns and advances every incident step, while handoff mechanics are scoped to work actually authorized for delegation.
- S9 — The incident workflow's existing safeguards, schema, allowances and functional behavior are unchanged. Exact requirement: "Do not change the incident schema, templates' data fields, validator implementation, query limits, or functional incident behavior." Acceptance: read the affected incident files and observe that identification order, allowances, rerun limits, SLA warning, single budget, one-writer rule, destination separation and close-out verification are unchanged, with no schema or validator edit.
- S10 — Retained correctness and safety obligations survive for every edited rule. Exact requirement: "Do not remove a legitimate correctness requirement merely because it contains terminology associated with the previous architecture." Acceptance: read the corrected instructions and their obligation accounting and observe outcome verification, evidence-class separation, high-risk work-unit requirements, authorization gates, required checks, Git safety, truthful attribution, fix-first disposition, scope restrictions, Herald's exclusivity and user-only merge all retained.
- S11 — The adoption-status page presents no retired delegation contract as current and does not claim a whole-matrix reassessment. Exact requirement: "odd-adoption-status.md must not present retired delegation contracts as current instructions." / "Do not claim that an entire historical matrix has been reassessed if only its affected rows were corrected." Acceptance: read the page and observe the affected row naming current owners and the pre-revision disclosure unchanged in force for the untouched rows.
- S12 — Versioning follows the established convention and is reported. Exact requirement: "If the current rules prescribe a version increment for changed runtime specifications or skill contracts, follow the established convention and report it." Acceptance: read the skill metadata versions and the root version marker and observe each advanced for the actual change, with the governing rule named.
- S13 — No mechanism, artifact, historical record or unrelated behavior is added or altered. Exact requirement: "No new skills. No new subagents. No new hooks or plugins. No new scripts or validators." / "Historical records and accepted ADRs remain unchanged." Acceptance: read the delivered diff and observe only the eight authorized files plus this record, with no permission, registry, validator, agent or dependency change.

## Tasks

- T1 | S1, S2, S3, S7, S10, S12 | inline (shared and root workflow rules; owner is the primary agent) — Cipher 🔓 (Lead Orchestrator) | done | commit: f9ebfc2
- T2 | S4, S5, S6, S8, S9, S12 | inline (skill contract rewrites; owner is the primary agent) — Cipher 🔓 (Lead Orchestrator) | done | commit: c0c256a
- T3 | S11, S13 | inline (documentation correction and record closure preparation) — Cipher 🔓 (Lead Orchestrator) | done | commit: 08989f8

## Log

- L1 — Original request: the corrective proposal was approved for implementation, with F-10 through F-12 added to the nine confirmed findings and decision D-1 answered "INCLUDE". The authorization is preserved verbatim in the block below; its operative constraints are what S1–S13 measure.

````
# AICore — Skills-First Review Consistency Implementation Authorization

I approve the corrective proposal and authorize implementation of all nine confirmed findings, F-01 through F-09, subject to the additional requirements below.

Decision D-1: INCLUDE the incident-workflow correction.

Do not defer F-09 or register it as debt.

The investigation is complete. Do not initiate another design investigation, independent audit, specialist consultation, or proposal acceptance cycle.

Proceed directly with the authorized implementation.

## 1. Non-negotiable execution contract

The purpose of this remediation is to make the already-approved skills-first architecture consistent across every relevant active instruction.

Cipher performs specialized work directly using skills and canonical documentation.

The following distinction must remain unambiguous throughout the repository:

- Automated verification: applicable objective checks.
- Self-review: the primary agent reviews its own work directly.
- Independent review: a separate reasoning context reviews a candidate only after explicit user authorization.

Self-review is the normal execution route.

Independent review is strictly opt-in.

A recommendation is not authorization.

A high-risk classification, failed check, remediation, completed work unit, implementation completion, ODD closure, or PR preparation does not authorize an independent reviewer.

Ordinary requests to review, verify, check for bugs, or ensure correctness do not authorize independent delegation.

Do not use the built-in General or Explore subagent as a replacement for a retired specialist reviewer.

Herald remains the exclusive Git/GitHub executor, including read-only operations, and retains all existing safety responsibilities.

## 2. Implement F-01 through F-09

Implement the nine confirmed corrections from the proposal.

Preserve all legitimate original obligations while removing retired orchestration semantics.

Do not perform mechanical replacements of words such as independent, review, verifier, gate, or acceptance.

Their meaning depends on the surrounding procedure.

In particular, preserve:

- Independent technical judgment by Cipher.
- Observable-outcome verification.
- Separation between evidence classes.
- Existing high-risk work-unit requirements.
- Actual authorization gates.
- Required automated checks.
- Git safety and refusal rules.
- Truthful evidence attribution.
- Fix-first finding disposition.
- Scope and permission restrictions.

Do not remove a legitimate correctness requirement merely because it contains terminology associated with the previous architecture.

## 3. Additional correction F-10 — Complete the two-mode design of code-review

External inspection of the current `.agents/skills/code-review/SKILL.md` identified a material omission in the corrective proposal.

Changing the skill description and introductory sections is insufficient.

The following existing sections still predominantly describe an independent reviewer:

- What a reviewer must receive.
- Report format.
- How findings are disposed.
- Hard limits.

In particular, the current skill instructs the reviewer to return findings to the coordinator, not modify source, and remain read-only on source, tests, records and configuration.

These are legitimate restrictions for a separately dispatched independent reviewer.

They must not become restrictions on Cipher's normal implementation lifecycle.

Refactor the instructional structure of the existing skill to make the following two execution modes explicit.

### Mode A — Primary-agent self-review

This is the default and normal mode.

Cipher must:

- Select and load the skill for applicable code self-review.
- Obtain the actual candidate and Git-derived evidence through Herald where necessary.
- Apply the existing technical review rubric directly.
- Identify evidence-based defects and risks.
- Correct in-scope defects directly under the existing authorization.
- Run or rerun applicable verification when changes require it.
- Report the actual results as self-review.
- Continue the authorized task without an acceptance handoff.

The act of reviewing may be observational, but loading the skill must not revoke the primary agent's existing authority to correct findings afterward.

Do not require a separate reviewer evidence packet, reviewer verdict, acceptance report, sign-off artifact, or coordinator handoff for routine self-review.

Use the existing task evidence and reporting procedures.

Self-review must remain proportionate to the change.

### Mode B — Explicitly authorized independent review

This mode is available only after explicit user authorization covering that review.

The separate reviewer:

- Receives the exact candidate identity, requirements, changed paths, applicable rubric and existing evidence.
- Remains read-only.
- Does not modify source, tests, records, or configuration.
- Does not execute Git or GitHub commands.
- Returns evidence-based findings to Cipher.
- Does not become an approval authority or universal delivery prerequisite.
- Does not automatically re-review remediation.

Cipher evaluates and disposes the returned findings under the existing fix-first and user-authorization rules.

### Shared rubric

Keep one canonical technical review rubric.

Do not duplicate the correctness, consistency, scope, public-API, architecture, testing, behavioral evidence, dead-code, and residual-risk criteria between the two modes.

The difference between the modes is the execution context and its responsibilities, not the technical standard.

Scope the existing reviewer-specific input requirements, verdict formatting, handoff instructions, and read-only restrictions to the independent-review mode wherever appropriate.

Do not weaken any Git restriction or grant authority through the skill.

The skill is a procedure, not a permission boundary.

Inspect its entire final content, including frontmatter, applicability, headings, procedure, report format and hard limits, before declaring F-05 and F-10 resolved.

## 4. Additional correction F-11 — Eliminate automatic re-review cycles

The canonical Mermaid diagram currently allows independent-review findings to return to implementation and eventually reach the independent-review dispatch decision again.

Ensure this does not automatically reuse the original review request as authorization for repeated independent reviews.

An independent-review authorization applies to the candidate and review scope it covers.

If a later correction changes that candidate:

- Preserve the previous review evidence and its actual candidate identity.
- Do not describe the previous verdict as applying to the changed candidate.
- Correct evidenced defects directly.
- Execute applicable self-review and automated verification.
- Update delivery evidence truthfully.
- Do not automatically dispatch a new independent reviewer.

A further independent review is permitted only when covered by the user's explicit authorization.

If the user explicitly authorizes multiple review rounds, respect the limits of that authorization. Otherwise, do not infer continuing authorization.

Correct the Mermaid diagram and its interpretation so that the optional review branch cannot create an unrequested recursive review cycle.

Preserve the existing ODD scope-change and closure-reopening requirements when a correction genuinely affects closed work.

The absence of a current independent verdict is not a blocker merely because an earlier candidate was independently reviewed.

## 5. Additional correction F-12 — Complete incident-workflow consistency

I approve inclusion of F-09, but do not limit the correction to adding a conditional phrase around AWAITING_REVIEW.

Inspect the actual incident-workflow execution path within the three already identified files:

- `.agents/skills/incident-workflow/SKILL.md`
- `.agents/skills/incident-workflow/references/_consistency-checklist.md`
- `.agents/skills/incident-workflow/references/analysis/state.md`

Ensure the default route is direct execution by Cipher.

Cipher must be able to:

- Read ticket data through the appropriate authorized tools.
- Perform register-first identification.
- Establish and investigate hypotheses.
- Execute authorized queries.
- Evaluate evidence.
- Maintain incident state and counters.
- Perform structural and semantic self-verification.
- Synthesize the result.
- Prepare the response and complete authorized close-out.

None of these responsibilities inherently requires a separate agent.

Distinguish calling an MCP, tool, script, or skill from dispatching a subagent.

For direct execution:

- Cipher is the authoritative owner and sole writer of the applicable incident resources.
- Cipher maintains the existing counters and verification evidence directly.
- Cipher advances after the actual applicable prerequisites and checks are satisfied.
- Cipher does not return AWAITING_REVIEW to an imaginary parent.
- Cipher does not wait for parent acceptance.
- Cipher does not redispatch itself to continue.
- Cipher does not dispatch another agent solely to accept a hypothesis, validate an edit, or approve a phase transition.

Where a genuine separate-instance procedure is retained, clearly scope its resource-handoff and ownership rules to work actually authorized for delegation.

Do not introduce a new default delegation trigger.

A retained handoff procedure must not authorize delegation by itself.

A separately authorized independent reviewer remains read-only and must not acquire implementation ownership.

Preserve the existing incident safeguards:

- Register-first identification.
- The H1 → H2 → H3 order.
- Hypothesis allowance.
- Query allowance.
- Same-query rerun limits.
- SLA warning.
- One authoritative incident budget.
- No counter resets or allowance cloning.
- One active writer per mutable resource.
- Non-overlapping destinations.
- Evidence integrity.
- Structural and semantic validation.
- Pre-close and post-close verification.
- External-operation and publication authorizations.

Do not change the incident schema, templates' data fields, validator implementation, query limits, or functional incident behavior.

If an additional active incident reference contains a genuine contradiction that cannot be resolved within the approved files, identify the exact path and request authorization for that narrow scope addition.

## 6. Correct the incident explanation

The investigation established that the existing instructions contradict one another.

It did not establish the model's internal reason for dispatching the General subagent.

Do not describe the autonomous dispatch as compliant with every existing rule: the existing skill already states that an independent review requires the user's decision.

The documented trigger conflicts with that existing authorization guard.

Preserve the distinction between:

- Confirmed contradictory instructions.
- Confirmed observed agent behavior.
- An unverified explanation of the model's reasoning.

No additional incident reproduction is authorized.

## 7. Documentation and canonical ownership

Update the existing canonical owners without creating duplicate workflow definitions.

In particular:

- AGENTS.md must contain the standing execution and authorization rule.
- agent-workflow.md must contain the correct ODD transitions, verification semantics and Mermaid diagram.
- agents.md must contain compatible shared reporting rules.
- code-review must correctly support the two execution modes.
- incident-workflow and its affected references must support direct execution.
- odd-adoption-status.md must not present retired delegation contracts as current instructions.

Preserve all seven original ODD steps.

Retain the documented local departure from upstream ODD concerning high-risk independent verification.

Do not introduce RDD.

Historical records and accepted ADRs remain unchanged.

For the adoption-status document, distinguish current statements from historical comparison results. Do not claim that an entire historical matrix has been reassessed if only its affected rows were corrected.

Check the existing versioning conventions before finalizing.

If the current rules prescribe a version increment for changed runtime specifications or skill contracts, follow the established convention and report it. Do not invent a new versioning policy or silently waive an existing one.

## 8. Authorized scope

The following eight existing files are authorized for modification:

1. `.aicore/core/knowledge/agent-workflow.md`
2. `.aicore/core/knowledge/agents.md`
3. `AGENTS.md`
4. `.agents/skills/code-review/SKILL.md`
5. `.agents/skills/incident-workflow/SKILL.md`
6. `.agents/skills/incident-workflow/references/_consistency-checklist.md`
7. `.agents/skills/incident-workflow/references/analysis/state.md`
8. `docs/architecture/odd-adoption-status.md`

Creation of the single governing ODD task record from the existing template is authorized.

Use the actual creation date under the established naming convention.

No existing historical ODD record may be modified.

No additional durable feature file is authorized. Re-verify the affected requirements in the existing durable feature contract and record the results through the existing procedure.

If an existing durable requirement genuinely requires modification, identify the exact change and request authorization.

No other file creation, deletion, movement, or modification is authorized.

Specifically excluded:

- Runtime permission changes.
- Core Sync engine changes.
- Distribution registry changes.
- Downstream repository access or modification.
- New skills.
- New subagents.
- New hooks or plugins.
- New scripts or validators.
- New governance mechanisms.
- New audit artifacts.
- Unrelated architectural or functional changes.

The additional corrections F-10 through F-12 are authorized within the existing eight-file modification scope.

Do not request another general approval merely because these corrections refine the already-approved implementation.

## 9. Implementation lifecycle

Create the governing ODD record as the sole bootstrap write.

Implement the proposed work units directly:

- WU1: root and shared workflow rules.
- WU2: code-review and incident-workflow corrections.
- WU3: adoption-status documentation and applicable closure preparation.

Use the existing ODD evidence and work-unit commit requirements.

Herald performs all Git/GitHub operations.

Do not delegate implementation or self-review to another agent.

When a work unit completes, review the actual candidate yourself using the applicable rubric and verify the affected outcome.

Continue to the next authorized work unit without waiting for another agent's acceptance.

Use the existing closure and delivery mechanics.

Do not create additional review rounds or checkpoint artifacts.

## 10. Verification

Use the verification plan from the proposal, with the following requirements.

### Documentation walkthroughs

Complete the previously defined scenarios A–L as read-and-trace exercises.

Also verify these specific paths:

- Cipher loads code-review, finds an authorized defect, fixes it directly and continues.
- Cipher completes a high-risk work unit with green checks and no independent-review authorization.
- Cipher receives findings from an authorized independent reviewer, corrects the candidate and does not automatically dispatch a second review.
- Cipher executes a complete incident workflow without separate-instance acceptance.
- A genuine incident resource handoff retains its ownership and accounting safeguards without becoming a default delegation path.
- Calling an MCP or specialized tool does not create an independent reviewer.
- The canonical Mermaid diagram has no unrequested reviewer-dispatch or recursive review path.

Do not launch synthetic agent tasks or additional sessions to exercise these scenarios.

### Existing checks

Run the applicable existing checks:

- ODD task-record validation.
- Durable feature-file validation.
- Applicable lint and formatting checks.
- Existing affected-path validation.

Do not invent a test runner or modify executable tests for this documentation-only remediation.

If the whole-repository formatting check fails on historical files, establish the actual base-versus-candidate evidence before classifying the failures as pre-existing.

Do not assume the affected historical paths from earlier reports are still the same.

Every new or modified file must pass its applicable formatting check.

Do not modify historical files to obtain a green result.

### Final semantic consistency check

Perform one focused self-review of the corrected active instructions and their relevant consumers.

Verify that:

- No active instruction authorizes an independent reviewer without explicit user authorization.
- No high-risk recommendation is conflated with dispatch.
- No retired independent feature gate remains.
- No default incident path requires parent acceptance.
- No independent-review restriction incorrectly revokes Cipher's normal implementation authority.
- No reviewer-specific handoff is required for self-review.
- No unrequested recursive review cycle remains.
- The code-review skill is discoverable for normal review requests.
- Existing correctness, evidence and safety requirements remain intact.

Use the existing evidence and rewrite-accounting requirements without creating a separate audit artifact or new acceptance mechanism.

Do not delegate this final check.

Do not claim that documentation inspection guarantees future model compliance.

## 11. Delivery authorization

I authorize:

- The scoped corrections described above.
- One governing ODD task record.
- One feature branch.
- Coherent work-unit commits through Herald.
- One PR published through Herald following the existing closure requirements.

I do not authorize merging the PR.

Do not make the absence of an independent reviewer a delivery blocker.

If a genuine unresolved issue prevents a specific authorized operation, report its evidence and the exact decision required.

Continue all unaffected authorized work.

## 12. Final report

When the authorized implementation and applicable verification are complete, report:

- PR URL and exact final head SHA.
- Exact file inventory.
- F-01 through F-12 dispositions.
- Corrected code-review execution modes.
- Corrected incident-workflow execution model.
- Corrected ODD transitions and Mermaid diagram.
- Existing verification commands and observed results.
- Documentation walkthrough results.
- Any remaining genuine limitation or unresolved blocker.
- Versioning decisions and their governing rule.
- Confirmation that historical records and unrelated functionality remain unchanged.
- Confirmation that no independent reviewer was dispatched.

Do not claim that self-review was independent verification.

Do not initiate another reviewer acceptance cycle.

Finish with an explicit FINALIZED status when the work is complete, and await my merge decision.

The goal is not to eliminate review.

The goal is to preserve rigorous technical review while ensuring the primary agent performs it directly by default, without recreating the retired multi-agent orchestration.
````

- L2 — Classification and baseline. Non-small — the change edits the root runtime rule, two injected shared rule files, two skill contracts and their references, and needs a governing record; it is not resumable from the request plus a diff. Baseline measured before the first edit: `pnpm format:check` reported `Checked 450 files in 51ms. No fixes applied` with exit 0, so the pre-existing formatting failures asserted by `2026-11-24-odd-record-state-reconciliation` L18 no longer hold and cannot be used to excuse any failure of this change. Durable-feature ownership: `odd/features/agent-workforce.md` already owns this capability through R4 and R7; both are re-verified and neither requires a wording change, so no feature file is edited and no new one is created.
- L3 — WU1 delivered in `f9ebfc2`. `AGENTS.md` now requires self-review before completion, names the three review skills, states that reviewing revokes no authority, keeps `Risk:` line, own commit and self-assessment for high-risk work, and states that an independent review runs only on explicit authorization — with recommendation, risk, completion, closure and ordinary review requests named as non-authorizing. `agent-workflow.md` guards the diagram edge on authorization of the candidate, makes the primary agent the challenger in H/I, states opt-in and non-renewal in AG/AH/AJ/AI, splits automated verification, self-review and independent review into three bullets, advances step 6 to outcome verification, and drops the retired gate term from the compact-report rule and the decision-only-stops sentence. `agents.md` names an authorization pause or an unresolved prerequisite. Root spec marker advanced 7.0.0 → 7.0.1.
- L4 — WU2 delivered in `c0c256a`. `code-review` now declares Mode A (default, direct, correcting, proportionate, no artifact, no handoff) and Mode B (explicitly authorized, read-only, non-authoritative, candidate-scoped, non-renewing) over one unmodified rubric, scopes the reviewer-input, verdict-format and read-only sections to Mode B, and selects itself for an ordinary review request from its description; metadata version 1.0.0 → 1.1.0. `incident-workflow` states direct execution as the default route, prefixes the dispatch, isolation and handoff bullets with delegated-only scope, gives `AWAITING_REVIEW` a delegated run and a direct-execution counterpart, states that a recorded dispatch procedure never authorizes delegation, renames step 5 to "Continue with the owning writer", names Cipher as the default investigate writer, and splits collapse acceptance by mode; the checklist and `analysis/state.md` carry the same scoping. Metadata version 5.0.0 → 5.0.1.
- L5 — WU3 delivered in `08989f8`. The adoption-status "Delegation and skills" row names its current owners and the current rule instead of a retired subagent-dispatch contract and an independent routing gate, and a dated bullet states that this row alone was corrected while every other row keeps its pre-revision reading.
- L6 — Rewrite acceptance accounting. Originals and candidates are the two committed states of each listed file (`daffd976` → `f9ebfc2`, `c0c256a`, `08989f8`). Retained unchanged: the automated-verification gate; self-review never being independent verification; high-risk own commit, `Risk:` line and self-assessment; recommendation-never-required; findings disposition by fix-first; not-a-prerequisite, absence-is-not-a-check and no stand-in verdict; the permission-envelope limit; every ODD step, forecast, scope-change, mirror, runner-selection, incomplete-evidence and task-navigation rule; the code-review rubric in all four groups with its report format, `[PASS]` zero-open-findings rule, INFO distinction and owner pointers; the reviewer-input requirements and read-only limits; the no-new-acceptance-mechanism limit; every incident safeguard (register-first, H1→H2→H3, `3/3`, `0/6`, `0/2`, 75% SLA, one budget, no resets or cloning, one writer per resource, non-overlapping destinations, structural and semantic validation, pre-close and close-out, external-operation authorizations, "role identity is not independence"); the matrix's upstream-intent, evidence and unverified columns and the October 28 supersession note. Translated: the three code-review occasions into two modes keeping all three; the conditional dispatch recipe into an authorization-gated clause; the unconditional coordinator dispatch, handoff and `AWAITING_REVIEW` clauses into delegated-run scope with an explicit direct-execution counterpart; the retired-gate vocabulary into authorization-pause and unresolved-prerequisite vocabulary. Retired: only the claim that a "declared subagent-dispatch contract" exists, which no longer does. Added: authorization-coverage and non-renewal rules, Mode A's retained authority, and the ordinary-request discovery trigger. Source neutrality holds — no destination runner, pin or local policy value was introduced.
- L7 — Verification, with base and candidate measured. After all edits: `pnpm format:check` reports `Checked 450 files in 75ms. No fixes applied` (exit 0; 450 rather than 451 because `odd/tasks/**/*.md` is outside the Markdown formatter's scope); `pnpm lint` reports `$ oxlint` with no finding (exit 0); `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks` reports every record `ok`, 35 of 35 including this one; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts odd/features` reports all 16 `ok` with `agent-workforce.md` at derived status `achieved`. One defect was introduced and fixed before its commit: the corrected matrix row needed realigning — `pnpm exec biome format --write docs/architecture/odd-adoption-status.md` reformatted that one file, our own change, and touched no historical content. Durable-feature re-verification for this change: `agent-workforce.md` R4 holds — the rubric is not presented as an independent reviewer, the separate context is the source of independence rather than the skill, and the permission-envelope limit stands — and R7 holds — review only on request, recommendation permitted, never a prerequisite. No requirement text changed and no tick moved. First failure: no applicable executable failure exists for this change, which edits instructions and prose so no behavioural test can fail RED; the only executable checks are the corpus validators, lint and formatting, and the single real defect it produced was caught by `format:check` and corrected before commit.
- L8 — Documentation walkthroughs, read-and-trace only; no session, reviewer or synthetic task was launched. A: direct, no artifact, no reviewer. B: artifact-free route plus mandatory self-review, now discoverable. C: step 6 hands to outcome verification and delegation stays a justified choice. D: risk is assessed, the work unit carries its own commit and self-assessment, review is recommended and never dispatched. E: a failed check remains a blocker and is never resolved by a reviewer's presence. F: closure needs the verified outcome and no acceptor. G: PR readiness is decided by checks and items, with the verdict line optional. H: a corrected candidate keeps the earlier verdict against its real candidate and is not re-dispatched. I: the authorized route exists and stays non-default. J: no active record predates this contract — every one of the 34 pre-existing records is `closed` — and the corrected matrix row no longer asserts a stale owner. K: `dependency-review` and `visual-review` stay self-contained with no role requirement. L: an ordinary review request selects Mode A. Target paths: loading the rubric, correcting directly and continuing holds; a high-risk unit with green checks and no authorization dispatches nothing; authorized findings are corrected without a second dispatch; a genuine handoff keeps its ownership and accounting without becoming a delegation path; calling an MCP, script or skill creates no reviewer; and the diagram has no unrequested or recursive review path. The one path that does **not** hold is the complete incident workflow: see the blocked entry below.
- L9 — Self-review of the delivered candidate in Mode A, applying the rubric at the three commits. Cross-file consistency: each of the three verification mechanisms is defined once in `AGENTS.md`, restated only as a pointer elsewhere, and no file still routes a high-risk item into a dispatch. Scope: no path outside the eight authorized files and this record was touched; no mechanism, script, registry, permission or agent was added. Dead instructions: no surviving reference to the retired "third case", to a coordinator dispatch in the incident default path, or to the removed gate vocabulary in an active rule. Public contract: every skill's frontmatter keeps its required fields and no new required field was introduced; the code-review rubric is intact. Evidence truthfulness: no claim of independent verification appears anywhere in the record or the instructions. Two defects were found and fixed during this pass rather than after delivery: the diagram carried an unnecessary `<br/>` tag, replaced by a single-line label, and the corrected matrix row needed the formatter realignment recorded at L7.
- L10 — Blocked: 2026-11-24 — one requirement cannot be satisfied inside the authorized file set. `references/analysis/02-investigate.md:3` opens with "STOP — assigned-writer step only. This step runs under the coordinator's assignment (see `AGENTS.md` § Roster). Do not execute these steps without that assignment.", and the same assignment/acceptance/cessation framing recurs at `01-identify.md:10,12,31,61`, `02-investigate.md:5–6,12,14,16,24,28,35,82` and `03-synthesize.md:4,10,12,21,29,62`. Those three files are outside the eight authorized paths, and `AGENTS.md` § Roster now names no assignment mechanism, so the investigate step still requires a separate writer before it can run. S8 therefore holds for the skill, the checklist and `state.md` and fails for the step templates. The required decision is a narrow scope addition covering exactly those three reference files, with the same delegated-run scoping already applied to the authorized files. Every other authorized requirement is satisfied; nothing was closed and no pull request was published.
