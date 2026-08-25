# Plan — Make plan-goal confirmation readable

> **Status:** active
> **Started:** 2026-08-25 00:27
> **Subject:** Resolve DEBT-001 by separating plan goals from the confirmation control
> **Layout:** subfolder pattern

## Context

- Prompted by: DEBT-001 records that plan-goal confirmation rendered all metadata and goals as an unscannable question-control paragraph.
- Goal: make each confirmed goal readable before the user is asked for a decision.
- Outcome: plan-enforce requires a Markdown goal presentation followed by a short question-only confirmation.
- User story: skipped; this is a non-programming process-contract change with no feature-visible behavior.

## Goals

- ⬜ **G1:** Before confirmation, plan-enforce requires every detected goal to appear as a separate readable Markdown `G1`...`Gn` item.
- ⬜ **G2:** The question control contains only a concise proceed/revise decision while plan type, user-story scope, and any goal-bloat notice are visibly separate.
- ⬜ **G3:** The rewritten flow still requires an explicit user confirmation before any plan or phase file is created.
- ⬜ **G4:** DEBT-001 records its resolution only after the changed skill and its plan artifacts pass validation and audit.

## Body

- Update the live plan-enforce Confirm gate and creation step so presentation precedes a short `question` call.
- Keep the one-question confirmation requirement; do not add a second confirmation round or weaken the pre-file gate.
- Update the lifecycle example so future maintainers do not restore the dense-control pattern.
- Update the accepted-debt record with resolution evidence after the audit passes.

## Phase index — dispatch table

| # | Phase | Owner | Runbook | Output |
|---|---|---|---|---|
| 1 | Confirmation-flow remediation (G1-G3) | Cipher 🔓 (L2 Lead) | `phase-01-remediation.md` | Updated skill contract |
| 2 | Skill quality audit (G1-G3) | Vault 🔐 (Catalog Steward) | `phase-02-vault-audit.md` | Vault audit report |
| 3 | Debt closure (G4) | Cipher 🔓 (L2 Lead) | `phase-03-debt-closure.md` | Resolved DEBT-001 record |

## Critical files / tools

- `.opencode/skills/plan-enforce/SKILL.md`
- `knowledge/debt.md`
- `.opencode/skills/plan-enforce/scripts/validate_plan.py`

## Verification

- ☑ Phase 1 output: the skill requires readable goal presentation before a concise question-only confirmation.
- ☑ Phase 2 output: Vault PASS confirms the contract is readable, complete, and contained.
- ☑ Phase 3 output: DEBT-001 records only the validator and Vault PASS evidence actually produced.

## Out of scope

- Changing the plan artifact schema, validator script, templates, user-story behavior, or stash lifecycle.
- Adding a second confirmation question, UI integration, dependencies, or source-code changes.

## Resolved decisions

- 2026-08-25 — The goal list is presented in Markdown before the question control; the control itself asks only whether to proceed or revise.
- 2026-08-25 — This remains a one-question pre-file gate; plan type, user-story scope, and goal-bloat information are presented separately rather than omitted.
- 2026-08-25 — Vault PASS and the validator results support DEBT-001 closure; the record cites those literal outcomes.
- 2026-08-25 — Explicit lifecycle exception (user-authorized): the stale duplicate plan `plans/git-convention-alignment-20260824/` — both the `Status: active` copy and the incomplete archive copy under `plans/.completed/` — was deleted verbatim on the user's direct instruction ("delete all") after the prior archive operation duplicated it. User authority overrides the never-delete-plan rule for this reconciliation only; no future deletion may cite this entry as precedent.
