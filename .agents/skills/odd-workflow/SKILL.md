---
name: odd-workflow
description: Create and maintain the single ODD feature document in odd/tasks/. Use when starting a feature, adding a spec or task, recording a decision, changing a requirement, or closing a feature.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 2.5.0
---
<!-- core:begin -->

## Mandatory core

### What I do

Create, read, update, and close the single authoritative feature document for a feature, and create or update the feature's durable file in `odd/features/` that states what the feature is and the requirements it must satisfy. Its subordinate full mirror follows `knowledge/agent-workflow.md` → `### Full feature mirror and resume`; it is not a second tracker or a context-injection mechanism. The durable file derives its status from its own ticks; it is never a second task record. This skill owns record mechanics, not a duplicate mirror protocol.

### Create a feature document

- Copy `odd/tasks/_template.md` to `odd/tasks/<YYYY-MM-DD>-<feature-name>.md`, using the document's creation date, which must equal its `Created:` header value; never reconstruct the format by research.
- Keep that creation-date prefix unchanged afterwards. Existing undated feature documents keep their names; `odd/tasks/_template.md` stays undated. The date prefix provides chronological filename sorting without changing other folders' ordering.
- Fill the short header with `Status`, `Owner`, and `Created` and always show all four context fields: `Objective`, `Branch`, `Delivery`, and `Runner`. Fill each field with the actual value or `N/A — reason`; do not silently omit a field, and never invent a branch or runner. Existing closed feature documents are not retrofitted. `Delivery` carries the chosen strategy, authored-line forecast, and slice boundaries; `Runner` is the literal applicable command.
- Fill `## Specs` using the specification procedure below.
- Fill `## Tasks` with one line per task: stable ID, linked `S#`, route (`inline` or `delegated`) with the reason/trigger that decided it — responsible owner, status (`open`, `in progress`, `done`), and commit. Record the route and its trigger evidence, not the route label alone. Use `commit: pending` only while status is `open` or `in progress`; `done` requires a 7–64 character hexadecimal commit identifier. One authorized coherent work-unit commit may evidence several tasks; do not require one commit per task. High-risk units may use separate reviewable commits.
- Fill `## Log` with `L1` = the original request verbatim; record each later user correction as its own entry dated and quoted verbatim, and its evidence and rationale may accompany it in that entry.
- After bootstrap, apply the workflow's `### Full feature mirror and resume`. Keep verified project/feature identity, document locator, backend ID, exact verified content revision and comparison evidence, or explicit pending recovery, compactly in the existing Log. Respect project/task backend-write restrictions; record preparation does not itself establish runtime synchronization.

### Create or update the feature file

- Every non-small feature owns one durable file at `odd/features/<feature>.md`, named for the capability it describes and never dated, created from `odd/features/_template.md`; the template is the only feature-file template and the format is never reconstructed by research. Create the file the first time the feature is worked, and read and update it on every later change.
- **Name it for the capability, not the change.** The file name states what the system provides, in the words a reader would use to find it. The name survives a change of implementation: if replacing the mechanism would leave the name wrong, the name describes the mechanism rather than the capability. A name that must change whenever the implementation changes describes a change record, not a contract.
- **Update before creating.** Before creating a durable file, read `odd/features/` and decide whether the capability already belongs to an existing file. When it does, update that file; a new file is created only for a genuinely distinct, enduring capability with its own observable rules. One change may affect several durable files, and each affected file records the requirements that change touched.
- The file is not a second tracker. The record in `odd/tasks/` stays the single authoritative intent, task and status record for one change; the file states what the feature is and lists the requirements it must satisfy. The file lists no change records and holds no work-in-progress state. A requirement states only what must remain true and appends no pointer to implementation or history: no file path, heading reference, line number, command, or record of when or how it was checked is added to it, and no change record, its Log, or a line in one is cited. Where a specific path, component or artifact is itself part of the required behavior, the requirement names it as the behavior it guarantees rather than as evidence that the behavior exists. The evidence that a requirement was checked belongs in the change record that affected it.
- The shape is fixed: a title for the feature, one paragraph saying what it is, one status line, and the requirement list, where each requirement is one `R#` line in the form `- [ ] R# — <what must be true for this feature to count as complete>`.
- The status line follows the ticks rather than an independent claim: every requirement ticked is `achieved`, some ticked is `partial`, none ticked is `not started`. The validator computes and reports that derived status.
- A tick asserts that the requirement currently holds. A change re-verifies only the requirements it affects: when verification confirms the requirement, the tick stands; when a regression is established, the tick is removed and the failure and its cause are recorded in the change's own record; when verification could not be completed and the change demonstrably could have affected the requirement, the tick is removed and the uncertainty and its reason are recorded in the change's own record. Only the change that delivers or re-verifies a requirement may set its tick.
- A requirement carries a mark only when the feature adopts a standard that already exists, recording where this repository departs from it: `upstream` unchanged, `upstream · local detail` sharpened here, `upstream · narrowed` relaxed here, `local` added here, `local · conflicts` contradicting the standard. A feature explicit from this repository carries no mark.
- Every change reads the affected durable file and records what it changed in it: which requirements it added, reworded or retired, and the verification outcome for each affected requirement. Requirements the change did not affect are left alone and are not re-verified.
- Validate the file with the skill's validator, pointed at the file or the directory that holds the feature's files: `uv run --frozen python3 .agents/skills/odd-workflow/scripts/validate_feature_file.py <feature-file-or-directory>`. It reports the derived status. The script is **mechanical anatomy only**; exit 0 proves the shape, the requirement lines, the ticks and the placeholders. It does not prove that a requirement holds or that the feature is complete — the independent semantic review in `### Close` owns that. The record's own validation stays in `### Validate`.
- The mark vocabulary and the filling rules live in the template's `## Guidance` section, and each requirement's upstream source and local owner live where that requirement cites them. This skill owns the mechanics, not that analysis.

