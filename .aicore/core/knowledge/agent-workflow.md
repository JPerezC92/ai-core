# Agent workflow

ODD is the governing workflow: apply the universal entry gate in `AGENTS.md` on every request and read this entry's applicable sections before their governed actions. Read-only and small work create no durable feature artifact. For authorized non-small state-changing work, creating the governing feature document from its template is the sole authorized bootstrap write; no other mutation precedes it. Revise an existing document before affected work resumes and apply decision-only stops. This entry routes work; it does not grant authority, replace an owner procedure, or prove delivery.

### Canonical ODD flow

The supplied diagram is preserved with its operational interpretation below. Vendor labels describe capabilities, not installed commands. Written alignment, observed scenario execution and unverified runtime behavior are separate evidence states: the diagram or a green validator establishes no adoption by itself.

```mermaid
flowchart TD
    A[Request] --> B{Implementation authorized?}
    B -->|No| C[Explore or explain without task artifacts]
    B -->|Yes| D[Explore existing code]
    D --> E{Research useful and selected?}
    E -->|Yes| F[Scoped research]
    E -->|No| G[Resolve real scope decisions only]
    F --> G
    G --> H{High-consequence unproven premise?}
    H -->|Yes| I[One evidence-based assumption challenge]
    H -->|No| J{Substantial implementation?}
    I --> J
    J -->|Yes| K[One task record and durable feature]
    J -->|No| L[Small work without durable task artifacts]
    K --> TT[Resolve applicable test-first policy and runner]
    L --> TT
    TT --> M[Implement next authorized task directly]
    M --> N[Applicable proportionate checks and self-review]
    N --> Q[Record truthful results]
    Q --> QC[Commit work units in reviewable slices, high-risk units alone]
    QC --> R{Tracked feature?}
    R -->|No| AB[Ordinary checks and policy]
    R -->|Yes| T[Update intent, tasks and evidence]
    T --> U{Work remains or requirements changed?}
    U -->|Yes| V[Revise affected tasks within authorized scope]
    V --> M
    U -->|No| W{Any applicable check failed or guarantee unestablished?}
    W -->|Yes| X[Report the failure and keep the record open]
    X --> V
    W -->|No| Y[Close the record with its verified outcome]
    Y --> AB
    AB --> AG{User authorized an independent review of this candidate?}
    AG -->|Yes| AH[Dispatch a fresh context against the named candidate]
    AG -->|No| AI[Prepare delivery evidence and publish]
    AH --> AJ{Findings returned?}
    AJ -->|Yes| V
    AJ -->|No| AI
    AI --> S[Deliver]
    Z[Resume interrupted feature] --> W2[Read task file; reconcile evidence]
    W2 --> TT
```

- **A–D, J/L:** protocol steps 1–4 determine authority, exploration and substantial versus small work, not file/line counts. Read-only explanation ends with outcome verification, without implementation, commit or tracker requirements.
- **E/F/G:** research is optional when useful and selected, not a compulsory detour; follow the research owner's saved-evidence procedure. Resolve accessible facts first, then only genuine user-only scope decisions. Continue automatically when authorized scope and prerequisites are settled.
- **H/I:** for a high-consequence unproven premise that could materially change the solution, the primary agent challenges that premise once with evidence before committing to it — directly, not by dispatching anyone. The challenge is evidence, not a veto: the primary agent resolves the result or routes a genuine user decision, and no second agent must accept the challenge for work to proceed.
- **K/T/Z/W2:** the task record is authoritative for active work; resume from it and relevant current evidence, without a memory dependency.
- **TT/M/N/Q:** resolve applicable test-first policy and the actual runner before implementation; use protocol step 6 and Behavioral verification and runner selection below. Record observed results honestly, including failed, skipped and pending controls, under the skill's evidence procedure. Implementation is performed directly by the primary agent; no delegation is required and none is implied.
- **QC/R/U/V:** commit coherent reviewable authorized work units through the release owner; isolate high-risk units in their own reviewable commits. Update tracked intent/tasks/evidence, then continue remaining authorized work; changed requirements reopen only affected work under scope readiness. Small work gains no feature document merely to report a commit.
- **W/X:** a failed applicable check, or an applicable guarantee that remains unestablished, is a real blocker. It keeps the record open and the delivery not ready; it is never resolved by the absence or presence of a reviewer, and an unavailable check whose guarantee a permitted alternative establishes is not one.
- **Y/AB:** closure states the verified outcome and every failed or pending check. Native receipt-driven review is not adopted here and is not an available branch; ordinary checks and policy apply.
- **AG/AH/AJ/AI:** an independent review is optional and strictly opt-in. It runs only on explicit user authorization covering that review, against the candidate and scope that authorization names; a declared high-risk item may justify **recommending** one, and a recommendation authorizes nothing. When it runs, its findings are disposed like any other finding. When none is requested, delivery proceeds on automated verification plus self-review, and no stand-in verdict is created. Findings that return to implementation do not renew the authorization: the earlier verdict keeps the candidate it actually judged, the defect is corrected and verified directly, and a further review needs a further authorization.
- **AG/AH/S:** deliver coherent reviewable units, planning rollback where risk warrants it. Closing a document is not delivery; apply the skill's Delivery boundary and `.aicore/core/knowledge/release.md`.

