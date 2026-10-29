# Agent workflow

<!-- core:begin -->
## Mandatory core

Read this entry before acting. ODD is the governing workflow: read-only and small work create no durable feature artifact. For authorized non-small state-changing work, creating the governing feature document from its template is the sole authorized bootstrap write; no other mutation precedes it. Revise an existing document before affected work resumes and retain the execution-review pause. This entry routes work; it does not grant authority, replace an owner procedure, or prove delivery.

### ODD protocol

1. **Authorize** — Does the request authorize a change? Read-only requests stay read-only. Findings do not silently expand authorization. Report the permitted outcome and boundary with the request/standing-instruction evidence; COMPLETE when that boundary is established, then explore. Missing user-only authority blocks the affected operation and names the required decision.
2. **Explore** — Read the governing source and its required dependents, proportionately. Load applicable instructions and relevant dependencies. Report inspected inputs and evidence gaps; COMPLETE when sufficient context supports the next decision, then resolve uncertainty. Route resolvable gaps through the coordinator, not automatically to the user.
3. **Resolve uncertainty** — Before implementation, resolve task-relevant uncertainty, identify the requested observable outcome and the minimal sufficient change, and distinguish that outcome from the proposed mechanism. Ask one focused question for a real user-only decision; investigate accessible facts first. Delegated workers report gaps to Cipher 🔓 (Lead Orchestrator) and never invoke the user-facing question tool. Report the resolution and evidence; when no question is needed, state why the available evidence settles the relevant uncertainty. COMPLETE then classify; unresolved prerequisites keep affected work BLOCKED with its resolution owner and next action.
4. **Classify** — Work is small only when it is understood, risk-contained, and resumable from the request plus diff; all three conditions must hold. Non-small work is anything else. Counts of files, commands, tests, fixes, tasks, or requested todo lists never decide classification. This ODD test is the authority for new work. Report the evidence for all three tests and resulting class; COMPLETE then apply step 5, including its artifact-free route. Missing classification means stop and report before writing. Do not start step 5, and do not mutate, until the three-test result is reported.
5. **Track before the first write** — Read-only and small work create no durable feature artifact: report artifact creation NOT APPLICABLE with that reason, then proceed only within the authorized route. For authorized non-small state-changing work, creating the governing feature document from `odd/tasks/_template.md` is the sole authorized bootstrap write. A missing required feature document permits only that authorized bootstrap creation. No other mutation — edit, write, delete, rename, or mutating shell command — precedes it. Never implement first and document retroactively. Revise an existing governing document before affected work resumes. Produce the feature document and execution review under the existing `AGENTS.md` Conventions pause; report its evidence and pending decision, and do not mark this step COMPLETE or implement until the existing execution-review gate permits continuation. Authorization and applicable safety/review gates remain independent.
6. **Implement task by task** — Deliver coherent slices in dependency order, respecting owner gates; dispatch independent ready tasks concurrently under the shared coordination rules. Define applicable acceptance checks and collect actual verification evidence with each task, not only at PR preparation. Tests and documentation ship with the slice. Follow the odd-workflow skill's implementation evidence procedure. When a relevant runnable deterministic test and a clear expected outcome exist, observe RED before implementation, then GREEN and refactor; otherwise record the actual exception and run proportionate checks. Never invent a runner or a test where none applies; do not add a test harness. Existing architecture/edit gates, whole-suite ownership, and independent completion review remain binding. Report each slice's result, outcome evidence, check/gate states and next ready task; loop here while tasks or applicable owner gates remain. An authored slice may finish while step 6 remains IN PROGRESS: never mark it COMPLETE pending an applicable owner gate. When all task delivery gates and outcome checks are satisfied, report COMPLETE and advance to independent feature acceptance in step 7. Read-only work reports implementation NOT APPLICABLE and advances to outcome verification without mutation.
7. **Close** — Before claiming any task done, verify the requested observable outcome separately from tests, architecture review or source-health checks; those checks do not substitute for outcome evidence. Apply the odd-workflow skill's independent semantic completion review before a feature completion claim; anatomy validation or a green suite alone is insufficient. Report the verified outcome, missing evidence, every failed or pending check/control, and the next step; do not represent pending controls as satisfied. Reproduce a reported failure before deciding it already works. Feature acceptance is independent of step 6 slice/owner-gate acceptance; follow the skill's Close safeguards. COMPLETE only with current required acceptance and outcome evidence; otherwise remain IN PROGRESS/BLOCKED or return to the affected earlier step. Small/read-only work verifies its outcome without creating a feature artifact. Exhausted verified authorized scope ends with ALL FINISHED; remaining authorized work continues under the transitions below.

These uncertainty and outcome controls apply to every task, including small and read-only work. On a user correction, Cipher 🔓 (Lead Orchestrator) re-evaluates the requested goal against the mechanism and scope, updates affected Specs/tasks before affected work resumes, and invalidates stale assignments and evidence; unrelated work stays unchanged. Small/read-only work keeps corrected intent in the existing conversation/diff, without a feature artifact. Workers report affected gaps and stale evidence to the coordinator. Use the existing workflow and gates: no new tracker, count threshold, extra ritual/pause or user confirmation is introduced, and existing approvals remain binding.

