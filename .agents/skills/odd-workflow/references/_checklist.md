# ODD feature-document checklist

## Create

- [ ] This is authorized non-small state-changing work; read-only and small work require no feature artifact.
- [ ] Copy `odd/tasks/_template.md`; do not invent the format.
- [ ] Verify creation-date filename/header agreement, immutable prefix, existing-undated and template exceptions against skill `### Create a feature document`.
- [ ] Verify all seven header fields, actual values or justified N/A, literal Runner, Delivery contents and closed-history exception against skill `### Create a feature document`.
- [ ] The feature's durable file exists at `odd/features/<feature>.md`, named for the capability it describes and never dated, and was created from `odd/features/_template.md` — the only feature-file template — the first time the feature was worked; verify its shape (a title, one paragraph saying what the feature is, one status line, the requirement list), that its status follows the ticks, and that it lists no change record and holds no work-in-progress state, and that every requirement states only what must remain true, appending no pointer to implementation or history — no file path, heading reference, line number, command, or record of when or how it was checked — and citing no change record, its Log, or a line in one, while a specific path, component or artifact that is itself part of the required behavior is named as the behavior it guarantees rather than as evidence that it exists, with the evidence that a requirement was checked belonging to the change record that affected it, against skill `### Create or update the feature file`.
- [ ] The change reads the affected durable file and records what it changed in it — which requirements it added, reworded or retired, and the verification outcome for each affected requirement — leaving requirements it did not affect alone and not re-verified, and a ticked requirement it found unsatisfied, or that it could not verify and could have affected, loses its tick with the failure or uncertainty and its reason recorded in this change's record, against skill `### Create or update the feature file`.
- [ ] Reject anatomically valid but conversation-only Specs such as `approved` or `ok analyze how to achieve it please`. For mixed requirement/approval messages, check the exact requirement plus behavior/check in Specs and the full message/approval context in Log.
- [ ] The record's requirement wording, acceptance clauses and task rows check the verbatim-requirement, one-action acceptance and task-row rules against skill `### Write meaningful specifications` and `### Create a feature document`; evidenced uncertainty and no invented scope still apply, and the rule text is not restated here.
- [ ] Verify forecast, running authored count, generated-file exclusion, strategy/slices and before-next-commit trigger against skill `### Delivery forecast`; keep the advisory task-size distinction intact.
- [ ] `## Log` starts with `L1` = the original request verbatim; each later user correction is its own dated, verbatim entry, and its evidence and rationale may accompany it in that entry.

## Before the first write

- [ ] Apply `knowledge/agent-workflow.md` `### ODD protocol` before any write (authorize, uncertainty/outcome, classify, artifact-free or bootstrap, independent gates). Do not restate that protocol here.
- [ ] Feature scope is expressed through Specs/Tasks, not treated as an exclusive file partition; shared-resource overlap names its canonical owner/dependency and follows serialized-writer coordination.
- [ ] After creating the governing document or materially replanning, check execution-review presentation, actual authority/prerequisites and any genuine decision against `AGENTS.md` → Conventions → Decision-only stops. Already-authorized settled work has no automatic creation/replan approval pause; routine Log/evidence updates do not restart review, and creating the document remains the sole bootstrap write.
- [ ] After bootstrap, the existing Log identifies the project/feature, locator, backend ID and exact fully verified record revision, or explicit pending recovery, under `knowledge/agent-workflow.md` → `### Full feature mirror and resume`; backend-write restrictions remain binding and no summary-only copy is counted as synchronized.

## Change

- [ ] Check current reassessment/readiness evidence under `knowledge/agent-workflow.md` `### Scope changes and readiness`; apply skill `### Change a requirement` before affected work resumes.
- [ ] The affected task is reopened; unrelated tasks stay unchanged.

## Implement and verify

- [ ] Verify dependency order, concurrency prerequisites and owner gates against workflow `### ODD protocol` step 6 and shared safe-parallel coordination.
- [ ] For findings exposing related impact or escaped coverage, apply workflow `#### Finding-triggered impact reassessment and escape tracing`; check the existing Log and the durable source that carries the trace detail against skill `### Implement and verify` and `### Log evidence`, without expanding scope or creating another tracker.
- [ ] Verify step 6's conditional RED/GREEN/refactor evidence or actual exception/proportionate checks; carry the actual runner to workers under skill `### Implement and verify`.
- [ ] Check step 6 task acceptance evidence and accompanying tests/documentation during delivery, not only PR preparation.
- [ ] Check that required evidence exists — the outcome, the verdict, and a pointer identifying the durable source that carries the detail — and that the durable source is a committed artifact, the pull-request body, the record itself, or, for reproducible detail only, a gitignored `output/` artifact; evidence required for future verification or acceptance never rests only in temporary output. Original execution provenance is preserved under whichever durable home holds it.
- [ ] No applicable executable check means actual static/manual verification or justified N/A, never an invented test or execution transcript.
- [ ] Check step reports, skipped reasons and checkpoint-not-completion distinctions against workflow `#### Step reporting and transitions`.
- [ ] Check bounded continuation, blocker ownership/user-only stopping and exhausted-scope reporting against that heading and `knowledge/agents.md` `### Message presentation`.
- [ ] Instruction-change evidence identifies original/candidate inputs and complete retained/translated/retired obligation accounting with authority/rationale, held in the existing Log, with the accounting decision and outcome in the record and the itemized detail in the durable source that carries it; the complete accounting must exist before acceptance. Prose/examples have normal/adverse scenario walkthrough actions, expected/observed results and outcome evidence. Apply the skill's canonical Implement and verify safeguards, without another tracker or harness.
- [ ] Verify applicable per-rule RED, command-regression and per-spec outcome evidence against workflow `### Behavioral verification and runner selection`; actual runner, execution owners, safety restrictions and justified exceptions remain explicit.
- [ ] At material record changes, work-unit commits and resume, check the exact verified revision or pending recovery in the existing Log against workflow `### Full feature mirror and resume`; conflict/unavailability is never reported as successful synchronization.

