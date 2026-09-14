# Phase 5 — Audit plan and story surfaces

> **Owner:** Sentinel 🛡️ (Quality Guardian)
> **Pre:** Bastion and Vault return `[PASS]`; debt entries remain open pending Phase 6 evidence.
> **Reads:** all files under `plans/skill-debt-resolution-20260914/`; `user-stories/index.md`; `user-stories/git-pr-drafting.md`; `user-stories/op-model-configuration.md`; `knowledge/debt.md`; `.opencode/skills/git-pr/SKILL.md`; `.opencode/skills/op-model/SKILL.md`
> **Writes:** all files under `plans/skill-debt-resolution-20260914/`; `user-stories/index.md`; `user-stories/git-pr-drafting.md`; `user-stories/op-model-configuration.md`

## Steps

1. Audit every active plan and story line against Sentinel's full rulebook and the plan consistency checklist.
2. Verify story title/status rows mirror the index, goals trace acceptance criteria, and pending criteria remain valid while the plan is active.
3. Verify the plan preserves the user-only merge boundary and requires explicit user authorization before Phase 6's checkpoint commit.
4. Verify debt retirement is gated on all original resolution criteria and that no register entry is removed early.
5. Apply only authorized mechanical fixes within Writes; return `[PASS]` only after all findings are resolved.

## Output

- **Artifact:** Sentinel pre-retirement gate response in the phase handoff.
- **Schema / shape:** `[PASS]` or `[FAIL]`, audited paths, fixes, judgment calls, and exact evidence.

## Verify commands

| Executor | Command |
|---|---|
| Cipher 🔓 (Lead Orchestrator) | `python3 .opencode/skills/plan-enforce/scripts/validate_plan.py plans/skill-debt-resolution-20260914 --stories user-stories` |

## Gate

- ⬜ Sentinel returns `[PASS]` and the plan validator exits 0.

## Abort conditions

- Halt if any story/index mismatch, stale criterion, unsupported debt claim, or user-authority violation remains.
