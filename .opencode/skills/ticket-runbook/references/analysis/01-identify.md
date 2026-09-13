# Identify — Ticket <ID>

> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Pre:** Ticket ID available; ticket-read tool authenticated.
> **Reads:** the ticket via the ticket-read tool; `knowledge/symptoms.md`; `knowledge/problems.md`
> **Writes:** `01-identify.md` (filled); `state.md` header (`Phase`, `identification_verdict`, `Updated`)

## Steps

1. Normalize the ticket: system, module, country, campaign, and the raw symptom/error text.
2. Match the error signature against `knowledge/symptoms.md`. A class matches only when every **Required signal** is present and no **Exclusion** is present. Record the matching `S-xx` (or "no class match").
3. Filter `knowledge/problems.md` to `Team: incident` rows whose `Symptom` references the matched `S-xx` and whose `System` + `Module` align with the ticket. Exclude `Lifecycle: resolved` and `Lifecycle: retired` rows.
4. Evaluate every candidate row's `Discriminators` against the current ticket and disqualify a row when any `Exclusions` condition is present.
5. Issue exactly one verdict — `exact`, `structural`, or `no_match` — and write it to `identification_verdict` in `state.md`:
   - `exact`: exactly one `active` incident `P-NNN` with `Allow_exact: yes` and every discriminator already evidenced in the ticket.
   - `structural`: exactly one `candidate` or `active` incident `P-NNN`.
   - `no_match`: no eligible incident `P-NNN` remains. An empty register is valid and yields `no_match` — never halt.
6. If more than one incident `P-NNN` remains eligible, do not choose — record every candidate and return `no_match` with an ambiguity note.
7. Verdict-source restriction: archives, patterns registers, KBA/RCA catalogs, and knowledge search are evidence/backfill only. They never issue a verdict. Consult them only after a `no_match`, and label what they return as evidence.

## Output

- **Artifact:** `01-identify.md` (filled); `state.md` (`Phase: identify`, `identification_verdict`, `Updated`).
- **Schema:** system, module, matched `S-xx`, matched incident `P-NNN` (or "none"), discriminator/exclusion evaluation, verdict (`pending | exact | structural | no_match`), rationale.

## Identification results

| Field | Value |
|---|---|
| System | <SYSTEM> |
| Module | <fill> |
| Symptom class | <S-xx> or none |
| Matched incident problem | <P-NNN> or none |
| Discriminators evaluated | <fill> |
| Exclusions present | <fill> or none |
| Verdict | pending / exact / structural / no_match |
| Rationale | <fill> |

## Gate

- ⬜ System and module classified from the ticket
- ⬜ Symptom class matched against required signals + exclusions, or recorded as "no class match"
- ⬜ Every eligible incident `P-NNN` evaluated for discriminators and exclusions
- ⬜ `identification_verdict` is `exact`, `structural`, or `no_match` (not `pending` when the step closes)
- ⬜ `exact` and `structural` cite the incident `P-NNN`; `no_match` cites none
- ⬜ No archive, pattern, KBA/RCA, or knowledge-search result issued the verdict

## Abort conditions

- Ticket-read auth error → run the auth-refresh routine, then retry once. If still failing → halt, report to user.
- System cannot be classified from ticket content → halt; ask user for clarification before the investigate step.
- More than one incident `P-NNN` remains eligible after every filter → halt; present the ambiguity to Cipher 🔓 (Lead Orchestrator). Do not pick one.
