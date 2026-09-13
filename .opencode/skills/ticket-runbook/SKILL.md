---
name: ticket-runbook
description: Scaffold a per-ticket working analysis (analysis/state.md + identify/investigate/synthesize) for an incident ticket, identify it register-first via S-xx → incident P-NNN, and collapse to one ticket_ID.md record at close. Use when starting analysis on a new incident ticket.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 2.0.0
  dependencies:
    - PyYAML==6.0.3
---

## What I do

Scaffold a per-ticket `analysis/` working set from `references/analysis/` (`state.md`, `01-identify.md`, `02-investigate.md`, `03-synthesize.md`) and run **register-first identification**: normalize the ticket, match an `S-xx` symptom class, then match at most one `Team: incident` `P-NNN` from `knowledge/problems.md` and issue a verdict of `exact`, `structural`, or `no_match`. The working analysis is always scaffolded, whatever the verdict. At close, the working analysis and `response-draft.md` collapse to one `ticket_<id>.md` record plus `screenshots/`, `validations/`, and the cited evidence.

`01-identify.md` also documents an optional, incident-only verifier route (the `query-verification` skill) on the investigate step that consumes one existing Query-budget slot; it never adds automatic query execution and never changes the state header schema.

## When to use me

- User provides a ticket ID for a **new** incident ticket.
- Cipher 🔓 (Lead Orchestrator) dispatches this skill at the start of a new incident analysis.
- Keywords: `ticket-runbook`, `analysis/`, ticket ID when no existing working analysis is present.

## Arguments

From the user's request, extract:

- **ticket id** — the ticket number (e.g. `183700`). If not provided, ask the user.

## Steps

### 1. Read the ticket

Delegate all ticket data extraction to the project's ticket-read tool. Do not read the ticket system directly here.

Required outputs:
- System (business area)
- Module
- Country/region + campaign/period (if applicable)
- Symptom summary (1–2 sentences)
- `due_by_time` (SLA deadline in ISO format)

Hold these values for later sections.

### 2. Identify — register-first (`S-xx` → incident `P-NNN`)

Run this order. Do not skip or reorder, and do not consult any other source for a verdict.

1. **Normalize the ticket** — derive system, module, country, campaign, and the raw symptom/error text from step 1.
2. **Match `S-xx`** — match the ticket's error signature against `knowledge/symptoms.md`. A class matches only when every **Required signal** is present and no **Exclusion** is present. Record the matching class (or "no class match"). One class is primary; note any secondary classes.
3. **Filter incident `P-NNN`** — read `knowledge/problems.md` and select only rows where `Team: incident`, `Symptom` references the matched `S-xx`, `System` and `Module` align with the ticket, and `Lifecycle` is matchable (`candidate`, `active`, or `mitigated`; `resolved` and `retired` are never matched).
4. **Evaluate discriminators and exclusions** — for each candidate row, every `Discriminators` `field=value` must be evaluated against the current ticket, and any `Exclusions` condition present disqualifies the row.
5. **Issue the verdict** — `exact`, `structural`, or `no_match`, then write it to `identification_verdict` in `analysis/state.md`.

**Verdict rules (HARD):**

| Verdict | Condition |
|---|---|
| `exact` | Exactly one `active` incident `P-NNN` with `Allow_exact: yes` remains, and **every** discriminator is already evidenced in the current ticket. |
| `structural` | Exactly one `candidate` or `active` incident `P-NNN` remains; its hypothesis still requires current-ticket validation. |
| `no_match` | No eligible incident `P-NNN` remains. **An empty `knowledge/problems.md` register always yields `no_match` — never halt on an empty register.** |
| `pending` | Initial scaffold value only; replaced in this step. |

- If more than one incident `P-NNN` remains eligible after every filter, do NOT choose. Record every candidate and return `no_match` with an ambiguity note for Cipher 🔓 (Lead Orchestrator).
- **Verdict-source restriction (HARD RULE):** only `S-xx` → incident `P-NNN` can produce `exact` or `structural`. Resolved-ticket archives, patterns registers, KBA/RCA catalogs, and knowledge search are evidence/backfill sources only — they MUST NOT issue, upgrade, or echo an identification verdict. They may be consulted only after a `no_match`, and only as labeled investigation evidence.
- A row does not need to exist for `no_match`; an empty register is the canonical `no_match` case.

### 3. Scaffold the working analysis (always)

Always scaffold, whatever the verdict — `exact`, `structural`, and `no_match` all get the same three working files.

