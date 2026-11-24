---
name: odd-workflow
description: Create and maintain the single ODD feature document in odd/tasks/. Use when starting a feature, adding a spec or task, recording a decision, changing a requirement, or closing a feature.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 3.1.0
---

<!-- core:begin -->

## Mandatory core

### What I do

Create, read, update, and close the single authoritative feature document for a feature, and create or update the feature's durable file in `odd/features/` that states what the feature is and the requirements it must satisfy. Its subordinate full mirror follows `.aicore/core/knowledge/agent-workflow.md` → `### Full feature mirror and resume`; it is not a second tracker or a context-injection mechanism. The durable file derives its status from its own ticks; it is never a second task record. This skill owns record mechanics, not a duplicate mirror protocol.

### Create a feature document

- Copy `.aicore/core/odd/tasks/_template.md` to `odd/tasks/<YYYY-MM-DD>-<feature-name>.md`, using the document's creation date, which must equal its `Created:` header value; never reconstruct the format by research.
- Keep that creation-date prefix unchanged afterwards. Existing undated feature documents keep their names; `.aicore/core/odd/tasks/_template.md` stays undated. The date prefix provides chronological filename sorting without changing other folders' ordering.
- Fill the short header with `Status`, `Owner`, and `Created` and always show all four context fields: `Objective`, `Branch`, `Delivery`, and `Runner`. Fill each field with the actual value or `N/A — reason`; do not silently omit a field, and never invent a branch or runner. Existing closed feature documents are not retrofitted. `Delivery` carries the chosen strategy, authored-line forecast, and slice boundaries; `Runner` is the literal applicable command.
- Fill `## Specs` using the specification procedure below.
- Fill `## Tasks` with one line per task: stable ID, linked `S#`, route (`inline` or `delegated`) with the reason/trigger that decided it — responsible owner, status (`open`, `in progress`, `done`), and commit. Record the route and its trigger evidence, not the route label alone. Use `commit: pending` only while status is `open` or `in progress`; `done` requires a 7–64 character hexadecimal commit identifier. One authorized coherent work-unit commit may evidence several tasks; do not require one commit per task. Every task names the commit that actually carries its work, and a shared reference is valid only when that commit contains each task's own work. A high-risk unit must carry its own commit, so a high-risk change is never mixed with unrelated tasks and remains revertible and reviewable alone. A commit represents one deliverable behaviour, fix, migration or documentation outcome rather than a file type, and its message states the outcome rather than listing paths.
- Fill `## Log` with `L1` = the original request verbatim; record each later user correction as its own entry dated and quoted verbatim, and its evidence and rationale may accompany it in that entry.
- After bootstrap, apply the workflow's `### Full feature mirror and resume`. Keep verified project/feature identity, document locator, backend ID, exact verified content revision and comparison evidence, or explicit pending recovery, compactly in the existing Log. Respect project/task backend-write restrictions; record preparation does not itself establish runtime synchronization.

### Create or update the feature file

