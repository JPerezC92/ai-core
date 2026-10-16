<!-- core:begin -->
# User story — register-first-incident-identification

> **Created:** 2026-09-12
> **Title:** Register-first incident identification
> **Status:** active
> **version:** 1.1.1
> **Epic:** incident-diagnostics
> **Affected areas:** `.opencode/skills/ticket-runbook/`, `knowledge/symptoms.md`, `knowledge/problems.md`, `knowledge/agents.md`, `.opencode/agents/investigator.md`, `.opencode/agents/ledger.md`, `.opencode/agents/quill.md`, `.opencode/agents/scribe.md`

## Persona

- Cipher 🔓 (Lead Orchestrator) starting a new incident analysis, who must identify a known problem without scanning RAG, ticket archives, or KBA/RCA as matchers.

## Goal

- **G:** Incident identification is deterministic: ticket signal → symptom class → known problem → `exact` | `structural` | `no_match`.
  - Done when: an empty problem register yields `no_match` and a full investigation; exact/structural require a cited problem identifier; working analysis uses one bounded working set; an evidence-backed register draft receives exact `approved` / `aprobado` authorization before gated mutation; a non-destructive pre-close gate passes before semantic close-out confirmation and authorized collapse; post-collapse validation leaves one durable ticket record plus local and remote image locations.

## Scenario

- A new incident arrives. Cipher 🔓 (Lead Orchestrator) runs `ticket-runbook`. The skill classifies a symptom, matches at most one known problem, and writes the working analysis. When root cause is confirmed, Scribe ✍️ (Docs & Problems Manager) prepares the register-admission draft immediately; after exact `approved` / `aprobado` user approval, Cipher 🔓 (Lead Orchestrator) applies it through the destination's gated tool before collapse. At close, Ledger 📒 (Record Keeper) runs the non-destructive pre-close gate, confirms the earlier register mutation plus query/evidence/content retention, obtains the exact `Close out now` authorization, removes only the working analysis markdown and the response draft, then runs the post-collapse validator over the ticket record and cited evidence.

## Acceptance criteria

- ✅ **AC1:** An empty problem register is a valid state and produces a `no_match` verdict rather than halting the workflow.
- ✅ **AC2:** `exact` and `structural` verdicts cite an existing problem identifier; archives, patterns, knowledge-base articles, and knowledge search cannot issue those verdicts.
- ✅ **AC3:** A problem entry is admitted as `candidate` on the first confirmed case and may be promoted to `active` only after a second independent confirmed case.
- ✅ **AC4:** Working analysis is a bounded working set of a state file and three ordered analysis steps — identify, investigate, synthesize — and nothing else.
- ✅ **AC5:** Close-out retains one durable ticket record plus its screenshots, validations, and other cited evidence; each used image records a local path and a remote URL when both exist.
- ✅ **AC6:** Close-out runs two ordered stages: a read-only pre-close gate, then an authorized collapse. The gate requires exactly one ticket record, the complete working set and response draft, durable directories, every machine-addressable citation, and consistent identification/register state. Semantic review then confirms prior register admission and all other cited evidence before the explicit collapse authorization. Both validator modes are read-only; the separately authorized collapse performs the documented working-file deletion.
- ✅ **AC7:** Image citations in a ticket record are ticket-folder-relative and resolve inside the ticket folder; repository-relative spellings and parent-directory escapes are rejected at both close-out stages.
- ✅ **AC8:** Optional query verification remains symptom evidence only and consumes one existing query-budget slot on the investigate step.
- ✅ **AC9:** Register admission is prepared before destructive collapse and does not wait for the collapse authorization; a missing admission workflow or gated tool halts the operation.
- ✅ **AC10:** Every executed investigation query survives collapse verbatim in the ticket record or a cited validation artifact; a reusable confirming query is optionally persisted as SQL plus an adjacent sidecar referenced from Evidence.
- ✅ **AC11:** When the proof path is a reusable identification pack, Evidence records a pointer to a destination-relative pack path rather than inlining SQL or result tables in the registers, and a later structural match follows that pointer before framing a new query.
- ✅ **AC12:** Fill-token scanning ignores HTML comments, so commented-out example tokens do not fail the pre-close gate.
- ✅ **AC13:** Placeholders inside documented command examples do not fail step validation; genuine unfilled output tokens still fail until filled.
- ✅ **AC14:** Query-budget enforcement compares used slots to the declared denominator rather than a fixed default; the scaffold default remains six.

## Proof

