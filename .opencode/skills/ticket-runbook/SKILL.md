---
name: ticket-runbook
description: Scaffold a per-ticket working analysis (analysis/state.md + identify/investigate/synthesize) for an incident ticket, identify it register-first via S-xx → incident P-NNN, and collapse to one ticket_ID.md record at close. Use when starting analysis on a new incident ticket.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 2.4.1
  dependencies: PyYAML==6.0.3
---

## Project extensions

### Validator script

This project's ticket-runbook validator script is `uv run --frozen python3 .opencode/skills/ticket-runbook/scripts/validate_runbook.py`.

### Working-set and record templates

This project's ticket-runbook templates and references:

- Analysis template directory: `references/analysis/` (`state.md`, `01-identify.md`, `02-investigate.md`, `03-synthesize.md`)
- Ticket record template: `references/ticket-template.md`
- Response-draft template: `references/response-draft-template.md`
- Consistency checklist: `references/_consistency-checklist.md`
- Verifier protocol: `.opencode/skills/query-verification/SKILL.md` and `.opencode/skills/query-verification/references/protocol-v1.md`

### Register, working-set, and record paths

- Symptom register: `knowledge/symptoms.md` (rows `S-xx`).
- Problem register: `knowledge/problems.md` (rows `P-NNN`; `Team: incident`; `case:` / `pack:` / `diagnostic:` pointers).
- Per-ticket analysis working set: the `analysis/` subfolder containing `state.md`, `01-identify.md`, `02-investigate.md`, `03-synthesize.md`.
- Ticket folder artifacts: `screenshots/`, `validations/`, the ephemeral `response-draft.md`, and the durable `ticket_<id>.md` record.
- Ticket-record response section: `## Responses`.
- Close-out authorization phrase: `Close out now`.

### Screenshot naming convention

This project's screenshot files use the `NN_<source>_<entity>[_<distinguisher>].png` convention (zero-padded NN matches ImagenN order; no campaign/entity ID/region in filename).

## Mandatory core

### What I do

Scaffold a per-ticket analysis working set (see Project extensions) from the analysis template (see Project extensions) and run **register-first identification**: normalize the ticket, match an `S-xx` symptom class, then match at most one `Team: incident` `P-NNN` from the project's problem register (see Project extensions) and issue a verdict of `exact`, `structural`, or `no_match`. The working analysis is always scaffolded, whatever the verdict. When the root cause is confirmed, the runbook grows the symptom/problem registers immediately — before destructive collapse and never gated on it — preserving every executed query durably and, when the confirming query is reusable, a destination-relative verifier pair a later ticket can replay. At close, the working analysis and the project's response-draft file collapse to the durable ticket record plus the project's screenshots and validations directories (see Project extensions), and the cited evidence.

The identify-step artifact (see Project extensions) also documents an optional, incident-only verifier route (the `query-verification` skill) on the investigate step that consumes one existing Query-budget slot; it never adds automatic query execution and never changes the state header schema.

### When to use me

- User provides a ticket ID for a **new** incident ticket.
- Cipher 🔓 (Lead Orchestrator) dispatches this skill at the start of a new incident analysis.
- Keywords: `ticket-runbook`, the analysis working set (see Project extensions), ticket ID when no existing working analysis is present.

### Arguments

From the user's request, extract:

- **ticket id** — the ticket number (e.g. `183700`). If not provided, ask the user.

### Steps

#### 1. Read the ticket

Delegate all ticket data extraction to the project's ticket-read tool. Do not read the ticket system directly here.

Required outputs:
- System (business area)
- Module
- Country/region + campaign/period (if applicable)
- Symptom summary (1–2 sentences)
- `due_by_time` (SLA deadline in ISO format)

Hold these values for later sections.

#### 2. Identify — register-first (`S-xx` → incident `P-NNN`)

Run this order. Do not skip or reorder, and do not consult any other source for a verdict.

