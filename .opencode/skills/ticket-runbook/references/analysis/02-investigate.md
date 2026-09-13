# Investigate — Ticket <ID>

> ⚠️ **STOP — Cipher 🔓 (Lead Orchestrator) dispatch only.** This step Owner is Investigator 🔍 (Incident Investigator) (see `AGENTS.md` § Roster). Cipher 🔓 (Lead Orchestrator) MUST dispatch the Investigator — do NOT execute Steps inline.

> **Owner:** Investigator 🔍 (Incident Investigator)
> **Pre:** `01-identify.md` exists with a non-`pending` `identification_verdict`; `Phase` is `identify`.
> **Reads:** `01-identify.md`; `state.md`; the ticket; `knowledge/problems.md` (the cited `P-NNN` row, if any); for the optional verifier route, `.opencode/skills/query-verification/SKILL.md` and `.opencode/skills/query-verification/references/protocol-v1.md`
> **Writes:** `02-investigate.md` (filled); updates `state.md` (`Phase`, kill-switch counters, `Updated`); optionally writes the redacted case-evidence record under the ticket's session-specific `validations/` folder

## Steps

1. Branch on `identification_verdict`:
   - `exact` — record the cited `P-NNN`, restate its evidenced discriminators, and confirm the recorded root cause and fix still apply to the current ticket. No fresh hypothesis framing.
   - `structural` — restate the one inherited hypothesis from the cited `P-NNN` and validate it against the current ticket with adapted queries.
   - `no_match` — frame ≤3 evidence-backed hypotheses (H1 most likely). Each hypothesis MUST have: statement, partial evidence, refutation criteria, and a proposed validation query. Do not suggest skills by name.
2. Execute ONE query per hypothesis, in H1→H2→H3 order. Before each query: check `Query-budget` — if it is `6/6`, stop and report budget exhausted.
3. After each query: write the result verbatim (exact counts, exact timestamps, exact field values). No paraphrase. Set `Confirmed: yes | no | inconclusive` for each hypothesis.
4. After each same-query re-run (identical query re-executed): increment `Same-query-reruns`. If it reaches 2, stop re-running; flag in output.
5. Write `02-investigate.md`: one block per hypothesis with Query / Result (verbatim) / Confirmed.
6. Update `state.md`: decrement `Hypotheses-outstanding` per resolved hypothesis; update `Query-budget` as `used/limit`; update `Same-query-reruns`; set `Phase: investigate`, `Updated: <now>`.

## Optional verifier route (query-verification pilot)

> Optional and incident-only. The manual per-hypothesis query path in Steps 1–6 is unchanged and remains the default. Use this route only when the hypothesis has an incident-owned verifier sidecar and the destination-owned adapter is available.

1. Validate the verifier before any execution. The core skill never executes SQL:
   `python3 .opencode/skills/query-verification/scripts/query_verification.py validate --query-root ./sql --sidecar ./sql/checks/example-amount.verifier.yaml`
   On non-zero exit, stop — the verifier is rejected and the destination-owned adapter MUST NOT execute it.
2. Hand the validated sidecar to the destination-owned adapter. The adapter binds the declared named parameters, executes the read-only query, and returns normalized JSON. AICore does not execute the query, hold credentials, or invoke the adapter.
3. Evaluate the normalized output locally and write the redacted case evidence:
   `python3 .opencode/skills/query-verification/scripts/query_verification.py evaluate --sidecar ./sql/checks/example-amount.verifier.yaml --adapter-output ./validations/session/adapter-output.json --evidence ./validations/session/example-amount.evidence.json`
4. Record the verifier-evidence block below and update `state.md` as in Step 6.

**Query-budget accounting:** exactly one adapter execution consumes exactly one existing Query-budget slot. The `6/6` cap, the `Same-query-reruns` cap of 2, and the normal per-hypothesis query path are unchanged. No new counter, budget, or header field is introduced.

**Non-verifier queries:** any query not run through the verifier route keeps the required verbatim `Query:` / `Result (verbatim)` evidence from Steps 2 and 4.