- AC1 → `knowledge/problems.md` `## Rules` · `.opencode/skills/ticket-runbook/SKILL.md` `#### 2. Identify — register-first` verdict table · `.opencode/skills/ticket-runbook/scripts/test_validate_runbook_register_first.py` `test_empty_register_verdict_no_match_ok`
- AC2 → `knowledge/agents.md` `### Register-first identification (HARD RULE)` · `.opencode/agents/investigator.md` `### Hard Rules` verdict-source restriction · `.opencode/skills/ticket-runbook/scripts/test_validate_runbook_register_first.py` `test_exact_requires_cited_p_nnn`
- AC3 → `knowledge/problems.md` `## Lifecycle`
- AC4 → `.opencode/skills/ticket-runbook/SKILL.md` `### Working-set and record templates` · `.opencode/skills/ticket-runbook/references/analysis/state.md` and ordered analysis-step templates
- AC5 → `.opencode/skills/ticket-runbook/SKILL.md` `#### 7. Close-out (two-stage: readiness gate, then authorized collapse)` · `.opencode/agents/ledger.md` `#### Close-out collapse (two-stage contract)` · `.opencode/agents/quill.md` `### Hard Rules` image discipline/footer
- AC6 → `.opencode/skills/ticket-runbook/scripts/ticket_runbook_pkg/entry.py` `validate_pre_close` and `validate_close_out` · `.opencode/skills/ticket-runbook/scripts/test_validate_runbook_pre_close.py` `ValidateRunbookPreCloseTests` · `.opencode/skills/ticket-runbook/scripts/test_validate_runbook_close_out.py` `ValidateRunbookCloseOutTests`
- AC7 → `.opencode/skills/ticket-runbook/scripts/ticket_runbook_pkg/entry.py` `_resolve_ticket_path` · `.opencode/skills/ticket-runbook/scripts/test_validate_runbook_paths.py` `ValidateRunbookPathCitationTests` · `.opencode/agents/ledger.md` `#### Images scope` · `.opencode/agents/quill.md` `#### Self-audit before return (CRITICAL)`
- AC8 → `.opencode/skills/ticket-runbook/SKILL.md` `### Optional verifier route (investigate step)` · `.opencode/skills/ticket-runbook/references/analysis/02-investigate.md` optional verifier route and query-budget accounting
- AC9 → `.opencode/skills/ticket-runbook/SKILL.md` register-admission and two-stage close-out workflow · `knowledge/agents.md` `### Register-first identification (HARD RULE)` proactive admission · `.opencode/agents/scribe.md` `#### Problem record management`
- AC10 → `.opencode/skills/ticket-runbook/references/analysis/02-investigate.md` Step 7 Retention · `knowledge/problems.md` `## Entry format` Evidence
- AC11 → `knowledge/problems.md` `## Entry format` Evidence and `## Lifecycle` operational gate · `knowledge/agents.md` `### Register-first identification (HARD RULE)` proactive admission · `.opencode/skills/ticket-runbook/references/analysis/02-investigate.md` Step 7 Retention
- AC12 → `.opencode/skills/ticket-runbook/scripts/test_validate_runbook.py` `test_state_html_comment_is_not_unfilled_token` · `.opencode/skills/ticket-runbook/scripts/test_validate_runbook_pre_close.py` `test_state_html_comment_is_not_unfilled_token_in_pre_close`
- AC13 → `.opencode/skills/ticket-runbook/scripts/test_validate_runbook_step_mode.py` `test_filled_investigate_keeps_sidecar_command_examples`, `test_unfilled_output_fill_fails_step_investigate`
- AC14 → `.opencode/skills/ticket-runbook/SKILL.md` `#### 3. Scaffold the working analysis (always)` Query-budget rule · `.opencode/skills/ticket-runbook/scripts/test_validate_runbook_header_budgets.py` `test_query_budget_compared_to_denominator` · `.opencode/skills/ticket-runbook/scripts/test_validate_runbook_pre_close.py` raised/exceeded denominator cases

## Constraints

- Identification is register-first: only the problem register can issue `exact` or `structural`, and each cites an existing problem identifier — because matching against archives or knowledge bases reintroduces the guessing the register exists to remove.
- Register growth happens before destructive collapse — because a confirmed root cause that is lost with the working set is unrecoverable.
- Both close-out validator modes are non-mutating — because a validator that writes cannot honestly serve as a gate.
- Ticket image citations use one ticket-folder-relative form — because two accepted spellings produce two resolution bugs.
- Identification packs are an Evidence pointer, not inlined diagnostic content — because the destination owns the storage layout and the registers must stay thin.
- Collapse requires an exact user authorization string — because deleting working analysis is destructive and is never implied by a readiness gate.

<!-- core:end -->

<!-- project:begin -->
## Approval record

> **Contract approval:** 2026-10-15 — user approved clarifying read-only validator modes versus separately authorized collapse, preserving all close-out authorization and evidence-retention gates. Revision history is explicitly pending under the approved timing rule.

## Local evidence

- **AC6:** Prior source Proof recorded Bastion 🧱 (Backend & Scripts Architect) and Crucible 🔥 (Test Architect) `[PASS]` on 2026-09-16.
- **AC11:** Prior source Proof recorded Sentinel 🛡️ (Quality Guardian) `[PASS]` for identification-pack pointer handling.
- **AC12:** Prior source Proof recorded Bastion 🧱 (Backend & Scripts Architect) and Crucible 🔥 (Test Architect) `[PASS]` on 2026-09-27. These retained observations are not fresh executions or destination verification.

## Revision tracking

- 2026-10-15 — Approved validator/collapse actor clarification awaits a delivery-matching history reference. Existing validator evidence and exact destructive-action authorization remain governing; no ticket mutation is performed by this revision. History finalization remains required before completion, archival, or release handoff.

## Change log

- before 2026-09-16 — earlier history: see git history for this file
- 2026-09-16 — ticket-runbook-pre-close-20260915 (PR #41): delivered the two-stage non-destructive close-out and the unified ticket-folder `path:` form.
- 2026-09-16 — identification-pack-pointer-20260916 (PR #42): added the optional `pack:` Evidence pointer for destination-owned identification packs.
- 2026-09-27 — runbook-budget-and-plan-review-20260927 (PR #44): added HTML-comment fill-token ignore, sidecar instruction excludes, and the denominator-authoritative Query-budget KILL-2 (`ticket-runbook` 2.4.0).
- 2026-10-09 — aicore-all-files-pr-20261008 (PR #52): replaced version-pinned Query-budget evidence, made approval before gated register mutation explicit, and repointed register/pre-close/close-out/path evidence to current concern-focused modules.
- 2026-10-12 — story revision (PR #59): split behavioural criteria from `## Proof`, generalized the working-set and close-out contracts, and moved register-first policy into `## Constraints`.
<!-- project:end -->
