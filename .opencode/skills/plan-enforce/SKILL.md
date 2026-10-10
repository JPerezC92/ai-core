---
name: plan-enforce
description: Enforce plan-first discipline for non-trivial tasks. Creates or resumes a subfolder plan artifact in plans/ before code-writing work, and verifies a user-confirmed PR merge before branch cleanup. Use when the user asks to plan work, types /plan, Cipher is about to dispatch Forge for implementation, or a user confirms a PR merge.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.17.0
---

## Project extensions

### Protected upstream base ref

This project's protected upstream base ref is `origin/main` — remote `origin`, branch `main`. Mandatory core denotes it with `$BASE`, composed as `$BASE="${BASE_REMOTE}/${BASE_BRANCH}"`; substituting this project's values (`$BASE_REMOTE=origin`, `$BASE_BRANCH=main`) keeps every command identical to `origin/main`.

### Reviewed whole-suite command

This project's reviewed whole-suite test command is `uv run --frozen --group dev pytest -q`.

### Test file pattern and harness config

This project's Python test-file pattern is `test_*.py`. This project's root opencode config is `opencode.jsonc`; Crucible 🔥 (Test Architect) runner permissions live under `agent.crucible.permission`.

### Plan validator script

This project's plan validator script is `uv run --frozen python3 .opencode/skills/plan-enforce/scripts/validate_plan.py`. Every Python invocation in this skill runs through the project's virtual environment.

### Plan, story, and checklist templates

This project's plan-enforce templates and references:

- Programming plan template: `references/_template-programming.md`
- Base plan template: `references/_template.md`
- Phase template: `references/_phase-template.md`
- User-story template: `references/_template-user-story.md`
- Consistency checklist: `references/_consistency-checklist.md`

## Mandatory core

### What I do

Create or resume a plan before non-trivial implementation work, then enforce its scope, phase gates, and pre-release completion lifecycle.

### When to use me

- User types `/plan` or asks to create, resume, or show a plan.
- Cipher 🔓 (Lead Orchestrator) is about to dispatch Forge 🔨 (Implementer).
- A current task changes scope or requires a new implementation phase.
- A user confirms a PR merge and the merged branch needs verification before cleanup.

### Arguments

From the user's request, extract:

- **task description** — concise description of the intended work.

If no task description and no active plan are available, collect the description with the `question` tool.

#### Argument collection form

| name | type | validation | trigger |
|---|---|---|---|
| `task_description` | text | non-empty | no active plan and no task description |

Use one `question` call. The first option is the parsed value when one is available; do not add a manual “Other” option.

### Base ref variable

`$BASE` denotes the destination's protected upstream base ref; `$BASE_REMOTE` and `$BASE_BRANCH` are its remote and branch components, with `$BASE="${BASE_REMOTE}/${BASE_BRANCH}"`. This project's concrete values are in Project extensions (see **Protected upstream base ref**).

### Stash safety gate

This gate has two ordered parts: an initial read-only inventory and a post-scope collision check. It runs before new-plan creation, plan resumption, archive work, and every Forge 🔨 (Implementer) dispatch. The gate never mutates the caller repository's stash or refs.

#### Initial read-only inventory

Run this inventory before selecting a plan, deriving a new plan, or writing a plan file:

| Command | Purpose |
|---|---|
| `git ls-remote "$BASE_REMOTE" "refs/heads/$BASE_BRANCH"` | Capture `LIVE_MAIN_SHA`. Fail closed if unavailable. |
| `git rev-parse refs/stash` | Capture `STASH_FINGERPRINT`; an absent ref means there is no stash to inspect. |
| `git stash list` | Enumerate stash selectors and subjects. |
| `git stash show -u <selector>` | List each stash's tracked, deleted, and untracked paths. |
| `git rev-parse <stash-sha>^1` | Resolve the selected stash's base commit. |
| `git merge-base --is-ancestor <base-sha> <live-main-sha>` | Test whether the stash base is behind live main. |
| `git merge-base --is-ancestor <live-main-sha> <base-sha>` | Test whether the stash base is ahead of live main. |

