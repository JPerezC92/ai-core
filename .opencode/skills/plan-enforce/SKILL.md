---
name: plan-enforce
description: Enforce plan-first discipline for non-trivial tasks. Creates or resumes a subfolder plan artifact in plans/ before code-writing work, and verifies a user-confirmed PR merge before branch cleanup. Use when the user asks to plan work, types /plan, Cipher is about to dispatch Forge for implementation, or a user confirms a PR merge.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.18.0
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

### Plan and checklist templates

This project's plan-enforce templates and references:

- Programming plan template: `references/_template-programming.md`
- Base plan template: `references/_template.md`
- Phase template: `references/_phase-template.md`
- Plan/phase/audit/completion checklist: `references/_consistency-checklist.md`

The canonical user-story template and story-hygiene checklist are owned by the `user-story` skill at `.opencode/skills/user-story/references/`.

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

Before invoking the `question` tool, run bounded discovery (see **Bounded discovery before scope confirmation**) and send one regular Markdown message that visibly separates the decision inputs of the combined scope confirmation:

1. Under `**Goals**`, render every detected `G1..Gn` goal as its own Markdown bullet with its full observable condition, each traced to a selected criterion of the approved story (or `## Context` when stories are skipped).
2. Under `**Plan classification**`, render the detected plan type, user-story scope (create, update, or skipped with reason), and goal-bloat status (`none` or the triggered soft flag).
3. Under `**Discovery**`, render the affected code, documentation, and dependency evidence found, with the paths read.
4. Do not place the full goal list, plan type, user-story scope, discovery evidence, or goal-bloat detail in the `question` text. The user must be able to scan them outside the compact question control.

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

A plan reconciles only the acceptance criteria it **committed to deliver** — the selected criteria of the approved story that its goals trace to — the criteria it **materially changes**, and any regression it introduced. Other legitimate story commitments the plan did not select stay `⬜` and do not block completion:

- `✅` — a committed or materially-changed criterion established by verified evidence, resolved through the story's `## Proof` section (a completed goal's `Done when:`, a passing verify command, or a recorded outcome). No committed criterion may remain `⬜` at completion.
- `❌` — a committed criterion explicitly known to be unmet. A `❌`, an unmet committed criterion, or a regression the plan introduced blocks `## Outcome` and archival until satisfied or removed.
- A committed or materially-changed criterion removed as out-of-scope is deleted from the story (not left unchecked) and recorded as a dated change-log line, optionally pointing at a follow-up story.
- A criterion the plan did not select is not reconciled: leaving it `⬜` is not a defect, and no blanket "every touched-story criterion" disposition applies.
- **`## Constraints` are respected, never delivered.** A story's `## Constraints` entries are pre-decided restrictions, not obligations to build: confirm none was violated, and never tick, deliver, or reconcile one as a criterion.

Reconciliation is fail-closed on adverse evidence: `## Outcome` and the archive move stay blocked while a committed criterion lacks evidence, a `## Constraints` entry the plan violated is unresolved, a regression the plan introduced is unresolved, or the final-snapshot evidence is missing or adverse. Release events (PR opened/reviewed/merged) are release history, not feature acceptance criteria; a feature criterion may state the release policy (e.g. "merge remains user-only") but never a specific PR/review/merge event.

#### Resume (completion)

When the plan's work is done and its audits have passed — before the release PR is built:

- Confirm `## Audit` records an independent auditor's `[PASS]` with `Auditor`, `Findings`, and `Date` (see **Independent audit gate**); `[PENDING]`, `[FAIL]`, or a missing audit blocks completion.
- Evaluate completion evidence as a layered matrix on the current snapshot: code architecture, test architecture, test execution, and model/guidance verdicts — each with its scope and verdict. A passing execution result never stands in for a required architecture verdict, and a missing or adverse layer blocks completion. A planning-readiness audit is never reused as the completion audit. Adjudicate any adverse finding before marking a goal or criterion complete, writing `## Outcome`, or archiving.
- Run acceptance-criterion reconciliation (see **Acceptance-criterion reconciliation**) over the criteria this plan committed to deliver and materially changed, plus any regression it introduced; block `## Outcome` and the archive move while any committed criterion is unmet, any relevant regression is open, or the final-snapshot evidence is missing or adverse. Unselected story criteria stay `⬜` and do not block.
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

Stories are the durable per-feature definitions (`user-stories/<feature-slug>.md`); plans are temporal. Pre-plan behavior discussion, story ownership, creation, revision, and collision analysis belong to the `user-story` skill, and `.opencode/skills/user-story/references/_consistency-checklist.md` is the canonical story format/hygiene contract. Planning only consumes an approved (`active`) story and the selected criteria it hands over — never a `draft`, and never a story choice renegotiated here. If no approved story owns a feature the plan will write, stop and route that feature to `user-story` before creating plan files. Cite each touched story under `plan.md` → `## Critical files / tools`; trace each goal to a selected acceptance criterion, or to `## Context` / `## Goals` when stories are skipped. Stories are never archived or deleted with plans.