### Resume active work

Read the active task record and relevant current files and evidence; reconcile approved scope, current state, unresolved decisions and next action before resuming. Resolve changed requirements and reselect applicable checks. Memory is optional and never a prerequisite. An uncommitted task record lost with its checkout has no separately verified recovery copy under this workflow.

### Behavioral verification and runner selection

- Before each implementation task, map each affected `S#` to its observable acceptance action/result and to the check that proves it. Use the actual applicable runner, exact inputs and expected outcome; inspect existing test policy/commands rather than inventing a harness.
- For each requested behavioral rule with a relevant runnable deterministic test, observe at least one RED for that rule's intended reason before implementation, then GREEN and refactor; a failure for another rule is not its RED evidence. Distinguish a reproduced defect from missing environment/dependencies or unrelated failure; record actual exceptions and proportionate static/manual checks when executable RED/GREEN is inapplicable.
- For changed command behavior, run the same changed input against previous and current code in equivalent authorized isolated conditions; compare stdout, stderr and exit status, recording the expected and observed differences. Add regression coverage for every touched existing command or option sharing the changed code, including relevant error cases, not only the newly requested path. Reuse existing shared-state helpers and preserve their invariants rather than introducing parallel state setup; update help and documentation for changed commands, options and messages.
- Use isolated disposable inputs and state for mutating examples only when those mutations are explicitly authorized; do not run a destructive/live example merely to obtain RED or a previous/current comparison. Missing authority or an unsafe environment is a reported verification limitation, not permission to skip silently or invent success.
- Verify each affected spec's observable outcome separately from structural health, tests and architecture checks; record literal command/manual-action provenance and observed results under the skill's Implement and verify procedure. An unavailable runner/verifier leaves the guarantee it exists to establish unestablished — never passed — and `### Verification contingency` owns what that permits; a check not yet attempted stays pending. Prose-only changes use normal/adverse walkthroughs without claiming runtime execution.
- **Automated verification is the primary gate and is genuinely independent of the author's reasoning**: the checker does not share the author's assumptions. **Self-review** is a checklist pass over the author's own diff; it is cheap, useful for consistency, and is never described as independent verification.
- **Self-review is the normal route, and the author performs it directly.** Load the applicable review skill and apply its rubric to the actual candidate in the authoring context; a Git-derived fact obtained through the release owner is not a separate context. Reviewing does not revoke existing authority: correct in-scope defects, rerun the affected checks, and continue the authorized task. No reviewer packet, verdict or handoff is created for it.
- **An independent review runs only when the user explicitly authorizes that review.** A declared high-risk item may justify **recommending** one — a recommendation is never authorization — and no other condition authorizes it: not a completed work unit, a green check, a remediation, closure or pull-request preparation. On that authorization, a fresh verification context is dispatched against the named candidate with the applicable review skill and the evidence it must judge. It returns findings, not a delivery gate. Its absence is not a pending check and never a blocker.

### Verification contingency

A check is an **instrument**; the **guarantee** is what must be true. Its result is one of three, and they are never interchangeable:

- **Passed** — the check executed and its requirements held.
- **Failed** — the check executed and detected a breach.
- **Unavailable** — the check did not execute because of a tool defect, a missing dependency or an infrastructure failure. This result establishes neither compliance nor breach, and it is distinct from a check not yet attempted.

When a required check cannot execute:

