# Phase 1 — Knowledge content split and rename

> **Owner:** Forge 🔨 (Implementer)
> **Pre:** Goals G1–G3 confirmed by the user; `core-sync` v1.1.0 and `diagnostic-system` v1.0.0 contracts active with their `**Contract approval:**` records; stash gate clear at `00a6168d65e6` with no stash entries; this phase's write footprint is disjoint from T2 (`distribution-clearance*`, `.opencode/skills/core-sync/**`), T3 (`README.md`), and T4 (`user-stories/**`); the two heading resolutions are applied (living-design carve produces `## Purpose`/`## Status`; verify row 5 names the real `knowledge/agents.md` heading).
> **Reads:** `knowledge/agents.md`; `knowledge/debt.md`; `knowledge/debt.template.md`; `knowledge/problems.md`; `knowledge/symptoms.md`; `knowledge/query-verification-design.md`; `user-stories/core-sync.md`; `user-stories/diagnostic-system.md`; `user-stories/incident-query-verification-pilot.md`; `user-stories/register-first-incident-identification.md`; `AGENTS.md`
> **Writes:** `knowledge/agents.md`; `knowledge/debt.md`; `knowledge/problems.md`; `knowledge/symptoms.md`; `knowledge/diagnostic-system-design.md`; `knowledge/query-verification-design.md`; `knowledge/debt.template.md`

## Assignment and resources

- Workflow / task / instance: `knowledge-distribution-20261014` / T1 / Forge 🔨 (Implementer) instance 1 — knowledge content responsibility.
- Accepted predecessors / input identities: none — independent of T2; consumed inputs are the five source knowledge files and the three approved story bodies at their persisted identities.
- Permitted resource access: read the listed knowledge and story files; write exactly the seven `**Writes:**` paths, including the two deletions; no git state mutation; no writes under `distribution-clearance*`, `.opencode/skills/`, `README.md`, or `user-stories/`.
- Ownership / output destination: exclusive writer of `knowledge/**` for this workflow; the return goes to Cipher 🔓 (Lead Orchestrator).
- Required gates / continuation / join owner: the Verify commands below; parent Cipher 🔓 (Lead Orchestrator) accepts the return and dispatches continuation.
- Capacity allocation / accounting owner: Cipher 🔓 (Lead Orchestrator) shared ledger.
- Readiness / serialization evidence: concurrent with T2 on verified disjoint write footprints (`knowledge/**` versus registry and skill paths); no shared mutable resource.

## Steps

1. Edit `knowledge/agents.md`: move the `## Mandatory core` block (including the roster table) above `## Project extensions`; wrap the mandatory block in `<!-- core:begin -->` and `<!-- core:end -->`; wrap the extensions block in `<!-- project:begin -->` and `<!-- project:end -->`; preserve every heading and table row byte-for-byte — including `### Bounded-query discipline (SELECT-in-WHERE)`, which keeps its exact name. Move the `### Knowledge registers` block into the core region (adjacent to the register-first rules) with the approved neutral wording — "The symptom-class catalog is `knowledge/symptoms.md` and the known-problem register is `knowledge/problems.md`. A project that does not enable the incident domain replaces these with its own registers in its project extension." — and keep `## Project extensions` as the project region's surface for such overrides.
2. Edit `knowledge/debt.md`: wrap the frame — title through the `## Register` heading — in the core pair; wrap the entries area (currently the single empty-state line) in the project pair; do not add a core table.
3. Delete `knowledge/debt.template.md`.
4. Edit `knowledge/problems.md`: wrap the whole body in the core pair — frame, entry format, lifecycle, rules, and the Register core table — and replace the empty-register sentence with the frame rule `An empty register is valid and identifies as no_match.`; add no project pair because no source-side project text exists.
5. Edit `knowledge/symptoms.md`: wrap the whole body in the core pair — catalog, matching rules, register note; add no project pair.
6. Create `knowledge/diagnostic-system-design.md` from `knowledge/query-verification-design.md`, then delete the old path: set the H1 to `# Diagnostic System Design`; reword the onboarding parenthetical to the clearance delivery model; split `## Status and purpose` into a core heading `## Purpose` (holding the purpose paragraphs — including the onboarding promise, the destination-storage paragraph, and the identification-packs paragraph) and a project heading `## Status` (holding the status verdict and the deferred list); wrap in the core pair `## Purpose`, core model, portability contract, implemented pilot contract, broader contract, flow, two-team workflow map, intended shared path, register interaction, and verification and evidence constraints; wrap in the project pair `## Status`, refinement backlog, implementation entry criteria, advisory dispositions and audit verdicts, and refinement history.
7. Run every Verify command and report each output verbatim in the phase return.

