# User story — plan-enforce

> **Created:** 2026-09-10
> **Title:** Plan-enforce
> **Status:** active
> **version:** 1.1.0
> **Epic:** plan-governance
> **Affected areas:** `.opencode/skills/plan-enforce/`, `.opencode/skills/git-commit/`, `.opencode/skills/git-pr/`, `.opencode/skills/op-agent-creator/`, `.opencode/skills/op-model/`, `.opencode/skills/op-skill-creator/`, `AGENTS.md`, `knowledge/agents.md`, `user-stories/`, `.opencode/agents/atrium.md`, `.opencode/agents/bastion.md`, `.opencode/agents/crucible.md`, `.opencode/agents/marshal.md`, `.opencode/agents/sentinel.md`, `.opencode/agents/vault.md`, `opencode.jsonc`

## Persona

- Cipher 🔓 (Lead Orchestrator), who writes, reviews, executes, and archives plans and must not skip executor assignment, independent audit, the human review turn, or story-criterion disposition.

## Goal

- **G:** While a plan is alive, plan-enforce is one feature: every verify command has an authorized executor, drift cannot complete without an independent `[PASS]`, the user gets a review turn before Forge 🔨 (Implementer), and a touched story cannot archive with `⬜` or `❌`.
  - Done when: every verify command names an authorized executor, no plan archives without an independent `[PASS]`, the execution-review message precedes any Forge 🔨 (Implementer) dispatch, and no touched story retains `⬜` or `❌`. Evidence: `.opencode/skills/plan-enforce/SKILL.md` `### Verification command executors`, `#### Independent audit gate`, `### Execution-review message`, `#### Acceptance-criterion reconciliation (fail-closed)`, and `### Plan lifecycle rules`.

## Scenario

- Cipher 🔓 (Lead Orchestrator) writes a plan. Each phase names an executor per verify command. After files are written, the next message is issue then goal then how then files; Forge 🔨 (Implementer) waits for a later explicit ask. An independent auditor records `[PASS]` before execute or complete. At archive, every touched criterion is `✅` or removed.

## Acceptance criteria

> **Evidence basis:** Each criterion names its controlling source section or test symbol. Candidate-specific claims include a current verification command/result or remain unchecked pending completion.

