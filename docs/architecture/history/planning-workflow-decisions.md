# Planning and Implementation Workflow — Analysis and Decisions

**Status:** Historical decision record — source contracts approved; D1–D15 selected for execution planning; delivery tracked in the implementation plan  
**Purpose:** Choose a faster, more reliable planning workflow first, then improve implementation definitions without weakening clean architecture or review.  
**Scope of this document:** Selected improvements and their rationale. The user delegated the implementation decisions and authorized improvement work. This document records that direction; the execution plan and current role/permission rules govern the actual edits and commands.

## 1. Executive recommendation

Adopt **contract-first planning and bounded, behavior-first implementation**.

- Finish enough discovery to understand the affected boundaries before presenting goals.
- Discuss and approve the user story's behavior first. Then confirm the implementation scope and plan classification without renegotiating the same behavior.
- Write a plan that fixes outcomes, architecture, public contracts, allowed files, prerequisites, and verification. Do not write the implementation twice, first as a plan and then as code.
- Validate the plan mechanically, then review its meaning independently. A valid document shape is not proof that the proposed solution is correct.
- Implement one coherent behavior slice at a time. Use real red–green–refactor for testable behavior changes; do not impose it on every documentation or cosmetic change. Assess all files included in the plan for design conformance and include their necessary architectural rework.
- Every new or changed behavior includes its documentation updates in the same plan and slice. Documentation is part of the delivered contract, not a later cleanup.
- Keep architecture review, test-architecture review, and test execution separate. None substitutes for the others.

The proposed sequence is:

**Story discussion and catalogue validation → user-approved feature contract → bounded implementation discovery → execution-scope decision → concise plan → writer review → independent planning review → execution authorization → behavior slices → completion review → archive → authorized release.**

This is neither “design everything before writing anything” nor “start coding without understanding the system.” Understand the system boundaries; defer internal details until the relevant slice.

## 2. What happened and what is established

### 2.1 Time and evidence

The user reports **more than five hours to write the plan files**. That is user-reported elapsed time, not an instrumented breakdown. No reliable attribution of minutes to individual reads, audits, pauses, or edits is available.

The conversation establishes repeated clarification, late discovery, inconsistent runbooks, corrective edits, and review loops. User pauses and cancelled tasks are not classified as avoidable waste.

### 2.2 Observed failure pattern

The workflow repeatedly became:

**Draft → discover a missing fact → ask → patch one symptom → rerun a narrow check → claim completion → discover another contradiction.**

Concrete failures included:

- Incorrect file counts and section ownership before full inspection of the affected material.
- Confusing the user's tested-file registration requirement with inventories and readiness-status systems.
- Adding destination work that the user did not request.
- Investigating heading, version, debt, permission, and fixture requirements after writing the plan.
- Keeping framework-specific definitions under an “agnostic” heading instead of translating their architectural meaning.
- Preserving obsolete definitions because a preservation check treated unchanged text as the success condition.
- Using token-presence checks to “prove” semantic requirements: a file can contain `execute()` without separating a use case from infrastructure.
- Repairing one reported occurrence without reviewing its callers, sibling rules, examples, story criteria, and authoring guidance.
- Sending auditors conclusions to confirm rather than interpretations they could challenge.
- Declaring the work complete while its recorded completion audit or archive lifecycle was still incomplete.
- Excessive process narration and repeated confirmation of already-settled choices.

The main cause was avoidable rework. Longer prompts, more files, or more audit rounds do not fix an incorrect starting contract.

### 2.3 Current repository evidence

| Surface | What the current text establishes | Consequence for the recommendation |
|---|---|---|
| `AGENTS.md` → Conventions | Repository facts should be established before escalation; only genuine user-only decisions reach `question`; mechanical checks are the orchestrator's responsibility | Investigate before asking. Keep semantic judgment separate from mechanical checking. |
| `.opencode/skills/plan-enforce/SKILL.md` → Goal lifecycle / User stories / Create new plan | Goals and classification need a combined confirmation; the creation sequence places the story gate afterward | Investigate story ownership before presenting the combined confirmation. |
| Programming template → Verification; consistency checklist → Verification parity; validator → `check_verification_parity` | The template illustrates goal-level bullets, while the checklist and validator require one verification checkbox per phase | Make examples and executable validation agree. Keep goal evidence within the phase-level verification rather than changing the invariant arbitrarily. |
| Phase template → Steps; programming template → anti-improvisation footer | Steps are described as individual commands or file edits, with every command/file/gate explicit | Preserve exact public contracts and scope, but distinguish those from implementation details the implementer should decide. |
| Validator → `check_placeholders`, `_split_table_row`, `_extract_writes_paths` | Instructional comments are rejected in generated artifacts; table cells split at pipes; phase Writes paths are semicolon-separated | Provide compatible examples and regression tests instead of teaching the writer by failed validation. |
| Consistency checklist → Loop rule; validator module documentation | Mechanical checks do not establish executor authority, goal meaning, or audit quality | Read and assess the content. Do not claim semantic success from exit 0. |
| `.opencode/agents/forge.md` → Warmup / Per-step execution | The shared contract and architecture rulebooks are read fresh; source reads are scoped to touched/replaced files; edits are gated | Retain rule comprehension; eliminate unrelated codebase reads and inconsistent gate routing. |
| `.opencode/agents/crucible.md` → Your Role | Test architecture can be reviewed with no implementation present, explicitly including a TDD red phase | TDD is possible through the designated executor; it is not inherently blocked by the implementer's lack of a runner grant. |
| Test executor's spec → Test Execution / Bash Grant Scope | Only the exact reviewed whole-suite command, explicitly dispatched, is authorized | Do not quietly use a targeted command. Focused execution is a separate, explicitly approved capability if later justified. |
| `plan-enforce` → Non-TypeScript test files / Completion | Python test phases require whole-suite exit 0 and separate architecture verdicts at their completion gate | A deliberately failing red checkpoint needs an explicit intermediate-state definition; it must not be mistaken for completed work. |
| `plan-enforce` → Dispatch bundle contract | The current handoff requires the full goals, runbook, and consumed outputs verbatim | Any narrower handoff mechanism needs an explicit rule change, not silent abbreviation. |
| `plan-enforce` → Resume (completion) / Plan lifecycle rules | Completion evidence and archival precede release; planning and completion audits are distinct | Fix lifecycle execution as part of workflow reliability, not as an optional post-merge cleanup. |

