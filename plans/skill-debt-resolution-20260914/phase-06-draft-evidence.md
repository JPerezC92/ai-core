# Phase 6 — Produce real draft evidence

> **Owner:** Herald 📯 (Release Manager) + Cipher 🔓 (Lead Orchestrator)
> **Pre:** Phases 1-5 pass; the user separately authorizes the checkpoint commit; no push, PR, or merge is authorized by that approval.
> **Reads:** current branch status/diff; `plans/skill-debt-resolution-20260914/plan.md` Context; `.opencode/skills/git-pr/SKILL.md`; `.gitignore`; `knowledge/debt.md` DEBT-001/002
> **Writes:** Git checkpoint commit containing reviewed implementation plus the active Plan 2 artifacts; `pr-draft.md` only

## Steps

1. Stop and obtain explicit user authorization for Herald's checkpoint commit. Do not infer it from Plan 2 execution approval.
2. Cipher evaluates and hands Herald the complete gate packet: stash/collision pass, Bastion/Vault/Sentinel results, no dependency-manifest diff, and exact intended staged paths.
3. Herald uses `git-commit` artifacts, stages only approved implementation/story/active-plan paths, commits without push, and returns the immutable checkpoint SHA. No PR is created.
4. Cipher invokes the updated `git-pr` skill on the now-ahead branch; the skill writes only `pr-draft.md` and must discover `plans/skill-debt-resolution-20260914/plan.md` through `plans/*/plan.md`.
5. Verify the generated Summary states the plan Context's why: user-directed DEBT-002/003 resolution plus DEBT-001's same-skill trigger; a changed-file-only summary does not pass.
6. Verify all non-possessive Herald mentions in `git-pr/SKILL.md` carry `(Release Manager)` and record literal counts/locations.
7. Preserve `pr-draft.md` as ignored temporal evidence for Phase 7; do not push or open a PR.

## Output

- **Artifact:** Checkpoint commit SHA and `pr-draft.md` evidence report.
- **Schema / shape:** User authorization evidence; exact SHA; discovered subfolder plan path; quoted Context-derived draft text; mention sweep; no push/PR/merge.

## Verify commands

| Executor | Command |
|---|---|
| Herald 📯 (Release Manager) | `git rev-list --count origin/main..HEAD` |
| Cipher 🔓 (Lead Orchestrator) | `python3 .opencode/skills/plan-enforce/scripts/validate_plan.py plans/skill-debt-resolution-20260914 --stories user-stories` |

## Gate

- ⬜ User explicitly authorizes and Herald creates one checkpoint commit without push or PR.
- ⬜ A real git-pr draft run finds the subfolder plan and its Summary contains the Context's why.
- ⬜ DEBT-001/002 resolution evidence is complete and screenshot-ready for the clearing release handoff.

## Abort conditions

- Halt without explicit checkpoint-commit authorization.
- Halt if the plan is archived/missing before the draft run, the branch is not ahead of `main`, or the draft omits Context motivation.
- Halt on any push, PR-create, PR-edit, or merge request; each requires its own later authorization and merge is user-only.
