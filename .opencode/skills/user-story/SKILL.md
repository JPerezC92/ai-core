---
name: user-story
description: Define, revise, and collision-review a durable feature contract (user story) before implementation planning. Reconciles the story catalogue, discusses persona/goal/scenarios/acceptance criteria, records explicit approval, and hands the approved criteria to plan-enforce. Use when you want to define a feature story, modify an existing story, check story collisions, or settle feature behavior before planning.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.2.0
---

## What I do

Own the pre-plan feature contract. I create or revise a durable user story that states a feature's persona, observable goal, scenarios, and acceptance criteria; verify it against the whole story catalogue for semantic collisions; obtain explicit approval; and hand the approved story and its selected criteria to `plan-enforce`.

I settle **what the feature is** — never **how or when it is built**. Approval here is a behavioral contract, not a plan, permission grant, or authorization to execute code.

## When to use me

- A new feature's behavior must be defined before implementation planning.
- An existing story must be revised, superseded, or extended.
- Story ownership is ambiguous and possible collisions must be checked.
- Trigger keywords: "define a feature story", "modify an existing story", "check story collisions".

## Key paths

- Catalogue index: `user-stories/index.md`
- Story files: `user-stories/<feature-slug>.md`
- Canonical story template: `references/_template-user-story.md`
- Consistency checklist: `references/_consistency-checklist.md`
- Classification guide (what belongs in a contract): `references/_classification-guide.md`
- Handoff consumer: `.opencode/skills/plan-enforce/SKILL.md` (`### User stories`)

## Steps

1. **Reconcile the catalogue.** Enumerate `user-stories/*.md` and reconcile against `user-stories/index.md`. Every story file must appear in the index and every index row must resolve to a file. Report missing files, orphaned rows, or `Title`/`Status`/`Epic`/`Affected areas` mismatches — never interpret missing or ambiguous catalogue evidence as absence of a collision.
2. **Read every story body.** Read the whole catalogue before judging ownership; when it is large, use the index to filter by epic and affected areas, then read every candidate body in full. Respect each story's status — `draft`, `active`, `superseded`. A `draft` is in-progress discussion, not an approved contract.
3. **Present ownership choices.** Before writing anything, present the relevant existing persona/goals/scenarios as evidence and recommend one of:
   - **UPDATE** — revise the story that already owns the feature.
   - **rename / supersession** — the feature replaces, or is replaced by, another story; record the relationship explicitly.
   - **CREATE** — no story owns the feature.

   Wait for the user's explicit choice via the `question` tool. Shared affected files alone never prove duplicate ownership.
4. **Discuss the contract.** Work through persona, observable goal, scenarios, and acceptance criteria with the user. Each criterion is self-contained and names the surface that proves it, by section or symbol.
5. **Preview the delta.** Show the exact contract change — fields added, removed, or reworded — before writing. The user may authorize a persisted **draft**; a draft is not an approved planning contract.
6. **Run semantic collision analysis** against the whole catalogue: duplicate scenarios, contradictions, extension/supersession, dependencies, and shared affected areas. Report each collision with the paired statements and a recommended disposition. Unresolved contradictions block approval and handoff. This requires reading the stories — a keyword scan is not sufficient.
7. **Obtain explicit approval.** Ask for approval only after the collision review reports no unresolved contradiction. Approval establishes the contract; it does not establish implementation acceptance, grant permissions, or authorize execution. An existing approved contract is never silently overwritten while alternatives are discussed.
8. **Persist and mirror.** Write the approved contract to `user-stories/<feature-slug>.md` using the canonical template: behavioural acceptance criteria that pass the churn test, a `## Proof` section recording where each criterion is demonstrated, a bounded `## Change log` entry, and only currently governing `## Constraints` each carrying `— because <reason>`. Mirror `Title`/`Status`/`Epic`/`Affected areas` into `user-stories/index.md`.
9. **Hand off to `plan-enforce`.** Provide the approved story, the selected delivery criteria, governing constraints, and dependencies. Preserve remaining legitimate commitments as `⬜`. `plan-enforce` owns goal traceability and completion reconciliation — I do not create a competing completion policy and never archive a plan.

### Contract fields

- **Persona** — one actor, with their role in context.
- **Goal** — an observable condition, with a `Done when:` criterion.
- **Scenario** — trigger, action, result.
- **Acceptance criteria** — self-contained observable conditions at a boundary; they pass the churn test and carry no internal symbols, module paths, function signatures, test class names, or file inventories. No plan-only goal, temporal `plans/`/`output/` path, volatile test count, or superseded version.
- **Proof** — where each criterion is demonstrated (`<AC-id> → <section or symbol> · <command/verdict>`); may go stale without invalidating the contract and never sets a criterion's status.
- **Change log** — bounded to 5 recent one-line entries plus an optional rollup. Each entry carries a **durable anchor** — a commit SHA, PR number, or ticket ID — because `plans/` and `output/` are temporal and untracked. The label is the plan slug when one governed the work, otherwise the literal `story revision`; never invent a plan slug.
- **Constraints** — pre-decided restrictions the plan must respect, never deliver; each carries `— because <reason>`. `## Resolved decisions` is retired and is not written.

### Draft versus approved

| State | Meaning | Consumed by `plan-enforce`? |
|---|---|---|
| `draft` | Work in progress; discussion may still change it | No |
| `active` | The approved contract | Yes |
| `superseded` | Retained history replaced by another story | No |

A `draft` may be persisted without approval. Only an explicitly approved (`active`) story is a planning contract.

### Collision report shape

For each finding: the type (duplicate scenario / contradiction / extension / supersession / dependency / shared affected area), the two paired statements with their story slugs, the concrete conflict, and a recommended disposition. Block on unresolved contradictions.

## Boundaries

- I do not create implementation plans, edit application code, grant permissions, or split existing stories.
- I change another story only after an explicit approved collision resolution; a full-catalogue review does not authorize bulk rewriting.
- A persisted draft is not an approved planning contract.
- Approval is not implementation evidence or execution authorization.
- Semantic collisions require reading the stories, not a keyword scan; read-only mechanical validation reuses existing authorized facilities rather than a separate checker engine.

## Examples

**New feature.** The user says "I want a feature that drafts release notes." I reconcile `user-stories/index.md`, read every body, find no owner, recommend CREATE with the candidate list, discuss persona/goal/scenarios/criteria, run collision analysis, obtain approval, write `user-stories/release-notes.md`, mirror the index, and hand the selected criteria to `plan-enforce`.

**Existing feature.** The user says "make the story skill also support supersession." I recommend UPDATE on `user-story`, preview the added scenario and criteria, check the whole catalogue for contradictions, obtain approval, and append a dated `story revision` change-log entry.

**Ambiguous ownership.** Two active stories share an affected area. I present both personas/goals/scenarios as evidence, report whether they are a duplicate or a genuine extension, and wait for the user's UPDATE / rename / CREATE decision before writing.

## Troubleshooting

- **Index and files disagree:** report the mismatch as catalogue drift and resolve it before ownership analysis; never assume a missing row means no collision.
- **User wants a plan now:** route to `plan-enforce` only after the contract is approved; a draft is not a planning input.
- **Collision found but user wants to proceed:** stop; an unresolved contradiction blocks approval and handoff until the user resolves it (merge, supersede, or narrow scope).
- **Tempted to auto-check criteria:** don't; criterion disposition is semantic, evidence-to-checkbox analysis performed at plan completion, never auto-checked here.
