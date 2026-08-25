# Phase 3 — Agent-spec audit

> **Owner:** Sentinel 🛡️ (Quality Guardian)
> **Pre:** Phase 1 gate passed and the Herald runtime-spec edit is available for review.
> **Reads:** `.opencode/agents/herald.md` and `plans/git-convention-alignment-20260824/plan.md`
> **Writes:** none.

## Steps

1. Audit the Herald runtime-spec change for document consistency, roster naming, internal convention alignment, imperative hard-rule language, and accidental scope expansion.
2. Return a PASS, ADVISORY, or BLOCK report with exact file and line references for every finding.

## Output

- **Artifact:** Sentinel report returned to Cipher 🔓 (L2 Lead); no persisted file.
- **Schema / shape:** PASS, ADVISORY, or BLOCK plus evidence-grounded findings and required remediation, if any.

## Gate

- ☑ Sentinel verifies G4-G5 after the user-approved imperative correction.

## Abort conditions

- Stop if Sentinel identifies an issue requiring changes outside the approved manifest.
- Stop if a BLOCK cannot be resolved without changing a confirmed goal.