- Every non-small feature owns one durable file at `odd/features/<feature>.md`, named for the capability it describes and never dated, created from `.aicore/core/odd/features/_template.md`; the template is the only feature-file template and the format is never reconstructed by research. Create the file the first time the feature is worked, and read and update it on every later change.
- **Name it for the capability, not the change.** The file name states what the system provides, in the words a reader would use to find it. The name survives a change of implementation: if replacing the mechanism would leave the name wrong, the name describes the mechanism rather than the capability. A name that must change whenever the implementation changes describes a change record, not a contract.
- **Update before creating.** Before creating a durable file, read `odd/features/` and decide whether the capability already belongs to an existing file. When it does, update that file; a new file is created only for a genuinely distinct, enduring capability with its own observable rules. One change may affect several durable files, and each affected file records the requirements that change touched.
- The file is not a second tracker. The record in `odd/tasks/` stays the single authoritative intent, task and status record for one change; the file states what the feature is and lists the requirements it must satisfy. The file lists no change records and holds no work-in-progress state. A requirement states only what must remain true and appends no pointer to implementation or history: no file path, heading reference, line number, command, or record of when or how it was checked is added to it, and no change record, its Log, or a line in one is cited. Where a specific path, component or artifact is itself part of the required behavior, the requirement names it as the behavior it guarantees rather than as evidence that the behavior exists. The evidence that a requirement was checked belongs in the change record that affected it.
- The shape is fixed: a title for the feature, one paragraph saying what it is, one status line, and the requirement list, where each requirement is one `R#` line in the form `- [ ] R# — <what must be true for this feature to count as complete>`.
- The status line follows the ticks rather than an independent claim: every requirement ticked is `achieved`, some ticked is `partial`, none ticked is `not started`. The validator computes and reports that derived status.
- A tick asserts that the requirement currently holds. A change re-verifies only the requirements it affects: when verification confirms the requirement, the tick stands; when a regression is established, the tick is removed and the failure and its cause are recorded in the change's own record; when verification could not be completed and the change demonstrably could have affected the requirement, the tick is removed and the uncertainty and its reason are recorded in the change's own record. Only the change that delivers or re-verifies a requirement may set its tick.
- A requirement carries a mark only when the feature adopts a standard that already exists, recording where this repository departs from it: `upstream` unchanged, `upstream · local detail` sharpened here, `upstream · narrowed` relaxed here, `local` added here, `local · conflicts` contradicting the standard. A feature explicit from this repository carries no mark.
- Every change reads the affected durable file and records what it changed in it: which requirements it added, reworded or retired, and the verification outcome for each affected requirement. Requirements the change did not affect are left alone and are not re-verified.
- Validate the file with the skill's validator, pointed at the file or the directory that holds the feature's files: `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts <feature-file-or-directory>`. It reports the derived status. The script is **mechanical anatomy only**; exit 0 proves the shape, the requirement lines, the ticks, the placeholders and that every code fence closes explicitly. It does not prove that a requirement holds or that the feature is complete — the completion judgement in `### Close` owns that. The record's own validation stays in `### Validate`.
- The mark vocabulary and the filling rules live in the template's `## Guidance` section, and each requirement's upstream source and local owner live where that requirement cites them. This skill owns the mechanics, not that analysis.

### Write meaningful specifications

Derive numbered `S#` behavioral clauses, constraints and acceptance checks from the request, corrections and approved proposal. Each entry states the required observable behavior and how it will be checked.

Every entry carries four parts: the `S#` identifier; an observable behavior or constraint statement; the requirement-defining wording preserved verbatim; and an acceptance clause. This shape illustrates one entry:

- `S# — <observable behavior or constraint statement>. Exact requirement: <requirement-defining wording, verbatim>. Acceptance: <one action> and <one observable result>.`

Those labels are illustrative, not required syntax: the mechanical validator accepts any `- S# — …` entry, so the shape proves anatomy only, never meaning.

One `S#` per independently verifiable outcome. Split when no single check covers all parts — a request that reports a defect, adds a capability and constrains a platform is three entries, because each part needs its own check.

An entry states what must remain true, not how it was implemented: it carries no file path, command, commit or architecture narration, except where the path, component or artifact is itself the required behaviour, which is then named as the behaviour it guarantees rather than as evidence that the behaviour exists. A requirement is stated once; an entry that repeats a requirement another entry already states is deleted rather than retained beside it.

A symptom report is not yet a requirement: state the behavior you are committing to, and keep the symptom verbatim. The quoted report says what was observed; the entry says what becomes true and how it is checked.

Acceptance names one action and one observable result. `Works correctly` is not acceptable: it names neither.

Preserve the user's exact requirements, strings, errors, commands and examples verbatim alongside that meaning; do not paraphrase or normalize requirement-defining wording, replace it with a summary, or add unrequested scope. Record genuine uncertainty as evidence or a focused question, never an unsupported assumption.