1. If the ticket folder does not exist, create it first: ticket folder + `screenshots/` + `validations/` + ticket record (from `references/ticket-template.md`) + `response-draft.md` (from `references/response-draft-template.md`).
2. Copy the analysis template from `references/analysis/` into the ticket folder's `analysis/` subfolder: `state.md`, `01-identify.md`, `02-investigate.md`, `03-synthesize.md`.
3. Initialize the `analysis/state.md` header: `Phase` (`identify`), `SLA-due` (from ticket), `Updated` (current timestamp), `Hypotheses-outstanding` (`3/3`), `Query-budget` (`0/6`, used/limit; `6/6` is exhausted), `identification_verdict` (`pending`), `Same-query-reruns` (`0/2`).
4. Record the identification result in `01-identify.md`: system, module, matched `S-xx`, matched incident `P-NNN` (if any), discriminator/exclusion evaluation, verdict, and rationale.

**Screenshot naming convention:** files placed in `screenshots/` must follow the project's `NN_<source>_<entity>[_<distinguisher>].png` convention (zero-padded NN matches ImagenN order; no campaign/entity ID/region in filename). Forbidden initial names: `image1.png`, `screenshot.png`, any name without the `NN_` prefix. Investigator 🔍 (Incident Investigator) + Quill 🪶 (Note Drafter) dispatch prompts MUST reference final filenames; renaming at close-out is a process violation.

**Pre-stage rule:** ALL screenshots (query images and browser captures) MUST exist on disk in `screenshots/` BEFORE Quill 🪶 (Note Drafter) is dispatched for the response phase. Dispatching Quill against not-yet-created image paths causes a guaranteed self-audit FAIL (`image_path_invalid`).

**Imagen location rule:** every used image records its local `path:` (repo-relative file) and, when the ticket system returned one, its remote `url:` (ticket-system location). Never record a remote `url:` that does not exist, and never fabricate a local `path:`.

### 4. Validate

Immediately after scaffolding, run `python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <ticket-folder>/analysis --scaffold`. Exit 0 → proceed. Non-zero exit → read the error output, fix the offending field, re-run. Do NOT continue until the validator passes.

> Evidence discipline applies: if the validator reports a field value violation, fix the value to match actual evidence — never invent a value to satisfy the validator.

**Per-step validator invocation (HARD RULE):** before advancing the completed step `NAME` (`identify`, `investigate`, `synthesize`), run `python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <analysis-dir> --step NAME`. Abort if exit ≠ 0. Do NOT advance the `Phase:` field until the validator exits clean. After the header advances, reserve default full validation — `python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <analysis-dir>` — for checking every completed step through the `Phase:` header.

### 5. Dispatch the owning agent

After the analysis scaffolds and validates:

1. If the verdict is `exact` or `structural`: notify Cipher 🔓 (Lead Orchestrator) of the matched `P-NNN` and verdict so it dispatches Investigator 🔍 (Incident Investigator) for the investigate step.
2. If the verdict is `no_match`: notify Cipher 🔓 (Lead Orchestrator) that the register yielded no match and the investigate step starts from fresh hypotheses.

**HARD RULE — dispatch enforcement:** Cipher 🔓 (Lead Orchestrator) MUST dispatch Investigator 🔍 (Incident Investigator) to execute the investigate step. Cipher 🔓 (Lead Orchestrator) MUST NOT execute that step inline. Cipher 🔓 (Lead Orchestrator) owns all dispatch decisions. This skill does NOT dispatch agents directly.

### 6. Close-out collapse

At close, after the posted response is verified:

1. Run `python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <ticket-folder> --close-out`.
2. The durable set is `ticket_<id>.md` plus `screenshots/`, `validations/`, and every other cited evidence file.
3. Remove `analysis/state.md` and every `analysis/*.md` working file, and remove `response-draft.md`, **only after** the close-out check passes.
4. Never delete `screenshots/`, `validations/`, or any cited evidence file.

## Optional verifier route (investigate step)

The investigate step documents an optional, incident-only verifier route. It is off by default; the manual per-hypothesis query path is unchanged and remains the default.

- The `query-verification` skill validates an incident-owned, sidecar-defined SQL verifier against an invocation-time query root and evaluates the destination-owned adapter's normalized output offline. AICore never executes the query, holds credentials, or invokes the adapter.
- Exactly one adapter execution consumes exactly one existing Query-budget slot. The `6/6` cap, the `Same-query-reruns` cap of 2, and the normal per-hypothesis query path are unchanged; no new header field, counter, or budget is introduced.
- The redacted case-evidence record is written under the ticket's existing session-specific `validations/` folder with the verifier ID as the filename stem.
- The analysis and ticket evidence record only the verifier ID, the three-state verdict, the source/definition/evidence digests, and the redacted case-evidence path. Credentials, raw adapter output, rendered SQL, rendered parameter values, and unredacted configured identifiers are never retained.
- A `verified` verdict is symptom evidence only; it never establishes root-cause equivalence or authorizes a fix.

