# Phase 2 — Skill quality audit

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** Phase 1 gate passed and the changed plan-enforce skill is available.
> **Reads:** `.opencode/skills/plan-enforce/SKILL.md` and `plans/plan-goal-confirmation-presentation-20260824/plan.md`
> **Writes:** none.

## Steps

1. Audit the changed confirmation contract for readability, one-question gate preservation, goal/type/story/bloat completeness, and scope containment.
2. Return a PASS, ADVISORY, or BLOCK report with exact file and line references for every finding.

## Output

- **Artifact:** Vault report returned to Cipher 🔓 (L2 Lead); no persisted file.
- **Schema / shape:** PASS, ADVISORY, or BLOCK plus evidence-grounded findings and required remediation, if any.

## Gate

- ☑ Vault returns PASS after the goal-bloat presentation instruction was aligned with the Confirm gate.

## Abort conditions

- Stop if Vault identifies a correctness issue outside the approved write manifest.
- Stop if a BLOCK cannot be resolved without changing a confirmed goal.
