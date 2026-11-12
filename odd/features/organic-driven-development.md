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
- [ ] R11 `local` — evidence invalidated by a change is voided, never carried forward.
- [ ] R12 `local` — an independent reviewer's verdict is recorded per requirement before close.
- [x] R13 `local` — the feature validation passes before close.
- [x] R14 `upstream · narrowed` — closing the record is not delivery; push, PR and merge stay separately authorized.
- [x] R15 `upstream · local detail` — the Log is a brief journal of decisions, outcomes, verdicts and pointers rather than an execution diary: routine corrections stay brief, and a command, an inspected file, a delegation, a reviewer response, a repeated successful test or a routine progress update earns no entry of its own.
- [x] R16 `upstream · local detail` — there is no separate evidence artifact, directory, index or service: attestational detail lives in the durable source that already carries it, and evidence required for future verification or acceptance never rests only in a temporary artifact.
- [x] R17 `local` — a closed task record becomes eligible for retirement only after seven complete calendar days from its recorded closure date, and only when it is delivered, unreferenced by a durable surface, free of any open obligation, and already carrying its decisive content in a durable home; removal is user-authorized and never automatic.
- [x] R18 `local` — a durable feature file is named for the capability it describes, the name survives a change of implementation, and a change updates an existing contract before creating a new one.
- [x] R19 `upstream · local detail` — the Log's entry identifiers ascend with `L1` first, and a deviation is reported rather than passing silently.