1. Name the cause from the tool's own output, and separate an execution failure from a reported violation.
2. Name the guarantee the check exists to establish.
3. Identify an alternative procedure the governance already permits that establishes that guarantee to at least the same standard, and use the simplest one that does.
4. Record the unavailable instrument and its failure, the guarantee, the alternative and its observed result under the evidence obligations this file and the release workflow already state.
5. When no such procedure exists, the affected operation stays blocked on the **missing guarantee**, never on the instrument's unavailability, and the report names that guarantee.

**A prescribed instrument is substitutable by default.** A workflow naming a command, script or tool prescribes how the guarantee is established; naming it does not by itself make it non-substitutable, so a defect in it leaves the contingency route open. The route closes only where a rule declares the instrument non-substitutable or where its use is itself an essential security or contractual requirement.

**Authorization follows the guarantee.** An alternative establishing the same guarantee to at least the same standard proceeds without additional user consultation. A weaker guarantee, an unestablished part of the original requirement, a change to an essential contractual or security boundary, or a material residual risk needing acceptance is a material deviation and goes to the existing user-authority or authorized-exception mechanism that already governs that boundary; this section adds no approval of its own.

**Non-waivable guarantees block.** When an essential guarantee cannot be established by any permitted procedure, the affected operation remains blocked.

**Execution status and verification status stay separate.** The unavailable instrument is never reported as passed because an alternative succeeded: the alternative establishes the guarantee, and the record states both facts. A detected breach is never reclassified as a tooling exception.

**Precedence.** This section governs how a prescribed instrument is satisfied. It relaxes no guarantee an instrument exists to prove, and it overrides no rule declaring itself non-substitutable. A permission denial, an authorization boundary, a security control or a governance gate is not a tool defect and is never substituted; where a rule already reserves a decision to the user, an instrument failure decides nothing.

**A distributed defect does not suspend authorized work.** Distributed rules, tools and workflows are a shared baseline, not a release-coupled runtime. A defective distributed instrument does not by itself block completion of otherwise-verifiable authorized work, and synchronization is not a prerequisite for it. The ownership boundary survives unchanged: distributed content — a `core` region, a raw distributed file, a distributed skill or script, a merge-managed configuration and a managed instance alike — is never edited, patched, shadowed or replaced by a locally maintained copy to route around a defect, and `project`-region and destination-owned content stay the destination's own. The alternative must therefore be a procedure the destination holds outside the defective distributed content, and a correction to that content belongs to its upstream owner. A confirmed defect is disclosed with sufficient evidence to its owner through the destination's existing mechanism, and no work waits for its acknowledgment, registration, correction, review, merge, release or synchronization. Re-encountering a documented defect under materially unchanged circumstances reuses that reference and the still-permitted alternative without a duplicate report or further authorization, while each delivery keeps its own verification evidence; repeated use is never a permanent substitute for correcting the defect.

**Report it once, concisely.** The existing change record, verification evidence and release structures carry the unavailable instrument and its failure, the objective, the alternative, its observed result, any remaining limitation, and the applicable authorization or defect reference. No new form, artifact or per-check reporting is added, and an ordinary passing check needs nothing beyond the evidence already required.

### ODD protocol

