---
name: plan-enforce
description: Legacy migration-only plan workflow. New work uses the ODD feature document at odd/tasks/<feature-name>.md and the odd-workflow skill. Retains plan-enforce for existing plans and user-confirmed PR merge cleanup.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.23.8
---
<!-- core:begin -->

## Mandatory core

> **Migration-only:** New work uses the ODD feature document at `odd/tasks/<feature-name>.md` and the `odd-workflow` skill. This skill remains for legacy plans and user-confirmed PR merge cleanup.

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

If no task description and no active plan are available, Cipher 🔓 (Lead Orchestrator) collects the description with the `question` tool. A delegated run reports the gap to Cipher 🔓 and never invokes that tool.

#### Argument collection form

| name | type | validation | trigger |
|---|---|---|---|
| `task_description` | text | non-empty | no active plan and no task description |

Use one `question` call. The first option is the parsed value when one is available; do not add a manual “Other” option.

### Base ref variable

`$BASE` denotes the destination's protected upstream base ref; `$BASE_REMOTE` and `$BASE_BRANCH` are its remote and branch components, with `$BASE="${BASE_REMOTE}/${BASE_BRANCH}"`. This project's concrete values are in Project extensions (see **Protected upstream base ref**).

### Stash safety gate

**Mandatory loading:** read `references/_lifecycle-contract.md`'s loading instructions and operation table, then load its common lifecycle rules and every additional section applicable to the event, including named subsections. Standalone read-only stash inventory/status uses its separate bounded rows. Do not load unrelated post-merge proof during planning. Missing, unread, incomplete, or conflicting **applicable** content blocks the operation; these summaries are not a fallback.

Apply its ordered **Stash safety gate** for the mapped events, including creation, resumption, archival, reopening, and every Forge 🔨 (Implementer) dispatch: live read-only inventory with SHA/fingerprint and both ancestry directions, complete write/delete manifest, then collision check. `PLANNED_PATH_OVERLAP` blocks the affected write/dispatch. Never mutate stash/refs in this gate; erasure remains user-only. Its **Stash status query** defines the mechanical verdict and inconclusive response.

### Check for active plan

1. Run the initial inventory.
2. Scan `plans/*.md` (excluding `.completed/`) and `plans/*/plan.md`.
3. Read candidate plan files and select those with `Status: active`.
4. If one active plan exists, read it and, for subfolder layout only, its `phase-*.md` siblings; derive its manifest and run the post-scope collision check before showing the plan or dispatching Forge 🔨 (Implementer). Resumption also requires the current independent-audit `[PASS]` under **Plan lifecycle rules** and the **Independent audit gate**.
5. If no active plan exists, continue to **Create new plan**. If multiple exist, Cipher 🔓 (Lead Orchestrator) stops and asks the user to select one; a delegated run reports the candidates and gap to Cipher 🔓.

An archived plan is never resumed directly from `plans/.completed/`. Restore it to `plans/`, set `Status: active`, and append `Reopened: YYYY-MM-DD HH:MM` before resuming.

### Goal lifecycle

Detect `G1..Gn` from the approved selected criteria (or Context/Goals when skipped), confirm before file creation, persist as `## Goals` checkboxes, watch drift, and resume at completion.

#### Detect

Extract the goals from the approved selected criteria (or from Context/Goals when stories are skipped) before writing any plan file. Do not invent feature behavior from task phrasing:

1. Number them `G1`, `G2`, … in order of importance.
2. State each goal as what must be true when the plan is done — an observable condition, not an activity.
3. Programming goals (see **Template selection**) additionally carry a `Done when:` criterion (see Persist).
4. More than 5 goals triggers the soft goal-bloat flag (see **Simplicity discipline**) — report it in the confirmation gate; do not silently proceed.
5. Draft done-conditions referencing another document's state from its current text, read fresh at plan creation, never memory/prior-plan phrasing. Quote the governing text in the goal or verification line.

#### Present (pre-file gate)

Before `question`, run bounded discovery and send one regular Markdown message with visibly separate inputs:

