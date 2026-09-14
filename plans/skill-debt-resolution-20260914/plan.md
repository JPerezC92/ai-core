# Plan — Git PR and model-skill debt resolution

> **Status:** active
> **Started:** 2026-09-14 04:09
> **Subject:** resolve DEBT-001/002/003 with verified git-pr context discovery and typed op-model records
> **Layout:** subfolder pattern

## Context

- Prompted by: the user directed that DEBT-002 and DEBT-003 be fixed; the debt register requires DEBT-001 to ship in the next change touching `git-pr`, so all three debts must clear together.
- Goal: correct `git-pr` plan discovery and roster wording, type the `op-model` record boundary without behavior drift, verify both skills, and retire only evidence-cleared debt entries.
- Outcome: `git-pr` uses subfolder-plan Context in an actual draft run, `op-model` has a typed record contract with preserved behavior, and DEBT-001/002/003 leave the open-debt register in their clearing release.

## Goals

- ⬜ **G1:** `git-pr` discovers both `plans/*.md` and `plans/*/plan.md`, an actual draft run uses subfolder-plan Context, and every non-possessive Herald mention includes `(Release Manager)`.
  - Done when: DEBT-001 and DEBT-002 resolution criteria are reproduced with a generated draft and a complete mention sweep.
- ⬜ **G2:** `op-model/scripts/models.py` declares a `TypedDict` for model records, types `_num`'s parameter, and uses that record type throughout without changing parsing, matching, grouping, or output behavior.
  - Done when: deterministic behavior checks pass and Bastion 🧱 (Backend & Scripts Architect) returns `[PASS]`.
- ⬜ **G3:** `knowledge/debt.md` retains only open debt; DEBT-001, DEBT-002, and DEBT-003 are removed after their criteria pass, with the eventual commit/PR handoff carrying the resolution evidence required by the register.
  - Done when: all three headings are absent, register rules remain unchanged, and the release evidence checklist is explicit.
- ⬜ **G4:** The two new durable feature stories, programming plan, modified skills, and Python script pass plan/story validation, Sentinel, Vault, and all applicable script architecture checks.
  - Done when: no story criterion remains unresolved at plan completion and all required gates return `[PASS]`.

## Current state

| Area | Current | Evidence |
|---|---|---|
| `git-pr` plan context | Step 3 checks only `plans/*.md`; subfolder plans are missed. | `knowledge/debt.md` DEBT-001; `.opencode/skills/git-pr/SKILL.md:42-45` |
| `git-pr` roster mentions | Three non-possessive Herald mentions omit `(Release Manager)`. | `knowledge/debt.md` DEBT-002; `.opencode/skills/git-pr/SKILL.md:85,157,185` |
| `op-model` types | `_num` has an untyped parameter; record dictionaries are untyped. | `knowledge/debt.md` DEBT-003; `.opencode/skills/op-model/scripts/models.py:52,79,90,103` |
| Durable stories | No user story defines either skill's current feature behavior. | `user-stories/index.md` |

## Behavior change

| Goal | Before | After | Interface contracts | Do-not-break |
|---|---|---|---|---|
| G1 | Step 3 searches only `plans/*.md`, so subfolder-plan Context can be omitted; three non-possessive Herald mentions omit the role. | Step 3 searches `plans/*.md` and `plans/*/plan.md`; a real draft proves Context use; all Herald mentions carry `(Release Manager)`. | `pr-draft.md` output shape, title authority, and test-evidence contract unchanged. | Read-only drafting boundary, unchecked test-plan contract, immutable-head evidence contract, and no-PR-mutation rules. |
| G2 | `_num`'s parameter is untyped; structured model records are untyped `dict`. | `ModelRecord` is a `TypedDict` used by `parse_records`, `matches`, and grouping; `_num` accepts `object`. | `models.py` CLI, JSON-lines record schema, and exit codes unchanged. | Parsing, malformed-block skipping, normalization, matching, grouping, sorting, and no-match behavior. |
| G3 | DEBT-001, DEBT-002, and DEBT-003 remain open. | The same release that meets their criteria deletes all three entries and carries evidence forward. | `knowledge/debt.md` entry format and rules unchanged. | Unrelated register content and all other open debt entries. |
| G4 | Neither skill has a dedicated durable story. | Two active stories define and verify both features. | `user-stories/index.md` remains the structural reference point. | Existing stories and their index rows. |

## Design decisions

- Keep `git-pr` and `op-model` implementation in separate phases so the documentation-only and Python changes have independent gates.
- Bump `git-pr` `1.3.0` to `1.3.1` and `op-model` `1.0.0` to `1.0.1`; both are compatible corrections, not new public capabilities.
- Add no test file or dependency for the annotation-only Python change; use deterministic import/parse/match/group/output checks plus Bastion audit. Crucible is not applicable unless execution adds or edits a test file.
- Verify DEBT-001 with a real `git-pr` draft only after the user authorizes a checkpoint commit that puts the branch ahead of `main`; do not create, push, or merge a PR during that phase.
- Delete debt entries only after implementation and specialist evidence exists; preserve the register rules byte-for-byte.
- Reduction pass: merge final story reconciliation and debt retirement into one phase; keep Bastion, Vault, and Sentinel phases separate because their rulebooks and authority differ.