1. **Authorize** — Does the request authorize a change? Read-only requests stay read-only. Findings do not silently expand authorization. Missing user-only authority blocks the affected operation and names the required decision.
2. **Explore** — Read the governing source and required dependents proportionately; trace changed concepts through owners and relevant consumers, tests and documentation. Do not substitute an unrelated repository-wide sweep. Report material evidence gaps.
3. **Resolve uncertainty** — Identify the requested observable outcome, the minimal sufficient change and task-relevant risks. Investigate accessible facts first; ask a focused question for a genuine user-only decision. Explain significant technical decisions and alternatives; unresolved requirements or user-owned decisions stop affected work. Before large-scale or costly work, warn the user, explain material alternatives and obtain any required authorization.
4. **Classify** — Work is small only when it is understood, risk-contained, and resumable from the request plus diff; all three conditions must hold. Non-small work is anything else. Counts of files, commands, tests, fixes, tasks, or requested todo lists never decide classification. Classify before writing; explain the route when material, uncertain or disputed.
5. **Track before the first write** — Read-only and small work create no durable feature artifact. For authorized non-small state-changing work, creating the governing task record from `.aicore/core/odd/tasks/_template.md` is the sole authorized bootstrap write. Create the durable feature from `.aicore/core/odd/features/_template.md` in the same bootstrap when no suitable owner exists. No other mutation precedes bootstrap. Never implement first and document retroactively; revise affected intent before resuming changed work. Keep the durable feature's affected requirements and derived status current. Continue already-authorized work without an automatic approval pause; unresolved authority and prerequisites still block affected work.
6. **Implement task by task** — Deliver coherent slices in dependency order, respecting owner gates. Define applicable acceptance checks and collect actual verification evidence with each task, not only at PR preparation. Tests and documentation ship with the slice. Follow the odd-workflow skill's implementation evidence procedure. When a relevant runnable deterministic test and a clear expected outcome exist, observe RED before implementation, then GREEN and refactor; otherwise record the actual exception and run proportionate checks. Never invent a runner or a test where none applies; do not add a test harness. Implementation is done directly by the primary agent; delegating a slice is a choice justified by a named reason, never a requirement, and the agent that performs the work also owns its checks and evidence. Report each slice's result, outcome evidence, check states and next ready task; when an existing feature's `## Tasks` row is marked `done`, report that transition at the time with the task outcome, commit, supporting evidence, applicable checks and their state, and next ready task. The feature document remains the sole task/status record. Loop here while tasks or applicable gates remain. When all task delivery gates and outcome checks are satisfied, report COMPLETE and advance to outcome verification in step 7. Read-only work reports implementation NOT APPLICABLE and advances to outcome verification without mutation.
7. **Close** — Before claiming any task done, verify the requested observable outcome separately from tests, architecture review or source-health checks; those checks do not substitute for outcome evidence. Apply the odd-workflow skill's completion procedure before a feature completion claim; anatomy validation or a green suite alone is insufficient. Report the verified outcome per requirement, every failed or pending check, and the next step; do not represent pending controls as satisfied. Reproduce a reported failure before deciding it already works. COMPLETE only with current required acceptance and outcome evidence; otherwise remain IN PROGRESS/BLOCKED or return to the affected earlier step. Small/read-only work verifies its outcome without creating a feature artifact. Exhausted verified authorized scope ends with ALL FINISHED; remaining authorized work continues under the transitions below.

These uncertainty and outcome controls apply to every task, including small and read-only work. Apply `### Scope changes and readiness` when scope, inputs or prerequisites change. The visible checkpoints below add no permission, approval gate, or user confirmation; they do not create another tracker or count threshold.

**Removed orchestration requirements versus retained correctness requirements.** What this workflow no longer requires is the _arrangement_: mandatory specialist delegation, per-mutation review checkpoints, dispatcher/admin handoff protocols, an independent semantic acceptor at closure, an independent pull-request gate, and a verdict document standing in for a check. What it still requires is _correctness_: the observable outcome's own verification, the applicable automated checks, honest recording of failures and pending controls, scope authority, work-unit commit discipline, and truthful delivery evidence. A missing reviewer is not a missing requirement.

**Local departures from official ODD.** AICore follows the seven-step protocol with local adaptations: optional independent review, Herald's exclusive Git and GitHub boundary, durable feature files and record retirement, no mandatory full memory mirror, and selective rather than universal verbatim history. Native receipt-driven development is not adopted. The dated comparison lives in `docs/architecture/odd-adoption-status.md` and ADR-0011.

#### Step reporting and transitions

