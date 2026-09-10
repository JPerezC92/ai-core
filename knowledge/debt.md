# Accepted Debt Register

Records of deferred technical or process debt that are **non-blocking** for release.

## Entry format

Each entry MUST include:

- **ID** — unique identifier (e.g. `DEBT-001`)
- **Date** — when the deferral decision was made
- **Description** — what is deferred
- **Direct evidence** — the evidence that justifies deferral
- **Resolution criteria** — what must be true for the debt to be cleared
- **Explicit deferral decision** — who decided, and when

## Rules

- An accepted debt is nonblocking only when its record here carries direct evidence, resolution criteria, and an explicit deferral decision (see Herald 📯 (Release Manager) spec).
- Disclose the ID and unresolved criteria in any operation report that touches it.
- Clear and retire a debt in the same PR: the PR that clears a debt deletes its entry from this register, and its body and commit carry the Resolution evidence (criteria met, validation and audit results). Git history is the permanent record for retired entries; this register holds open debts only. Never open a dedicated PR whose sole purpose is pruning cleared entries — each debt is retired by exactly one PR: its clearing PR.

## Register

### DEBT-002 — `migrate-core-to-project` manifest table exceeds the extraction threshold

- **ID** — DEBT-002
- **Date** — 2026-09-10
- **Description** — The `migrate-core-to-project` `SKILL.md` "Core manifest" lookup table is ~37 lines, above the ~30-line QC-27 extraction threshold; it could move to `references/` and be referenced from `SKILL.md`.
- **Direct evidence** — Vault 🔐 (Catalog Steward) release-gate audit (2026-09-10), finding F3: the table at `.opencode/skills/migrate-core-to-project/SKILL.md:155-191` is a static lookup above the threshold. Pre-existing: the query-verification/test-audit changeset added only two rows and introduced no part of this size.
- **Resolution criteria** — Move the manifest table to a `references/` file and have `SKILL.md` reference it, then pass a Vault 🔐 (Catalog Steward) re-audit; or record a Vault-accepted in-place exception with the rationale.
- **Explicit deferral decision** — Cipher 🔓 (Lead Orchestrator), 2026-09-10: deferred as out of scope for the query-verification and test-audit governance changeset.
