# PR release-readiness discipline

> **Status:** closed
> **Closed:** 2026-10-28
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-10-28
> **Objective:** Prevent PRs from opening or being reported complete with unactioned review findings or unverified release claims.
> **Branch:** docs/workflow/pr-release-readiness
> **Delivery:** single documentation slice; forecast 70 authored additions plus deletions, generated files excluded; actual at ad26af3 is 48 additions plus 1 deletion; no code or test harness
> **Runner:** `uv run --frozen python3 .opencode/skills/odd-workflow/scripts/validate_feature.py odd/tasks/pr-release-readiness-discipline.md`; Markdown/text-integrity check on changed docs

## Specs

- S1 — User request, verbatim: "ok then can u make a draft tast just to keep it parked ,then continue with PR fixes". Create a durable draft task now, without implementing it; continue the current PR fixes separately.
- S2 — When authorized, add a mandatory release-readiness gate before PR creation: every test-plan command and result, gate result, open task, excluded path and unverified control must be recorded; missing evidence blocks PR creation. Add a post-review finding-action table requiring disposition, owner, action and user-decision flag for every finding; a raw findings list is not an acceptable handoff. Preserve the existing single feature tracker and all current approval, permission, evidence and review gates.
- S3 — Do not implement this draft in PR #112 or claim it delivered. Implementation requires its own execution review, owner routing, tests or proportionate documentation checks, and independent semantic acceptance.
- S4 — User authorized implementation by selecting "Implement prevention discipline now". Apply the rule only to existing workflow owners: `knowledge/agent-workflow.md`, `.opencode/skills/odd-workflow/SKILL.md`, `.opencode/skills/odd-workflow/references/_checklist.md`, and the PR-findings adjudication section in `knowledge/agents.md`. Do not create a second tracker, new permission, mandatory approval ritual, or test harness. Advance the ODD skill version for the new enforceable behavior; preserve existing obligations.

## Tasks

- T1 | S2, S4 | delegated (single serialized documentation writer for the four existing workflow owners; exact paths named in S4) — Scribe ✍️ (Docs & Problems Manager) | done | commit: ad26af3
- T2 | S2, S3, S4 | delegated (independent semantic/workflow review after implementation; no edits) — Sentinel 🛡️ (Quality Guardian) | done | commit: ad26af3
- T3 | S2, S4 | delegated (skill catalog audit of the updated ODD skill; no edits) — Vault 🔐 (Catalog Steward) | done | commit: ad26af3
- T4 | S1, S2, S3, S4 | inline (coordinator validation, feature closure and actual commit evidence) — Cipher 🔓 (Lead Orchestrator) | done | commit: ad26af3

## Log

- L1 — Original request, verbatim: "ok then can u make a draft tast just to keep it parked ,then continue with PR fixes"
- L2 — 2026-10-28 parked: this record exists only to preserve the prevention task. No workflow, core, skill, PR, permission, test or source change is authorized or claimed. PR #112 fixes remain a separate active task.
- L3 — 2026-10-28 user chose "Implement prevention discipline now" from the next-action question. The parked draft is reopened for implementation; S4 bounds the change to existing workflow owners.
- L4 — 2026-10-28 execution plan: Scribe ✍️ (Docs & Problems Manager) updates the four owners; Sentinel 🛡️ (Quality Guardian) and Vault 🔐 (Catalog Steward) review; coordinator validates, commits and opens a docs-only PR. No new tracker or approval ritual; all existing gates remain binding.
- L5 — Close: 2026-10-28 implementation delivered in `ad26af3` (five files, +48/−1): mandatory pre-PR release-readiness packet and post-review finding-action table in the workflow, ODD skill, checklist and adjudication rules; ODD skill version 1.7.0. Sentinel 🛡️ (Quality Guardian) PASS after correcting Log dates/roster formatting; Vault 🔐 (Catalog Steward) PASS 25/25. Feature validator and Markdown checks passed. No test harness added; no new tracker, approval ritual or permission. PR publication remains separate.