- **Meaningful progress:** report material decisions, completed units, evidence, changed scope, blockers and next action as needed. Routine transitions and completed steps need no mandatory narration. Never hide a pending check, unresolved prerequisite or user-only decision.
- **States:** ✅ COMPLETE · 🟡 IN PROGRESS · 🚧 BLOCKED · ⏭️ NOT APPLICABLE/SKIPPED. The full vocabulary and presentation rules live in `.aicore/core/knowledge/agents.md` `### Message presentation`.
- **Continuation:** continue to the next ready task inside the active authorized scope; task completion is not a stop. A published pull request does not exhaust the authorized scope: the workflow continues through the delivery-evidence preparation and readiness verification, and the agent stops only when the pull request is reported ready for the user's merge decision or a genuine blocker is reported. A blocker is an unmet prerequisite preventing the affected operation: name its resolution owner and next action. Only a genuine user-only decision or permission requires a user stop with the exact user action. If the authorized scope is exhausted and verified, say `ALL FINISHED` with delivered scope, verification, deferred items, and next options; do not select unrelated work.
- **Skipped checks:** report applicable checks not run and the reason.
- **Transitions:** the seven steps are not seven implementation tasks; step 6 repeats task-level delivery. A failed check stays in step 6 unless it exposes a requirement or scope change, which returns to the affected earlier step. Step 7 is incomplete while any required check remains pending.
- **Prerequisites:** assess authority, scope and prerequisites before each unit; report changed scope or a material blocker. Configured permissions constrain available operations but do not establish workflow readiness.
- **Bootstrap and decision boundary:** creating the governing feature document is the sole bootstrap write. Execution review and decision-only stops after creation or material replanning are owned by `AGENTS.md` → Conventions; this protocol points to that owner rather than adding an automatic pause.

**Illustrative examples only — not execution evidence or actual feature status.**

- **Uncertainty resolved without a question:** `example-feature · T1 — Step 3 Resolve uncertainty — ✅ COMPLETE — uncertainty: whether small work requires a feature document. Evidence: this file, ODD protocol steps 4–5, explicitly makes small work artifact-free. Requested outcome: follow the authorized small-work route; minimal sufficient change: no feature-document creation. No additional research or user question required: the existing contract settles the artifact requirement; classification remains to be established. Next: Step 4 Classify against all three tests. Continuing.`
- **Authored slice, check pending:** `example-feature · T4 — Step 6 Implement task by task — 🟡 IN PROGRESS — implementation slice delivered; one required check still pending. Evidence: candidate slice and the pending check recorded in the example feature Log. Next: run the remaining command before advancing to step 7. No user action needed: the coordinator can run it. Continuing.`
- **Skipped check, not a completed phase:** `example-feature · T5 — Step 6 Implement task by task — 🟡 IN PROGRESS; RED/GREEN check ⏭️ NOT APPLICABLE — reason: prose-only slice has no applicable executable test; manual walkthrough is recorded in the example feature Log. Next: finish the pending walkthrough and record its outcome. Continuing.`

### Scope changes and readiness

The coordinator owns reassessment; workers stop affected operations and report gaps or stale evidence. On a correction, scope expansion or changed prerequisite:

1. **Stop affected work.** Invalidate affected readiness, assignments and evidence before further implementation; do not discard unrelated work or treat every correction as material replanning.
2. **Identify the delta.** Re-evaluate the requested observable goal against the proposed mechanism and scope. State what changed and justify each retained conclusion against current evidence; an earlier `COMPLETE` declaration alone is not content-specific evidence of exploration, resolved uncertainty or readiness for the changed scope.
3. **Re-explore affected context.** Read the affected authoritative sources and required dependencies, reassess relevant risks, and resolve affected uncertainty under protocol steps 2–3. Reclassify under step 4 if the delta affects understanding, risk containment or resumability. Preserve unaffected conclusions where their inputs and applicability remain valid; mandatory full/fresh-read obligations still apply.
4. **Revise the affected plan.** Update affected Specs, tasks, acceptance checks and assignments before affected work resumes, using the `odd-workflow` skill for feature-record operations. The revised plan is accompanied by an impact explanation stating the original requirement, the changed requirement, the difference, the affected specifications, implementation decisions, tasks, validations and evidence, the conclusions that remain valid, the revised plan and acceptance criteria, and the remaining risk; it is distinct from the execution review in step 5 and is delivered before affected implementation continues. Small/read-only work keeps corrected intent in the existing conversation/diff, without a feature artifact; a changed classification follows step 5's existing route.
5. **Apply decision-only stops.** Explain material changes, affected files, risks and genuine decisions under `AGENTS.md` → Conventions. Stop affected work for unresolved authority or prerequisites, not merely because a record was created or replanned. A clear requirement, authorized scope and accepted risk are distinct; communicate and obtain the user-owned decision when a material expansion or risk is not covered.
6. **Resume on current prerequisites only.** Check that the accepted inputs, conclusions, checks, owner gates and approval still cover the affected scope; obtain any required refreshed acceptance or approval before resuming. Report content-specific evidence and missing/stale prerequisites with their resolution owner and next action. Prior approval does not authorize an added scope merely because earlier steps were marked complete.