**Evidence retention:** the redacted case-evidence record is written under the ticket's existing session-specific `validations/` folder with the verifier ID as the filename stem. Credentials, raw adapter output, rendered SQL, rendered parameter values, and unredacted configured identifiers MUST NOT appear in `02-investigate.md`, `state.md`, or the ticket record — only the verifier ID, the three-state verdict, the source/definition/evidence digests, and the redacted case-evidence path are recorded.

## Output

- **Artifact:** `02-investigate.md` (filled).
- **Schema:** one block per hypothesis — `Query:` (exact SQL/document query), `Result:` (verbatim), `Confirmed: yes|no|inconclusive`. Plus kill-switch status summary at bottom. When the optional verifier route is used, also add a verifier-evidence block (verifier ID, three-state verdict, source/definition/evidence digests, redacted case-evidence path).

## Investigation results

### H1 — <title>
- **Statement:** The problem could be <X>
- **Partial evidence:** <what supports this>
- **Refutation criteria:** <what single result would rule it out>
- **Query:** `<exact query>`
- **Result (verbatim):** <exact counts, timestamps, field values>
- **Confirmed:** yes / no / inconclusive

### H2 — <title>
- **Statement:** The problem could be <X>
- **Partial evidence:** <what supports this>
- **Refutation criteria:** <what single result would rule it out>
- **Query:** `<exact query>`
- **Result (verbatim):** <exact counts, timestamps, field values>
- **Confirmed:** yes / no / inconclusive

### H3 — <title>
- **Statement:** The problem could be <X>
- **Partial evidence:** <what supports this>
- **Refutation criteria:** <what single result would rule it out>
- **Query:** `<exact query>`
- **Result (verbatim):** <exact counts, timestamps, field values>
- **Confirmed:** yes / no / inconclusive

## Kill-switch summary

| Kill-switch | Budget | Consumed | Status |
|---|---|---|---|
| Query-budget (used/limit) | 6 | <fill> | <ok / exhausted> |
| Same-query-reruns | 2 | <fill> | <ok / limit reached> |
| Hypotheses-outstanding | 3 | <fill> | <fill> remaining |

## Verifier evidence (optional)

> Include this block only when the optional verifier route was used; omit it entirely otherwise. A `verified` verdict is symptom evidence only — it does not establish root-cause equivalence or authorize a fix.

- **Hypothesis:** H1 | H2 | H3
- **Verifier ID:** the validated verifier `id`
- **Verdict:** verified | not_verified | inconclusive
- **Source digest:** the `sha256:` digest of the evaluated source bytes
- **Definition digest:** the `sha256:` digest of the sidecar bytes
- **Evidence digest:** the deterministic `sha256:` digest of the redacted record
- **Redacted case evidence:** the session `validations/` path to the verifier-ID-stemmed `.evidence.json`

## Gate

- ⬜ `exact` and `structural` cite the `P-NNN` inherited from `01-identify.md`; `no_match` frames ≤3 hypotheses
- ⬜ Each hypothesis has a Confirmed verdict
- ⬜ `Query-budget` in `state.md` is used/limit and does not exceed `6/6`
- ⬜ `Same-query-reruns` counter does not exceed 2
- ⬜ All result values are verbatim — no paraphrase, no rounding
- ⬜ If the optional verifier route was used: the verifier-evidence block records the verifier ID, one of the three verdicts, the source/definition/evidence digests, and the redacted case-evidence path
- ⬜ The verifier route consumed exactly one Query-budget slot; the `6/6` cap, `Same-query-reruns`, and the manual per-hypothesis path are unchanged
- ⬜ A verifier verdict is recorded as symptom evidence only — not as root-cause proof or fix authorization

## Abort conditions

- `Query-budget` reaches `6/6` with no confirmed hypothesis → halt; return to Cipher 🔓 (Lead Orchestrator) with a budget-exhausted signal.
- `Same-query-reruns` reaches 2 → cease re-running; report to Cipher 🔓 (Lead Orchestrator).
- Cannot frame even one evidence-backed hypothesis → halt with an "insufficient data" finding. Do not invent hypotheses.
- Halt if the optional verifier route would require a state-header schema change, a query-budget increase, ticket data migration, or automatic query execution.
- Halt if a verifier verdict would be represented as root-cause proof or a user-authorized fix.