These references support proposed changes. They are not findings that authorize editing their sources now.

## 3. Important distinctions

### 3.1 Planning scope versus discovery scope

A complete plan needs a complete allowed write/delete manifest and known dependency contracts. It does not require understanding every unrelated implementation.

Read the full contents of the affected specifications before interpreting them. For source code, read the assigned unit and the dependencies whose implementation affects the change; an interface alone is insufficient when error handling, state, transactions, or side effects matter.

Broaden discovery when evidence crosses a boundary, not simply because a repository exists. Shared schemas, shared fixtures, public APIs, security behavior, and cross-layer refactors can legitimately require broader reads.

### 3.2 Architectural contract versus coding recipe

The plan must decide responsibilities, dependency direction, `execute()`, required folder organization, public inputs/outputs, permitted paths, and gates.

It usually should not prewrite private helper bodies, speculative algorithms, or long shell-quoted edit scripts. Those details increase drafting cost and become stale as soon as the implementer learns something new.

Exact commands remain appropriate for migrations, external operations, permission-sensitive execution, and genuinely deterministic mechanical work.

### 3.3 TDD versus test-first versus architecture

- **TDD:** run a meaningful failing test, implement the smallest passing behavior, then refactor and rerun. An observed red result is part of the evidence.
- **Test-first without observed red:** useful specification work, but not a demonstrated red–green cycle.
- **Clean architecture:** responsibility and dependency rules that need a separate review, regardless of test results.

Tests can faithfully verify the wrong requirement. A test and implementation that share the same false assumption do not validate the user's goal.

### 3.4 Preservation versus retaining mistakes

A before-copy establishes what changed, not what must remain correct forever. Preserve valid obligations and concrete examples; explicitly replace obsolete, contradictory, or noncompliant definitions.

Use dispositions such as **retained**, **translated**, **moved**, **replaced**, and **retired**, with reasons and the governing requirement. “Every old line survived” is not an architectural acceptance criterion.

### 3.5 Recommendations versus adopted policy

The user delegated selection of the best solutions and authorized the improvements, selected the standalone story skill and approved-criteria completion scope, approved the three feature contracts, and required rework for nonconforming files included in a plan. D1–D15 are selected and their delivery is tracked in the implementation plan. The conditional focused-runner option in D8 is deferred until a pilot demonstrates a need and its permissions are explicitly reviewed. Current permissions and mandatory gates continue to apply while the new definitions are planned and implemented.

### 3.6 The story defines the feature; the plan defines its execution

The user story owns the persona, business outcome, scenarios, observable acceptance criteria, and durable behavioral/architectural constraints. Establish those before planning a new or changed feature.

The implementation plan derives its feature goals from that approved contract and adds phases, owners, read/write paths, commands, dependencies, and verification gates. Those execution details are not all copied into the story. An implementation-only repair or refactor can trace to the existing behavior it preserves rather than inventing a new user-facing feature.

If planning discovers a needed behavior change, return to story discussion, show the delta, validate its collisions, and obtain replacement approval before changing the execution plan. Story approval does not establish that the feature is implemented and does not authorize code execution.

## 4. Planning improvements — D1 through D6

### D1 — Evidence-first, bounded discovery

**Status:** Selected; delivery tracked in the implementation plan  
**Recommendation:** Complete relevant discovery before drafting goals, without requiring a repository-wide read.

Before goal confirmation:

1. Understand the requested outcome in business terms.
2. Read the affected rulebooks and inspect the affected code boundaries.
3. Establish actual file ownership, existing stories, dependencies, fixtures, versions, documentation consumers, and lifecycle obligations.
4. Identify public contracts, required changes, and real user-only decisions.
5. Derive the intended write/delete set in memory.

Record facts in the existing plan Context or Current state section. Do not create a compulsory second discovery document.

**Alternative:** Draft immediately and use review to discover missing facts. Rejected: it reproduces the expensive repair cycle.

**Proof of improvement:** No goal confirmation depends on an uninspected file count, section label, or assumed ownership.

**Proposed homes:** `plan-enforce/SKILL.md` → Create new plan / Goal lifecycle; existing templates.

### D2 — One evidence-backed scope decision

**Status:** Selected; delivery tracked in the implementation plan  
**Recommendation:** Investigate options and recommend a solution before confirmation. With D13 adopted, approve the story contract first; the later combined plan goals/classification/scope confirmation references that contract rather than reauthoring it.

