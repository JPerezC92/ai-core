# User story — plan-enforce

> **Created:** 2026-09-10
> **Title:** Plan-enforce
> **Status:** active
> **version:** 1.1.0
> **Epic:** plan-governance
> **Affected areas:** `.opencode/skills/plan-enforce/`, `AGENTS.md`, `user-stories/`, `.opencode/agents/bastion.md`, `.opencode/agents/crucible.md`, `.opencode/agents/sentinel.md`

## Persona

- Cipher 🔓 (Lead Orchestrator), who writes, reviews, executes, and archives plans and must not skip executor assignment, independent audit, the human review turn, or story-criterion disposition.

## Goal

- **G:** While a plan is alive, plan-enforce is one feature: every verify command has an authorized executor, drift cannot complete without an independent `[PASS]`, the user gets a review turn before Forge 🔨 (Implementer), and a touched story cannot archive with `⬜` or `❌`.
  - Done when: every verify command names an authorized executor, no plan archives without an independent `[PASS]`, the execution-review message precedes any Forge 🔨 (Implementer) dispatch, and no touched story retains `⬜` or `❌`.

## Scenario

- Cipher 🔓 (Lead Orchestrator) writes a plan. Each phase names an executor per verify command. After files are written, the next message is issue then goal then how then files; Forge 🔨 (Implementer) waits for a later explicit ask. An independent auditor records `[PASS]` before execute or complete. At archive, every touched criterion is `✅` or removed.

## Acceptance criteria