### Write meaningful specifications

Derive numbered `S#` behavioral clauses, constraints and acceptance checks from the request, corrections and approved proposal. Each entry states the required observable behavior and how it will be checked.

Every entry carries four parts: the `S#` identifier; an observable behavior or constraint statement; the requirement-defining wording preserved verbatim; and an acceptance clause. This shape illustrates one entry:

- `S# — <observable behavior or constraint statement>. Exact requirement: <requirement-defining wording, verbatim>. Acceptance: <one action> and <one observable result>.`

Those labels are illustrative, not required syntax: the mechanical validator accepts any `- S# — …` entry, so the shape proves anatomy only, never meaning.

One `S#` per independently verifiable outcome. Split when no single check covers all parts — a request that reports a defect, adds a capability and constrains a platform is three entries, because each part needs its own check.

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

Whether an entry is meaningful is owned by the independent semantic review in `### Close`, not by the validator.

### Delivery forecast

Forecast authored additions plus deletions, excluding generated files, and record the chosen delivery strategy and slice boundaries compactly in the existing document. Maintain a running count from work-unit commits; when the forecast OR the running count exceeds about 400 authored changed lines, apply the chosen strategy before the next commit. Keep the ~400-line task size advisory — not a hard cap, classification input, automatic review trigger, or delivery-slice boundary — separate from that feature-level strategy trigger, and add no second tracker.

### Before the first write

Apply `knowledge/agent-workflow.md` `### ODD protocol`, including its every-task uncertainty and observable-outcome controls. Do not restate that protocol here. That protocol's `#### Step reporting and transitions` owns step reporting, the state/evidence/next-action fields, and scope-bounded continuation. Execution review after creation or material replanning follows `AGENTS.md` → Conventions → Decision-only stops; check current authority and prerequisites, not an automatic document-creation approval pause.

### Change a requirement

Read and apply `knowledge/agent-workflow.md` `### Scope changes and readiness` before resuming affected work. In the feature record, rewrite only the affected spec and reopen only its task; do not append a new promise over a contradictory old one. Use the specification procedure above for changed requirements. Scope reassessment, stale-evidence handling and the artifact-free route remain defined by that workflow owner, not by this record procedure.

### Implement and verify

Read and apply `knowledge/agent-workflow.md` `### ODD protocol`, step 6, for dependency order, task acceptance checks, tests/documentation, conditional RED/GREEN/refactor, actual exceptions and existing owner/whole-suite gates; apply `knowledge/agents.md` `### Safe parallel task coordination (HARD RULE)` for accepted predecessors and concurrency. Carry the actual applicable runner and evidence to workers. Step reports and continuation follow the workflow's `#### Step reporting and transitions`.

For findings exposing related impact or escaped coverage, read and apply the workflow's `#### Finding-triggered impact reassessment and escape tracing`. Record the trace through the existing Log and the durable source that carries its detail, not a separate tracker. This pointer grants no additional read or write scope.

Apply the workflow's `### Behavioral verification and runner selection` for per-spec verification and command-regression evidence. After material record changes, work-unit commits, resume and closure, apply its `### Full feature mirror and resume`; retain the exact verified record revision or pending recovery in the existing Log, never a separate status tracker or a claim based only on a summary.

