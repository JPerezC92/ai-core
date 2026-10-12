# User story — python-pytest

> **Created:** 2026-09-27
> **Title:** Python pytest test runner
> **Status:** active
> **version:** 1.2.0
> **Epic:** developer-tooling
> **Affected areas:** `pyproject.toml`, `uv.lock`, `.opencode/agents/crucible.md`, `.opencode/agents/bastion.md`, `.opencode/agents/ledger.md`, `.opencode/skills/plan-enforce/`, `.opencode/skills/ticket-runbook/`, `.opencode/skills/query-verification/`, `.opencode/skills/*/scripts/test_*.py`, `AGENTS.md`, `opencode.jsonc`

## Persona

- A core maintainer running AICore's Python skill tests; an adopter selects its own approved development-test runner for Crucible 🔥 (Test Architect).

## Goal

- **G:** AICore's Python tests run as one reviewed, project-wide suite, and Crucible 🔥 (Test Architect) reports running it separately from judging its architecture. Other projects approve their own runner.
  - Done when: the approved whole-suite command collects and passes every Python test under the project root except the configured exclusions; a test added anywhere under the root joins without a configuration or permission edit; the suite runs in parallel under the unchanged reviewed command; the runner is not a dependency of the shipped package; filesystem cases use temporary directories; and Crucible 🔥 (Test Architect) returns execution results separately from an architecture verdict.

## Scenario

- A programming phase edits or adds a Python test. The phase runbook declares the project's approved whole-suite command in the executor-command table. Bastion 🧱 (Backend & Scripts Architect) audits applicable Python implementation. Crucible 🔥 (Test Architect) runs the suite and returns its test-architecture verdict; a test added under the project root outside the configured exclusions joins the suite without editing `pyproject.toml` or the grant, because discovery is project-wide rather than a positive list of directories.

## Acceptance criteria

- ✅ **AC1:** The approved whole-suite command runs the complete Python suite and passes on a clean candidate.
- ✅ **AC2:** Any test placed under the project root outside the configured exclusions joins the suite without editing configuration or permissions.
- ✅ **AC3:** The suite runs in parallel under the unchanged reviewed command.
- ✅ **AC4:** The test runner and its parallelism helper are not dependencies of the shipped package.
- ✅ **AC5:** Crucible 🔥 (Test Architect) owns execution and test-architecture review for each project's approved whole suite, including tests outside skill directories, and reports them as separate verdicts; a cancelled or missing review is never reported as passing.
- ✅ **AC6:** AICore's harness config grants Crucible 🔥 (Test Architect) exactly the reviewed whole-suite command plus narrow read-only discovery, and the shared spec carries no executable grant of its own.
- ✅ **AC7:** The approved runner is project-owned: AICore's command is never imposed on another project, and each destination reviews and owns its own runner policy.
- ✅ **AC8:** Each test module and each test class covers one behavioural concern; shared builders live in undiscovered helper modules and filesystem cases use temporary directories rather than production data or host Git state.
- ✅ **AC9:** Every Python command runs through the project virtual environment; no AICore-owned example invokes a bare or global interpreter.
- ✅ **AC10:** `plan-enforce` and `AGENTS.md` require the approved command for Python skill tests and do not forbid the chosen framework.

## Proof

- AC1 → `.opencode/skills/plan-enforce/SKILL.md` `#### Non-TypeScript test files` · `uv run --frozen --group dev pytest -q` → exit 0 · Crucible 🔥 (Test Architect) architecture `[PASS]`
- AC2 → `pyproject.toml` `[tool.pytest.ini_options]` `testpaths`, `python_files`, `python_classes`, `norecursedirs` · `uv run --frozen --group dev pytest -q` → exit 0
- AC3 → `pyproject.toml` `[tool.pytest.ini_options]` `addopts` · `uv.lock` `pytest-xdist` · Warden 🔒 (Dependency Warden) `[PASS]` 2026-10-05
- AC4 → `pyproject.toml` `[dependency-groups].dev` vs `[project].dependencies` · `uv lock --check` → exit 0 · Warden 🔒 (Dependency Warden) `[PASS]` 2026-09-27
- AC5 → `.opencode/agents/crucible.md` `### Test Execution`, `### Test Organization by Concern`
- AC6 → `.opencode/agents/crucible.md` `### Bash Grant Scope`, `### Local Permissions` · `opencode.jsonc` · `opencode debug config > /dev/null` → exit 0
- AC7 → `.opencode/agents/warden.md` `#### Bash Grant Registry` · `.opencode/agents/crucible.md` `### Test Execution`
- AC8 → `.opencode/agents/crucible.md` `### Test Organization by Concern` · underscore-prefixed testkit modules · `tmp_path`
- AC9 → `AGENTS.md` `### Environment constraints` · validator and query examples
- AC10 → `AGENTS.md` Conventions · `.opencode/skills/plan-enforce/SKILL.md` `#### Non-TypeScript test files`

## Constraints

- pytest is the single Python test runner, locked in the root `dev` group — because one reviewed runner keeps the executor grant and the command literal from drifting apart.
- Parallelism ships as pytest configuration rather than a separate command — because the reviewed command literal and its permission grant must not drift.
- Runtime `[project].dependencies` stays PyYAML-only — because skill test tooling must never become a downstream runtime requirement.
- Whole-suite discovery is project-wide, not a directory allowlist — because a positive list forces a configuration edit for every new test location.
- Test organization is one behavioural concern per module and per class, with no line cap — because behaviour, not size, sets the boundary.
- Baseline suites are pytest-native, with no `unittest.TestCase` inheritance or `unittest.main()` entrypoint — because mixing frameworks splits the executor grant and the runner policy.
- Runner validation is structural, not heuristic — because text scanning cannot establish that a grant is narrow or that a command is the reviewed one.
- Architecture review is separate from execution — because a passing suite never establishes architectural conformance.

## Change log

- before 2026-09-27 — earlier history: see git history for this file
- 2026-09-27 — python-pytest-20260927 (PR #43): adopted pytest as the Python runner with whole-project discovery and the reviewed whole-suite command.
- 2026-10-07 — core-sync-review (PR #52): narrowed Crucible's discovery permissions, aligned AICore Python invocation examples with `uv run --frozen`, and split mixed core-sync test concerns.
- 2026-10-09 — aicore-all-files-pr-20261008 (PR #51): applied the frozen-environment Python invocation contract across the full ticket-runbook and query-verification skill roots.
- 2026-10-11 — regionize-agents-20261010 (PR #53): inherited test and backend reference rulebooks now ship in core; runner selection and executable grants stay project-owned.
- 2026-10-12 — story revision (PR #59): split behavioural criteria from proof, removed the enumerated test-file inventory from `Done when:`, and promoted pre-decided runner policy into `## Constraints`.
