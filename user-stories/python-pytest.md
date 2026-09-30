# User story — python-pytest

> **Created:** 2026-09-27
> **Title:** Python pytest test runner
> **Status:** active
> **version:** 1.1.0
> **Epic:** developer-tooling
> **Affected areas:** `pyproject.toml`, `uv.lock`, `.opencode/agents/crucible.md`, `.opencode/agents/bastion.md`, `.opencode/skills/plan-enforce/`, `.opencode/skills/*/scripts/test_*.py`, `AGENTS.md`

## Persona

- A core maintainer running AICore's Python skill tests; an adopter selects its own approved development-test runner for Crucible 🔥 (Test Architect).

## Goal

- **G:** pytest is AICore's Python test runner, locked in the root UV `dev` group; Crucible 🔥 (Test Architect) runs the approved whole suite and audits its test architecture. Other projects approve their own suite commands.
  - Done when: `uv run --frozen --group dev pytest -q` collects and passes every `test_*.py` in the project — wherever it lives, with no subdirectory allowlist and no per-file permission edit; pytest remains outside runtime `[project]` dependencies; Crucible 🔥 (Test Architect) reports the execution result and an architecture `[PASS]`.

## Scenario

- A programming phase edits or adds a Python test. The phase runbook declares the project's approved whole-suite command (AICore: `uv run --frozen --group dev pytest -q`) in the executor-command table. Bastion 🧱 (Backend & Scripts Architect) audits applicable Python implementation. Crucible 🔥 (Test Architect) runs the suite and returns its test-architecture verdict; a test added anywhere in the project joins that suite without editing `pyproject.toml` or the grant, because discovery is project-wide rather than a list of directories.

## Acceptance criteria

- ✅ pytest is locked only under `[dependency-groups] dev`; `[project].dependencies` stays PyYAML-only; `uv lock --check` exits 0. Evidence: `pyproject.toml` `pytest==9.0.3` in `dev`; `PyYAML==6.0.3` only in `[project].dependencies`; Warden 🔒 (Dependency Warden) downstream `[PASS]` `output/audits/2026-09-27-pytest-lockfile.md`.
- ✅ `uv run --frozen --group dev pytest -q` exits 0 and collects every `test_*.py` in the project, wherever it lives. Evidence: `pyproject.toml` `testpaths = ["."]` with junk-only `norecursedirs` (no `.*` entry); all four skill script files plus every later addition are collected.
- ✅ Those four files are pytest-native: no `unittest.TestCase` and no `unittest.main()`. Evidence: `git grep -n "unittest.TestCase"` and `git grep -n "unittest.main("` under `.opencode/skills/` return no matches.
- ✅ Crucible 🔥 (Test Architect) File-Type Branch routes `.opencode/skills/*/scripts/test_*.py` to `## PYTHON PYTEST TESTS` and returns `[PASS]` or `[FAIL]`; `[UNCERTAIN]` is not acceptable for that scope. Evidence: Crucible 🔥 (Test Architect) `1.2.0`; `[PASS]` on all four converted files.
- ✅ plan-enforce and `AGENTS.md` require the pytest command for Python skill tests and no longer forbid a test framework. Evidence: `AGENTS.md` `2.3.0`; plan-enforce `1.13.0`.
- ✅ AICore's root `opencode.jsonc` permits Crucible 🔥 (Test Architect) to execute the reviewed whole-suite command, and the shared agent spec does not copy that UV grant into unrelated adopters. Evidence: `uv run --frozen --group dev pytest -q`; `.opencode/agents/crucible.md` 1.3.0 has no frontmatter grant.
- ✅ Restarted Crucible 🔥 (Test Architect) runs and audits every `test_*.py` in the project; the hermetic discovery test proves a new test dropped outside `.opencode/` is collected with no `pyproject.toml` or grant edit, and leaves no workspace artefact. A different framework in an adopting project needs a newly reviewed project-owned suite command. Evidence: `TestpathsDiscoveryTests.test_testpaths_discovers_probes_outside_opencode`; `RunnerPolicyTests` proves `check`/`propose-lock` accept the exact fixed suite and a destination's own reviewed package test while rejecting path/wildcard/reordered/interior-whitespace variants.

## Change log

- 2026-09-29 - catalog-driven-adoption-20260929: Phase 4 made discovery **project-wide** — `pyproject.toml` now uses `testpaths = ["."]` with junk-only `norecursedirs` (`node_modules`, `.venv`, `output`, `plans/.completed`, `build`, `dist`, `__pycache__`, `.git`) and deliberately **no** `.*` entry, so a `test_*.py` anywhere in the project is collected with no config or grant edit; the previous 4-directory allowlist silently skipped tests outside itself. Added `TestpathsDiscoveryTests.test_testpaths_discovers_probes_outside_opencode`, which drops probes outside `.opencode/` and restores the workspace byte-for-byte. Added the net-new runner-policy validator: `check`/`propose-lock`/`apply` accept the exact fixed suite command by literal comparison and a destination's own reviewed package test, and reject path/wildcard/reordered/interior-whitespace variants plus broad catch-all allows as `policy_violation`, without ever imposing AICore's command on another project — `RunnerPolicyTests` (12 tests). `protocol-v2.md` §11 documents the runner policy. Corrected previously recorded evidence that cited a non-existent `RootSuiteDiscoveryTests` class and a stale `313 passed` figure; that class was never part of this plan.
- 2026-09-27 - python-pytest-20260927: created the durable pytest-runner definition.
- 2026-09-27 - python-pytest-20260927: locked `pytest==9.0.3` as `dev`; converted four suites (244 passed); Crucible 🔥 (Test Architect) `1.2.0` pytest ruleset.
- 2026-09-28 — plan-enforce-story-fold-20260928: version 1.1.0 separates AICore's UV pytest runner from the portable Crucible 🔥 (Test Architect) execution role; test-runner permissions belong to each project's root config.
- 2026-09-28 — plan-enforce-story-fold-20260928: user corrected G6 from a single-file grant to whole-suite execution and future test discovery; historical single-file evidence is retained but not treated as proof of the new criterion.

## Resolved decisions

- 2026-09-27 - pytest is the single Python test runner as a root `dev` group; runtime deps stay PyYAML-only.
- 2026-09-27 - existing TestCase suites are converted in the same plan that introduces the runner.
- 2026-09-27 - collision with `plan-enforce-executor-validation`: keep executor-table rules; retire the no-pytest AC/decision; this story owns the runner.
- 2026-09-28 - plan-enforce-story-fold-20260928: that collision target is now `plan-enforce` (the executor-validation file is superseded).
