---
name: ticket-runbook
description: Scaffold a runbook subfolder for an incident ticket using its bundled runbook template. Decides whether a ticket needs a full runbook based on prior-art search (known-problem register, resolved tickets, patterns register, KBA/RCA catalogs, knowledge search). Use when starting analysis on a new incident ticket.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.1.0
---

## What I do

Scaffold a per-ticket `runbook/` subfolder from `references/runbook/` and populate its header fields. Includes a prior-art gate: if a replay-candidate is found, skip runbook ceremony and apply the known solution directly.

## When to use me

- User provides a ticket ID for a **new** incident ticket.
- Cipher 🔓 (Lead Orchestrator) dispatches this skill at the start of a new incident analysis.
- Keywords: `runbook`, ticket ID when no existing runbook folder is present.

## Arguments

From the user's request, extract:

- **ticket id** — the ticket number (e.g. `183700`). If not provided, ask the user.

If not provided, ask the user.

## Steps

### 1. Read the ticket

Delegate all ticket data extraction to the project's ticket-read tool. Do not read the ticket system directly here.

Required outputs:
- Domain (business area)
- Module
- Country/region + campaign/period (if applicable)
- Symptom summary (1–2 sentences)
- `due_by_time` (SLA deadline in ISO format)

Hold these values for later sections.

### 2. Prior-art search

Run in order. Stop as soon as a replay-candidate verdict can be issued.

0. **Symptom-first diagnostic** — match the ticket's error signature against `knowledge/symptoms.md`; if a class matches, note the S-xx and its canonical diagnostic, then use the S-xx as a filter over `knowledge/problems.md` in the next step.
1. **Known-problem register** — read `knowledge/problems.md`. For each record, compare the ticket's symptom + module against the record's `Symptom` (S-xx), `Domain`, `Problem`, and `Evidence` fields. Match criterion: ≥2 of (system, module, issue_type, symptom keywords) align AND the record's `Team` field is `incident`. Note the record ID (P-NNN) and matched fields.
2. **Resolved ticket archive** — Grep the resolved-ticket archive on symptom keywords + module. Read each hit's summary, root cause, and frontmatter (module, related ticket, status). Same domain + module + failure mode:
   - same identifying values → `Replay-candidate: yes`
   - different values → `Replay-candidate: structural` (inherit hypothesis; VERIFY parent reference — do not copy blindly)
3. **Patterns register** — read the project's patterns registry. A pattern match sets `Replay-candidate: pending` — confirm with step 4.
4. **KBA/RCA catalogs** — Glob the knowledge-base and root-cause article folders. Scan for module + symptom keyword match. Note any matching file path.
5. **Knowledge search fallback** — run only after steps 0–4 return no match. Surface only results with score **>=0.85**. Discard everything below threshold silently. Do not narrate the lookup.

### 3. Decide runbook scaffold

| Verdict | Action |
|---|---|
| `Replay-candidate: yes` | Do NOT scaffold. Report the matching source, cite the workaround, recommend the derivation path. Signal Cipher — no phase files needed. |
| `Replay-candidate: structural` | Scaffold runbook (phase files needed for validation). Hypothesis inherited from prior. The investigator executes validation with adapted queries. |
| `Replay-candidate: no` | Proceed to step 4: scaffold the runbook. Full investigation phases. |

**Choosing between `yes` and `structural`:**
- Same values + same campaign → `yes` (exact replay)
- Same module + same failure chain + DIFFERENT values → `structural`
- When uncertain → `structural` (safer than `yes` — preserves validation step)

> **Parent-reference verification (HARD RULE):** when inheriting a parent/reference ticket from a prior sibling, VERIFY the reference still applies to THIS ticket (the prior may cite a different parent). Do not copy the parent number blindly — confirm with the user or re-derive.

### 4. Scaffold runbook

Execute when `Replay-candidate: no` (full scaffold) OR `Replay-candidate: structural` (scaffold with hypothesis and synthesis skipped — uses prior queries from the referenced ticket). Skip entirely when `Replay-candidate: yes`.

1. Copy the runbook template from `references/runbook/` (`runbook.md` + `phase-01-triage.md` … `phase-06-respond.md`) into the ticket folder's `runbook/` subfolder.
2. If the ticket folder does not exist, create it first: ticket folder + `screenshots/` + `validations/` + ticket record (from `references/ticket-template.md`) + `response-draft.md` (from `references/response-draft-template.md`).
3. Initialize `runbook.md` header fields: `Phase` (`01`), `SLA-due` (from ticket), `Updated` (current timestamp), `Hypotheses-outstanding` (`3/3`), `Query-budget` (`0/6`, used/limit; `6/6` is exhausted), `Replay-candidate`, `Same-query-reruns` (`0/2`).
4. Initialize the phase-01 triage file with ticket-specific context in its Pre block. Leave all Step / Gate / Abort sections as-is from the template.

**Screenshot naming convention:** files placed in `screenshots/` must follow the project's `NN_<source>_<entity>[_<distinguisher>].png` convention (zero-padded NN matches ImagenN order; no campaign/entity ID/region in filename). Forbidden initial names: `image1.png`, `screenshot.png`, any name without the `NN_` prefix. Investigator + Quill dispatch prompts MUST reference final filenames; renaming at close-out is a process violation.

