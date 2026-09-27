# User story — python-pytest

> **Created:** 2026-09-27
> **Title:** Python pytest test runner
> **Status:** active
> **Epic:** developer-tooling
> **Affected areas:** `pyproject.toml`, `uv.lock`, `.opencode/agents/crucible.md`, `.opencode/agents/bastion.md`, `.opencode/skills/plan-enforce/`, `.opencode/skills/*/scripts/test_*.py`, `AGENTS.md`

## Persona

- A core maintainer who runs Python skill tests and an adopter who must inherit one Python test runner from AICore.

## Goal

- **G:** pytest is the only Python test runner for skill tests, locked in the root UV `dev` group, with Crucible 🔥 (Test Architect) as the test-architecture owner.
  - Done when: `uv run --frozen --group dev pytest` collects and passes the skill suites; pytest is not a runtime `[project]` dependency; Crucible 🔥 (Test Architect) `## PYTHON PYTEST TESTS` returns `[PASS]` or `[FAIL]` for exact active-plan `test_*.py` files.

## Scenario

- A programming phase edits a Python skill test. The phase runbook declares `uv run --frozen --group dev pytest` in the executor-command table. Bastion 🧱 (Backend & Scripts Architect) audits script architecture. Crucible 🔥 (Test Architect) returns `[PASS]` or `[FAIL]` against the pytest ruleset. The four existing skill suites run under that same command.

## Acceptance criteria

- ✅ pytest is locked only under `[dependency-groups] dev`; `[project].dependencies` stays PyYAML-only; `uv lock --check` exits 0. Evidence: `pyproject.toml` `pytest==9.0.3` in `dev`; `PyYAML==6.0.3` only in `[project].dependencies`; Warden 🔒 (Dependency Warden) downstream `[PASS]` `output/audits/2026-09-27-pytest-lockfile.md`.
- ✅ `uv run --frozen --group dev pytest -q` exits 0 and collects the four skill `test_*.py` files. Evidence: 244 passed.
- ✅ Those four files are pytest-native: no `unittest.TestCase` and no `unittest.main()`. Evidence: `git grep -n "unittest.TestCase"` and `git grep -n "unittest.main("` under `.opencode/skills/` return no matches.
- ✅ Crucible 🔥 (Test Architect) File-Type Branch routes `.opencode/skills/*/scripts/test_*.py` to `## PYTHON PYTEST TESTS` and returns `[PASS]` or `[FAIL]`; `[UNCERTAIN]` is not acceptable for that scope. Evidence: Crucible 🔥 (Test Architect) `1.2.0`; `[PASS]` on all four converted files.
- ✅ plan-enforce and `AGENTS.md` require the pytest command for Python skill tests and no longer forbid a test framework. Evidence: `AGENTS.md` `2.3.0`; plan-enforce `1.13.0`.

## Change log

- 2026-09-27 - python-pytest-20260927: created the durable pytest-runner definition.
- 2026-09-27 - python-pytest-20260927: locked `pytest==9.0.3` as `dev`; converted four suites (244 passed); Crucible 🔥 (Test Architect) `1.2.0` pytest ruleset.

## Resolved decisions

- 2026-09-27 - pytest is the single Python test runner as a root `dev` group; runtime deps stay PyYAML-only.
- 2026-09-27 - existing TestCase suites are converted in the same plan that introduces the runner.
- 2026-09-27 - collision with `plan-enforce-executor-validation`: keep executor-table rules; retire the no-pytest AC/decision; this story owns the runner.
