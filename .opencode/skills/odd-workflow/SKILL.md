---
name: odd-workflow
description: Create and maintain the single ODD feature document at odd/tasks/<feature-name>.md. Use when starting a feature, adding a spec or task, recording a decision, changing a requirement, or closing a feature.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.1.0
---
<!-- core:begin -->

## Mandatory core

### What I do

Create, read, update, and close the single feature document for a feature. I do not create a second tracker, an Engram mirror, or a context-injection mechanism.

### Create a feature document

- Copy `odd/tasks/_template.md` to `odd/tasks/<feature-name>.md`; never reconstruct the format by research.
- Fill `## Specs` with numbered `S#` requirements, exact strings, and acceptance checks.
- Fill `## Tasks` with one line per task: stable ID, linked `S#`, route or owner, status (`open`, `in progress`, `done`), and commit.
- Fill `## Log` with `L1` = the original request verbatim, then corrections, evidence, and rationale in order.

### Before the first write

For non-trivial work, the feature document exists before the first state-changing action. Read-only requests stay read-only and create no artifact. The existing plan-enforce threshold decides whether work is non-trivial; this skill does not change it.

### Change a requirement

Rewrite only the affected spec and reopen only its task. Do not append a new promise over a contradictory old one.

### Close

Report the verified outcome, every failed or pending check, and the next step. Reproduce a reported failure before deciding it already works. On close, every task is `done`; set `Status: closed`, add `> **Closed:** date`, and record a final `L# — Close:` entry.

### Handoff

Pass a reference to the feature document and its `S#`, never a paraphrase. The worker reads until `## Log` and reports which specs it covered.

### Delivery boundary

Closing the feature document is not delivery. Commit, push, PR, release, and archive require explicit user authorization. A PR is a reviewable slice — work-unit commits or the feature's task slice — never the accumulated branch and never a substitute for the feature document. Git execution remains with Herald; merge remains user-only.

### Validate

Run `uv run --frozen python3 .opencode/skills/odd-workflow/scripts/validate_feature.py odd/tasks` before closing. The script is **mechanical anatomy only**; exit 0 proves the headings, `S#`/`T#`/`L1`, task status, and placeholders are correct. It does not prove that a spec is meaningful, a task is complete, or the evidence is true — Cipher's semantic review owns that.

### References

- `odd/tasks/_template.md` — the only feature-document template.
- `.opencode/skills/odd-workflow/references/_checklist.md` — creation and close checks.
- `.opencode/skills/odd-workflow/scripts/validate_feature.py` — mechanical validator.
<!-- core:end -->

<!-- project:begin -->
## Project extensions
<!-- project:end -->