Separate requirements from conversation: directions to analyze and words of approval are authorization/history in `## Log`, not feature capabilities. For a mixed requirement/approval message, retain the exact requirement in Specs with its behavioral clause and check, and preserve the full message and approval context in Log. Do not discard a requirement merely because the same message approves work.

Illustrative authoring examples only, not execution evidence. This invented multi-part request reports a symptom, asks for a capability, adds a constraint and approves work:

- `Checkout shows "Something broke" instead of the receipt when a card is declined. Also let me export the receipt as PDF from the order page, and it must work on Firefox. approved`

Correct — one entry per independently verifiable outcome:

- `S1 — A declined card shows the requested error text. Exact requirement: Checkout shows "Something broke" instead of the receipt when a card is declined. Acceptance: submit a declined card and read the checkout result; the displayed text is exactly "Something broke".`
- `S2 — The order page exports a receipt as PDF. Exact requirement: let me export the receipt as PDF from the order page. Acceptance: open an order page and trigger the PDF export; one PDF receipt file downloads.`
- `S3 — Receipt PDF export works on Firefox. Exact requirement: it must work on Firefox. Acceptance: run the S2 export in Firefox; the same PDF receipt downloads.`

Bad: `S1 — approved` or `S2 — ok analyze how to achieve it please`. These are conversation-only entries, rejected because they state no observable behavior and carry no check, even if anatomy validation passes.

Mixed message: the request above ends with `approved`. Its requirements live in S1–S3; the complete message and approval context go in Log. The approval neither removes a requirement nor becomes one.

Whether an entry is meaningful is owned by the completion judgement in `### Close`, not by the validator.

### Delivery forecast

Forecast authored additions plus deletions, excluding generated files, and record the chosen delivery strategy and slice boundaries compactly in the existing document. Maintain a running count from work-unit commits; when the forecast OR the running count exceeds about 400 authored changed lines, apply the chosen strategy before the next commit. Keep the ~400-line task size advisory — not a hard cap, classification input, automatic review trigger, or delivery-slice boundary — separate from that feature-level strategy trigger, and add no second tracker.

The budget is a review signal, never a reason to shrink evidence: never delete or compress tests, documentation, comments or blank lines to fit it. Slice by work unit instead, or report the overage. A feature of roughly 100 authored changed lines or fewer stays inline as one unit; splitting it manufactures commits without creating an independent review boundary.

Every planned work unit records its rollback boundary — the exact files and behaviour revertible without unwinding unrelated work — together with the unit's own focused check and its observed result.

### Before the first write

Apply `.aicore/core/knowledge/agent-workflow.md` `### ODD protocol`, including its every-task uncertainty and observable-outcome controls. Do not restate that protocol here. That protocol's `#### Step reporting and transitions` owns step reporting, the state/evidence/next-action fields, and scope-bounded continuation. Execution review after creation or material replanning follows `AGENTS.md` → Conventions → Decision-only stops; check current authority and prerequisites, not an automatic document-creation approval pause.

### Change a requirement

Read and apply `.aicore/core/knowledge/agent-workflow.md` `### Scope changes and readiness` before resuming affected work. In the feature record, rewrite only the affected spec and reopen only its task; do not append a new promise over a contradictory old one. Use the specification procedure above for changed requirements. Scope reassessment, stale-evidence handling and the artifact-free route remain defined by that workflow owner, not by this record procedure.

### Implement and verify

Read and apply `.aicore/core/knowledge/agent-workflow.md` `### ODD protocol`, step 6, for dependency order, task acceptance checks, tests/documentation, conditional RED/GREEN/refactor, actual exceptions and the runner obligations; apply `##### Behavioral verification and runner selection` in that same file for the per-spec and command-regression evidence. Carry the actual applicable runner and evidence with the work. Step reports and continuation follow the workflow's `#### Step reporting and transitions`.

A work unit ships the tests and documentation it needs. A unit that changes behaviour carries or updates the tests that verify it; a unit that changes a user-visible rule carries the documentation that explains it. Never defer that material to a later unit to keep a diff small.

