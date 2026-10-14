# Phase 2 — Clearance registry and knowledge classes

> **Owner:** Forge 🔨 (Implementer)
> **Pre:** Goals G1–G3 confirmed; `core-sync` v1.1.0 contract active; stash gate clear at `00a6168d65e6` with no stash entries; user corrections 2026-10-14 (drift-watch) remove the interim `core_table` declaration — this phase delivers plain region rows and the class documentation; write footprint disjoint from T1 (`knowledge/**`), T3 (`README.md`), and T4 (`user-stories/**`).
> **Reads:** `distribution-clearance.json`; `distribution-clearance.definition.md`; `.opencode/skills/core-sync/SKILL.md`; `.opencode/skills/core-sync/scripts/core_sync_pkg/domain/clearance.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/domain/test_clearance_metadata.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_agent_versions.py`; `user-stories/core-sync.md`
> **Writes:** `distribution-clearance.json`; `distribution-clearance.definition.md`; `.opencode/skills/core-sync/SKILL.md`; `.opencode/skills/core-sync/scripts/core_sync_pkg/domain/clearance.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/domain/test_clearance_metadata.py`; `.opencode/skills/core-sync/scripts/core_sync_pkg/tests/test_agent_versions.py`

## Assignment and resources

- Workflow / task / instance: `knowledge-distribution-20261014` / T2 / Forge 🔨 (Implementer) instance 2 — registry and class-documentation responsibility, including the declaration removal.
- Accepted predecessors / input identities: T2's earlier deliveries at their recorded identities are superseded on the declaration only; the `test_agent_versions.py` pin fix (`66e47012…`) stands and is out of scope for removal.
- Permitted resource access: read the listed registry, skill, parser, and test files plus the approved stories; write exactly the six `**Writes:**` paths; no git state mutation; no writes under `knowledge/`, `README.md`, or `user-stories/`; the fixture verification may create and mutate only `/tmp/opencode/kd-dest`.
- Ownership / output destination: exclusive writer of the clearance registry, the definition document, and `.opencode/skills/core-sync/**`; the return goes to Cipher 🔓 (Lead Orchestrator).
- Required gates / continuation / join owner: Bastion 🧱 (Backend & Scripts Architect) `[PASS]` on the Python edits and Crucible 🔥 (Test Architect) `[PASS]` on the reviewed whole-suite command and test architecture; parent Cipher 🔓 (Lead Orchestrator) accepts and dispatches continuation.
- Capacity allocation / accounting owner: Cipher 🔓 (Lead Orchestrator) shared ledger.
- Readiness / serialization evidence: concurrent with T1 and T3 on verified disjoint write footprints.

## Steps

1. Restore `core_sync_pkg/domain/clearance.py` to its pre-plan content at `00a6168d65e6` — remove the `core_table` field, the boolean validation, and the shape docstring changes: the model is uniform core-region copy-paste and no declaration is consumed anywhere (user correction 2026-10-14).
2. Restore `core_sync_pkg/domain/test_clearance_metadata.py` to its pre-plan content at `00a6168d65e6` — remove the three `core_table` cases and their factory/TypedDict additions; keep every other case untouched.
3. Edit `distribution-clearance.json`: keep the five `knowledge/` `region` rows and remove the `core_table: true` attributes from `knowledge/agents.md`, `knowledge/problems.md`, and `knowledge/symptoms.md` — every knowledge row becomes plain `{ "mode": "region" }`; schema `1` and every other row stay byte-identical.
4. Edit `distribution-clearance.definition.md`: remove `core_table` from the file-record shapes and delete the `## Core table` section; keep and reword `## Knowledge distribution classes` so it states the classes without a declaration concept — shared rules; record-bearing register whose core is frame-only and carries no table (the debt register); shared catalog whose core ships in full; living design whose core is the shared contract with refinement state project-side — and keep the retired seed described without its literal filename.
5. Restore `.opencode/skills/core-sync/SKILL.md` to its pre-plan content at `00a6168d65e6` — remove the `core_table` record-shape mention and paragraph.
6. Confirm `core_sync_pkg/tests/test_agent_versions.py` still carries the user-approved pin fix (`inquisitor.md`: `1.5.0`) and change nothing in it.
7. Run every Verify command — the reviewed whole-suite command, the fixture chain, and the registry row count — and report each output verbatim in the phase return.

## Output

