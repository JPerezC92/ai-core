# ODD feature-document checklist

## Create

- [ ] This is authorized non-small state-changing work; read-only and small work require no feature artifact.
- [ ] Copy `.aicore/core/odd/tasks/_template.md`; do not invent the format.
- [ ] Verify creation-date filename/header agreement, immutable prefix, existing-undated and template exceptions against skill `### Create a feature document`.
- [ ] Verify all seven header fields, actual values or justified N/A, literal Runner, Delivery contents and closed-history exception against skill `### Create a feature document`.
- [ ] Check the durable feature owner, shape, derived status and enduring requirement semantics against skill `### Create or update the feature file`.
- [ ] The change reads the affected durable file and records what it changed in it — which requirements it added, reworded or retired, and the verification outcome for each affected requirement — leaving requirements it did not affect alone and not re-verified, and a ticked requirement it found unsatisfied, or that it could not verify and could have affected, loses its tick with the failure or uncertainty and its reason recorded in this change's record, against skill `### Create or update the feature file`.
- [ ] Reject conversation-only Specs. Preserve material requirements and approval context without duplicating full messages.
- [ ] Check selective exact wording, observable acceptance and task rows against skill `### Write meaningful specifications` and `### Create a feature document`; preserve evidenced uncertainty and avoid invented scope.
- [ ] Verify coherent units, focused checks and risk-based rollback against skill `### Delivery planning`.
- [ ] Check material exact wording and resumability against skill `### Create a feature document`; verbatim blocks follow `### Log evidence`.

## Before the first write

- [ ] Apply `.aicore/core/knowledge/agent-workflow.md` `### ODD protocol` before any write (authorize, uncertainty/outcome, classify, artifact-free or bootstrap, authorization gates). Do not restate that protocol here.
- [ ] Feature scope is expressed through Specs/Tasks, not treated as an exclusive file partition; shared-resource overlap names its canonical owner/dependency and follows serialized-writer coordination.
- [ ] After creating the governing document or materially replanning, check execution-review presentation, actual authority/prerequisites and any genuine decision against `AGENTS.md` → Conventions → Decision-only stops. Already-authorized settled work has no automatic creation/replan approval pause; routine Log/evidence updates do not restart review, and creating the document remains the sole bootstrap write.

## Change

- [ ] Check current reassessment/readiness evidence under `.aicore/core/knowledge/agent-workflow.md` `### Scope changes and readiness`; apply skill `### Change a requirement` before affected work resumes.
- [ ] The affected task is reopened; unrelated tasks stay unchanged.

## Implement and verify

- [ ] Verify dependency order, concurrency prerequisites and any applicable authorization gate against workflow `### ODD protocol` step 6.
- [ ] For findings exposing related impact or escaped coverage, apply workflow `#### Finding-triggered impact reassessment and escape tracing`; check the existing Log and the durable source that carries the trace detail against skill `### Implement and verify` and `### Log evidence`, without expanding scope or creating another tracker.
- [ ] Verify step 6's conditional RED/GREEN/refactor evidence or actual exception/proportionate checks; carry the actual runner to workers under skill `### Implement and verify`.
- [ ] Check step 6 task acceptance evidence and accompanying tests/documentation during delivery, not only PR preparation.
- [ ] Check that required evidence exists — the outcome, the verdict, and a pointer identifying the durable source that carries the detail — and that the durable source is a committed artifact, the pull-request body, the record itself, or, for reproducible detail only, a gitignored `output/` artifact; evidence required for future verification or acceptance never rests only in temporary output. Original execution provenance is preserved under whichever durable home holds it.
- [ ] No applicable executable check means actual static/manual verification or justified N/A, never an invented test or execution transcript.
- [ ] Check step reports, skipped reasons and checkpoint-not-completion distinctions against workflow `#### Step reporting and transitions`.
- [ ] Check bounded continuation, blocker ownership/user-only stopping and exhausted-scope reporting against that heading and `.aicore/core/knowledge/agents.md` `### Message presentation`.
- [ ] Instruction-change evidence identifies original/candidate inputs and complete retained/translated/retired obligation accounting with authority/rationale, held in the existing Log, with the accounting decision and outcome in the record and the itemized detail in the durable source that carries it; the complete accounting must exist before acceptance. Prose/examples have normal/adverse scenario walkthrough actions, expected/observed results and outcome evidence. Apply the skill's canonical Implement and verify safeguards, without another tracker or harness.
- [ ] Verify applicable per-rule RED, command-regression and per-spec outcome evidence against workflow `### Behavioral verification and runner selection`; actual runner, execution owners, safety restrictions and justified exceptions remain explicit.

