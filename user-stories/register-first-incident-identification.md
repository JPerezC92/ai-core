# User story — register-first-incident-identification

> **Created:** 2026-09-12
> **Title:** Register-first incident identification
> **Status:** active
> **version:** 1.0.0
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

- ✅ Empty `knowledge/problems.md` is valid and produces `identification_verdict: no_match`, not a halt. Evidence: `knowledge/problems.md` (empty-register is valid); `.opencode/skills/ticket-runbook/SKILL.md` verdict table `no_match` row and step 5; `test_empty_register_verdict_no_match_ok`.
- ✅ Exact and structural verdicts cite an existing `P-NNN`; archives, patterns, KBA/RCA, and knowledge search cannot issue those verdicts. Evidence: `ticket-runbook/SKILL.md` verdict-source restriction; `knowledge/agents.md` register-first identification; `investigator.md` verdict-source restriction; `test_exact_requires_cited_p_nnn`.
- ✅ First confirmed case admits `candidate` (structural only); second independent confirmed case may promote to `active`. Evidence: `knowledge/problems.md` lifecycle rules.
- ✅ Working analysis is `state.md` + `01-identify.md` + `02-investigate.md` + `03-synthesize.md`. Evidence: `.opencode/skills/ticket-runbook/references/analysis/`.
- ✅ Close-out durable set is `ticket_ID.md` plus `screenshots/`, `validations/`, and other cited evidence; each used image records local `path:` and remote `url:` when both exist. Evidence: `.opencode/skills/ticket-runbook/SKILL.md` Close-out collapse; `.opencode/agents/ledger.md` close-out collapse; `.opencode/agents/quill.md` image footer.
- ✅ Close-out uses two mechanical stages: a read-only pre-close gate requires exactly one ticket record, the complete working set and draft, durable directories, every machine-addressable `path:` citation, and valid identification/register consistency; semantic review then confirms prior register admission and all other cited evidence before exact `Close out now`, ephemeral-file deletion, and the existing post-collapse assertion. Neither validator mode mutates ticket files. Evidence: `validate_runbook.py` `--pre-close`/`--close-out` (mutually exclusive argparse group; PRE-CLOSE violations; CLOSE-0..6 exact-one enforcement); `test_validate_runbook.py` cases incl. `test_pre_close_passes_pure_and_public_validation`, `test_pre_close_is_byte_for_byte_non_mutating`, `test_close_out_fails_before_and_passes_after_collapse`; `ticket-runbook` SKILL.md close-out step; `_consistency-checklist.md` pre-close/semantic/authorization/postcondition sections; `ledger.md` two-stage contract; Bastion 🧱 (Backend & Scripts Architect) and Crucible 🔥 (Test Architect) `[PASS]` 2026-09-16.
- ✅ Ticket-record `path:` citations are ticket-folder-relative `screenshots/<filename>` only; `--pre-close` and `--close-out` reject repo-relative `tickets/.../screenshots/...` spellings; Ledger 📒 (Record Keeper) LS-SCREENSHOTS and Quill 🪶 (Note Drafter) `image_path_invalid` resolve inside the ticket folder. Evidence: `validate_runbook.py` shared `_resolve_ticket_path` resolver + `test_validate_runbook.py` cases incl. `test_repo_relative_spelling_fails_pre_close`, `test_repo_relative_spelling_fails_close_out`, `test_ticket_relative_cited_path_passes_pre_close`, `test_ticket_relative_cited_path_passes_close_out`, `test_close_out_rejects_parent_escape_via_close_5`, `test_directory_citation_fails_pre_close_and_close_out`; `ticket-template.md` footer; `SKILL.md` Imagen location rule; `_consistency-checklist.md` pre-close readiness; `ledger.md` Images scope + LS-SCREENSHOTS join; `quill.md` `image_path_invalid`; Bastion 🧱 (Backend & Scripts Architect) and Crucible 🔥 (Test Architect) `[PASS]` 2026-09-16.
- ✅ Optional query-verification remains symptom evidence only and consumes one existing query-budget slot on the investigate step. Evidence: `ticket-runbook/SKILL.md` query-verification step; `references/analysis/02-investigate.md`.
- ✅ After a confirmed root cause, register admission runs before destructive collapse — it does not wait for `Close out now` — creating or updating the `S-xx`/`P-NNN` row with a durable `case:` pointer. Evidence: `ticket-runbook` SKILL.md steps 6-7; `knowledge/agents.md` Proactive admission.
- ✅ Every executed investigation query survives collapse verbatim in `ticket_<id>.md` or a cited `validations/` artifact; when the confirming query is reusable it is optionally persisted as SQL plus adjacent sidecar at a destination-declared path with a `diagnostic:` pointer in Evidence. Evidence: `ticket-runbook` `references/analysis/02-investigate.md` Step 7; `knowledge/problems.md` Evidence format.
- ✅ When the proof path is a reusable identification pack (multi-statement or multi-result correlation), Evidence may record `pack:` plus a destination-relative path without placing SQL or result tables in `knowledge/problems.md` or `knowledge/symptoms.md`; the destination chooses how and where to store the pack; a later `structural` ticket follows `pack:` before framing a new query; `diagnostic:` remains protocol-v1 only. Evidence: `knowledge/problems.md` Evidence format and operational gate; `knowledge/agents.md` identification packs; `ticket-runbook/SKILL.md` verifier-step guidance; `references/analysis/02-investigate.md` Step 7; `_consistency-checklist.md` sections `Query retention and register admission (close-out)` and `Semantic close-out confirmation (before authorization)`; Sentinel 🛡️ (Quality Guardian) `[PASS]`.
- ✅ Fill-token scan ignores HTML comments, including a single-line comment in `analysis/state.md`, so `--pre-close` does not report them as `UNFILLED-TOKEN`. Evidence: `validate_runbook.py` `_check_step_body_fill_markers`; `test_state_html_comment_is_not_unfilled_token`; Bastion 🧱 (Backend & Scripts Architect) and Crucible 🔥 (Test Architect) `[PASS]` 2026-09-27.
- ✅ Instruction CLI placeholders `` `<sidecar-parent-dir>` `` and `` `<sidecar-path>` ``, and durable ticket records spelled with `` `<ID>` ``, do not fail `--step investigate`; Output fill tokens still fail until filled. Evidence: `EXCLUDE_FILL_TOKENS`; `test_filled_investigate_keeps_sidecar_command_examples`; `test_unfilled_output_fill_fails_step_investigate`.
- ✅ KILL-2 compares Query-budget used to the header denominator, not a hardcoded 6. `14/14` passes; `7/6` fails. Default scaffold limit remains 6. Evidence: `validate_runbook.py` `check_kill_switches`; `test_query_budget_compared_to_denominator`; `test_pre_close_accepts_authorized_raised_query_budget`; `test_pre_close_rejects_query_budget_over_denominator`; `ticket-runbook` SKILL.md 2.4.0.

