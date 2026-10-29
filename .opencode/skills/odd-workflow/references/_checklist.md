# ODD feature-document checklist

## Create

- [ ] This is authorized non-small state-changing work; read-only and small work require no feature artifact or new evidence template.
- [ ] Copy `odd/tasks/_template.md`; do not invent the format.
- [ ] Header carries Status, Owner, and Created and always shows all four context fields — Objective, Branch, Delivery, and Runner — each filled with the actual value or `N/A — reason`; no field is silently omitted, and no branch or runner is invented. Existing closed feature documents are not retrofitted.
- [ ] `## Specs` has numbered `S#` with exact strings and acceptance checks: the user's exact requirements, strings, errors, commands, and examples are preserved verbatim with their checks alongside, and nothing is paraphrased, normalized, or added unrequested. Uncertainty is recorded as evidence or a focused question, not an unsupported assumption.
- [ ] `## Tasks` has stable IDs, linked `S#`, route (`inline` or `delegated`) with the reason/trigger that decided it — responsible owner, status (`open`, `in progress`, `done`), and commit; the route and its trigger evidence are recorded, not the route label alone. `pending` is only for open/in-progress tasks; done tasks cite a 7–64 character hexadecimal commit identifier. One authorized coherent work-unit commit may evidence several tasks; one commit per task is not required, and high-risk units may use separate reviewable commits.
- [ ] Authored additions plus deletions are forecast excluding generated files; the chosen strategy and slice boundaries are recorded compactly in this document, and a running count is maintained from work-unit commits so the strategy is applied before the next commit when either the forecast or the running count exceeds about 400 authored changed lines. The ~400-line task size stays advisory and separate — no hard cap, classification input, automatic review trigger, delivery-slice boundary, or second tracker is introduced.
- [ ] `## Log` starts with `L1` = the original request verbatim; each later user correction is its own dated, verbatim entry, with evidence and rationale in separate entries rather than merged into the correction text.

## Before the first write

- [ ] The request is authorized; read-only work stays read-only.
- [ ] The governing ODD protocol's every-task uncertainty/outcome checkpoint is applied: task-relevant uncertainty is resolved, the requested observable outcome is distinguished from the mechanism, and the minimal sufficient change is identified. Small/read-only work gains no artifact or extra ritual/confirmation.
- [ ] Classify with the ODD test: small only when understood, risk-contained, and resumable from request plus diff; counts never decide.
- [ ] Read-only and small work create no durable feature artifact. For authorized non-small state-changing work, creating the governing ODD feature document from its template is the sole authorized bootstrap write; no other mutation precedes it. Revise an existing document before affected work resumes, retaining the execution-review pause below.
- [ ] Authorization and applicable safety/review gates are checked independently of classification.
- [ ] Feature scope is expressed through Specs/Tasks, not treated as an exclusive file partition; shared-resource overlap names its canonical owner/dependency and follows serialized-writer coordination.
- [ ] After creating the governing document or materially replanning, the execution-review pause is presented — Issue → Goal → How → Files, the gate, and the decision needed — before implementation; routine Log/evidence updates do not restart it, and creating the document is the sole bootstrap write. Owner: `AGENTS.md` → Conventions.

## Change

- [ ] A user correction re-evaluates goal versus mechanism/scope under the governing protocol; affected Specs/tasks are updated before affected work resumes, with stale assignments/evidence invalidated. Small/read-only intent stays in the existing conversation/diff. A requirement change rewrites only the affected spec.
- [ ] The affected task is reopened; unrelated tasks stay unchanged.

## Implement and verify

