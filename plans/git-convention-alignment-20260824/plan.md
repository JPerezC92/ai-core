# Plan — Align git conventions across skills

> **Status:** active
> **Started:** 2026-08-24 18:46
> **Subject:** Align branch, commit, PR, and Herald naming with Conventional Commits in monorepos
> **Layout:** subfolder pattern

## Context

- Prompted by: type-list drift (`hotfix` versus `ci`), no branch-to-PR linkage, and incompatible two-segment Herald fallback names.
- Goal: define one commitlint-compatible convention that remains unambiguous across monorepo application boundaries.
- Outcome: the three git skills and Herald use the same types, scope grammar, and branch format.
- User story: skipped; this is a non-programming process/tooling documentation change with no feature-visible behavior.

## Goals

- ⬜ **G1:** Branch, commit, and PR skills share the commitlint type set: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, and `test`; `hotfix` is not a type.
- ⬜ **G2:** Scope rules use one kebab-case token: backend-only product apps use `app-api`, frontend-only product apps use `app-web`, split apps use those suffixes per side and `app` only when one change spans both; shared core, independent apps, and cross-cutting concerns keep their own names.
- ⬜ **G3:** A matching `type/scope/description` branch supplies commit type/scope defaults and is checked against the PR title; diff evidence wins and any mismatch is surfaced.
- ⬜ **G4:** Herald's mandatory fallback branch naming uses the same three-segment `type/scope/description` convention.
- ⬜ **G5:** Herald's hard rule for uncleared Critical/High visual findings uses an imperative instruction and preserves its raw-blocker condition.

## Body

- Replace drifted type lists and scope guidance in the three standalone git skills.
- Preserve skill responsibilities: branch-name suggests only, commit writes only `commit.txt`, PR writes only `pr-draft.md`.
- Add branch-derived defaults/checks without making a branch name override the actual diff.
- Correct Herald's two-segment fallback without changing its release authority or flow.
- Apply the user-approved imperative correction at Herald line 117 without changing the blocker condition.

## Phase index — dispatch table

| # | Phase | Owner | Runbook | Output |
|---|---|---|---|---|
| 1 | Convention alignment (G1-G5) | Cipher 🔓 (L2 Lead) | `phase-01-convention.md` | Four aligned runtime documents |
| 2 | Skill quality audit (G1-G3) | Vault 🔐 (Catalog Steward) | `phase-02-vault-audit.md` | Vault audit report |
| 3 | Agent-spec audit (G4-G5) | Sentinel 🛡️ (Quality Guardian) | `phase-03-sentinel-audit.md` | Sentinel audit report |

## Critical files / tools

- `.opencode/skills/git-branch-name/SKILL.md`
- `.opencode/skills/git-commit/SKILL.md`
- `.opencode/skills/git-pr/SKILL.md`
- `.opencode/agents/herald.md`
- `.opencode/skills/plan-enforce/scripts/validate_plan.py`

## Verification

- ☑ Phase 1 output: the four runtime documents use the approved convention with no residual `hotfix` type or two-segment Herald fallback, and Herald's visual gate is imperative.
- ☑ Phase 2 output: Vault audit passes the three skills after the scope-taxonomy remediation.
- ☑ Phase 3 output: Sentinel verifies G4-G5 after the user-approved imperative correction.

## Out of scope

- Adding commitlint, semantic-release, CI enforcement, or git hooks.
- Changing source code, dependency manifests, lockfiles, or repository branching policy beyond the documented fallback format.
- Clearing `DEBT-001`; its plan-enforce presentation-flow correction is deferred.

## Resolved decisions

- 2026-08-24 — Use the 11 types accepted by `@commitlint/config-conventional`; Conventional Commits itself requires only `feat` and `fix` and permits extensions.
- 2026-08-24 — Use `app-api` and `app-web` for one side of a split app; use `app` only when a single change genuinely spans both sides.
- 2026-08-24 — Standalone product backend and frontend apps also use `app-api` and `app-web`; `core`, `ui-kit`, and `cli` keep their canonical package or app names.
- 2026-08-24 — Branch names default commit type/scope and check PR-title consistency, but diff evidence overrides a stale or misleading branch name.
- 2026-08-24 — User requested `DEBT-001` for unreadable plan-goal presentation; it is outside this plan's scope.
- 2026-08-24 — User expanded this plan to include Sentinel's advisory at `.opencode/agents/herald.md:117`; apply the imperative correction without altering the raw-blocker condition.
- 2026-08-24 — Sentinel verified G5: the wording is imperative and retains the same raw-blocker condition.