For findings exposing related impact, read and apply the workflow's `#### Finding-triggered impact reassessment`. Record the trace through the existing Log and the durable source that carries its detail, not a separate tracker. This pointer grants no additional read or write scope.

After material record changes, work-unit commits, resume and closure, apply the workflow's `### Full feature mirror and resume`; retain the exact verified record revision or pending recovery in the existing Log, never a separate status tracker or a claim based only on a summary.

Delivered coverage traces to the governing `S#` entries at the boundary the testing contract assigns, and the record states that trace. A historical example becomes a requirement only when a governing specification or an accepted user decision states it as one; no coverage obligation arises from a count, and no one-to-one requirement-to-test mapping is required.

For feature work, the `## Log` records the outcome, the verdict, and a pointer that identifies where the evidence lives: the task/spec, the result, and the identity of the artifact that carries the detail — a commit, a path, or a pull request. The provenance detail — the literal command with its invocation and arguments, the tested input or commit identity, the dependency and environment identities, the responsible executor, and the expected versus observed result — lives in the durable source that already carries it: the committed diff, the test, a committed artifact, the pull-request body, or the record itself.

Evidence required for future verification or acceptance must remain in a durable source; a gitignored `output/` artifact may hold reproducible detail only.
If no executable check applies, record the actual static/manual verification or justified N/A; never invent a test. This is evidence, not an execution transcript, new heading, or second tracker. Read-only and small work do not acquire a mandatory feature document.

For instruction changes, identify original and candidate inputs and preserve complete retained/translated/retired accounting of valid original obligations with authority and rationale before acceptance; the accounting decision and its outcome stay in the existing Log, its itemized detail stays in a durable source — the committed artifact, the pull-request body, or the record itself, and acceptance still requires the complete accounting to exist. For prose and examples, walk through applicable normal and adverse scenarios against their governing rules; record the manual action, inputs, expected outcome and observed outcome there. Literal execution provenance and separate observable-outcome evidence remain required; planned checks or an author's confidence are not results.

### Log evidence

The `## Log` is a brief logbook, not an execution diary. `L1` holds the original request verbatim; each later user correction is its own dated entry, quoted verbatim, and its evidence and rationale may accompany it in that entry. The rationale for a meaningful accepted change, the observed outcomes, the progress and the next step are appended as the work proceeds. Routine corrections stay brief: there is no exhaustive decision journal, and a command, an inspected file, a delegation, a reviewer response, a repeated successful test or a routine progress update earns no entry of its own.

A Log entry carries the outcome, the verdict and a pointer identifying the durable source that holds the detail: a commit id, a path, or a pull-request number and head. It does not reproduce an enumerated review finding list, an investigation narrative, a raw command-output dump, or a copy of a pull-request body — those live in the durable source that already carries them — and the entry keeps one line naming what happened, the result, and where the detail lives.

Evidence for a feature falls into three classes. **Decisive** — requests, corrections, approvals and their labels, decisions, obligations, acceptance limits and commits — is permanent. It lives in the record while the record is live, and it must reach a durable owner — a durable feature file, an architecture decision record, the debt register, or the owning instruction file — before the record may be retired under `### Retire a task record`.
**Reproducible** — content a reader can regenerate or re-read from Git, a committed artifact or a gitignored `output/` artifact — is referenced by pointer only. **Attestational** — obligation accounting, verification verdicts and identities, input and candidate identities, literal commands with observed results, and preservation mappings — lives in the durable source that already carries it: the committed diff, the test, a committed artifact, the pull-request body, or the record itself.
A gitignored `output/` artifact may hold reproducible detail only; it never becomes the sole home of evidence required for future verification or acceptance. Record the provenance in the Log only when no durable source carries it.

There is no separate evidence artifact, directory, index or service. The record's `## Log` carries the decision, the outcome, the verdict and the pointer; the durable source carries the provenance. Never move, summarize, reformat or retype an entry that no available tool can read completely: keep it byte-identical in place, flag it, and state what a complete read requires.

