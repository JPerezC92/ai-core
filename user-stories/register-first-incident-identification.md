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
  - Done when: an empty problem register yields `no_match` and a full investigation; exact/structural require a cited `P-NNN`; working analysis uses three files; a non-destructive pre-close gate passes before semantic close-out confirmation and authorized collapse; post-collapse validation leaves `ticket_<id>.md` plus local `path:` and remote `url:` image locations.

## Scenario

- A new incident arrives. Cipher 🔓 (Lead Orchestrator) runs `ticket-runbook`. The skill classifies a symptom, matches at most one incident `P-NNN`, and writes `analysis/01-identify.md`, `analysis/02-investigate.md`, and `analysis/03-synthesize.md`. Register admission runs immediately when root cause is confirmed. At close, Ledger 📒 (Record Keeper) runs the non-destructive pre-close gate, confirms the earlier register mutation plus query/evidence/content retention, obtains the exact `Close out now` authorization, removes only the working analysis markdown and `response-draft.md`, then runs the post-collapse validator over `ticket_<id>.md` and cited evidence.

## Acceptance criteria

- ✅ Empty `knowledge/problems.md` is valid and produces `identification_verdict: no_match`, not a halt. Evidence: `knowledge/problems.md:44,52`; `.opencode/skills/ticket-runbook/SKILL.md:62`; `test_empty_register_verdict_no_match_ok`.
- ✅ Exact and structural verdicts cite an existing `P-NNN`; archives, patterns, KBA/RCA, and knowledge search cannot issue those verdicts. Evidence: `ticket-runbook/SKILL.md:56-66`; `knowledge/agents.md:21`; `investigator.md:66-68`; `test_exact_requires_cited_p_nnn`.
- ✅ First confirmed case admits `candidate` (structural only); second independent confirmed case may promote to `active`. Evidence: `knowledge/problems.md:26-34`.
- ✅ Working analysis is `state.md` + `01-identify.md` + `02-investigate.md` + `03-synthesize.md`. Evidence: `.opencode/skills/ticket-runbook/references/analysis/`.
- ✅ Close-out durable set is `ticket_ID.md` plus `screenshots/`, `validations/`, and other cited evidence; each used image records local `path:` and remote `url:` when both exist. Evidence: `.opencode/skills/ticket-runbook/SKILL.md` Close-out collapse; `.opencode/agents/ledger.md` close-out collapse; `.opencode/agents/quill.md` image footer.
- ✅ Close-out uses two mechanical stages: a read-only pre-close gate requires exactly one ticket record, the complete working set and draft, durable directories, every machine-addressable `path:` citation, and valid identification/register consistency; semantic review then confirms prior register admission and all other cited evidence before exact `Close out now`, ephemeral-file deletion, and the existing post-collapse assertion. Neither validator mode mutates ticket files. Evidence: `validate_runbook.py` `--pre-close`/`--close-out` (mutually exclusive argparse group; PRE-CLOSE violations; CLOSE-0..6 exact-one enforcement); `test_validate_runbook.py` 59 stdlib tests incl. `test_pre_close_passes_pure_and_public_validation`, `test_pre_close_is_byte_for_byte_non_mutating`, `test_close_out_fails_before_and_passes_after_collapse`; `ticket-runbook` SKILL.md 2.2.0 step 7; `_consistency-checklist.md` pre-close/semantic/authorization/postcondition sections; `ledger.md` 1.2.0 two-stage contract; Bastion 🧱 (Backend & Scripts Architect) and Crucible 🔥 (Test Architect) `[PASS]` 2026-09-16.
- ✅ Ticket-record `path:` citations are ticket-folder-relative `screenshots/<filename>` only; `--pre-close` and `--close-out` reject repo-relative `tickets/.../screenshots/...` spellings; Ledger 📒 (Record Keeper) LS-SCREENSHOTS and Quill 🪶 (Note Drafter) `image_path_invalid` resolve inside the ticket folder. Evidence: `validate_runbook.py` shared `_resolve_ticket_path` resolver + `test_validate_runbook.py` 59 stdlib tests incl. `test_repo_relative_spelling_fails_pre_close`, `test_repo_relative_spelling_fails_close_out`, `test_ticket_relative_cited_path_passes_pre_close`, `test_ticket_relative_cited_path_passes_close_out`, `test_close_out_rejects_parent_escape_via_close_5`, `test_directory_citation_fails_pre_close_and_close_out`; `ticket-template.md` footer; `SKILL.md` Imagen location rule; `_consistency-checklist.md` pre-close readiness; `ledger.md` Images scope + LS-SCREENSHOTS join; `quill.md` 1.1.1 `image_path_invalid`; Bastion 🧱 (Backend & Scripts Architect) and Crucible 🔥 (Test Architect) `[PASS]` 2026-09-16.
- ✅ Optional query-verification remains symptom evidence only and consumes one existing query-budget slot on the investigate step. Evidence: `ticket-runbook/SKILL.md:110-120`; `references/analysis/02-investigate.md`.
- ✅ After a confirmed root cause, register admission runs before destructive collapse — it does not wait for `Close out now` — creating or updating the `S-xx`/`P-NNN` row with a durable `case:` pointer. Evidence: `ticket-runbook` SKILL.md steps 6-7; `knowledge/agents.md` Proactive admission.
- ✅ Every executed investigation query survives collapse verbatim in `ticket_<id>.md` or a cited `validations/` artifact; when the confirming query is reusable it is optionally persisted as SQL plus adjacent sidecar at a destination-declared path with a `diagnostic:` pointer in Evidence. Evidence: `ticket-runbook` `references/analysis/02-investigate.md` Step 7; `knowledge/problems.md` Evidence format.
- ✅ When the proof path is a reusable identification pack (multi-statement or multi-result correlation), Evidence may record `pack:` plus a destination-relative path without placing SQL or result tables in `knowledge/problems.md` or `knowledge/symptoms.md`; the destination chooses how and where to store the pack; a later `structural` ticket follows `pack:` before framing a new query; `diagnostic:` remains protocol-v1 only. Evidence: `knowledge/problems.md:18,36`; `knowledge/agents.md:25`; `ticket-runbook/SKILL.md:110`; `references/analysis/02-investigate.md:14`; `_consistency-checklist.md:58,79-80`; Sentinel 🛡️ (Quality Guardian) `[PASS]` 2026-09-16.