Separate the user's requested outcomes, necessary correctness dependencies, and optional enhancements. Present the actual affected files with the choices. Ask only decisions the repository cannot settle.

Routine factual corrections must be explained and reflected in evidence. Material changes to confirmed goals still require the existing goal-drift procedure; this proposal does not authorize silent scope changes.

**Alternative:** Repeated questionnaires while discovery continues. Rejected: the user becomes the repository analyst and must repeatedly restate the same intent.

**Proof of improvement:** The confirmation packet includes the researched story choice and any real architectural tradeoff, with no second discovery-driven story questionnaire.

**Proposed homes:** `plan-enforce/SKILL.md` → Goal lifecycle / User-story collision gate / Create new plan; `AGENTS.md` → question routing.

### D3 — Contract-sized plans and effective writer review

**Status:** Selected; delivery tracked in the implementation plan  
**Recommendation:** Write the shortest complete execution contract, then review its meaning before independent audit.

Each phase fixes its owner, prerequisites, input contracts, allowed writes, observable output, verification/executor, and failure conditions. Include the affected documentation paths and their owners in the same write/delete manifest. A phase boundary follows a coherent outcome or handoff, not an arbitrary number of files.

Before audit, read the entire candidate plan and check:

- The behavior matches the user's goal, not just the writer's wording.
- Every prerequisite is available when used, and every output has a consumer or proving check.
- Manifest, interfaces, examples, and story criteria agree.
- Documentation describes the intended behavior and its constraints, not the superseded behavior; changed examples, diagrams, and cross-references are accounted for.
- New gates account for existing fixtures and callers.
- Verification actually establishes the property claimed.
- Shell commands are syntactically valid and authorized.
- No stale rule, version reference, or lifecycle prerequisite remains.

Use one canonical phase command definition with references elsewhere. Avoid independently rewriting long inline scripts in goals, phases, stories, and audit prompts.

**Alternative:** Fully scripted file-by-file plans for all changes. Rejected as the default: it pre-solves implementation, multiplies duplicated text, and increases quoting and drift defects.

**Boundary:** Bounded engineering judgment may decide private implementation details. It cannot change required layers, `execute()`, folders, public contracts, permissions, or scope.

**Proposed homes:** `plan-enforce/SKILL.md` → anti-improvisation / Self-verification; programming and phase templates; consistency checklist.

### D4 — Independent semantic review and bounded recovery

**Status:** Selected; delivery tracked in the implementation plan  
**Recommendation:** Review neutrally, fix findings coherently, and trigger a reassessment after two failed independent planning audits.

The audit packet distinguishes user decisions, verified facts, and design interpretations. Do not instruct the auditor to accept the author's interpretation as “confirmed context.”

Require reading of the in-scope content. Mechanical checks supplement that reading; they do not replace it. Every semantic finding states the expected obligation, observed behavior, evidence, and proposed correction.

Read the changed rule's consumers and sibling definitions when fixing it. Do not repeatedly repair one keyword at a time.

After two failed audits, diagnose whether the scope, requirement translation, or proposed architecture is wrong before drafting another repair. Continue toward a clean required verdict after the reassessment. Escalate only a genuine user-only decision.

**Alternative:** Unlimited narrow audit/patch rounds. Rejected: repeated “PASS” claims on partial or stale scopes made the user discover the remaining defects.

**Boundary:** Two failures are a recovery trigger, not a waiver of independent review or permission to ship a failing plan. Existing stop-and-report rules remain in force until revised.

**Proposed homes:** `plan-enforce/SKILL.md` → Independent audit gate / Self-verification; `knowledge/agents.md` → evidence/report discipline.

### D5 — Compatible templates and a mechanical-only validator

**Status:** Selected; delivery tracked in the implementation plan  
**Recommendation:** Align templates, checklist, and validator, and prove compatibility with representative generated artifacts.

Keep the current phase-level verification parity; place each goal's proving evidence inside its owning phase verification. Make Writes examples show the accepted semicolon format. Keep author instructions clearly separate from rendered plan content.

Cover the observed failures with meaningful validator tests: rendered-template compatibility, permitted command text/table escaping, manifest equality, and goal/phase references. Inspect the existing validator tests before choosing new cases; do not add duplicate tests.

Do not expand the validator into an architecture or intent classifier. A grep for `execute()` or absence of a framework token cannot prove dependency inversion or correct generalization.

**Alternative:** Relax the checklist until inconsistent examples pass. Rejected: it removes correctness instead of fixing the source of drift.

**Proposed homes:** Existing planning templates, `_consistency-checklist.md`, `validate_plan.py`, and its existing tests.

### D6 — Concise updates and complete authorized execution

**Status:** Selected; delivery tracked in the implementation plan  
**Recommendation:** Report results and decisions, and continue authorized work until done or genuinely blocked.

An update states the result, material change, next action, and any blocker. Do not publish internal deliberation, narrate routine reads, or repeatedly restate unchanged goals.

The plan-creation execution-review stop remains deliberate. After execution is authorized, do not stop with “I will do the rest next” or ask whether to continue when no user decision is needed.

**Alternative:** Long process narration and repeated offers to proceed. Rejected: it consumes attention without improving evidence or outcomes.

**Proposed homes:** `AGENTS.md` → Conventions; `knowledge/agents.md` → Report discipline; implementation handoff guidance.

## 5. Implementation improvements — D7 through D11