## Goal-to-story trace

| Goal | Story | Acceptance coverage |
|---|---|---|
| G1 | `user-stories/git-pr-drafting.md` | Dual plan discovery, Context-grounded draft, roster mention conformance |
| G2 | `user-stories/op-model-configuration.md` | Typed record contract and behavior preservation |
| G3 | Plan Context/Goals | Register retirement is process evidence, not feature behavior |
| G4 | Both stories | All criteria reconciled with specialist evidence |

## Phase index — dispatch table

| # | Phase | Owner | Runbook | Output | Goals |
|---|---|---|---|---|---|
| 1 | Correct `git-pr` | Forge 🔨 (Implementer) | `phase-01-forge-git-pr.md` | Updated `git-pr` skill and pending story | G1, G4 |
| 2 | Type `op-model` records | Forge 🔨 (Implementer) | `phase-02-forge-op-model.md` | Updated script, skill, and pending story | G2, G4 |
| 3 | Audit Python architecture | Bastion 🧱 (Backend & Scripts Architect) | `phase-03-bastion.md` | Bastion gate response | G2, G4 |
| 4 | Audit skill quality | Vault 🔐 (Catalog Steward) | `phase-04-vault.md` | Vault gate response for both skills | G1, G2, G4 |
| 5 | Audit plan and story surfaces | Sentinel 🛡️ (Quality Guardian) | `phase-05-sentinel.md` | Sentinel pre-retirement gate response | G4 |
| 6 | Produce real draft evidence | Herald 📯 (Release Manager) + Cipher 🔓 (Lead Orchestrator) | `phase-06-draft-evidence.md` | Authorized checkpoint commit plus `pr-draft.md` evidence | G1, G3 |
| 7 | Retire debts and reconcile stories | Cipher 🔓 (Lead Orchestrator) + Sentinel 🛡️ (Quality Guardian) | `phase-07-retire-and-audit.md` | Cleared register, verified stories, final Sentinel gate | G1, G2, G3, G4 |

## Critical files / tools

- `.opencode/skills/git-pr/SKILL.md`
- `.opencode/skills/op-model/SKILL.md`
- `.opencode/skills/op-model/scripts/models.py`
- `knowledge/debt.md`
- `user-stories/git-pr-drafting.md`
- `user-stories/op-model-configuration.md`
- `user-stories/index.md`
- `.opencode/skills/plan-enforce/scripts/validate_plan.py`
- `pr-draft.md` (ignored, temporal verification artifact)

## Verification

- [x] Phase 1: both plan-layout patterns and all corrected Herald mentions are present; `git-pr` remains a valid OpenCode skill.
- [x] Phase 2: `ModelRecord` and `_num` annotations are present and deterministic behavior checks preserve the output contract.
- [x] Phase 3: Bastion returns `[PASS]` for the final Python script.
- [x] Phase 4: Vault returns `[PASS]` for both modified skills and their patch versions.
- [x] Phase 5: Sentinel returns `[PASS]` for active plan/story/index surfaces before debt retirement.
- ⬜ Phase 6: an authorized checkpoint commit enables a real `git-pr` run whose draft summary uses this subfolder plan's Context.
- ⬜ Phase 7: DEBT-001/002/003 are removed, all story criteria are `✅`, final Sentinel returns `[PASS]`, and plan validation exits 0.

## Out of scope

- Plan 1 identity files: `.opencode/agents/warden.md`, `.opencode/skills/migrate-core-to-project/SKILL.md`, and `user-stories/aicore-adoption-sync.md`; preserve their existing uncommitted changes.
- New dependencies, manifests, lockfiles, CI, application code, or CodeRelay changes.
- Behavioral redesign of model discovery, provider choice, config editing, PR creation, or test-evidence policy.
- Any accepted debt other than DEBT-001, DEBT-002, and DEBT-003.
- Push, PR creation, or merge without separate explicit user authorization; merge is user-only.

## Pending

- [waiting for] User authorization to execute Plan 2; plan creation itself does not authorize implementation.
- [waiting for] During Phase 6 only, explicit user authorization for Herald's checkpoint commit; no push or PR is implied.

## Resolved decisions

- 2026-09-14 — The user directed two sequential plans: non-programming identity work first, programming debt work second.
- 2026-09-14 — DEBT-001 joins DEBT-002 because its register entry requires shipment in the next change touching `git-pr`.
- 2026-09-14 — The user authorized creating this plan and its stories but explicitly withheld execution.
- 2026-09-14 — Sentinel Phase-5 judgment calls dispositioned: the Behavior-change table was aligned to the canonical programming columns; completed phase-verification items are marked; G3 traces to the plan's Context/Goals because debt-register retirement is process evidence the story template forbids as a feature criterion (documented exception to the story-trace rule).
