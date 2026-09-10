# User story — plan-enforce-executor-validation

> **Created:** 2026-09-10
> **Title:** Plan-enforce executor validation
> **Status:** active
> **Epic:** plan-governance
> **Affected areas:** `.opencode/skills/plan-enforce/`, `.opencode/agents/bastion.md`, `.opencode/agents/crucible.md`

## Persona

- A plan owner who needs every verification command to name the agent responsible for executing it and its evidence reviewer to validate that assignment.

## Goal

- **G:** Prevent a plan phase from assigning a verification command without a traceable executor, while requiring a real `[PASS]`/`[FAIL]` test-architecture audit for Python test files.
  - Done when: the plan validator rejects a missing, empty, or malformed canonical `Executor`/`Command` table row, phase review checks assigned authority, and Python stdlib unittest files use their declared runnable `python3` command plus Bastion 🧱 (Backend & Scripts Architect) [PASS] and Crucible 🔥 (Test Architect) [PASS]/[FAIL] — with [UNCERTAIN] not acceptable for that scope — without adding pytest.

## Scenario

- A programming phase writes a Python test file. Its phase runbook declares each verification command in the canonical executor-command table. The validator rejects an omitted or malformed pair; the phase review confirms the executor has authority, Bastion 🧱 (Backend & Scripts Architect) audits the Python files, and Crucible 🔥 (Test Architect) returns its `[PASS]`/`[FAIL]` test-architecture verdict.

## Acceptance criteria

- ✅ Every phase verification command has one canonical executor-command table row with exactly the `Executor` and `Command` columns, and the validator rejects a missing, empty, or malformed table. Evidence: `validate_plan.py` and its 29-test suite enforce the canonical table, including 8 executor-command table cases (7 rejection + 1 acceptance); `plan-enforce` is `1.10.0`.
- ✅ The validator checks declared traceability only; phase review verifies executor authority against the relevant agent rulebook or permission model. Evidence: the validator enforces declared table shape and traceability only, and phase review audits authority against `.opencode/agents/bastion.md` `1.2.0` and `.opencode/agents/crucible.md` `1.1.0`.
- ✅ Python stdlib unittest edits require the declared runnable `python3` command, Bastion 🧱 (Backend & Scripts Architect) [PASS], and Crucible 🔥 (Test Architect) [PASS]/[FAIL]. Evidence: `plan-enforce` `1.10.0` requires the declared literal `python3` command plus both the Bastion 🧱 (Backend & Scripts Architect) `1.2.0` and Crucible 🔥 (Test Architect) `1.1.0` verdicts.
- ✅ Crucible 🔥 (Test Architect) is dispatched for test-file edits and returns [PASS] or [FAIL]; [UNCERTAIN] is no longer acceptable for exact active-plan Python stdlib unittest files. Evidence: Crucible 🔥 (Test Architect) `1.1.0` `## PYTHON STDLIB UNITTEST TESTS` returned `[PASS]` for all three suites — `test_query_verification.py` (73 tests), `test_validate_plan.py` (29 tests), and `test_validate_runbook.py` — each exit 0.
- ✅ No pytest dependency, lockfile update, or test-framework migration is introduced. Evidence: no pytest import or test-framework dependency was added; `pyproject.toml` and `uv.lock` are unchanged.

## Change log

- 2026-09-10 - advisory-fixes-plan-enforce-20260910: created the durable executor-validation and stdlib unittest governance definition.
- 2026-09-10 - python-test-audit-governance-20260910: superseded the recorded-applicability gate; Python stdlib unittest edits now require Crucible 🔥 (Test Architect) [PASS]/[FAIL], and [UNCERTAIN] is not acceptable for that scope.

## Resolved decisions

- 2026-09-10 - executor enforcement uses canonical declared executor-command traceability in the validator plus phase-review authority audit; the validator does not parse agent permission models.
- 2026-09-10 - the project retains Python stdlib `unittest`; pytest is not introduced.
- 2026-09-10 - Python stdlib unittest test architecture is owned by Crucible 🔥 (Test Architect) via the additive `## PYTHON STDLIB UNITTEST TESTS` branch; [UNCERTAIN] is not acceptable for exact active-plan Python test files. This supersedes the earlier recorded-applicability verdict.