On resumption, authoritative repository owners and the governing task record establish current scope and state. Apply Resume active work above; verify recalled leads against authoritative files and create no competing tracker.

#### Finding-triggered impact reassessment

Apply this procedure when a user report, a failed check or a requested review exposes an omitted dependency, a companion surface, a shared failure pattern or a stale scope premise.

1. **Bound related discovery.** Follow the evidenced relationship from the finding to its owner, live consumers and relevant companions. Record inspected paths, exclusions with reasons and remaining unknown edges. Stay within the current task's scope; a needed read outside it is reported before access.
2. **Separate origin from escape.** Classify origin as `baseline`, `implementation`, `remediation` or `unknown`, separately from the evidenced escape point: `discovery`, `assignment`, `verification`, `review` or `unknown`, citing the evidence. Candidate comparisons may only bound the interval in which a defect appeared; do not claim an exact introducing edit without evidence. `unknown` is a valid and sufficient classification.
3. **Reconcile without expanding authority.** Carry newly evidenced impact into the existing scope-readiness steps above. Preserve checks whose inputs are unchanged; rerun the ones the change actually invalidated. Reassessment grants no additional writes, resources or approvals.
4. **Retain evidence once.** Record decisive classifications, limitations and lessons in the existing feature Log under the skill's Log-evidence rule. Small/read-only work retains the trace in its existing conversation/diff/report without a mandatory new artifact.

### Release workflow

Apply `.aicore/core/knowledge/release.md`. That file owns PR release readiness and delivery-evidence routing. This entry does not restate them.

### Incomplete evidence retrieval

Treat a truncation marker, omitted range, or unverified end of required content as an incomplete read, never as complete evidence. Recover the missing ranges with a reader the executing agent already holds the authority to use — a bounded search command when its runtime grants one, the file-reading tools when they return the whole range, or a supplied identity check when none of those is available — and never require one specific tool. For long lines, retrieve overlapping chunks and verify the overlaps and the end, not just line pagination. Bind the result to the source identity and verify the source remained stable across retrieval using an authorized identity check. Record the ranges, coverage, identity method and its limitations in the existing handoff. Neither a path nor an index hit proves content identity. If complete coverage or identity cannot be established, report the missing evidence and stop the affected conclusion without bypassing a denial. A requested independent reviewer retains its own verification duties.

### Task-specific navigation

Use the ODD classification and authorization rules above before choosing a change route. Start with the assignment's exact source paths, relevant dependencies, applicable runtime and skill; explore further only where the task or an unresolved fact requires it. Content already current in the run — injected instructions, a file read in this session, an existing artifact — satisfies an ordinary reading requirement for that content; re-read it only when it changed, when the available evidence is incomplete, or when its owner requires a fresh read. Search the named path first and expand only for an identified dependency or evidence gap. Mandatory full-guide, full-file and fresh-read obligations are unaffected and remain binding. This is the workflow router, not another task tracker.