1. `**Goals**`: one Markdown bullet per goal, full observable condition and selected approved-story criterion trace (or Context when stories are skipped).
2. `**Plan classification**`: detected type, story scope (create/update/skipped with reason), and goal-bloat status (`none` or triggered flag).
3. `**Discovery**`: affected code/documentation/dependency evidence and paths read.
4. Keep these details outside the compact `question` control, never in its text.

#### Confirm (pre-file gate)

Before ANY plan file, make exactly one short `question` call: proceed with or revise the displayed goals/classification. In that single round confirm all four: full `G1..Gn` conditions, detected type, triggered goal-bloat flag, and story scope for programming/feature-visible changes (whether CREATE/UPDATE is needed). No `plan.md`/phase file until confirmation; no skipped Markdown presentation, second question round, or paraphrased confirmation.

#### Persist

Write the confirmed goals into the active plan artifact (`plan.md`, or the single-file plan file) under `## Goals`:

- One checkbox per goal: `- ⬜ **G1:** <goal>`
- Each goal lists Issue, How, and Files. `## Context` remains the overall issue.
- Programming plans use the programming plan template (see **Plan and checklist templates**), where every goal also carries a `Done when:` criterion — the observable condition that proves the goal is met.
- After confirmation, goals are never renumbered or reworded silently — changes go through Drift watch.

#### Drift watch

Watch for goal drift on every phase close, every scope change, and every collateral-fix verification. When the work no longer matches the confirmed goals — or a goal must be added, removed, or reworded:

1. **Stop** — do not continue editing plan files.
2. **Notify** the user with evidence: which goal drifted, what the current work does instead, and what the plan file says.
3. **Wait** for the user's call — the user decides whether to update the goals, adjust the work, or abort. Never self-approve a goal change.
4. On user approval, update the `## Goals` block and append a dated line to `## Resolved decisions` recording the change.

#### Acceptance-criterion reconciliation (fail-closed)

Apply **Acceptance-criterion reconciliation (fail-closed)** from the loaded lifecycle contract, including **Story ownership and current evidence**: reconcile selected/materially-changed criteria and regressions through Proof at the authorized owner; destinations record local outcomes without editing inherited core. Preserve unselected commitments and evidence-grounded shared marks. Respect, never deliver/tick Constraints. Unmet criteria, violations, regressions, missing/adverse final evidence, or unfinalized required history block completion; release events are history, not criteria.

#### Resume (completion)

Apply **History finalization gate** and **Resume (completion)** from the loaded lifecycle contract before building the release PR: current independent completion `[PASS]`, layered evidence, accepted joins, owner-aware reconciliation, matching history, chat goals resume, then Outcome → completed metadata → archive → filesystem verification. Missing/adverse evidence or required history blocks finalization. Planning readiness, inherited marks, or test execution alone is never completion proof. Cipher 🔓 (Lead Orchestrator) must not report the plan complete, and must not report that plan’s PR or release done, until every confirmed goal is marked complete, Outcome is written, completed metadata is set, and the plan is archived with filesystem verification. An opened, reviewed, or merged PR, or a shipped status, does not replace that sequence. If close-out was skipped after a ship report, restore the still-active plan, run that same pre-release sequence, then archive; do not add a post-merge archive step.

### Simplicity discipline

Challenge every artifact for removal or merger before rendering. Every dispatch-table phase traces to ≥1 goal; remove or merge untraced phases. Remove files, phases, and steps not demanded by a goal or explicit request. Programming plans record cuts/mergers and reasons in `## Design decisions`. More than 5 goals or any non-single-observable goal triggers a soft bloat flag at confirmation; the user chooses whether to trim, split, or accept it.

Admit a finding only with its confirmed goal, governing clause, responsible actor and shipped path (not a helper/fixture), expected-versus-observed behavior, scope, reproduction/static fact, literal severity output, and keep/fix/reject-scope decision. Classify it as a requirement defect, documentation drift, or supplemental concern; reject speculative blockers and judge the flow once, not through unbounded helpers or test matrices. When behavior is replaced, superseded, or newly wired, search for and remove dead code/stale wiring and record the sweep at completion; no validated-but-unread field, dead symbol, or stale mapping survives.