For each selector, resolve its full object SHA and base SHA. Classify it in this exact order:

1. **current** — base SHA exactly equals `LIVE_MAIN_SHA`.
2. **stale** — base SHA is an ancestor of `LIVE_MAIN_SHA`.
3. **ahead** — `LIVE_MAIN_SHA` is an ancestor of the base SHA.
4. **diverged** — neither SHA is an ancestor of the other.

Malformed selectors, missing objects, unparseable output, or a changed fingerprint from the plan's recorded fingerprint fail closed. Caller-repository stash mutation is forbidden. The permission policy denies direct destructive stash/ref/reflog/pruning pathways; this is a targeted policy, not an exhaustive shell sandbox.

#### Derive the write/delete manifest

Derive the manifest before the collision check:

- **New plan:** derive the complete write/delete manifest in memory from the intended task and phase design before writing any plan or phase file.
- **Existing subfolder plan:** derive the manifest from every phase runbook's `## Writes` block.
- **Existing single-file plan:** derive the manifest from its explicit write/delete instructions only.

Read-only inputs are never manifest entries. The manifest must be complete before a new plan file is created or Forge 🔨 (Implementer) is dispatched.

#### Post-scope collision check

Intersect every stashed changed path from the initial inventory with the derived write/delete manifest:

- Any intersection is `PLANNED_PATH_OVERLAP`: fail closed before plan-file creation or Forge 🔨 (Implementer) dispatch.
- No intersection permits the plan flow to continue.
- A stale, ahead, or diverged non-overlapping stash is a user-gated reconciliation candidate; current non-overlapping stashes are reported and retained.

#### Stash lifecycle

Park work via `git stash push` / `git stash save` — git never erases existing stash entries on push; stash entries use stack semantics. Recover via `git stash apply <ref>` — non-destructive, the entry survives as a durable backup. Erasure (`pop`, `drop`, `clear`, `update-ref -d refs/stash`) is denied to model agents and is user-only, run manually in the user's terminal.

#### Stash status query

To answer "are there unapplied stashes?" mechanically, run these three read-only commands:

| Command | Purpose |
|---|---|
| `git stash list` | Enumerate stash selectors. |
| `git stash show -u <selector> --name-only` | List tracked, deleted, and untracked paths per stash. |
| `git status --porcelain` | List current worktree paths. |

Verdict: ALL stash paths present in worktree status = applied; any missing = unapplied. If the comparison is inconclusive (worktree diverged after apply), say "cannot confirm mechanically" — never guess.

### Check for active plan

1. Run the initial inventory.
2. Scan `plans/*.md` (excluding `.completed/`) and `plans/*/plan.md`.
3. Read candidate plan files and select those with `Status: active`.
4. If one active plan exists, read it and its `phase-*.md` siblings, derive its manifest, and run the post-scope collision check before showing the plan or dispatching Forge 🔨 (Implementer).
5. If no active plan exists, continue to **Create new plan**. If multiple exist, stop and ask the user to select one.

An archived plan is never resumed directly from `plans/.completed/`. Restore it to `plans/`, set `Status: active`, and append `Reopened: YYYY-MM-DD HH:MM` before resuming.

### Goal lifecycle

Goals are numbered `G1..Gn`, detected from the task description, confirmed with the user before any file creation, persisted as `## Goals` checkboxes in `plan.md`, watched for drift across the plan's life, and resumed at completion.

#### Detect

Extract the goals from the task description before writing any plan file:

1. Number them `G1`, `G2`, … in order of importance.
2. State each goal as what must be true when the plan is done — an observable condition, not an activity.
3. Programming goals (see **Template selection**) additionally carry a `Done when:` criterion (see Persist).
4. More than 5 goals triggers the soft goal-bloat flag (see **Simplicity discipline**) — report it in the confirmation gate; do not silently proceed.
5. A goal whose done-condition references another document's state (a debt-register entry, a rule file, a checklist) MUST be drafted from that document's current text, read fresh at plan-creation — never from memory or a prior plan's phrasing. Quote the governing text in the goal or its verification line. A done-condition invented from recall inherits the recall error and every downstream gate verifies the assumption instead of the source (observed 2026-08-30: a "mark resolved in register" goal contradicted the register's own retirement rule).