#### Step reporting and transitions

- **Step report:** after each completed step, report feature/task identity; step number and name; state; result; evidence pointer; next action.
- **States:** ✅ COMPLETE · 🟡 IN PROGRESS · 🚧 BLOCKED · ⏭️ NOT APPLICABLE/SKIPPED. The full vocabulary and presentation rules live in `knowledge/agents.md` `### Message presentation`.
- **Continuation:** continue to the next ready task inside the active authorized scope; task completion is not a stop. A blocker is an unmet prerequisite preventing the affected operation: name its resolution owner and next action. Resolve coordinator/agent-resolvable blockers within existing authority; only a genuine user-only decision or permission requires a user stop with the exact user action. If the authorized scope is exhausted and verified, say `ALL FINISHED` with delivered scope, verification, deferred items, and next options; do not select unrelated work.
- **Skipped steps:** a skipped or inapplicable step states its reason. A checkpoint or owner-gate return (`AWAITING_REVIEW`, `BLOCKED`) is not step completion.
- **Transitions:** the seven steps are not seven implementation tasks; step 6 repeats task-level delivery. A failed review stays in step 6 unless it exposes a requirement or scope change, which returns to the affected earlier step. Step 7 is incomplete while any required review or check remains.
- **Bootstrap and pause:** creating the governing feature document is the sole bootstrap write. The execution-review pause after creating it or materially replanning is owned by `AGENTS.md` → Conventions; this protocol points to it and does not duplicate it.

**Illustrative examples only — not execution evidence or actual feature status.**

- **Uncertainty resolved without a question:** `example-feature · T1 — Step 3 Resolve uncertainty — ✅ COMPLETE — uncertainty: whether small work requires a feature document. Evidence: knowledge/agent-workflow.md, ODD protocol steps 4–5, explicitly makes small work artifact-free. Requested outcome: follow the authorized small-work route; minimal sufficient change: no feature-document creation. No additional research or user question required: the existing contract settles the artifact requirement; classification remains to be established. Next: Step 4 Classify against all three tests. Continuing.`
- **Authored slice, owner gate pending:** `example-feature · T4 — Step 6 Implement task by task — 🟡 IN PROGRESS — authored presentation slice finished; applicable owner review pending. Evidence: candidate slice and pending gate recorded in the example feature Log. Next: obtain owner verdict before completing step 6; step 7 independent feature acceptance follows delivery gates. No user action needed: the coordinator can dispatch the authorized review. Continuing.`
- **Skipped check, not a completed phase:** `example-feature · T5 — Step 6 Implement task by task — 🟡 IN PROGRESS; RED/GREEN check ⏭️ NOT APPLICABLE — reason: prose-only slice has no applicable executable test; manual walkthrough is recorded in the example feature Log. Next: finish pending owner review, then independent feature acceptance. Continuing.`

### PR release readiness

Before opening a PR, Cipher 🔓 (Lead Orchestrator) assembles and verifies one release-readiness packet: the exact test-plan actions or commands with their observed results; every applicable gate status; the open-or-closed status of each task and of the feature; excluded or unrelated paths; unverified user-only controls; and each body claim against its evidence. Missing, contradictory, or stale evidence blocks PR creation until resolved — a partially verified packet is never an acceptable substitute. This applies to every PR, including docs-only changes, and introduces no tracker, no second approval ritual, and no change to existing authorizations or gates.

### Post-review finding actions

After each review round, Cipher 🔓 (Lead Orchestrator) uses the canonical combined rendered chat summary or, only when eligible, compact ready message in `knowledge/agents.md` `### PR review findings (adjudication)`. That owner defines finding presentation, accounting and readiness conditions; a raw findings list is not an acceptable handoff. Its fix-first rule, deferral authority, refutation evidence and loop cap remain unchanged, as do all existing gates; no tracker or additional approval step is introduced.

### Task-specific navigation

Use the ODD classification and authorization rules above before choosing a change route. Start with the assignment's exact source paths, relevant dependencies, applicable runtime and skill; explore further only where the task or an unresolved fact requires it. This is the workflow router, not another task tracker.