### Dispatch bundle contract

Every subagent dispatch prompt MUST contain verbatim: (1) the plan Subject; (2) the full `## Goals` block, checkboxes included; (3) the full phase runbook (for an eligible single-file plan, its complete in-file execution instructions, including applicable programming sections, instead); and (4) each prior-phase Output value consumed by that phase's Reads, explicitly none for single-file plans without phase IO. "See phase-01 output," summarized goals, or paraphrased phase content do not qualify. Verify all four before dispatch; if anything is missing, rebuild and do not dispatch.

Include verbatim the question prohibition and stop-report contract: never invoke the user-facing `question` tool. If required input, instruction, or evidence is missing, halt and report to Cipher 🔓 (Lead Orchestrator) the task as received, exact missing item, inspected sources, bounded options, and recommended default. Never guess, assume, silently continue, or stall.

### Task coordination and accepted joins

Apply `knowledge/agents.md` **Safe parallel task coordination (HARD RULE)**; declarations supplement, never replace, the verbatim bundle. Cipher 🔓 (Lead Orchestrator) alone coordinates and accepts the workflow.

- **Assignment:** record workflow/task/instance identity, role/responsibility, accepted predecessor results and input identities, exact permitted writes/other resource accesses, output destination, required gates, continuation/join owner, capacity allocation/accounting owner in plan/phase declarations. Instances gain no additional role authority or allowances.
- **Readiness:** accept relevant predecessors; require present/current inputs, existing approvals/gates, compatible resource access, and declared available capacity. Dispatch independent ready tasks concurrently, including same-role instances. Explain serialization by actual dependency, conflict, gate, or capacity; phase numbers and roles prove neither independence nor isolation. Unknown external capacity/isolation blocks dispatch.
- **Resources:** declare read/write/mutation modes and one active writer per canonical mutable resource, including aliases, overlapping directories, creation/deletion/rename, shared exports/contracts/fixtures, generated/autofix outputs, reports/indexes/registers, external records, browser/auth sessions, environments, Git/worktree state and PR bodies. Whole-file edits conflict despite separate text regions; directory deletion conflicts with descendants. Declare read-side effects. Unchanged shared reads may overlap; reject incompatible access unless isolation is verified, not inferred from sessions/prompts.
- **Evidence:** allocate attributable instance outputs before dispatch. Keep fixed governing paths exclusive/serialized, never rename them to manufacture parallelism. Autofix reviewers are writers. Hold reviewed content/dependencies stable with identities/scope; relevant change invalidates affected verdicts/assignments. Slice review cannot replace combined-candidate/completion gates.
- **Handoffs:** required edit gates return `AWAITING_REVIEW` with task identity, changed paths, content/input identity, owner gate, completed operations and resource-use state; this is not step completion. The parent obtains the existing owner's current verdict and explicitly redispatches accepted continuation. No callbacks, hidden suspension, cancellation, or self-dispatch are implied. Out-of-assignment needs halt before mutation and return `BLOCKED` with need, evidence, options/default; the coordinator resolves scope/approval and obtains observed cessation before transferring ownership. Stop requests, timeouts, old timestamps, or completed tool returns alone do not prove continuing side effects ceased.
- **Join:** `COMPLETED` returns outputs, consumed identities, gate evidence and resource-release status; the coordinator accepts all relevant results and the combined candidate before dependent work/completion. Incomplete, failed, stale, or still-mutating predecessors never unblock it. Preserve separate execution/review verdicts and one shared budget ledger; scope/input changes invalidate affected evidence before redispatch. Preserve source authority, incident ordering/budget denominators, mutation approvals and close-out gates.

Structural validation is not locking, semantic independence, isolation, executor authority, or workflow acceptance. Sequential plans retain their supported shape; declare their actual dependencies and handoffs in prose without changing parsed tables/labels.

### Template selection

