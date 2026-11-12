# Organic Driven Development

Organic Driven Development governs every request. Read-only and small work leave no artifact; non-small state-changing work is tracked in one change record that states what the feature must achieve.

**Status:** partial

## Requirements

- [x] R1 `upstream` — the work obeys the seven protocol steps: authorize, explore, resolve uncertainty, classify, track before the first write, implement task by task, close.
- [ ] R2 `local · conflicts` — a change in requirement or acceptance restarts the route at step 1. Divergence: the original rewrites only the affected spec and reopens only its task.
- [x] R3 `upstream` — every requirement states its exact wording.
- [x] R4 `upstream` — acceptance per requirement names one action and one observable result.
- [x] R5 `upstream · local detail` — every task names its requirement, route, owner and status.
- [x] R6 `upstream · local detail` — the check that ran is recorded, and a verdict alone does not substitute for it.
- [ ] R7 `local` — each piece of evidence is bound to the commit it ran against.
- [ ] R8 `upstream` — the failure that existed first is recorded, or the reason an executable failure cannot apply is stated.
- [x] R9 `upstream` — what was not verified is named.
- [x] R10 `local` — every requirement the change affects is accounted as met, restated or retired, and requirements the change did not affect are left alone.
- [x] R11 `local` — evidence invalidated by a change is voided, never carried forward: a reviewer re-invoked for a related change reuses reference material only while that material and its dependencies are unchanged, always produces a new verdict for changed inputs, and states the reused material, the re-read inputs and the content identity its verdict binds to.
- [ ] R12 `local` — an independent reviewer's verdict is recorded per requirement before close.
- [x] R13 `local` — the feature validation passes before close.
- [x] R14 `upstream · narrowed` — closing the record is not delivery; push, PR and merge stay separately authorized.
- [x] R15 `upstream · local detail` — the Log is a brief journal of decisions, outcomes, verdicts and pointers rather than an execution diary: routine corrections stay brief, and a command, an inspected file, a delegation, a reviewer response, a repeated successful test or a routine progress update earns no entry of its own.
- [x] R16 `upstream · local detail` — there is no separate evidence artifact, directory, index or service: attestational detail lives in the durable source that already carries it, and evidence required for future verification or acceptance never rests only in a temporary artifact.
- [x] R17 `local` — a closed task record becomes eligible for retirement only after seven complete calendar days from its recorded closure date, and only when it is delivered, unreferenced by a durable surface, free of any open obligation, and already carrying its decisive content in a durable home; removal is user-authorized and never automatic.
- [x] R18 `local` — a durable feature file is named for the capability it describes, the name survives a change of implementation, and a change updates an existing contract before creating a new one.
- [x] R19 `upstream · local detail` — the Log's entry identifiers ascend with `L1` first, and a deviation is reported rather than passing silently.
- [x] R20 `local` — a further correction review is dispatched only after every finding from the previous round is confirmed addressed on the candidate under review; an exception identifies the remaining findings, their formal disposition and the governing authorization, and a generic reason never bypasses an unresolved finding.
- [x] R21 `local` — every document-audit dispatch declares its audit mode and its in-scope set, and an edit-triggered audit is scoped to the changed paths unless a broader scope is required by a dependency, by applicable policy or by the explicit audit purpose, and that broader scope is named.
