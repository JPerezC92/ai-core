---
name: odd-workflow
description: Create and maintain the single ODD feature document in odd/tasks/. Use when starting a feature, adding a spec or task, recording a decision, changing a requirement, or closing a feature.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.8.2
---
<!-- core:begin -->

## Mandatory core

### What I do

Create, read, update, and close the single feature document for a feature. I do not create a second tracker, an Engram mirror, or a context-injection mechanism.

### Create a feature document

- Copy `odd/tasks/_template.md` to `odd/tasks/<feature-name>.md`; never reconstruct the format by research.
- Fill the short header with `Status`, `Owner`, and `Created` and always show all four context fields: `Objective`, `Branch`, `Delivery`, and `Runner`. Fill each field with the actual value or `N/A — reason`; do not silently omit a field, and never invent a branch or runner. Existing closed feature documents are not retrofitted. `Delivery` carries the chosen strategy, authored-line forecast, and slice boundaries; `Runner` is the literal applicable command.
- Fill `## Specs` with numbered `S#` requirements, exact strings, and acceptance checks. Preserve the user's exact requirements, strings, errors, commands, and examples verbatim; do not paraphrase, normalize, or add unrequested requirements. Record genuine uncertainty as evidence or a focused question, never an unsupported assumption.
- Fill `## Tasks` with one line per task: stable ID, linked `S#`, route (`inline` or `delegated`) with the reason/trigger that decided it — responsible owner, status (`open`, `in progress`, `done`), and commit. Record the route and its trigger evidence, not the route label alone. Use `commit: pending` only while status is `open` or `in progress`; `done` requires a 7–64 character hexadecimal commit identifier. One authorized coherent work-unit commit may evidence several tasks; do not require one commit per task. High-risk units may use separate reviewable commits.
- Fill `## Log` with `L1` = the original request verbatim; record each later user correction as its own entry dated and quoted verbatim, with evidence and rationale in separate entries rather than merged into the correction text.

### Delivery forecast

Forecast authored additions plus deletions, excluding generated files, and record the chosen delivery strategy and slice boundaries compactly in the existing document. Maintain a running count from work-unit commits; when the forecast OR the running count exceeds about 400 authored changed lines, apply the chosen strategy before the next commit. Keep the ~400-line task size advisory — not a hard cap, classification input, automatic review trigger, or delivery-slice boundary — separate from that feature-level strategy trigger, and add no second tracker.

### Before the first write

Apply `knowledge/agent-workflow.md` `### ODD protocol`, including its every-task uncertainty and observable-outcome controls. Do not restate that protocol here. That protocol's `#### Step reporting and transitions` owns step reporting, the state/evidence/next-action fields, and scope-bounded continuation. The execution-review pause after creating the document or materially replanning is owned by `AGENTS.md` → Conventions.

### Change a requirement

Apply the protocol's correction checkpoint before resuming affected work: re-evaluate goal versus mechanism/scope, rewrite only the affected spec and reopen only its task, and invalidate affected stale evidence and assignments. Do not append a new promise over a contradictory old one. Small/read-only work retains corrected intent in the existing conversation/diff, not a new artifact.

### Implement and verify

Deliver coherent tasks in dependency order with their tests and documentation. Respect accepted predecessors and owner gates; independent ready tasks may run concurrently under the shared coordination rules. Define each task's applicable acceptance checks and collect actual evidence during implementation, not only when preparing a PR.

Conditional test-first: when a relevant runnable deterministic test and a clear expected outcome exist, observe RED before implementation, then GREEN and refactor; otherwise record the actual exception and run proportionate checks. Carry the actual runner and evidence to workers; never invent a runner or add a test harness. Existing architecture/edit gates, whole-suite ownership, and independent completion review remain binding.

For feature work, record compact evidence in the existing `## Log`: task/spec, exact tested input/content or commit identity, relevant dependency and environment/configuration identities, responsible executor, literal command (including invocation and arguments) or manual action, expected result, observed result/verdict, and exit status when applicable. Preserve original execution provenance. If no executable check applies, record the actual static/manual verification or justified N/A; never invent a test. This is evidence, not an execution transcript, new heading, or second tracker. Read-only and small work do not acquire a mandatory feature document or evidence template.

For instruction changes, identify original and candidate inputs and preserve complete retained/translated/retired accounting of valid original obligations with authority and rationale in the existing Log before acceptance. For prose and examples, walk through applicable normal and adverse scenarios against their governing rules; record the manual action, inputs, expected outcome and observed outcome there. Literal execution provenance and separate observable-outcome evidence remain required; planned checks or an author's confidence are not results.

### Close

Before completion, Cipher 🔓 (Lead Orchestrator) obtains an independent semantic review by a reviewer who did not author the delivered changes or their evidence. Compare the actual original request and corrections, Specs, delivered content, obligation accounting and evidence; account for every valid original obligation as retained, translated, or explicitly retired with authority and rationale. Check unresolved requirements, durable evidence at its proper owner (not essential evidence available only in temporary output), shared/local ownership, source neutrality, and precise execution provenance. When a PR exists, verify current PR evidence under its canonical evidence procedure. An author's summary, inherited marks, anatomy validation or a green suite cannot substitute. Require zero open findings before a clean feature completion claim; record the review identity, scope and result in the existing Log.

Separately verify remediation of reported findings and obtain fresh whole-feature semantic acceptance over the current combined candidate; remediation-only verification does not establish feature acceptance. Existing reviewer independence must hold, but this does not demand different new agents where it already holds. Identify the reviewed original/candidate inputs, full obligation accounting, literal provenance, scenario walkthroughs and outcome evidence in the existing Log before acceptance. Relevant changes invalidate affected verdicts and evidence. Preserve the existing `knowledge/agents.md` review-loop cap and accumulated rounds; changing reviewer does not reset it. These checks use existing gates and the single feature record, not a duplicate tracker, harness or additional pause.

Apply the protocol's separate observable-outcome verification before any task completion claim; tests, architecture and source-health evidence are not outcome proof. Report the verified outcome, missing evidence, every failed or pending check/control, and the next step without claiming pending controls are satisfied. Reproduce a reported failure before deciding it already works. When the authorized scope is complete, present it with the `ALL FINISHED` format in `knowledge/agents.md` `### Message presentation`; do not select unrelated work. On close, every task is `done` and has a commit reference. Set `Status: closed`, add `> **Closed:** date`, and record a final `L# — Close:` entry.

### Handoff

Pass a reference to the feature document and its `S#`, never a paraphrase. The worker reads until `## Log` and reports which specs it covered.

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
