<!--
HARD RULE — fill every Step / Output / Gate / Abort. No `TBD` placeholders. Agent improvisation forbidden.
-->

# Phase 2 — Create problems register scaffold

> **Owner:** Scribe ✍️ (Docs & problem management)
> **Pre:** `knowledge/symptoms.md` exists (Phase 1 gate passed).
> **Reads:** `knowledge/symptoms.md` (class list for the Symptom column), `knowledge/debt.md` (empty-scaffold style precedent)
> **Writes:** `knowledge/problems.md` (new)

## Steps

1. Create `knowledge/problems.md`:
   - H1 `# Problem Records` plus intro: chronological, evidence-backed incident records; each row is a child instance of a symptom class in `knowledge/symptoms.md`; primary symptom class first when a row references several.
   - `## Entry format` — one row per record; columns exactly `ID | Date | Team | Symptom | Domain | Problem | Evidence | Root cause | Fix applied | Status`; glossary:
     - ID: P-NNN
     - Date: when faced
     - Team: `incident` | `dev` (mandatory discriminator)
     - Symptom: >=1 S-xx refs from `knowledge/symptoms.md`, comma-separated, primary first (e.g. `S-05, S-07`)
     - Domain: system / module / package / tool the problem belongs to
     - Problem: one-liner
     - Evidence: command output, log excerpt, or file:line
     - Root cause: the actual cause, not the symptom
     - Fix applied: what was done, or "pending"
     - Status: open | closed
   - `## Rules`: (1) every row MUST reference >=1 existing S-xx; (2) Team MUST be `incident` or `dev`; (3) evidence-backed only — no rows without cited evidence; (4) duplicates merge into the existing row, never re-filed; (5) this register is destination-seeded — ships empty.
   - `## Register` — table header `| ID | Date | Team | Symptom | Domain | Problem | Evidence | Root cause | Fix applied | Status |` with `(no entries yet)` below, matching the `knowledge/debt.md` scaffold style.

## Output

- **Artifact:** `knowledge/problems.md`
- **Schema / shape:** H1 + intro; `## Entry format` (columns + glossary); `## Rules`; `## Register` (empty header + `(no entries yet)`). Zero seed rows.

## Gate

- ⬜ `knowledge/problems.md` exists; `## Register` header present with `(no entries yet)` and no `| P-` rows.
- ⬜ Every Symptom rule references `knowledge/symptoms.md`; Team constrained to `incident`/`dev`.
- ⬜ No project-specific content: `grep -iE 'playwright|faker|tismart|belcorp|SDP|ubuntu|personal-portfolio' knowledge/problems.md` → no match.

## Abort conditions

- Halt if a seed incident from another project would be required to make the scaffold meaningful — it must ship empty.
- Halt if any column or rule diverges from the confirmed schema without Cipher approval.

## Tool whitelist / blacklist

- Whitelist: read tools; file write on `knowledge/problems.md`.
- Blacklist: edits to `knowledge/symptoms.md`, `knowledge/agents.md`, any skill, or `AGENTS.md` in this phase.