| Task                                                      | Applicable read-pointers and boundary                                                                                                                                                                                                                                                                                                                                                                                                    |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Read-only explanation or inspection                       | Read the governing source and relevant dependencies. No feature artifact; unrelated read-only questions do not trigger blanket architecture reading. Architecture-dependent explanations follow the shared clean-architecture applicability rule.                                                                                                                                                                                        |
| Authorized non-small change                               | Read the governing `odd/tasks/<YYYY-MM-DD>-<feature-name>.md` through `## Log`, the assigned `S#` and relevant Log evidence, then the named source/dependency paths and owner procedure. Only authorized template-based creation of that document may bootstrap; no other mutation precedes it, and revisions precede affected work. Small work remains artifact-free.                                                                   |
| Implementation or architecture/conformance review         | Follow `.aicore/core/knowledge/agents.md` → Clean architecture → `.aicore/core/architecture/README.md` for responsibility-based common, shape and guide reading, expanding whenever required. Reviews retain full or fresh reads required for their scope. The implementing agent verifies against the owner text; a requested independent review may apply the `code-review` skill to the same owners.                                  |
| Testing design, test edit or test review                  | Follow `.aicore/core/architecture/testing/architecture.md` and its applicable stack guide. The implementing agent authors and runs the tests of its slice routinely. A requested independent review may apply the `code-review` skill's testing section. Execution/install grants remain runtime-owned.                                                                                                                                  |
| Formatting, linting, compiler or whitespace configuration | Read `.aicore/core/tooling/README.md`; it owns the canonical standards, their applicability, the project-owned settings and the authorized-exception route. A project's own configuration extends the canonical files and declares only what it owns — a local rule that duplicates a canonical one is a defect, and adopting the standard authorizes no repository-wide reformat, no dependency install and no change to existing code. |
| Dependency surface change                                 | Apply `.agents/skills/dependency-review/SKILL.md` before proposing a new package or changing a manifest or lockfile, and obtain user authorization before any installation.                                                                                                                                                                                                                                                              |
| Visual or accessibility design and review                 | Apply `.agents/skills/visual-review/SKILL.md` for a design brief or an audit of a rendered surface.                                                                                                                                                                                                                                                                                                                                      |
| Research or saved-evidence reuse                          | Read the project's configured catalog, matching topics, cited evidence and template; inspect applicability and freshness before reuse; investigate only the bounded gaps. Keep one durable record per topic and leave publication with its configured owner. Unrelated tasks do not require a research detour.                                                                                                                           |
| Incident identification                                   | Follow `.aicore/core/knowledge/agents.md` → Register-first identification and `.agents/skills/incident-workflow/SKILL.md`: symptom → incident problem → verdict, before evidence-only archive/pattern/KBA lookup after `no_match`.                                                                                                                                                                                                       |
| Incident escalation synthesis or routing                  | Follow `.aicore/core/knowledge/escalation.md` for the routing contract and sole matrix template; this project's ticket-system mappings and existing approval/execution owners remain authoritative.                                                                                                                                                                                                                                      |
| Historical context                                        | History, research and persona material do not replace current rules or become general prerequisites.                                                                                                                                                                                                                                                                                                                                     |
| Cache retrieval or code analysis                          | Apply `.aicore/core/knowledge/agents.md` → Applicable analysis tools and the root runtime's project bindings: use relevant exposed, authorized tools during exploration/review, report justified non-use or limitations, and retain scope, full reads and execution gates.                                                                                                                                                               |

Crosslinks locate owners; they do not require recursive rereading of every linked document. This does not waive runtime-required fresh/full reads or relevant dependency exploration. If a required pointer is missing, stop the affected operation and report the exact configured path, expected owner and missing evidence; never guess a replacement. An optional unconfigured/unavailable research catalog follows an explicit gap-reporting route instead.

### Feature document

One change owns one temporary authoritative record in `odd/tasks/`, not a second tracker. Its durable feature file describes the capability and enduring requirements, with status derived from ticks. The task Log holds material decisions, outcomes and evidence pointers, not an execution transcript; evidence required for future verification or acceptance never rests only in a gitignored temporary artifact.

Before creating or maintaining a feature record, load the `odd-workflow` skill and its applicable references. Use `.aicore/core/odd/tasks/_template.md` and `.aicore/core/odd/features/_template.md` as the sole templates. The skill owns record mechanics; this workflow owns authorization, classification and readiness.

### Durable feature file

Every non-small feature owns one durable file at `odd/features/<feature>.md`, named for the capability it describes and never dated, created from `.aicore/core/odd/features/_template.md`. The file is not a second tracker: it states what the feature is and lists the requirements it must satisfy, so the current definition is readable without reconstructing it from the change records. The record in `odd/tasks/` remains the single authoritative intent, task and status record for one change. The name states what the system provides and survives a change of implementation, and a change updates an existing durable file before creating a new one. Features worked before this rule are not retrofitted: a file is created the next time the feature is touched.

