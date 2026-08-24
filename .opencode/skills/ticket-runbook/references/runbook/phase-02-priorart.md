# Phase 02 — Prior Art

> ⚠️ **STOP — Cipher dispatch only.** This phase Owner is the Investigator (see `AGENTS.md` § Roster). Cipher 🔓 (L2 Lead) MUST dispatch the Investigator — do NOT execute Steps inline.

> **Owner:** Investigator
> **Pre:** `runbook/phase-01-triage.md` exists and has a dispatch list; `Replay-candidate: pending` in the runbook header.
> **Reads:** `knowledge/problems.md` (known-problem register, filtered by symptom class); the knowledge-base and root-cause article folders; the knowledge-search tool (threshold ≥0.85)
> **Writes:** `runbook/phase-02-priorart.md` (filled); updates `runbook.md` `Replay-candidate` field

## Steps

1. Read `knowledge/problems.md`. For each record, compare symptom + module from phase-01-triage.md against the record's `Symptom`, `Domain`, `Problem`, and `Evidence` fields. Note any match on ≥2 of: system, module, issue_type, symptom keywords.
2. Scan the knowledge-base article folder for a module + symptom keyword match.
3. Scan the root-cause article folder for matching root-cause patterns.
4. Run the knowledge-search tool with the symptom query. Surface only results with score ≥0.85. Discard everything below threshold silently.
5. Verdict — 3-tier ladder:
   - **`yes`**: ≥1 source matches on system + module + failure mode + same identifying values (same country/entity). Cite source path + match fields + workaround. Skip phases 03/04/05.
   - **`structural`**: ≥1 source matches on system + module + failure-mode chain (same tables, same data sources) but DIFFERENT identifying values (different country or entity). Cite source path + inherited hypothesis. Skip phase 03; execute phase 04 with adapted queries. If phase-04 results deviate from the prior pattern, escalate to `no`.
   - **`no`**: No match from any step. Full investigation phases 02-06.
6. Write `runbook/phase-02-priorart.md`: list of sources scanned, matches found (or "no match"), verdict, workaround from the matching problem file (if yes/structural), recommended derivation path if replay confirmed.
7. Update `runbook.md`: set `Replay-candidate: yes|structural|no`, `Phase: 02`, `Updated: <now>`.

## Output

- **Artifact:** `runbook/phase-02-priorart.md` + updated `runbook/runbook.md`
- **Schema:** prior-art file lists sources-checked, match-evidence (file path + matched fields), verdict (`yes/no`), workaround text if yes, derivation recommendation if yes.

## Prior art results

| Source | Path | Match fields | Verdict |
|---|---|---|---|
| known-problem register | <fill or "no match"> | <fill> | <fill> |
| resolved-ticket archive | <fill or "no match"> | <fill> | <fill> |
| knowledge-base | <fill or "no match"> | <fill> | <fill> |
| root-cause articles | <fill or "no match"> | <fill> | <fill> |
| knowledge search (≥0.85) | <fill or "no match"> | <fill> | <fill> |

**Replay-candidate verdict:** yes / structural / no

> **Parent-ref verification (HARD RULE):** When inheriting a parent/reference ticket from a prior sibling, VERIFY the reference still applies to THIS ticket (the prior may cite a different parent). Do not copy the parent number blindly — confirm with the user or re-derive.

## Gate

- ⬜ All known-problem register records filtered by symptom class were scanned (count matches checked count)
- ⬜ Knowledge-search tool called with threshold ≥0.85 applied
- ⬜ `Replay-candidate` field in `runbook.md` is `yes`, `structural`, or `no` (not `pending`)
- ⬜ If `yes`: source path cited; workaround block present
- ⬜ If `structural`: prior source cited; inherited hypothesis stated; adapted query plan noted

## Post-phase dispatch (HARD RULE — Cipher direct)

After this phase Gate passes, BEFORE advancing `Phase:` in `runbook.md`, starting the next phase, OR closing the ticket (for Phase 06), Cipher 🔓 (L2 Lead) MUST dispatch Ledger 📒 to sync the ticket record per `.opencode/agents/ledger.md` § Incremental sync per phase. Forbidden: batching multiple phases' Ledger syncs into a single end-of-ticket dispatch.

## Abort conditions

- `knowledge/problems.md` missing or empty → halt; prior-art primary source absent. Report to Cipher — cannot issue a replay verdict.
- Knowledge-search tool unavailable → continue with steps 1-3 only; note the skip in phase-02 output; do NOT block on the tool failure.