1. **Normalize the ticket** — derive system, module, country, campaign, and the raw symptom/error text from step 1.
2. **Match `S-xx`** — match the ticket's error signature against the project's symptom register (see Project extensions). A class matches only when every **Required signal** is present and no **Exclusion** is present. Record the matching class (or "no class match"). One class is primary; note any secondary classes.
3. **Filter incident `P-NNN`** — read the project's problem register (see Project extensions) and select only rows where `Team: incident`, `Symptom` references the matched `S-xx`, `System` and `Module` align with the ticket, and `Lifecycle` is matchable (`candidate`, `active`, or `mitigated`; `resolved` and `retired` are never matched).
4. **Evaluate discriminators and exclusions** — for each candidate row, every `Discriminators` `field=value` must be evaluated against the current ticket, and any `Exclusions` condition present disqualifies the row.
5. **Issue the verdict** — `exact`, `structural`, or `no_match`, then write it to the identification-verdict header field in the analysis state file (see Project extensions).

**Verdict rules (HARD):**

| Verdict | Condition |
|---|---|
| `exact` | Exactly one `active` incident `P-NNN` with `Allow_exact: yes` remains, and **every** discriminator is already evidenced in the current ticket. |
| `structural` | Exactly one `candidate` or `active` incident `P-NNN` remains; its hypothesis still requires current-ticket validation. |
| `no_match` | No eligible incident `P-NNN` remains. **An empty problem register (see Project extensions) always yields `no_match` — never halt on an empty register.** |
| `pending` | Initial scaffold value only; replaced in this step. |

- If more than one incident `P-NNN` remains eligible after every filter, do NOT choose. Record every candidate and return `no_match` with an ambiguity note for Cipher 🔓 (Lead Orchestrator).
- **Verdict-source restriction (HARD RULE):** only `S-xx` → incident `P-NNN` can produce `exact` or `structural`. Resolved-ticket archives, patterns registers, KBA/RCA catalogs, and knowledge search are evidence/backfill sources only — they MUST NOT issue, upgrade, or echo an identification verdict. They may be consulted only after a `no_match`, and only as labeled investigation evidence.
- A row does not need to exist for `no_match`; an empty register is the canonical `no_match` case.

#### 3. Scaffold the working analysis (always)

Always scaffold, whatever the verdict — `exact`, `structural`, and `no_match` all get the same three working files.

1. If the ticket folder does not exist, create it first: ticket folder + the project's screenshots directory + the project's validations directory + ticket record (from the ticket record template — see Project extensions) + the project's response-draft file (from the response-draft template — see Project extensions).
2. Copy the analysis template from the analysis template directory (see Project extensions) into the ticket folder's analysis subfolder as the project's analysis working set (see Project extensions).
3. Initialize the analysis state-file header (see Project extensions): `Phase` (`identify`), `SLA-due` (from ticket), `Updated` (current timestamp), `Hypotheses-outstanding` (`3/3`), `Query-budget` (`0/6`, used/limit, default limit 6), `identification_verdict` (`pending`), `Same-query-reruns` (`0/2`). **Query-budget (HARD):** exhausted means used equals the current limit; halt-and-ask at that point unless the user already raised the denominator. Raise the denominator first (`14/14`); never write used greater than limit; never write `14/6`.
4. Record the identification result in the identify-step artifact (see Project extensions): system, module, matched `S-xx`, matched incident `P-NNN` (if any), discriminator/exclusion evaluation, verdict, and rationale.

**Screenshot naming convention:** files placed in the project's screenshots directory must follow the project's screenshot naming convention (see Project extensions). Forbidden initial names: `image1.png`, `screenshot.png`, or any name without the project's required prefix (see Project extensions). Investigator 🔍 (Incident Investigator) + Quill 🪶 (Note Drafter) dispatch prompts MUST reference final filenames; renaming at close-out is a process violation.

**Pre-stage rule:** ALL screenshots (query images and browser captures) MUST exist on disk in the project's screenshots directory (see Project extensions) BEFORE Quill 🪶 (Note Drafter) is dispatched for the response phase. Dispatching Quill against not-yet-created image paths causes a guaranteed self-audit FAIL (`image_path_invalid`).