| Task | Applicable read-pointers and boundary |
|---|---|
| Read-only explanation or inspection | Read the governing source and relevant dependencies. No feature artifact; unrelated read-only questions do not trigger blanket architecture reading. Architecture-dependent explanations follow the shared clean-architecture applicability rule. |
| Authorized non-small change | Read the governing `odd/tasks/<feature-name>.md` through `## Log`, the assigned `S#` and relevant Log evidence, then the named source/dependency paths and owner procedure. Only authorized template-based creation of that document may bootstrap; no other mutation precedes it, and revisions precede affected work. Small work remains artifact-free. |
| Implementation or architecture/conformance review | Follow `knowledge/agents.md` → Clean architecture → `architecture/README.md` for common contract, applicable shapes and selected implementation guide. Preserve the owner's required full reads, relevant context, warmups and fresh-read checkpoints. |
| Testing design, test edit or test review | Follow `architecture/testing/architecture.md` and its applicable stack guide, with `.opencode/agents/crucible.md` and any additionally applicable language-owner procedure. Execution/install and edit gates remain runtime-owned. |
| Research or saved-evidence reuse | Follow `.opencode/agents/augur.md` → Research Workflow and the project's configured catalog, matching topics, cited evidence, template and publication owner. Inspect applicability/freshness before reuse and investigate bounded gaps; unrelated tasks do not require a research detour. |
| Incident identification | Follow `knowledge/agents.md` → Register-first identification and the assigned incident runtime/skill: symptom → incident problem → verdict, before evidence-only archive/pattern/KBA lookup after `no_match`. |
| Historical context | History, research and persona material do not replace current rules or become general prerequisites; retain any owner-required persona reads. |
| Cache retrieval or code analysis | Apply `knowledge/agents.md` → Applicable analysis tools and the root runtime's project bindings: use relevant exposed, authorized tools during exploration/review, report justified non-use or limitations, and retain role scope, full reads and execution gates. |

Crosslinks locate owners; they do not require recursive rereading of every linked document. This does not waive runtime-required fresh/full reads or relevant dependency exploration. If a required pointer is missing, stop the affected operation and report the exact configured path, expected owner and missing evidence to Cipher 🔓 (Lead Orchestrator); never guess a replacement. An optional unconfigured/unavailable research catalog follows the research runtime's explicit gap-reporting route instead.

### Feature document

- One feature owns one document: `odd/tasks/<feature-name>.md`.
- The short header keeps `Status`, `Owner`, and `Created` and always shows the `Objective`, `Branch`, `Delivery`, and `Runner` context fields. Fill each field with the actual value or `N/A — reason`; never silently omit a field or invent a branch or runner. Existing closed feature documents are not retrofitted. `Delivery` carries the chosen strategy, authored-line forecast, and slice boundaries; `Runner` is the literal applicable command.
- `## Specs` carries numbered `S#` requirements, exact strings, and acceptance checks. Preserve the user's exact requirements, strings, errors, commands, and examples verbatim; do not paraphrase, normalize, or add unrequested requirements. Record genuine uncertainty as evidence or a focused question, never an unsupported assumption.
- `## Tasks` carries one line per task: stable ID, linked `S#`, route (`inline` or `delegated`) with the reason/trigger that decided it — responsible owner, status, and commit. Record the route and its trigger evidence, not the route label alone. A `done` task cites a 7–64 character hexadecimal commit reference. An authorized coherent work-unit commit may evidence several tasks; do not require one commit per task. High-risk units may use separate reviewable commits.
- Forecast authored additions plus deletions, excluding generated files, and record the chosen delivery strategy and slice boundaries compactly in the existing document. Maintain a running count from work-unit commits; when the forecast OR the running count exceeds about 400 authored changed lines, apply the chosen strategy before the next commit. The ~400-line task size is advisory only — not a hard cap, classification input, automatic review trigger, or delivery-slice boundary — and stays separate from that feature-level strategy trigger.
- `## Log` carries `L1` = the original request verbatim; each later user correction is its own entry dated and quoted verbatim, with evidence and rationale in separate entries rather than merged into the correction text.
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

### Conflict

Identify both obligations, their authority, owner, impact, and disposition. Stop affected action while unresolved. Do not silently expand unrelated work. Do not defer mandatory safeguards or necessary touched-file rework because correction is complex. Route unrelated defects to their owner with explicit deferral; reporting is not accepted debt.

### Keep files small

Put each concern in its owner. Before growing a file, remove duplication or extract a named responsibility with purpose, applicability, owner, and an explicit read-pointer. Do not split by arbitrary parts.

Extract skill support to `.opencode/skills/<skill>/references/<concern>.md`; executable tooling to `scripts/`; a new common policy to `knowledge/<concern>.md`. Architecture definitions belong in `architecture/`: select through `architecture/README.md`, read `architecture/clean-architecture.md`, applicable `architecture/shapes/`, and the selected implementation guide in `architecture/stacks/`; testing definitions belong in `architecture/testing/architecture.md` and its selected stack guide. Agent runtimes retain authority, execution, scope, gates, dependency ownership, and reporting, not competing definition copies. Source-local ADRs explain decisions under `docs/architecture/decisions/` and are not required shared dependencies. Move each obligation to one home, replace the old body with a pointer, update consumers, and verify links and clearance before deleting the old copy. Shared required extracts ship with clearance; source-local history is not a shared dependency.

New architecture paths and their consumers ship together through explicit per-file clearance; destination-authorized `core-sync init --bind-cleared` enrollment is required for new or markerless paths, not `apply` alone. Destination reconciliation remains destination-owned; pending reconciliation blocks acceptance. Documentation review does not establish implementation conformance or authorize application remediation.

Durable history lives at its owner: the feature document's `## Log`, the ADR, and `docs/architecture/history/`.
<!-- core:end -->

<!-- project:begin -->
## Project extensions
<!-- project:end -->
