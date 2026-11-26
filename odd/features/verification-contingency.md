# Verification contingency

A failed verification instrument does not decide whether work can proceed. This feature guarantees that a distributed check which cannot execute is reported as unavailable rather than as passed or failed, that an equivalent procedure establishing the same guarantee lets authorized work continue without waiting for an upstream correction, and that delivery readiness follows the guarantees rather than the instruments that were executed.

**Status:** not started

## Requirements

- [ ] R1 — Verification is reported as one of three distinct outcomes: satisfied, violated, or unavailable; an unavailable result establishes neither compliance nor breach, and it stays distinct from a check that has not yet been attempted.
- [ ] R2 — A required check that cannot execute is resolved by naming its cause, separating a tooling failure from a detected violation, naming the guarantee the check exists to establish, and using a permitted alternative that establishes it; when none exists, the affected operation is blocked on the missing guarantee and the report names that guarantee rather than the failed instrument.
- [ ] R3 — Naming a particular command, script, or tool prescribes the instrument without by itself making it non-substitutable; the contingency route is removed only by an explicit non-substitutability or by an instrument whose use is itself an essential security or contractual requirement.
- [ ] R4 — An alternative establishing the same guarantee to at least the same standard proceeds without additional user consultation; weaker verification, an unestablished part of the requirement, a changed contractual or security boundary, or a material residual risk needing acceptance uses the user-authority or authorized-exception mechanism that already governs that boundary, and no additional approval mechanism exists.
- [ ] R5 — The instrument's execution status is never confused with the guarantee's verification status: an unavailable instrument is never reported as passed because an alternative succeeded, and a detected violation is never reclassified as a tooling exception.
- [ ] R6 — Delivery readiness follows the guarantees that are established rather than the instruments that were executed, and each delivery retains its own verification evidence.
- [ ] R7 — A confirmed defect in a distributed file is disclosed with sufficient evidence to its owner, and no destination waits for acknowledgment, issue creation, correction, review, merge, release, or synchronization before completing otherwise-verifiable authorized work; a distributed file is never edited locally to route around the defect.
- [ ] R8 — A documented defect whose circumstances remain materially unchanged reuses its existing reference and its still-authorized alternative without a duplicate report or repeated authorization, and repeated use never becomes a permanent substitute for correcting the confirmed defect.
- [ ] R9 — Contingency reporting stays inside the existing change record, verification evidence, and release structures, naming the unavailable instrument and its failure, the verification objective, the alternative, the observed result, any remaining limitation, and the applicable authorization or defect reference, without a new form, artifact, or per-guarantee reporting for ordinary passing checks.
