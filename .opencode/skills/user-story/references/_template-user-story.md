# User story — <feature-slug>

> **Created:** YYYY-MM-DD
> **Title:** <short human title — mirrors the `title` column in `user-stories/index.md`>
> **Status:** <draft | active | superseded — mirrors the `status` column in `user-stories/index.md`>
> **version:** 1.0.0
> **Epic:** <epic-slug> (optional — leave empty when no epic)
> **Affected areas:** <matching handle, e.g. `src/`, `.opencode/skills/user-story/`, a backend tooling path>

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

<!-- Churn test (write-time, mandatory): if a criterion would need rewording when the
     implementation changes, rewrite it as observable behaviour or move it to
     `## Constraints`. Internal symbols, module paths, function signatures, test class
     names, and file inventories never appear here.

     Each criterion is self-contained and observable at a boundary (CLI output, file
     bytes, API response, screen, ops log) without reading code or internal state.
     It states the promise only. Where the promise is demonstrated belongs in `## Proof`.

     The churn test binds every criterion a plan writes or materially changes.
     Criteria untouched by a plan are grandfathered until that story is next revised.

     Every criterion carries a resolvable `AC<n>` id in positional order, so `## Proof`
     can reference it. The id is mandatory; a short name after an em dash is optional:
     `- ⬜ **AC1 — <optional name>:** <criterion>`.

     Reconciliation (approved-criteria scope, fail-closed): at plan completion only the criteria the plan
     selected to deliver, materially changed, or regressed are reconciled.
     ✅ = evidence-established, resolved through the story's `## Proof` section
     ❌ = explicitly unmet — blocks the touching plan's completion until satisfied or removed
     ⬜ = a legitimate commitment the plan did not select — it remains and does not block completion
     Out-of-scope work is removed from these criteria (not left unchecked) and recorded in the change log.
     Release events (PR opened/reviewed/merged) are not acceptance criteria; record them in the change log. -->

- ⬜ **AC1 — <optional name>:** <criterion 1>
- ⬜ **AC2:** <criterion 2>

## Proof

<!-- Where each criterion is demonstrated. Proof may go stale without invalidating the
     contract: a rename or refactor updates this section only. Each line is
     <AC-id> → <section or symbol> · <command/verdict>, and every AC id used here
     resolves to exactly one criterion above. The count of proof lines equals the
     count of criteria.
     Proof never states a requirement and never sets a criterion's status. -->

- AC1 → <section or symbol> · <command/verdict>
- AC2 → <section or symbol> · <command/verdict>

## Constraints

<!-- Pre-decided restrictions the plan must RESPECT, never deliver. Each entry carries
     its rationale in the form `— because <reason>`. Bounded to the currently governing
     set; superseded constraints are removed (git history retains them).
     Plan-execution and scheduling notes are not constraints.
     Example: - pytest is the single test runner — because one reviewed runner keeps the
     executor grant and the command literal from drifting. -->

- <restriction> — because <reason>

## Change log

<!-- Bounded, newest last: at most 5 one-line entries, each
     - YYYY-MM-DD — <plan-slug>: <what changed about this feature>
     For a story-only revision made by the `user-story` skill with no plan, use the literal
     `story revision` in place of the plan slug — never invent a plan slug:
     - YYYY-MM-DD — story revision: <what changed about this feature>
     plus at most one rollup line once older entries are dropped:
     - before YYYY-MM-DD — earlier history: see git history for this file
     Process/execution narration (planning-only status, phase/gate results, counts) is NOT a change-log entry. -->
