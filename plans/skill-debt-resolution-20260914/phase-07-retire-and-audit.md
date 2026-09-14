# Phase 7 — Retire debts and reconcile stories

> **Owner:** Cipher 🔓 (Lead Orchestrator) + Sentinel 🛡️ (Quality Guardian)
> **Pre:** Phase 6 produces complete DEBT-001/002 draft evidence; Bastion has passed DEBT-003; Vault and Sentinel preflight have passed.
> **Reads:** `knowledge/debt.md`; Phase 1-6 outputs; `pr-draft.md`; `user-stories/git-pr-drafting.md`; `user-stories/op-model-configuration.md`; `user-stories/index.md`; all active Plan 2 files
> **Writes:** `knowledge/debt.md`; `user-stories/git-pr-drafting.md`; `user-stories/op-model-configuration.md`; all active Plan 2 files

## Steps

1. Re-read `knowledge/debt.md` fresh and compare each DEBT-001/002/003 resolution criterion to literal Phase 3, 4, 5, and 6 evidence.
2. Only if every criterion passes, delete each complete DEBT-001, DEBT-002, and DEBT-003 entry; preserve the register title, format, rules, and unrelated entries byte-for-byte. Do not add resolved markers.
3. Reconcile every pending criterion in both new stories to `✅` with concise evidence; any unmet criterion stays `❌` and blocks completion rather than remaining `⬜`.
4. Append dated story change-log entries for this plan; keep title/status mirrored in the index.
5. Build the release-evidence handoff requiring the eventual commit message and PR body to state: all three original criteria met; exact behavior/validation commands; Bastion/Vault/Sentinel verdicts; the clearing change deletes all three entries.
6. Dispatch Sentinel to audit the final register deletion, both stories, index, and all active plan files; fix only authorized mechanical issues.
7. Run the plan validator. Cipher presents the goal resume, writes Outcome, marks completed, and archives the folder before any PR is created.

## Output

- **Artifact:** `knowledge/debt.md`; two verified stories; final Sentinel gate; completed archived plan; release-evidence handoff.
- **Schema / shape:** Zero DEBT-001/002/003 headings; no `⬜`/`❌` in touched stories; `[PASS]`; validator exit 0; Outcome covers G1-G4.

## Verify commands

| Executor | Command |
|---|---|
| Cipher 🔓 (Lead Orchestrator) | `grep -c '^### DEBT-00[123]' knowledge/debt.md` |
| Cipher 🔓 (Lead Orchestrator) | `python3 .opencode/skills/plan-enforce/scripts/validate_plan.py plans/skill-debt-resolution-20260914 --stories user-stories` |

## Gate

- ⬜ Debt entries are removed only on complete evidence; register rules remain intact.
- ⬜ Both stories have no unresolved criterion and mirror the index.
- ⬜ Final Sentinel and validator pass; Outcome and archive lifecycle complete before PR creation.

## Abort conditions

- Halt and retain the corresponding debt entry if any original criterion lacks executed evidence.
- Halt on any story `⬜`/`❌`, register-rule diff, missing release-evidence item, or Sentinel finding.
- Halt before commit/push/PR/merge; those remain separate release actions and merge remains user-only.