Choose and confirm the template at the goals gate, before creating files. Detect programming plans by paths, not subject: any code write under application source, backend tooling, `scripts/`, `.opencode/skills/**/scripts/`, or ticket tooling qualifies. Use the programming template (goals with `Done when:`, Current state, Behavior change, Design decisions, per-phase Goals and Verify commands); otherwise use the base template. Confirm the type in the same `question` call as the goals; never choose silently.

### Verification command executors

Every phase runbook has one non-empty `## Verify commands` Markdown table with exactly two columns, `Executor` and `Command`; each command has exactly one non-empty executor. The static validator checks table shape and traceability only, never permission models. Phase review separately verifies that each executor has the role and tool authority to run the command.

| Executor | Command |
|---|---|
| <Name Emoji (Role)> | `<shell command>` |

#### Non-TypeScript test files

Crucible 🔥 (Test Architect) executes each declared approved test command; Forge 🔨 (Implementer) writes tests; Bastion 🧱 (Backend & Scripts Architect) audits applicable Python implementation. A plan editing a Python test in reviewed discovery areas must list the reviewed whole-suite command (Project extensions), obtain Bastion 🧱 (Backend & Scripts Architect) `[PASS]` on applicable implementation edits, then dispatch Crucible 🔥 (Test Architect) to return `[PASS]` or `[FAIL]`. `[UNCERTAIN]` is not acceptable. Cipher 🔓 (Lead Orchestrator) checks the exact command before dispatch; runner permissions are in the root opencode config under `agents.crucible.permissions` and gate command text, not sandbox execution. Existing TypeScript / Atrium 🏛️ (Frontend Architect) and Crucible 🔥 (Test Architect) gates remain unchanged.

### User stories

Stories (`user-stories/<feature-slug>.md`) are durable; plans are temporal and never archive/delete stories. `user-story` owns pre-plan behavior discussion, ownership, creation, revision and collision analysis; its `references/_consistency-checklist.md` is the canonical format/hygiene contract. Planning consumes approved (`active`) stories and selected criteria, never drafts or renegotiated choices. Cite every touched story under `## Critical files / tools`; missing ownership stops planning and routes to `user-story`.

### User-story scope

Programming plans ALWAYS carry a story for each feature touched by writes under application source, backend tooling, `scripts/`, `.opencode/skills/**/scripts/`, or ticket tooling. At the goals gate, flag non-programming changes to feature-visible behavior and confirm whether a story is needed. Pure docs/process/tooling plans skip stories; `## Context` / `## Goals` record the work.

### Planning input — approved story and selected criteria

Read the approved (`active`) story, selected criteria, Proof, Constraints, and applicable project-owned approval/history tracking together. Intent governs, never invented intent or overriding task phrasing; drafts are not planning contracts. An approved revision with explicitly pending history may feed planning under the lifecycle contract's **History finalization gate**. Inherited marks never prove current-plan or destination checks. Trace goals to selected criteria (or Context/Goals when skipped), respect Constraints, and apply **Story ownership and current evidence**; no approved owner means route to `user-story` before plan creation.

### Bounded discovery before scope confirmation

Before the **combined scope confirmation** (goals, plan type, goal-bloat, user-story scope — see **Goal lifecycle** and **Create new plan**), run a bounded, read-only discovery pass and fold its evidence into that same confirmation:

1. **Affected code.** Locate and read the modules, services, public interfaces, and call sites the selected criteria touch. Never plan against a path you have not inspected.
2. **Affected documentation.** Identify every durable documentation surface the behavior change alters (README, `knowledge/` registers, skill prose, user stories, reference docs) and name its owner. Same-change documentation is planned here, not after the fact (see **Documentation discipline**).
3. **Affected dependencies.** Identify packages, contracts, and cross-module interfaces the change reads or alters, with their version or interface constraints.
4. **Planned-file design conformance.** Read every file the manifest will modify or add and assess its current design against `knowledge/agents.md` **Clean architecture (language-agnostic) (HARD RULE)** and the applicable language profile. Nonconforming planned files require rework in this plan, including necessary supporting files/tests/docs in the manifest before execution. No legacy exemption or behavioral-patch substitute; no unrelated repository-wide migration.
5. **Bound the pass.** Discovery is scoped to the selected criteria and their direct dependents; it names the paths read and the evidence found. It never edits files, installs dependencies, or widens into unrelated subsystems.

