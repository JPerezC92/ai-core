# Phase 2 — Skill quality audit

> **Owner:** Vault 🔐 (Catalog Steward)
> **Pre:** Phase 1 gate passed and its four runtime documents are available for review.
> **Reads:** `.opencode/skills/git-branch-name/SKILL.md`, `.opencode/skills/git-commit/SKILL.md`, `.opencode/skills/git-pr/SKILL.md`, and `plans/git-convention-alignment-20260824/plan.md`
> **Writes:** none.

## Steps

1. Audit the three changed skills for standalone completeness, Conventional Commits accuracy, chain consistency, scope-rule ambiguity, and scope creep.
2. Return a PASS, ADVISORY, or BLOCK report with exact file and line references for every finding.

## Output

- **Artifact:** Vault report returned to Cipher 🔓 (L2 Lead); no persisted file.
- **Schema / shape:** PASS, ADVISORY, or BLOCK plus evidence-grounded findings and required remediation, if any.

## Gate

- ☑ Vault returns PASS after the scope-taxonomy remediation.

## Abort conditions

- Stop if Vault identifies a correctness or lifecycle problem outside the approved manifest.
- Stop if a BLOCK cannot be resolved without changing a confirmed goal.
