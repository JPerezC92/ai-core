# Diagnostics directory clearance

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-02
> **Objective:** Clear `knowledge/diagnostics/` as one region directory root instead of three per-file rows.
> **Branch:** N/A — not created; suggested `feat/core-sync/clear-diagnostics-directory`
> **Delivery:** single work-unit commit; forecast ≈40 authored additions + ≈15 deletions (definition + registry), far below the ~400-line strategy trigger. Slices: definition (T1) → registry (T2) → verification (T3).
> **Runner:** `uv run --frozen --group dev pytest -q`

Load and read the `odd-workflow` skill (`.opencode/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — The distribution registry uses the `knowledge/diagnostics/` folder root instead of three per-file entries. Exact requirement: the knowledge/diagnostics in the distribution file have 3 entries can we just use this knowledge/diagnostics. Acceptance: read `distribution-clearance.json`; its only diagnostics key is `knowledge/diagnostics/` with `{"mode": "region"}`.
- S2 — `knowledge/` is not itself a directory root. Exact requirement: just use this knowledge/diagnostics. Acceptance: read `distribution-clearance.json`; it has no `knowledge/` directory-root key.
- S3 — The format definition classifies `knowledge/diagnostics/` as a region directory root. Acceptance: read `distribution-clearance.definition.md`; `knowledge/diagnostics/` is listed among region directory roots.
- S4 — Every current file under `knowledge/diagnostics/` still expands as region. Acceptance: expand the registry over the live tree; every file under `knowledge/diagnostics/` maps to region.
- S5 — Shipped sources in the work unit are only the format definition and the clearance registry. Acceptance: inspect the work-unit diff; its shipped paths are `distribution-clearance.definition.md` and `distribution-clearance.json`.

## Tasks

- T1 | S3 | delegated (format-owner prose; the definition currently forbids a diagnostics directory root and must change first) — Scribe ✍️ (Docs & Problems Manager) | in progress | commit: pending
- T2 | S1, S2 | inline (registry data edit validated mechanically; precedent `directory-root-distribution-clearance` T2) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T3 | S4, S5 | delegated (whole-suite execution belongs to the test-architecture owner; the focused registry-conformance test and the expansion equivalence probe stay coordinator-run) — Crucible 🔥 (Test Architect) | in progress | commit: pending

## Log

- L1 — Original request, verbatim: "hey help me the knowledge/diagnostics in the distribution file have 3 entries can we just use this knowledge/diagnostics, u understand?"
- L2 — Feasibility evidence (read-only). `distribution-clearance.json` currently lists three `region` file rows under `knowledge/diagnostics/`. Directory inventory: exactly those three files (`problems.md`, `symptoms.md`, `diagnostic-guidance.md`); each already carries core/project markers. Directory-root expansion is already generic (`distribution-clearance.definition.md` Directory-root records; prior features `directory-root-distribution-clearance` and `2026-11-02-architecture-directory-clearance`). `knowledge/` cannot be one root: `knowledge/agent-workflow.md` and `knowledge/release.md` are `raw`, while the other knowledge sources are `region`.
- L3 — Constraint ownership evidence: `distribution-clearance.definition.md:23` currently classifies region knowledge documents as "individually cleared `knowledge/` files, including `knowledge/diagnostics/` files" and "not a directory-root clearance". That statement is the format-owner contradiction this request retires. Scope rule `:77–:78` already permits a directory root when every file under it is intended for distribution, with automatic join of later files. No `core-sync` SKILL.md statement names these three paths as per-file-only; README payload sentences name the files as shipped content, not as registry row kinds.
- L4 — Classification evidence (ODD step 4): understanding — mechanism, current three-file inventory, mixed-mode `knowledge/` siblings, and the definition contradiction are established by L2/L3; risk — contained, because the change is reversible, deletes no data, and keeps the three current files on `region`; resumability — not resumable from request plus diff alone, because the format owner's "not a directory-root clearance" rule and the auto-join tradeoff carry the rationale. Third test fails, so the work is non-small and this record is the bootstrap write.
- L5 — 2026-11-02 — User correction, verbatim: "did u aligned how the specs should be writed?"
- L6 — Specs rewrite against `.opencode/skills/odd-workflow/SKILL.md` `### Write meaningful specifications`. Defect: S1 was a Log-style verbatim dump that also carried conversational "hey help me" / "u understand?", which belong in L1 only. S5 had no acceptance check. Rewrite: behavior-first clauses, exact requirement wording retained in S1, conversation left in Log, each spec now has an observable check. Requested outcome unchanged. Execution-review pause remains open.
- L7 — 2026-11-02 — User correction, verbatim: "the project was updated, reanalyze"
- L8 — Reanalysis after HEAD `760817f` (`docs(odd): add specification authoring procedure (#158)`). Herald 📯 (Release Manager) session `ses_e603fcc51ffeOA4LEXC8Z1g1GV`: branch `main`, working tree otherwise clean, this record still untracked. Registry, definition, and `knowledge/diagnostics/` inventory are unchanged: three `region` file rows; definition `:23` still says those files are "not a directory-root clearance"; the folder still holds exactly `problems.md`, `symptoms.md`, `diagnostic-guidance.md`. Changed prerequisite: `odd-workflow` `1.10.0` now requires one independently verifiable outcome per `S#` and one action→one observable result. Prior S1–S5 packed multiple checks into each entry, so they fail that contract. Requested outcome unchanged. Specs and task links rewritten to S1 folder root, S2 no `knowledge/` root, S3 definition classification, S4 live expansion still region, S5 shipped diff is definition + registry only. Auto-join of later files remains existing directory-root behavior, not a new spec. Execution-review pause remains open.
- L9 — 2026-11-02 — User authorization, verbatim: "approved"
- L10 — T1 S3 accepted. Scribe ✍️ (Docs & Problems Manager) session `ses_e603c073dffeVSO7mKqlE1Jktw` edited `distribution-clearance.definition.md` only. Coordinator live-read: `knowledge/diagnostics/` is listed among region directory roots at `:26`, `:34`, `:39`, `:80`. Line `:23` no longer names diagnostics files as individually cleared and no longer says "not a directory-root clearance". Payload table rows for the three files remain at `:48–:49`.
- L11 — T2 S1/S2. Coordinator edited `distribution-clearance.json`: replaced the three per-file diagnostics rows with `knowledge/diagnostics/` → `{"mode": "region"}`. Live-read: the only diagnostics key is that root; there is no `knowledge/` directory-root key; `schema` remains `1`.
- L12 — T3 S4 expansion. Executor: Cipher 🔓 (Lead Orchestrator). Recipe: `parse_clearance` → `enumerate_files_under` → `expand_clearance` on the live tree. Convenience command: `uv run --frozen python3 C:\Users\dexm7\AppData\Local\Temp\opencode\expand_diagnostics.py` (exit 0). Observed: enumerated `['diagnostic-guidance.md', 'problems.md', 'symptoms.md']`; diag_map all `region`; `all_region True`; `knowledge_root False`.
- L13 — T3 focused registry-conformance. Command: `uv run --frozen --group dev pytest .opencode/skills/core-sync/scripts/core_sync_pkg/domain/test_clearance_metadata.py -q`. Exit 0. Observed: `31 passed in 2.12s`.
- L14 — T3 whole suite. Crucible 🔥 (Test Architect) session `ses_e603a1206ffehZOGyCNhTkEW08`. Command: `uv run --frozen --group dev pytest -q`. Exit 0. Observed: `925 passed, 6 skipped in 8.75s`. Execution result only; no test-file architecture review assigned.
