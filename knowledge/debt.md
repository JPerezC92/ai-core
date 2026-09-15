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

### DEBT-001 — Stale plan-enforce version citations

- **Date:** 2026-09-15
- **Description:** `plan-enforce` advanced from `1.11.1` to `1.12.0`, but current-state citations still name `1.11.1` in `user-stories/plan-enforce-executor-validation.md`, `user-stories/plan-enforce-story-acceptance-reconciliation.md`, `user-stories/incident-query-verification-pilot.md`, and `knowledge/query-verification-design.md`.
- **Direct evidence:** `grep -rn '1\.11\.1' --include=*.md .` includes those four files among its matches (it also matches `plans/**`, `output/**`, and this register), while the shipped skill frontmatter reads `1.12.0`; the four cited occurrences are current-state requirements, not historical changelog lines.
- **Resolution criteria:** every current-state citation names the shipped `plan-enforce` version; historical changelog and resolved-decision lines may retain the old version.
- **Explicit deferral decision:** Cipher 🔓 (Lead Orchestrator), 2026-09-15, during the PR #39 review — a citation-currency chore that is non-blocking for the audit-gate release.