Record the discovery evidence in the plan (`## Current state` for programming plans, `## Body` otherwise) and present it with the goals. Discovery is not a substitute for confirmation — it feeds the same single confirmation round.

### Contract-sized phases

Each phase is **contract-sized**: it names one coherent responsibility and the exact interfaces it produces or consumes, its allowed writes, its outputs, and the gates that close it. Size a phase by responsibility, never by an arbitrary file count.

- **Responsibilities** — one outcome per phase; split a phase that carries two unrelated outcomes.
- **Interfaces** — the public paths, export/function names, and data shapes the phase produces and consumes, stated explicitly in the `Reads` / `Writes` / `Output` block.
- **Allowed writes** — the exact repo-relative paths in the phase `**Writes:**` block; no phase writes outside them.
- **Outputs** — the artifact and its schema/shape.
- **Gates** — the conditions for accepting this phase and releasing its declared dependents, not an unconditional next-phase barrier.

Phases state behavior and contracts, not private implementation: never prewrite private helper bodies, line-by-line algorithms, or internal variable names. A phase that lists a number of files instead of a responsibility is mis-sized — re-cut it by contract.

### Expected-red intermediate checkpoint

A test-first behavior slice may record **expected red**: the designated executor runs the new test through its authorized command, recording a non-zero exit with the intended failure. This intermediate evidence proves only that the test can fail.

- Expected red is never a goal `✅`, a phase gate PASS, or an acceptance `✅`; it proves the test can fail, not that the behavior works.
- The phase still requires final green: the same executor's command exits 0 with the test passing.
- Applicable architecture verdicts (Atrium 🏛️ (Frontend Architect) / Bastion 🧱 (Backend & Scripts Architect) / Crucible 🔥 (Test Architect)) and the reviewed whole-suite gate (Project extensions) remain required at the phase gate and at completion; expected red substitutes for none of them.
- Only the designated executor's authorized command captures the red result; the implementer does not run tests outside its grant.

### Create new plan

1. Run the initial inventory; choose subfolder layout unless ALL five single-file criteria in `references/_template.md` are met (1 owner, ≤30 instruction lines, no phase IO contracts, no external state mutation, no improvisation risk).
2. Consume the approved story and selected criteria without renegotiation (see **Planning input**). If ownership is missing or CREATE/UPDATE is needed, route to `user-story` and stop before files. Record skipped stories in Context. Do not re-filter unread catalogue bodies here.
3. Derive slug, the complete write/delete manifest, and execution instructions in memory; derive phases only for subfolder layout. Detect numbered `G1..Gn` from those selected criteria (see **Goal lifecycle**).
4. Run bounded discovery; present goals/classification/evidence, then Cipher 🔓 (Lead Orchestrator) makes the single short confirming `question` before files. Confirm path-detected template type with goals. A delegated run reports the confirmation packet to Cipher 🔓 and never invokes `question`.
5. Run the post-scope collision check; stop on overlap.
6. Render only the confirmed layout:
   - **Single-file:** create `plans/<task-slug>-YYYYMMDD.md` from `references/_template.md`'s minimal single-file body, with `Layout: single-file` and `## Audit`. Include applicable programming content when path-detected. Put the sole owner's complete instructions, explicit write/delete paths, outputs, authorized verification and gates in that file. Do not create a plan folder, phase runbooks, phase IO contracts, or dispatch table. If the complete contract cannot meet every single-file criterion, return to scope confirmation for subfolder layout rather than silently changing it.
   - **Subfolder:** create `plans/<task-slug>-YYYYMMDD/plan.md` and one phase-template `phase-NN-<owner>.md` per phase. Record the full manifest; `Action`/`Path` rows must equal the union of phase `**Writes:**` paths.