### D7 — One behavior contract per coherent slice

**Status:** Selected; delivery tracked in the implementation plan  
**Recommendation:** Implement bounded vertical behavior slices within the approved architecture and manifest.

A slice is an observable behavior, not necessarily one file. A use-case change can require a domain port, an adapter, a caller, tests, and documentation to remain coherent.

Before implementation, identify its input, success result, business failure result, boundary behavior, affected callers, and documentation impact. Read those files and necessary dependencies; do not design unrelated future features. Update the affected durable documentation as part of that slice, under its declared owner.

Implement the smallest complete change satisfying the behavior. “Smallest” does not justify collapsing domain/application/infrastructure into one command handler or bypassing `execute()`.

**Alternative:** Global design of every private detail before the first implementation step. Rejected as the default: it produces speculation, excessive reads, and oversized batches.

**Proposed homes:** `plan-enforce` → phase design; `.opencode/agents/forge.md` → Migration Scope / Per-step execution.

### D8 — Real TDD where it earns its cost

**Status:** Selected; delivery tracked in the implementation plan  
**Recommendation:** Use red–green–refactor for testable new behavior and bug fixes; use characterization tests first for behavior-preserving legacy refactors.

Correction to the earlier advice: TDD does not require the implementer to own test execution. `.opencode/agents/crucible.md` explicitly supports a red phase without implementation. The orchestrator can dispatch the approved test executor between writing a test and implementing its behavior.

Proposed cycle:

1. **Red:** write one meaningful behavior test against the public contract; the designated executor runs an authorized command. Record why it fails. A broken environment, unrelated failure, or syntax error is not evidence of the intended missing behavior.
2. **Green:** implement only the assigned behavior through the required layers; execute the same approved check and establish it passes.
3. **Refactor:** improve design without changing behavior; rerun affected checks and review the dependency boundaries.
4. **Slice completion:** satisfy the required architecture, test-architecture, and execution gates. An expected red result never substitutes for a completed phase PASS.

For this proposal to be adopted, define the intermediate red checkpoint explicitly. Current phase-completion rules still require the reviewed whole suite to exit 0; an intermediate failing run cannot be silently accepted as that gate.

Apply the cycle according to change type:

| Change | Recommended approach |
|---|---|
| New business rule or use-case behavior | TDD against the use-case contract and ports |
| Reproducible bug | A failing regression test, then the fix |
| Legacy refactor with weak coverage | Characterize the current valid behavior, then refactor behind stable contracts |
| Parser or boundary rejection behavior | Table-driven valid/invalid cases and explicit error-contract tests |
| Documentation, rulebook reorganization, or cosmetic edit | Content/semantic review and appropriate checks; no artificial TDD requirement |
| Exploratory UI work | Clarify the intended interaction first; then test the accepted behavior at the prescribed frontend boundary |

For React, retain the existing unit definition: render the component with the real Hook and use case; mock the service boundary, not the Hook. TDD must not introduce a replacement test pyramid.

**Alternative:** Test-first writing with execution postponed until all code is written. Useful in some circumstances, but not an observed TDD cycle. Do not label it red–green without a witnessed red result.

**Runner recommendation:** Keep test execution with the designated executor. Initially use only current approved commands. If the whole-suite round trip is too expensive, propose one project-reviewed focused command family for that executor, with explicit permission review and a retained whole-suite completion gate. Do not expand the implementer's grants merely to reduce latency.

**Proposed homes:** `plan-enforce` → Verification command executors / phase gates; `.opencode/agents/forge.md`; `.opencode/agents/crucible.md`; project configuration only if a focused runner is separately approved.

### D9 — Impact-scoped reading and snapshot-aware reviews

**Status:** Selected; delivery tracked in the implementation plan  
**Recommendation:** Keep complete semantic review of affected content, but avoid rereading unrelated code and unchanged tests for every iteration.

Read scope includes:

- The assigned behavior and changed files.
- Relevant domain types, ports, and public interfaces.
- Concrete dependency code when its behavior affects the change.
- Direct callers, shared schemas, and fixtures affected by that contract.
- The tests proving the behavior and regression boundaries.
- Documentation that defines or explains the changed contract, including stories, user/developer guidance, examples, and cross-references.

Broaden scope when a shared dependency changes. A shared fixture can affect many tests, so narrowly reviewing only the new test is insufficient in that case. “Read interfaces only” is not a universal rule.

Record review scope and the reviewed file snapshot. Reuse evidence only for unchanged content and unchanged dependencies; a changed assumption, file, or dependency invalidates the affected evidence. A fresh-context agent needs the real contract and source pointers, not an unverified remembered summary.

Keep the current automatic edit gates until any different review schedule is explicitly adopted. Optimize the scope supplied to those gates; do not silently skip them or turn an old PASS into approval of a new snapshot.

**Alternative:** Reread the entire repository and every test after each edit. Rejected as the default: cost grows without proportional new evidence.

**Proposed homes:** Implementer warmup and read scope; architecture/test reviewer scope and reporting; plan handoff definitions. Any dispatch change must reconcile the existing verbatim-bundle rule.

### D10 — One effective architecture contract, not legacy exceptions

**Status:** Selected; delivery tracked in the implementation plan  
**Recommendation:** Normalize implementer/reviewer definitions before making TDD the default for applicable changes.

