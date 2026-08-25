# Phase 1 — Confirmation-flow remediation

> **Owner:** Cipher 🔓 (L2 Lead)
> **Pre:** No active plan, empty stash inventory, approved G1-G4, and no user-story requirement.
> **Reads:** `.opencode/skills/plan-enforce/SKILL.md` and `plans/plan-goal-confirmation-presentation-20260824/plan.md`
> **Writes:** `.opencode/skills/plan-enforce/SKILL.md`

## Steps

1. Add an explicit presentation requirement to the Confirm gate: render the goal list as individual Markdown items before invoking the question tool.
2. Require plan type, user-story scope, and any goal-bloat notice to appear in a separate visible classification block before the question tool.
3. Restrict the question text to a concise proceed/revise decision that refers to the already displayed information; retain the one-question pre-file gate.
4. Update the Create new plan step and the goals-lifecycle example to use the same presentation order.
5. Bump the plan-enforce skill version for the compatible contract correction.
6. Re-read the skill and confirm no instruction asks the question tool to carry the full goal list or classification block.

## Output

- **Artifact:** `.opencode/skills/plan-enforce/SKILL.md`
- **Schema / shape:** A readable Markdown-first confirmation contract with one concise question-only confirmation.

## Gate

- ☑ G1-G3 are satisfied without adding a second confirmation round or changing unrelated plan-enforce behavior.

## Abort conditions

- Stop if satisfying readability requires a second question-tool call or removes an existing pre-file confirmation requirement.
