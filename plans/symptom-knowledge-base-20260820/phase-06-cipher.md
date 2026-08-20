<!--
HARD RULE — fill every Step / Output / Gate / Abort. No `TBD` placeholders. Agent improvisation forbidden.
-->

# Phase 6 — Update AGENTS.md reuse guide

> **Owner:** Cipher 🔓 (L2 Lead)
> **Pre:** Phase 5 gate passed.
> **Reads:** `AGENTS.md` (reuse guide section)
> **Writes:** `AGENTS.md` (edited)

## Steps

1. In `AGENTS.md`, reuse guide step 2 ("Keep the shared infrastructure the agents reference"), extend the list to name all four knowledge files:
   - `knowledge/agents.md` (shared rules) and `knowledge/debt.md` (accepted-debt register) → add `knowledge/symptoms.md` (symptom-class catalog) and `knowledge/problems.md` (problem records).
2. Confirm no other `AGENTS.md` section (roster, conventions, Cipher ownership) needs the new files.

## Output

- **Artifact:** `AGENTS.md` (edited)
- **Schema / shape:** reuse-guide step 2 names the four knowledge files including the two new ones; nothing else changed.

## Gate

- ⬜ `grep -c 'knowledge/symptoms.md' AGENTS.md` → >=1.
- ⬜ `grep -c 'knowledge/problems.md' AGENTS.md` → >=1.

## Abort conditions

- Halt if the edit touches roster, identity, or conventions content beyond the reuse-guide list.

## Tool whitelist / blacklist

- Whitelist: read tools; edit on `AGENTS.md`.
- Blacklist: edits to any other file in this phase.
