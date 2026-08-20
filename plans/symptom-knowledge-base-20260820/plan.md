# Plan — Symptom-based knowledge base for incident + programming teams

> **Status:** active
> **Started:** 2026-08-20 03:58
> **Subject:** Ship a shared, team-guarded symptom knowledge base (symptoms.md taxonomy + problems.md register), wire it into the prior-art rules, and add it to the reuse core
> **Layout:** subfolder pattern

## Context

- Prompted by: user's symptom-knowledge-base idea (adapted from a proposal in another project); AICore already mandates prior-art scans ("Problem catalog", "Patterns register", "KBA/RCA catalogs") in `knowledge/agents.md` but none of those artifacts exist — the rule has nothing behind it.
- Goal: give the prior-art rule a real, neutral, team-guarded implementation shared by incident and dev teams, and ship it in the reusable core.
- Outcome: two knowledge files (symptoms.md taxonomy, problems.md known-problem register) + wiring edits to `knowledge/agents.md`, the `ticket-runbook` skill, and the `investigator` spec + reuse-core lists. No code, no seed rows in AICore, no user story (pure docs/process/tooling plan — story skip recorded here per user-story scope rules).

## Goals

- ✅ **G1:** `knowledge/symptoms.md` ships a durable, neutral symptom-class catalog — fixed S-01..S-07 classes, each with canonical diagnostic + fix routing, agnostic wording, no project-specific content.
- ✅ **G2:** `knowledge/problems.md` ships an empty seed-ready scaffold with schema `ID | Date | Team | Symptom (S-xx, primary first) | Domain | Problem | Evidence | Root cause | Fix applied | Status`.
- ✅ **G3:** `knowledge/agents.md` prior-art rule wires to the concrete artifacts (symptom-first diagnostic), adds the team-discriminated match criterion, and encodes the version-first and stop-and-ask hard rules.
- ✅ **G4:** Incident prior-art executors (`ticket-runbook` skill + `investigator` agent spec) match against `knowledge/symptoms.md` + `knowledge/problems.md` with the Team filter.
- ✅ **G5:** Reuse infrastructure (AGENTS.md reuse guide + migrate-core-to-project skill) lists and ships the two new knowledge files.

## Body

### Relationship model

- `symptoms.md` = taxonomy (fixed classes, never deleted); `problems.md` = known-problem register (child rows).
- Many-to-many: one class → many problems; one problem → comma-separated S-xx list, primary first (e.g. `S-05, S-07`). No junction table.
- Lookup filter: `Symptom (S-xx match) + Team + Domain`.
- Diagnostic flow: unexpected error → match signature to a class → canonical diagnostic → filter problems by S-xx + Team → prior occurrence → apply known fix; novel → file P-NNN under the class.

### Ownership

- `knowledge/symptoms.md`, `knowledge/agents.md`, and skills → Vault 🔐 (shared rules, incident-side governance, skills catalog).
- `knowledge/problems.md` → Scribe ✍️ (docs & problem management).
- `AGENTS.md` reuse guide → Cipher 🔓 (lead file).

### Neutral-core rule

- `symptoms.md` ships filled (durable, neutral). `problems.md` ships empty; destinations seed after copy. No personal-portfolio or tismart content may appear.

## Phase index — dispatch table

| # | Phase | Owner | Runbook | Output |
|---|---|---|---|---|
| 1 | Create symptom taxonomy | Vault 🔐 | `phase-01-vault.md` | `knowledge/symptoms.md` (new) |
| 2 | Create problems register scaffold | Scribe ✍️ | `phase-02-scribe.md` | `knowledge/problems.md` (new) |
| 3 | Wire prior-art rule + hard rules | Vault 🔐 | `phase-03-vault.md` | `knowledge/agents.md` (edited) |
| 4 | Wire ticket-runbook prior-art | Vault 🔐 | `phase-04-vault.md` | `.opencode/skills/ticket-runbook/SKILL.md` (edited) |
| 5 | Update migrate-core-to-project infra lists | Vault 🔐 | `phase-05-vault.md` | `.opencode/skills/migrate-core-to-project/SKILL.md` (edited) |
| 6 | Update AGENTS.md reuse guide | Cipher 🔓 | `phase-06-cipher.md` | `AGENTS.md` (edited) |
| 7 | Wire investigator prior-art scan | Vault 🔐 | `phase-07-vault.md` | `.opencode/agents/investigator.md` (edited) |

## Critical files / tools

- `knowledge/symptoms.md` (new), `knowledge/problems.md` (new)
- `knowledge/agents.md` (edit), `.opencode/skills/ticket-runbook/SKILL.md` (edit), `.opencode/skills/migrate-core-to-project/SKILL.md` (edit), `.opencode/agents/investigator.md` (edit), `AGENTS.md` (edit)
- Read-only references: `knowledge/debt.md` (empty-scaffold style precedent), plan-enforce templates

## Verification

- ✅ Phase 1 output artifact exists and is valid (7 class rows, no project-specific content)
- ✅ Phase 2 output artifact exists and is valid (empty scaffold, schema exact)
- ✅ Phase 3 gate passed (both files referenced; version-first + stop-and-ask present)
- ✅ Phase 4 gate passed (both files referenced with Team filter; no register write)
- ✅ Phase 5 gate passed (every Infra list names both files; count claims unchanged)
- ✅ Phase 6 gate passed (reuse guide names both files)
- ✅ Phase 7 gate passed (investigator prior-art scan wired with Team filter)
- ✅ All gates in each phase runbook passed

## Out of scope

- Seeding any problem records in AICore (destinations seed after copy), including the DEBT-001..004 fold-in
- Splitting into separate incident/dev catalogs (decided: one shared base)
- Editing any `.opencode/agents/*.md` spec or persona CV other than `investigator.md` (phase 7)
- Migrating anything into a destination project
- Any code, script, or test writes

## Pending

(none)

## Resolved decisions

- 2026-08-20 — one shared base for both teams, guarded by a mandatory Team discriminator on every problem record and in the match criterion (user: "the safer way to avoid errors").
- 2026-08-20 — many-to-many relationship: one class → many problems; one problem → comma-separated S-xx list, primary first. No junction table.
- 2026-08-20 — `problems.md` ships as an empty scaffold; no seeds in AICore (neutral-core rule).
- 2026-08-20 — version-first and stop-and-ask hard rules fold into the G3 wiring edit, not a separate goal.
- 2026-08-20 — prior-art item renamed "Problem catalog" → "Problem records" (the old term came from a business-docs folder in the source project and meant nothing concrete here; "ledger" collides with the Ledger subagent name). `knowledge/problems.md` backs the "Problem records" slot; the symptom catalog is a new pre-step on top, not a replacement of destination problem records.
- 2026-08-20 — G4 widened to cover the `investigator` agent spec in addition to `ticket-runbook` (the investigator is the prior-art executor per ticket-runbook's dispatch rule). Added phase 7.
- 2026-08-20 — register display term renamed "Problem records" → "Known-problem register" after double-check found "problem records" overloaded: it already names Scribe's destination-side ticket-system records (problem-records folder + problem-create/sync skills). The markdown register is now "known-problem register"; filename `knowledge/problems.md` unchanged; Scribe's ticket-system "problem records" untouched.