### User-story scope

Programming plans ALWAYS carry a story for each feature touched by writes under application source, backend tooling, `scripts/`, `.opencode/skills/**/scripts/`, or ticket tooling. At the goals gate, flag non-programming changes to feature-visible behavior and confirm whether a story is needed. Pure docs/process/tooling plans skip stories; `## Context` / `## Goals` record the work.

### Planning input — approved story and selected criteria

Planning starts from the **approved story** and the selected criteria it hands over — never from an invented feature intent. `user-story` owns the feature contract (see **User stories**); planning consumes it:

- Read the approved (`active`) story body and the criteria selected for delivery. These are the source of feature intent: the task phrasing never overrides the story.
- Read the story's `## Proof` and `## Constraints` with it. `## Proof` is where delivery evidence resolves; `## Constraints` are pre-decided restrictions to respect, never deliver or tick.
- Trace every goal to a selected acceptance criterion of the approved story, or to `## Context` / `## Goals` when stories are skipped (see **User stories**).
- A `draft` story is in-progress discussion, not a planning contract — do not plan from it.
- If no approved story owns a feature the plan will write, stop and route that feature to `user-story` before creating plan files.

### Bounded discovery before scope confirmation

Before the **combined scope confirmation** (goals, plan type, goal-bloat, user-story scope — see **Goal lifecycle** and **Create new plan**), run a bounded, read-only discovery pass and fold its evidence into that same confirmation:

1. **Affected code.** Locate and read the modules, services, public interfaces, and call sites the selected criteria touch. Never plan against a path you have not inspected.
2. **Affected documentation.** Identify every durable documentation surface the behavior change alters (README, `knowledge/` registers, skill prose, user stories, reference docs) and name its owner. Same-change documentation is planned here, not after the fact (see **Documentation discipline**).
3. **Affected dependencies.** Identify packages, contracts, and cross-module interfaces the change reads or alters, with their version or interface constraints.
4. **Planned-file design conformance.** Read every file the manifest will modify or add and assess its current design against the approved contract (`knowledge/agents.md` `### Clean architecture (language-agnostic) (HARD RULE)` and the applicable language profile). A planned file that does not conform is reworked within this plan: its necessary supporting files, tests, and documentation enter the manifest before execution. Existing nonconformance is not a legacy exemption; a small behavioral patch never substitutes for necessary design correction, and the rework does not expand into an unrelated repository-wide migration.
5. **Bound the pass.** Discovery is scoped to the selected criteria and their direct dependents; it names the paths read and the evidence found. It never edits files, installs dependencies, or widens into unrelated subsystems.

Record the discovery evidence in the plan (`## Current state` for programming plans, `## Body` otherwise) and present it with the goals. Discovery is not a substitute for confirmation — it feeds the same single confirmation round.

### Contract-sized phases

Each phase is **contract-sized**: it names one coherent responsibility and the exact interfaces it produces or consumes, its allowed writes, its outputs, and the gates that close it. Size a phase by responsibility, never by an arbitrary file count.

- **Responsibilities** — one outcome per phase; split a phase that carries two unrelated outcomes.
- **Interfaces** — the public paths, export/function names, and data shapes the phase produces and consumes, stated explicitly in the `Reads` / `Writes` / `Output` block.
- **Allowed writes** — the exact repo-relative paths in the phase `**Writes:**` block; no phase writes outside them.
- **Outputs** — the artifact and its schema/shape.
- **Gates** — the conditions that must be true before the next phase begins.

Phases state behavior and contracts, not private implementation: never prewrite private helper bodies, line-by-line algorithms, or internal variable names. A phase that lists a number of files instead of a responsibility is mis-sized — re-cut it by contract.

### Expected-red intermediate checkpoint

A behavior slice (a test-first slice inside a phase) may record its intended failing test as an **expected red** checkpoint: the designated executor runs the newly added test through its authorized command and records the red result (a non-zero exit carrying the expected failure) as evidence the test exercises the intended behavior. Expected red is an intermediate checkpoint only.

- Expected red is never a goal `✅`, a phase gate PASS, or an acceptance `✅`; it proves the test can fail, not that the behavior works.
- The phase still requires final green: the same executor's command exits 0 with the test passing.
- Applicable architecture verdicts (Atrium 🏛️ (Frontend Architect) / Bastion 🧱 (Backend & Scripts Architect) / Crucible 🔥 (Test Architect)) and the reviewed whole-suite gate (Project extensions) remain required at the phase gate and at completion; expected red substitutes for none of them.
- Only the designated executor's authorized command captures the red result; the implementer does not run tests outside its grant.

### Create new plan

