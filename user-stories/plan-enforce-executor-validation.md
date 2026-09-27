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
  - Done when: the plan validator rejects a missing, empty, or malformed canonical `Executor`/`Command` table row, phase review checks assigned authority, and Python skill test files use their declared runnable `uv run --frozen --group dev pytest` command plus Bastion 🧱 (Backend & Scripts Architect) [PASS] and Crucible 🔥 (Test Architect) [PASS]/[FAIL] — with [UNCERTAIN] not acceptable for that scope.

## Scenario

- A programming phase writes a Python test file. Its phase runbook declares each verification command in the canonical executor-command table. The validator rejects an omitted or malformed pair; the phase review confirms the executor has authority, Bastion 🧱 (Backend & Scripts Architect) audits the Python files, and Crucible 🔥 (Test Architect) returns its `[PASS]`/`[FAIL]` test-architecture verdict.

## Acceptance criteria

- ✅ Every phase verification command has one canonical executor-command table row with exactly the `Executor` and `Command` columns, and the validator rejects a missing, empty, or malformed table. Evidence: `validate_plan.py` and its 50-test suite enforce the canonical table, including 8 executor-command table cases (7 rejection + 1 acceptance); `plan-enforce` is `1.12.1`.
- ✅ The validator checks declared traceability only; phase review verifies executor authority against the relevant agent rulebook or permission model. Evidence: the validator enforces declared table shape and traceability only, and phase review audits authority against `.opencode/agents/bastion.md` `1.2.0` and `.opencode/agents/crucible.md` `1.1.0`.
- ✅ Python skill test edits require the declared runnable `uv run --frozen --group dev pytest` command, Bastion 🧱 (Backend & Scripts Architect) [PASS], and Crucible 🔥 (Test Architect) [PASS]/[FAIL]. Evidence: plan-enforce `1.13.0`; Bastion 🧱 (Backend & Scripts Architect) `1.3.0`; Crucible 🔥 (Test Architect) `1.2.0`; all four suites `[PASS]`.
- ✅ Crucible 🔥 (Test Architect) is dispatched for test-file edits and returns [PASS] or [FAIL]; [UNCERTAIN] is not acceptable for exact active-plan Python pytest files. Evidence: Crucible 🔥 (Test Architect) `1.2.0` `## PYTHON PYTEST TESTS` `[PASS]` on all four converted files.

## Change log

- 2026-09-10 - advisory-fixes-plan-enforce-20260910: created the durable executor-validation and stdlib unittest governance definition.
- 2026-09-10 - python-test-audit-governance-20260910: superseded the recorded-applicability gate; Python stdlib unittest edits now require Crucible 🔥 (Test Architect) [PASS]/[FAIL], and [UNCERTAIN] is not acceptable for that scope.
- 2026-09-12 - refresh-git-pr-evidence-contract-20260912: refreshed the current plan-enforce requirement citations to the shipped 1.11.1; no feature behavior or acceptance criteria changed.
- 2026-09-15 - debt-001-citation-currency-20260915: refreshed the current plan-enforce citations to the shipped 1.12.1 and the 50-test suite; no feature behavior or acceptance criteria changed.
- 2026-09-27 - python-pytest-20260927: retired the no-pytest AC; Python-test gate now requires `uv run --frozen --group dev pytest`; executor-table ACs unchanged. The Python runner definition moved to `python-pytest`.

## Resolved decisions

- 2026-09-10 - executor enforcement uses canonical declared executor-command traceability in the validator plus phase-review authority audit; the validator does not parse agent permission models.
- 2026-09-10 - the project retains Python stdlib `unittest`; pytest is not introduced.
- 2026-09-10 - Python stdlib unittest test architecture is owned by Crucible 🔥 (Test Architect) via the additive `## PYTHON STDLIB UNITTEST TESTS` branch; [UNCERTAIN] is not acceptable for exact active-plan Python test files. This supersedes the earlier recorded-applicability verdict.
- 2026-09-27 - python-pytest-20260927: user chose a new `python-pytest` story plus an update of this story; the 2026-09-10 no-pytest decision is superseded. Executor-table validation stays here; the Python runner moves to `python-pytest`.
