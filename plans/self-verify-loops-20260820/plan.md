# Plan — self-verify loops for plan-enforce and ticket-runbook

> **Status:** active
> **Started:** 2026-08-20 18:37
> **Subject:** Add parallel self-verification tooling (canonical checklist + validator script + post-write loop) to plan-enforce and ticket-runbook, migrating ticket-runbook's missing template/validator from the source project.
> **Layout:** subfolder pattern

## Context

> Why is this being done? What prompted it? What is the intended outcome?

- Prompted by: both skills write files and then stop without re-checking them; repeated manual double-checks found inconsistencies the skills should have caught themselves.
- Goal: give each skill a post-write self-verification loop — a canonical checklist (contract) + a mechanical validator script (helper) + an analysis loop — so written artifacts are consistent before reporting done.
- Outcome: plan-enforce and ticket-runbook each self-verify their own artifacts; ticket-runbook's missing runbook template/validator are migrated and neutralized.
- Story: skipped — core tooling plan (AICore's own skill infrastructure), not a product feature; consistent with prior AICore tooling plans.

## Goals

- ⬜ **G1:** plan-enforce self-verifies its written artifacts (plan.md, phase files, user story, index) before reporting done.
  - Done when: `references/_consistency-checklist.md` exists; `scripts/validate_plan.py` + `test_validate_plan.py` pass; `SKILL.md` has a post-write loop; `sentinel.md` rules 7/8 point at the checklist; frontmatter `version: 1.5.0`.
- ⬜ **G2:** ticket-runbook's missing runbook template + validator are migrated into AICore and neutralized.
  - Done when: the 9 runbook/ticket/response-draft templates exist under `references/`; `scripts/validate_runbook.py` + `test_validate_runbook.py` exist and the test passes; no tismart/SDP/Activo/domain-agent content remains in the migrated files.
- ⬜ **G3:** ticket-runbook self-verifies its written artifacts (runbook, phase files, folder structure) before reporting done.
  - Done when: `references/_consistency-checklist.md` exists; `SKILL.md` has a post-write loop; frontmatter `version: 1.1.0`.

## Current state

| Area | Current file / behavior | Evidence (file + line / command output) |
|---|---|---|
| plan-enforce skill | writes plan/phase/story/index then stops; no re-read of its own output | `.opencode/skills/plan-enforce/SKILL.md` (create-new-plan steps 9–12; no post-write check) |
| plan/phase/story contract | fragmented across templates, SKILL.md invariants, sentinel rules 7/8 | `.opencode/skills/plan-enforce/references/_template*.md`; `.opencode/agents/sentinel.md:89-100` |
| ticket-runbook skill | cites "the project's runbook template" + validator, neither shipped in AICore | `.opencode/skills/ticket-runbook/SKILL.md:76,87` |
| runbook template/validator | present only in the source project | `tismart-support/tickets/_template/runbook/*.md`, `tickets/validate_runbook.py` |
| sentinel plan scope | `plans/*.md` only — misses subfolder plans + phase files | `.opencode/agents/sentinel.md:32,89` |

## Behavior change

| Goal | Before | After | Interface contracts | Do-not-break |
|---|---|---|---|---|
| G1 | plan-enforce writes then stops | loop: re-read → validate_plan.py → analysis → fix → repeat (S-07 cap) | `_consistency-checklist.md` is canonical; sentinel rules 7/8 point at it | sentinel still audits plans/user-stories |
| G2 | runbook template + validator absent from AICore | 9 templates + validate_runbook.py migrated + neutralized | `references/runbook/*.md`, `scripts/validate_runbook.py` | existing runbook schema (7 header fields, kill-switches, 6 phases) |
| G3 | ticket-runbook cites an absent template/validator | local template + validate_runbook.py + loop | `references/`, `scripts/` local paths | existing runbook schema (7 header fields, kill-switches, 6 phases) |

## Design decisions

- Checklist + validator + loop per skill, parallel and independent — mechanical subset (enums, sections, placeholders) is script-enforced; semantic correctness (values match evidence, verdict/naming consistency) stays in the agent's analysis loop. Rejected: script-as-full-authority (would skip analysis); one shared checklist for both skills (different artifacts).
- Canonical checklist lives in each skill's `references/` — Sentinel 🛡️ (Quality Guardian) points at plan-enforce's checklist; validate_runbook.py enforces ticket-runbook's mechanical subset. Rejected: keeping criteria split across 3 files (drift).
- `scripts/` for Python validators, `references/` for markdown templates — matches `op-model/scripts/` + `plan-enforce/references/` convention.
- Skip user story — core tooling, not a product feature.

## Phase index — dispatch table

| # | Phase | Owner | Runbook | Output | Goals |
|---|---|---|---|---|---|
| 1 | plan-enforce self-verify tooling | Vault 🔐 (Catalog Steward) | `phase-01-vault.md` | `_consistency-checklist.md`, `validate_plan.py`, `test_validate_plan.py`, `SKILL.md` (loop + 1.5.0) | G1 |
| 2 | ticket-runbook migration + self-verify tooling | Vault 🔐 (Catalog Steward) | `phase-02-vault.md` | migrated templates (9), `_consistency-checklist.md`, `validate_runbook.py`, `test_validate_runbook.py`, `SKILL.md` (loop + 1.1.0) | G2, G3 |
| 3 | sentinel pointer + scope | Sentinel 🛡️ (Quality Guardian) | `phase-03-sentinel.md` | `sentinel.md` (rules 7/8 pointer, `plans/**`) | G1 |

> Every phase traces to ≥ 1 goal ID. A phase with no Goals column entry is speculative — remove or merge it.

## Critical files / tools

- `.opencode/skills/plan-enforce/SKILL.md` + `references/`
- `.opencode/skills/ticket-runbook/SKILL.md`
- `.opencode/agents/sentinel.md`
- Source for migration: `tismart-support/tickets/_template/` + `tickets/validate_runbook.py` + `test_validate_runbook.py`

## Verification

- ⬜ G1: `python3 .opencode/skills/plan-enforce/scripts/test_validate_plan.py` → exit 0
- ⬜ G1: `sentinel.md` rules 7/8 point at `_consistency-checklist.md`; `plan-enforce/SKILL.md` loop present + `version: 1.5.0`
- ⬜ G2: `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/test_validate_runbook.py` → exit 0
- ⬜ G2: `grep -riE --exclude-dir=.venv '\b(tismart|sdp|activo|belcorp|ember|atlas|ranger|lex)\b' .opencode/skills/ticket-runbook/` → no matches. `## Gate` is required runbook-template structure, not neutralization residue.
- ⬜ G3: `ticket-runbook/SKILL.md` loop present + `version: 1.1.0`

## Out of scope / Do-not-touch

- `validate_tickets.py`, `ticket_models.py`, `schema.json`, `generate_schema.py` (ticket-record frontmatter — Ledger's domain)
- `knowledge/agents.md`, `knowledge/symptoms.md`, `knowledge/problems.md`
- Other skills (`op-model`, `migrate-core-to-project`, git skills)

## Resolved decisions

- 2026-08-20 — response-facing prose stays Spanish (publication language); framework/headers English.
- 2026-08-20 — scripts are mechanical helpers; semantic correctness stays in the agent's analysis loop.