#### Present (pre-file gate)

Before invoking the `question` tool, send one regular Markdown message that visibly separates the decision inputs:

1. Under `**Goals**`, render every detected `G1..Gn` goal as its own Markdown bullet with its full observable condition.
2. Under `**Plan classification**`, render the detected plan type, user-story scope (create, update, or skipped with reason), and goal-bloat status (`none` or the triggered soft flag).
3. Do not place the full goal list, plan type, user-story scope, or goal-bloat detail in the `question` text. The user must be able to scan them outside the compact question control.

#### Confirm (pre-file gate)

Before creating ANY plan file, run exactly one short `question` call that asks whether to proceed with or revise the already displayed goals and classification. The answer confirms, in a single round:

1. The detected goal list — `G1..Gn` with their conditions.
2. The detected plan type (see **Template selection**).
3. The soft goal-bloat flag, when triggered.
4. The user-story scope, when the plan is programming OR changes feature-visible behavior (see **User-story scope**) — confirm whether a story must be created/updated.

Do not create `plan.md` or any `phase-*.md` until the user confirms all four. Skipping the Markdown presentation, adding a second question round, or paraphrasing any part of the confirmation is a violation.

#### Persist

Write the confirmed goals into `plan.md` under `## Goals`:

- One checkbox per goal: `- ⬜ **G1:** <goal>`
- Each goal lists Issue, How, and Files. `## Context` remains the overall issue.
- Programming plans use the programming plan template (see Project extensions), where every goal also carries a `Done when:` criterion — the observable condition that proves the goal is met.
- After confirmation, goals are never renumbered or reworded silently — changes go through Drift watch.

#### Drift watch

Watch for goal drift on every phase close, every scope change, and every collateral-fix verification. When the work no longer matches the confirmed goals — or a goal must be added, removed, or reworded:

1. **Stop** — do not continue editing plan files.
2. **Notify** the user with evidence: which goal drifted, what the current work does instead, and what the plan file says.
3. **Wait** for the user's call — the user decides whether to update the goals, adjust the work, or abort. Never self-approve a goal change.
4. On user approval, update the `## Goals` block and append a dated line to `## Resolved decisions` recording the change.

#### Acceptance-criterion reconciliation (fail-closed)

A user story a plan touches may not carry undetermined criteria past plan completion. When the plan's work is done, every acceptance criterion in every story this plan created or updated must be dispositioned:

