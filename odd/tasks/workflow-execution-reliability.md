# Workflow execution reliability

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-10-29
> **Objective:** Make ODD step reporting, scope-bounded continuation, execution-review timing, standing authorization, and finding/blocker presentation explicit and consistent.
> **Branch:** docs/workflow/workflow-execution-reliability
> **Delivery:** One documentation work-unit; forecast ~320 authored additions and ~20 deletions, excluding generated files; slice 1 = ODD protocol and presentation standard, slice 2 = root/skill/checklist pointers, slice 3 = debt correction and independent review. No code, no new tracker, no new approval.
> **Runner:** `uv run --frozen python3 .opencode/skills/odd-workflow/scripts/validate_feature.py odd/tasks`

## Specs

- S1 — Authorized outcome: implement the accepted workflow-repair proposal. Acceptance: the three presentation message types and the ODD step mapping are documented in their canonical owners; no second tracker and no eighth ODD phase are introduced.
- S2 — ODD step reporting: after each completed step, report feature/task identity, step number and name, state (`COMPLETE`, `IN PROGRESS`, `BLOCKED`, `NOT APPLICABLE`), result, evidence pointer, and next action. A skipped or inapplicable step states its reason. Acceptance: `knowledge/agent-workflow.md` → `### ODD protocol` defines the fields and transitions; examples cover no-question and not-applicable steps.
- S3 — Scope-bounded continuation: continue to the next ready task within the active authorized scope; task completion is not a stopping condition. Exhausted scope → `ALL FINISHED` with delivered scope, verification, deferred items, and next options; do not select unrelated work to avoid stopping. A genuine decision, permission, or blocker stops with the exact required user action. Acceptance: the ODD protocol and `AGENTS.md` state the same continuation boundary.
- S4 — Execution-review timing: the governing feature document exists before the first non-small mutation; after creating it or materially replanning, present Issue → Goal → How → Files plus the gate and the decision needed, then pause before implementation. Routine Log/evidence updates do not restart the pause. Creating the governing document is the sole bootstrap write. Acceptance: `AGENTS.md` and the ODD skill point to the same rule without duplicating it.
- S5 — Standing authorization: explicit authorization may be supplied once or through an applicable standing instruction; local commits remain standing-authorized; push, PR, merge, tag, release, and archive remain separately authorized; a tool-permission denial is never bypassed. Acceptance: the ODD skill's delivery boundary and the existing `AGENTS.md` local authorization agree.
- S6 — Presentation standard: distinguish findings, severity, advisory findings, blockers, checks, and decisions; standardize state emojis: ✅ complete/fixed/pass, 🟡 in progress/pending, 🚧 blocked, ⏭️ not applicable/skipped, 🔴 open, ⏸ deferred, ✖ rejected, ❌ fail/error, ⚠️ advisory, ❓ decision required; severity remains text (`HIGH`/`MEDIUM`/`LOW`), and emojis never replace the required text; keep the existing findings table and unique `Counts:` accounting; present blockers/checks separately from finding counts; use `ALL FINISHED` for completed scope and the existing compact ready-to-merge format for a clean PR. Acceptance: `knowledge/agents.md` defines the three message types, the emoji vocabulary, and examples; unresolved (open or deferred), pending, or advisory items never become a clean `[PASS]`.
- S7 — Preserve existing safeguards: Forge-only code authorship, Bastion/Crucible edit gates, independent completion review, zero-open-findings `[PASS]`, evidence discipline, debt preservation, and existing authorizations remain binding. No new engine, harness, tracker, or approval ritual. Acceptance: no competing copy of those rules is introduced.
- S8 — Correct the record: `DEBT-021`'s claim that the loop cap applied after the second `[FAIL]` is corrected because two distinct failed reviews do not satisfy the rule; the original evidence is preserved. `DEBT-019` is not recovered, and no debt is retired without its resolution criteria. Acceptance: the debt entry carries a dated correction; no debt retirement occurs in this feature.
- S9 — Verify and close: an independent semantic review by a reviewer who did not author the changes, plus the ODD validator, covers the documentation-only delivery. Acceptance: review `[PASS]` with zero open findings, validator `ok`, and actual evidence in `## Log`.

## Tasks

- T1 | S2 | delegated (ODD protocol definition; documentation owner) — Scribe ✍️ (Docs & Problems Manager) | in progress | commit: pending
- T2 | S4 | inline (root runtime spec; Cipher owns the conventions) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T3 | S3, S5 | delegated (ODD skill delivery/continuation wording; documentation owner) — Scribe ✍️ (Docs & Problems Manager) | in progress | commit: pending
- T4 | S6 | delegated (presentation standard, including the standardized emoji state markers, in the findings owner; documentation owner) — Scribe ✍️ (Docs & Problems Manager) | in progress | commit: pending
- T5 | S8 | inline (debt correction; Cipher) — Cipher 🔓 (Lead Orchestrator) | in progress | commit: pending
- T6 | S9 | delegated (independent semantic review; reviewer must not have authored the changes) — Sentinel 🛡️ (Quality Guardian) | open | commit: pending
- T7 | S1, S2, S3, S4, S5, S6, S7, S8, S9 | inline (close, validator, and commit coordination; Cipher + Herald) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending

## Log

- L1 — User request, 2026-10-29, verbatim: "now recap all the error u had and all the debts related to workflow issues, we need to solve them , analyze and propose".
- L2 — User correction, 2026-10-29, verbatim: "ok, i like your proposal but u cant just invent how u will present to me the infromation we need to standarize it like example  the infromation presentation of finding blockers advisories u need to analyze and propose how u will present to me".
- L3 — User approval, 2026-10-29, verbatim: "ok, u can procced i allow it".
- L4 — 2026-10-29 — Accepted proposal decision: three message types (progress, findings/blocked, completion); ODD step mapping; findings/blockers/checks/decisions separated; existing findings table and counts reused; no second tracker or new engine. Evidence: conversation record 2026-10-29 and the proposal accepted in L3.
- L5 — 2026-10-29 — Scope boundary: correct `DEBT-021`'s loop-cap wording, preserve its original evidence, do not recover `DEBT-019`, and do not retire any debt without its resolution criteria. The feature is documentation-only; code remediation remains deferred.
- L6 — User suggestion, 2026-10-29, verbatim: "i accept but i have a suggestions, use emojis on your message emjis are very usefull like the ✅ ❌and standarizd another if needed". Decision: standardize the emoji state vocabulary in S6 and the presentation owner; emojis mark state, not severity, and never replace required text.
- L7 — 2026-10-29 — Implementation evidence: T1/T3/T4 edited by Scribe (agent-workflow, odd-workflow skill/checklist, agents); T2/T5 edited by Cipher (AGENTS, debt). Files: `knowledge/agent-workflow.md`, `knowledge/agents.md`, `AGENTS.md`, `.opencode/skills/odd-workflow/SKILL.md`, `.opencode/skills/odd-workflow/references/_checklist.md`, `knowledge/debt.md`. Markdown text-integrity check passed; ODD validator `ok`; Sentinel independent review pending. No code or test change.
- L8 — 2026-10-29 — Sentinel review `task6/sentinel1` found 5 findings. Fixed: AGENTS pause wording (material replanning, gate, decision), ODD step examples, presentation examples, open-advisory wording, and S6 `[PASS]` wording. Re-review pending; no code.
- L9 — 2026-10-29 — Sentinel re-review `task9/sentinel1` found 2 findings: the advisory sentence still bypassed fix-first, and the `ALL FINISHED` example invented a three-file/reviewed scope. Fixed in `knowledge/agents.md`; re-review pending; no code.