Every role must agree on the generic domain/application/infrastructure responsibilities, `execute()`, preserved folder design, selected language/library interpretation, and domain-error versus boundary-error behavior.

Distinguish static dependency direction from runtime call flow: a use case can invoke an injected port that performs IO without importing the concrete infrastructure implementation. “No concrete IO in application” is not “the application can never invoke an effect through a port.” Also distinguish returned business failures from boundary/programming exceptions, so negative-input tests and runner exception helpers do not conflict with the business-error contract. Serialization into a transport envelope belongs at the delivery boundary, not automatically inside the business operation.

Read the definitions as effective instructions, including examples and local extensions. A statement granting legacy names or arbitrary IO helpers must not undermine a required use-case boundary elsewhere.

Existing nonconforming code is not an exception that makes future code compliant. If that file is included in the plan, its necessary design rework belongs in the same plan, along with affected tests and documentation. Old rules may be replaced or retired when they contradict the accepted contract; record the translation and reason. No blanket “scripts are exempt” interpretation.

Normalize gate ownership too: frontend architecture goes to its reviewer, backend/script architecture to its reviewer, and test architecture/execution to their owner. The implementer's general “every step needs the frontend PASS” wording must not contradict its backend/Python-specific gate.

**Alternative:** Add another shared-contract citation while leaving conflicting detailed instructions effective. Rejected: that is how cosmetic conformance previously passed review.

**Boundary:** Include architectural rework for nonconforming planned files; do not expand into unrelated repository-wide migrations. Inspect the actual defect and supporting dependencies before deriving the manifest. Existing debt cannot be silently used to claim a clean verdict.

**Proposed homes:** `knowledge/agents.md`; `.opencode/agents/forge.md`, `atrium.md`, `bastion.md`, `crucible.md`; authoring and review references only where their contract changes.

### D11 — Evidence-bound completion and automatic lifecycle follow-through

**Status:** Selected; delivery tracked in the implementation plan  
**Recommendation:** Distinguish planning readiness, implementation correctness, test execution, completion, and release explicitly.

A planning PASS establishes the plan is coherent. It does not approve future implementation. A completion review binds to the final artifacts and must verify the user's actual requirement, including semantic structure and rejected definitions—not only token presence or old-line retention.

Map completion evidence by applicable layer: code architecture, test architecture, execution, and guidance/content. For docs-only work, establish why code/test execution layers do not apply instead of fabricating a test PASS.

Only then mark goals and acceptance criteria complete, write Outcome, set completed, archive, and verify the active copy is gone. Documentation conformance is part of that final-artifact evidence: code/tests passing cannot excuse stale instructions or examples. When release is authorized, send the evaluated packet to the release owner. Do not defer the archive until after merge or ask the user to remind the orchestrator.

**Alternative:** Check off goals after a validator pass and repair lifecycle metadata after release. Rejected: it allowed incomplete reviews and active plans to be described as finished.

**Proposed homes:** `plan-enforce` → Completion / Independent audit gate / lifecycle; audit reporting and orchestrator release handoff.

### D12 — Documentation is part of every behavior change

**Status:** Selected; delivery tracked in the implementation plan  
**Recommendation:** Discover, plan, update, and semantically review documentation together with every new or changed behavior.

The user explicitly requires documentation updates when implementing new things or changing existing things. It is not an optional follow-up after code is declared done.

During discovery, identify the existing documents that define or consume the affected contract. Read them before deciding the implementation and documentation scope. If a new behavior has no durable documentation home, establish the appropriate home in the same plan, following the existing story/ownership rules.

Record the actual documentation paths, the responsible owners, the intended changes, and the proving review in the plan. This can live in the existing Current state/Behavior change/phase fields; no compulsory separate documentation-plan artifact is needed.

Documentation impact includes:

| Changed concern | Documentation to inspect and update |
|---|---|
| Feature behavior and failures | Existing user story, acceptance criteria, and relevant user/developer guidance |
| Public API, input/output, or configuration | Interface documentation, examples, setup instructions, and callers' documented assumptions |
| Architectural responsibilities or folder conventions | Shared contract, relevant language/library interpretation, diagrams, and authoring/review guidance |
| Agent authority, routing, or workflow | Runtime specs, shared rules, affected skills, and their templates/checklists |
| CLI/tool behavior | Skill usage, command examples, exit contracts, and troubleshooting |
| Renamed or relocated surface | Links, cited sections/symbols, index entries, and all affected examples |

At slice completion, read the updated documents against the implemented behavior. Verify that they explain the actual contract and that no old instruction, diagram, example, or link contradicts it. Presence checks and matching file counts cannot establish this.

**Alternative:** Deliver code first and defer documentation. Rejected: it leaves future agents and users working from stale contracts, reproducing the defects in this session.

**Boundary:** Update documentation because of actual dependency on the changed contract, not through unrelated repository-wide rewrites. Documentation does not grant authority to broaden implementation scope or publish under another role's permissions. Keep durable product guidance separate from temporal audit evidence.

**Proposed homes:** `plan-enforce` → discovery / manifest / phase design / completion; implementation and documentation-owner definitions; semantic review checklist.

## 6. Recommended operating models

### 6.0 Story-first discussion

