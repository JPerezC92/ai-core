# Agent workflow

<!-- core:begin -->
## Mandatory core

Read this entry before acting. ODD is the governing workflow: read-only and small work create no durable feature artifact; authorized non-small state-changing work has one governing feature document before the first mutation. This entry routes work; it does not grant authority, replace an owner procedure, or prove delivery.

### ODD protocol

1. **Authorize** — Does the request authorize a change? Read-only requests stay read-only. Findings do not silently expand authorization.
2. **Explore** — Read the governing source and its required dependents, proportionately. Load applicable instructions and relevant dependencies.
3. **Resolve uncertainty** — Ask one focused question for a real user-only decision; investigate accessible facts first. Delegated workers report gaps to Cipher 🔓 (Lead Orchestrator) and never invoke the user-facing question tool.
4. **Classify** — Work is small only when it is understood, risk-contained, and resumable from the request plus diff; all three conditions must hold. Non-small work is anything else. Counts of files, commands, tests, fixes, tasks, or requested todo lists never decide classification. This ODD test is the authority for new work; `plan-enforce` handles existing legacy plans and user-confirmed legacy PR-merge cleanup, not new-work classification.
5. **Track before the first write** — Read-only and small work create no durable feature artifact. For authorized non-small state-changing work, create or update the governing feature document before the first state-changing action. Authorization and applicable safety/review gates remain independent.
6. **Implement task by task** — Deliver coherent slices in dependency order, respecting owner gates; dispatch independent ready tasks concurrently under the shared coordination rules. Define applicable acceptance checks and collect actual verification evidence with each task, not only at PR preparation. Tests and documentation ship with the slice. Follow the odd-workflow skill's implementation evidence procedure; never invent a runner or a test where none applies.
7. **Close** — Apply the odd-workflow skill's independent semantic completion review before a feature completion claim; anatomy validation or a green suite alone is insufficient. Report the verified outcome, every failed or pending check, and the next step. Reproduce a reported failure before deciding it already works.

### Task-specific navigation

Use the ODD classification and authorization rules above before choosing a change route. Start with the assignment's exact source paths, relevant dependencies, applicable runtime and skill; explore further only where the task or an unresolved fact requires it. This is the workflow router, not another task tracker.

| Task | Applicable read-pointers and boundary |
|---|---|
| Read-only explanation or inspection | Read the governing source and relevant dependencies. No feature artifact; unrelated read-only questions do not trigger blanket architecture reading. Architecture-dependent explanations follow the shared clean-architecture applicability rule. |
| Authorized non-small change | Read the governing `odd/tasks/<feature-name>.md` through `## Log`, the assigned `S#` and relevant Log evidence, then the named source/dependency paths and owner procedure. The authorized feature document precedes mutations; small work remains artifact-free. |
| Implementation or architecture/conformance review | Follow `knowledge/agents.md` → Clean architecture → `architecture/README.md` for common contract, applicable shapes and selected implementation guide. Preserve the owner's required full reads, relevant context, warmups and fresh-read checkpoints. |
| Testing design, test edit or test review | Follow `architecture/testing/architecture.md` and its applicable stack guide, with `.opencode/agents/crucible.md` and any additionally applicable language-owner procedure. Execution/install and edit gates remain runtime-owned. |
| Research or saved-evidence reuse | Follow `.opencode/agents/augur.md` → Research Workflow and the project's configured catalog, matching topics, cited evidence, template and publication owner. Inspect applicability/freshness before reuse and investigate bounded gaps; unrelated tasks do not require a research detour. |
| Incident identification | Follow `knowledge/agents.md` → Register-first identification and the assigned incident runtime/skill: symptom → incident problem → verdict, before evidence-only archive/pattern/KBA lookup after `no_match`. |
| Legacy migration or historical context | Use the named legacy owner/skill only when the task requires it. History, research and persona material do not replace current rules or become general prerequisites; retain any owner-required persona reads. |