- **Artifact:** `distribution-clearance.json`
- **Schema / shape:** schema `1` with five plain knowledge region rows and no table declarations; the definition document and README-facing classes describe the distribution classes; the parser and skill prose are back at their pre-plan content; the agent-version pin matches the delivered `inquisitor.md` frontmatter; the fixture chain exits 0 reporting the knowledge rows current.
- **Attribution / identities:** T2; produced content identities recorded in the return (the restored files must match their `00a6168d65e6` content byte-for-byte).
- **Parent handoff:** completed operations, Bastion 🧱 (Backend & Scripts Architect) and Crucible 🔥 (Test Architect) gate evidence, fixture chain output, and current resource-use state; author completion is not acceptance.

## Verify commands

| Executor | Command |
|---|---|
| Crucible 🔥 (Test Architect) | `uv run --frozen --group dev pytest -q` |
| Cipher 🔓 (Lead Orchestrator) | `uv run --frozen python3 -c "import json,pathlib,shutil;shutil.rmtree('/tmp/opencode/kd-dest',ignore_errors=True);d=pathlib.Path('/tmp/opencode/kd-dest');sp=pathlib.Path('.');(d/'.aicore').mkdir(parents=True,exist_ok=True);(d/'AGENTS.md').write_text('# Destination\n');(d/'opencode.jsonc').write_text('{}\n');cl=json.loads((sp/'distribution-clearance.json').read_text())['cleared'];[(d/k).mkdir(parents=True,exist_ok=True) if k.endswith('/') else (d/k).parent.mkdir(parents=True,exist_ok=True) for k in cl];[((d/p).mkdir(parents=True,exist_ok=True)) for k in cl if k.endswith('/') for p in (sp/k).rglob('*') if p.is_dir()]" && uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py init --source . --destination /tmp/opencode/kd-dest --bindings /tmp/opencode/kd-dest/.aicore/core.yaml --source-revision 00a6168d65e6e5eb15332ce4fd2f4eca5570bac1 --bind-cleared && uv run --frozen python3 -c "import pathlib,yaml;p=pathlib.Path('/tmp/opencode/kd-dest/.aicore/core.yaml');d=yaml.safe_load(p.read_text());d['pending']=[];p.write_text(yaml.safe_dump(d, sort_keys=False))" && uv run --frozen python3 .opencode/skills/core-sync/scripts/core_sync.py check --source . --destination /tmp/opencode/kd-dest --bindings /tmp/opencode/kd-dest/.aicore/core.yaml --source-revision 00a6168d65e6e5eb15332ce4fd2f4eca5570bac1` |
| Cipher 🔓 (Lead Orchestrator) | `grep -c 'knowledge/' distribution-clearance.json` |

## Gate

- ⬜ Crucible 🔥 (Test Architect) ran the reviewed whole-suite command with exit 0 and returned a test-architecture `[PASS]`; Bastion 🧱 (Backend & Scripts Architect) returned `[PASS]` on the Python edits; `[FAIL]` or `[UNCERTAIN]` blocks the phase.
- ⬜ No `core_table` reference remains in any durable surface outside `plans/`, and the restored files match their `00a6168d65e6` content byte-for-byte.
- ⬜ The registry keeps schema `1`, keeps every non-knowledge row byte-identical, and carries exactly five plain `knowledge/` region rows.
- ⬜ The fixture chain exits 0 and verification reports the five knowledge rows current.
- ⬜ The agent-version pin still matches the delivered `inquisitor.md` frontmatter and no other pinned version changed.
- ⬜ This phase ships documentation content: the definition document is reviewed against the delivered uniform model, not against this plan's description of it.
- ⬜ Relevant content and dependencies stayed stable for review, identities and scope are recorded, and the parent accepted the return; relevant changes invalidate affected verdicts before redispatch.

## Abort conditions

- Halt if the whole-suite command exits non-zero after the second unchanged run, if any pre-existing case regresses, or if a restore would deviate from the `00a6168d65e6` content — report `BLOCKED` with the literal output and the bounded options.
- Halt if the fixture chain fails after one retry from its self-cleaned directory — report the literal `init`/`check` output rather than editing around it.
- Halt if a registry row would reference a path outside this plan's confirmed names, or if the pin fix would be disturbed.
- Stop before any out-of-assignment write or incompatible access; report `BLOCKED` with the exact need, evidence, and bounded options.