When a finding-triggered trace is retained, identify the finding and available baseline, implementation and remediation candidates; retain inspected/changed evidence and coverage limitations, with defect origin separate from escape point and `unknown` valid where evidence is missing. Keep the validated conclusions in the existing Log; the supporting detail stays in the durable source that carries it. Before disposing of supporting detail, retain decisive classifications, limitations and lessons in the Log. Small/read-only work keeps its trace in the existing conversation, diff or report without a mandatory feature artifact.

**Close-time reconciliation** is part of closure. Before `Status: closed`, every decisive conclusion the change produced is either in the record or in the durable owner it belongs to, and the record names where it went. Git history is the recovery archive for what a committed artifact already carried.

### Close

Before completion, verify the delivered work against the record's own `S#` requirements at the commit that carries it, not against an uncommitted working tree. Compare the actual original request and corrections, Specs, delivered content, obligation accounting and evidence; account for every valid original obligation as retained, translated, or explicitly retired with authority and rationale. Check unresolved requirements, durable evidence at its proper owner (not essential evidence available only in temporary output), shared/local ownership, source neutrality, and precise execution provenance. A green suite or a validator pass is an input, never completion.

**An independent review is optional and is never an acceptance prerequisite.** The user may request one, and a declared high-risk item may justify recommending one. When a review runs, its findings are disposed under `.aicore/core/knowledge/agents.md` `### Finding disposition` and its verdict, if any, is recorded in the Log with the candidate it judged. When no review was requested, the record states that plainly: no verdict, acceptance statement or reviewer identity is invented, and the absence of a reviewer is not an open finding, not a pending check, and never a reason to keep an otherwise complete record open.

Require zero open findings before a **clean** feature completion claim. A **user-accepted residual risk** is the single exception, and it is never a clean completion: when a finding is left unfixed and the user has explicitly accepted it as residual risk, the record may close only with the finding, its risk, its disposition and the deciding authority preserved verbatim in the Log, a `> **Residual risks:**` header line naming the accepted findings, and an explicit statement that completion carries accepted residual risks rather than clean completion. A blocking finding is never closed this way, a deferred or unaccepted finding remains open, and an accepted advisory is never relabelled `[PASS]` or `FIXED`.

Relevant changes invalidate the evidence that covered them: re-run the affected checks and record the new result. This uses the existing gates and the single feature record — no duplicate tracker, harness or additional pause.

Read and apply `.aicore/core/knowledge/agent-workflow.md` `### ODD protocol`, step 7, for separate observable-outcome verification, failure reproduction and honest reporting of missing evidence/pending controls before task completion. Reporting and scope-bounded continuation follow its `#### Step reporting and transitions` and `.aicore/core/knowledge/agents.md` `### Message presentation`. On close, every task is `done` and has a commit reference. Set `Status: closed`, add `> **Closed:** date`, and record a final `L# — Close:` entry.

**Closure disposition.** A record closed on or after `2026-11-24` states what became of the work in a `> **Disposition:**` field, and the value never overstates it. `completed` is the only disposition that claims delivery, and it keeps every requirement above unchanged — the verified outcome, every task `done` against the commit that carries its work, and the closure evidence. `cancelled` requires an explicit user authorization for the cancellation recorded in the Log; it preserves the historical implementation evidence and the completed task rows, and it never implies that the remaining requirements were completed or accepted. `superseded` requires a `> **Superseded-by:**` field naming the delivery that replaced this work, or an evidenced statement of why the original requirements are obsolete, and it never conceals an unresolved requirement or technical defect. A record closed before that date keeps its existing shape and is not retro-fitted. A closed record whose recorded closure date cannot be read as a calendar date is treated as in scope, so a malformed date never lets a record escape the field.

