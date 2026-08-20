# Known-problem Register

Chronological, evidence-backed incident records. Each row is a child instance of a symptom class in `knowledge/symptoms.md`; when a row references several classes, the primary symptom class comes first.

## Entry format

One row per record; columns exactly `ID | Date | Team | Symptom | Domain | Problem | Evidence | Root cause | Fix applied | Status`:

- **ID** — P-NNN
- **Date** — when faced
- **Team** — `incident` | `dev` (mandatory discriminator)
- **Symptom** — >=1 S-xx refs from `knowledge/symptoms.md`, comma-separated, primary first (e.g. `S-05, S-07`)
- **Domain** — system / module / package / tool the problem belongs to
- **Problem** — one-liner
- **Evidence** — command output, log excerpt, or file:line
- **Root cause** — the actual cause, not the symptom
- **Fix applied** — what was done, or "pending"
- **Status** — open | closed

## Rules

- Every row MUST reference >=1 existing S-xx from `knowledge/symptoms.md`.
- Team MUST be `incident` or `dev`.
- Evidence-backed only — no rows without cited evidence.
- Duplicates merge into the existing row, never re-filed.
- This register is destination-seeded — ships empty.

## Register

| ID | Date | Team | Symptom | Domain | Problem | Evidence | Root cause | Fix applied | Status |
|---|---|---|---|---|---|---|---|---|---|

(no entries yet)
