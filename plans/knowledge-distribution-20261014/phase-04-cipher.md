# Phase 4 — Story record convergence

> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Pre:** T1–T3 returns accepted; the combined candidate is stable at the join; the completion evidence matrix is being assembled; the anchor lifecycle is known (release identity created only by separately authorized release work).
> **Reads:** `user-stories/core-sync.md`; `user-stories/diagnostic-system.md`; `user-stories/incident-query-verification-pilot.md`; `user-stories/index.md`; `plans/knowledge-distribution-20261014/plan.md`; the delivered `knowledge/`, registry, and README state
> **Writes:** `user-stories/core-sync.md`; `user-stories/diagnostic-system.md`; `user-stories/incident-query-verification-pilot.md`

## Assignment and resources

- Workflow / task / instance: `knowledge-distribution-20261014` / T4 / Cipher 🔓 (Lead Orchestrator) — story record convergence (coordinator-owned completion work, matching the `safe-roster-parallelism-20261013` convergence precedent).
- Accepted predecessors / input identities: T1, T2, and T3 accepted returns with their gate evidence and recorded content identities.
- Permitted resource access: read the story files, index, plan, and delivered state; write exactly the three `**Writes:**` story files; no git state mutation; no writes under `knowledge/`, `distribution-clearance*`, `.opencode/skills/`, or `README.md`.
- Ownership / output destination: exclusive writer of the three story files; output is the story record state reported into the completion evidence.
- Required gates / continuation / join owner: the completion audit (completion-time, distinct from the planning audit) and acceptance-criterion reconciliation; this phase is itself the coordinator's work.
- Capacity allocation / accounting owner: Cipher 🔓 (Lead Orchestrator) shared ledger.
- Readiness / serialization evidence: serializes after T3 on a real dependency — delivery history is recorded only for accepted delivered behaviour, and the final stale-name sweep runs after these entries land.

## Steps

1. Reconcile the committed criteria against delivered evidence: `core-sync` AC10, AC11, AC16, AC19, AC20; `diagnostic-system` AC6, AC7; `incident-query-verification-pilot` AC5. Establish each through its `## Proof` surface; leave unselected commitments untouched. Also correct `user-stories/diagnostic-system.md` AC4's `## Proof` citation to the real heading `### Bounded-query discipline (SELECT-in-WHERE)` — proof-only, the invented `### Query safeguards` name is not evidence, and the contract text is untouched. Then apply the approved contract correction (user 2026-10-14): reword `core-sync` AC19 to "**Core table:** A cleared markdown source's tables live in its core region and ship with it byte-for-byte like the rest of the core; records the source keeps are project-region content and never ship." and reword AC20's "declare their distribution class" to "carry a documented distribution class"; set both back to `⬜` and re-establish them through their `## Proof` surfaces once T1's block move and T2's declaration removal land.
2. Draft one dated `## Change log` entry per touched story with label `knowledge-distribution-20261014` and a real anchor (the delivering commit SHA, PR number, or ticket): for `core-sync`, the five knowledge region rows with documented distribution classes, the knowledge splits, and the living-design rename; for `diagnostic-system`, the delivered living-design companion; for `incident-query-verification-pilot`, one combined entry naming both the approved 2026-10-14 revision (the AC5 reword and the AC4/AC5/AC7 proof-surface corrections) and the delivered clearance row — keeping the pilot within the five-entry bound by dropping the oldest entry (`2026-09-15 — ticket-runbook-register-admission-20260914 (PR #38)`) into the rollup line `before 2026-09-16 — earlier history: see git history for this file`. Entry text describes the rename without restating the retired names, so the stale-name sweep stays clean.
3. Write the entries only when the anchor exists and resolves (delivery-match rule). If no real anchor exists yet, return the exact remaining blocker — the required entry text and the absent anchor — and retain the plan; never invent an anchor and never write a temporal `plans/` or `output/` path as one.
4. Re-run the stale-name sweep over every non-temporal surface and verify per story that the entry is present, anchored, and within the bounded change-log limit; report the verbatim outputs.

## Output

- **Artifact:** `user-stories/incident-query-verification-pilot.md`
- **Schema / shape:** each touched story carries exactly one new dated entry for this delivery with a resolvable anchor (or the exact recorded anchor blocker), the pilot within the five-entry bound, and reconciled criteria established through their `## Proof` surfaces; the stale-name sweep clean.
- **Attribution / identities:** T4; consumed inputs are the accepted T1–T3 states and the three story files at their read identities; produced content identities recorded in the return.
- **Parent handoff:** reconciliation results, entry text or the exact anchor blocker, and current resource-use state; author completion is not acceptance.

## Verify commands

| Executor | Command |
|---|---|
| Cipher 🔓 (Lead Orchestrator) | `grep -c 'knowledge-distribution-20261014' user-stories/core-sync.md user-stories/diagnostic-system.md user-stories/incident-query-verification-pilot.md` |
| Cipher 🔓 (Lead Orchestrator) | `awk '/## Change log/,0' user-stories/incident-query-verification-pilot.md \| grep -c '^-'` |
| Cipher 🔓 (Lead Orchestrator) | `! grep -rnI -e 'query-verification-design' -e 'debt\.template' --exclude-dir=plans --exclude-dir=output --exclude-dir=.git --exclude-dir=.venv --exclude-dir=__pycache__ .` |

## Gate

- ⬜ Each committed criterion is evidence-established through its `## Proof` surface, and unselected commitments remain untouched.
- ⬜ Each touched story carries one dated entry with a real resolvable anchor, or the exact anchor blocker is returned with the plan retained and archival blocked — never an invented anchor.
- ⬜ The pilot's change log holds six lines after the drop-oldest/rollup action — five dated entries plus one rollup line.
- ⬜ The final stale-name sweep exits 0 over every non-temporal surface after the entries land.
- ⬜ The completion audit (distinct from the planning audit) and the criterion reconciliation complete on the final candidate before `## Outcome`.
- ⬜ Relevant content and dependencies stayed stable for review, identities and scope are recorded; relevant changes invalidate affected verdicts before redispatch.

## Abort conditions

- Halt on an invented or unresolvable anchor, a silent story-contract change, a change-log bound violation, or a false checkbox — report `BLOCKED` with the evidence.
- Halt if a committed criterion lacks evidence or a `## Constraints` entry would be violated — completion stays blocked until resolved or the criterion is removed with a dated record.
- Stop before any out-of-assignment write or incompatible access; report `BLOCKED` with the exact need, evidence, and bounded options.
