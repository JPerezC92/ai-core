<!-- core:begin -->
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
- **ID allocation.** Each register owns an independent monotonic ID sequence; IDs are never shared across projects or registers. Allocate the next ID as the current high-water plus one, read from this register's own recorded next-ID value — never recomputed from the currently open entries, because retiring an entry erases the maximum and would reuse an issued ID. Gaps are valid history: never refill one, and never reuse a retired ID. If the register has no recorded next-ID, bootstrap it once from the highest identifier ever present in this register's verified history; when that history is unavailable, truncated, or renamed, stop and report the gap instead of guessing a starting value.

## Register
<!-- core:end -->

<!-- project:begin -->
**Open debts: 1.** The DEBT-008/009/010 deletion made in clearing commit `5eed3317…` is recorded as **provisional**, not a settled retirement; see the standing-condition record in `user-stories/plan-lifecycle-governance.md`.

### DEBT-015

- **ID** — `DEBT-015`
- **Date** — 2026-10-23
- **Description** — Cipher 🔓 (Lead Orchestrator) recommended merging PR #81 before PR #80 based on stale session context that said PR #80 was still open, without first checking live PR states or comparing the feature branch with current `main`. This gave the user an incorrect merge order and delayed identifying that PR #80 had already merged and PR #81 needed reconciliation.
- **Direct evidence** — In the conversation on 2026-10-23, Cipher 🔓 (Lead Orchestrator) said “merge #81 first” and described PR #80 as still open. Herald's subsequent live `gh pr view` evidence showed PR #80 `MERGED` at commit `06e3aff022abf67084cfb0c9e02ace97912d7364`; live `main` was at that same commit. PR #81 remained `OPEN`, based on `3fda46693831a1fcce60a7eec6ad34bb28907341`; GitHub reported `mergeable=CONFLICTING` and `mergeStateStatus=DIRTY`. The compare endpoint reported PR #81 one commit behind live `main`; `.opencode/agents/inquisitor.md` was the overlapping path.
- **Resolution criteria** — Before giving merge-order or readiness advice, inspect live metadata for every involved PR (state, base, head, merge commit, and mergeability) and the current base-branch SHA; compare each PR head against that live base, identify overlapping paths, and disclose whether the advice relies on current state. An independent review of a later merge-order recommendation must confirm it matches the captured live metadata.
- **Explicit deferral decision** — 2026-10-23 — user directed “and add as a debt the error u maded”; Cipher 🔓 (Lead Orchestrator) records the stale-state recommendation as a nonblocking process debt. This record does not authorize merging PR #81 or bypassing its refresh, validation, or review gates.

**ID to use for the next new debt:** `DEBT-019`. This is an allocation counter, not an open debt.
<!-- project:end -->