- **Shape and meaning.** A title, one paragraph, one status line and `- [ ] R#` requirements describe the enduring capability, not implementation activities or execution history. The skill's `### Create or update the feature file` owns semantic authoring and references; evidence belongs in the task or another durable owner.
- **Status.** The file carries one status — `achieved`, `partial` or `not started` — derived from the ticks: every requirement ticked is `achieved`, some ticked is `partial`, none ticked is `not started`. The value follows the ticks and is never an independent claim; the validator computes and reports that derived status.
- **Mark.** A requirement carries a mark only when the feature adopts a standard that already exists, and the mark records where this repository departs from it: `upstream` unchanged, `upstream · local detail` sharpened here, `upstream · narrowed` relaxed here, `local` added here, `local · conflicts` contradicting the standard. A feature explicit from this repository carries no mark.
- **Tick.** A tick asserts that the requirement currently holds. A change re-verifies only the requirements it affects: the tick stands when verification confirms the requirement, is removed with the failure and its cause recorded in the change's own record when a regression is established, and is removed with the uncertainty and its reason recorded there when verification could not be completed and the change could have affected the requirement. Only the change that delivers or re-verifies a requirement may set its tick.
- **Every change.** Read the affected durable file and record requirement changes and verification outcomes in the task. An implementation-only change that does not affect the enduring contract or its verified status requires no feature-file edit. Unaffected requirements are left alone.
- **Regression.** A change that establishes a ticked requirement is no longer satisfied removes that tick and records the failure and its cause in its own record. A change that cannot complete verification and that could have affected the requirement removes the tick and records the uncertainty and its reason.

Creation and update mechanics — the template path, the shape, the derivation rule, the affected-requirements duty and the validation command — live in the `odd-workflow` skill → `### Create or update the feature file`. The template's `## Guidance` section carries the mark vocabulary and the filling rules, and each requirement's upstream source and local owner live where that requirement cites them; this entry states the rule without restating that analysis.

### Template rule

Every repeatable artifact has exactly one template. Create a new file by copying its template and filling it; never reconstruct the format by research. If a second instance of a file type is needed and no template exists, create the template first.

| Artifact                   | Template                                                       |
| -------------------------- | -------------------------------------------------------------- |
| Feature document           | `.aicore/core/odd/tasks/_template.md`                          |
| Durable feature file       | `.aicore/core/odd/features/_template.md`                       |
| Feature-document checklist | `.agents/skills/odd-workflow/references/_checklist.md`         |
| Implementation stack guide | `.aicore/core/architecture/implementation/stacks/_template.md` |
| Testing stack guide        | `.aicore/core/architecture/testing/stacks/_template.md`        |

### Conflict

Identify both obligations, their authority, owner, impact, and disposition. Stop affected action while unresolved. Do not silently expand unrelated work. Do not defer mandatory safeguards or necessary touched-file rework because correction is complex. Route unrelated defects to their owner with explicit deferral; reporting is not accepted debt.

### Keep files small

Put each concern in its owner. Before growing a file, remove duplication or extract a named responsibility with purpose, applicability, owner, and an explicit read-pointer. Do not split by arbitrary parts.

A distinct workflow (for example release) belongs in `.aicore/core/knowledge/<flow>.md`, not in this ODD protocol file and not in an agent runtime. Move the obligation, replace the old body with a pointer, and inject the new home through `instructions` only when it replaces law that was already injected — never as a second copy. Project grants for that flow live in that file's `project` region or in `AGENTS.md` project extensions, not in this core protocol.

Extract skill support to `.agents/skills/<skill>/references/<concern>.md`; executable tooling to `scripts/`; a new common policy to `.aicore/core/knowledge/<concern>.md`. Architecture definitions belong in `.aicore/core/architecture/`: select through `.aicore/core/architecture/README.md`, read `.aicore/core/architecture/implementation/architecture.md`, applicable `.aicore/core/architecture/implementation/shapes/`, and the selected implementation guide in `.aicore/core/architecture/implementation/stacks/`; testing definitions belong in `.aicore/core/architecture/testing/architecture.md` and its selected stack guide. Agent runtimes retain authority, execution, scope, gates, dependency ownership, and reporting, not competing definition copies. Source-local ADRs explain decisions at the project's configured record location and are not required shared dependencies; their lifecycle and propagation gate are owned by `.aicore/core/knowledge/architecture-decision-workflow.md`. Move each obligation to one home, replace the old body with a pointer, update consumers, and verify links and clearance before deleting the old copy. Shared required extracts ship with clearance; source-local history is not a shared dependency.

New architecture paths and their consumers ship together through applicable clearance, including directory-root clearance where configured; an `apply` binds a newly cleared `raw` path and creates its absent target in the same run, while a new markerless region destination requires `init --bind-cleared` enrollment. Destination reconciliation remains destination-owned; pending reconciliation blocks acceptance. Documentation review does not establish implementation conformance or authorize application remediation.

Durable history lives at its owner: the feature document's `## Log`, the ADR, and `docs/architecture/history/`.