**Closure consistency.** The stages and each stage's precondition are stated in `### Completion stages`. A record whose task rows are all `done` is either closed with its closure evidence — the verified outcome and the delivery evidence it asserts — or active with the open closure prerequisite named in its Log by an entry that begins `Blocked:`. Completion is never fabricated and a feature with missing evidence is never closed automatically: the missing evidence is named, not assumed. The validator detects this only for records created on or after the rule's effective date, so a historical record's status, Log and Specs are left exactly as written rather than rewritten to satisfy a later convention.

**Closure evidence the validator observes.** For a record created on or after the closure-evidence effective date `2026-11-19`, a closed record's `## Log` must state **the first failure, or the reason none applies**, and the existing validator checks only that: the Log states the failure that existed first in a form containing `first failure`, `first failing` or `first failed`; or it states, in one of these phrasings, why an executable failure cannot apply: `no applicable executable failure`, `executable failure cannot apply`, or `no executable failure applies`.

The per-requirement reviewer-verdict entry and the commit-binding of those entries were retired with the multi-agent acceptance model. A record is no longer closed by a second agent's verdict, so requiring one would be an obligation with no owner; the validator no longer checks for it, and a record that carries no reviewer verdict is valid. The first-failure rule survives because it is an evidence-honesty obligation about the delivered work, not about a reviewer.

A `Blocked:` entry — the open-closure-prerequisite entry a completed-but-active record requires — reports a prerequisite, not an accepted result.

These checks observe documentary structure only: they prove that the shape exists, never that the evidence is true. Records created before `2026-11-19` keep their existing status, Log and Specs and are never re-validated against these rules.

### Retire a task record

A closed task record is deleted once it is eligible. Retirement is part of the normal authorized Git workflow: it is never a background service and never an agent's own initiative, and it requires no per-record approval.

**When it runs.** Run the check in the closure work unit: before the closure commit is made and before any pull request is published. Deletions then ride the same delivery as the change that closes the work, already-accepted delivery evidence is never modified afterwards, and an authorized local-only delivery retires eligible records exactly as a released one does.

**Eligibility — three stages, and the first one that fails excludes the record.** A record is retired only when (1) it passes the feature validation its own contract states, because a record whose structure is not trustworthy must not be deleted evidence; (2) it carries genuine, unambiguous closure metadata, meaning status and closure date read only from column-zero header lines in the header region, outside fenced blocks; and (3) at least seven complete calendar days have passed since that closure date. The closure date field is the only age source; no timestamp is recorded and none is required. A record that fails validation stays ineligible until its defects are corrected, and the report names the validation failure as its exclusion reason.

**Never deleted.** A record that does not pass feature validation; a record whose status is not `closed`; a record younger than seven complete calendar days; a record with no recorded closure date or with a closure date that is not a real calendar date; a record whose closure metadata is ambiguous, meaning more than one status line or more than one distinct closure date; a record whose code fence never closes, because its structure cannot be trusted; and a record that cannot be read.

**Running the check.** `node .agents/skills/odd-workflow/scripts/retirement_check.ts odd/tasks`, optionally with `--as-of YYYY-MM-DD` for a deterministic report. It is a read-only report: it names every eligible record and the reason each excluded record is excluded, and it deletes nothing.

**Executing the deletion.** The deletion is performed by Herald 📯 (Release Manager) in the authorized Git workflow, and the durable feature files under `odd/features/` are the authoritative specifications, which this rule never touches. The user authorizes the retention policy itself, so a record the check reports as eligible is deleted without a separate per-record approval; a deletion outside this policy is not authorized. Before deleting, confirm that no durable surface depends on a record as the sole home of evidence it requires; a record a durable surface still cites as that evidence is retained and reported, because the retention policy preserves required durable evidence rather than discarding it.

This rule introduces no daemon, scheduler, additional agent, retention database or tracking system: it is one command in the existing skill and the ordinary Git workflow.

**Open closure prerequisite.** A record whose task rows are all `done` but which is not closed names its open closure prerequisite in a Log entry that begins `Blocked:` (see `### Close`). Its status is `active`, so it is not eligible for deletion.

### Handoff

Pass a reference to the feature document and its `S#`, never a paraphrase. Whoever performs the work reads until `## Log` and reports which specs it covered.

