# User story — plan-enforce-execution-review

> **Created:** 2026-09-27
> **Title:** Plan-enforce execution review
> **Status:** active
> **Epic:** plan-governance
> **Affected areas:** `.opencode/skills/plan-enforce/`, `AGENTS.md`, `user-stories/`

## Persona

- Cipher 🔓 (Lead Orchestrator), who must show a finished plan in human-readable issue / goal / how / files form and wait before implementation.

## Goal

- **G:** After plan files are written, the user gets a review turn. Implementation does not start in the same turn.
  - Done when: the last message and `plan.md` each state, per goal, the issue, the goal, how it is fixed, and the files; Forge 🔨 (Implementer) is dispatched only on a later explicit user ask.

## Scenario

- Cipher 🔓 (Lead Orchestrator) finishes writing a plan. The next chat message is the execution-review: for each goal, issue then goal then how then files, in prose. Cipher 🔓 (Lead Orchestrator) stops. Forge 🔨 (Implementer) runs only after the user later says to execute.

## Acceptance criteria

- ✅ After plan files and self-verification, Cipher 🔓 (Lead Orchestrator) sends the execution-review message and does not dispatch Forge 🔨 (Implementer) in that turn. Evidence: `plan-enforce` SKILL.md 1.14.0 step 13 and lifecycle row `Plan files written`; Sentinel 🛡️ (Quality Guardian) `[PASS]` 2026-09-27.
- ✅ The message is human-readable prose per goal in order Issue, Goal, How, Files. A recap table does not replace that prose. Evidence: SKILL.md `## Execution-review message`.
- ✅ `plan.md` templates carry the same per-goal Issue / How / Files layout. Evidence: `references/_template.md`; `references/_template-programming.md`.
- ✅ `AGENTS.md` forbids a Forge 🔨 (Implementer) dispatch in the same turn as the execution-review message, and forbids a corrective, release, or scope-change question without that file list. Evidence: `AGENTS.md` 2.4.0 Conventions.
- ✅ Independent audit `[PASS]` and the stash gate still apply on the later execution turn. Evidence: SKILL.md Forge 🔨 (Implementer) dispatch lifecycle row.
- ✅ Before creating a new story file, Cipher 🔓 (Lead Orchestrator) presents index-filtered candidates with evidence and obtains an explicit UPDATE / rename / CREATE choice. CREATE without that choice is a violation. Evidence: SKILL.md User stories and User-story collision gate.

## Change log

- 2026-09-27 — runbook-budget-and-plan-review-20260927: created the feature definition for the post-write execution-review message and the hard stop before Forge 🔨 (Implementer).
- 2026-09-27 — runbook-budget-and-plan-review-20260927: locked CREATE-after-analysis; `plan-enforce-plan-audit-gate` stays the validator-plus-`[PASS]` story.
- 2026-09-27 — runbook-budget-and-plan-review-20260927: implemented plan-enforce 1.14.0 and `AGENTS.md` 2.4.0 — execution-review stop, per-goal Issue / How / Files templates, and CREATE only after an explicit UPDATE / rename / CREATE choice.

## Resolved decisions

- 2026-09-27 — this is a separate story from `plan-enforce-plan-audit-gate`; audit `[PASS]` remains required on the execution turn and is not the review message.
- 2026-09-27 — user locked keep-this-story after collision analysis; CREATE requires an explicit UPDATE / rename / CREATE choice.