Crosslinks locate owners; they do not require recursive rereading of every linked document. This does not waive runtime-required fresh/full reads or relevant dependency exploration. If a required pointer is missing, stop the affected operation and report the exact configured path, expected owner and missing evidence to Cipher 🔓 (Lead Orchestrator); never guess a replacement. An optional unconfigured/unavailable research catalog follows the research runtime's explicit gap-reporting route instead.

### Feature document

- One feature owns one document: `odd/tasks/<feature-name>.md`.
- `## Specs` carries numbered `S#` requirements, exact strings, and acceptance checks.
- `## Tasks` carries one line per task: stable ID, linked `S#`, route or owner, status, and commit.
- `## Log` carries `L1` = the original request verbatim, then corrections, evidence, and rationale appended in order.
- A requirement change rewrites only the affected spec and reopens only its task.
- Feature scope is the requirement/task boundary, not an exclusive file reservation. Shared-rule and shared-file changes are allowed when explicitly scoped, authorized through their canonical owner, and coordinated under `knowledge/agents.md` `### Safe parallel task coordination (HARD RULE)`; overlapping writes are serialized.
- Handoffs reference the document and its `S#`; the worker reads until `## Log` and reports which specs it covered.
- No second tracker, no Engram mirror, no per-request context injection.
- The Log holds decisions and evidence, not a running execution transcript.

### Template rule

Every repeatable artifact has exactly one template. Create a new file by copying its template and filling it; never reconstruct the format by research. If a second instance of a file type is needed and no template exists, create the template first.

| Artifact | Template |
|---|---|
| Feature document | `odd/tasks/_template.md` |
| Feature-document checklist | `.opencode/skills/odd-workflow/references/_checklist.md` |
| Implementation stack guide | `architecture/stacks/_template.md` |
| Testing stack guide | `architecture/testing/stacks/_template.md` |
| Legacy plan, migration only | `.opencode/skills/plan-enforce/references/_template.md` |
| Legacy story, migration only | `.opencode/skills/user-story/references/_template-user-story.md` |

### Conflict

Identify both obligations, their authority, owner, impact, and disposition. Stop affected action while unresolved. Do not silently expand unrelated work. Do not defer mandatory safeguards or necessary touched-file rework because correction is complex. Route unrelated defects to their owner with explicit deferral; reporting is not accepted debt.

### Keep files small

Put each concern in its owner. Before growing a file, remove duplication or extract a named responsibility with purpose, applicability, owner, and an explicit read-pointer. Do not split by arbitrary parts.

Extract skill support to `.opencode/skills/<skill>/references/<concern>.md`; executable tooling to `scripts/`; a new common policy to `knowledge/<concern>.md`. Architecture definitions belong in `architecture/`: select through `architecture/README.md`, read `architecture/clean-architecture.md`, applicable `architecture/shapes/`, and the selected implementation guide in `architecture/stacks/`; testing definitions belong in `architecture/testing/architecture.md` and its selected stack guide. Agent runtimes retain authority, execution, scope, gates, dependency ownership, and reporting, not competing definition copies. Source-local ADRs explain decisions under `docs/architecture/decisions/` and are not required shared dependencies. Move each obligation to one home, replace the old body with a pointer, update consumers, and verify links and clearance before deleting the old copy. Shared required extracts ship with clearance; source-local history is not a shared dependency.

New architecture paths and their consumers ship together through explicit per-file clearance; destination-authorized `core-sync init --bind-cleared` enrollment is required for new or markerless paths, not `apply` alone. Destination reconciliation remains destination-owned; pending reconciliation blocks acceptance. Documentation review does not establish implementation conformance or authorize application remediation.

Durable history lives at its owner: the feature document's `## Log`, the story's change log if a story still exists, the ADR, and `docs/architecture/history/`. A plan's `## Resolved decisions` is temporal; it does not replace the owner record.
<!-- core:end -->

<!-- project:begin -->
## Project extensions
<!-- project:end -->
