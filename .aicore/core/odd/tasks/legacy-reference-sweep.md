# Legacy reference sweep

> **Status:** closed
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-10-23
> **Closed:** 2026-10-23

## Specs

- S1 — Every operational new-work pointer in `AGENTS.md`, `knowledge/agents.md`, and `.opencode/agents/*.md` points to `odd/tasks/<feature-name>.md` and the `odd-workflow` skill.
- S2 — References that exist only for migration are labeled legacy, not active.
- S3 — Historical records in `knowledge/diagnostic-system-design.md` and `docs/architecture/history/` keep their historical status and are not rewritten as current.
- S4 — The sweep is bounded to the named source roots; `plans/`, `research/`, `output/`, and history are excluded.
- S5 — Every disposition is recorded in this feature document's Log.

## Tasks

- T1 | S1, S4 | Inventory operational references in `AGENTS.md`, `knowledge/agents.md`, `forge.md`, `bastion.md`, `herald.md`, `sentinel.md`, `README.md` | done | commit: ae234b2eaed7ca2a64ae836a9328dc5f80fbfc1b
- T2 | S2, S3 | Classify each hit as retarget, legacy label, or historical | done | commit: ae234b2eaed7ca2a64ae836a9328dc5f80fbfc1b
- T3 | S1, S2 | Apply the minimal edits | done | commit: ae234b2eaed7ca2a64ae836a9328dc5f80fbfc1b
- T4 | S5 | Re-sweep and record the disposition | done | commit: ae234b2eaed7ca2a64ae836a9328dc5f80fbfc1b

## Log

- L1 — "ok"
- L2 — Scope: operational references only; legacy plans, research, output, and historical records are excluded from rewriting.
- L3 — Inventory found active plan/story references in `AGENTS.md` (reuse guide), `knowledge/agents.md` (Sentinel scope and Cipher ownership), `forge.md`, `bastion.md`, `herald.md`, `sentinel.md`, and `README.md`.
- L4 — Intended dispositions: `AGENTS.md` reuse guide retargeted to `odd/tasks/`; shared story adoption labeled legacy; version rule uses the feature Log. `knowledge/agents.md` Sentinel scope includes `odd/tasks/`; Cipher owns `odd-workflow`; legacy plan/story checks labeled. `forge.md` and `bastion.md` use the active feature document or assignment instead of a plan `## Writes` manifest. `herald.md` plan lifecycle labeled legacy; new work closes in place. `sentinel.md` adds `odd/tasks/` and a feature-document consistency check. `README.md` labels story/plan adoption as legacy migration.
- L5 — Re-sweep: remaining `plan-enforce`, `plans/`, and `user-stories/` hits are the intentional threshold in `AGENTS.md`, labeled legacy migration, or historical design records.
- L6 — Initial close missed residual plan pointers in `forge.md` and `bastion.md`, the `AGENTS.md` execution-review and dispatch wording, and the story Proof. Audit-7 found them; the index link was present but inserted inside the table.
- L7 — Fixed the residual pointers, repointed the story Proof to S7–S10, and moved the index note after the table. Audit-8 then found the unlabeled Herald plan-staging line and incomplete sweep accounting; both are fixed.
- L8 — Final re-sweep is clean: no unlabeled active new-work pointer remains. The only `plans/` lifecycle text is explicitly legacy (Herald).
- L9 — Close: independent audit-9 PASS, no findings. The feature is closed.
- L10 — Recorded the delivery commit for completed tasks: PR #78 merge commit `ae234b2eaed7ca2a64ae836a9328dc5f80fbfc1b`.
