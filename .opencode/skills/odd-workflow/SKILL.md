---
name: odd-workflow
description: Create and maintain the single ODD feature document in odd/tasks/. Use when starting a feature, adding a spec or task, recording a decision, changing a requirement, or closing a feature.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 2.0.0
---
<!-- core:begin -->

## Mandatory core

### What I do

Create, read, update, and close the single authoritative feature document for a feature. Its subordinate full mirror follows `knowledge/agent-workflow.md` → `### Full feature mirror and resume`; it is not a second tracker or a context-injection mechanism. This skill owns record mechanics, not a duplicate mirror protocol.

### Create a feature document

- Copy `odd/tasks/_template.md` to `odd/tasks/<YYYY-MM-DD>-<feature-name>.md`, using the document's creation date, which must equal its `Created:` header value; never reconstruct the format by research.
- Keep that creation-date prefix unchanged afterwards. Existing undated feature documents keep their names; `odd/tasks/_template.md` stays undated. The date prefix provides chronological filename sorting without changing other folders' ordering.
- Fill the short header with `Status`, `Owner`, and `Created` and always show all four context fields: `Objective`, `Branch`, `Delivery`, and `Runner`. Fill each field with the actual value or `N/A — reason`; do not silently omit a field, and never invent a branch or runner. Existing closed feature documents are not retrofitted. `Delivery` carries the chosen strategy, authored-line forecast, and slice boundaries; `Runner` is the literal applicable command.
- Fill `## Specs` using the specification procedure below.
- Fill `## Tasks` with one line per task: stable ID, linked `S#`, route (`inline` or `delegated`) with the reason/trigger that decided it — responsible owner, status (`open`, `in progress`, `done`), and commit. Record the route and its trigger evidence, not the route label alone. Use `commit: pending` only while status is `open` or `in progress`; `done` requires a 7–64 character hexadecimal commit identifier. One authorized coherent work-unit commit may evidence several tasks; do not require one commit per task. High-risk units may use separate reviewable commits.
- Fill `## Log` with `L1` = the original request verbatim; record each later user correction as its own entry dated and quoted verbatim, with evidence and rationale in separate entries rather than merged into the correction text.
- After bootstrap, apply the workflow's `### Full feature mirror and resume`. Keep verified project/feature identity, document locator, backend ID, exact verified content revision and comparison evidence, or explicit pending recovery, compactly in the existing Log. Respect project/task backend-write restrictions; record preparation does not itself establish runtime synchronization.

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

Apply the workflow's `### Behavioral verification and runner selection` for per-spec verification and command-regression evidence. After material record changes, work-unit commits, resume and closure, apply its `### Full feature mirror and resume`; retain the exact verified record revision or pending recovery in the existing Log, never a separate status tracker or a claim based only on a summary.

For feature work, record compact evidence in the existing `## Log`: task/spec, exact tested input/content or commit identity, relevant dependency and environment/configuration identities, responsible executor, literal command (including invocation and arguments) or manual action, expected result, observed result/verdict, and exit status when applicable. Preserve original execution provenance. If no executable check applies, record the actual static/manual verification or justified N/A; never invent a test. This is evidence, not an execution transcript, new heading, or second tracker. Read-only and small work do not acquire a mandatory feature document or evidence template.

For instruction changes, identify original and candidate inputs and preserve complete retained/translated/retired accounting of valid original obligations with authority and rationale in the existing Log before acceptance. For prose and examples, walk through applicable normal and adverse scenarios against their governing rules; record the manual action, inputs, expected outcome and observed outcome there. Literal execution provenance and separate observable-outcome evidence remain required; planned checks or an author's confidence are not results.

### Close

Before completion, Cipher 🔓 (Lead Orchestrator) obtains an independent semantic review by a reviewer who did not author the delivered changes or their evidence. Compare the actual original request and corrections, Specs, delivered content, obligation accounting and evidence; account for every valid original obligation as retained, translated, or explicitly retired with authority and rationale. Check unresolved requirements, durable evidence at its proper owner (not essential evidence available only in temporary output), shared/local ownership, source neutrality, and precise execution provenance. When a PR exists, verify current PR evidence under its canonical evidence procedure. An author's summary, inherited marks, anatomy validation or a green suite cannot substitute. Require zero open findings before a clean feature completion claim; record the review identity, scope and result in the existing Log.

Separately verify remediation of reported findings and obtain fresh whole-feature semantic acceptance over the current combined candidate; remediation-only verification does not establish feature acceptance. Existing reviewer independence must hold, but this does not demand different new agents where it already holds. Identify the reviewed original/candidate inputs, full obligation accounting, literal provenance, scenario walkthroughs and outcome evidence in the existing Log before acceptance. Relevant changes invalidate affected verdicts and evidence. Preserve the existing `knowledge/agents.md` review-loop cap and accumulated rounds; changing reviewer does not reset it. These checks use existing gates and the single feature record, not a duplicate tracker, harness or additional pause.

Read and apply `knowledge/agent-workflow.md` `### ODD protocol`, step 7, for separate observable-outcome verification, failure reproduction and honest reporting of missing evidence/pending controls before task completion. Reporting and scope-bounded continuation follow its `#### Step reporting and transitions` and `knowledge/agents.md` `### Message presentation`. On close, every task is `done` and has a commit reference. Set `Status: closed`, add `> **Closed:** date`, and record a final `L# — Close:` entry.

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

Run `uv run --frozen python3 .opencode/skills/odd-workflow/scripts/validate_feature.py odd/tasks` before closing. The script is **mechanical anatomy only**; exit 0 proves the headings, `S#`/`T#`/`L1`, task status, 7–64 character hexadecimal commit references, and placeholders are correct. It does not prove verbatim fidelity, that a spec is meaningful, that a runner applies or ran, that a task is complete, or that the evidence is true — the independent semantic review above owns that, with acceptance by Cipher 🔓 (Lead Orchestrator).

### References

- `odd/tasks/_template.md` — the only feature-document template.
- `.opencode/skills/odd-workflow/references/_checklist.md` — creation and close checks; read it in full before creating or closing a feature.
- `.opencode/skills/odd-workflow/scripts/validate_feature.py` — mechanical validator.
<!-- core:end -->
