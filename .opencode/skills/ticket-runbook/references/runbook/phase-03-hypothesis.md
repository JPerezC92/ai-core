# Phase 03 — Hypothesis

> ⚠️ **STOP — Cipher dispatch only.** This phase Owner is the Investigator (see `AGENTS.md` § Roster). Cipher 🔓 (L2 Lead) MUST dispatch the Investigator — do NOT execute Steps inline.

> **Owner:** Investigator
> **Pre:** `Replay-candidate: no` confirmed in `runbook.md`; `phase-02-priorart.md` exists.
> **Reads:** `runbook/phase-01-triage.md`; `runbook/phase-02-priorart.md`; ticket description (already read in phase 01 — use from triage notes, do not re-read the ticket)
> **Writes:** `runbook/phase-03-hypothesis.md`

## Steps

1. From the phase-01 symptom + phase-02 no-match, frame ≤3 hypotheses. Each hypothesis MUST have:
   - Statement: what the problem could be
   - Partial evidence: what from the ticket/prior-art supports this hypothesis
   - Refutation criteria: what single query result would rule it out
   - Proposed validation query: table/collection + filter (no actual query execution here)
2. Rank hypotheses H1 (most likely) → H2 → H3 based on evidence weight.
3. Do NOT suggest skills by name. Do NOT propose more than 3 hypotheses.
4. Write `runbook/phase-03-hypothesis.md` with the ranked list.
5. Update `runbook.md`: `Hypotheses-outstanding: 3/3`, `Phase: 03`, `Updated: <now>`.

## Output

- **Artifact:** `runbook/phase-03-hypothesis.md`
- **Schema:** H1/H2/H3 blocks, each with Statement / Partial evidence / Refutation criteria / Proposed validation query. No TBD blocks.

## Hypotheses

### H1 — <title>
- **Statement:** The problem could be <X>
- **Partial evidence:** <what supports this>
- **Refutation criteria:** <what single result would rule it out>
- **Proposed validation:** table/collection `<name>` where `<filter>`

### H2 — <title>
- **Statement:** The problem could be <X>
- **Partial evidence:** <what supports this>
- **Refutation criteria:** <what single result would rule it out>
- **Proposed validation:** table/collection `<name>` where `<filter>`

### H3 — <title>
- **Statement:** The problem could be <X>
- **Partial evidence:** <what supports this>
- **Refutation criteria:** <what single result would rule it out>
- **Proposed validation:** table/collection `<name>` where `<filter>`

## Gate

- ⬜ ≤3 hypotheses present
- ⬜ Each hypothesis has all 4 sub-fields (Statement, Partial evidence, Refutation criteria, Proposed validation)
- ⬜ No skill names appear in the hypothesis list
- ⬜ `Hypotheses-outstanding` in `runbook.md` is updated

## Post-phase dispatch (HARD RULE — Cipher direct)

After this phase Gate passes, BEFORE advancing `Phase:` in `runbook.md`, starting the next phase, OR closing the ticket (for Phase 06), Cipher 🔓 (L2 Lead) MUST dispatch Ledger 📒 to sync the ticket record per `.opencode/agents/ledger.md` § Incremental sync per phase. Forbidden: batching multiple phases' Ledger syncs into a single end-of-ticket dispatch.

## Abort conditions

- Cannot frame even 1 evidence-backed hypothesis from ticket content → halt; return to Cipher with an "insufficient ticket data" finding. Do not invent hypotheses.
