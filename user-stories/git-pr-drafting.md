# User story — git-pr-drafting

> **Created:** 2026-09-14
> **Title:** Pull request draft generation
> **Status:** active
> **Epic:** developer-tooling
> **Affected areas:** `.opencode/skills/git-pr/`, `plans/`, `pr-draft.md`

## Persona

- A maintainer preparing a reviewable pull request from a branch whose motivation is recorded in a plan.

## Goal

- **G:** Generate a concise PR draft grounded in branch evidence and the plan's motivation without mutating GitHub state.
  - Done when: both supported plan layouts are discovered, the Summary uses available plan Context, the test plan remains executable and unchecked, and the skill leaves PR creation to the authorized release workflow.

## Scenario

- A maintainer finishes work governed by either a single-file or subfolder plan, invokes `git-pr`, and receives `pr-draft.md` whose title follows the diff while its Summary explains the Context's why and whose test plan remains unchecked until executed evidence exists.

## Acceptance criteria

- ⬜ Plan discovery searches both `plans/*.md` and `plans/*/plan.md` for active or completed plans.
- ⬜ A real draft run on a branch ahead of `main` discovers a subfolder plan and incorporates its Context motivation into the Summary.
- ⬜ Every non-possessive Herald mention uses `Herald 📯 (Release Manager)`; possessives remain bare.
- ⬜ The skill writes only `pr-draft.md`, never mutates GitHub or git state, and preserves the unchecked test-plan plus immutable-head evidence contracts.

## Change log

- 2026-09-14 — skill-debt-resolution-20260914: created the durable feature definition for dual-layout plan discovery and context-grounded PR drafting; criteria remain pending during plan creation.

## Resolved decisions

- 2026-09-14 — DEBT-001 requires an actual draft run, so verification waits for a separately authorized checkpoint commit and never treats static wording alone as execution evidence.
