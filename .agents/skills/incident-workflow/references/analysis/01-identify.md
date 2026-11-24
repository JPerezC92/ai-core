# Identify — Ticket <ID>

> **Owner:** Cipher 🔓 (Lead Orchestrator), or the explicitly assigned identify-step writer in a delegated run
> **Pre:** Ticket ID available; ticket-read tool authenticated.
> **Reads:** the ticket via the ticket-read tool; `.aicore/core/knowledge/diagnostics/symptoms.md`; `.aicore/core/knowledge/diagnostics/problems.md`; `incidents/diagnostics/symptoms.md`; `incidents/diagnostics/problems.md`
> **Writes:** `01-identify.md` (filled); `state.md` header (`Phase`, `identification_verdict`, `Updated`)

## Execution ownership and handoff

The default route is direct execution: Cipher 🔓 (Lead Orchestrator) reads the ticket, performs the identification and writes `01-identify.md` and `state.md` itself, then satisfies the Gate below and advances. Reading a ticket through its tool is not a dispatch, and direct execution records no assignment, no acceptance event and no ownership transfer. Ticket-read authentication/refresh is declared session access, not an assumed shared read.

For a delegated run, record workflow/ticket, task/instance, role/responsibility, accepted ticket-read result and register input identities, exact writes/other access, allocated output destinations, gates, continuation/join owner and capacity/accounting owner in existing Markdown or the dispatch. This assigned identify instance alone writes the named working files, and Cipher 🔓 (Lead Orchestrator) owns acceptance and accounting. A recorded assignment procedure neither requires delegation nor authorizes it: the user's authorization for separate work does.

Supporting evidence instances may return bounded attributed results against compatible stable inputs, never verdicts or state/counter changes. Preserve normalize→S-xx→incident P-NNN→discriminators/exclusions→verdict order; archives/backfill remain forbidden until `no_match`. No new analysis files or YAML fields. Before investigation, the identification result, its input/output identities and its gates are recorded and the Gate below is satisfied — by Cipher directly, or by the coordinator accepting a delegated return after observing prior resource-use cessation. Hypotheses/query/rerun allowances are never reset.

## Steps

1. Normalize the ticket: system, module, country, campaign, and the raw symptom/error text.
2. Match the error signature against the shared baseline `.aicore/core/knowledge/diagnostics/symptoms.md` and the project catalog `incidents/diagnostics/symptoms.md`. A class matches only when every **Required signal** is present and no **Exclusion** is present. Record the matching identifier, baseline `S-xx` or project `LOCAL:S-xx` (or "no class match").
3. Filter `incidents/diagnostics/problems.md` to `Team: incident` rows whose `Symptom` references the matched identifier and whose `System` + `Module` align with the ticket. Exclude `Lifecycle: resolved` and `Lifecycle: retired` rows.
4. Evaluate every candidate row's `Discriminators` against the current ticket and disqualify a row when any `Exclusions` condition is present.
5. Issue exactly one verdict — `exact`, `structural`, or `no_match` — and write it to `identification_verdict` in `state.md`:
   - `exact`: exactly one `active` incident `P-NNN` with `Allow_exact: yes` and every discriminator already evidenced in the ticket.
   - `structural`: exactly one `candidate`, `active`, or `mitigated` incident `P-NNN`.
   - `no_match`: no eligible incident `P-NNN` remains. An empty register is valid and yields `no_match` — never halt.
6. If more than one incident `P-NNN` remains eligible, do not choose — record every candidate and return `no_match` with an ambiguity note.
7. Verdict-source restriction: archives, patterns registers, KBA/RCA catalogs, and knowledge search are evidence/backfill only. They never issue a verdict. Consult them only after a `no_match`, and label what they return as evidence.

## Output

- **Artifact:** `01-identify.md` (filled); `state.md` (`Phase: identify`, `identification_verdict`, `Updated`).
- **Schema:** system, module, matched `S-xx`, matched incident `P-NNN` (or "none"), discriminator/exclusion evaluation, verdict (`pending | exact | structural | no_match`), rationale.
- **Handoff:** task/instance, consumed input/output identities, actual counter snapshot, finished supporting results, completed-step validator/gate evidence and current resource-use state. In direct execution the investigate step begins once the Gate below is satisfied; in a delegated run the coordinator accepts this return before assigning the successor.

## Identification results

| Field                    | Value                                   |
| ------------------------ | --------------------------------------- |
| System                   | <SYSTEM>                                |
| Module                   | <fill>                                  |
| Symptom class            | <S-xx> or none                          |
| Matched incident problem | <P-NNN> or none                         |
| Discriminators evaluated | <fill>                                  |
| Exclusions present       | <fill> or none                          |
| Verdict                  | pending / exact / structural / no_match |
| Rationale                | <fill>                                  |

## Gate

- ⬜ System and module classified from the ticket
- ⬜ Symptom class matched against required signals + exclusions, or recorded as "no class match"
- ⬜ Every eligible incident `P-NNN` evaluated for discriminators and exclusions
- ⬜ `identification_verdict` is `exact`, `structural`, or `no_match` (not `pending` when the step closes)
- ⬜ `exact` and `structural` cite the incident `P-NNN`; `no_match` cites none
- ⬜ No archive, pattern, KBA/RCA, or knowledge-search result issued the verdict
- ⬜ Stable inputs and any separately attributed supporting returns accounted for; sole writer and conserved counters confirmed; completed-step validation passes before the header advances

## Abort conditions

- Ticket-read auth error → run the auth-refresh routine, then retry once. If still failing → halt, report to user.
- System cannot be classified from ticket content → halt; ask user for clarification before the investigate step.
- More than one incident `P-NNN` remains eligible after every filter → halt; present the ambiguity to Cipher 🔓 (Lead Orchestrator). Do not pick one.
- Conflicting access, stale inputs, missing capacity or unverified isolation → report `BLOCKED` before that operation; do not infer isolation, expand writes or use the question tool from a delegated run. Direct execution may use the question tool for a genuine user-only decision.
