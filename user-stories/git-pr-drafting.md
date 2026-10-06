# User story — git-pr-drafting

> **Created:** 2026-09-14
> **Title:** Pull request draft generation
> **Status:** active
> **version:** 1.0.0
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

- ✅ Plan discovery searches both `plans/*.md` and `plans/*/plan.md` for active or completed plans. Evidence: `.opencode/skills/git-pr/SKILL.md` `1.4.0` plan-discovery section.
- ✅ A real draft run on a branch ahead of `main` discovers a subfolder plan and incorporates its Context motivation into the Summary. Evidence: the `git-pr` run at checkpoint `64fae1bf4aa5978e5a8a14ce63a30fca11905660` discovered `plans/skill-debt-resolution-20260914/plan.md` via `plans/*/plan.md` and its Summary bullet states the plan's why (DEBT-001/002/003).
- ✅ Every non-possessive Herald mention uses `Herald 📯 (Release Manager)`; possessives remain bare. Evidence: Vault 🔐 (Catalog Steward) `[PASS]` for `git-pr` `1.4.0`; all mentions conform.
- ✅ The skill writes only `pr-draft.md`, never mutates GitHub or git state, and preserves the unchecked test-plan plus immutable-head evidence contracts. Evidence: `pr-draft.md` gitignored by `.gitignore`; the run staged and committed nothing; Vault 🔐 (Catalog Steward) `[PASS]`.
- ✅ `Observed output` in PR test evidence is the human-readable verdict only — for pytest, the `N passed in Xs` line (and the exit code where relevant); progress bars, per-test dots, stack traces, and raw dumps are forbidden unless the user explicitly asks. Evidence: `.opencode/skills/git-pr/SKILL.md` `1.4.0` **Verdict-only observed output**; consumers `.opencode/agents/inquisitor.md` `1.4.0` and `.opencode/agents/herald.md` `1.4.0`.

## Change log

- 2026-09-14 — skill-debt-resolution-20260914: created the feature definition; added dual-layout plan discovery and context-grounded PR drafting (`git-pr` `1.3.1`).
- 2026-10-05 — process-debt-clearance-20261005: added the verdict-only `Observed output` criterion (`git-pr` `1.4.0`; consumers inquisitor and herald).

## Resolved decisions

- 2026-09-14 — the skill writes only `pr-draft.md` and never mutates GitHub or git state; the test plan stays unchecked until executed evidence exists.