1. Read the index and enumerate the actual story files; reconcile missing bodies and unindexed stories.
2. Read every story body for semantic comparison, with each story's status respected. This is a bounded catalogue read, not a whole-codebase scan.
3. Recommend UPDATE, CREATE, or a supersession relationship based on persona, scenario, goal, and acceptance criteria—not path overlap alone.
4. Discuss the desired behavior and preview the proposed contract or revision. Persist a draft only when its artifact write is authorized; an existing approved contract is not silently overwritten during discussion.
5. Validate the proposed contract's structure, index consistency, and semantic collisions against the full catalogue.
6. User approval establishes the contract for planning; implementation evidence, not approval, establishes acceptance checkmarks.
7. Hand the selected story and its approved criteria to `plan-enforce`.

### 6.1 Planning

1. Start from the approved user story and identify the implementation outcome and affected contracts.
2. Inspect affected content, documentation, and dependencies; resolve repository facts.
3. Present researched options only for real user choices, with a recommendation and affected files.
4. Assess design conformance of the planned files and include necessary rework/supporting paths; confirm goals, classification, and delivery criteria together.
5. Draft the manifest and coherent phases from those contracts, including documentation updates and their owners.
6. Validate shape, then perform writer semantic review.
7. Obtain neutral independent review and remediate coherently.
8. Present execution review and stop as the current policy requires.

### 6.2 Implementation

1. Receive the authorized slice and its contracts.
2. Read applicable architecture definitions and affected source/test boundaries.
3. Choose TDD, characterization-first, or direct verification according to the change type.
4. Implement through the prescribed layers and paths, and update the slice's affected documentation under its declared owner.
5. Run authorized checks with the designated executor and obtain the required independent architecture verdicts.
6. Review the complete slice's interfaces and callers, then continue the next authorized slice.
7. At completion, reconcile evidence and story criteria, archive, and perform release only on authorization.

These are proposed operating models, not new executable grants.

## 7. Examples of adequate verification

| Requirement | Insufficient check | Required meaning to establish |
|---|---|---|
| Generic architecture section | Heading exists; framework keyword absent | The section defines responsibilities, folder organization, and dependency constraints derived from the concrete rules |
| Use-case boundary | `execute()` appears in the file | The named use case has an explicit input/output contract, depends on ports, and does not parse CLI input or perform concrete IO |
| React interpretation | The word React is under another heading | Component + real Hook + use case remain the unit; the service is mocked; no Hook is called from the ordinary `execute()` function |
| Python conformance | The suspension sentence is gone | Every detailed rule and example obeys the layers and required entry point; module/IO conventions do not act as an exemption |
| Preservation | Every old line is still present | Valid obligations survive; obsolete or conflicting ones are deliberately replaced/retired, with their architectural meaning accounted for |
| Test-first behavior | A new test file exists | The executor observed the intended failure before the fix and observed the same behavior passing afterward |
| Documentation is current | Files or links exist; a Change log line was added | Read the changed guidance, diagrams, and examples against the actual contract; no superseded instruction survives |
| Completion | Validator exit 0 or a planning PASS | Applicable final-snapshot reviews and execution evidence satisfy the user's goals; lifecycle records match reality |

## 8. Rollout order

### First — repair planning mechanics and review quality

Prioritize D1–D6, D11, and D12. Align the templates/checklist/validator and discovery/confirmation order before adding new workflow machinery. Include documentation impact and semantic documentation review in the workflow. Preserve the validator's documented mechanical invariants and public interface; do not preserve a demonstrated parser defect merely because it is existing behavior.

### Second — normalize implementation definitions

Apply D7, D9, and D10. Establish coherent slice contracts, read scopes, architecture routing, and effective language profiles. Keep existing execution permissions and automatic gates.

### Third — pilot real TDD and measure feedback cost

Apply D8 on a bounded, testable change with the existing approved executor. Record red/green evidence and the whole-suite round-trip cost. Only then decide whether a narrowly reviewed focused-runner capability is worth adding.

Do not start with a repository-wide source refactor, a new orchestration framework, or broader implementer permissions. These are not necessary to fix the observed planning failures.

## 9. How to tell whether the changes helped

For a small pilot set, record:

- Time spent in discovery, drafting, writer repair, independent review, and implementation feedback separately.
- Number of user decision rounds and whether each required user authority.
- Planning audit rounds and recurring defect categories.
- Files read and reread, with the reason broader scope was necessary.
- False or stale PASS claims discovered later.
- For TDD, the intended red failure, green result, and execution turnaround.
- Whether the completion/archive/release sequence finished without a user reminder.
- Whether documentation updates shipped with the behavior change and whether stale guidance was discovered afterward.

Use existing local plan/output evidence; do not add a metrics service. Compare similar task types rather than claiming a universal time target. A complex architecture decision can justify more discovery than a routine bounded fix.

Desired outcome: routine plans need a coherent first draft and a bounded remediation path; the user does not have to repeatedly find omitted requirements. Shorter documents alone are not success.

## 10. Decision record

The user selected the workflow direction, approved the three story contracts, and required D15's architectural rework for nonconforming planned files. Feature-contract approval does not establish implementation acceptance; all workflow changes remain pending until source surfaces and evidence establish completion. These are decision items, not an execution plan's goal count.

