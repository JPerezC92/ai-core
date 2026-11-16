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
- [x] R15 `upstream · local detail` — the Log is a brief journal of decisions, outcomes, verdicts and pointers rather than an execution diary: routine corrections stay brief, an entry reproduces no review transcript, investigation narrative, raw output dump or pull-request body, and a command, an inspected file, a delegation, a reviewer response, a repeated successful test or a routine progress update earns no entry of its own.
- [x] R16 `upstream · local detail` — there is no separate evidence artifact, directory, index or service: attestational detail lives in the durable source that already carries it, and evidence required for future verification or acceptance never rests only in a temporary artifact.
- [x] R17 `local` — a closed record is deleted once its status is exactly `closed` and at least seven complete calendar days have passed since its recorded closure date; no other condition makes a record eligible, no per-record approval is required, an unclosed, too-young, undated, malformed or unreadable record is never deleted, the durable feature files are never touched by the rule, and a record a durable surface still relies on as the sole home of required evidence is retained so the policy preserves required durable evidence rather than discarding it.
- [x] R18 `local` — a durable feature file is named for the capability it describes, the name survives a change of implementation, and a change updates an existing contract before creating a new one.
- [x] R19 `upstream · local detail` — the Log's entry identifiers ascend with `L1` first, and a deviation is reported rather than passing silently.
- [x] R20 `local` — a further correction review is dispatched only after every finding from the previous round is confirmed addressed on the candidate under review; an exception identifies the remaining findings, their formal disposition and the governing authorization, and a generic reason never bypasses an unresolved finding.
- [x] R21 `local` — every document-audit dispatch declares its audit mode and its in-scope set, and an edit-triggered audit is scoped to the changed paths unless a broader scope is required by a dependency, by applicable policy or by the explicit audit purpose, and that broader scope is named.
- [x] R22 `local` — specialist review is dispatched by distinct material risk inside that specialist's authority, never by edit frequency or checkpoint presence, and a change matching several risks yields one dispatch per distinct specialist responsibility rather than one per trigger label; every reviewer's contract, severity, approval and BLOCK obligation is unchanged.
- [x] R23 `local` — verified evidence is reused while its inputs and dependencies are unchanged, changed inputs are re-verified, an independent reviewer may still challenge any evidence, and reuse creates neither a tracker nor a per-edit evidence report.
- [x] R24 `local` — from the rule's effective date onward, a record whose tasks are all done is either closed with its closure evidence or active with its open closure prerequisite named in its Log; the check is prospective, so a historical record's status, Log and Specs are never rewritten to satisfy it, and independent acceptance is never fabricated nor a feature with missing evidence closed automatically.
- [x] R25 `upstream · local detail` — each requirement states one independently verifiable outcome, preserves the requirement-defining wording verbatim, names one action and one observable result in its acceptance, and carries no implementation narration and no requirement another entry already states.
