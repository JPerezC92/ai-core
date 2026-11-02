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
- **User-directed cancellation.** An explicit user decision may cancel an open debt without satisfying its resolution criteria. Cancellation is not resolution or clearance. Before removing the entry, preserve the user decision, unmet criteria, and supporting evidence in the governing feature record; include the cancellation and its evidence in the authorized delivery. This route does not alter the clearing-PR rule for resolved debts.
- **ID allocation.** Each register owns an independent monotonic ID sequence; IDs are never shared across projects or registers. Allocate the next ID as the current high-water plus one, read from this register's own recorded next-ID value — never recomputed from the currently open entries, because retiring an entry erases the maximum and would reuse an issued ID. Gaps are valid history: never refill one, and never reuse a retired ID. If the register has no recorded next-ID, bootstrap it once from the highest identifier ever present in this register's verified history; when that history is unavailable, truncated, or renamed, stop and report the gap instead of guessing a starting value.

## Register
<!-- core:end -->

<!-- project:begin -->
**Open debts: 3.**

### DEBT-022 — ODD step-status reporting and continuation

- **ID:** DEBT-022
- **Date:** 2026-10-29
- **Description:** After finishing an ODD step, Cipher 🔓 (Lead Orchestrator) did not send a status message identifying the step, its state, the evidence, and the next step, and did not continue to the next step. Work stopped or jumped to another task without stating which step was skipped and why, so the user had to ask repeatedly where the work stood.
- **Direct evidence:** Conversation record 2026-10-29; user instruction "add taht as a debt when u finish a step u should send a message of the status and continue"; `odd/tasks/domain-use-case-conventions.md` L1–L7; the step-status table delivered only after the user asked.
- **Resolution criteria:** Every completed ODD step produces a concise status message with the step number, state, evidence pointer, and next step; work continues to the next step unless a required gate or blocker stops it; any skipped step is named with its reason. Demonstrate this across the remaining steps of the active feature and the next non-small feature.
- **Explicit deferral decision:** User instruction 2026-10-29: "add taht as a debt when u finish a step u should send a message of the status and continue". The user accepted the process debt and directed continuation.

### DEBT-029 — Stop without a user-action requirement

- **ID:** DEBT-029
- **Date:** 2026-10-29
- **Description:** Cipher 🔓 (Lead Orchestrator) stopped without a user-action requirement and left informational text that named no decision or next step. The stop did not distinguish "all pending work is finished" from "work remains," so the user had to ask why the turn ended.
- **Direct evidence:** Conversation record 2026-10-29; user corrections "why u stopped now?", "stopo dodging, hey u should understand if u stop there should be a reason that require me to take an action, in other casu if u finalized all your pending why u dolnt senmt a clear message like ALL FINISHED, and next steps or ask about what to do next"; `AGENTS.md` project extension `### Stop and next-step reporting`; no code change.
- **Resolution criteria:** Every stop either names the exact user action required or says `ALL FINISHED`, lists the completed scope, and states the next steps; if work remains, continue to the next ready task; informational evidence alone is not a stop reason. Demonstrate on the current push/PR and future tasks.
- **Explicit deferral decision:** User instruction 2026-10-29: "add this error as a debt iun the workflow and then continue with the 5". The user accepted the process debt and directed the push/PR.

### DEBT-032 — Reviewer dispatched without prior coordinator self-verification

- **ID:** DEBT-032
- **Date:** 2026-10-31
- **Description:** On the same feature, Cipher 🔓 (Lead Orchestrator) dispatched the corpus auditor three times and re-gated an owner reviewer twice, each round verifying corrections that Cipher 🔓 (Lead Orchestrator) could and should have verified itself first. Findings raised by the audit were produced by Cipher's own bookkeeping — a `done` task without a commit reference, five specs missing acceptance clauses, a Log entry that merged a verbatim correction with its rationale, undated Log entries, a task ID in the `S#` column, an inaccurate line reference in a debt entry, and a delivery claim that predated the commits. Each round therefore measured the coordinator's proofreading rather than the reviewer's judgment, and the review loop went to its cap on a defect that a single self-check would have caught.
- **Direct evidence:** Conversation record 2026-10-31 including the user's correction "about sentinel stop just raising it without a double chek of the fixes i presume u were lefting issues and calling him again and again, verify for issues then when u are sure call him again"; Sentinel 🛡️ (Quality Guardian) audit rounds 1–3 for `odd/tasks/architecture-whole-file-distribution.md` (findings S1–S6, then the narrowed S2 plus missing acceptance clauses and merged Log entry, then F1–F2); Crucible 🔥 (Test Architect) rounds 1–2 (C1–C4, then C3/C4 verification). The failure recurred on the same day and is recorded here: a fourth audit round found five coordinator-authored defects, including that the project's own anatomy validator had not been run before the dispatch, which would have caught the bold spec/Log forms, the unlinked task spec, and the two-commit field in one pass.
- **Resolution criteria:** Before any owner-gate or audit dispatch, the coordinator runs its own mechanical verification of the candidate — document anatomy, acceptance-clause presence, Log separation and dating, evidence accuracy including file:line references, registry consistency, and the change's own observable predicates — and fixes what it finds. Reviewers are dispatched on a self-checked candidate, so their rounds judge substance rather than coordinator proofreading. Demonstrated on the next review dispatch of this feature and the next non-small feature.
- **Explicit deferral decision:** User instruction 2026-10-31: "about sentinel stop just raising it without a double chek of the fixes i presume u were lefting issues and calling him again and again, verify for issues then when u are sure call him again". The user accepted the process debt and directed self-verification before the next review dispatch.

**ID to use for the next new debt:** `DEBT-037`. This is an allocation counter, not an open debt.
<!-- project:end -->