| Decision | Status | Recommended choice |
|---|---|---|
| D1 — Discovery | Selected; delivery tracked in the implementation plan | Evidence-first, bounded to affected contracts |
| D2 — Confirmation | Selected; delivery tracked in the implementation plan | Research first; one combined scope/story/classification decision |
| D3 — Plan and self-review | Selected; delivery tracked in the implementation plan | Contract-sized phases; semantic writer review before audit |
| D4 — Audit recovery | Selected; delivery tracked in the implementation plan | Neutral audits; two failed planning audits trigger reassessment, never a waived gate |
| D5 — Templates and validation | Selected; delivery tracked in the implementation plan | Compatible examples and regression tests; validator remains mechanical |
| D6 — Communication/execution | Selected; delivery tracked in the implementation plan | Concise result updates; complete authorized work unless genuinely blocked |
| D7 — Implementation slices | Selected; delivery tracked in the implementation plan | One coherent observable behavior per slice |
| D8 — TDD | Selected; delivery tracked in the implementation plan | Real red–green–refactor where useful; designated authorized executor; no automatic grant expansion |
| D9 — Reads and reviews | Selected; delivery tracked in the implementation plan | Impact-scoped full content review; snapshot-aware evidence; retain current edit gates |
| D10 — Architecture definitions | Selected; delivery tracked in the implementation plan | One effective contract; replace contradictory legacy rules; normalize gate ownership |
| D11 — Completion | Selected; delivery tracked in the implementation plan | Final-snapshot evidence, criteria reconciliation, and archive before release |
| D12 — Documentation | Selected; delivery tracked in the implementation plan | Documentation impact, updates, and semantic review belong to the same behavior change |
| D13 — Story-first workflow | Selected; delivery tracked in the implementation plan | Standalone `user-story` skill; approved behavior before implementation planning |
| D14 — Story collisions | Selected; delivery tracked in the implementation plan | Read the entire story catalogue; mechanical consistency plus semantic collision analysis |
| D15 — Planned-file design conformance | Selected; delivery tracked in the implementation plan | Rework nonconforming files included in the plan, with necessary tests/docs and declared supporting paths |

## 11. Story-first additions — D13 and D14

### D13 — A standalone user-story discussion skill

**Status:** Selected; delivery tracked in the implementation plan  
**Recommendation:** Add `.opencode/skills/user-story/SKILL.md` for collaboratively creating or updating an approved feature contract before planning.

The local skills catalogue has no equivalent standalone story-discussion workflow. `plan-enforce` currently performs story selection and negotiation during planning. Move that pre-plan responsibility into `user-story`; retain execution planning, goal traceability, verification, and completion lifecycle in `plan-enforce`. Reuse the canonical story template instead of creating a competing format.

Example invocation: “Use `user-story` to define this feature” or “Update the story for this behavior change.” The skill reads the catalogue, recommends the correct owner story, discusses the behavior with the user, previews the proposed contract, validates it, and obtains approval before handing it to planning.

An approved story is a feature definition, not proof of implementation. A draft is not an approved planning contract. Acceptance checkmarks remain evidence-based; user approval alone never marks an unimplemented criterion complete.

For an active-story revision, compare old and proposed behavior, preserve the existing approved contract until the replacement is approved, and update the index and bounded feature Change log together. Story-only discussions need a legitimate change-record form that does not require a fabricated implementation-plan slug.

**Completion policy selected by the user:** A plan reconciles all criteria it commits to deliver or modifies, and checks that previously established behavior has not regressed. Other legitimate approved commitments remain in the active story; they are not removed merely because one plan delivers only part of the feature. This differs from the current blanket rule that no unchecked criterion may remain in any touched story and must be reconciled in the skill, checklist, and story-audit rules before use.

**Alternative:** Keep story discussion embedded in `plan-enforce`. Rejected as the preferred design: the user wants to invoke discussion independently and approve the feature before generating execution artifacts.

**Scope boundary:** No bulk splitting, renaming, or reorganization of existing large stories. Do not create implementation plans, modify application code, or run application behavior inside this discussion skill. Read-only mechanical story validation remains limited to the orchestrator's authorized tools and commands.

**Likely homes:** new `user-story/SKILL.md`; `plan-enforce` story handoff and template/checklist; `AGENTS.md`; story-audit rules; README; UPDATE the `plan-enforce` story and CREATE a story for the new skill only after explicit story choice.

### D14 — Catalogue-wide story validation and collision analysis

**Status:** Selected; delivery tracked in the implementation plan  
**Recommendation:** Enumerate the catalogue, read all bodies, and evaluate collisions before approving a new or revised story.

At the initial catalogue review, nine feature-story files plus the index were enumerated and all nine bodies were read. That established ownership: planning belongs to `plan-enforce`, architecture definitions to `clean-architecture-contract`, and pytest runner authority to `python-pytest`. The subsequently created `user-story` contract adds the standalone discussion feature; the initial inventory is historical evidence, not a current catalogue count.

The skill must repeat catalogue discovery when invoked. Do not assume an earlier inventory remains complete. Draft and superseded stories participate with their status understood; a superseded rule is not treated as current authority.

| Collision or inconsistency | Required assessment |
|---|---|
| Duplicate ownership | Two stories promise the same actor/trigger/outcome; recommend updating the canonical story or explicitly establishing distinct scopes |
| Contradiction | Paired criteria or governing decisions cannot both hold; report the actual statements and obtain a disposition |
| Extension or supersession | New behavior broadens or replaces an existing contract; show the old-to-new relationship before approval |
| Dependency | One story needs another's outcome; record the relationship, not a duplicate acceptance definition |
| Shared affected files | Use as an ownership clue; it is not by itself a semantic collision or a concrete write collision |
| Index/body drift | Missing file, unindexed story, wrong title/status/areas, or malformed body; report exact inconsistencies |

