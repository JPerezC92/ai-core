# Phase 1 — Close-out join text

> **Owner:** Forge 🔨 (Implementer)
> **Pre:** Confirmed G1/G2; approved AC40/AC41; empty stash; Cipher 🔓 (Lead Orchestrator) authorized execution on a later turn after independent planning `[PASS]`
> **Reads:** `user-stories/plan-lifecycle-governance.md` AC40 AC41 Constraints; current bytes of the three write paths; this runbook
> **Writes:** `.opencode/skills/plan-enforce/SKILL.md`; `.opencode/skills/plan-enforce/references/_lifecycle-contract.md`; `.opencode/skills/plan-enforce/references/_consistency-checklist.md`

## Assignment and resources

- Workflow / task / instance: `close-out-before-done-claim-20261022` / phase-01 / `phase-01-forge`
- Accepted predecessors / input identities: none besides the confirmed plan and approved story
- Permitted resource access: write only the three **Writes** paths; read story and plan; no Git
- Ownership / output destination: Forge 🔨 (Implementer) is the sole writer of those three files
- Required gates / continuation / join owner: after edits return `AWAITING_REVIEW`; Cipher 🔓 (Lead Orchestrator) dispatches Sentinel 🛡️ (Quality Guardian); Cipher 🔓 accepts
- Capacity allocation / accounting owner: Cipher 🔓 (Lead Orchestrator)
- Readiness / serialization evidence: exclusive writes; no parallel writer on these files

## Steps

1. In `SKILL.md` `#### Resume (completion)` and `### Plan lifecycle rules` (or the equivalent loaded-contract pointers): state that Cipher 🔓 must not report the plan complete or its PR/release done until goal checkmarks, Outcome, completed metadata, archive, and filesystem verification have occurred; an opened/reviewed/merged PR or shipped status does not replace that sequence (AC40).
2. In the same skill surfaces: if close-out was skipped after a ship report, restore the still-active plan, run that same pre-release sequence, then archive; do not add a post-merge archive step (AC41).
3. In `_lifecycle-contract.md` `## Resume (completion)` and the lifecycle rows `Audits pass, release PR requested` and `User confirms PR merge`: the same AC40 join and AC41 repair; keep “no post-merge archive step” on the happy path.
4. In `_consistency-checklist.md` completion analysis: a done-claim without that close-out is a failed completion, not a missing nicety.
5. Preserve all existing AC14/AC23/AC34 obligations; do not retokenize core with source runners; do not edit `user-stories/` or `knowledge/debt.md`.
6. Re-read the three files; return `AWAITING_REVIEW` with changed paths.

## Output

- **Artifact:** the three **Writes** paths
- **Schema / shape:** each contains an observable AC40 done-claim join and AC41 repair rule; post-merge still does not archive; no new Git/release authority
- **Attribution / identities:** `phase-01-forge`; consumed AC40/AC41 text
- **Parent handoff:** `AWAITING_REVIEW`; no Git; resource-use ceased on those files after the return

## Verify commands

| Executor | Command |
|---|---|
| Cipher 🔓 (Lead Orchestrator) | `uv run --frozen python3 .opencode/skills/plan-enforce/scripts/validate_plan.py plans/close-out-before-done-claim-20261022` |

## Gate

- ⬜ Each write path states AC40 (no done-claim without close-out) and AC41 (restore + same sequence; no post-merge archive)
- ⬜ Existing archive-before-release and no-post-merge-archive happy path remain
- ⬜ Sentinel 🛡️ (Quality Guardian) `[PASS]` on the three files plus this plan
- ⬜ Validator command exits 0
- ⬜ Relevant content/dependencies stayed stable for review, identities/scope are recorded, and current applicable verdicts are accepted; relevant changes invalidate affected verdicts/assignments before redispatch.
- ⬜ The parent accepted every relevant return and the combined candidate, keeping review/execution verdicts separate; no incomplete, failed, stale or still-mutating predecessor unblocks dependent work/completion.
- ⬜ If this phase ships a behavior-visible change: the affected documentation is written in the same change and reviewed against the delivered behavior (not the plan's description of it).

## Abort conditions

- Halt if a write would add a post-merge archive path or weaken archive-before-release
- Halt if story or debt files are in scope
- Stop before any out-of-assignment write/mutation or incompatible access; report `BLOCKED` to the parent. Missing current inputs/capacity/isolation or stale evidence blocks readiness, not permission to improvise.