For feature work, the `## Log` records the outcome, the verdict, and a pointer that identifies where the evidence lives: the task/spec, the result, and the identity of the artifact that carries the detail — a commit, a path, or a pull request. The provenance detail — the literal command with its invocation and arguments, the tested input or commit identity, the dependency and environment identities, the responsible executor, and the expected versus observed result — lives in the durable source that already carries it: the committed diff, the test, a committed artifact, the pull-request body, or the record itself. Record it in the Log only when no durable source carries it. Evidence required for future verification or acceptance must remain in a durable source; a gitignored `output/` artifact may hold reproducible detail only. If no executable check applies, record the actual static/manual verification or justified N/A; never invent a test. This is evidence, not an execution transcript, new heading, or second tracker. Read-only and small work do not acquire a mandatory feature document.

For instruction changes, identify original and candidate inputs and preserve complete retained/translated/retired accounting of valid original obligations with authority and rationale before acceptance; the accounting decision and its outcome stay in the existing Log, its itemized detail stays in a durable source — the committed artifact, the pull-request body, or the record itself, and acceptance still requires the complete accounting to exist. For prose and examples, walk through applicable normal and adverse scenarios against their governing rules; record the manual action, inputs, expected outcome and observed outcome there. Literal execution provenance and separate observable-outcome evidence remain required; planned checks or an author's confidence are not results.

### Log evidence

Evidence for a feature falls into three classes. **Decisive** — requests, corrections, approvals and their labels, decisions, obligations, acceptance limits and commits — is permanent. It lives in the record while the record is live, and it must reach a durable owner — a durable feature file, an architecture decision record, the debt register, or the owning instruction file — before the record may be retired under `### Retire a task record`. **Reproducible** — content a reader can regenerate or re-read from Git, a committed artifact or a gitignored `output/` artifact — is referenced by pointer only. **Attestational** — obligation accounting, reviewer verdicts and identities, input and candidate identities, literal commands with observed results, and preservation mappings — lives in the durable source that already carries it: the committed diff, the test, a committed artifact, the pull-request body, or the record itself. A gitignored `output/` artifact may hold reproducible detail only; it never becomes the sole home of evidence required for future verification or acceptance.

There is no separate evidence artifact, directory, index or service. The record's `## Log` carries the decision, the outcome, the verdict and the pointer; the durable source carries the provenance. Never move, summarize, reformat or retype an entry that no available tool can read completely: keep it byte-identical in place, flag it, and state what a complete read requires.

When a finding-triggered trace is retained, identify the finding and available baseline, implementation and remediation candidates; retain inspected/assigned/changed evidence and coverage limitations, with defect origin separate from escape point and `unknown` valid where evidence is missing. Keep the coordinator-validated conclusions in the existing Log; the supporting detail stays in the durable source that carries it. One assigned writer incorporates owner responses and reviewer evidence; the trace grants no independent auditor writing authority. Before disposing of supporting detail, retain decisive classifications, limitations and lessons in the Log. Small/read-only work keeps its trace in the existing conversation, diff or report without a mandatory feature artifact.

**Close-time reconciliation** is part of closure. Before `Status: closed`, every decisive conclusion the change produced is either in the record or in the durable owner it belongs to, and the record names where it went. Git history is the recovery archive for what a committed artifact already carried.

### Close

Before completion, Cipher 🔓 (Lead Orchestrator) obtains an independent semantic review by a reviewer who did not author the delivered changes or their evidence. Compare the actual original request and corrections, Specs, delivered content, obligation accounting and evidence; account for every valid original obligation as retained, translated, or explicitly retired with authority and rationale. Check unresolved requirements, durable evidence at its proper owner (not essential evidence available only in temporary output), shared/local ownership, source neutrality, and precise execution provenance. When a PR exists, verify current PR evidence under its canonical evidence procedure. An author's summary, inherited marks, anatomy validation or a green suite cannot substitute. Require zero open findings before a clean feature completion claim; record the review identity, scope and result in the existing Log.

Separately verify remediation of reported findings and obtain fresh whole-feature semantic acceptance over the current combined candidate; remediation-only verification does not establish feature acceptance. Existing reviewer independence must hold, but this does not demand different new agents where it already holds. Identify the reviewed original/candidate inputs, full obligation accounting, literal provenance, scenario walkthroughs and outcome evidence in the existing Log before acceptance. Relevant changes invalidate affected verdicts and evidence. Preserve the existing `knowledge/agents.md` review-loop cap and accumulated rounds; changing reviewer does not reset it. These checks use existing gates and the single feature record, not a duplicate tracker, harness or additional pause.

Read and apply `knowledge/agent-workflow.md` `### ODD protocol`, step 7, for separate observable-outcome verification, failure reproduction and honest reporting of missing evidence/pending controls before task completion. Reporting and scope-bounded continuation follow its `#### Step reporting and transitions` and `knowledge/agents.md` `### Message presentation`. On close, every task is `done` and has a commit reference. Set `Status: closed`, add `> **Closed:** date`, and record a final `L# — Close:` entry.

