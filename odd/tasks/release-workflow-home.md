# Release workflow home

> **Status:** closed
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-10-29
> **Closed:** 2026-10-29
> **Objective:** Give the release workflow one home, keep ODD free of it, and inject that home in `instructions` only as a replacement, not a second copy.
> **Branch:** `docs/release/workflow-home`
> **Delivery:** single serialized documentation work unit; forecast 180 authored lines (generated files excluded); running count 1 work-unit commit `eeeef0c` plus this close-record commit; slice: new home, move packet out of ODD, pointers, config inject, clearance
> **Runner:** `uv run --frozen python3 .opencode/skills/odd-workflow/scripts/validate_feature.py odd/tasks/release-workflow-home.md` and `uv run --frozen python3 .opencode/skills/op-skill-creator/scripts/check_markdown_text.py --policy knowledge/unicode-policy.json odd/tasks/release-workflow-home.md knowledge/release.md knowledge/agent-workflow.md AGENTS.md .opencode/skills/odd-workflow/SKILL.md .opencode/skills/odd-workflow/references/_checklist.md`

## Specs

- S1 — User requirement, verbatim: "go" on the proposal: one home `knowledge/release.md` for the release workflow; move `### PR release readiness` and `### Post-review finding actions` out of `knowledge/agent-workflow.md` and leave a pointer; do not copy Herald, Inquisitor, or git-pr procedures into the new home.
- S2 — User requirement, verbatim: "this should be included in instrction opencode config too rigth?" Add `knowledge/release.md` to `opencode.jsonc` `instructions` **instead of** leaving that law in the protocol file, not as well as. Do not inject Herald, Inquisitor, `git-pr`, or the cleanup preflight skill.
- S3 — User requirement, verbatim: "in agent we need to add something taht explain how should be organized our workflow guidelines". Strengthen `knowledge/agent-workflow.md` `### Keep files small`: a distinct workflow does not attach to the ODD protocol and does not live in an agent runtime. `AGENTS.md` points at that organization rule; it does not restate a flow table.
- S4 — `AGENTS.md` is a pointer to `knowledge/release.md`, not a release rulebook. Standing merged-branch cleanup after proven merge lives in `knowledge/release.md` `project` (evidence pointer `odd/tasks/verified-merged-branch-cleanup.md` L2). Do not re-ask. `SAFE_TO_CLEAN` remains evidence, not that grant. Leave `### Merged-branch cleanup preflight` as the command binding.
- S5 — Live consumers of the moved headings (odd-workflow skill, checklist Delivery) become pointers to `knowledge/release.md`. Do not restate the packet. New file is region-cleared like other knowledge documents. No copy of step 8, review procedure, or PR-body format. No second tracker.

## Tasks

- T1 | S1, S3, S4, S5 | inline (new shared knowledge file plus ODD extract; one writer) — Cipher 🔓 (Lead Orchestrator): create `knowledge/release.md`, move the two headings out of `knowledge/agent-workflow.md`, strengthen Keep files small | done | commit: eeeef0c
- T2 | S2, S3, S4, S5 | inline (same serialized writer; AGENTS, config, skill, checklist, clearance share the new home) — Cipher 🔓 (Lead Orchestrator): pointer consumers, `instructions` replacement inject, clearance row | done | commit: eeeef0c
- T3 | S1, S2, S3, S4, S5 | delegated (independent semantic review) — Sentinel 🛡️ (Quality Guardian): no competing copies, ODD not a junk drawer, inject is replacement not extra copy | done | commit: eeeef0c
- T4 | S2, S5 | inline (coordinator validation) — Cipher 🔓 (Lead Orchestrator): runner, accept, close after work-unit commit | done | commit: eeeef0c

## Log

- L1 — User request, verbatim: "go"
- L2 — 2026-10-29 prior correction, verbatim: "i am talking about taht  but be critical and not compliant , and this should be included in instrction opencode config too rigth?"
- L3 — Classified non-small: new shared knowledge file, ODD extract, config inject, clearance. Sole bootstrap write is this record.
- L4 — Execution-review was the accepted proposal (one home, move not copy, inject instead of as well as). User authorized go. Implementation follows in this authorized scope.
- L5 — 2026-10-29 T1/T2 authored: `knowledge/release.md` created; ODD PR headings replaced by pointer; Keep files small forbids attaching new flows to ODD; AGENTS 3.2.3 pointer; `instructions` adds `knowledge/release.md`; skill 1.8.2 and checklist Delivery are pointers; clearance region row. T3 Sentinel 🛡️ (Quality Guardian) sentinel-1 `[PASS]`, zero findings. Validator `ok`. Markdown check exit 0, no diagnostics. Work-unit commit `eeeef0c8ada308378b586b5f27cc154ee86229c8` (short `eeeef0c`) on `docs/release/workflow-home`.
- L6 — Close: T1–T4 done against `eeeef0c`. Release home is `knowledge/release.md`; ODD points; `instructions` injects that home with the other two, not Herald/Inquisitor/git-pr. Deferred: none. Push/PR not claimed.