- ✅ Every phase verification command has one canonical executor-command table row with exactly the `Executor` and `Command` columns, and the validator rejects a missing, empty, or malformed table. Evidence: `validate_plan.py` and its suite enforce the canonical table, including 8 executor-command table cases (7 rejection + 1 acceptance).
- ✅ The validator checks declared traceability only; phase review verifies executor authority against the relevant agent rulebook or permission model. Evidence: the validator enforces declared table shape and traceability only, and phase review audits authority against `.opencode/agents/bastion.md` `1.5.0` and `.opencode/agents/crucible.md` `1.5.0`.
- ✅ Python skill test edits require the project's reviewed whole-suite command (AICore: `uv run --frozen --group dev pytest -q`), Bastion 🧱 (Backend & Scripts Architect) [PASS], and Crucible 🔥 (Test Architect) [PASS]/[FAIL]. Evidence: plan-enforce rules; Crucible 🔥 (Test Architect) 1.5.0.
- ✅ Goal trace, manifest equality, and verification parity are enforced with `GOAL-TRACE:`, `MANIFEST:`, and `VERIFICATION-PARITY:` findings. Evidence: `validate_plan.py` `check_goal_trace`/`check_manifest_equality`/`check_verification_parity`.
- ✅ A completed plan requires `## Audit` with a non-empty `Auditor`, a `[PASS]` verdict, and a non-empty `Date`; unknown or `[FAIL]` verdicts fail. Evidence: `check_audit_gate`.
- ✅ The skill documents the loop, the independent-audit gate before a ready report or Forge 🔨 (Implementer) dispatch, the fail-closed fallback, and the pass-count report; both templates carry a compliant `## Audit` block. Evidence: `SKILL.md` Post-write self-verification loop and Independent audit gate.
- ✅ After plan files and self-verification, Cipher 🔓 (Lead Orchestrator) sends the execution-review message and does not dispatch Forge 🔨 (Implementer) in that turn. Evidence: `plan-enforce` SKILL.md execution-review step and lifecycle row `Plan files written`.
- ✅ The message is human-readable prose per goal in order Issue, Goal, How, Files. A recap table does not replace that prose. Evidence: SKILL.md `## Execution-review message`.
- ✅ `plan.md` templates carry the same per-goal Issue / How / Files layout. Evidence: `references/_template.md`; `references/_template-programming.md`.
- ✅ `AGENTS.md` forbids a Forge 🔨 (Implementer) dispatch in the same turn as the execution-review message, and forbids a corrective, release, or scope-change question without that file list. Evidence: `AGENTS.md` Conventions.
- ✅ Independent audit `[PASS]` and the stash gate still apply on the later execution turn. Evidence: SKILL.md Forge 🔨 (Implementer) dispatch lifecycle row.
- ✅ Before creating a new story file, Cipher 🔓 (Lead Orchestrator) presents index-filtered candidates with evidence and obtains an explicit UPDATE / rename / CREATE choice. CREATE without that choice is a violation. Evidence: SKILL.md User stories and User-story collision gate.
- ✅ AICore's `plan-enforce` skill states the canonical fail-closed reconciliation invariant: no `⬜` or `❌` remains after a touching plan completes; each criterion is `✅` or removed as out-of-scope. Evidence: `.opencode/skills/plan-enforce/SKILL.md` section `### Acceptance-criterion reconciliation (fail-closed)`.
- ✅ `plan-enforce` blocks `## Outcome` and archival until every touched story is fully dispositioned. Evidence: completion bullet in `### Resume (completion)`.
- ✅ Sentinel 🛡️ (Quality Guardian) reports a stale `⬜`, fulfilled-but-unchecked, or release-event criterion in a touched story as a blocking finding, and never auto-checks a box. Evidence: `.opencode/agents/sentinel.md` story-audit rules.
- ✅ Release events are not feature acceptance criteria; release policy stays enforceable and actual events live in change-log/PR history. Evidence: `SKILL.md` invariant sentence; `_template-user-story.md` `## Acceptance criteria` guidance.
- ✅ For a project with an approved whole-suite runner, plan-enforce assigns Crucible 🔥 (Test Architect) the suite command rather than requiring a new grant per test file. Its phase gate needs the whole-suite command exit 0 plus test-architecture `[PASS]`; Bastion 🧱 (Backend & Scripts Architect) remains the Python implementation auditor. Evidence: Crucible 🔥 (Test Architect) ran `uv run --frozen --group dev pytest -q` with exit 0; discovery is project-wide (`testpaths = ["."]` with junk-only `norecursedirs`, no `.*` entry), so a test added anywhere in the project joins the suite with no `pyproject.toml` or grant edit. Historical runs (`108` single-file, `304`, and `313`) are retained as history only, not as current evidence.
- ✅ The delivered plan-enforce workflow separates mandatory lifecycle from project extensions while preserving plan/story/audit/executor and review-turn obligations. Evidence: `plan-enforce/SKILL.md` two-section layout (Sentinel 🛡️ PASS) with project suite/base/validator in Project extensions; the three portability references are corrected; generated plan/story schemas stay unwrapped.
- ✅ Delivered authoring procedures, degraded checks, examples and portable references agree with the actual sectioned source. Evidence: `op-skill-creator`/`op-agent-creator` emit the two-section layout; the plan-enforce references no longer carry the source UV suite example; `ticket-runbook/references/response-draft-template.md` uses neutral greeting guidance; generated records remain unwrapped. Sentinel 🛡️ PASS.
- ✅ An admitted finding is an evidence-bounded packet — confirmed goal, governing normative clause, actual responsible actor and the shipped path it controls (distinct from a helper or fixture), expected versus observed behavior, affected scope, a reproduction or static fact, severity with literal output, and an explicit keep / fix / reject-scope decision; review classifies it as a requirement defect, documentation drift, or supplemental concern, and no speculative blocker or growing helper/test matrix is admitted. Evidence: `plan-enforce/SKILL.md` **Simplicity discipline**; `_consistency-checklist.md` **Completion and findings**.
- ✅ Every dispatch prompt is fail-closed checked for the complete verbatim bundle — Subject, full `## Goals` block, full phase file, and re-pasted prior-phase values — and carries the question-routing prohibition and stop-and-report contract; a summarized goal or paraphrased step is never dispatched. Evidence: `plan-enforce/SKILL.md` **Dispatch bundle contract**; `knowledge/agents.md` Question-routing rule.
- ✅ Completion is a layered matrix on the current snapshot — code architecture, test architecture, test execution, and model/guidance verdicts, each with its scope and verdict; a passing execution never substitutes for a required architecture verdict, and a missing or adverse layer blocks completion. Evidence: `plan-enforce/SKILL.md` `### Resume (completion)`; `_consistency-checklist.md` **Completion and findings**.
- ✅ A planning-readiness audit and a completion audit are distinct: the completion audit evaluates the finished work at its final candidate and is required before `## Outcome`, goal checkmarks, and archive, so a planning `[PASS]` or an execution-only result never substitutes for it. Evidence: `plan-enforce/SKILL.md` `#### Independent audit gate`.
- ✅ Replaced, superseded, or newly wired behavior requires a recorded legacy/dead-code sweep: search for the superseded implementation, remove dead code and stale wiring, and record the sweep as completion evidence, so no validated-but-unread field, dead symbol, or stale mapping survives a completed change. Evidence: `plan-enforce/SKILL.md` **Simplicity discipline**; `_consistency-checklist.md` **Completion and findings**.
- ✅ When asked to analyze all pending changes, every nonignored modified, deleted, and untracked path is enumerated and given an evidence-based `ship` / `fix` / `drop` disposition from inspected content before any scope question; manifest absence never proves a path unrelated, and completion is never claimed beyond the reviewed scope. Evidence: `plan-enforce/SKILL.md` `### All-changes disposition`; `AGENTS.md` `2.7.0` Conventions.

## Change log

- 2026-10-05 — process-debt-clearance-20261005: added evidence-bounded finding admission, the fail-closed dispatch bundle with the stop-and-report contract, the layered completion-evidence matrix, the planning-vs-completion audit distinction, the legacy/dead-code revalidation gate, and the all-changes disposition.
- 2026-10-05 — sectioned-core-delivery-reconciliation-20261005: sectioned the skill; corrected the portability references and the neutral response-template greeting.
- 2026-10-03 — sectioned-adoption-remediation-20261003: applied fail-closed evidence-to-criterion reconciliation to the reopened criteria.
- 2026-09-28 — plan-enforce-story-fold-20260928: unified the four plan-enforce stories into one; added the destination-approved Crucible whole-suite test-execution gate.
- before 2026-09-28 — earlier history: see git history for this file.

## Resolved decisions

- 2026-09-10 — executor enforcement is declared table shape plus phase-review authority; the validator does not parse permission models.
- 2026-09-12 — no leftover `⬜` or `❌` after a touching plan completes.
- 2026-09-15 — the validator catches mechanical drift; an independent auditor supplies the semantic verdict.
- 2026-09-27 — CREATE requires an explicit UPDATE / rename / CREATE choice.
