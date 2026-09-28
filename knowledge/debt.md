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

### DEBT-001 — PR test-evidence observed output is unstandardized

- **ID:** DEBT-001
- **Date:** 2026-09-27
- **Description:** `## Test evidence` Observed output has no human-readable contract. Agents paste full runner stdout (pytest `-q` progress dots, traces, dumps). The useful signal is the verdict line.
- **Direct evidence:** PR #44 Test evidence for pytest at `c89a6e6698a52948cfbf3f62c8eb41f04383482e` recorded `........................................................................ [ 97%]` / `.. [100%]` plus `74 passed in 0.11s`. User rejected the dots as unhelpful. `git-pr` SKILL.md Post-PR evidence contract requires `<literal observed output>` with no verdict-only rule. Inquisitor 🔎 (PR Reviewer) and Herald 📯 (Release Manager) persist that same shape.
- **Resolution criteria:** `git-pr`, Inquisitor 🔎 (PR Reviewer), and Herald 📯 (Release Manager) require Observed output to be the human-readable verdict only (for pytest: `N passed in Xs`). Progress bars, per-test dots, stack traces, and raw dumps are forbidden unless the user asks for them. Clearing PR UPDATES `user-stories/git-pr-drafting.md`; do not CREATE a new story. That PR deletes this entry.
- **Explicit deferral decision:** User, 2026-09-27 — strip the dots from PR #44 now; standardize the contract later. Non-blocking for #44 merge.
