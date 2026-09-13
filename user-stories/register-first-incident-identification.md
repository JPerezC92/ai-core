# User story — register-first-incident-identification

> **Created:** 2026-09-12
> **Title:** Register-first incident identification
> **Status:** active
> **Epic:** incident-diagnostics
> **Affected areas:** `.opencode/skills/ticket-runbook/`, `knowledge/symptoms.md`, `knowledge/problems.md`, `knowledge/agents.md`, `.opencode/agents/investigator.md`, `.opencode/agents/ledger.md`, `.opencode/agents/quill.md`

## Persona

- Cipher 🔓 (Lead Orchestrator) starting a new incident analysis, who must identify a known problem without scanning RAG, ticket archives, or KBA/RCA as matchers.

## Goal

- **G:** Incident identification is deterministic: ticket signal → `S-xx` → `P-NNN` → `exact` | `structural` | `no_match`.
  - Done when: an empty problem register yields `no_match` and a full investigation; exact/structural require a cited `P-NNN`; working analysis uses three files; close-out leaves `ticket_<id>.md` plus local `path:` and remote `url:` image locations.

## Scenario

- A new incident arrives. Cipher 🔓 (Lead Orchestrator) runs `ticket-runbook`. The skill classifies a symptom, matches at most one incident `P-NNN`, and writes `analysis/01-identify.md`, `analysis/02-investigate.md`, and `analysis/03-synthesize.md`. At close, Ledger 📒 (Record Keeper) verifies `ticket_<id>.md` and cited evidence files, then removes working analysis markdown and `response-draft.md`.

## Acceptance criteria

- ✅ Empty `knowledge/problems.md` is valid and produces `identification_verdict: no_match`, not a halt. Evidence: `knowledge/problems.md:44,52`; `.opencode/skills/ticket-runbook/SKILL.md:62`; `test_empty_register_verdict_no_match_ok`.
- ✅ Exact and structural verdicts cite an existing `P-NNN`; archives, patterns, KBA/RCA, and knowledge search cannot issue those verdicts. Evidence: `ticket-runbook/SKILL.md:56-66`; `knowledge/agents.md:21`; `investigator.md:66-68`; `test_exact_requires_cited_p_nnn`.
- ✅ First confirmed case admits `candidate` (structural only); second independent confirmed case may promote to `active`. Evidence: `knowledge/problems.md:26-34`.
- ✅ Working analysis is `state.md` + `01-identify.md` + `02-investigate.md` + `03-synthesize.md`. Evidence: `.opencode/skills/ticket-runbook/references/analysis/`.
- ✅ Close-out durable set is `ticket_ID.md` plus `screenshots/`, `validations/`, and other cited evidence; each used image records local `path:` and remote `url:` when both exist. Evidence: `ticket-runbook/SKILL.md:101-108`; `.opencode/agents/ledger.md` close-out collapse; `.opencode/agents/quill.md` image footer.
- ✅ Optional query-verification remains symptom evidence only and consumes one existing query-budget slot on the investigate step. Evidence: `ticket-runbook/SKILL.md:110-120`; `references/analysis/02-investigate.md`.

## Change log

- 2026-09-12 - register-first-incident-identification-20260912: created the feature definition for register-first identification and the 3-file working analysis / single-ticket close-out.

## Resolved decisions

- 2026-09-12 — rewrite `ticket-runbook` in place; Increment 1 is AICore-only; tismart upgrade follows the AICore merge.
- 2026-09-12 — working `analysis/` files collapse to `ticket_<id>.md` at close; keep screenshots, validations, and cited evidence; each image records local path and remote URL.
- 2026-09-12 — collision with `incident-query-verification-pilot`: extend that story's scenario from Phase 04 to the investigate step; do not change its completed acceptance criteria.