## Close

- [ ] Verify separate task-outcome evidence, honest missing/failed/pending-control reporting, next action and reported-failure reproduction against workflow `### ODD protocol` step 7.
- [ ] Independent verification handoff covers the whole feature including Log and returns per-spec verdicts for authorized examples under workflow `### Behavioral verification and runner selection`; this does not substitute for whole-feature semantic acceptance.
- [ ] Every task is `done` and has a commit reference.
- [ ] The independent reviewer's per-requirement verdict, the retained/translated/retired accounting, the recorded evidence and the voiding of evidence invalidated by a change are verified against skill `### Close`; the durable feature file carries the requirement-level account of what the change added, reworded or retired for the requirements it affected, and every ticked requirement the change found unsatisfied, or could not verify and could have affected, is unticked with the failure or uncertainty and its reason recorded in this change's record, against skill `### Create or update the feature file`. The rule text is not restated here.
- [ ] Review checks unresolved requirements, durable evidence at its owner rather than temporary-output-only proof, shared/local ownership, source neutrality, precise invocation provenance, and current PR evidence under the canonical procedure when a PR exists.
- [ ] The existing Log records review identity, scope and result; zero findings remain open before a clean completion claim. Anatomy, a green suite, inherited marks and the author's summary are not semantic completion evidence.
- [ ] Remediation verification is separate from fresh whole-feature semantic acceptance of the current combined candidate; independence holds without demanding different new agents unnecessarily. Accumulated rounds and the existing review-loop cap survive reviewer changes. Apply the skill's canonical Close safeguards; no extra pause is introduced.
- [ ] Close-time evidence reconciliation is complete: every decisive conclusion the change produced is in the record or in the durable owner it belongs to, the record names where it went, and no durable surface cites a temporary artifact as the sole home of evidence required for future verification or acceptance. `### Log evidence` owns the reconciliation mechanics; `knowledge/agent-workflow.md` → `### Feature document` owns the record-versus-durable-owner boundary.
- [ ] Where a finding-triggered trace exists, verify candidate/finding identities, inspected/assigned/changed evidence, separate origin/escape classifications (including justified unknown), coordinator validation and single-writer retention of decisive classifications, limitations and lessons before disposal against skill `### Log evidence`. The supporting detail stays in the durable source that carries it. Small/read-only work remains artifact-free.
- [ ] `Status` is `closed`, a `Closed:` date is present, and the Log has a `Close:` entry.
- [ ] Closure mirror refresh/readback or explicit pending recovery is evidenced under workflow `### Full feature mirror and resume`; source-policy alignment is not runtime-adoption proof.
- [ ] Completion is presented as `ALL FINISHED` (delivered scope, verification, deferred items, next options) or the eligible compact ready-to-merge message, with findings, blockers, checks, and decisions kept separate, no empty findings table, and no unrelated work selected. Owner: `knowledge/agents.md` → `### Message presentation`.
- [ ] `uv run --frozen python3 .agents/skills/odd-workflow/scripts/validate_feature.py odd/tasks` exits 0, and `uv run --frozen python3 .agents/skills/odd-workflow/scripts/validate_feature_file.py <feature-file-or-directory>` exits 0 over the durable feature file — its shape, requirement lines and ticks are checked against `odd/features/_template.md` and skill `### Create or update the feature file`, and the validator reports the derived status. These are mechanical anatomy only; independent semantic review and acceptance by Cipher 🔓 (Lead Orchestrator) remain required.

## Delivery

- [ ] Closing the feature document is not delivery.
- [ ] Explicit authorization may be standing; local commits are standing-authorized only when the project says so. Push, PR, merge, tag, release, and archive remain separately authorized, a tool-permission denial is never bypassed, and Git execution stays with Herald 📯 (Release Manager).
- [ ] A PR is a reviewable slice, not the accumulated branch.
- [ ] Apply `knowledge/release.md` before a PR is opened and after every review round. Do not restate that workflow here.

## Forbidden

- [ ] No competing tracker or per-request context injection; a subordinate full feature mirror follows workflow `### Full feature mirror and resume`, never independent intent/status authority.
- [ ] No execution transcript in the Log; decisions, outcomes, verdicts and pointers only.