Delegating a slice is a choice justified by a named reason — a bounded exploration the coordinator needs in order to decide, independent parallel work on disjoint surfaces, a long-session context limit, or a fresh context for a requested review. It is never a requirement, and the agent that performs the work owns its checks and evidence.

For a **requested independent review**, apply `.aicore/core/knowledge/agent-workflow.md` → `### Behavioral verification and runner selection`: point the reviewer at the whole feature including Log, the exact candidate identity, its authorized examples and the observed evidence, together with the applicable review skill (`code-review`, `dependency-review`, or `visual-review`). Retain the returned findings and their dispositions in the existing Log. This neither creates an acceptance gate nor grants execution authority.

### Feature scope

The feature's `Specs` and `Tasks` bound its requirements and work; they do not reserve an exclusive set of files. A feature may touch a shared rule or file when its canonical owner and authority are clear. Record relevant dependencies in the feature record; never invent a file-level isolation rule. When work is genuinely concurrent, one active writer owns a canonical mutable resource at a time.

### Delivery boundary

Closing the feature document is not delivery. Explicit authorization may be supplied per action or through an applicable standing instruction; local commits are standing-authorized only when the project says so. Push, PR, merge, tag, release, and archive remain separately authorized, and a tool-permission denial is never bypassed. A PR is a reviewable slice — work-unit commits or the feature's task slice — never the accumulated branch and never a substitute for the feature document. Git execution remains with Herald 📯 (Release Manager); merge remains user-only.

### Completion stages

A change reaches completion in stages. Each stage has its own precondition; their ordering dependencies are stated below.

1. **Work units planned** — the delivery forecast records the strategy, each unit's slice boundary, rollback boundary and focused check, and which tasks share which unit.
2. **Implementation delivered** — the authorized work is committed in work-unit commits, every affected task row is `done` and carries the commit that actually carries its work, and each unit ships its own tests and documentation.
3. **Verification complete** — the applicable automated checks have run against the delivered content and are recorded with their result. These are inputs to completion, never a substitute for it.
4. **Optional independent review** — only when the user requested one, or accepted a recommendation. Its findings are disposed and recorded; its absence changes nothing in the stages below and is never a missing prerequisite.
5. **Record closed** — `Status: closed`, the `> **Closed:**` date, the final `L# — Close:` entry and the closure evidence are set.
6. **Closure committed** — Herald 📯 (Release Manager) commits the closure edit on the feature branch, together with the retention deletions this stage performs per `### Retire a task record`, after that section's dependency safeguard has been applied to every candidate. **Pull-request management may not begin before this stage is satisfied.**
7. **Pull request published** — Herald 📯 (Release Manager) has published exactly the authorized pull request against its base, and its head is fixed.
8. **Delivery evidence recorded** — the PR body carries the test evidence, findings, open debt and the readiness statement, with every required item verified. Readiness is reported only when that holds; an unchecked required item or an open `BLOCK` finding withholds it.
9. **Pull request merged** — the merge is the user's decision alone and stays separately authorized; no agent merges.
10. **Post-merge cleanup** — the merged-branch cleanup runs only after a proven merge.

**Ordering.** Stages 1 to 6 complete the whole ODD lifecycle, and stage 7 cannot begin until stage 6 is satisfied: an active record, an unfinished task row, a `commit: pending` reference or a closure that exists only as an uncommitted edit blocks pull-request management rather than merely blocking a readiness announcement. There is no post-publication closure stage. Closure and the merge stay independent of each other — closure requires no merge evidence, and a merge requires no closure — so a merged pull request does not close its record and a closed record does not merge it. Stage 10 follows a proven merge. A closed record becomes eligible for retirement under `### Retire a task record`, which depends on the record's own closure date and not on a merge. This rule governs records closed after it; a record closed earlier keeps its closure, and a closure obligation `### Close` already required but that was not recorded is completed, not rewritten.