7. For **subfolder layout only**, complete each phase's Owner, Pre, Reads, Writes, assignment/resources, Steps, Output, Verify commands, Gate, and Abort conditions; no `TBD` in Steps/Output/Gate/Abort. Steps state contract outcomes, not private implementation. Declare accepted dependencies, capacity, handoffs and join readiness; add one traced verification checkbox per phase output. Single-file layout retains applicable assignment, owner, approval and review gates without inventing phases or handoffs.
8. After the coherent write batch for the selected layout, run the post-write self-verification loop once on that batch. After it passes, send the execution-review message and stop. Do not dispatch Forge 🔨 (Implementer) in this turn or treat `ExitPlanMode` as implementation authorization.

### Execution-review message

After written plans pass self-verification, Cipher 🔓 (Lead Orchestrator) sends one readable final message and stops. Use prose per goal, in order: Issue, Goal, How, Files; `plan.md` uses the same layout and `## Context` states the overall issue. An optional file table follows, never replaces, the prose; dense dumps/table-only briefs fail. Do not dispatch Forge 🔨 (Implementer) in this turn or ask corrective, release, or scope questions without the file list. Forge 🔨 (Implementer) may start only on a later user turn explicitly authorizing execution, after independent-audit `[PASS]` and the stash gate.

### Post-write self-verification loop

Run after each coherent plan/phase/story/index write batch and every Forge 🔨 (Implementer) dispatch that mutates plan artifacts; repeat until clean:

1. Re-read each written `plan.md`, phase file, story, and index.
2. Mechanical pass, by layout: active subfolder plans touching stories/index use `<plan-dir> --stories user-stories`; no-story subfolder plans use `<plan-dir>`; single-file plans use `<plan.md> --single-file`, and when a single-file plan touches `user-stories/index.md` add `--stories user-stories`. Both layouts check Status/Completed, required sections, placeholders, and the completed-plan audit gate. Apply index mirroring in either layout when stories/index are touched. Subfolder layout additionally checks phase sections/labels, executor-command tables, goal trace, manifest equality, and verification parity; do not impose those phase checks on single-file plans.
3. Analysis pass against the consistency checklist: evidence-match goals and Issue/How/Files; check output/verification trace, explicit allowed writes, and applicable story/index metadata. Check phase/goal links and Writes/manifest equality only for subfolder layout; single-file review checks its complete in-file execution contract instead. Reconcile selected/materially-changed criteria and regressions at completion under the lifecycle contract's ownership and history rules; preparation may retain truthful pending criteria/history. Preserve unselected commitments and inherited core. When the write revises or replaces existing instructions, run rewrite-acceptance accounting: identify the original and candidate content and disposition every valid original obligation as retained, translated, or justifiably retired with an authority-grounded rationale, plus a source-neutrality check (no source-specific runner or interpreter, dependency pin, or mandated local policy value); superseded wording is never imported as precedent. Read actual files, diffs, and command output, never their description; never invent a value. Escalate missing decisions through the existing question-routing rule.
4. Repeat to zero findings and report `self-verification passes: N`. After 3 iterations or the same unchanged violation twice, stop-and-ask (S-07).

Mechanical success never substitutes for actual-content semantic self-review.

#### Independent audit gate

Never report readiness or dispatch Forge 🔨 (Implementer) on the writer's own word. Before either, dispatch an independent checklist audit (see **Plan and checklist templates**): Sentinel 🛡️ (Quality Guardian) by default, Vault 🔐 (Catalog Steward) for catalog-heavy plans. Record `Auditor`, `Verdict`, `Findings`, and `Date` under `## Audit`; verdict is `[PENDING]`, `[PASS]`, or `[FAIL]`. Readiness/dispatch requires `[PASS]`, non-empty auditor, and date. If unavailable, remain not-ready; a substitute requires explicit user authorization recorded in the audit. Never self-audit, invent a verdict, or downgrade `[FAIL]`. Planning and completion audits are distinct: completion evaluates the final candidate and is required before `## Outcome`, goal checkmarks, and archive; planning `[PASS]` or execution alone cannot substitute.