**Image location rule:** every used image records its local `path:` as a ticket-folder-relative file (the project's screenshot path spelling; see Project extensions) and, when the ticket system returned one, its remote `url:` (ticket-system location). Never record a remote `url:` that does not exist, never fabricate a local `path:`, and never spell the local path repo-relative (see Project extensions).

#### 4. Validate

Immediately after scaffolding, run the ticket-runbook validator script (see Project extensions) with the ticket folder's analysis directory and `--scaffold`. Exit 0 → proceed. Non-zero exit → read the error output, fix the offending field, re-run. Do NOT continue until the validator passes.

> Evidence discipline applies: if the validator reports a field value violation, fix the value to match actual evidence — never invent a value to satisfy the validator.

**Per-step validator invocation (HARD RULE):** before advancing the completed step `NAME` (`identify`, `investigate`, `synthesize`), run the validator script (see Project extensions) with `<analysis-dir> --step NAME`. Abort if exit ≠ 0. Do NOT advance the `Phase:` field until the validator exits clean. After the header advances, reserve default full validation — the validator script with `<analysis-dir>` — for checking every completed step through the `Phase:` header.

#### 5. Dispatch the owning agent

After the analysis scaffolds and validates:

1. If the verdict is `exact` or `structural`: notify Cipher 🔓 (Lead Orchestrator) of the matched `P-NNN` and verdict so it dispatches Investigator 🔍 (Incident Investigator) for the investigate step.
2. If the verdict is `no_match`: notify Cipher 🔓 (Lead Orchestrator) that the register yielded no match and the investigate step starts from fresh hypotheses.

**HARD RULE — dispatch enforcement:** Cipher 🔓 (Lead Orchestrator) MUST dispatch Investigator 🔍 (Incident Investigator) to execute the investigate step. Cipher 🔓 (Lead Orchestrator) MUST NOT execute that step inline. Cipher 🔓 (Lead Orchestrator) owns all dispatch decisions. This skill does NOT dispatch agents directly.

#### 6. Register admission (confirmed root cause; non-destructive)

Preparation starts as soon as the root cause is confirmed — it does not wait for the close-out authorization (see Project extensions). Cipher 🔓 (Lead Orchestrator) dispatches Scribe ✍️ (Docs & Problems Manager) to prepare an evidence-backed register draft. Scribe ✍️ (Docs & Problems Manager) presents it for exact user approval (`approved` or `aprobado`); only after that approval does Cipher 🔓 (Lead Orchestrator) apply the mutation through the destination's gated tool. If the destination workflow or tool is unavailable, stop and report; do not improvise. Complete the approved register mutation before destructive collapse:

1. Create the missing `S-xx` symptom class in the project's symptom register (see Project extensions) when no class matches the confirmed failure signature.
2. Admit a novel cause as a `candidate` `P-NNN` row in the project's problem register (see Project extensions) when no eligible problem exists.
3. Append the durable `case:` pointer for the current case to the existing `P-NNN` row's Evidence.
4. Promote a `candidate` to `active` only after a second independent confirmed case.

Register growth requires the durable case pointer but does not require a reusable diagnostic. When the confirming query is reusable, also persist it as parameterized SQL plus an adjacent `.verifier.yaml` sidecar at the destination project's declared query-storage path and record `diagnostic:<destination-relative-sidecar-path>` in the row's Evidence; if the destination has no declared path, ask for it — the `P-NNN` and case pointer are recorded first. When the proof path is a reusable identification pack rather than a one-row verifier, persist it at the destination-chosen path and record `pack:<destination-relative-pack-path>` in the row's Evidence; do not run the query-verification evaluator on a pack (see Project extensions) — it is not a verifier and has no sidecar or result contract. A later `structural` ticket follows a recorded `pack:` pointer first — resolving the destination-relative path and replaying that correlation with current-ticket keys under destination-owned execution (the core never executes or parses the pack) — then follows `diagnostic:` through the verifier protocol when present (see Project extensions), before framing a new query. The `case:` pointer is still recorded first, the destination chooses the pack layout, the core never names the directory, and the register row never receives SQL statements or result tables. This is symptom/problem register admission, not a patterns-catalog check.

This step is not destructive and never gates on file deletion.

#### 7. Close-out (two-stage: readiness gate, then authorized collapse)

Register-admission preparation starts at step 6; the approved mutation must be applied before collapse. This step only confirms that earlier mutation — it never re-admits. If approval or the destination's gated tool is missing, halt before collapse. The durable set is the durable ticket record plus the project's screenshots and validations directories (see Project extensions), and every other cited evidence file. At close, run this order without skipping or reordering:

1. Complete posted-response synchronization: the responses section (see Project extensions) of the durable ticket record mirrors the latest posted response (never the draft).
2. Run the validator script (see Project extensions) with `<ticket-folder> --pre-close`. This mode is read-only and requires: exactly one durable ticket record; the complete project analysis working set (state + step files; see Project extensions — nothing missing, nothing unexpected); the project's response-draft file; the project's screenshots and validations directories; a completed `synthesize` phase; every machine-addressable `path:` citation in the ticket record spelled ticket-folder-relative (the project's screenshot path spelling; see Project extensions) and resolving to an existing file inside the ticket folder; and valid identification/register consistency. Abort on any non-zero exit.
3. Semantic confirmation — the validator never claims this ground: confirm the earlier register admission completed (the case pointer, plus an identification-pack pointer or a diagnostic-sidecar pointer when applicable); every executed query from the investigate-step artifact (see Project extensions) is preserved verbatim in the durable ticket record or a cited validations artifact (see the retention rule in the investigate template — Project extensions); every non-local-path evidence citation (prose/backtick references) resolves to real evidence; and record content/completeness gates pass.
4. Obtain the exact close-out authorization phrase (see Project extensions).
5. Remove the analysis working-set state file, every analysis step file, and the project's response-draft file (see Project extensions) — nothing else.
6. Run the validator script (see Project extensions) with `<ticket-folder> --close-out` and require exit 0. If it fails after collapse, halt without deleting anything further: the durable ticket record, the screenshots and validations directories, and every cited durable evidence file are never deleted to satisfy a validator.

### Optional verifier route (investigate step)

The investigate step documents an optional, incident-only verifier route. It is off by default; the manual per-hypothesis query path is unchanged and remains the default.

- The `query-verification` skill validates an incident-owned, sidecar-defined SQL verifier against an invocation-time query root and evaluates the destination-owned adapter's normalized output offline. The core never executes the query, holds credentials, or invokes the adapter.
- Exactly one adapter execution consumes exactly one existing Query-budget slot. The default Query-budget limit is 6 (exhausted when used equals limit); halt-and-ask at that point unless the user already raised the denominator. Never write used greater than limit; never write `14/6`. The `Same-query-reruns` cap of 2 and the normal per-hypothesis query path are unchanged; no new header field, counter, or budget is introduced.
- The redacted case-evidence record is written under the ticket's existing session-specific validations folder (see Project extensions) with the verifier ID as the filename stem.
- The analysis and ticket evidence record only the verifier ID, the three-state verdict, the source/definition/evidence digests, and the redacted case-evidence path. Credentials, raw adapter output, rendered SQL, rendered parameter values, and unredacted configured identifiers are never retained.
- A `verified` verdict is symptom evidence only; it never establishes root-cause equivalence or authorizes a fix.

The normative contract lives in the `query-verification` skill and its protocol reference (see Project extensions); the optional block and the synthesis restriction live in the investigate and synthesize templates (see Project extensions).

### Post-write self-verification loop

Run immediately after scaffolding, before each step-header advance, and after every advance. Iterate until a full pass finds zero violations:

1. **Re-read** the written set: the analysis working-set state file, each written analysis step file (see Project extensions), and the ticket folder structure.
2. **Mechanical pass** — immediately after scaffolding, run the validator script (see Project extensions) with `<analysis-dir> --scaffold`; it verifies the header plus the copied step structure while later template bodies remain intentional. Before advancing completed step `NAME`, run the validator script (see Project extensions) with `<analysis-dir> --step NAME`; a completed step must contain no unfilled tokens. After the header advances, reserve default full validation — the validator script with `<analysis-dir>` — for all completed steps through the header. Fix anything it reports.
3. **Analysis pass** — re-read each file against the consistency checklist (see Project extensions): at scaffold time, verify the identify-step artifact's `Pre` has this ticket's context while later template bodies intentionally remain unfilled; after completion, verify no completed step has unfilled tokens. In every mode, verify header values match evidence (`SLA-due`, the identification-verdict field vs the register match, kill-switch counters reflect actual consumption), folder structure complete (the project's screenshots directory, validations directory, ticket record, and response-draft file; see Project extensions), and the project's screenshot naming convention. Never invent a value to satisfy a check — stop and ask.
4. **Repeat** until a clean pass, then report the pass count.
5. **Cap (S-07):** after 3 iterations, or the same violation persisting twice unchanged, stop-and-ask instead of looping.

The validator script is a helper, not the authority — it catches repetitive mechanical drift; semantic correctness is the analysis pass.

### Examples

**Example 1 — new casuistic, no register match**

- User says: `#191700`
- Ticket: system X, module Y, region Z, period P; error matches `S-02`
- Register: no incident `P-NNN` for `S-02` + system X + module Y (register empty)
- Verdict: `identification_verdict: no_match`
- Result: analysis working set scaffolded (see Project extensions); validator exits 0; Cipher 🔓 (Lead Orchestrator) dispatches Investigator 🔍 (Incident Investigator) to frame hypotheses.
- After the root cause is confirmed: Cipher 🔓 (Lead Orchestrator) dispatches Scribe ✍️ (Docs & Problems Manager), which admits a `candidate` `P-NNN` with the durable case pointer (and, when reusable, the verifier pair at the destination's declared path) — it does not wait for the close-out authorization (see Project extensions). Collapse waits for the close-out authorization.

**Example 2 — structural match**

- User says: `#191800`
- Ticket: system W, module V, region U, period T; error matches `S-03`
- Register: one `candidate` incident `P-NNN` on `Symptom` + `System` + `Module`; discriminators partially evidenced
- Verdict: `identification_verdict: structural` — cited source: the project's problem register (see Project extensions) (P-NNN)
- Result: analysis working set scaffolded (see Project extensions); Investigator 🔍 (Incident Investigator) validates the inherited hypothesis against the current ticket.

**Example 3 — exact match**

- User says: `#191900`
- Register: exactly one `active` incident `P-NNN` with `Allow_exact: yes`; every discriminator already evidenced in the ticket
- Verdict: `identification_verdict: exact` — cited source: the project's problem register (see Project extensions) (P-NNN)
- Result: analysis working set scaffolded (see Project extensions); Cipher 🔓 (Lead Orchestrator) dispatches the recorded fix path through the normal approval flow.

### Troubleshooting

**Analysis template missing:**
- Cause: the analysis template directory (see Project extensions) does not exist in this skill.
- Fix: halt; report to Cipher 🔓 (Lead Orchestrator) — the template precondition is not met. Do not scaffold manually.

**Validator exits non-zero:**
- Cause: missing or malformed header field in the analysis state file (see Project extensions), or a malformed step file.
- Fix: read the exact error line; edit only the offending field; re-run the validator.

**Empty problem register:**
- Cause: no incident `P-NNN` rows are registered yet.
- Fix: none — this is the valid `no_match` case. Scaffold the working analysis and proceed without halting.

**Ticket system auth error on read:**
- Cause: tool token expired.
- Fix: the ticket-read tool triggers the auth-refresh routine internally. If still failing after refresh, halt and report to Cipher 🔓 (Lead Orchestrator).

**Knowledge search unavailable:**
- Cause: the knowledge-search tool is not reachable.
- Fix: do not block — knowledge search is a backfill source, never a verdict source. Skip it and proceed with the register-first identification.
