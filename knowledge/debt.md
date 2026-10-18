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
**Open debts: 2.**

### DEBT-007

- **ID** — `DEBT-007`
- **Date** — 2026-10-18
- **Description** — The forbidden-AI-attribution matcher's literal token set is not recorded in any repository-readable surface, so the exact-token attribution scan cannot be reproduced from the checkout; PR reviews fall back to a conventional attribution-token scan.
- **Direct evidence** — PR #70 review at head `b82cdcad04c51eb0b5c3eeae78f2db651b75f88c` (finding 1): the matcher's tokens are defined outside every readable repo surface (`inquisitor.md` keeps them external; `herald.md` carries policy prose only); the conventional scan over both commit subjects and full message bodies, the PR title and body, and all four changed-file bodies returned zero matches.
- **Resolution criteria** — The approved matcher's literal token set is recorded in a repository surface the reviewing role can read, and the exact-token scan runs and is documented at a PR head.
- **Explicit deferral decision** — 2026-10-18 — user directed "add them as debts"; deferred at the PR #70 review by Inquisitor 🔎 (PR Reviewer), adjudicated `defer-to-debt` by Cipher 🔓 (Lead Orchestrator).

### DEBT-008

- **ID** — `DEBT-008`
- **Date** — 2026-10-18
- **Description** — `user-stories/core-sync.md`'s 2026-10-18 revision entry states "AC24's promise, mark, and Proof unchanged" beside the documented form-only Proof correction (verdict date removed from the Proof line); the wording could distinguish value stability from the recorded form change.
- **Direct evidence** — PR #70 review at head `b82cdcad04c51eb0b5c3eeae78f2db651b75f88c` (finding 2): the form-only correction is documented in the adjacent entry; no criterion, promise, mark, or verdict value changed.
- **Resolution criteria** — The wording is aligned at the next `core-sync` story revision so the entry distinguishes promise/mark/verdict-value stability from the recorded form correction.
- **Explicit deferral decision** — 2026-10-18 — user directed "add them as debts"; deferred at the PR #70 review by Inquisitor 🔎 (PR Reviewer), adjudicated `defer-to-debt` by Cipher 🔓 (Lead Orchestrator).

**ID to use for the next new debt:** `DEBT-009`. This is an allocation counter, not an open debt.
<!-- project:end -->
