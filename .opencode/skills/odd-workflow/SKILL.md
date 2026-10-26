---
name: odd-workflow
description: Create and maintain the single ODD feature document in odd/tasks/. Use when starting a feature, adding a spec or task, recording a decision, changing a requirement, or closing a feature.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.4.0
---
<!-- core:begin -->

## Mandatory core

### What I do

Create, read, update, and close the single feature document for a feature. I do not create a second tracker, an Engram mirror, or a context-injection mechanism.

### Create a feature document

- Copy `odd/tasks/_template.md` to `odd/tasks/<feature-name>.md`; never reconstruct the format by research.
- Fill `## Specs` with numbered `S#` requirements, exact strings, and acceptance checks.
- Fill `## Tasks` with one line per task: stable ID, linked `S#`, route or owner, status (`open`, `in progress`, `done`), and commit. Use `commit: pending` only while status is `open` or `in progress`; `done` requires a 7–64 character hexadecimal commit identifier.
- Fill `## Log` with `L1` = the original request verbatim, then corrections, evidence, and rationale in order.

### Before the first write

Classify using `knowledge/agent-workflow.md` `### ODD protocol`: work is small only when it is understood, risk-contained, and resumable from the request plus diff; counts do not decide. Read-only and small work create no durable feature artifact. For authorized non-small state-changing work, the governing feature document exists before the first state-changing action. Authorization and safety/review gates remain independent; plan-enforce does not classify new work.

### Change a requirement

Rewrite only the affected spec and reopen only its task. Do not append a new promise over a contradictory old one.

### Implement and verify

Deliver coherent tasks in dependency order with their tests and documentation. Respect accepted predecessors and owner gates; independent ready tasks may run concurrently under the shared coordination rules. Define each task's applicable acceptance checks and collect actual evidence during implementation, not only when preparing a PR.

For feature work, record compact evidence in the existing `## Log`: task/spec, exact tested input/content or commit identity, relevant dependency and environment/configuration identities, responsible executor, literal command (including invocation and arguments) or manual action, expected result, observed result/verdict, and exit status when applicable. Preserve original execution provenance. If no executable check applies, record the actual static/manual verification or justified N/A; never invent a test. This is evidence, not an execution transcript, new heading, or second tracker. Read-only and small work do not acquire a mandatory feature document or evidence template.

### Close

Before completion, Cipher 🔓 (Lead Orchestrator) obtains an independent semantic review by a reviewer who did not author the delivered changes or their evidence. Compare the actual original request and corrections, Specs, delivered content, obligation accounting and evidence; account for every valid original obligation as retained, translated, or explicitly retired with authority and rationale. Check unresolved requirements, durable evidence at its proper owner (not essential evidence available only in temporary output), shared/local ownership, source neutrality, and precise execution provenance. When a PR exists, verify current PR evidence under its canonical evidence procedure. An author's summary, inherited marks, anatomy validation or a green suite cannot substitute. Require zero open findings before a clean feature completion claim; record the review identity, scope and result in the existing Log.

Report the verified outcome, every failed or pending check, and the next step. Reproduce a reported failure before deciding it already works. On close, every task is `done` and has a commit reference. Set `Status: closed`, add `> **Closed:** date`, and record a final `L# — Close:` entry.

### Handoff

Pass a reference to the feature document and its `S#`, never a paraphrase. The worker reads until `## Log` and reports which specs it covered.

### Feature scope

The feature's `Specs` and `Tasks` bound its requirements and work; they do not reserve an exclusive set of files. A feature may touch a shared rule or file when its canonical owner and authority are clear. Record relevant dependencies in the feature record and coordinate overlapping writes under `knowledge/agents.md` `### Safe parallel task coordination (HARD RULE)`; never invent a file-level isolation rule.

### Delivery boundary

Closing the feature document is not delivery. Commit, push, PR, release, and archive require explicit user authorization. A PR is a reviewable slice — work-unit commits or the feature's task slice — never the accumulated branch and never a substitute for the feature document. Git execution remains with Herald; merge remains user-only.

### Validate

Run `uv run --frozen python3 .opencode/skills/odd-workflow/scripts/validate_feature.py odd/tasks` before closing. The script is **mechanical anatomy only**; exit 0 proves the headings, `S#`/`T#`/`L1`, task status, and placeholders are correct. It does not prove that a spec is meaningful, a task is complete, or the evidence is true — the independent semantic review above owns that, with acceptance by Cipher 🔓 (Lead Orchestrator).

### References

- `odd/tasks/_template.md` — the only feature-document template.
- `.opencode/skills/odd-workflow/references/_checklist.md` — creation and close checks.
- `.opencode/skills/odd-workflow/scripts/validate_feature.py` — mechanical validator.
<!-- core:end -->

<!-- project:begin -->
## Project extensions
<!-- project:end -->
