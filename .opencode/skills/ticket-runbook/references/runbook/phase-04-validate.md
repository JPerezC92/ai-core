# Phase 04 — Validate

> ⚠️ **STOP — Cipher 🔓 (Lead Orchestrator) dispatch only.** This phase Owner is Investigator 🔍 (Incident Investigator) (see `AGENTS.md` § Roster). Cipher 🔓 (Lead Orchestrator) MUST dispatch the Investigator 🔍 (Incident Investigator) — do NOT execute Steps inline.

> **Owner:** Investigator 🔍 (Incident Investigator)
> **Pre:** `runbook/phase-03-hypothesis.md` exists with ≥1 hypothesis; `Query-budget` is `used/limit`, and `N/6` has remaining budget when N < 6.
> **Reads:** `runbook/phase-03-hypothesis.md`; the primary database / document database as appropriate for the system; for the optional verifier route, `.opencode/skills/query-verification/SKILL.md` and `.opencode/skills/query-verification/references/protocol-v1.md`
> **Writes:** `runbook/phase-04-validate.md`; updates `runbook.md` kill-switch counters; optionally writes the redacted case-evidence record under the ticket's session-specific `validations/` folder when the verifier route is used

## Steps

1. Execute ONE query per hypothesis, in H1→H2→H3 order. Before each query: check `Query-budget` — if it is `6/6`, stop and report budget exhausted.
2. After each query: write the result verbatim (exact counts, exact timestamps, exact field values). No paraphrase. Set `Confirmed: yes | no | inconclusive` for each hypothesis.
3. After each same-query re-run (identical query re-executed): increment `Same-query-reruns` counter. If the counter reaches 2, stop re-running; flag in output.
4. Write `runbook/phase-04-validate.md`: one block per hypothesis with Query / Result (verbatim) / Confirmed verdict.
5. Update `runbook.md`: decrement `Hypotheses-outstanding` per confirmed/ruled-out hypothesis; update `Query-budget` as `used/limit`; update `Same-query-reruns`; set `Phase: 04`, `Updated: <now>`.

## Optional verifier route (query-verification pilot)

> Optional and incident-only. The manual per-hypothesis query path in Steps 1–5 is unchanged and remains the default. Use this route only when the hypothesis has an incident-owned verifier sidecar and the destination-owned adapter is available.

1. Validate the verifier before any execution. The core skill never executes SQL:
   `python3 .opencode/skills/query-verification/scripts/query_verification.py validate --query-root ./sql --sidecar ./sql/checks/example-amount.verifier.yaml`
   On non-zero exit, stop — the verifier is rejected and the destination-owned adapter MUST NOT execute it.
2. Hand the validated sidecar to the destination-owned adapter. The adapter binds the declared named parameters, executes the read-only query, and returns normalized JSON. AICore does not execute the query, hold credentials, or invoke the adapter.
3. Evaluate the normalized output locally and write the redacted case evidence:
   `python3 .opencode/skills/query-verification/scripts/query_verification.py evaluate --sidecar ./sql/checks/example-amount.verifier.yaml --adapter-output ./validations/session/adapter-output.json --evidence ./validations/session/example-amount.evidence.json`
4. Record the verifier-evidence block below and update `runbook.md` as in Step 5.

**Query-budget accounting:** exactly one adapter execution consumes exactly one existing Query-budget slot. The `6/6` cap, the `Same-query-reruns` cap of 2, and the normal per-hypothesis query path are unchanged. No new counter, budget, or header field is introduced.

**Non-verifier queries:** any query not run through the verifier route keeps the required verbatim `Query:` / `Result (verbatim)` evidence from Steps 2 and 4.

**Evidence retention:** the redacted case-evidence record is written under the ticket's existing session-specific `validations/` folder with the verifier ID as the filename stem. Credentials, raw adapter output, rendered SQL, rendered parameter values, and unredacted configured identifiers MUST NOT appear in `runbook/phase-04-validate.md`, `runbook.md`, or the ticket record — only the verifier ID, the three-state verdict, the source/definition/evidence digests, and the redacted case-evidence path are recorded.

## Output

- **Artifact:** `runbook/phase-04-validate.md`
- **Schema:** one block per hypothesis — `Query:` (exact SQL/document query), `Result:` (verbatim), `Confirmed: yes|no|inconclusive`. Plus kill-switch status summary at bottom. When the optional verifier route is used, also add a verifier-evidence block (verifier ID, three-state verdict, source/definition/evidence digests, redacted case-evidence path).

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

## Verifier evidence (optional)

> Include this block only when the optional verifier route was used; omit it entirely otherwise. A `verified` verdict is symptom evidence only — it does not establish root-cause equivalence or authorize a fix.

### Verifier evidence
- **Hypothesis:** H1 | H2 | H3
- **Verifier ID:** the validated verifier `id`
- **Verdict:** verified | not_verified | inconclusive
- **Source digest:** the `sha256:` digest of the evaluated source bytes
- **Definition digest:** the `sha256:` digest of the sidecar bytes
- **Evidence digest:** the deterministic `sha256:` digest of the redacted record
- **Redacted case evidence:** the session `validations/` path to the verifier-ID-stemmed `.evidence.json`

## Gate

- ⬜ Each hypothesis has a Confirmed verdict
- ⬜ `Query-budget` in `runbook.md` is used/limit and does not exceed `6/6`
- ⬜ `Same-query-reruns` counter does not exceed 2
- ⬜ All result values are verbatim — no paraphrase, no rounding
- ⬜ If the optional verifier route was used: the verifier-evidence block records the verifier ID, one of the three verdicts, the source/definition/evidence digests, and the redacted case-evidence path
- ⬜ The verifier route consumed exactly one Query-budget slot; the `6/6` cap, `Same-query-reruns`, and the manual per-hypothesis path are unchanged
- ⬜ No credentials, raw adapter output, rendered parameter values, or unredacted configured identifiers appear in the runbook or ticket evidence
- ⬜ A verifier verdict is recorded as symptom evidence only — not as root-cause proof or fix authorization

## Post-phase dispatch — HARD RULE: dispatched directly by Cipher 🔓 (Lead Orchestrator)

After this phase Gate passes, BEFORE advancing `Phase:` in `runbook.md`, starting the next phase, OR closing the ticket (for Phase 06), Cipher 🔓 (Lead Orchestrator) MUST dispatch Ledger 📒 (Record Keeper) to sync the ticket record per `.opencode/agents/ledger.md` § Incremental sync per phase. Forbidden: batching multiple phases' Ledger syncs into a single end-of-ticket dispatch.

## Abort conditions

- `Query-budget` reaches `6/6` with no confirmed hypothesis → halt; return to Cipher 🔓 (Lead Orchestrator) with a budget-exhausted signal. Cipher 🔓 (Lead Orchestrator) decides whether to request an exception or escalate.
- `Same-query-reruns` reaches 2 → cease re-running; report to Cipher 🔓 (Lead Orchestrator).
- Halt if the optional verifier route would require a runbook-header schema change, a query-budget increase, ticket data migration, or automatic query execution.
- Halt if a verifier verdict would be represented as root-cause proof or a user-authorized fix.
