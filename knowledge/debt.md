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
- Clearing a debt updates the record with the resolution.

## Register

### DEBT-001 — Plan-goal confirmation presentation

- **Date** — 2026-08-24
- **Description** — The plan-enforce goal-confirmation prompt rendered all metadata and goals as one dense, unscannable paragraph in the question UI.
- **Direct evidence** — User-provided screenshot and correction on 2026-08-24 show the confirmation text wrapping as a single block, obscuring individual goals and their acceptance conditions.
- **Resolution criteria** — Update the plan-enforce confirmation flow so goals are presented as a readable Markdown `G1`...`Gn` list before a short question-tool confirmation; keep plan type and user-story scope visually separate.
- **Explicit deferral decision** — User directed Cipher to record this presentation defect as debt on 2026-08-24; it is outside the approved git-convention alignment scope.
- **Resolution** — Cleared 2026-08-25. Plan-enforce v1.6.0 requires a separate Markdown `**Goals**` list and `**Plan classification**` block before one concise proceed/revise question. Validation: `python3 .opencode/skills/plan-enforce/scripts/validate_plan.py plans/plan-goal-confirmation-presentation-20260824` returned `ok`; `python3 .opencode/skills/plan-enforce/scripts/test_validate_plan.py` passed 21 tests. Vault 🔐 (Catalog Steward) returned PASS for the live contract on 2026-08-25.
