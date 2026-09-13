# Synthesize — Ticket <ID>

> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Pre:** `02-investigate.md` exists; ≥1 hypothesis has `Confirmed: yes` or all are `inconclusive`; `Phase` is `investigate`.
> **Reads:** `01-identify.md`; `02-investigate.md`; the escalation matrix
> **Writes:** `03-synthesize.md` (filled); updates `state.md` (`Phase`, `Updated`)

## Steps

1. Read the `02-investigate.md` verbatim results. Identify the confirmed hypothesis (or the most-supported inconclusive if no confirmation).
2. State the root cause in ≤3 bullet lines, each labeled `Fact` (direct evidence) or `Hypothesis` (partial evidence + refutation criteria cited).
3. Select the derivation path from the escalation matrix based on system + root-cause type.
4. Identify the response surface: what the visible note must convey — symptom confirmed, root cause (labeled), recommended action, derivation target. ≤15 lines total including the derivation call.
5. Write `03-synthesize.md`: root-cause block (Fact/Hypothesis labeled), derivation decision, response surface.
6. Update `state.md`: `Phase: synthesize`, `Updated: <now>`.

> **Verifier-evidence rule:** a `verified` verdict from the optional investigate-step verifier route is symptom evidence only. It cannot by itself establish root-cause equivalence or authorize a fix. Any root cause it supports must still be labeled `Fact` or `Hypothesis` under Step 2 and meet the same evidence bar as any other hypothesis.

## Output

- **Artifact:** `03-synthesize.md` (filled).
- **Schema:** root-cause block (≤3 bullets, each labeled Fact/Hypothesis), derivation target (named, not TBD), response surface (≤15 lines). A verifier `verified` verdict is symptom evidence only and is never represented as root-cause proof or fix authorization.

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
- ⬜ A verifier `verified` verdict, if present, is treated as symptom evidence only — not as root-cause proof or fix authorization

## Abort conditions

- All `02-investigate.md` verdicts are `inconclusive` AND no partial evidence is sufficient for a labeled hypothesis → halt; Cipher 🔓 (Lead Orchestrator) escalates without a response surface.
- Halt if a verifier verdict would be represented as root-cause proof or a user-authorized fix.
