# User story — <feature-slug>

> **Created:** YYYY-MM-DD
> **Title:** <short human title — mirrors the `title` column in `user-stories/index.md`>
> **Status:** <draft | active | superseded — mirrors the `status` column in `user-stories/index.md`>
> **version:** 1.0.0
> **Epic:** <epic-slug> (optional — leave empty when no epic)
> **Affected areas:** <matching handle, e.g. `src/`, `.opencode/skills/plan-enforce/`, a backend tooling path>

<!-- Status vocabulary: `draft` is work in progress and is NOT an approved planning contract;
     `active` is the approved contract `plan-enforce` derives goals from;
     `superseded` is retained history replaced by another story. Approval is a behavioral
     contract only — it is not implementation evidence, a permission grant, or execution authorization. -->

## Persona

> Who is the feature for? One actor, with their role in context.

- <persona, e.g. "an analyst who triages support tickets">

## Goal

> What must be true when this feature is done — the observable condition, not the activity.

- **G:** <goal>
  - Done when: <observable condition>

## Scenario

> The concrete situation the persona is in and the behavior the feature must provide.

- <scenario — trigger, action, result>

## Acceptance criteria

<!-- Reconciliation (approved-criteria scope, fail-closed): at plan completion only the criteria the plan
     selected to deliver, materially changed, or regressed are reconciled.
     ✅ = evidence-established (a completed goal's Done when:, a passing command, or a recorded outcome)
     ❌ = explicitly unmet — blocks the touching plan's completion until satisfied or removed
     ⬜ = a legitimate commitment the plan did not select — it remains and does not block completion
     Out-of-scope work is removed from these criteria (not left unchecked) and recorded in the change log.
     Release events (PR opened/reviewed/merged) are not acceptance criteria; record them in the change log.
     Each criterion is self-contained: it cites the surface it proves by section/symbol, never a plan-only goal, a temporal `plans/`/`output/` path, a volatile test count, or a superseded version (or a version number unless that version is the requirement). -->

- ⬜ <criterion 1>
- ⬜ <criterion 2>

## Change log

<!-- Bounded, newest last: at most 5 one-line entries, each
     - YYYY-MM-DD — <plan-slug>: <what changed about this feature>
     For a story-only revision made by the `user-story` skill with no plan, use the literal
     `story revision` in place of the plan slug — never invent a plan slug:
     - YYYY-MM-DD — story revision: <what changed about this feature>
     plus at most one rollup line once older entries are dropped:
     - before YYYY-MM-DD — earlier history: see git history for this file
     Process/execution narration (planning-only status, phase/gate results, counts) is NOT a change-log entry. -->

## Resolved decisions

<!-- Optional. Current, bounded set of decisions that still govern this feature (design constraint + why).
     Replace superseded decisions; never append without bound. Plan-execution/scheduling and superseded
     decisions are removed — git history retains them.
     Example: - 2026-05-20 — decided X over Y because Z -->