- [ ] Coherent tasks follow dependency order and owner gates; independent ready tasks may proceed concurrently under shared coordination rules.
- [ ] Conditional test-first: when a relevant runnable deterministic test and a clear expected outcome exist, RED is observed before implementation, then GREEN and refactor; otherwise the actual exception and proportionate checks are recorded. No runner or test harness is invented; architecture/edit gates, whole-suite ownership, and independent completion review remain binding.
- [ ] Each task defines applicable acceptance checks and collects actual evidence during implementation; its tests and documentation ship with the slice.
- [ ] Compact existing-Log evidence identifies task/spec, exact tested content/input or commit, relevant dependencies and environment/configuration, executor, literal command/invocation/arguments or manual action, expected and observed results/verdict, and applicable exit status; original execution provenance is preserved.
- [ ] No applicable executable check means actual static/manual verification or justified N/A, never an invented test or execution transcript.
- [ ] After each completed step, the report carries feature/task identity, step number/name, state, result, evidence pointer, and next action, using the standardized emoji state; a skipped step states its reason, and a checkpoint or owner-gate return is not step completion. Owner: `knowledge/agent-workflow.md` → `#### Step reporting and transitions`.
- [ ] Work continues to the next ready task within active authorized scope. Blockers name the unmet prerequisite, resolution owner and next action; coordinator/agent-resolvable blockers do not force a user stop. Only user-only decisions/permissions name required user action. Exhausted verified scope ends with `ALL FINISHED` (delivered scope, verification, deferred items, next options), never unrelated work. Owners: `knowledge/agent-workflow.md` → `#### Step reporting and transitions`; `knowledge/agents.md` → `### Message presentation`.
- [ ] Instruction-change evidence identifies original/candidate inputs and complete retained/translated/retired obligation accounting with authority/rationale in the existing Log; prose/examples have normal/adverse scenario walkthrough actions, expected/observed results and outcome evidence. Apply the skill's canonical Implement and verify safeguards, without another tracker or harness.

## Close

- [ ] The requested observable outcome is verified separately from tests, architecture or source-health checks before claiming any task done; the verified outcome is reported.
- [ ] Missing evidence and every failed or pending check/control are reported honestly; pending controls are not represented as satisfied.
- [ ] The next step is stated.
- [ ] A reported failure was reproduced before deciding it already works.
- [ ] Every task is `done` and has a commit reference.
- [ ] A reviewer independent of delivered-change and evidence authorship compares the actual original request/corrections, Specs, delivered content, complete obligation accounting and evidence; valid obligations are retained, translated or retired with explicit authority and rationale.
- [ ] Review checks unresolved requirements, durable evidence at its owner rather than temporary-output-only proof, shared/local ownership, source neutrality, precise invocation provenance, and current PR evidence under the canonical procedure when a PR exists.
- [ ] The existing Log records review identity, scope and result; zero findings remain open before a clean completion claim. Anatomy, a green suite, inherited marks and the author's summary are not semantic completion evidence.
- [ ] Remediation verification is separate from fresh whole-feature semantic acceptance of the current combined candidate; independence holds without demanding different new agents unnecessarily. Identified original/candidate inputs, complete obligation accounting, literal provenance, scenario and outcome evidence are in the existing Log before acceptance. Relevant changes invalidate affected verdicts/evidence; accumulated rounds and the existing review-loop cap survive reviewer changes. Apply the skill's canonical Close safeguards; no extra pause is introduced.
- [ ] `Status` is `closed`, a `Closed:` date is present, and the Log has a `Close:` entry.
- [ ] Completion is presented as `ALL FINISHED` (delivered scope, verification, deferred items, next options) or the eligible compact ready-to-merge message, with findings, blockers, checks, and decisions kept separate, no empty findings table, and no unrelated work selected. Owner: `knowledge/agents.md` → `### Message presentation`.
- [ ] `uv run --frozen python3 .opencode/skills/odd-workflow/scripts/validate_feature.py odd/tasks` exits 0. This is mechanical anatomy only; independent semantic review and acceptance by Cipher 🔓 (Lead Orchestrator) remain required.

## Delivery

- [ ] Closing the feature document is not delivery.
- [ ] Explicit authorization may be standing; local commits are standing-authorized only when the project says so. Push, PR, merge, tag, release, and archive remain separately authorized, a tool-permission denial is never bypassed, and Git execution stays with Herald 📯 (Release Manager).
- [ ] A PR is a reviewable slice, not the accumulated branch.
- [ ] Before a PR is opened, the release-readiness packet is verified and recorded in the existing feature record or PR draft: exact test-plan actions or commands with observed results, every applicable gate status, each task's and the feature's open-or-closed status, excluded or unrelated paths, unverified user-only controls, and each body claim against its evidence. Missing, contradictory or stale evidence blocks PR creation.
- [ ] After every review round, presentation follows the canonical combined rendered chat summary or eligible compact ready message in `knowledge/agents.md` `### PR review findings (adjudication)`, including its accounting and readiness conditions; a raw findings list is not an accepted handoff. Fix-first, deferral authority, refutation evidence, the loop cap, all existing gates and the PR-body evidence schema are unchanged.
- [ ] These release-readiness and finding-action checks apply to docs-only PRs too and introduce no tracker and no new approval.

## Forbidden

- [ ] No second tracker, no Engram mirror, no per-request context injection.
- [ ] No execution transcript in the Log; decisions and evidence only.