## Change log

- 2026-09-12 - register-first-incident-identification-20260912: created the feature definition for register-first identification and the 3-file working analysis / single-ticket close-out.
- 2026-09-15 - ticket-runbook-register-admission-20260914: recorded the approved extension for proactive register growth, durable retention of every executed query, and optional destination-relative verifier replay; acceptance criteria update with implementation.
- 2026-09-15 - ticket-runbook-pre-close-20260915: planned the two-stage non-destructive readiness gate and post-collapse assertion after a real close-out exposed the 2.1.0 ordering contradiction.
- 2026-09-16 - ticket-runbook-pre-close-20260915: implemented the two-stage close-out — read-only `--pre-close` gate, semantic confirmation, exact `Close out now`, ephemeral-only deletion, post-collapse `--close-out` — across the validator suite (then 53 tests; 58 after the path-unification step), skill 2.2.0, consistency checklist, Ledger 📒 (Record Keeper) 1.2.0, and catalog 2.2.0.
- 2026-09-16 - ticket-runbook-pre-close-20260915: planned one ticket-folder-relative `path:` form `screenshots/<filename>` for both validator modes and every teaching surface.
- 2026-09-16 - ticket-runbook-pre-close-20260915: implemented the unified ticket-folder `path:` resolver (58-test suite), the short-form template/SKILL/checklist teaching, Ledger 📒 (Record Keeper) LS-SCREENSHOTS ticket-folder join, and Quill 🪶 (Note Drafter) 1.1.1 `image_path_invalid`.
- 2026-09-16 - ticket-runbook-pre-close-20260915: corrected the pre-close criterion's test-count citation from 53 to 58 after PR #41 review.
- 2026-09-16 - ticket-runbook-pre-close-20260915: PR #41 rework hardened `--pre-close` to reject a non-file citation (directory) like `--close-out`; test-count evidence refreshed to 59.
- 2026-09-16 - identification-pack-pointer-20260916: planned an optional `pack:` Evidence pointer for destination-owned identification packs; protocol-v1 `diagnostic:` unchanged; Tismart sync deferred.

## Resolved decisions

- 2026-09-12 — rewrite `ticket-runbook` in place; Increment 1 is AICore-only; tismart upgrade follows the AICore merge.
- 2026-09-12 — working `analysis/` files collapse to `ticket_<id>.md` at close; keep screenshots, validations, and cited evidence; each image records local path and remote URL.
- 2026-09-12 — collision with `incident-query-verification-pilot`: extend that story's scenario from Phase 04 to the investigate step; do not change its completed acceptance criteria.
- 2026-09-15 — `ticket-runbook-register-admission-20260914` extends this feature after a confirmed root cause: register growth happens before destructive collapse, every executed query remains durable, and an optional reusable verifier is discovered through the destination-relative `P-NNN` pointer.
- 2026-09-15 — User selected a new `--pre-close` readiness mode over a prose-only reorder; existing `--close-out` semantics remain the post-collapse assertion, and the later Tismart atomic sync is a separate post-merge plan.
- 2026-09-16 — User chose one ticket-folder-relative `path:` form `screenshots/<filename>` for AICore; both validator modes enforce it; Tismart `#229255` rewrite waits for the later adoption/close.
- 2026-09-16 — Identification packs are a `pack:` pointer, not `diagnostic:`; AICore defines replay order; destination chooses storage layout; no Tismart sync in this plan.