**Pre-stage rule:** ALL screenshots (query images and browser captures) MUST exist on disk in `screenshots/` BEFORE Quill 🪶 (Note Drafter) is dispatched for the response phase. Dispatching Quill against not-yet-created image paths causes a guaranteed self-audit FAIL (`image_path_invalid`).

### 5. Validate

Immediately after scaffolding, run `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/validate_runbook.py <ticket-folder>/runbook --scaffold`. Exit 0 → proceed. Non-zero exit → read the error output, fix the offending field, re-run. Do NOT continue until the validator passes.

> Evidence discipline applies: if the validator reports a field value violation, fix the value to match actual evidence — never invent a value to satisfy the validator.

**Per-phase validator invocation (HARD RULE):** before advancing the completed phase `NN`, run `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/validate_runbook.py <runbook-dir> --phase NN`. Abort if exit ≠ 0. Do NOT advance the `Phase:` field until the validator exits clean. After the header advances, reserve default full validation — `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/validate_runbook.py <runbook-dir>` — for checking every completed phase through the `Phase:` header.

### 6. Dispatch first agent

After the runbook scaffolds and validates:

1. If prior-art search (step 2) already completed the prior-art phase logic: mark that phase complete in `runbook.md` and notify Cipher to skip to the hypothesis phase.
2. Otherwise: notify Cipher 🔓 (Lead Orchestrator) that the runbook is ready with the exact domain classified in phase-01.

**HARD RULE — dispatch enforcement:** Cipher MUST dispatch the investigator to execute the prior-art phase. Cipher MUST NOT execute that phase inline. Cipher owns all dispatch decisions. This skill does NOT dispatch agents directly.

## Post-write self-verification loop

Run immediately after scaffolding, before each phase-header advance, and after every advance. Iterate until a full pass finds zero violations:

1. **Re-read** the written set: `runbook/runbook.md`, each written `phase-NN-*.md`, and the ticket folder structure.
2. **Mechanical pass** — immediately after scaffolding, run `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/validate_runbook.py <runbook-dir> --scaffold`; it verifies the header plus the copied phase structure while later template bodies remain intentional. Before advancing completed phase `NN`, run `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/validate_runbook.py <runbook-dir> --phase NN`; a completed phase must contain no unfilled tokens. After the header advances, reserve default full validation — `uv run --locked --project .opencode/skills/ticket-runbook python .opencode/skills/ticket-runbook/scripts/validate_runbook.py <runbook-dir>` — for all completed phases through the header. Fix anything it reports.
3. **Analysis pass** — re-read each file against `references/_consistency-checklist.md`: at scaffold time, verify phase-01 `Pre` has this ticket's context while later template bodies intentionally remain unfilled; after completion, verify no completed phase has unfilled tokens. In every mode, verify header values match evidence (`SLA-due`, `Replay-candidate` vs prior-art, kill-switch counters reflect actual consumption), folder structure complete (`screenshots/`, `validations/`, ticket record, `response-draft.md`), and screenshot `NN_` naming. Never invent a value to satisfy a check — stop and ask.
4. **Repeat** until a clean pass, then report the pass count.
5. **Cap (S-07):** after 3 iterations, or the same violation persisting twice unchanged, stop-and-ask instead of looping.

`scripts/validate_runbook.py` is a helper, not the authority — it catches repetitive mechanical drift; semantic correctness is the analysis pass.

## Examples

**Example 1 — new casuistic, runbook scaffolded**

- User says: `#191700`
- Ticket: domain X, module Y, region Z, period P
- Prior-art: known-problem register — no match; KBA/RCA — no match; knowledge search 0.72 — below threshold, discarded
- Verdict: `Replay-candidate: no`
- Result: runbook scaffolded; validator exits 0; Cipher dispatches the investigator.

**Example 2 — replay-candidate, no runbook**

- User says: `#191800`
- Ticket: domain W, module V, region U, period T
- Prior-art: known-problem register — match on Symptom (S-xx) + Domain + Problem (identifier collision)
- Verdict: `Replay-candidate: yes` — source: `knowledge/problems.md` (P-NNN); matched fields: Symptom, Domain, Problem
- Result: no runbook scaffolded; finding block returned to Cipher; Quill 🪶 (Note Drafter) dispatched from the finding.

## Troubleshooting

**Runbook template missing:**
- Cause: the `references/runbook/` template directory does not exist in this skill.
- Fix: halt; report to Cipher — the template precondition is not met. Do not scaffold manually.

**Validator exits non-zero:**
- Cause: missing or malformed header field in `runbook.md`.
- Fix: read the exact error line; edit only the offending field; re-run the validator.

**Ticket system auth error on read:**
- Cause: tool token expired.
- Fix: the ticket-read tool triggers the auth-refresh routine internally. If still failing after refresh, halt and report to Cipher.

**Knowledge search unavailable:**
- Cause: the knowledge-search tool is not reachable.
- Fix: skip the fallback step only; continue with the earlier prior-art steps. Note the skip in output. Do NOT block on it.
