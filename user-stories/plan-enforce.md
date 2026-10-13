# User story — plan-enforce

> **Created:** 2026-09-10
> **Title:** Plan-enforce
> **Status:** active
> **version:** 1.3.0
> **Epic:** plan-governance
> **Affected areas:** `.opencode/skills/plan-enforce/`, `.opencode/skills/user-story/`, `.opencode/skills/git-commit/`, `.opencode/skills/git-pr/`, `.opencode/skills/op-agent-creator/`, `.opencode/skills/op-model/`, `.opencode/skills/op-skill-creator/`, `AGENTS.md`, `knowledge/agents.md`, `README.md`, `user-stories/`, `.opencode/agents/atrium.md`, `.opencode/agents/bastion.md`, `.opencode/agents/crucible.md`, `.opencode/agents/forge.md`, `.opencode/agents/marshal.md`, `.opencode/agents/sentinel.md`, `.opencode/agents/vault.md`, `opencode.jsonc`

## Persona

- Cipher 🔓 (Lead Orchestrator), who writes, reviews, executes, and archives plans and must not skip executor assignment, independent audit, the human review turn, or story-criterion disposition.

## Goal

- **G:** Derive an evidence-grounded, contract-sized execution plan from approved story behavior, with authorized verification, required design rework, and completion scoped to the criteria the plan commits to deliver or materially changes.
  - Done when: affected code/documentation is inspected before scope confirmation; goals trace to approved criteria; nonconforming planned files have explicit rework; every verification command has an authorized executor; planning and completion reviews are independently evidenced; the execution-review turn precedes implementation; committed criteria are fulfilled without deleting other story commitments; and final evidence, Outcome, and archival precede release.

## Scenario

- After the user approves a new or revised story, Cipher 🔓 (Lead Orchestrator) inspects the implementation and documentation boundaries, selects the delivery criteria, and writes contract-sized phases with complete manifests and authorized executors. Required architectural rework is included for nonconforming planned files. The user receives execution review before implementation. Expected-red test evidence remains an intermediate checkpoint, not completion. The final review fulfills the declared criteria and checks relevant established behavior for regressions; other legitimate story commitments remain recorded. Outcome and archival precede an authorized release.

## Acceptance criteria