## Output

- **Artifact:** `knowledge/diagnostic-system-design.md`
- **Schema / shape:** five knowledge files each carrying exactly one ordered core pair, with a project pair only in `agents.md`, `debt.md`, and `knowledge/diagnostic-system-design.md`; the renamed living design's core region carries the `## Purpose` heading with the onboarding-promise, destination-storage, and identification-packs paragraphs; `debt.template.md` and `knowledge/query-verification-design.md` absent.
- **Attribution / identities:** T1; consumed inputs are the five source knowledge files and the approved stories; produced content identities are recorded in the return.
- **Parent handoff:** completed operations, gate evidence (verbatim command outputs), and current resource-use state; author completion is not acceptance.

## Verify commands

| Executor | Command |
|---|---|
| Cipher 🔓 (Lead Orchestrator) | `for f in knowledge/agents.md knowledge/debt.md knowledge/problems.md knowledge/symptoms.md knowledge/diagnostic-system-design.md; do grep -q '^<!-- core:begin -->$' "$f" \|\| exit 1; grep -q '^<!-- core:end -->$' "$f" \|\| exit 1; done` |
| Cipher 🔓 (Lead Orchestrator) | `grep -c '^<!-- project:begin -->$' knowledge/agents.md knowledge/debt.md knowledge/diagnostic-system-design.md knowledge/problems.md knowledge/symptoms.md` |
| Cipher 🔓 (Lead Orchestrator) | `awk '/core:begin/,/core:end/' knowledge/diagnostic-system-design.md \| grep -cE 'Ticket-enabled destinations receive\|Destination chooses storage\|Identification packs\|^## Purpose$'` |
| Cipher 🔓 (Lead Orchestrator) | `test ! -e knowledge/debt.template.md && test ! -e knowledge/query-verification-design.md` |
| Cipher 🔓 (Lead Orchestrator) | `grep -q '### Artifact naming (HARD RULE)' knowledge/agents.md && grep -q '### Bounded-query discipline (SELECT-in-WHERE)' knowledge/agents.md && grep -q '### Register-first identification' knowledge/agents.md && grep -q '### Safe parallel task coordination (HARD RULE)' knowledge/agents.md && grep -q '### Clean architecture (language-agnostic) (HARD RULE)' knowledge/agents.md` |

## Gate

- ⬜ Every Verify command exits as expected and its output is recorded verbatim in the accepted return.
- ⬜ The living design's core region carries the `## Purpose` heading with the onboarding-promise, destination-storage, and identification-packs paragraphs (the pilot's design proof surfaces; the AC4 investigate-step surface resolves at the runbook skill surface), and every heading cited by existing story proofs survives verbatim — `### Bounded-query discipline (SELECT-in-WHERE)` keeps its exact name.
- ⬜ The rename and template deletion leave no reference to the old names under `knowledge/` or `user-stories/`.
- ⬜ This phase ships documentation content: the delivered bytes are reviewed against the approved content division, not against this plan's description of it.
- ⬜ Relevant content and dependencies stayed stable for review, identities and scope are recorded, and the parent accepted the return; relevant changes invalidate affected verdicts before redispatch.

## Abort conditions

- Halt if any cited heading is missing or altered, any marker pair is malformed or duplicated, or a file loses content outside the intended moves — restore from the read inputs and report `BLOCKED` to the parent.
- Halt if a Verify command fails twice with unchanged content (S-07 stop-and-ask) — report the literal output rather than editing around it.
- Stop before any out-of-assignment write or incompatible access; report `BLOCKED` with the exact need, evidence, and bounded options.