### Retire a task record

A closed task record stays in `odd/tasks/` until every condition below holds. Retirement is a user-authorized deletion: it is never automatic, never a background service, and never an agent's own initiative.

1. **Closed.** The record carries `Status: closed`, a `> **Closed:**` date, a `Close:` Log entry, and every task row `done` with its commit reference.
2. **Age.** Seven complete calendar days have passed since the recorded `> **Closed:**` date. That date field is the only source; no timestamp is recorded and none is required.
3. **Delivered.** Closure is not delivery. Delivery is proven by the existing merge-proof rule in `knowledge/release.md` — the pull request's recorded merge commit reachable from the verified base, with the verified pull-request identity and the pinned branch tips — applied to the pull request that delivered the record. Herald 📯 (Release Manager) executes it. A squash or rebase merge is judged by that rule and never by ordinary commit ancestry; the record's own task commit is not the test.
4. **Unreferenced.** No durable tracked surface outside `odd/tasks/` cites the record: not a durable feature file, not an architecture decision record, not the debt register, not a research or architecture document, and not an owner instruction file.
5. **Durable home.** Every decisive conclusion the record holds — user approvals and authorization boundaries, accepted architectural decisions, open risks and known limitations, and unresolved obligations — already lives in a durable owner, named by the record.
6. **No open obligation.** No unresolved pull request, review round, approval, delivery dependency or user decision depends on the record.
7. **Authorized.** The user approved the deletion of that exact record. Herald 📯 (Release Manager) executes it; no agent deletes a record on its own initiative.

**Candidate inventory.** On explicit request, a read-only inventory of the records satisfying conditions 1, 2 and 4 is produced, with the reason each excluded record is excluded. The inventory is a proposal: deletion follows only after the user's explicit approval.

**Never retired.** A record whose decisive content has no durable home stays until that content is propagated to one. Retirement reduces the record corpus; it never discards a decision.

### Handoff

Pass a reference to the feature document and its `S#`, never a paraphrase. The worker reads until `## Log` and reports which specs it covered.

For the independent verification handoff, apply `knowledge/agent-workflow.md` → `### Behavioral verification and runner selection`: point the verifier to the whole feature including Log, its authorized examples and observed evidence; retain the returned per-spec verdicts and missing checks in the existing Log. This does not replace `### Close` semantic acceptance or grant execution authority.

### Feature scope

The feature's `Specs` and `Tasks` bound its requirements and work; they do not reserve an exclusive set of files. A feature may touch a shared rule or file when its canonical owner and authority are clear. Record relevant dependencies in the feature record and coordinate overlapping writes under `knowledge/agents.md` `### Safe parallel task coordination (HARD RULE)`; never invent a file-level isolation rule.

### Delivery boundary

Closing the feature document is not delivery. Explicit authorization may be supplied per action or through an applicable standing instruction; local commits are standing-authorized only when the project says so. Push, PR, merge, tag, release, and archive remain separately authorized, and a tool-permission denial is never bypassed. A PR is a reviewable slice — work-unit commits or the feature's task slice — never the accumulated branch and never a substitute for the feature document. Git execution remains with Herald 📯 (Release Manager); merge remains user-only.

### Release readiness and review findings

Apply `knowledge/release.md` before opening any PR and after every review round. Do not restate that workflow here. Feature `### Delivery boundary` authorization remains separately required.

### Validate

Run `uv run --frozen python3 .agents/skills/odd-workflow/scripts/validate_feature.py odd/tasks` before closing. The script is **mechanical anatomy only**; exit 0 proves the headings, `S#`/`T#`/`L1`, the Log's `L#` identifiers ascend with `L1` first, task status, 7–64 character hexadecimal commit references, and placeholders are correct. It does not prove verbatim fidelity, that a spec is meaningful, that a runner applies or ran, that a task is complete, or that the evidence is true — the independent semantic review above owns that, with acceptance by Cipher 🔓 (Lead Orchestrator).

### References

- `odd/tasks/_template.md` — the only feature-document template.
- `odd/features/_template.md` — the only durable-feature-file template.
- `.agents/skills/odd-workflow/references/_checklist.md` — creation and close checks; read it in full before creating or closing a feature.
- `.agents/skills/odd-workflow/scripts/validate_feature.py` — mechanical validator.
- `.agents/skills/odd-workflow/scripts/validate_feature_file.py` — mechanical validator for the durable feature file; it reports the derived status.
<!-- core:end -->