- ✅ Every phase verification command has one canonical executor-command table row with exactly the `Executor` and `Command` columns, and the validator rejects a missing, empty, or malformed table. Evidence: `.opencode/skills/plan-enforce/scripts/test_validate_plan_phase_structure.py::ValidatePlanPhaseStructureTests.test_verify_table_absent_flagged`, `test_verify_table_wrong_header_flagged`, `test_verify_table_extra_column_flagged`, `test_verify_table_empty_executor_flagged`, and `test_verify_table_empty_command_flagged`; verification `uv run --frozen --group dev pytest -q` → exit 0.
- ✅ The validator checks declared traceability only; phase review verifies executor authority against the relevant agent rulebook or permission model. Evidence: `.opencode/skills/plan-enforce/SKILL.md` `### Verification command executors`; `.opencode/agents/bastion.md` `### PYTHON BACKEND — backend tooling paths, ticket tooling, and plan-scoped skill scripts`; `.opencode/agents/crucible.md` `### Test Execution`; current verification `uv run --frozen --group dev pytest -q` → exit 0.
- ✅ Python skill test edits require the project's reviewed whole-suite command (AICore: `uv run --frozen --group dev pytest -q`), Bastion 🧱 (Backend & Scripts Architect) [PASS], and Crucible 🔥 (Test Architect) [PASS]/[FAIL]. Evidence: `.opencode/skills/plan-enforce/SKILL.md` `#### Non-TypeScript test files`; `.opencode/agents/crucible.md` `### Test Execution`; verification `uv run --frozen --group dev pytest -q` → exit 0.
- ✅ Goal trace, manifest equality, and verification parity are enforced with `GOAL-TRACE:`, `MANIFEST:`, and `VERIFICATION-PARITY:` findings. Evidence: `validate_plan.py` `check_goal_trace`/`check_manifest_equality`/`check_verification_parity`.
- ✅ A completed plan requires `## Audit` with a non-empty `Auditor`, a `[PASS]` verdict, and a non-empty `Date`; unknown or `[FAIL]` verdicts fail. Evidence: `check_audit_gate`.
- ✅ The skill documents the loop, the independent-audit gate before a ready report or Forge 🔨 (Implementer) dispatch, the fail-closed fallback, and the pass-count report; both templates carry a compliant `## Audit` block. Evidence: `.opencode/skills/plan-enforce/SKILL.md` `### Post-write self-verification loop` and `#### Independent audit gate`; `.opencode/skills/plan-enforce/references/_template.md` and `.opencode/skills/plan-enforce/references/_template-programming.md` `## Audit` blocks.
- ✅ After plan files and self-verification, Cipher 🔓 (Lead Orchestrator) sends the execution-review message and does not dispatch Forge 🔨 (Implementer) in that turn. Evidence: `.opencode/skills/plan-enforce/SKILL.md` `### Execution-review message` and `### Plan lifecycle rules` row `Plan files written`.
- ✅ The message is human-readable prose per goal in order Issue, Goal, How, Files. A recap table does not replace that prose. Evidence: `.opencode/skills/plan-enforce/SKILL.md` `### Execution-review message`.
- ✅ `plan.md` templates carry the same per-goal Issue / How / Files layout. Evidence: `references/_template.md`; `references/_template-programming.md`.
- ✅ `AGENTS.md` forbids a Forge 🔨 (Implementer) dispatch in the same turn as the execution-review message, and forbids a corrective, release, or scope-change question without that file list. Evidence: `AGENTS.md` Conventions.
- ✅ Independent audit `[PASS]` and the stash gate still apply on the later execution turn. Evidence: `.opencode/skills/plan-enforce/SKILL.md` `### Plan lifecycle rules` row `Forge 🔨 (Implementer) dispatch`.
- ✅ Before creating a new story file, Cipher 🔓 (Lead Orchestrator) presents index-filtered candidates with evidence and obtains an explicit UPDATE / rename / CREATE choice. CREATE without that choice is a violation. Evidence: SKILL.md User stories and User-story collision gate.
- ✅ AICore's `plan-enforce` skill states the canonical fail-closed reconciliation invariant: no `⬜` or `❌` remains after a touching plan completes; each criterion is `✅` or removed as out-of-scope. Evidence: `.opencode/skills/plan-enforce/SKILL.md` `#### Acceptance-criterion reconciliation (fail-closed)`.
- ✅ `plan-enforce` blocks `## Outcome` and archival until every touched story is fully dispositioned. Evidence: completion bullet in `### Resume (completion)`.
- ✅ Sentinel 🛡️ (Quality Guardian) reports a stale `⬜`, fulfilled-but-unchecked, or release-event criterion in a touched story as a blocking finding, and never auto-checks a box. Evidence: `.opencode/agents/sentinel.md` `#### Story-audit checks (report-only)` and `#### Judgment calls (report only)` item 6.
- ✅ Release events are not feature acceptance criteria; release policy stays enforceable and actual events live in change-log/PR history. Evidence: `.opencode/skills/plan-enforce/SKILL.md` `#### Acceptance-criterion reconciliation (fail-closed)`; `.opencode/skills/plan-enforce/references/_template-user-story.md` `## Acceptance criteria`.
- ✅ For a project with an approved whole-suite runner, plan-enforce assigns Crucible 🔥 (Test Architect) the suite command rather than requiring a new grant per test file. Its phase gate needs the whole-suite command exit 0 plus test-architecture `[PASS]`; Bastion 🧱 (Backend & Scripts Architect) remains the Python implementation auditor. Evidence: current verification `uv run --frozen --group dev pytest -q` → exit 0 and Crucible 🔥 (Test Architect) test-architecture `[PASS]`; `pyproject.toml` `[tool.pytest.ini_options]` sets `testpaths = ["."]`, `python_files = ["test_*.py"]`, `python_classes = ["*Tests"]`, and `norecursedirs = ["node_modules", ".venv", "output", "plans/.completed", "build", "dist", "__pycache__", ".git"]`.
- ✅ Mandatory lifecycle rules are separated from project-specific extensions while preserving plan/story/audit/executor/review-turn obligations. Evidence: `.opencode/skills/plan-enforce/SKILL.md` `## Mandatory core`, `## Project extensions`, `### Resume (completion)`, and `#### Independent audit gate`; current Vault 🔐 (Catalog Steward) `[PASS]` on the skill/reference surface, 2026-10-09 (4,489 words).
- ✅ Authoring procedures, degraded checks, examples, and portable references agree with the current mandatory source rules. Evidence: `.opencode/skills/plan-enforce/SKILL.md` `### Dispatch bundle contract`, `### User stories`, `### Simplicity discipline`, and linked references/templates; current Vault 🔐 (Catalog Steward) audit `[PASS]` on the skill/reference surface, 2026-10-09.
- ✅ An admitted finding is an evidence-bounded packet — confirmed goal, governing normative clause, actual responsible actor and the shipped path it controls (distinct from a helper or fixture), expected versus observed behavior, affected scope, a reproduction or static fact, severity with literal output, and an explicit keep / fix / reject-scope decision; review classifies it as a requirement defect, documentation drift, or supplemental concern, and no speculative blocker or growing helper/test matrix is admitted. Evidence: `plan-enforce/SKILL.md` **Simplicity discipline**; `_consistency-checklist.md` **Completion and findings**.
- ✅ Every dispatch prompt is fail-closed checked for the complete verbatim bundle — Subject, full `## Goals` block, full phase file, and re-pasted prior-phase values — and carries the question-routing prohibition and stop-and-report contract; a summarized goal or paraphrased step is never dispatched. Evidence: `plan-enforce/SKILL.md` **Dispatch bundle contract**; `knowledge/agents.md` Question-routing rule.
- ✅ Completion is a layered matrix on the current snapshot — code architecture, test architecture, test execution, and model/guidance verdicts, each with its scope and verdict; a passing execution never substitutes for a required architecture verdict, and a missing or adverse layer blocks completion. Evidence: `plan-enforce/SKILL.md` `### Resume (completion)`; `_consistency-checklist.md` **Completion and findings**.
- ✅ A planning-readiness audit and a completion audit are distinct: the completion audit evaluates the finished work at its final candidate and is required before `## Outcome`, goal checkmarks, and archive, so a planning `[PASS]` or an execution-only result never substitutes for it. Evidence: `plan-enforce/SKILL.md` `#### Independent audit gate`.
- ✅ Replaced, superseded, or newly wired behavior requires a recorded legacy/dead-code sweep: search for the superseded implementation, remove dead code and stale wiring, and record the sweep as completion evidence, so no validated-but-unread field, dead symbol, or stale mapping survives a completed change. Evidence: `plan-enforce/SKILL.md` **Simplicity discipline**; `_consistency-checklist.md` **Completion and findings**.
- ✅ When asked to analyze all pending changes, every nonignored modified, deleted, and untracked path is enumerated and given an evidence-based `ship` / `fix` / `drop` disposition from inspected content before any scope question; manifest absence never proves a path unrelated, and completion is never claimed beyond the reviewed scope. Evidence: `plan-enforce/SKILL.md` `### All-changes disposition`; `AGENTS.md` Conventions.

