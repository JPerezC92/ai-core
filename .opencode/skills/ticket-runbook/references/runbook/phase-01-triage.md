# Phase 01 — Triage

> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Pre:** Ticket ID available; ticket-read tool authenticated.
> **Reads:** the ticket via the ticket-read tool (get_ticket + get_conversations); `knowledge/agents.md`; the symptom-class catalog (`knowledge/symptoms.md`)
> **Writes:** `runbook/runbook.md` (header initialized); `runbook/phase-01-triage.md` (filled)

## Steps

1. Read the ticket via the ticket-read tool — extract: system/domain, module, country, campaign, symptom summary, any entity identifiers.
2. Match ticket signals against the symptom-class catalog (`knowledge/symptoms.md`) active entries. If a signal match is found, set `Replay-candidate: pending` in the runbook header and record the class reference.
3. Classify the system/domain per `knowledge/agents.md`. For cross-system signals, list all matching systems.
4. Write `runbook/runbook.md` with the initialized header: `Phase: 01`, `SLA-due: <calculated>`, `Updated: <now>`, `Hypotheses-outstanding: 3/3`, `Query-budget: 0/6` (used/limit; `6/6` is exhausted), `Replay-candidate: pending`, `Same-query-reruns: 0/2`.
5. Write `runbook/phase-01-triage.md` completed block: system(s), module, symptom, class match (or "no match"), dispatch list for phase 02.

## Output

- **Artifact:** `runbook/runbook.md` (initialized) + `runbook/phase-01-triage.md` (filled)
- **Schema:** runbook.md header has all 7 fields; phase-01 has system, module, symptom, class-ref or "none", dispatch list.

## Triage results

| Field | Value |
|---|---|
| System | <fill> |
| Module | <fill> |
| Country | <fill> |
| Campaign | <fill> |
| Symptom | <fill> |
| Class match | none / <class-ref> |
| Dispatch list | <agent(s)> |

## Gate

- ⬜ System classified (exactly one or a named list for cross-system)
- ⬜ `runbook.md` header written with all 7 fields populated
- ⬜ Dispatch list names ≥1 domain agent

## Post-phase dispatch (HARD RULE — Cipher direct)

After this phase Gate passes, BEFORE advancing `Phase:` in `runbook.md`, starting the next phase, OR closing the ticket (for Phase 06), Cipher 🔓 (Lead Orchestrator) MUST dispatch Ledger 📒 to sync the ticket record per `.opencode/agents/ledger.md` § Incremental sync per phase. Forbidden: batching multiple phases' Ledger syncs into a single end-of-ticket dispatch.

## Abort conditions

- Ticket-read auth error → run the auth-refresh routine, then retry once. If still failing → halt, report to user.
- System cannot be classified from ticket content → halt; ask user for clarification before phase 02.
