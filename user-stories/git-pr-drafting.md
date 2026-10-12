# User story — git-pr-drafting

> **Created:** 2026-09-14
> **Title:** Pull request draft generation
> **Status:** active
> **version:** 1.1.0
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

- ✅ **AC1:** The skill finds the governing plan in either supported layout — a single file under `plans/` or a `plan.md` inside a plan subfolder — and accepts an active or completed plan.
- ✅ **AC2:** The draft's Summary explains the plan's Context motivation rather than merely restating the diff.
- ✅ **AC3:** Roster members are named in the canonical `Name Emoji (Role)` form in the skill's prose and in the generated draft; possessives stay bare-name.
- ✅ **AC4:** The skill writes only `pr-draft.md` and leaves GitHub and git state untouched.
- ✅ **AC5:** Test evidence records the human-readable verdict only; progress bars, per-test dots, stack traces, and raw dumps are omitted unless the maintainer explicitly asks.
- ✅ **AC6:** The generated test plan remains unchecked and executable until executed evidence exists.

## Proof

- AC1 → `.opencode/skills/git-pr/SKILL.md` plan-discovery section
- AC2 → `.opencode/skills/git-pr/SKILL.md` Summary construction · checkpoint `64fae1bf4aa5978e5a8a14ce63a30fca11905660`
- AC3 → Vault 🔐 (Catalog Steward) `[PASS]` on the `git-pr` surface
- AC4 → `pr-draft.md` gitignored · the recorded run staged and committed nothing · Vault 🔐 (Catalog Steward) `[PASS]`
- AC5 → `.opencode/skills/git-pr/SKILL.md` **Verdict-only observed output** · `.opencode/agents/inquisitor.md` · `.opencode/agents/herald.md`
- AC6 → `.opencode/skills/git-pr/SKILL.md` test-plan section

## Constraints

- The skill writes only `pr-draft.md` and never mutates GitHub or git state — because drafting is a review artifact and state changes belong to the authorized release workflow.
- PR creation is left to the authorized release workflow — because opening a PR requires an explicit per-repo user ask and is not implied by drafting.
- The test plan stays unchecked until executed evidence exists — because an unexecuted test plan is not a result.

## Change log

- before 2026-09-14 — earlier history: see git history for this file
- 2026-09-14 — skill-debt-resolution-20260914: created the feature definition; added dual-layout plan discovery and context-grounded PR drafting (`git-pr` `1.3.1`).
- 2026-10-05 — process-debt-clearance-20261005: added the verdict-only `Observed output` criterion (`git-pr` `1.4.0`; consumers Inquisitor 🔎 (PR Reviewer) and Herald 📯 (Release Manager)).
- 2026-10-12 — story revision: split behavioural criteria from `## Proof`, moved pre-decided policy into `## Constraints`, and dropped checkpoint/version pins from criterion text.