## Change log

- 2026-10-09 — aicore-all-files-pr-20261008: separated mandatory lifecycle obligations from destination extensions, aligned authoring guidance, and repointed verify-table test evidence to the concern-specific phase-structure module.
- 2026-10-07 — core-format-consistency: aligned skill/agent authoring guidance with optional ownership headings, corrected stale checklist references, added read/preview/confirm before configuration writes, tightened Crucible's read-only discovery grant, and made dispatch/report output bounded and task-specific.
- 2026-10-05 — process-debt-clearance-20261005: added evidence-bounded finding admission, the fail-closed dispatch bundle with the stop-and-report contract, the layered completion-evidence matrix, the planning-vs-completion audit distinction, the legacy/dead-code revalidation gate, and the all-changes disposition.
- 2026-10-05 — sectioned-core-delivery-reconciliation-20261005: sectioned the skill; corrected the portability references and the neutral response-template greeting.
- before 2026-10-05 — earlier history: see git history for this file

## Resolved decisions

- 2026-09-10 — executor enforcement is declared table shape plus phase-review authority; the validator does not parse permission models.
- 2026-09-12 — no leftover `⬜` or `❌` after a touching plan completes.
- 2026-09-15 — the validator catches mechanical drift; an independent auditor supplies the semantic verdict.
- 2026-09-27 — CREATE requires an explicit UPDATE / rename / CREATE choice.