- ✅ **AC1:** Every phase verification command has exactly one executor-command table row with exactly the `Executor` and `Command` columns, and a missing, empty, or malformed table is rejected.
- ✅ **AC2:** The validator checks declared traceability only; phase review separately verifies executor authority against the relevant agent rulebook or permission model.
- ✅ **AC3:** Python test edits require the project's reviewed whole-suite command, a backend implementation `[PASS]`, and a test-architecture `[PASS]` or `[FAIL]`; an uncertain verdict is not acceptable.
- ✅ **AC4:** Goal trace, manifest equality, and verification parity are each enforced by a distinct, named validator finding.
- ✅ **AC5:** A completed plan requires an audit block with a non-empty auditor, a `[PASS]` verdict, and a non-empty date; an unknown or `[FAIL]` verdict fails.
- ✅ **AC6:** The skill documents the self-verification loop, the independent-audit gate before a ready report or implementer dispatch, the fail-closed fallback when no auditor is available, and the pass-count report; both plan templates carry a compliant audit block.
- ✅ **AC7:** After plan files and self-verification, the orchestrator sends the execution-review message and does not dispatch an implementer in that turn.
- ✅ **AC8:** The execution-review message is human-readable prose per goal in the order Issue, Goal, How, Files; a recap table does not replace that prose.
- ✅ **AC9:** Both plan templates carry the same per-goal Issue / How / Files layout.
- ✅ **AC10:** The root runtime spec forbids an implementer dispatch in the same turn as the execution-review message, and forbids a corrective, release, or scope-change question without that file list.
- ✅ **AC11:** Independent audit `[PASS]` and the stash gate still apply on the later execution turn.
- ✅ **AC12 — Approved story input:** Pre-plan discussion, complete catalogue review, and explicit CREATE/UPDATE/contract approval belong to the story skill. Planning consumes the accepted contract and its selected criteria before deriving implementation goals and never silently invents feature behavior inside phases.
- ✅ **AC13 — Criterion-scoped reconciliation:** Before completion, every declared delivery criterion and every criterion materially changed by the work is evidence-established as resolved through the story's `## Proof` section; relevant previously established behavior is reviewed for regressions. Other legitimate unfulfilled commitments remain in the story and are not removed merely because this plan delivers only part of it. Completion also confirms the plan respected every `## Constraints` entry; constraints are never delivered and never ticked.
- ✅ **AC14 — Completion boundary:** Outcome and archival are blocked by an unmet committed criterion, a relevant regression, a violated `## Constraints` entry, or missing/adverse final-snapshot evidence — not solely by an unrelated unselected pending criterion in the same story. Material discovery that expands delivery scope is reflected in the approved story/plan before editing.
- ✅ **AC15 — Evidence-bound story audit:** Independent story audit verifies criteria against the plan's declared delivery scope and actual evidence, reports stale or falsely checked criteria and release-event criteria, and never auto-checks a box. Pending unselected commitments are distinguished from failed delivery.
- ✅ **AC16:** Release events are not feature acceptance criteria; release policy stays enforceable and actual release events live in change-log and PR history.
- ✅ **AC17:** For a project with an approved whole-suite runner, the plan assigns the test architect that suite command rather than requiring a new grant per test file; its phase gate needs the whole-suite command to exit 0 plus a test-architecture `[PASS]`, and the backend architect remains the Python implementation auditor.
- ✅ **AC18:** Mandatory lifecycle rules are separated from project-specific extensions while preserving the plan, story, audit, executor, and review-turn obligations.
- ✅ **AC19:** Authoring procedures, degraded checks, examples, and portable references agree with the current mandatory source rules.
- ✅ **AC20:** An admitted finding is an evidence-bounded packet — confirmed goal, governing normative clause, actual responsible actor and the shipped path it controls (distinct from a helper or fixture), expected versus observed behavior, affected scope, a reproduction or static fact, severity with literal output, and an explicit keep / fix / reject-scope decision; review classifies it as a requirement defect, documentation drift, or supplemental concern, and no speculative blocker or growing helper/test matrix is admitted.
- ✅ **AC21:** Every dispatch prompt is fail-closed checked for the complete verbatim bundle — Subject, full `## Goals` block, full phase file, and re-pasted prior-phase values — and carries the question-routing prohibition and the stop-and-report contract; a summarized goal or paraphrased step is never dispatched.
- ✅ **AC22:** Completion is a layered matrix on the current snapshot — code architecture, test architecture, test execution, and model/guidance verdicts, each with its scope and verdict; a passing execution never substitutes for a required architecture verdict, and a missing or adverse layer blocks completion.
- ✅ **AC23:** A planning-readiness audit and a completion audit are distinct: the completion audit evaluates the finished work at its final candidate and is required before `## Outcome`, goal checkmarks, and archive, so a planning `[PASS]` or an execution-only result never substitutes for it.
- ✅ **AC24:** Replaced, superseded, or newly wired behavior requires a recorded legacy/dead-code sweep: search for the superseded implementation, remove dead code and stale wiring, and record the sweep as completion evidence, so no validated-but-unread field, dead symbol, or stale mapping survives a completed change.
- ✅ **AC25:** When asked to analyze all pending changes, every nonignored modified, deleted, and untracked path is enumerated and given an evidence-based `ship` / `fix` / `drop` disposition from inspected content before any scope question; manifest absence never proves a path unrelated, and completion is never claimed beyond the reviewed scope.
- ✅ **AC26 — Discovery and phase contracts:** Bounded inspection of affected code, rulebooks, stories, documentation, and dependencies precedes the combined plan-scope/classification confirmation. Phases specify responsibilities, interfaces, allowed writes, outputs, and gates rather than prewriting private code or requiring arbitrary file-count phases.
- ✅ **AC27 — Compatible mechanical validation:** Representative rendered templates satisfy the documented validator invariants; valid escaped pipes do not become extra table columns; story metadata is matched to that story's own index row. The validator does not claim semantic correctness or executor authority from shape alone.
- ✅ **AC28 — Semantic review and recovery:** Writer and independent review read the actual in-scope content against approved behavior. Handoffs separate user decisions, facts, and interpretations; two failed planning audits trigger coherent reassessment without waiving the independent `[PASS]` gate.
- ✅ **AC29 — Expected-red checkpoint:** A behavior slice may record the intended failing test through the designated executor's authorized command before implementation. Expected red is not a phase, goal, or acceptance `[PASS]`; final green, applicable architecture verdicts, and the reviewed whole-suite completion gate remain required.
- ✅ **AC30 — Same-change documentation:** Actual affected documentation paths, owners, and proving semantic review are in the same plan/manifest as the behavior change. Final guidance, examples, diagrams, and links agree with the delivered contract.
- ✅ **AC31 — Nonconforming planned files:** During discovery, planned files are assessed against the approved design; necessary rework, supporting paths, tests, and documentation are included in the same plan before execution. Existing noncompliance is not an exemption, and a passing behavior test cannot substitute for architectural conformance. New required paths discovered later are added through the applicable manifest/scope process before editing.