## Close

- [ ] Verify separate task-outcome evidence, honest missing/failed/pending-control reporting, next action and reported-failure reproduction against workflow `### ODD protocol` step 7.
- [ ] Handling of a requested independent review is recorded only when one was requested: the candidate it judged, its findings and their dispositions. When none was requested, no verdict, acceptance statement or reviewer identity is invented and no entry is added merely to record that a review was offered.
- [ ] Every task is `done` and has a commit reference.
- [ ] The delivered work is verified against the record's own `S#` requirements at the commit that carries it; the retained/translated/retired accounting and the evidence invalidated by a change are handled per skill `### Close`; the durable feature file carries the requirement-level account of what the change added, reworded or retired for the requirements it affected, and every ticked requirement the change found unsatisfied, or could not verify and could have affected, is unticked with the failure or uncertainty and its reason recorded in this change's record, against skill `### Create or update the feature file`. The rule text is not restated here.
- [ ] The close checks unresolved requirements, durable evidence at its owner rather than temporary-output-only proof, shared/local ownership, source neutrality, precise invocation provenance, and current PR evidence under the canonical procedure when a PR exists.
- [ ] Zero findings remain open before a clean completion claim, and every applicable required check has passed. Anatomy, a green suite, inherited marks and the author's own summary are not outcome evidence.
- [ ] Remediation evidence is re-verified against the current candidate; the re-run checks and their results are recorded. No separate remediation-acceptance round is created.
- [ ] Close-time evidence reconciliation is complete: every decisive conclusion the change produced is in the record or in the durable owner it belongs to, the record names where it went, and no durable surface cites a temporary artifact as the sole home of evidence required for future verification or acceptance. `### Log evidence` owns the reconciliation mechanics; `.aicore/core/knowledge/agent-workflow.md` → `### Feature document` owns the record-versus-durable-owner boundary.
- [ ] Where a finding-triggered trace exists, verify candidate/finding identities, inspected/assigned/changed evidence, separate origin/escape classifications (including justified unknown), coordinator validation and single-writer retention of decisive classifications, limitations and lessons before disposal against skill `### Log evidence`. The supporting detail stays in the durable source that carries it. Small/read-only work remains artifact-free.
- [ ] `Status` is `closed`, a `Closed:` date is present, and the Log has a `Close:` entry; a record closed on or after `2026-11-24` states exactly one `Disposition`, with `superseded` naming its replacement delivery or explaining obsolescence, and `cancelled` carrying the user authorization for it, per skill `### Close`. A closure carrying user-accepted residual risks names them in a `Residual risks` header line and states that completion is not clean.
- [ ] Completion is presented as `ALL FINISHED` (delivered scope, verification, deferred items, next options) or the eligible compact ready-to-merge message, with findings, blockers, checks, and decisions kept separate, no empty findings table, and no unrelated work selected. Owner: `.aicore/core/knowledge/agents.md` → `### Message presentation`.
- [ ] `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks` exits 0, and `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts <feature-file-or-directory>` exits 0 over the durable feature file — its shape, requirement lines and ticks are checked against `.aicore/core/odd/features/_template.md` and skill `### Create or update the feature file`, and the validator reports the derived status. These are mechanical anatomy only; the completion judgement in skill `### Close` remains required.

## Delivery

- [ ] Closing the feature document is not delivery.
- [ ] Explicit authorization may be standing; local commits are standing-authorized only when the project says so. Push, PR, merge, tag, release, and archive remain separately authorized, a tool-permission denial is never bypassed, and Git execution stays with Herald 📯 (Release Manager).
- [ ] A PR is a reviewable slice, not the accumulated branch.
- [ ] Apply `.aicore/core/knowledge/release.md` before a PR is opened and after every review round. Do not restate that workflow here.

## Forbidden

- [ ] No competing tracker or per-request context injection; resume from the authoritative task and relevant evidence.
- [ ] No execution transcript in the Log; decisions, outcomes, verdicts and pointers only.