Validate the story's meaning and observable criteria as well as its mechanical shape. A script can establish index/body consistency; it cannot determine whether two differently worded scenarios conflict. Do not introduce a keyword-only collision detector or claim collision-free status from a validator exit code.

**Mechanical approach:** Reuse the existing story-index validation functions. A standalone entry point can be added to the existing validator if needed, without creating a separate validation engine or requiring a dummy plan merely to validate stories. Any such code requires a declared plan scope and tests; semantic catalogue review remains the agent's responsibility.

**Alternative:** Filter only by epic or path and read the selected candidates. Useful as an initial locator, but insufficient for the requested all-story collision review.

**Scope boundary:** Assess all stories, but edit only the selected contract and the index unless a separately authorized collision resolution requires another story change. Existing story splitting remains a future task.

## 12. Approved story contracts

### New story — `user-story`

The approved contract is `user-stories/user-story.md`, with status `active` and unchecked implementation criteria. It defines catalogue review, CREATE/UPDATE recommendation, discussion, contract preview, semantic collisions, approval, and the planning handoff. It does not own implementation or plan completion.

Catalogue assessment found no existing story for that independent discussion feature. Its dependencies are the planning lifecycle and shared architecture contract; common affected files do not make it a duplicate of either.

### Approved UPDATE — `plan-enforce`

Current story: `user-stories/plan-lifecycle-governance.md` (Plan lifecycle governance). The UPDATE heading preserves the historical story name.

The approved revision keeps planning-lifecycle ownership and replaces blanket touched-story completion with approved-criteria scope. Its behavioral contract is:

- Planning starts from an approved story or an existing approved behavior to preserve; the feature intent is not first invented inside phase instructions.
- Bounded code/documentation discovery precedes plan-scope confirmation, and the selected story is not renegotiated as a second story-choice questionnaire.
- Plans fix behavior, architecture, public contracts, permitted files, executors, and verification, without prewriting private implementation or requiring arbitrary file-count phases.
- Templates and the validator agree on mechanical structure; the validator associates index metadata with the correct story row and accepts valid escaped command-table content.
- Semantic writer review and independent review examine the actual content. Two failed planning audits trigger reassessment rather than serial keyword repairs.
- An observed expected-red checkpoint is intermediate; completion still requires the designated executor's approved whole-suite result and the separate applicable architecture verdicts.
- Completion reconciles the criteria the plan commits to deliver or materially changes, checks relevant established behavior for regressions, and preserves other approved commitments. Current criteria asserting that every touched-story criterion must be checked are replaced, not retained as competing rules.
- Documentation updates are in the same manifest/slice. Final evidence, Outcome, and archive precede an authorized release.
- Discovery assesses the design of files included in the plan and includes necessary rework, supporting paths, regression evidence, and documentation before implementation.

The Goal/Scenario and directly affected acceptance criteria have been revised. Unchanged acceptance evidence is retained; revised/new behavior remains unchecked until implemented. The story has not been split.

### Approved UPDATE — `clean-architecture-contract`

The approved revision keeps layer names, folder design, `execute()`, language/library interpretation, and the frontend pyramid. Its additions concern implementation and review:

- The implementer reads the shared contract and the applicable role/language definitions before an assigned behavior slice, with code/test/documentation reads scoped by actual dependency impact.
- Gate routing agrees for frontend, backend/script, and tests; an unconditional frontend-PASS instruction does not override a backend/Python gate.
- Review evidence records its source scope and snapshot; passing tests do not substitute for dependency/responsibility review, and unchanged evidence is reused only when its dependencies remain unchanged.
- A use case may invoke IO through an injected port while concrete IO and transport serialization remain at the appropriate edge. Returned business failures are distinguished from boundary/programming exceptions.
- Legacy implementation names or arbitrary IO helpers are not exemptions. Files included in a plan that violate the design require their necessary rework in that plan; unrelated repository-wide migrations are not implied.

The planning workflow owns phase design and TDD checkpoints. This story owns architectural invariants and role interpretation, so neither becomes a duplicate authority for the other.

### Implementation boundary

The user approved all three contracts, and the story files/index now reflect the revisions. This establishes the target behavior, not implementation acceptance or permission to bypass the existing execution-review turn.

## 13. D15 — Rework nonconforming planned files

**Status:** Selected; delivery tracked in the implementation plan

Read the files included in a plan against the approved architecture/design, rather than inferring conformance from their names, size, or passing tests. If a planned file violates that design, include the necessary rework in the same plan. Assess the actual supporting dependencies and add their required paths, tests, and documentation to the manifest before editing. If discovered after the manifest is agreed, follow the applicable scope-change process first.

Do not grandfather noncompliance, preserve an obsolete architecture merely because it is current, or substitute a small behavioral patch for necessary design correction. Conversely, do not turn this into an unrelated repository-wide rewrite: the boundary is the planned nonconforming files and the support needed to make them conform.

Proving contracts: `user-stories/plan-lifecycle-governance.md` **AC31** and `user-stories/clean-architecture-contract.md` **AC13**.

## 14. Next action

Inspect the actual architecture of files the workflow plan will modify, including the validator, then derive the rework/supporting-file manifest and execution plan from the approved criteria. No new execution plan has been created. Keep the selected planning improvements, implementation definitions, TDD pilot, and same-change documentation requirement; do not add existing-story splitting to this task.