## Proof

- AC1 → `.opencode/skills/plan-enforce/scripts/test_validate_plan_phase_structure.py` verify-table rejection cases · `uv run --frozen --group dev pytest -q` → exit 0
- AC2 → `.opencode/skills/plan-enforce/SKILL.md` `### Verification command executors` · `.opencode/agents/bastion.md` `### Rulebook` · `.opencode/agents/crucible.md` `#### Test Execution`
- AC3 → `.opencode/skills/plan-enforce/SKILL.md` `#### Non-TypeScript test files` · `.opencode/agents/crucible.md` `#### Test Execution`
- AC4 → `validate_plan.py` goal-trace / manifest-equality / verification-parity checks
- AC5 → `validate_plan.py` audit-gate check
- AC6 → `.opencode/skills/plan-enforce/SKILL.md` `### Post-write self-verification loop`, `#### Independent audit gate` · `references/_template.md` and `references/_template-programming.md` `## Audit` blocks
- AC7 → `.opencode/skills/plan-enforce/SKILL.md` `### Execution-review message` · `.opencode/skills/plan-enforce/references/_lifecycle-contract.md` `## Plan lifecycle rules` row `Plan files written`
- AC8 → `.opencode/skills/plan-enforce/SKILL.md` `### Execution-review message`
- AC9 → `references/_template.md` · `references/_template-programming.md`
- AC10 → `AGENTS.md` Conventions
- AC11 → `.opencode/skills/plan-enforce/references/_lifecycle-contract.md` `## Plan lifecycle rules` row `Forge 🔨 (Implementer) dispatch`
- AC12 → `.opencode/skills/plan-enforce/SKILL.md` story-input and goal-lifecycle rules · `.opencode/skills/user-story/SKILL.md`
- AC13 → `.opencode/skills/plan-enforce/references/_lifecycle-contract.md` `## Acceptance-criterion reconciliation (fail-closed)` · `.opencode/skills/user-story/references/_consistency-checklist.md` `## Approved-criteria completion scope`
- AC14 → `.opencode/skills/plan-enforce/references/_lifecycle-contract.md` `## Resume (completion)` · `.opencode/skills/plan-enforce/SKILL.md` `#### Drift watch`
- AC15 → `.opencode/agents/sentinel.md` `##### Story-audit checks` and `##### Judgment calls`
- AC16 → `.opencode/skills/plan-enforce/references/_lifecycle-contract.md` `## Acceptance-criterion reconciliation (fail-closed)` · `.opencode/skills/user-story/references/_template-user-story.md` `## Acceptance criteria`
- AC17 → `uv run --frozen --group dev pytest -q` → exit 0 · Crucible 🔥 (Test Architect) test-architecture `[PASS]` · `pyproject.toml` `[tool.pytest.ini_options]`
- AC18 → `.opencode/skills/plan-enforce/SKILL.md` `## Mandatory core`, `## Project extensions` · `.opencode/skills/plan-enforce/references/_lifecycle-contract.md` `## Resume (completion)` · `#### Independent audit gate` · Vault 🔐 (Catalog Steward) `[PASS]` 2026-10-09
- AC19 → `.opencode/skills/plan-enforce/SKILL.md` `### Dispatch bundle contract`, `### User stories`, `### Simplicity discipline` · linked references/templates · Vault 🔐 (Catalog Steward) `[PASS]` 2026-10-09
- AC20 → `.opencode/skills/plan-enforce/SKILL.md` `### Simplicity discipline` · `.opencode/skills/plan-enforce/references/_consistency-checklist.md` **Completion and findings**
- AC21 → `.opencode/skills/plan-enforce/SKILL.md` `### Dispatch bundle contract` · `knowledge/agents.md` Question-routing rule
- AC22 → `.opencode/skills/plan-enforce/references/_lifecycle-contract.md` `## Resume (completion)` · `.opencode/skills/plan-enforce/references/_consistency-checklist.md` **Completion and findings**
- AC23 → `.opencode/skills/plan-enforce/SKILL.md` `#### Independent audit gate`
- AC24 → `.opencode/skills/plan-enforce/SKILL.md` `### Simplicity discipline` · `.opencode/skills/plan-enforce/references/_consistency-checklist.md` **Completion and findings**
- AC25 → `.opencode/skills/plan-enforce/SKILL.md` `### All-changes disposition` · `AGENTS.md` Conventions
- AC26 → `.opencode/skills/plan-enforce/SKILL.md` `### Bounded discovery before scope confirmation`, `### Contract-sized phases` · `references/_template.md`, `references/_template-programming.md`, `references/_phase-template.md`
- AC27 → `validate_plan.py` rendered-template, phase-table, and story-index regression tests
- AC28 → `.opencode/skills/plan-enforce/SKILL.md` `### Post-write self-verification loop`, `#### Independent audit gate`
- AC29 → `.opencode/skills/plan-enforce/SKILL.md` `### Expected-red intermediate checkpoint` · `references/_phase-template.md` · `.opencode/agents/crucible.md` `#### Test Execution`
- AC30 → `.opencode/skills/plan-enforce/SKILL.md` `### Documentation discipline` · `.opencode/skills/plan-enforce/references/_consistency-checklist.md`
- AC31 → `.opencode/skills/plan-enforce/SKILL.md` `### Bounded discovery before scope confirmation` item 4 · `### Contract-sized phases`

