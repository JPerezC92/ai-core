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

- **G:** pytest is AICore's Python test runner, locked in the root UV `dev` group; the approved whole suite runs worker-parallel via `[tool.pytest.ini_options] addopts` with `pytest-xdist` in that group; Crucible 🔥 (Test Architect) runs the approved whole suite and audits its test architecture. Other projects approve their own suite commands.
  - Done when: `uv run --frozen --group dev pytest -q` collects and passes every `test_*.py` in the project — wherever it lives, with no subdirectory allowlist and no per-file permission edit — with worker distribution active; pytest and pytest-xdist remain outside runtime `[project]` dependencies; Crucible 🔥 (Test Architect) reports the execution result and an architecture `[PASS]`.

## Scenario

- A programming phase edits or adds a Python test. The phase runbook declares the project's approved whole-suite command (AICore: `uv run --frozen --group dev pytest -q`) in the executor-command table. Bastion 🧱 (Backend & Scripts Architect) audits applicable Python implementation. Crucible 🔥 (Test Architect) runs the suite and returns its test-architecture verdict; a test added anywhere in the project joins that suite without editing `pyproject.toml` or the grant, because discovery is project-wide rather than a list of directories.

## Acceptance criteria

- ✅ pytest is locked only under `[dependency-groups] dev`; `[project].dependencies` stays PyYAML-only; `uv lock --check` exits 0. Evidence: `pyproject.toml` `pytest==9.0.3` in `dev`; `PyYAML==6.0.3` only in `[project].dependencies`; Warden 🔒 (Dependency Warden) downstream `[PASS]` on the dev-group lockfile change (2026-09-27).
- ✅ The approved whole-suite command `uv run --frozen --group dev pytest -q` collects the delivered configuration/layout owner and passes on the complete clean candidate, with separate test architecture. Evidence: Crucible 🔥 architecture `[PASS]`; the whole suite passes (exact `uv run --frozen --group dev pytest -q`, exit 0). Discovery and the grant are unchanged.
- ✅ The whole suite runs worker-parallel under the unchanged reviewed command: `[tool.pytest.ini_options]` carries `addopts = ["-n", "auto"]` and `pytest-xdist` is locked only under `[dependency-groups] dev`. Evidence: `pyproject.toml` `[dependency-groups]` and `[tool.pytest.ini_options]`; `uv lock --check` exits 0; `uv run --frozen --group dev pytest -q` exit 0; Warden 🔒 (Dependency Warden) downstream `[PASS]` on the dev-group lockfile change (2026-10-05).
- ✅ Existing baseline suites are pytest-native: no `unittest.TestCase` inheritance or `unittest.main()` entrypoint. The split must retain those conventions; `unittest.mock` remains allowed. Evidence: baseline Python test classes at commit `f502d54`.
- ✅ Crucible 🔥 (Test Architect) owns execution and test-architecture review for each project's approved whole suite, including tests outside skill directories. It reports actual execution results separately from architecture `[PASS]`/`[FAIL]`; cancelled or missing review output is never relabeled `[PASS]`. Evidence: `.opencode/agents/crucible.md` 1.5.0 (whole-suite executor + separate execution/architecture reporting + project-wide discovery, no copied UV grant); Warden 🔒 (Dependency Warden) 1.5.0 and Inquisitor 🔎 (PR Reviewer) 1.4.0 aligned (Inquisitor routes test dispatch through Cipher 🔓 (Lead Orchestrator)); Crucible 🔥 (Test Architect) executes the root suite (`uv run --frozen --group dev pytest -q` exit 0) and returns the architecture verdict separately. Earlier narrower run counts are history, not current evidence.
- ✅ plan-enforce and `AGENTS.md` require the pytest command for Python skill tests and no longer forbid a test framework. Evidence: `AGENTS.md` Conventions; `plan-enforce` test-runner rules.
- ✅ AICore's root `opencode.jsonc` permits Crucible 🔥 (Test Architect) to execute the reviewed whole-suite command, and the shared agent spec does not copy that UV grant into unrelated adopters. Evidence: `uv run --frozen --group dev pytest -q`; `.opencode/agents/crucible.md` 1.5.0 has no frontmatter grant.
- ✅ Whole-project discovery is verified in an isolated temporary project, including tests in `tests/`, `src/`, a package, and a dot-directory; proof writes only under `tmp_path`, with its cache isolated, and touches no real repository probe/cache/user file. New project-wide tests require no per-file grant edit. Evidence: `.opencode/skills/sync-aicore-adoption/scripts/test_adoption_discovery.py::TestpathsDiscoveryTests::test_testpaths_discovers_project_locations_and_excludes_configured_junk`; Crucible 🔥 (Test Architect) static `[PASS]` and whole suite `uv run --frozen --group dev pytest -q` exit 0.
- ✅ Destination runner/no_tests authority and structural permission validation remain project-owned. Evidence: `test_adoption_runner_policy.py::RunnerPolicyTests` delivers the permission/JSONC/last-match-wins coverage; protocol-v2.md §8 and `adoption_policies.py` remain; sectioned rulebooks delivered (Sentinel 🛡️ PASS). AICore's runner is not imposed on adopters.
- ✅ Focused native pytest owners deliver all unique surviving behavior with temporary IO and no unnecessary Git setup for pure layout tests. Evidence: `test_adoption_config.py` delivers the assertion and guarded-root owners, `test_adoption_runner_policy.py` the runner-policy owner, and `test_adoption_layout.py` the layout owner, all with `tmp_path` IO; the old monolith stays deleted; recovery stays removed; no exact old count is required.
- ✅ Safety evidence distinguishes production reads, operator instructions, and fixture behavior. Controlled reads suppress optional index refresh, resolve real Git paths, and refuse lazy fetch. A clean bisect is not unsaved work. No state machine or Cartesian matrix was added. Evidence: Bastion 🧱 (Backend & Scripts Architect) `[PASS]` and Crucible 🔥 (Test Architect) architecture `[PASS]` on the controlled-read tests. The controlled-read tests pass under the whole suite `uv run --frozen --group dev pytest -q`.
- ✅ The delivered source separates AICore's UV environment from portable mandatory executor/review rules and preserves destination suite/installation authority. Evidence: `AGENTS.md` and the sectioned specs/skills keep project environment in Project extensions and portable rules in Mandatory core (Sentinel 🛡️ PASS 27/27); dependency groups and the literal suite grant are unchanged.
- ✅ Delivered rulebooks separate concrete test/framework/client preferences from generic hermeticity, traceability, IO/type safety and approvals. Evidence: `crucible.md`/`bastion.md` and the other sectioned specs keep framework examples in Project extensions and generic obligations in Mandatory core; Sentinel 🛡️ PASS; mandatory obligations are retained, not keyword-stripped.
- ✅ Test organization is by behavioral concern with no line cap: one concern per collected module, a module mixing unrelated concerns is split by concern, and a cohesive single-concern module stays whole however long it grows. Evidence: `.opencode/agents/crucible.md` 1.5.0 `### Test Organization by Concern` states the rule; the adoption suite split its former monoliths into concern-scoped modules (`test_adoption_candidates.py`, `test_adoption_lineage.py`, `test_adoption_protected_convergence.py`, `test_adoption_historical_assessment.py`, `test_adoption_protection_policy.py`, `test_adoption_notice.py`, `test_adoption_enrollment.py`, `test_adoption_runner_policy.py`, `test_adoption_layout.py`, `test_adoption_schema_parsing.py`, `test_adoption_lock_validity.py`, `test_adoption_protected_schema.py`, `test_adoption_review_snapshot.py`, `test_adoption_review_evidence.py`, `test_adoption_review_protected.py`, `test_adoption_snapshot_explicitness.py`, `test_adoption_snapshot_readonly.py`, `test_adoption_snapshot_live_state.py`) and deleted the four originals.
- ✅ Every Python command runs through the project virtual environment via `uv run --frozen`; a bare or global interpreter is never used. Evidence: `AGENTS.md` Environment constraints; the approved whole-suite command is `uv run --frozen --group dev pytest -q` and validators run as `uv run --frozen python3 …`.

