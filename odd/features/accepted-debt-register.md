# Accepted debt register

A single register in `.aicore/core/knowledge/debt.md` holds every accepted, non-blocking deferred work item with the evidence that justified deferral, the criteria for clearing it and the explicit deferral decision, so a deferred obligation stays visible instead of living only in a change record, a review summary or a report. The register holds open debts only; retired entries live in Git history.

**Status:** partial

## Requirements

- [x] R1 — Every open accepted debt carries an ID, a date, a description, direct evidence, resolution criteria and an explicit deferral decision.
- [ ] R2 — A resolved debt is cleared and retired within the same authorized, committed work unit, with its complete resolution evidence preserved at the durable owner that governs the delivered change.
- [x] R3 — An explicit user decision may cancel an open debt without satisfying its criteria; the decision, the unmet criteria and their supporting evidence are preserved in the governing change record before the entry is removed, and cancellation is never represented as resolution or clearance.
- [x] R4 — Identifiers follow this register's own recorded monotonic next-ID value, so a retired identifier is never reused and a gap is never refilled.
- [x] R5 — Every deferred work item carries a register entry linked to the finding, task or feature that produced it, stating why it was deferred, its impact and the condition for resolution.
