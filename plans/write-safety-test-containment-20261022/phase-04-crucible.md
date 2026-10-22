# Phase 4 — Verify held op-model change

> **Owner:** Crucible 🔥 (Test Architect)
> **Pre:** phases 2 and 3 accepted; plan audit `[PASS]`; user execution authorization for this turn.
> **Reads:** `.opencode/skills/op-model/scripts/op_model_lookup/infrastructure/process.py`; `infrastructure/test_process.py`; `e2e/conftest.py`; phase 2 return.
> **Writes:** none

## Assignment and resources

- Workflow / task / instance: `write-safety-test-containment-20261022` / `p4-opmodel-verify` / `p4-crucible`.
- Accepted predecessors / input identities: accepted phases 2 and 3; held `op-model` bytes recorded by hash at phase start.
- Permitted resource access: read the three op-model files; execute only the reviewed whole-suite command; no writes.
- Ownership / output destination: no mutable resource; the return is attributed to this instance.
- Required gates / continuation / join owner: Cipher 🔓 (Lead Orchestrator) accepts the return; no dependent phase.
- Capacity allocation / accounting owner: one verification slot from the coordinator ledger.
- Readiness / serialization evidence: last phase; no shared mutable resource; depends only on accepted implementation and docs.

## Steps

1. Cipher 🔓 (Lead Orchestrator) records the current SHA-256 identities of the three held op-model files; Crucible 🔥 (Test Architect) never runs Git or a hash command itself.
2. Run the reviewed whole-suite command through the project environment.
3. Confirm the op-model e2e executed the Windows `.cmd` shim (not skipped), record the fixture's redirected PATH value and the resolution evidence, and confirm no installed OpenCode binary was reachable.
4. Cipher 🔓 (Lead Orchestrator) recomputes the three SHA-256 identities after the run and confirms they are unchanged; the held change is verified, not modified.

## Output

- **Artifact:** verification record in this phase's return.
- **Schema / shape:** shell exit status, op-model e2e result, held-file identities before/after, and any skip.
- **Attribution / identities:** instance `p4-crucible`; consumed the suite command and held bytes.
- **Parent handoff:** verdict, evidence, and resource-release state.

## Verify commands

| Executor | Command |
|---|---|
| Crucible 🔥 (Test Architect) | `uv run --frozen --group dev pytest -q` |
| Cipher 🔓 (Lead Orchestrator) | `uv run --frozen python3 -B -c "import hashlib,pathlib; [print(hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest(), p) for p in ['.opencode/skills/op-model/scripts/op_model_lookup/infrastructure/process.py','.opencode/skills/op-model/scripts/op_model_lookup/infrastructure/test_process.py','.opencode/skills/op-model/scripts/op_model_lookup/e2e/conftest.py']]"` |

- The reviewer reports the suite execution separately from the test-architecture verdict.

## Gate

- ⬜ The reviewed whole-suite command exits 0.
- ⬜ The op-model e2e passes on Windows with the `.cmd` shim and is not skipped.
- ⬜ The three held op-model file identities are unchanged.
- ⬜ No installed OpenCode binary was reached by the e2e.
- ⬜ Execution evidence and verdict are recorded separately; parent accepted the return.

## Abort conditions

- Halt if the e2e is skipped or reaches the installed binary.
- Halt if the held bytes changed.
- Halt if the suite fails; report the literal failure instead of rerunning through a different command.
- Stop before any write; report `BLOCKED` to the parent.
