# Phase 06 — Respond

> ⚠️ **STOP — Cipher 🔓 (Lead Orchestrator) dispatch only.** This phase Owner is Quill 🪶 (Note Drafter). Cipher 🔓 (Lead Orchestrator) MUST dispatch Quill 🪶 — do NOT draft prose inline. Quill's self-audit signature is required on the draft (see `.opencode/agents/quill.md`).

> **Owner:** Quill 🪶 (Note Drafter)
> **Pre:** `runbook/phase-05-synthesis.md` exists with a response surface; `response-draft.md` does not yet exist (or is empty).
> **Reads:** `runbook/phase-05-synthesis.md`; `runbook/phase-04-validate.md` (verbatim evidence for citation)
> **Writes:** `response-draft.md`

## Steps

1. Read the `runbook/phase-05-synthesis.md` response surface block verbatim.
2. Draft the response note in the customer's language. Rules: no filler intro sentence restating ticket metadata; jump to the finding. Cite exact counts/timestamps from phase-04 verbatim results.
3. Self-audit per Quill's hard rules: check every sentence for assumption-free language; check no internal DB field names exposed; check image ordering (collection data → user evidence → source validation); check all findings trace to phase-04 confirmed evidence.
4. If the self-audit finds a violation: fix inline before writing to disk. Do NOT write a failing draft.
5. Write the approved draft to `response-draft.md`.
6. Signal Cipher 🔓 (Lead Orchestrator) that the draft is ready for review and post via the response-post tool.

## Output

- **Artifact:** `response-draft.md`
- **Schema:** customer-language response note, no filler intro, no internal field names, all claims trace to phase-04 evidence, self-audit PASS.

## Gate

- ⬜ `response-draft.md` exists and is non-empty
- ⬜ Quill 🪶 (Note Drafter) self-audit PASS (no forbidden tokens, no assumptions, no orphan image refs)
- ⬜ Cipher 🔓 (Lead Orchestrator) approval obtained before the response-post tool runs

## Post-phase dispatch — HARD RULE: dispatched directly by Cipher 🔓 (Lead Orchestrator)

After this phase Gate passes, BEFORE advancing `Phase:` in `runbook.md`, starting the next phase, OR closing the ticket (for Phase 06), Cipher 🔓 (Lead Orchestrator) MUST dispatch Ledger 📒 (Record Keeper) to sync the ticket record per `.opencode/agents/ledger.md` § Incremental sync per phase. Forbidden: batching multiple phases' Ledger syncs into a single end-of-ticket dispatch.

## Abort conditions

- Phase-05 synthesis has no response surface (escalation-only outcome) → skip phase 06; Cipher 🔓 (Lead Orchestrator) posts the derivation note directly.
- Quill 🪶 (Note Drafter) self-audit FAILs after 2 revision cycles → halt; return the draft to Cipher 🔓 (Lead Orchestrator) with the audit failures listed.
