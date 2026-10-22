# Phase 1 — Contain test temp roots

> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Pre:** stash gate passed (no stash entries); plan audit `[PASS]`; user execution authorization for this turn.
> **Reads:** `pyproject.toml` `[tool.pytest.ini_options]`; `.gitignore`; installed `_pytest/tmpdir.py`; current absence of a root `conftest.py`.
> **Writes:** `conftest.py`; `tests/test_pytest_temp_root.py`

## Assignment and resources

- Workflow / task / instance: `write-safety-test-containment-20261022` / `p1-containment` / `p1-cipher`.
- Accepted predecessors / input identities: none; the held working tree is not modified by this phase.
- Permitted resource access: create the two declared paths; read pytest configuration and installed pytest source; run no test command (Crucible 🔥 (Test Architect) executes). Root config and the root `tests/` directory are outside Forge 🔨 (Implementer)'s plan-scoped `.opencode/skills/*/scripts/` Python edit scope (`.opencode/agents/forge.md:44-49`), and Crucible 🔥 (Test Architect) never writes tests, so the coordinator owns this phase's writes.
- Ownership / output destination: Cipher 🔓 (Lead Orchestrator) is the only writer of these two paths; `output/.pytest-tmp/` is runtime state, not a tracked artifact.
- Required gates / continuation / join owner: Bastion 🧱 (Backend & Scripts Architect) `[PASS]` under Cipher 🔓 (Lead Orchestrator)'s explicit assignment of the root `conftest.py` to the Python rulebook, then Crucible 🔥 (Test Architect) `[PASS]`; Cipher 🔓 (Lead Orchestrator) accepts and releases phase 2.
- Capacity allocation / accounting owner: one writer slot from the coordinator ledger.
- Readiness / serialization evidence: independent of phases 2–4 except that its accepted suite run establishes containment for their suite runs.

## Steps

1. Add a root `conftest.py` that sets pytest's base temporary directory to a per-process path under `<project>/output/.pytest-tmp/` when the caller did not supply `--basetemp`. The directory must be unique per process so parallel workers never delete a shared directory, and `--basetemp` must still win when supplied.
2. Ensure the setting applies before `tmp_path` is first resolved, and that `output/` remains excluded from collection.
3. Add `tests/test_pytest_temp_root.py` asserting that `tmp_path` and the factory base directory both resolve inside the project root; the assertion must fail if the containment is removed.
4. Do not change `pyproject.toml`, `.gitignore`, or the reviewed suite command.

## Output

- **Artifact:** `conftest.py`; `tests/test_pytest_temp_root.py`
- **Schema / shape:** root conftest with the basetemp rule; one test module with containment assertions and no symlink creation.
- **Attribution / identities:** instance `p1-cipher`; consumed `pyproject.toml` at the current tree; produced file identities recorded on return.
- **Parent handoff:** changed paths, content identities, Bastion 🧱 (Backend & Scripts Architect) and Crucible 🔥 (Test Architect) verdicts, and current resource-use state.

## Verify commands

| Executor | Command |
|---|---|
| Crucible 🔥 (Test Architect) | `uv run --frozen --group dev pytest -q` |
| Cipher 🔓 (Lead Orchestrator) | `uv run --frozen python3 -B -c "import pathlib,tempfile; print(sorted(p.name for p in pathlib.Path(tempfile.gettempdir()).glob('pytest-of-*/*')))"` |

- The reviewer records that the session-directory name set under the host temp parent is unchanged during the run.
- Python `test_*.py` edits: Bastion 🧱 (Backend & Scripts Architect) `[PASS]` and Crucible 🔥 (Test Architect) `[PASS]` are required; `[UNCERTAIN]` is not acceptable.

## Gate

- ⬜ `conftest.py` sets a per-process project-contained basetemp without deleting another process's directory.
- ⬜ `tests/test_pytest_temp_root.py` passes and would fail without the conftest rule.
- ⬜ Crucible 🔥 (Test Architect) ran the reviewed whole-suite command with exit 0; Bastion 🧱 (Backend & Scripts Architect) `[PASS]`; Crucible 🔥 (Test Architect) test-architecture `[PASS]`.
- ⬜ The session-directory name set under the host temp parent is unchanged.
- ⬜ Reviewed content stayed stable; identities and scope recorded; parent accepted the return.

## Abort conditions

- Halt if containment requires changing the reviewed suite command or `pyproject.toml`.
- Halt if `--basetemp` cannot be set before `tmp_path` resolves.
- Halt if parallel workers delete or share one directory.
- Halt if the project path length breaks a test on Windows; report the measured path instead of shortening test names.
- Stop before any out-of-assignment write or incompatible access; report `BLOCKED` to the parent.
