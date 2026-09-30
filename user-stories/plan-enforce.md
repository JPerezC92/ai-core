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
  - Done when: those invariants are the criteria of this one active story; the four former files are deleted and Git retains their history.

## Scenario

- Cipher 🔓 (Lead Orchestrator) writes a plan. Each phase names an executor per verify command. After files are written, the next message is issue then goal then how then files; Forge 🔨 (Implementer) waits for a later explicit ask. An independent auditor records `[PASS]` before execute or complete. At archive, every touched criterion is `✅` or removed.

## Acceptance criteria

- ✅ Every phase verification command has one canonical executor-command table row with exactly the `Executor` and `Command` columns, and the validator rejects a missing, empty, or malformed table. Evidence: `validate_plan.py` and its suite enforce the canonical table, including 8 executor-command table cases (7 rejection + 1 acceptance); `plan-enforce` is `1.12.1`.
- ✅ The validator checks declared traceability only; phase review verifies executor authority against the relevant agent rulebook or permission model. Evidence: the validator enforces declared table shape and traceability only, and phase review audits authority against `.opencode/agents/bastion.md` `1.2.0` and `.opencode/agents/crucible.md` `1.1.0`.
- ✅ Python skill test edits require the project's reviewed whole-suite command (AICore: `uv run --frozen --group dev pytest -q`), Bastion 🧱 (Backend & Scripts Architect) [PASS], and Crucible 🔥 (Test Architect) [PASS]/[FAIL]. Evidence: plan-enforce rules; Crucible 🔥 (Test Architect) 1.3.0.
- ✅ Goal trace, manifest equality, and verification parity are enforced with `GOAL-TRACE:`, `MANIFEST:`, and `VERIFICATION-PARITY:` findings. Evidence: `validate_plan.py` `check_goal_trace`/`check_manifest_equality`/`check_verification_parity`.
- ✅ A completed plan requires `## Audit` with a non-empty `Auditor`, a `[PASS]` verdict, and a non-empty `Date`; unknown or `[FAIL]` verdicts fail. Evidence: `check_audit_gate`.
- ✅ The skill documents the loop, the independent-audit gate before a ready report or Forge 🔨 (Implementer) dispatch, the fail-closed fallback, and the pass-count report; both templates carry a compliant `## Audit` block. Evidence: `SKILL.md` Post-write self-verification loop and Independent audit gate.
- ✅ After plan files and self-verification, Cipher 🔓 (Lead Orchestrator) sends the execution-review message and does not dispatch Forge 🔨 (Implementer) in that turn. Evidence: `plan-enforce` SKILL.md 1.14.0 step 13 and lifecycle row `Plan files written`.
- ✅ The message is human-readable prose per goal in order Issue, Goal, How, Files. A recap table does not replace that prose. Evidence: SKILL.md `## Execution-review message`.
- ✅ `plan.md` templates carry the same per-goal Issue / How / Files layout. Evidence: `references/_template.md`; `references/_template-programming.md`.
- ✅ `AGENTS.md` forbids a Forge 🔨 (Implementer) dispatch in the same turn as the execution-review message, and forbids a corrective, release, or scope-change question without that file list. Evidence: `AGENTS.md` 2.4.0 Conventions.
- ✅ Independent audit `[PASS]` and the stash gate still apply on the later execution turn. Evidence: SKILL.md Forge 🔨 (Implementer) dispatch lifecycle row.
- ✅ Before creating a new story file, Cipher 🔓 (Lead Orchestrator) presents index-filtered candidates with evidence and obtains an explicit UPDATE / rename / CREATE choice. CREATE without that choice is a violation. Evidence: SKILL.md User stories and User-story collision gate.
- ✅ AICore's `plan-enforce` skill states the canonical fail-closed reconciliation invariant: no `⬜` or `❌` remains after a touching plan completes; each criterion is `✅` or removed as out-of-scope. Evidence: `.opencode/skills/plan-enforce/SKILL.md` section `### Acceptance-criterion reconciliation (fail-closed)`.
- ✅ `plan-enforce` blocks `## Outcome` and archival until every touched story is fully dispositioned. Evidence: completion bullet in `### Resume (completion)`.
- ✅ Sentinel 🛡️ (Quality Guardian) reports a stale `⬜`, fulfilled-but-unchecked, or release-event criterion in a touched story as a blocking finding, and never auto-checks a box. Evidence: `.opencode/agents/sentinel.md` `1.4.0`.
- ✅ Release events are not feature acceptance criteria; release policy stays enforceable and actual events live in change-log/PR history. Evidence: `SKILL.md` invariant sentence; `_template-user-story.md` `## Acceptance criteria` guidance.
- ✅ For a project with an approved whole-suite runner, plan-enforce assigns Crucible 🔥 (Test Architect) the suite command rather than requiring a new grant per test file. Its phase gate needs the whole-suite command exit 0 plus test-architecture `[PASS]`; Bastion 🧱 (Backend & Scripts Architect) remains the Python implementation auditor. Evidence: Crucible 🔥 (Test Architect) ran `uv run --frozen --group dev pytest -q` with exit 0 (`304 passed`); discovery is project-wide (`testpaths = ["."]` with junk-only `norecursedirs`, no `.*` entry), so a test added anywhere in the project joins the suite with no `pyproject.toml` or grant edit. Historical runs (`108` single-file, and a `313` figure recorded under a plan that was later superseded) are retained as history only, not as current evidence.

## Change log

- 2026-09-28 — plan-enforce-story-fold-20260928: unified `plan-enforce-executor-validation`, `plan-enforce-story-acceptance-reconciliation`, `plan-enforce-plan-audit-gate`, and `plan-enforce-execution-review` into this story. The old files were deleted; Git is the history. `post-merge-branch-cleanup` stays a separate story.
- 2026-09-28 — plan-enforce-story-fold-20260928: version 1.1.0 adds the destination-approved Crucible 🔥 (Test Architect) test-execution gate; the project-owned grant must be proven after OpenCode restart.
- 2026-09-28 — plan-enforce-story-fold-20260928: user locked a project-wide whole-suite G6 gate in place of the file-pattern-only runner; its new criterion remains pending until a suite run and destination grant review.

## Resolved decisions

- 2026-09-28 — user: one `plan-enforce` story; four old files deleted; post-merge stays.
- 2026-09-27 — CREATE requires an explicit UPDATE / rename / CREATE choice (from execution-review).
- 2026-09-15 — validator catches mechanical drift; independent auditor supplies the semantic verdict.
- 2026-09-12 — no leftover `⬜` or `❌` after a touching plan completes.
- 2026-09-10 — executor enforcement is declared table shape plus phase-review authority; the validator does not parse permission models.
