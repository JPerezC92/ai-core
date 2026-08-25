# Plan — Debt register retirement rule

> **Status:** active
> **Started:** 2026-08-25 13:28
> **Subject:** Add the clear+retire-in-same-PR lifecycle to the accepted-debt register
> **Layout:** subfolder pattern

## Context

- Prompted by: the debt register only grows — cleared entries stay forever and the original flow offered no removal path without a dedicated prune PR.
- Goal: the register holds open debts only; a debt leaves in the same PR that clears it.
- Outcome: `knowledge/debt.md` defines record → disclose → clear+retire lifecycle; DEBT-001 is retired by this change's own PR.
- User story: skipped; this is a non-programming governance-docs change with no feature-visible behavior.

## Goals

- ⬜ **G1:** `knowledge/debt.md` `## Rules` defines the full debt lifecycle — record, disclose, and clear+retire in the same PR; the clearing PR deletes the entry with Resolution evidence in its body/commit, the register holds open debts only, and dedicated prune PRs are forbidden.
- ⬜ **G2:** `DEBT-001` is removed from the register in this same change; its evidence already persists in PR #7's body, git history, and the merged plan archive, leaving the register with no open debts.
- ⬜ **G3:** The change passes a Sentinel 🛡️ (Quality Guardian) governance-doc spot-audit and ships via the standard branch → PR → review → merge flow, never a direct `main` commit.

## Body

- Rewrite the third register rule from "Clearing a debt updates the record" to the clear+retire-in-same-PR rule with git-history-as-archive rationale.
- Add an explicit prohibition on dedicated prune PRs.
- Remove the DEBT-001 entry as the rule's first application; note the retirement in the retirement-PR body (not in the register).
- Keep the entry format, the other two rules, and Herald's open-debt disclosure duty unchanged.

## Phase index — dispatch table

| # | Phase | Owner | Runbook | Output |
|---|---|---|---|---|
| 1 | Retirement-rule edit + DEBT-001 prune (G1-G2) | Cipher 🔓 (L2 Lead) | `phase-01-retirement-rule.md` | Updated `knowledge/debt.md` |
| 2 | Governance-doc audit (G3) | Sentinel 🛡️ (Quality Guardian) | `phase-02-sentinel-audit.md` | Sentinel audit report |

## Critical files / tools

- `knowledge/debt.md`

## Verification

- ☑ Phase 1 output: the Rules section defines clear+retire-in-same-PR, forbids prune PRs, and the register holds no entries.
- ☑ Phase 2 output: Sentinel returns PASS; its optional tagline-clarity advisory was applied (line 20 now reads "each debt is retired by exactly one PR: its clearing PR").

## Out of scope

- Changing Herald's disclosure duty, AGENTS.md, agent runtime specs, plan-enforce templates, or the validator.
- Migrating historical debt data anywhere other than git history.

## Resolved decisions

- 2026-08-25 — User selected open-debts-only retention: the register shows only open debts at all times.
- 2026-08-25 — User rejected prune-on-merge-later (forces a second PR per debt); clearing PR deletes the entry itself — one debt, one PR.
- 2026-08-25 — Git history (clearing-PR body + commit) is the permanent record for retired entries; no archive section.
