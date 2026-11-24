# Investigate — Ticket <ID>

> **Execution model:** by default Cipher 🔓 (Lead Orchestrator) executes this step directly and is not gated on an assignment. When separate work was explicitly authorized, the step runs under that instance's assignment; a recorded assignment procedure never authorizes delegation by itself.

> **Owner:** Cipher 🔓 (Lead Orchestrator), or the explicitly assigned investigate-step writer in a delegated run
> **Pre:** `01-identify.md` exists with a non-`pending` `identification_verdict`; `Phase` is `identify`; the identify step's Gate is satisfied and its header advanced. In a delegated run, additionally: identification's current input/output identities and gates accepted, prior resource-use cessation observed, and this investigate instance explicitly assigned.
> **Reads:** `01-identify.md`; `state.md`; the ticket; `incidents/diagnostics/problems.md` (the cited `P-NNN` row, if any)
> **Writes:** `02-investigate.md` (filled); updates `state.md` (`Phase`, kill-switch counters, `Updated`)

## Execution ownership and handoff

The default route is direct execution: Cipher 🔓 (Lead Orchestrator) frames the hypotheses, executes the queries, writes `02-investigate.md` and maintains `state.md` and its counters itself, then satisfies the Gate below and advances. Calling a query tool, adapter or MCP is not a dispatch, and direct execution creates no assignment, no acceptance event and no ownership transfer.

For a delegated run, record workflow/ticket, task/instance, role/responsibility, accepted predecessor/input identities, exact writes/other access, allocated destinations, required gates, continuation/join owner and capacity/accounting owner in existing Markdown or the dispatch. This assigned investigate instance alone writes state/counters and its step artifact, and Cipher 🔓 (Lead Orchestrator) owns authoritative incident accounting. Durable retention writes require their own exact assignment or an accepted handoff to their authorized writer; this template's retention obligation is not an implicit write grant.

Supporting instances return bounded, separately attributed evidence on frozen compatible inputs; they never write state/counters, frame competing hypotheses or execute incident queries. One incident hypothesis allowance and one Query-budget remain shared, not cloned per instance. Allocate inbound `downloads/` and response `screenshots/response-N/` as distinct destinations before work, plus other report/evidence paths; a fixed canonical path stays exclusively owned/serialized. Declare adapter, browser/auth-session and external capacity access separately; unknown isolation/capacity blocks that operation. Preserve stored pack precedence and H1→H2→H3 order even when supporting evidence reads run concurrently.

Accept current relevant supporting results before consuming them. Stale, incomplete or still-mutating results cannot unblock synthesis. In a delegated run the coordinator accepts the join and explicitly transfers ownership after prior access ceases; a completed return or old timestamp is not cessation proof, and no transfer resets budgets. Direct execution has no join to accept: Cipher records the evidence it obtained and continues under the same single budget.

## Steps

1. Branch on `identification_verdict`:
   - `exact` — record the cited `P-NNN`, restate its evidenced discriminators, and confirm the recorded root cause and fix still apply to the current ticket. No fresh hypothesis framing.
   - `structural` — restate the one inherited hypothesis from the cited `P-NNN`. If the row's Evidence carries a `pack:` pointer, resolve that destination-relative pack path FIRST: read the pack with destination tools and replay that correlation with current-ticket keys under destination-owned execution (the core never executes or parses the pack internals). Only then frame a new query — and only if the pack replay is rejected, inapplicable, or inconclusive. If the row has no pack pointer, validate the hypothesis with adapted queries as before.
   - `no_match` — frame ≤3 evidence-backed hypotheses (H1 most likely). Each hypothesis MUST have: statement, partial evidence, refutation criteria, and a proposed validation query. Do not suggest skills by name.