## Constraints

- Executor enforcement is declared table shape plus phase-review authority — because the validator cannot parse permission models and must not pretend to.
- The validator catches mechanical drift; an independent auditor supplies the semantic verdict — because shape checks cannot establish correctness.
- Completion reconciles committed or materially changed criteria and relevant regressions; unselected legitimate commitments remain — because a blanket whole-story gate would force deletion of valid commitments.
- CREATE requires an explicit UPDATE / rename / CREATE choice — because shared affected files never prove duplicate ownership.
- Story discussion owns feature behavior; plans own execution contracts — because feature intent must be settled before delivery mechanics.
- Nonconforming files included in a plan require their necessary design rework within that plan — because a partial patch on noncompliant code preserves the defect.
- Planning and completion audits are distinct — because a planning pass cannot certify a finished candidate.
- `## Resolved decisions` on a plan file is plan-scope history and remains in use there; it is retired only on story files — because plans record how scope changed and stories record what the feature is.

## Change log

- before 2026-10-07 — earlier history: see git history for this file
- 2026-10-07 — core-format-consistency (PR #52): aligned skill/agent authoring guidance with optional ownership headings, corrected stale checklist references, added read/preview/confirm before configuration writes, tightened Crucible's read-only discovery grant, and made dispatch/report output bounded and task-specific.
- 2026-10-11 — regionize-agents-20261010 (PR #53): authoring evidence now cites the standardized agent Rulebook and Workflow sections.
- 2026-10-11 — workflow-contract (PR #57): approved story-first planning, criterion-scoped completion, contract-sized phases, documentation coupling, expected-red checkpoints, and required rework for nonconforming planned files.
- 2026-10-11 — planning-workflow-20261011 (PR #57): delivered approved-story input, bounded discovery, contract-sized phases, semantic review + two-failure reassessment, expected-red checkpoint, criterion-scoped completion, same-change documentation, and the Sentinel story-audit alignment; validator reworked into layers with the path preserved.
- 2026-10-12 — story revision (PR #59): split behavioural criteria from `## Proof`, moved pre-decided planning policy into `## Constraints`, and dropped test symbols and config literals from criterion text.