- **Semantic review.** The neutral independent auditor reads the actual in-scope content — the real files, diffs, and command output — never the writer's summary of it. Mechanical checklist items and semantic/judgment items are reviewed separately; a mechanical pass never stands in for a semantic `[PASS]`.
- **Rewrite acceptance accounting.** When a write revises or replaces existing instructions, acceptance requires identified original and candidate inputs read as actual content — an author's summary or change description is never a substitute when an obligation comparison is required — and a complete disposition of every valid original obligation as retained, translated, or justifiably retired with an authority-grounded rationale, with superseded wording never imported as precedent. A source-neutrality check confirms no source-specific runner or interpreter, dependency pin, or mandated local policy value. Missing accounting, unauthorized or unrecognized obligation loss, or source-environment leakage prevents acceptance.
- **Handoff discipline.** An audit handoff separates **user decisions** (what the user chose), **facts** (what the repository and commands show), and **interpretations** (the auditor's reading of ambiguous evidence). The auditor flags any interpretation presented as fact and any decision attributed to the user without an explicit record.
- **Two-failure reassessment.** Two failed planning audits on the same plan trigger a coherent reassessment of the plan's discovery, scope, phase cuts, or premises — not a cosmetic edit to satisfy the next auditor. The reassessment may rework goals, discovery evidence, or phase boundaries; it never waives the independent `[PASS]` gate: readiness/dispatch still require a fresh independent auditor `[PASS]`.
- **Round ceiling.** Independent planning-readiness review permits at most three rounds for the same task. Edits, reviewer changes, or renames do not reset the count. After a third-round `[FAIL]`, stop and report unresolved blockers for the user's decision; no fourth round starts automatically. Earlier stop obligations still apply. Writer post-write self-verification (3 iterations / S-07) is a distinct loop and does not consume these rounds.
- **Consolidated findings.** The first independent planning-readiness audit consolidates findings against all applicable contracts. Later rounds preserve finding identities and dispositions, concentrating on corrections and affected dependencies or regressions without skipping mandatory checks. A newly discovered mandatory blocker remains blocking only with its governing requirement, evidence, and why it was missed earlier.
- **Nonblocking advice.** An advisory alone neither blocks planning readiness nor requires rewriting. A violation of an applicable mandatory obligation is never relabelled advisory.
- **Completion adversarial pass.** Before a plan is reported complete, the completion auditor reads the actual original and candidate content and the delivered evidence, and checks: original-obligation accounting completeness; evidence durability outside temporal `output/` or `plans/` paths; shared/project separation; source-neutrality under its stated boundary; and live PR test-plan evidence when a PR exists. Shape, presence, or self-attestation is not completion. A missing or adverse check blocks `## Outcome`, goal checkmarks, and archive.

### All-changes disposition

For an all-pending-changes analysis, inspect and disposition every nonignored modified/deleted/untracked path as evidence-based `ship`, `fix`, or `drop` before any scope question. Manifest absence or pre-existence does not prove unrelatedness. Do not defer while any inspected path lacks disposition or claim beyond reviewed scope.

### Plan lifecycle rules

Apply **Plan lifecycle rules** and **Reopen rule** from the loaded lifecycle contract for every lifecycle event. Only incomplete plans enter Git; completed tracked plans retire by deletions in their completing PR, never an archive commit. No plan deletion, merge command, or stash mutation occurs during archival. Scope changes retain user approval and invalidate affected assignments/evidence. Cipher 🔓 (Lead Orchestrator) must not report the plan complete or its PR/release done until goal checkmarks, Outcome, completed metadata, archive, and filesystem verification have occurred; an opened, reviewed, or merged PR or shipped status does not replace that sequence. If close-out was skipped after a ship report, restore the still-active plan, run that same pre-release sequence, then archive; post-merge branch cleanup still does not archive.

**User confirms PR merge:** apply **Post-merge proof and cleanup** from the loaded lifecycle contract. Require live MERGED metadata, exact immutable head match, checked fetch/ancestry/extraction, and per-path parity before force deletion; use safe deletion when tip ancestry holds. Fast-forward local base and delete remote only if present. Any proof error blocks deletion; merge remains user-only and no post-merge archive step exists. Skipped close-out is repaired by restoring the still-active plan and running the same pre-release sequence, not by archiving here.

### Documentation discipline

Documentation ships with the change, in the same plan: every behavior change carries its affected documentation through discovery, the manifest, and completion.

- **Discovery** names every affected documentation surface (README, `knowledge/` registers, skill prose, user stories, reference docs) and its owner, with the evidence that the surface is affected (see **Bounded discovery before scope confirmation**).
- **Manifest** lists each affected documentation path as an `Add` / `Modify` / `Delete` row, exactly like code paths; for subfolder layout the union of phase `**Writes:**` must equal it, and each row appears in at least one phase's writes. An eligible single-file plan records these actions and paths in its explicit write/delete instructions, without phase IO.
- **Completion** reviews each documented path against the delivered behavior, reading the actual documentation content — never the plan's description of it. A shipped behavior change whose documentation is missing or contradicts the delivered behavior blocks `## Outcome` and archival (see **Acceptance-criterion reconciliation**).

Published documents, durable criteria, Goal `Done when:`, and every `## Change log` entry must not cite temporal `plans/` or `output/` paths; cite a commit SHA, PR number, or ticket ID instead (see `.opencode/skills/user-story/references/_consistency-checklist.md`). Plans are untracked and machine-local: a plan folder is never a traceability anchor.

### Examples

**New/existing plan:** derive all writes and check stash collisions before creation/dispatch. **Independent work:** two same-role research instances read frozen inputs into distinct reports; cross-role writers own disjoint files with no changing shared dependency. Dispatch concurrently only after readiness/capacity checks. **Collision:** two writers targeting one file, even different sections, stay blocked until serialized or verified isolation. **Stale non-overlapping stash:** offer user-run apply or retention, never erasure. **Cleanup:** use confirmed `$PR_NUMBER`/`$BRANCH` and the post-merge proof sequence.

### Troubleshooting

**Live SHA unavailable:** remote/auth failure; resolve and rerun, never cache. **Stash overlap:** change scope or stay blocked; never erase (user may apply). **Cleanup proof fails:** mismatch, unchecked extraction or parity diff; retain branch, re-fetch/reevaluate. **Inventory denied:** retain targeted destructive denies followed by read-only stash list/show allows. **Lifecycle reference missing/unread:** load the applicable sections or stop, never use summaries. **Stale review:** changed input/content invalidates the verdict; hold the new candidate stable and obtain fresh applicable review. **Unfinished predecessor:** pending/failed/still-mutating worker; block dependent dispatch/completion, collect its attributable return and observed cessation, then accept or redispatch through the parent.

### Plan and checklist templates

Plan-enforce templates and references:

- Programming plan template: `references/_template-programming.md`
- Base plan template: `references/_template.md`
- Phase template: `references/_phase-template.md`
- Plan/phase/audit/completion checklist: `references/_consistency-checklist.md`
- Mandatory lifecycle contract: `references/_lifecycle-contract.md` (load applicable sections per its operation table)

The canonical user-story template and story-hygiene checklist are owned by the `user-story` skill at `.opencode/skills/user-story/references/`.
<!-- core:end -->

<!-- project:begin -->
## Project extensions

### Python invocation

This project's `<python>` is `uv run --frozen python3`.

### Protected upstream base ref

This project's protected upstream base ref is `origin/main` — remote `origin`, branch `main`. Mandatory core denotes it with `$BASE`, composed as `$BASE="${BASE_REMOTE}/${BASE_BRANCH}"`; substituting this project's values (`$BASE_REMOTE=origin`, `$BASE_BRANCH=main`) keeps every command identical to `origin/main`.

### Reviewed whole-suite command

This project's reviewed whole-suite test command is `uv run --frozen --group dev pytest -q`.

### Test file pattern and harness config

This project's Python test-file pattern is `test_*.py`. This project's root opencode config is `opencode.jsonc`; Crucible 🔥 (Test Architect) runner permissions live under `agents.crucible.permissions`.

### Plan validator script

This project's plan validator script is `<python> .opencode/skills/plan-enforce/scripts/validate_plan.py`. Every Python invocation in this skill runs through the project's virtual environment.
<!-- project:end -->
