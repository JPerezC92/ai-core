# Plan — Close-out before done-claim

> **Status:** active
> **Started:** 2026-10-22 18:00
> **Subject:** Make plan close-out (goal marks, Outcome, archive, filesystem verify) a hard join before any done-claim for the plan or its PR/release.
> **Layout:** subfolder pattern

## Context

- Prompted by: recurrent skip after PR #76 — plan left active, goals unmarked, work treated as shipped.
- Goal: consume approved `plan-lifecycle-governance` **AC40** and **AC41** so Cipher 🔓 (Lead Orchestrator) cannot report a plan or its release/PR done without close-out, and a skipped close-out is repaired by the same pre-release sequence.
- Outcome: (empty until completion)
- Story: `user-stories/plan-lifecycle-governance.md` v1.7.0; selected AC40/AC41 only; pending history; no Change log until a matching reference.
- Disclose **DEBT-013**: false “second active plan is forbidden” reading; this plan may coexist with `plans/agent-workflow-foundation-20261021`.

## Goals

- ⬜ **G1:** A plan is not reported complete, and that plan’s release or PR is not reported done, until every confirmed goal is marked complete, Outcome is written, completed metadata is set, and the plan is archived with filesystem verification. An opened, reviewed, or merged PR, or a shipped status, does not replace that sequence.
  - Issue: Cipher 🔓 (Lead Orchestrator) treated merge/ship as done while goals stayed unmarked and the plan stayed active.
  - How: Normative skill and lifecycle text make close-out a required join before any done-claim.
  - Files: `.opencode/skills/plan-enforce/SKILL.md`; `.opencode/skills/plan-enforce/references/_lifecycle-contract.md`; `.opencode/skills/plan-enforce/references/_consistency-checklist.md`
  - Trace: AC40

- ⬜ **G2:** If close-out was skipped after the work was treated as shipped, the still-active plan is restored and the same pre-release sequence runs, then archive. Post-merge branch cleanup still does not archive.
  - Issue: Repair was improvised after the user noticed; post-merge must not grow a second archive path.
  - How: Document restore + same pre-release sequence as the only repair; keep “no post-merge archive step”.
  - Files: `.opencode/skills/plan-enforce/SKILL.md`; `.opencode/skills/plan-enforce/references/_lifecycle-contract.md`
  - Trace: AC41

## Body

| Path read | Evidence |
|---|---|
| `plan-enforce/SKILL.md` Resume (completion), Check for active plan 4–5, Plan lifecycle | Close-out exists; done-claim join is not named; one-active is resume/select, not a ban on a second plan |
| `_lifecycle-contract.md` Resume (completion); rows Audits pass / User confirms PR merge | Archive before release PR; no post-merge archive |
| `_consistency-checklist.md` Completion and findings | History/Outcome gates; no explicit done-claim sentence |
| `plan-lifecycle-governance.md` AC40/AC41 | Approved, `⬜`, unverified Proof |
| `post-merge-branch-cleanup.md` | Branch proof only |

## Documentation

| Surface | Owner | Change |
|---|---|---|
| `.opencode/skills/plan-enforce/SKILL.md` | Forge 🔨 (Implementer) | Done-claim join + skipped-close-out repair |
| `.opencode/skills/plan-enforce/references/_lifecycle-contract.md` | Forge 🔨 (Implementer) | Same obligations in lifecycle rows |
| `.opencode/skills/plan-enforce/references/_consistency-checklist.md` | Forge 🔨 (Implementer) | Analysis bullet that a done-claim without close-out fails |

## Write/delete manifest

| Action | Path |
|---|---|
| Modify | `.opencode/skills/plan-enforce/SKILL.md` |
| Modify | `.opencode/skills/plan-enforce/references/_lifecycle-contract.md` |
| Modify | `.opencode/skills/plan-enforce/references/_consistency-checklist.md` |

## Phase index — dispatch table

| # | Phase | Owner | Runbook | Output |
|---|---|---|---|---|
| 1 | Close-out join text | Forge 🔨 (Implementer) | `phase-01-forge.md` | the three modified surfaces |

## Coordination and accepted joins

- Workflow identity / coordinator: `close-out-before-done-claim-20261022`; Cipher 🔓 (Lead Orchestrator)
- Capacity / authoritative accounting owner: Cipher 🔓 (Lead Orchestrator); one Forge instance
- Task instances: `phase-01-forge` — Forge 🔨 (Implementer) writes the three paths
- Accepted dependencies / inputs: none; confirmed G1/G2; approved AC40/AC41
- Readiness / serialization: single writer; after write Sentinel 🛡️ (Quality Guardian) then Bastion 🧱 (Backend & Scripts Architect) N/A (docs only)
- Resource modes / ownership: Forge exclusive write on the three paths; no Git
- Output allocation / attribution: in-place edits on those paths
- Checkpoints / transfers: Forge returns `AWAITING_REVIEW`; Cipher dispatches Sentinel 🛡️; Cipher accepts join
- Review stability / joins: identities recorded at dispatch; content change invalidates verdicts

## Critical files / tools

- `user-stories/plan-lifecycle-governance.md` (AC40, AC41, Constraints)
- `.opencode/skills/plan-enforce/SKILL.md`
- `.opencode/skills/plan-enforce/references/_lifecycle-contract.md`
- `.opencode/skills/plan-enforce/references/_consistency-checklist.md`
- `uv run --frozen python3 .opencode/skills/plan-enforce/scripts/validate_plan.py`

## Verification

- ✅ Phase 1 output artifact exists, is valid, and its applicable gates are accepted

## Audit

- Auditor: Sentinel 🛡️ (Quality Guardian) (`sentinel-plan-1`)
- Verdict: [PASS]
- Findings: 0 blocking (mechanical naming auto-fixes on roster mentions)
- Date: 2026-10-22
- Reviewed: `plan.md` + `phase-01-forge.md`; AC40/AC41 at `user-stories/plan-lifecycle-governance.md`

## Out of scope

- Completing or cancelling `agent-workflow-foundation-20261021`
- Post-merge branch deletion changes
- Validator/script changes
- Ticking AC40/AC41 or writing a Change log before a matching reference
- Git, PR, or release
- Clearing **DEBT-013** in this plan (disclose only)

## Resolved decisions

- 2026-10-22 — User confirmed G1+G2, base template, AC40/AC41 only, two active plans allowed.
- 2026-10-22 — **DEBT-013** records the false second-active prohibition.