## Change log

- 2026-10-05 — pytest-parallel-execution-20261005: added worker-parallel suite execution via addopts with pytest-xdist in the dev group; reviewed command unchanged.
- 2026-10-05 — adoption-test-split-debt-guard-20261005: recorded the concern-based test-organization rule and the project-venv rule; repointed runner/layout evidence to their concern modules.
- 2026-10-05 — sectioned-core-delivery-reconciliation-20261005: delivered the whole-suite Crucible runner with destination-owned runner governance.
- 2026-09-30 — catalog-driven-adoption: made discovery project-wide (`testpaths = ["."]`) and added the structural runner-policy validator.
- 2026-09-28 — plan-enforce-story-fold: separated AICore's UV pytest runner from the portable Crucible execution role.
- before 2026-09-28 — earlier history: see git history for this file.

## Resolved decisions

- 2026-09-27 — pytest is the single Python test runner, locked in the root `dev` group; runtime dependencies stay PyYAML-only.
- 2026-09-30 — whole-suite runner governance is project-owned; AICore's approved command is never imposed on another project.
- 2026-10-01 — runner validation is structural, not heuristic: only the nominated executor's ordered rules are inspected (last-match-wins); broad wildcard grants, malformed JSONC, and unapproved commands fail closed.
- 2026-10-05 — actual commands and outputs establish evidence; labels and text scanning do not. Architecture review is separate from execution.
- 2026-10-05 — safety tests label engine/helper/operator scopes and establish actual controlled effects; unsupported concerns are rejected before adding test obligations.
- 2026-10-05 — parallel execution ships as `[tool.pytest.ini_options] addopts` so the reviewed command literal and its permission grant never drift.