The normative contract lives in `.opencode/skills/query-verification/SKILL.md` and `.opencode/skills/query-verification/references/protocol-v1.md`; the optional block and the synthesis restriction live in `references/analysis/02-investigate.md` and `references/analysis/03-synthesize.md`.

## Post-write self-verification loop

Run immediately after scaffolding, before each step-header advance, and after every advance. Iterate until a full pass finds zero violations:

1. **Re-read** the written set: `analysis/state.md`, each written `analysis/0N-*.md`, and the ticket folder structure.
2. **Mechanical pass** — immediately after scaffolding, run `python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <analysis-dir> --scaffold`; it verifies the header plus the copied step structure while later template bodies remain intentional. Before advancing completed step `NAME`, run `python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <analysis-dir> --step NAME`; a completed step must contain no unfilled tokens. After the header advances, reserve default full validation — `python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py <analysis-dir>` — for all completed steps through the header. Fix anything it reports.
3. **Analysis pass** — re-read each file against `references/_consistency-checklist.md`: at scaffold time, verify `01-identify.md` `Pre` has this ticket's context while later template bodies intentionally remain unfilled; after completion, verify no completed step has unfilled tokens. In every mode, verify header values match evidence (`SLA-due`, `identification_verdict` vs the register match, kill-switch counters reflect actual consumption), folder structure complete (`screenshots/`, `validations/`, ticket record, `response-draft.md`), and screenshot `NN_` naming. Never invent a value to satisfy a check — stop and ask.
4. **Repeat** until a clean pass, then report the pass count.
5. **Cap (S-07):** after 3 iterations, or the same violation persisting twice unchanged, stop-and-ask instead of looping.

`scripts/validate_runbook.py` is a helper, not the authority — it catches repetitive mechanical drift; semantic correctness is the analysis pass.

## Examples

**Example 1 — new casuistic, no register match**

- User says: `#191700`
- Ticket: system X, module Y, region Z, period P; error matches `S-02`
- Register: no incident `P-NNN` for `S-02` + system X + module Y (register empty)
- Verdict: `identification_verdict: no_match`
- Result: `analysis/` scaffolded; validator exits 0; Cipher 🔓 (Lead Orchestrator) dispatches Investigator 🔍 (Incident Investigator) to frame hypotheses.

**Example 2 — structural match**

- User says: `#191800`
- Ticket: system W, module V, region U, period T; error matches `S-03`
- Register: one `candidate` incident `P-NNN` on `Symptom` + `System` + `Module`; discriminators partially evidenced
- Verdict: `identification_verdict: structural` — cited source: `knowledge/problems.md` (P-NNN)
- Result: `analysis/` scaffolded; Investigator 🔍 (Incident Investigator) validates the inherited hypothesis against the current ticket.

**Example 3 — exact match**

- User says: `#191900`
- Register: exactly one `active` incident `P-NNN` with `Allow_exact: yes`; every discriminator already evidenced in the ticket
- Verdict: `identification_verdict: exact` — cited source: `knowledge/problems.md` (P-NNN)
- Result: `analysis/` scaffolded; Cipher 🔓 (Lead Orchestrator) dispatches the recorded fix path through the normal approval flow.

## Troubleshooting

**Analysis template missing:**
- Cause: the `references/analysis/` template directory does not exist in this skill.
- Fix: halt; report to Cipher 🔓 (Lead Orchestrator) — the template precondition is not met. Do not scaffold manually.

**Validator exits non-zero:**
- Cause: missing or malformed header field in `analysis/state.md`, or a malformed step file.
- Fix: read the exact error line; edit only the offending field; re-run the validator.

**Empty `knowledge/problems.md`:**
- Cause: no incident `P-NNN` rows are registered yet.
- Fix: none — this is the valid `no_match` case. Scaffold the working analysis and proceed without halting.

**Ticket system auth error on read:**
- Cause: tool token expired.
- Fix: the ticket-read tool triggers the auth-refresh routine internally. If still failing after refresh, halt and report to Cipher 🔓 (Lead Orchestrator).

**Knowledge search unavailable:**
- Cause: the knowledge-search tool is not reachable.
- Fix: do not block — knowledge search is a backfill source, never a verdict source. Skip it and proceed with the register-first identification.
