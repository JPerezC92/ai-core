# Phase 04 — Validate

> ⚠️ **STOP — Cipher dispatch only.** This phase Owner is the Investigator (see `AGENTS.md` § Roster). Cipher 🔓 (Lead Orchestrator) MUST dispatch the Investigator — do NOT execute Steps inline.

> **Owner:** Investigator
> **Pre:** `runbook/phase-03-hypothesis.md` exists with ≥1 hypothesis; `Query-budget` is `used/limit`, and `N/6` has remaining budget when N < 6.
> **Reads:** `runbook/phase-03-hypothesis.md`; the primary database / document database as appropriate for the system
> **Writes:** `runbook/phase-04-validate.md`; updates `runbook.md` kill-switch counters

## Steps

1. Execute ONE query per hypothesis, in H1→H2→H3 order. Before each query: check `Query-budget` — if it is `6/6`, stop and report budget exhausted.
2. After each query: write the result verbatim (exact counts, exact timestamps, exact field values). No paraphrase. Set `Confirmed: yes | no | inconclusive` for each hypothesis.
3. After each same-query re-run (identical query re-executed): increment `Same-query-reruns` counter. If the counter reaches 2, stop re-running; flag in output.
4. Write `runbook/phase-04-validate.md`: one block per hypothesis with Query / Result (verbatim) / Confirmed verdict.
5. Update `runbook.md`: decrement `Hypotheses-outstanding` per confirmed/ruled-out hypothesis; update `Query-budget` as `used/limit`; update `Same-query-reruns`; set `Phase: 04`, `Updated: <now>`.

## Output

- **Artifact:** `runbook/phase-04-validate.md`
- **Schema:** one block per hypothesis — `Query:` (exact SQL/document query), `Result:` (verbatim), `Confirmed: yes|no|inconclusive`. Plus kill-switch status summary at bottom.

## Validation results

### H1 — <title>
- **Query:** `<exact query>`
- **Result (verbatim):** <exact counts, timestamps, field values>
- **Confirmed:** yes / no / inconclusive

### H2 — <title>
- **Query:** `<exact query>`
- **Result (verbatim):** <exact counts, timestamps, field values>
- **Confirmed:** yes / no / inconclusive

### H3 — <title>
- **Query:** `<exact query>`
- **Result (verbatim):** <exact counts, timestamps, field values>
- **Confirmed:** yes / no / inconclusive

## Kill-switch summary

| Kill-switch | Budget | Consumed | Status |
|---|---|---|---|
| Query-budget (used/limit) | 6 | <N used> | <ok / exhausted> |
| Same-query-reruns | 2 | <N> | <ok / limit reached> |
| Hypotheses-outstanding | 3 | <N confirmed/ruled out> | <N remaining> |

## Gate

- ⬜ Each hypothesis has a Confirmed verdict
- ⬜ `Query-budget` in `runbook.md` is used/limit and does not exceed `6/6`
- ⬜ `Same-query-reruns` counter does not exceed 2
- ⬜ All result values are verbatim — no paraphrase, no rounding

## Post-phase dispatch (HARD RULE — Cipher direct)

After this phase Gate passes, BEFORE advancing `Phase:` in `runbook.md`, starting the next phase, OR closing the ticket (for Phase 06), Cipher 🔓 (Lead Orchestrator) MUST dispatch Ledger 📒 to sync the ticket record per `.opencode/agents/ledger.md` § Incremental sync per phase. Forbidden: batching multiple phases' Ledger syncs into a single end-of-ticket dispatch.

## Abort conditions

- `Query-budget` reaches `6/6` with no confirmed hypothesis → halt; return to Cipher with a budget-exhausted signal. Cipher decides whether to request an exception or escalate.
- `Same-query-reruns` reaches 2 → cease re-running; report to Cipher.