## Change log

- 2026-09-27 — runbook-budget-and-plan-review-20260927: added HTML-comment fill-token ignore, sidecar instruction excludes, and the denominator-authoritative Query-budget KILL-2 (`ticket-runbook` 2.4.0).
- 2026-09-16 — ticket-runbook-pre-close-20260915: delivered the two-stage non-destructive close-out and the unified ticket-folder `path:` form.
- 2026-09-16 — identification-pack-pointer-20260916: added the optional `pack:` Evidence pointer for destination-owned identification packs.
- 2026-09-15 — ticket-runbook-register-admission-20260914: added proactive register admission and durable retention of every executed query.
- 2026-09-12 — register-first-incident-identification-20260912: created the register-first identification and 3-file working analysis / single-ticket close-out definition.
- before 2026-09-12 — earlier history: see git history for this file.

## Resolved decisions

- 2026-09-12 — working `analysis/` files collapse to `ticket_<id>.md` at close; screenshots, validations, and cited evidence are kept; each image records a local path and remote URL.
- 2026-09-15 — register growth happens before destructive collapse; every executed query stays durable; an optional reusable verifier is discovered through the destination-relative `P-NNN` pointer.
- 2026-09-16 — one ticket-folder-relative `path:` form `screenshots/<filename>`; both validator modes enforce it.
- 2026-09-16 — identification packs are a `pack:` pointer, not `diagnostic:`; AICore defines replay order; the destination chooses the storage layout.
