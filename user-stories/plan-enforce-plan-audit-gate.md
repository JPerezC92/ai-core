# User story — plan-enforce-plan-audit-gate

> **Created:** 2026-09-15
> **Title:** Plan-enforce plan audit gate
> **Status:** active
> **Epic:** plan-governance
> **Affected areas:** `.opencode/skills/plan-enforce/`, `user-stories/`

## Persona

- Cipher 🔓 (Lead Orchestrator), who writes plans and must not be able to skip the analysis pass or claim completion without an independent check.

## Goal

- **G:** A plan cannot drift silently and cannot reach completed without an independent audit verdict.
  - Done when: `validate_plan.py` fails genuine drift with stable finding codes and a completed plan without an `## Audit` `[PASS]` is rejected.

## Scenario

- Cipher 🔓 (Lead Orchestrator) writes a plan and runs the mechanical pass. The validator now also checks goal trace, manifest equality, verification parity, and the audit gate. Before a ready report or a Forge 🔨 (Implementer) dispatch, an independent auditor returns a verdict that is recorded in `## Audit`. A completed plan without `[PASS]` fails validation.

## Acceptance criteria

- ✅ Goal trace, manifest equality, and verification parity are enforced with `GOAL-TRACE:`, `MANIFEST:`, and `VERIFICATION-PARITY:` findings. Evidence: `validate_plan.py` `check_goal_trace`/`check_manifest_equality`/`check_verification_parity`; tests `test_goal_trace_uncited_goal_flagged`, `test_manifest_missing_phase_path_flagged`, `test_verification_parity_mismatch_flagged`.
- ✅ A completed plan requires `## Audit` with a non-empty `Auditor`, a `[PASS]` verdict, and a non-empty `Date`; unknown or `[FAIL]` verdicts fail. Evidence: `check_audit_gate`; tests `test_audit_gate_completed_without_audit_flagged`, `test_audit_gate_completed_fail_flagged`, `test_audit_gate_unknown_verdict_flagged`.
- ✅ The skill documents the loop, the independent-audit gate before a ready report or Forge 🔨 (Implementer) dispatch, the fail-closed fallback, and the pass-count report; both templates carry a compliant `## Audit` block. Evidence: `SKILL.md` Post-write self-verification loop and Independent audit gate; `references/_template.md` and `_template-programming.md`.
- ✅ The edits pass Bastion 🧱 (Backend & Scripts Architect) `[PASS]` and Crucible 🔥 (Test Architect) `[PASS]`, and the stdlib unittest suite is green at plan-enforce 1.12.0. Evidence: suite 50 tests OK; recorded gate verdicts.

## Change log

- 2026-09-15 — plan-enforce-plan-audit-gate-20260915: replaced the rejected self-declared `## Self-verification` idea with enforced mechanical drift checks plus an independent audit gate; plan-enforce advanced to 1.12.0.

## Resolved decisions

- 2026-09-15 — enforcement is split: the validator catches mechanical drift, and an independent auditor supplies the semantic verdict; a self-declared `Analysis: ok` string is not used because it verifies a claim, not the work.
- 2026-09-15 — the audit gate is enforced only at `Status: completed` so active drafting keeps validating; the skill separately blocks a ready report and Forge 🔨 (Implementer) dispatch without `[PASS]`.
