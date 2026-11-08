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
- Clear and retire a resolved debt in the same authorized, committed work unit: delete its entry from this register and preserve complete resolution evidence in the governing feature record and its Log, backed by delivery evidence. Identify the debt, evidence that every resolution criterion is met, validation results, independent review results, and the delivering commit; the commit must carry the resolution evidence or its durable governing-record reference. If a PR exists, its body must also carry that evidence or reference; a PR is not required for retirement. Git history is the permanent record for retired entries; this register holds open debts only. Never open a dedicated PR whose sole purpose is pruning cleared entries — each debt is retired by exactly one authorized, committed resolution work unit.
- **User-directed cancellation.** An explicit user decision may cancel an open debt without satisfying its resolution criteria. Cancellation is not resolution or clearance. Before removing the entry, preserve the user decision, unmet criteria, and supporting evidence in the governing feature record; include the cancellation and its evidence in the authorized delivery. This route does not waive the resolution-evidence requirements for resolved debts.
- **ID allocation.** Each register owns an independent monotonic ID sequence; IDs are never shared across projects or registers. Allocate the next ID as the current high-water plus one, read from this register's own recorded next-ID value — never recomputed from the currently open entries, because retiring an entry erases the maximum and would reuse an issued ID. Gaps are valid history: never refill one, and never reuse a retired ID. If the register has no recorded next-ID, bootstrap it once from the highest identifier ever present in this register's verified history; when that history is unavailable, truncated, or renamed, stop and report the gap instead of guessing a starting value.

## Register
<!-- core:end -->

<!-- project:begin -->
**ID to use for the next new debt:** `DEBT-042`. This is an allocation counter, not an open debt.
<!-- project:end -->