1. Run the initial inventory; choose subfolder layout unless there is one owner, one edited file, no handoff/external mutation, and ≤30 instruction lines.
2. Derive slug, phases, and complete write/delete manifest in memory. Detect numbered `G1..Gn` observable goals (see **Goal lifecycle**).
3. Run bounded discovery (affected code/documentation/dependencies) before the confirmation; then present goals, classification, and discovery evidence in Markdown, and make one short confirming `question` call before any file creation. Select the path-detected template and confirm its type with the goals.
4. Run the user-story gate: consume the approved story and its selected criteria from `user-story` (never renegotiate the choice), read/filter `user-stories/index.md`, and review candidate bodies for overlap; route any needed CREATE/UPDATE back to `user-story`. Wait for the approved story before creating; stop before plan creation on collision. Record skipped stories in Context.
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
3. Analysis pass against the consistency checklist: evidence-match confirmed goals; each goal has Issue/How/Files; phase-to-goal and phase-file links exist; verification checkboxes trace to outputs; phase Writes equal the manifest; story title/status mirror the index; every criterion this plan committed to deliver or materially changed is reconciled, while unselected criteria `⬜` are left untouched. This semantic writer self-review reads the actual in-scope content — the real files, diffs, and command output — never the plan's or template's description of it. Never invent a value; stop and ask.
4. Repeat to zero findings and report `self-verification passes: N`. After 3 iterations or the same unchanged violation twice, stop-and-ask (S-07).

The validator catches repetitive mechanical drift; the writer's semantic self-review owns correctness by reading the actual content, not a summary of it.

#### Independent audit gate

Never report readiness or dispatch Forge 🔨 (Implementer) on the writer's own word. Before either, dispatch an independent checklist audit (see Project extensions): Sentinel 🛡️ (Quality Guardian) by default, Vault 🔐 (Catalog Steward) for catalog-heavy plans. Record `Auditor`, `Verdict`, `Findings`, and `Date` under `## Audit`; verdict is `[PENDING]`, `[PASS]`, or `[FAIL]`. Readiness/dispatch requires `[PASS]`, non-empty auditor, and date. If unavailable, remain not-ready; a substitute requires explicit user authorization recorded in the audit. Never self-audit, invent a verdict, or downgrade `[FAIL]`. Planning and completion audits are distinct: completion evaluates the final candidate and is required before `## Outcome`, goal checkmarks, and archive; planning `[PASS]` or execution alone cannot substitute.

- **Semantic review.** The neutral independent auditor reads the actual in-scope content — the real files, diffs, and command output — never the writer's summary of it. Mechanical checklist items and semantic/judgment items are reviewed separately; a mechanical pass never stands in for a semantic `[PASS]`.
- **Handoff discipline.** An audit handoff separates **user decisions** (what the user chose), **facts** (what the repository and commands show), and **interpretations** (the auditor's reading of ambiguous evidence). The auditor flags any interpretation presented as fact and any decision attributed to the user without an explicit record.
- **Two-failure reassessment.** Two failed planning audits on the same plan trigger a coherent reassessment of the plan's discovery, scope, phase cuts, or premises — not a cosmetic edit to satisfy the next auditor. The reassessment may rework goals, discovery evidence, or phase boundaries; it never waives the independent `[PASS]` gate: readiness/dispatch still require a fresh independent auditor `[PASS]`.

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

Documentation ships with the change, in the same plan: every behavior change carries its affected documentation through discovery, the manifest, and completion.

- **Discovery** names every affected documentation surface (README, `knowledge/` registers, skill prose, user stories, reference docs) and its owner, with the evidence that the surface is affected (see **Bounded discovery before scope confirmation**).
- **Manifest** lists each affected documentation path as an `Add` / `Modify` / `Delete` row, exactly like code paths; the union of phase `**Writes:**` must equal it, and each row appears in at least one phase's writes.
- **Completion** reviews each documented path against the delivered behavior, reading the actual documentation content — never the plan's description of it. A shipped behavior change whose documentation is missing or contradicts the delivered behavior blocks `## Outcome` and archival (see **Acceptance-criterion reconciliation**).

Published documents, durable criteria, and Goal `Done when:` must not cite temporal `plans/` or `output/` paths; cite a commit SHA, PR number, or ticket ID instead (see `.opencode/skills/user-story/references/_consistency-checklist.md`).

### Examples

**New multi-phase task:** derive all phase writes and check collisions before creating a subfolder plan. **Existing plan:** compare every phase `## Writes` block with the inventory before Forge 🔨 (Implementer) dispatch. **Stale non-overlapping stash:** offer user-run `git stash apply` or leave it untouched; never erase/replay it. **Post-merge cleanup:** use the confirmed `$PR_NUMBER`/`$BRANCH` and the lifecycle row's derived variables/proof.

### Troubleshooting

**Live main SHA unavailable:** Cause: remote/authentication failure. Fix: resolve it and rerun inventory; never use a cached SHA. **Stash overlap:** Cause: a planned path intersects a stash path. Fix: change scope or stay blocked; never erase the stash (the user may run `git stash apply`). **Cleanup proof fails:** Cause: mismatch, unchecked extraction, or non-empty parity diff. Fix: do not delete; re-fetch and reevaluate. **Stash inventory denied:** Cause: permissions block the inventory. Fix: ensure config retains targeted destructive denies followed by read-only allows for `git stash list` and `git stash show -u`.
