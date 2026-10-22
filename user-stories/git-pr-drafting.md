<!-- core:begin -->
# User story — git-pr-drafting

> **Created:** 2026-09-14
> **Title:** Pull request draft generation
> **Status:** active
> **version:** 1.4.0
> **Epic:** developer-tooling
> **Affected areas:** `.opencode/skills/git-pr/`, `plans/`, `output/`

## Persona

- A maintainer preparing a reviewable pull request from a branch whose motivation is recorded in a plan.

## Goal

- **G:** Generate a concise PR draft grounded in branch evidence and the plan's motivation without mutating GitHub state.
  - Done when: both supported plan layouts are discovered, the Summary uses available plan Context, the test plan remains executable and unchecked, and the skill leaves PR creation to the authorized release workflow.

## Scenario

- A maintainer finishes work governed by either a single-file or subfolder plan, invokes `git-pr`, and receives a temporal PR-draft artifact whose title follows the diff while its Summary explains the Context's why and whose test plan remains unchecked until executed evidence exists.

## Acceptance criteria

- ✅ **AC1:** The skill finds the governing plan in either supported layout — a single file under `plans/` or a `plan.md` inside a plan subfolder — and accepts an active or completed plan.
- ✅ **AC2:** The draft's Summary explains the plan's Context motivation rather than merely restating the diff.
- ✅ **AC3:** Roster members are named in the canonical `Name Emoji (Role)` form in the skill's prose and in the generated draft; possessives stay bare-name.
- ⬜ **AC4:** The skill writes only the designated temporal draft artifact, never a repository-root draft or ignore-configuration file. It never mutates GitHub state or runs a Git command that mutates state.
- ✅ **AC5:** Test evidence records the human-readable verdict only; progress bars, per-test dots, stack traces, and raw dumps are omitted unless the maintainer explicitly asks.
- ✅ **AC6:** The generated test plan remains unchecked and executable until executed evidence exists.

## Proof

- AC1 → `.opencode/skills/git-pr/SKILL.md` `## Steps` item 2 governing plan discovery in either layout, active or completed
- AC2 → `.opencode/skills/git-pr/SKILL.md` `## Steps` item 2 Context read and `### Body` Summary requirement
- AC3 → registered root runtime (`AGENTS.md` source, resolved through its root binding) `### Conventions` roster mention format
- AC4 → `.opencode/skills/git-pr/SKILL.md` `## Steps` items 4–6 effective-ignore preflight and write, and `## Rules` write/mutation boundary · designated path in `## Constraints`
- AC5 → `.opencode/skills/git-pr/SKILL.md` `### Post-PR evidence contract` **Verdict-only observed output** · `.opencode/agents/inquisitor.md` `##### PR-body evidence boundary`
- AC6 → `.opencode/skills/git-pr/SKILL.md` `### Body` unchecked, executable Test plan requirements

## Constraints

- Draft generation writes only `output/pr-draft.md` after an effective-ignore check succeeds; GitHub mutations, root files, `.gitignore` edits, and state-mutating Git commands remain outside this skill — because drafts are temporal artifacts, not repository content. Denied, failed, or declined ignore remediation writes nothing.
- PR creation is left to the authorized release workflow — because opening a PR requires an explicit per-repo user ask and is not implied by drafting.
- The test plan stays unchecked until executed evidence exists — because an unexecuted test plan is not a result.

<!-- core:end -->

<!-- project:begin -->
## Approval record

- 2026-10-15 — The user explicitly approved aligning AC4 and its constraint with the existing skill's preview/approval-gated missing ignore entry, decline-blocks-both boundary, and no GitHub/state-mutating Git command. This records existing behavior, not permission to edit `.gitignore` in the distribution plan.
- 2026-10-21 — After DEBT-012, the user directed drafts off the repository root (“we have an output folder remenber”), then authorized continuation and “fix them” for the listed F11 hygiene/accounting repairs. Collision review: no other story owns the draft-write location; `concise-skill-authoring` AC5 still requires preserved Git safety. This records the replacement of skill-owned ignore edits with output-folder drafts plus fail-closed ignore preflight, not delivery or release.

## Local evidence

- **AC2:** Prior source Proof cited checkpoint `64fae1bf4aa5978e5a8a14ce63a30fca11905660` for Summary construction.
- **AC3, AC4:** Prior source Proof recorded Vault 🔐 (Catalog Steward) `[PASS]`, an ignored draft path, and a source run that staged and committed nothing. Those retained observations are not a new execution of the retired skill-owned ignore-edit/approval-decline boundary. The 2026-10-21 pointers (effective-ignore preflight, `output/pr-draft.md`, no skill-owned ignore mutation) supersede that boundary.
- **AC4 ignore preflight (2026-10-21 constructed, not a live draft):** Instruction text requires a successful effective-ignore check before write; denied/failed/declined remediation writes nothing. No `output/pr-draft.md` was created in this repair. Root `commit.txt`/`pr-draft.md` absent on coordinator listing.

## Revision tracking

- 2026-10-15 — Approved existing-behavior clarification and shared-region/Proof preparation awaited final-candidate acceptance and a delivery-matching history reference. AC4 retains its identity. The then-current skill's approval/decline ignore-edit clauses are superseded by the 2026-10-21 output-folder/preflight boundary; they are not the current proving surface.
- 2026-10-18 — Delivered by PR #71: AC4's Proof pointers were repointed to the condensed `git-pr` `## Steps` items 4–6 and `## Rules`; criterion identity, promise and mark are unchanged. Those step numbers are historical; current Proof follows steps 4–6 including ignore preflight.
- 2026-10-21 — AC4 promise restated as observable write/mutation boundary without a temporal path in the criterion; exact `output/pr-draft.md` stays in Constraints/Proof. Skill-owned `.gitignore` writes remain retired. Mark stays pending until matching delivery history. No PR/release is claimed.

## Change log

- before 2026-09-14 — earlier history: see git history for this file
- 2026-09-14 — skill-debt-resolution-20260914 (PR #36): created the feature definition; added dual-layout plan discovery and context-grounded PR drafting (`git-pr` `1.3.1`).
- 2026-10-05 — process-debt-clearance-20261005 (PR #47): added the verdict-only `Observed output` criterion (`git-pr` `1.4.0`; consumers Inquisitor 🔎 (PR Reviewer) and Herald 📯 (Release Manager)).
- 2026-10-12 — story revision (PR #59): split behavioural criteria from `## Proof`, moved pre-decided policy into `## Constraints`, and dropped checkpoint/version pins from criterion text.
- 2026-10-15 — story-distribution-20261015 (PR #64): clarified AC4 to the existing preview/approval-gated missing ignore entry and the no-state-mutating-Git-command boundary; regionized the story.
- 2026-10-18 — concise-skill-authoring (PR #71): repointed AC1/AC2/AC4 Proof to the condensed `git-pr` sections after the skill rewrite; no promise or mark change (`git-pr` `1.6.1`).
<!-- project:end -->