**Commit references.** A `done` task row names a commit that carries the work: the commit exists in this repository and its content is the work that task delivered. Several tasks may name one work-unit commit, and that reference is accurate only when the commit contains each named task's own work. A high-risk unit carries its own commit. A pull request's own work-unit commits remain valid references after the merge, whether or not the merge was a squash; when a squash commit is the carrier on the base branch, the delivery narrative names it as well. The record's own closure edit is delivered by the commit that carries it, because a task row's commit reference cannot name the commit that carries that row. Never create a commit solely to manufacture a reference.

**Reopening after publication.** If a review of the published pull request, a user report or a failed check identifies a defect that requires implementation work, the record is reopened and the closure repeated. This is an exceptional remediation path, not the normal lifecycle, and it is bounded:

- Only a finding recorded at the current pull-request head authorizes reopening, and the reopening entry names that finding.
- New work is limited to that finding's remediation and its own tests and documentation; the reopening entry states its work unit and rollback boundary.
- Any work not traceable to that finding needs fresh user authorization; reopening itself authorizes nothing beyond the finding.
- The existing pull request stays the only review vehicle: no replacement pull request, no reset review history, no renumbering of findings.
- Reopening sets `Status: active` and removes the `Close:` entry, which an active record may not carry; task rows revert to `in progress` only where their work actually changed.
- Stages 2 to 6 repeat in full, including the closure commit, before the pull request may return to ready.

**Reporting.** A delivery is complete only when stage 6 is satisfied and ready only when stage 8 is satisfied. The report that distinguishes a published-but-not-ready pull request, a ready one, and a finished delivery follows `.aicore/core/knowledge/agents.md` → `### Message presentation`.

### Release readiness and findings

Apply `.aicore/core/knowledge/release.md` before opening any PR and after every review round. Do not restate that workflow here. Feature `### Delivery boundary` authorization remains separately required.

### Validate

The validator runs natively on Node.js `>=24.12.0` with no runtime dependency, no build step and no bundle; a destination runs it as it stands, with nothing installed.

Run `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks` before closing. The script is **mechanical anatomy only**; exit 0 proves the headings, `S#`/`T#`/`L1`, the Log's `L#` identifiers ascend with `L1` first, task status, 7-64 character hexadecimal commit references, placeholders, the closure-consistency precondition, and — for a record created on or after `2026-11-19` — the first-failure evidence stated in `### Close`. A present but unreadable `Created` date fails closed. It also proves the record's fenced structure: every code fence closes explicitly, a fence that only ends because its containing block ended still counts as unclosed, and every rule that reads the record — its title and header metadata, its Specs, Tasks and Log entries, its Log-identifier ordering, its Close entry, its user-cancellation authorization, its superseded-record obsolescence explanation, its placeholders and its retirement eligibility — reads only text outside fenced blocks, so fenced content can neither satisfy an obligation nor trigger a diagnostic. It does not prove verbatim fidelity, that a spec is meaningful, that a runner applies or ran, that a task is complete, or that the evidence is true — the completion judgement in `### Close` owns that.

Alongside the two validators, the retirement check `node .agents/skills/odd-workflow/scripts/retirement_check.ts <tasks-directory>` is a read-only report: it lists the records that satisfy the routine eligibility gate and the reason each excluded record is excluded, and it deletes nothing.

### References

- `.aicore/core/odd/tasks/_template.md` — the only feature-document template.
- `.aicore/core/odd/features/_template.md` — the only durable-feature-file template.
- `.agents/skills/odd-workflow/references/_checklist.md` — creation and close checks; read it in full before creating or closing a feature.
- `.agents/skills/odd-workflow/scripts/validate_feature.ts` — mechanical validator.
- `.agents/skills/odd-workflow/scripts/validate_feature_file.ts` — mechanical validator for the durable feature file; it reports the derived status.
- `.agents/skills/odd-workflow/scripts/retirement_check.ts` — read-only retirement report; it computes the routine eligibility gate and deletes nothing.
<!-- core:end -->