2. Execute one query for the current hypothesis, preserving H1→H2→H3 order and the existing hypothesis, Query-budget and same-query-rerun allowances. Before that query: check `Query-budget` — if used equals the current limit, stop and report budget exhausted (default limit 6; halt-and-ask unless the user already raised the denominator). When a result rejects the hypothesis, record the rejection; evaluate it and proceed to the next permitted hypothesis only when the existing order, evidence bar, allowances and stop conditions are satisfied. A delegated run returns the rejection to its coordinator instead of continuing on its own.
3. After each query: write the result verbatim (exact counts, exact timestamps, exact field values). No paraphrase. Set `Confirmed: yes | no | inconclusive` for each hypothesis.
4. After each same-query re-run (identical query re-executed): increment `Same-query-reruns`. If it reaches 2, stop re-running; flag in output.
5. Write `02-investigate.md`: one block per hypothesis with Query / Result (verbatim) / Confirmed.
6. As sole writer, update `state.md` from actual consumption: decrement `Hypotheses-outstanding` per resolved hypothesis; update `Query-budget` as `used/limit`; update `Same-query-reruns`. Record each executed query's consumption once, even when its result is inconclusive; do not invent consumption for unexecuted work. A delegated instance that owns `state.md` gains no shell command from that ownership: it returns the written state so the coordinator runs the analysis-directory validation and, after record edits, the ticket-record validation. Direct execution runs both validations itself under its existing authority. Defer `Phase: investigate`, `Updated: <now>` until Step 7 and the step gates are complete and the applicable validation passes.
7. **Retention (before any collapse):** Every executed query block — manual `Query:` blocks and pack-replay evidence alike — must be preserved verbatim in the durable ticket record: copy each block into `ticket_<ID>.md` (Analysis section) or a cited artifact under `validations/` before close-out collapse deletes this file. Non-image case-evidence artifacts are written under the ticket's session `validations/` folder — never the ticket root — and before close-out every artifact under `validations/` must be durably cited in `ticket_<ID>.md` or intentionally uncited with an evidenced reason; no artifact is deleted to satisfy readiness. Collapse is the deletion step; the durable copy is the retention mechanism. A reusable `pack:` pointer is an extra durable pointer, not a substitute for verbatim ticket retention: every executed query block from the pack replay still copies into `ticket_<ID>.md` or a cited `validations/` artifact. Retention writes need their own authorization in a delegated run; in direct execution Cipher performs them within the ticket's existing authorized scope.

## Output

- **Artifact:** `02-investigate.md` (filled).
- **Schema:** one block per hypothesis — `Query:` (exact SQL/document query), `Result:` (verbatim), `Confirmed: yes|no|inconclusive`. Plus kill-switch status summary at bottom.
- **Handoff:** task/instance, accepted inputs and stable output identities, separately attributed supporting results, actual shared counter values, retention destinations/writer acceptance, validator/gate evidence and resource-use status. In direct execution synthesis begins once the Gate below is satisfied; in a delegated run the coordinator accepts this return before assigning synthesis.

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

| Kill-switch               | Budget | Consumed | Status               |
| ------------------------- | ------ | -------- | -------------------- |
| Query-budget (used/limit) | 6      | <fill>   | <ok / exhausted>     |
| Same-query-reruns         | 2      | <fill>   | <ok / limit reached> |
| Hypotheses-outstanding    | 3      | <fill>   | <fill> remaining     |

## Gate

- ⬜ `exact` and `structural` cite the `P-NNN` inherited from `01-identify.md`; `no_match` frames ≤3 hypotheses
- ⬜ Each hypothesis has a Confirmed verdict
- ⬜ `Query-budget` in `state.md` is used/limit and used is less than or equal to the current limit (default 6)
- ⬜ `Same-query-reruns` counter does not exceed 2
- ⬜ All result values are verbatim — no paraphrase, no rounding
- ⬜ Every executed query block has a durable verbatim copy in `ticket_<ID>.md` or a cited `validations/` artifact
- ⬜ One authorized state/counter writer and one conserved allowance; actual consumption recorded once; no duplicate allowance or concurrent query/hypothesis authority
- ⬜ Current relevant outputs and gates satisfied — Cipher's own in direct execution, the coordinator's acceptance in a delegated run — and, in a delegated run, prior access cessation observed before the writer transfer; reports, inbound `downloads/`, response `screenshots/response-N/`, validation files and external sessions keep compatible allocated ownership

## Abort conditions

- `Query-budget` used equals the current limit with no confirmed hypothesis → halt-and-ask unless the user already raised the denominator; in a delegated run, return a budget-exhausted signal to Cipher 🔓 (Lead Orchestrator).
- `Same-query-reruns` reaches 2 → cease re-running; report the limit to Cipher 🔓 (Lead Orchestrator).
- Cannot frame even one evidence-backed hypothesis → halt with an "insufficient data" finding. Do not invent hypotheses.
- Conflicting resources, stale inputs/results, unknown external capacity or missing handoff evidence → report `BLOCKED` before the affected operation; no scope expansion, and no question-tool call from a delegated run.
