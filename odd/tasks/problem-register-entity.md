# Problem-register entity

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-10-29
> **Objective:** Make `ProblemRow` a real domain entity that owns its invariants and matchability, instead of a TypedDict labeled as an entity.
> **Branch:** N/A — Herald 📯 (Release Manager) creates it at the first commit
> **Delivery:** one serialized domain slice in ticket-runbook; forecast ~280 authored additions + ~120 deletions, generated files excluded; slice 1 = `Problem` entity + caller/test updates. Value-object TypedDicts stay records. DEBT-027/028 out of scope.
> **Runner:** `uv run --frozen --group dev pytest .opencode/skills/ticket-runbook/scripts -q`

## Specs

- S1 — User request, verbatim: "then we can make them real entities?". Acceptance: `ticket_runbook_pkg/domain/entities.py` no longer holds a TypedDict named as an identity-bearing domain model. `Problem` (today `ProblemRow`) is a framework-free class with immutable identity, read-only accessors, and `@classmethod create(...)` that enforces the row's validity. Invalid register cells do not become an entity.
- S2 — User requirement, verbatim: "whats the point of a entity if it dont have behaviour isnt that in the research?". Acceptance: row-owned rules move onto the entity: allowed team/lifecycle/allow_exact/status, symptom references at least one S-xx, incident vs not, matchable lifecycle (`candidate`|`active`|`mitigated`), and exact-match eligibility (`active` and `allow_exact=yes`). Identification consistency that spans a verdict plus several rows stays a domain function, not a fake method on one row.
- S3 — User requirement, verbatim: "i am still talking about the anemic entities, why they dont have behaviour?". Acceptance: only the misnamed register entity is converted. `AnalysisHeader`, `TicketIdentification`, `CloseOutSnapshot`, and `ModeFindings` remain data records. DEBT-027, DEBT-028, and other packages' TypedDicts are out of scope.
- S4 — Existing REGISTER-* and VERDICT-* finding strings remain the validator's observable output. Mapping from entity/domain errors onto those codes stays at the check that already emits them; do not rename or drop the codes.
- S5 — User requirement, verbatim: "take care about magic string". Acceptance: domain values are named types or constants, not scattered literals. Team, lifecycle, allow-exact, status, and identification-verdict comparisons in the entity and row-owned rules use those names. Table-cell text is mapped once at `create()` / parse. Finding codes stay the S4 strings, referenced as named constants, not inline copies.

## Tasks

- T1 | S1, S2, S4, S5 | delegated (Forge 🔨 (Implementer) owns Python skill-script code; script edit gates through Bastion 🧱 (Backend & Scripts Architect); test edits through Crucible 🔥 (Test Architect)) — Forge 🔨 (Implementer) | open | commit: pending
- T2 | S3, S4, S5 | delegated (independent semantic review; reviewer must not have authored the entity or tests) — Sentinel 🛡️ (Quality Guardian) | open | commit: pending
- T3 | S1, S2, S3, S4, S5 | inline (coordinator accepts gates, combined candidate, and close after the work-unit commit) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending

## Log

- L1 — User request, 2026-10-29, verbatim: "then we can make them real entities?"
- L2 — User correction, 2026-10-29, verbatim: "be critical , whats the point of a entity if it dont have behaviour isnt that in the research?"
- L3 — User correction, 2026-10-29, verbatim: "i am still talking about the anemic entities, why they dont have behaviour?"
- L4 — 2026-10-29 — Scope from inspected code, not an extra product idea: only `ProblemRow` is labeled "Identity-bearing domain model" while holding no behavior. Validity today lives in `domain/rules.py` (`check_register_rows`, `check_identification_consistency`). The other ticket-runbook TypedDicts are snapshots/results. Ticket-runbook is a skill script (`architecture/shapes/scripts.md` P1); the Python stack's entity syntax (class, `create()`, read-only properties, no setters) is the representation, with no IO on the entity.
- L5 — User correction, 2026-10-29, verbatim: "this will create real entities? and take care about magic string"
- L6 — 2026-10-29 — Real entity means S1/S2: a class, not a TypedDict; `create()`; row-owned behavior. Magic strings means S5: no ad-hoc `"active"` / `"yes"` / `"incident"` in entity or row rules; named domain values; S4 output codes kept as named constants.
- L7 — User authorization, 2026-10-29, verbatim: "yes"
- L8 — 2026-10-29 — T1 forge1 then forge2. Bastion 🧱 (Backend & Scripts Architect) bastion2 [PASS], zero open (F1 closed: `IdentificationVerdict.PENDING.value`). Crucible 🔥 (Test Architect) crucible2 [PASS], zero open (split modules; no `pytest.raises`). Forge GREEN: `uv run --frozen --group dev pytest .opencode/skills/ticket-runbook/scripts -q` → 117 passed. Independent review T2 next.
