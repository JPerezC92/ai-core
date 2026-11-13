# Entity architecture record

> **Status:** closed
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-10-29
> **Closed:** 2026-10-29
> **Objective:** Record the real `Problem` entity in the architecture guides and ADR 0004 so docs match the code.
> **Branch:** feat/ticket-runbook/add-problem-entity
> **Delivery:** one documentation slice; forecast ~80 authored additions + ~40 deletions, generated files excluded; slice 1 = ADR 0004 evidence + Python/scripts entity-vs-record notes. No code. ADR 0005 unchanged.
> **Runner:** `uv run --frozen python3 .opencode/skills/odd-workflow/scripts/validate_feature.py odd/tasks/entity-architecture-record.md`

## Specs

- S1 — User request, verbatim: "did u updated the dock about the achitecture? aDN adrS?". Acceptance: this feature exists because those docs were not updated with the `Problem` entity; the gap is closed here, not claimed already done.
- S2 — User requirement, verbatim: "FIX IT TOO". Acceptance: update `docs/architecture/decisions/0004-domain-behavior-placement.md` with `odd/tasks/problem-register-entity.md` as evidence: `Problem` is a class with `create()`, named domain values, and row-owned behavior; a TypedDict labeled as an entity with no behavior is the mislabel to avoid. Do not mark ADR 0004 `Accepted` in this feature. Do not edit ADR 0005.
- S3 — Stack-guide note: in `architecture/stacks/python.md` → `Domain and ports`, state that an entity is a class with `create()` and behavior; `TypedDict` is structured intermediate/record data and is not an entity; do not place behaviorless TypedDicts in `entities.py`.
- S4 — Script shape: in `architecture/shapes/scripts.md` → `P1`, allow the stack entity representation when a script domain has identity and invariants; keep data-only constants, pure transformations, and TypedDict records. Do not require every script type to become a class.
- S5 — No application/Python code, test, dependency, permission, destination, or DEBT-027/028 change. `clean-architecture.md` C3 already states the anemic/record distinction; do not duplicate it there.

## Tasks

- T1 | S2, S3, S4 | delegated (Scribe ✍️ owns documentation; architecture core and source-local ADR) — Scribe ✍️ (Docs & Problems Manager) | done | commit: 2f7255c5aabbebe9ee2e7467850b5459048b23c1
- T2 | S1, S2, S3, S4, S5 | delegated (independent semantic review; reviewer must not have authored the docs) — Sentinel 🛡️ (Quality Guardian) | done | commit: 2f7255c5aabbebe9ee2e7467850b5459048b23c1
- T3 | S1, S2, S3, S4, S5 | inline (coordinator validates, accepts, closes after work-unit commit) — Cipher 🔓 (Lead Orchestrator) | done | commit: 2f7255c5aabbebe9ee2e7467850b5459048b23c1

## Log

- L1 — User request, 2026-10-29, verbatim: "did u updated the dock about the achitecture? aDN adrS?"
- L2 — User correction, 2026-10-29, verbatim: "FIX IT TOO"
- L3 — 2026-10-29 — Gap: `problem-register-entity` shipped code only. ADR 0004 is still `Proposed` and still describes functional `domain/` modules as the local observation without `Problem`. Python `Domain and ports` has entity syntax but does not forbid naming TypedDicts as entities. Scripts P1 names constants and pure transformations only. ADR 0005 stays untouched. ADR 0004 is not silently `Accepted`.
- L4 — User authorization, 2026-10-29, verbatim: "GO"
- L5 — 2026-10-29 — T1 scribe1 wrote ADR 0004 evidence, python.md entity-vs-TypedDict bullet, scripts.md P1 entity permission. Sentinel 🛡️ (Quality Guardian) sentinel1 [PASS], zero open. ADR 0004 remains Proposed. ADR 0005 untouched. No code.
- L6 — Close: 2026-10-29 — T1–T3 done against `2f7255c5aabbebe9ee2e7467850b5459048b23c1` on `feat/ticket-runbook/add-problem-entity`. ADR 0004 records `Problem`; python.md and scripts.md P1 distinguish entity vs TypedDict. ADR 0004 still Proposed. ADR 0005 unchanged. No push, PR, merge, or tag.