- `✅` — the criterion is established by verified evidence (a completed goal's `Done when:`, a passing verify command, or a recorded outcome). No fulfilled criterion may remain `⬜`.
- `❌` — the criterion is explicitly known to be unmet. A `❌` blocks plan completion and archival until the criterion is satisfied or removed.
- Out-of-scope work is removed from the story's acceptance criteria (not left unchecked) and recorded as a dated change-log line, optionally pointing at a follow-up story.

There is no "left as pending" state for a criterion in a touched story: an `⬜` after a touching plan completes is a stale-story defect. Release events (PR opened/reviewed/merged) are release history, not feature acceptance criteria; a feature criterion may state the release policy (e.g. "merge remains user-only") but never a specific PR/review/merge event.

#### Resume (completion)

When the plan's work is done and its audits have passed — before the release PR is built:

- Confirm `## Audit` records an independent auditor's `[PASS]` with `Auditor`, `Findings`, and `Date` (see **Independent audit gate**); `[PENDING]`, `[FAIL]`, or a missing audit blocks completion.
- Evaluate completion evidence as a layered matrix on the current snapshot: code architecture, test architecture, test execution, and model/guidance verdicts — each with its scope and verdict. A passing execution result never stands in for a required architecture verdict, and a missing or adverse layer blocks completion. A planning-readiness audit is never reused as the completion audit. Adjudicate any adverse finding before marking a goal or criterion complete, writing `## Outcome`, or archiving.
- Run acceptance-criterion reconciliation (see **Acceptance-criterion reconciliation**) over every touched story; block `## Outcome` and the archive move until no `⬜` or `❌` criterion remains — each is `✅` or removed as out-of-scope.
- Present the goals resume in chat: one line per goal, `✅` when met, `❌` when not, each with a 1-line evidence note.
- Write `## Outcome` into `plan.md` — what the plan produced, per goal — BEFORE moving the plan to `plans/.completed/`.
- Set `Status: completed`, append `Completed: YYYY-MM-DD HH:MM`, and move the plan to `plans/.completed/` (folder or file per layout). All of this happens pre-release; the merged PR number or merge SHA may be appended to the local archive copy afterwards as free metadata.
- Filesystem-verify the archive after the move: confirm every expected file exists under `plans/.completed/<plan>/` AND the active copy is gone from `plans/`. A `mv` that reports success can still leave the active copy in place (observed 2026-08-24); the filesystem, not the command's silence, is the evidence.
- A plan archived without `## Outcome` is a lifecycle violation: restore it, write the section, then archive again.

### Simplicity discipline

Challenge every artifact for removal or merger before rendering. Every dispatch-table phase traces to ≥1 goal; remove or merge untraced phases. Remove files, phases, and steps not demanded by a goal or explicit request. Programming plans record cuts/mergers and reasons in `## Design decisions`. More than 5 goals or any non-single-observable goal triggers a soft bloat flag at confirmation; the user chooses whether to trim, split, or accept it.

Admit a finding only with its confirmed goal, governing clause, responsible actor and shipped path (not a helper/fixture), expected-versus-observed behavior, scope, reproduction/static fact, literal severity output, and keep/fix/reject-scope decision. Classify it as a requirement defect, documentation drift, or supplemental concern; reject speculative blockers and judge the flow once, not through unbounded helpers or test matrices. When behavior is replaced, superseded, or newly wired, search for and remove dead code/stale wiring and record the sweep at completion; no validated-but-unread field, dead symbol, or stale mapping survives.

### Dispatch bundle contract

Every subagent dispatch prompt MUST contain verbatim: (1) the plan Subject; (2) the full `## Goals` block, checkboxes included; (3) the full phase runbook; and (4) each prior-phase Output value consumed by that phase's Reads. "See phase-01 output," summarized goals, or paraphrased phase content do not qualify. Verify all four before dispatch; if anything is missing, rebuild and do not dispatch.

Include verbatim the question prohibition and stop-report contract: never invoke the user-facing `question` tool. If required input, instruction, or evidence is missing, halt and report to Cipher 🔓 (Lead Orchestrator) the task as received, exact missing item, inspected sources, bounded options, and recommended default. Never guess, assume, silently continue, or stall.

### Template selection

Choose and confirm the template at the goals gate, before creating files. Detect programming plans by paths, not subject: any code write under application source, backend tooling, `scripts/`, `.opencode/skills/**/scripts/`, or ticket tooling qualifies. Use the programming template (goals with `Done when:`, Current state, Behavior change, Design decisions, per-phase Goals and Verify commands); otherwise use the base template. Confirm the type in the same `question` call as the goals; never choose silently.

### Verification command executors

Every phase runbook has one non-empty `## Verify commands` Markdown table with exactly two columns, `Executor` and `Command`; each command has exactly one non-empty executor. The static validator checks table shape and traceability only, never permission models. Phase review separately verifies that each executor has the role and tool authority to run the command.

| Executor | Command |
|---|---|
| <Name Emoji (Role)> | `<shell command>` |

#### Non-TypeScript test files

Crucible 🔥 (Test Architect) executes each declared approved test command; Forge 🔨 (Implementer) writes tests; Bastion 🧱 (Backend & Scripts Architect) audits applicable Python implementation. A plan editing a Python test in reviewed discovery areas must list the reviewed whole-suite command (Project extensions), obtain Bastion 🧱 (Backend & Scripts Architect) `[PASS]` on applicable implementation edits, then dispatch Crucible 🔥 (Test Architect) to return `[PASS]` or `[FAIL]`. `[UNCERTAIN]` is not acceptable. Cipher 🔓 (Lead Orchestrator) checks the exact command before dispatch; runner permissions are in the root opencode config under `agent.crucible.permission` and gate command text, not sandbox execution. Existing TypeScript / Atrium 🏛️ (Frontend Architect) and Crucible 🔥 (Test Architect) gates remain unchanged.

### User stories

Stories are the durable per-feature definitions (`user-stories/<feature-slug>.md`); plans are temporal. Read `user-stories/index.md` first, filter by epic/affected areas, then read candidate bodies. Before creating any story, Cipher 🔓 (Lead Orchestrator) presents evidence-backed UPDATE / rename / CREATE choices and waits for explicit user choice via `question`; CREATE without that choice or Cipher's own say-so is forbidden. Create only for a feature without a story after explicit CREATE. Update the affected story with the plan work to reflect the current feature and append a dated `## Change log` entry. On overlap, contradiction, or extension, run the collision gate. Stories are never archived/deleted with plans. Cite each touched story under `plan.md` → `## Critical files / tools`; trace each goal to a story acceptance criterion, or to plan Context/Goals when stories are skipped.

### User-story scope

Programming plans ALWAYS carry a story for each feature touched by writes under application source, backend tooling, `scripts/`, `.opencode/skills/**/scripts/`, or ticket tooling. At the goals gate, flag non-programming changes to feature-visible behavior and confirm whether a story is needed. Pure docs/process/tooling plans skip stories; `## Context` / `## Goals` record the work.

### User-story collision gate

Read the index, filter by epic/affected areas, read candidate bodies, and check for overlap (same scenario), contradiction, or extension (superseding/broadening a feature). On any collision, stop before creating a plan; report the existing persona/goal/scenario and corresponding intended statements, then ask the user how to proceed. Before creating a story, present the filtered choices UPDATE / rename / CREATE with evidence and wait for explicit `question`-tool choice. Record the decision in the affected story's bounded `## Resolved decisions`, replacing superseded entries. Re-run this gate when scope adds a feature.

### Story hygiene

Stories define current features, not work history. Every acceptance criterion and Goal `Done when:` states an observable condition and cites the proving surface; no plan-only goal or temporal `plans/`/`output/` dependency is allowed, except a genuine feature input. Cite evidence by exact command+verdict or durable commit SHA, never volatile test counts; cite section/symbol rather than version unless version is the requirement, never a version this plan bumps, and replace `file:line` with section/symbol.

Keep at most 5 recent one-line `## Change log` entries (`<date> — <plan-slug>: <feature change>`) plus `before <date> — earlier history: see git history for this file` when rolling up. Exclude process narration. `## Resolved decisions` contains only current governing decisions with rationale; replace superseded and remove execution/scheduling decisions. Git history is permanent. Sentinel 🛡️ (Quality Guardian) audits these rules; the validator does not.

### Create new plan

1. Run the initial inventory; choose subfolder layout unless there is one owner, one edited file, no handoff/external mutation, and ≤30 instruction lines.
2. Derive slug, phases, and complete write/delete manifest in memory. Detect numbered `G1..Gn` observable goals (see **Goal lifecycle**).
3. Present goals and classification in Markdown, then make one short confirming `question` call before any file creation. Select the path-detected template and confirm its type with the goals.
4. Run the user-story gate: read/filter `user-stories/index.md`, review candidate bodies, and decide UPDATE / rename / CREATE / COLLIDE per feature. Wait for explicit story choice before creating; stop before plan creation on collision. Record skipped stories in Context.
5. Run the post-scope collision check; stop on overlap.
6. Create `plans/<task-slug>-YYYYMMDD/plan.md` and one phase-template `phase-NN-<owner>.md` per phase. Record the full manifest; `Action`/`Path` rows must equal the union of phase `**Writes:**` paths.
7. Complete each phase's Owner, Pre, Reads, Writes, Steps, Output, Verify commands, Gate, and Abort conditions; no `TBD` in Steps/Output/Gate/Abort. Add one verification checkbox per phase output and trace every checkbox.
8. Run the post-write self-verification loop on every written file. After it passes, send the execution-review message and stop. Do not dispatch Forge 🔨 (Implementer) in this turn or treat `ExitPlanMode` as implementation authorization.

### Execution-review message

After written plans pass self-verification, Cipher 🔓 (Lead Orchestrator) sends one readable final message and stops. Use prose per goal, in order: Issue, Goal, How, Files; `plan.md` uses the same layout and `## Context` states the overall issue. An optional file table follows, never replaces, the prose; dense dumps/table-only briefs fail. Do not dispatch Forge 🔨 (Implementer) in this turn or ask corrective, release, or scope questions without the file list. Forge 🔨 (Implementer) may start only on a later user turn explicitly authorizing execution, after independent-audit `[PASS]` and the stash gate.

### Post-write self-verification loop

Run after every plan/phase/story/index write and every Forge 🔨 (Implementer) dispatch that mutates plan artifacts; repeat until clean:

1. Re-read each written `plan.md`, phase file, story, and index.
2. Mechanical pass: active subfolder plans touching stories/index use `<plan-dir> --stories user-stories`; no-story plans use `<plan-dir>`; single-file plans use `<plan.md> --single-file`. Fix validator findings for Status/Completed, required sections and labels, executor-command tables, placeholders, index mirroring, goal trace, manifest equality, verification parity, and completed-plan audit gate.
3. Analysis pass against the consistency checklist: evidence-match confirmed goals; each goal has Issue/How/Files; phase-to-goal and phase-file links exist; verification checkboxes trace to outputs; phase Writes equal the manifest; story title/status mirror the index; no touched story has `⬜` criteria at completion. Never invent a value; stop and ask.
4. Repeat to zero findings and report `self-verification passes: N`. After 3 iterations or the same unchanged violation twice, stop-and-ask (S-07).

The validator catches repetitive mechanical drift; the analysis pass owns semantic correctness.

#### Independent audit gate

Never report readiness or dispatch Forge 🔨 (Implementer) on the writer's own word. Before either, dispatch an independent checklist audit (see Project extensions): Sentinel 🛡️ (Quality Guardian) by default, Vault 🔐 (Catalog Steward) for catalog-heavy plans. Record `Auditor`, `Verdict`, `Findings`, and `Date` under `## Audit`; verdict is `[PENDING]`, `[PASS]`, or `[FAIL]`. Readiness/dispatch requires `[PASS]`, non-empty auditor, and date. If unavailable, remain not-ready; a substitute requires explicit user authorization recorded in the audit. Never self-audit, invent a verdict, or downgrade `[FAIL]`. Planning and completion audits are distinct: completion evaluates the final candidate and is required before `## Outcome`, goal checkmarks, and archive; planning `[PASS]` or execution alone cannot substitute.

### All-changes disposition

For an all-pending-changes analysis, inspect and disposition every nonignored modified/deleted/untracked path as evidence-based `ship`, `fix`, or `drop` before any scope question. Manifest absence or pre-existence does not prove unrelatedness. Do not defer while any inspected path lacks disposition or claim beyond reviewed scope.

### Plan lifecycle rules

| Event | Required action |
|---|---|
| Any plan/phase/story/index file write | Run the post-write self-verification loop (mechanical + analysis) until clean. |
| Plan files written | Send the execution-review message and stop. Do not dispatch Forge 🔨 (Implementer) in the plan-creation turn. |
| Phase completes | Mark its verification item complete in `plan.md`. |
| Scope changes | Stop; notify the user with evidence of the drift and wait for their call; then update `## Goals` and append a dated line to `## Resolved decisions`; re-derive the manifest and re-run the collision check. |
| Forge 🔨 (Implementer) dispatch | Dispatch only on a later user turn that explicitly authorizes execution after the execution-review message. Run both stash-gate parts, require an active plan, and require a recorded independent-audit `[PASS]` in `## Audit` before dispatch. |
| Plan ready to report or resume | Require a recorded independent-audit `[PASS]` with auditor and date; an unavailable auditor leaves the plan not-ready (fail-closed). |
| Audits pass, release PR requested | Present the goals resume in chat (`✅`/`❌` per goal with evidence), write `## Outcome`, set `Status: completed`, append `Completed: YYYY-MM-DD HH:MM`, and move the plan to `plans/.completed/` — all BEFORE the release PR is built. |
| Plan was tracked mid-work | Stage the plan-file deletions into the completing PR; never stage a completed plan's content. |
| PR review demands rework | Restore the plan folder from `plans/.completed/` per the reopen rule, resume, re-complete pre-release, and re-stage the deletions. |
| Plan cancelled | Complete it as cancelled: `## Outcome` records the cancellation; a tracked cancelled plan retires through the next PR's deletions. |
| User confirms PR merge | Run both stash-gate parts. Confirm the PR state is `MERGED` via `gh pr view "$PR_NUMBER" --json state,mergeCommit,headRefName,headRefOid`, then `git fetch "$BASE_REMOTE" "$BASE_BRANCH"` and pin the immutable PR head `HEAD_REF_OID`. Require `git rev-parse "$BRANCH"` to equal `HEAD_REF_OID` (halt on mismatch). If `mergeCommit` is non-empty, require `git merge-base --is-ancestor "$MERGE_COMMIT" "$BASE"` to succeed. If `git merge-base --is-ancestor "$BRANCH" "$BASE"` succeeds (merge-commit or fast-forward), branch-tip ancestry proves the merge and `git branch -d` applies. Otherwise (squash or rebase merge) prove content parity on the immutable head: `MERGE_BASE="$(git merge-base "$BASE" "$HEAD_REF_OID")"`, then `git diff --name-only -z "$MERGE_BASE" "$HEAD_REF_OID" > "$PATHS_FILE"` while checking its status (an empty result is allowed), then load the NUL-delimited paths into `CHANGED_PATHS` with a read loop; the proof is `git diff --quiet --exit-code "$BASE" "$HEAD_REF_OID" -- "${CHANGED_PATHS[@]}"` exiting 0. Any metadata, fetch, head-mismatch, merge-base, extraction, ancestry, or diff error blocks deletion; only after that proof is `git branch -D` authorized. Never `-D` without a `MERGED` state plus a parity proof. Then fast-forward the local `$BASE_BRANCH` branch and delete the local branch plus the remote branch when it still exists. No post-merge archive step exists; user-only merge authority is unchanged. |

Git tracks only incomplete plans. Stage plan artifacts only while their plan is incomplete; a plan tracked mid-work leaves git through file deletions staged in its own completing PR; a single-session plan is never committed anywhere. Plans remain active through implementation and audit — completion and archive happen pre-release. Never delete a plan, create an archive commit, invoke a merge command, or mutate a stash during archival.

### Documentation discipline

Published documents, durable criteria, and Goal `Done when:` must not cite temporal `plans/` or `output/` paths; cite a commit SHA, PR number, or ticket ID instead (see **Story hygiene**).

### Examples

**New multi-phase task:** derive all phase writes and check collisions before creating a subfolder plan. **Existing plan:** compare every phase `## Writes` block with the inventory before Forge 🔨 (Implementer) dispatch. **Stale non-overlapping stash:** offer user-run `git stash apply` or leave it untouched; never erase/replay it. **Post-merge cleanup:** use the confirmed `$PR_NUMBER`/`$BRANCH` and the lifecycle row's derived variables/proof.

### Troubleshooting

**Live main SHA unavailable:** Cause: remote/authentication failure. Fix: resolve it and rerun inventory; never use a cached SHA. **Stash overlap:** Cause: a planned path intersects a stash path. Fix: change scope or stay blocked; never erase the stash (the user may run `git stash apply`). **Cleanup proof fails:** Cause: mismatch, unchecked extraction, or non-empty parity diff. Fix: do not delete; re-fetch and reevaluate. **Stash inventory denied:** Cause: permissions block the inventory. Fix: ensure config retains targeted destructive denies followed by read-only allows for `git stash list` and `git stash show -u`.
