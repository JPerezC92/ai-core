# ODD feature-document checklist

## Create

- [ ] This is authorized non-small state-changing work; read-only and small work require no feature artifact or new evidence template.
- [ ] Copy `odd/tasks/_template.md`; do not invent the format.
- [ ] Verify creation-date filename/header agreement, immutable prefix, existing-undated and template exceptions against skill `### Create a feature document`.
- [ ] Verify all seven header fields, actual values or justified N/A, literal Runner, Delivery contents and closed-history exception against skill `### Create a feature document`.
- [ ] Verify numbered behavioral Specs, exact requirement/literal fidelity, acceptance checks and evidenced uncertainty against skill `### Write meaningful specifications`; no invented scope.
- [ ] Reject anatomically valid but conversation-only Specs such as `approved` or `ok analyze how to achieve it please`. For mixed requirement/approval messages, check the exact requirement plus behavior/check in Specs and the full message/approval context in Log.
- [ ] Verify each entry states one independently verifiable outcome with one action→observable-result acceptance and no generic `works correctly`, and that a multi-part request is split into separate `S#` entries — skill `### Write meaningful specifications`.
- [ ] Verify task IDs, spec links, route/trigger evidence, owner, allowed status, pending/hex commit rules and coherent multi-task/high-risk commit choices against skill `### Create a feature document`.
- [ ] Verify forecast, running authored count, generated-file exclusion, strategy/slices and before-next-commit trigger against skill `### Delivery forecast`; keep the advisory task-size distinction intact.
- [ ] `## Log` starts with `L1` = the original request verbatim; each later user correction is its own dated, verbatim entry, with evidence and rationale in separate entries rather than merged into the correction text.

## Before the first write

- [ ] Apply `knowledge/agent-workflow.md` `### ODD protocol` before any write (authorize, uncertainty/outcome, classify, artifact-free or bootstrap, independent gates). Do not restate that protocol here.
- [ ] Feature scope is expressed through Specs/Tasks, not treated as an exclusive file partition; shared-resource overlap names its canonical owner/dependency and follows serialized-writer coordination.
- [ ] After creating the governing document or materially replanning, the execution-review pause is presented — Issue → Goal → How → Files, the gate, and the decision needed — before implementation; routine Log/evidence updates do not restart it, and creating the document is the sole bootstrap write. Owner: `AGENTS.md` → Conventions.

## Change

- [ ] Check current reassessment/readiness evidence under `knowledge/agent-workflow.md` `### Scope changes and readiness`; apply skill `### Change a requirement` before affected work resumes.
- [ ] The affected task is reopened; unrelated tasks stay unchanged.

## Implement and verify

- [ ] Verify dependency order, concurrency prerequisites and owner gates against workflow `### ODD protocol` step 6 and shared safe-parallel coordination.
- [ ] Verify step 6's conditional RED/GREEN/refactor evidence or actual exception/proportionate checks; carry the actual runner to workers under skill `### Implement and verify`.
- [ ] Check step 6 task acceptance evidence and accompanying tests/documentation during delivery, not only PR preparation.
- [ ] Compact existing-Log evidence identifies task/spec, exact tested content/input or commit, relevant dependencies and environment/configuration, executor, literal command/invocation/arguments or manual action, expected and observed results/verdict, and applicable exit status; original execution provenance is preserved.
- [ ] No applicable executable check means actual static/manual verification or justified N/A, never an invented test or execution transcript.
- [ ] Check step reports, skipped reasons and checkpoint-not-completion distinctions against workflow `#### Step reporting and transitions`.
- [ ] Check bounded continuation, blocker ownership/user-only stopping and exhausted-scope reporting against that heading and `knowledge/agents.md` `### Message presentation`.
- [ ] Instruction-change evidence identifies original/candidate inputs and complete retained/translated/retired obligation accounting with authority/rationale in the existing Log; prose/examples have normal/adverse scenario walkthrough actions, expected/observed results and outcome evidence. Apply the skill's canonical Implement and verify safeguards, without another tracker or harness.

## Close

- [ ] Verify separate task-outcome evidence, honest missing/failed/pending-control reporting, next action and reported-failure reproduction against workflow `### ODD protocol` step 7.
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
- [ ] Apply `knowledge/release.md` before a PR is opened and after every review round. Do not restate that workflow here.

## Forbidden

- [ ] No second tracker, no Engram mirror, no per-request context injection.
- [ ] No execution transcript in the Log; decisions and evidence only.
