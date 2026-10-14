# Phase 3 — Documentation sweep

> **Owner:** Forge 🔨 (Implementer)
> **Pre:** T1 and T2 returns accepted by Cipher 🔓 (Lead Orchestrator) with their gate evidence; the combined candidate is stable at the join; write footprint disjoint from T1 (`knowledge/**`), T2 (registry and skill paths), and T4 (`user-stories/**`).
> **Reads:** `README.md`; `distribution-clearance.definition.md`; `knowledge/agents.md`; `knowledge/debt.md`; `knowledge/problems.md`; `knowledge/symptoms.md`; `knowledge/diagnostic-system-design.md`
> **Writes:** `README.md`

## Assignment and resources

- Workflow / task / instance: `knowledge-distribution-20261014` / T3 / Forge 🔨 (Implementer) instance 3 — documentation responsibility.
- Accepted predecessors / input identities: T1's accepted return (the delivered `knowledge/**` state) and T2's accepted return (registry, definition, parser) at their recorded content identities.
- Permitted resource access: read the delivered knowledge, registry, and definition files; write exactly `README.md`; no git state mutation; no writes under `knowledge/`, `distribution-clearance*`, `.opencode/skills/`, or `user-stories/`.
- Ownership / output destination: exclusive writer of `README.md`; the return goes to Cipher 🔓 (Lead Orchestrator).
- Required gates / continuation / join owner: the Verify command below; parent Cipher 🔓 (Lead Orchestrator) accepts the return and the combined candidate.
- Capacity allocation / accounting owner: Cipher 🔓 (Lead Orchestrator) shared ledger.
- Readiness / serialization evidence: serializes after the join on a real dependency — it reviews and describes the delivered state of T1 and T2, which must be accepted first.

## Steps

1. Edit `README.md`: rewrite the `knowledge/` inventory rows and the reuse-guide shipping policy to the delivered model — uniform core-region copy with no table declarations (register tables live in the core region and copy with it), the debt register shipping its frame only with entries as project-region content, the shared catalogs shipping in full, destination-filed records living in project regions and never substituted, and the living design shipping its shared contract under its new name; remove the retired seed instruction and the old living-design name, describing the retired seed without its literal filename; set the suite counts to the post-revert measurement from `uv run --frozen --group dev pytest --collect-only -q`.
2. Run the stale-name sweep over every non-temporal surface — the whole tree except `plans/`, `output/`, tool caches, and VCS internals, covering tracked and untracked deliverables alike — and report the verbatim output. The sweep runs before plan archival and is re-run by phase-04 after the story entries land.
3. Review the edited README and the delivered definition document against the delivered behaviour — reading the actual content, not this plan's description of it — and report any contradiction or its absence.

## Output

- **Artifact:** `README.md`
- **Schema / shape:** README inventory and reuse guide matching the delivered behaviour; stale-name sweep clean over every non-temporal surface.
- **Attribution / identities:** T3; consumed inputs are the accepted T1/T2 states at their recorded identities; produced content identity recorded in the return.
- **Parent handoff:** completed operations, gate evidence, and current resource-use state; author completion is not acceptance.

## Verify commands

| Executor | Command |
|---|---|
| Cipher 🔓 (Lead Orchestrator) | `! grep -rnI -e 'query-verification-design' -e 'debt\.template' --exclude-dir=plans --exclude-dir=output --exclude-dir=.git --exclude-dir=.venv --exclude-dir=__pycache__ .` |

## Gate

- ⬜ The Verify command exits 0 (no matches anywhere outside temporal areas) with its output recorded verbatim in the accepted return.
- ⬜ README and the definition document are reviewed against the delivered behaviour — the actual content, not this plan's description of it — and no contradiction survives.
- ⬜ Relevant content and dependencies stayed stable for review, identities and scope are recorded, and the parent accepted the return and the combined candidate; relevant changes invalidate affected verdicts before redispatch.

## Abort conditions

- Halt if README would contradict the delivered behaviour or if a stale name survives on any non-temporal surface — report `BLOCKED` with the evidence and bounded options.
- Stop before any out-of-assignment write or incompatible access; report `BLOCKED` with the exact need, evidence, and bounded options.
