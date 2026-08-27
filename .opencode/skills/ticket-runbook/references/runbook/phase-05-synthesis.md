# Phase 05 — Synthesis

> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Pre:** `runbook/phase-04-validate.md` exists; ≥1 hypothesis has `Confirmed: yes` or all are `inconclusive`.
> **Reads:** `runbook/phase-01-triage.md`; `runbook/phase-04-validate.md`; the escalation matrix
> **Writes:** `runbook/phase-05-synthesis.md`; updates `runbook.md` `Phase`

## Steps

1. Read the phase-04 verbatim results. Identify the confirmed hypothesis (or the most-supported inconclusive if no confirmation).
2. State the root cause in ≤3 bullet lines, each labeled `Fact` (direct evidence) or `Hypothesis` (partial evidence + refutation criteria cited).
3. Select the derivation path from the escalation matrix based on system + root-cause type.
4. Identify the response surface: what the visible note must convey — symptom confirmed, root cause (labeled), recommended action, derivation target. ≤15 lines total including the derivation call.
5. Write `runbook/phase-05-synthesis.md`: root-cause block (Fact/Hypothesis labeled), derivation decision, response surface.
6. Update `runbook.md`: `Phase: 05`, `Updated: <now>`.

## Output

- **Artifact:** `runbook/phase-05-synthesis.md`
- **Schema:** root-cause block (≤3 bullets, each labeled Fact/Hypothesis), derivation target (named, not TBD), response surface (≤15 lines).

## Root cause

- **[Fact/Hypothesis]:** <root cause bullet 1>
- **[Fact/Hypothesis]:** <root cause bullet 2 — if needed>
- **[Fact/Hypothesis]:** <root cause bullet 3 — if needed>

## Derivation decision

- **Target:** <named from the escalation matrix>
- **Target team:** <team>
- **Rationale:** <one line from the escalation matrix>

## Response surface (≤15 lines)

<what the visible note must convey — symptom, root cause labeled, action, derivation target>

## Gate

- ⬜ Root-cause bullets present and labeled Fact or Hypothesis
- ⬜ Derivation target named (not "TBD")
- ⬜ Response surface ≤15 lines

## Post-phase dispatch (HARD RULE — Cipher direct)

After this phase Gate passes, BEFORE advancing `Phase:` in `runbook.md`, starting the next phase, OR closing the ticket (for Phase 06), Cipher 🔓 (Lead Orchestrator) MUST dispatch Ledger 📒 to sync the ticket record per `.opencode/agents/ledger.md` § Incremental sync per phase. Forbidden: batching multiple phases' Ledger syncs into a single end-of-ticket dispatch.

## Abort conditions

- All phase-04 verdicts are `inconclusive` AND no partial evidence is sufficient for a labeled hypothesis → halt; Cipher escalates without a response surface.
