<!-- core:begin -->
# User story — agent-workflow-navigation

> **Created:** 2026-10-21
> **Title:** Agent workflow navigation
> **Status:** active
> **version:** 1.0.0
> **Epic:** core-governance
> **Affected areas:** `AGENTS.md`, `knowledge/agent-workflow.md`, `knowledge/agents.md`

## Persona

- A maintainer delegating requests who needs clear authority, critical assessment, and actionable feedback.

## Goal

- **G:** Agents locate governing sources, challenge unsupported conclusions, and report actionable outcomes without changing authority.
  - Done when: owners are discoverable, premises are evidence-checked, feedback is clear, and conflicts are routed without bypassing safeguards or expanding scope.

## Scenario

- A request arrives: identify its governing sources before acting.
- A user or subagent premise lacks support: explain evidence, uncertainty, and the recommended next action.
- A conflict appears: identify its owners and obligations, stop unresolved affected action, and propose a disposition.
- An update or report is due: give clear feedback using its applicable format.

## Acceptance criteria

- ⬜ **AC1 — Discoverable authority:** Before acting on a request, an agent can find the governing behavioral requirements, engineering conventions, procedure, and execution boundaries. Requirements remain distinct from current verification evidence, and discovering a rule or approval does not grant execution authority.
- ⬜ **AC2 — Critical assessment:** Unsupported user or subagent conclusions are challenged with evidence. Established facts, interpretations, uncertainty, and missing evidence are distinguished; accessible facts are investigated before requesting a genuinely unresolved user decision.
- ⬜ **AC3 — Clear ordinary feedback:** Ordinary recurring feedback clearly states the applicable status, evidence, impact, recommendation, next action, and any decision needed. Specialized audit, incident, and PR formats remain governing rather than being replaced by the ordinary envelope.
- ⬜ **AC4 — Encountered conflicts:** A conflict identifies the opposing obligations, their authority and responsible owner, impact, and disposition. An unresolved conflict stops affected action; unrelated work is not silently expanded, and mandatory safeguards or necessary touched-file rework are not deferred merely because correction is complex.

## Proof

- AC1 → `knowledge/agent-workflow.md` `Find the governing source` · written, unverified
- AC2 → `knowledge/agent-workflow.md` `Assess the request` · written, unverified
- AC3 → `knowledge/agent-workflow.md` `Report an outcome` · written, unverified
- AC4 → `knowledge/agent-workflow.md` `Handle a conflict` · written, unverified

## Constraints

- Existing role, permission, approval, and workflow boundaries remain governing — because navigation grants no authority.
- Existing stories, policies, procedures, and conventions retain their responsibilities — because entry guidance must not duplicate rulebooks.
- Shared contracts change only at their authorized source through the existing distribution workflow — because destination-local outcomes cannot override protected shared requirements.
<!-- core:end -->

<!-- project:begin -->
## Approval record

- 2026-10-21 — After catalogue/collision review and the four-criterion preview, the user selected “Approve CREATE (Recommended)”. This approves contract/plan preparation, not runtime implementation or release.

## Local evidence

Constructed walkthroughs, not live runs, against the four guide sections: unsupported premise and bad subagent `[PASS]` are challenged; story/implementation conflicts stop affected work; unrelated defects are routed; required architecture rework is not deferred; ordinary updates keep specialized PR format; stale `[PASS]` needs current snapshot evidence.

Root rewrite from SHA256 `06bf5fcc895e61fe59f4f37556a131c59effbc8c5189756ca8e8e0b9289b95cf`: user-only `question` and “never silently infer” retained; always-ask-on-ambiguity translated to investigate first; required workflow read added. Other root obligations unchanged.

Identified observations, not live release: F03 no-audit probe was exit 0, then exit 1 missing-audit after the common `check_audit_gate` path. Skill gate `repair-vault-review-1` and runtime gate `repair-sentinel-runtime-2` `[PASS]`. Suite 27 fails were core-sync/op-model ids, not plan-enforce. DEBT-011/012 and G remain unclaimed.

## Revision tracking

- Guide, ADR, clearance, and root pointer are written. AC1–AC4 stay pending until independent acceptance and matching delivery history. No passing result or matching reference is invented.

## Change log
<!-- project:end -->
