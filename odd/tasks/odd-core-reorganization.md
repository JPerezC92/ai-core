# ODD core reorganization

> **Status:** closed
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-10-23
> **Closed:** 2026-10-23

## Specs

- S1 — ODD is the core workflow: Authorize, Explore, Resolve uncertainty, Classify, Track before the first write, Implement, Close.
- S2 — One feature document per feature at `odd/tasks/<feature-name>.md`, with `## Specs`, `## Tasks`, and `## Log`.
- S3 — Track before the first write for non-trivial work; read-only requests stay read-only; the existing plan-enforce threshold remains the authority.
- S4 — Every repeatable artifact has exactly one template; create by copying the template, never by research.
- S5 — No second tracker, no Engram mirror, and no per-request context injection.
- S6 — Close reports the verified outcome, every failed or pending check, and the next step.
- S7 — Discoverable authority: before acting, an agent can find the governing requirements, conventions, procedure, and execution boundaries; requirements stay distinct from current evidence; discovering a rule does not grant execution authority.
- S8 — Critical assessment: unsupported conclusions are challenged with evidence; facts, interpretations, uncertainty, and missing evidence are distinguished; accessible facts are investigated before a user-only question.
- S9 — Clear ordinary feedback: status, evidence, impact, recommendation, next action, and decision needed; specialized audit, incident, and PR formats remain governing.
- S10 — Encountered conflicts: identify the opposing obligations, their authority and owner, impact, and disposition; stop affected action; do not silently expand unrelated work or defer mandatory safeguards.

## Tasks

- T1 | S1, S2, S4 | Core entry, `odd-workflow` skill, feature template, checklist, `AGENTS.md` pointer | done | commit: pending
- T2 | S3, S5, S6 | First feature document and story supersession | done | commit: pending
- T3 | S7, S8, S9, S10 | Story migration, legacy routing, walkthrough | done | commit: pending

## Log

- L1 — "write a completely new plan, dont touch the old foundation plan file, the new goal is to confiugure the most near organic driven development , just inside the project we willl not touch the harness"
- L2 — "hey i think i wasent clear ODD if being our new CORE u understand what means that?"
- L3 — "u forgot the histories? as i saw it our histories files are like the features files, u resear hed how ODD structure their histories?"
- L4 — "hey we are reorganizing to achieve the most nearest to ODD dont try to preserve old things"
- L5 — "i agreed and all files that will be repeatable should become a template i dont want to tell future agent to need a new research to create a new file u understand? this should apply on future files"
- L6 — "FOCUS ON THE ODD IMPLEMENTATION WORKFLOW I ALREADY TOLD U WE ARE REORGANIZING THE PROJECT"
- L7 — Decisions: ODD is the core; the feature document is the single record; the template rule is mandatory; no second tracker; no context injection; the legacy story is superseded, not deleted.
- L8 — The core entry, feature template, and first feature document are written. The `odd-workflow` skill, checklist, `AGENTS.md` pointer, and story supersession are next.
- L9 — Implemented: the ODD core entry, `odd-workflow` skill, checklist, `AGENTS.md` pointer, story and index supersession, legacy skill notices, README structure map, and clearance row.
- L10 — The legacy `plans/odd-project-adoption-20261022/` plan remains a migration input; this feature document is the active record.
- L11 — Constructed walkthrough: a new feature copies `odd/tasks/_template.md`; this document is the worked example with Specs S1–S10, Tasks T1–T3, and Log L1–L11. Pending checks: independent audit and legacy plan retirement. Next step: verify the template on the next feature.
- L12 — The legacy foundation plan `plans/agent-workflow-foundation-20261021/plan.md` and the legacy adoption plan `plans/odd-project-adoption-20261022/plan.md` stay untouched. Their rules and pending goals are not binding for the ODD workflow; this feature document is the active record.
- L13 — Second live feature `odd/tasks/legacy-reference-sweep.md` was created from `odd/tasks/_template.md` and run spec → task → log → close. The template is proven on real work.
- L14 — Audit-7 found residual plan pointers in `forge.md` and `bastion.md` and broken story Proof; the sweep feature fixed them. No re-audit was run.
- L15 — Close: independent audit-9 PASS, no findings: ODD core, template, skill, `AGENTS.md` pointer, story supersession, and reference sweep verified. The reorganization is closed; legacy migration remains future work.
