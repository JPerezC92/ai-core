---
name: git-pr
description: Draft a pull request title and body from branch commits and the base diff, then initialize and validate the local body-only review document. Use when opening a PR, drafting its description, or getting a branch ready to merge.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.12.1
  domain: git
---
<!-- core:begin -->

## Steps

1. Establish scope: the commits on the branch and the complete diff from the merge base with the project's configured base ref (`$BASE`, substituted with the project's actual base) to the current head, sampling the highest-signal files when the change set is large. That diff is the only scope evidence; a whitespace or staging diagnostic never is. An unresolvable or ambiguous configured base stops the draft and is reported as a blocker; never substitute a base of your own choosing.
2. Read `knowledge/agent-workflow.md` and apply `### ODD protocol` for classification; do not restate that protocol here. Establish authorized intent from the request/assignment, branch/task context, scoped commits and reconciled diff:
   - **Small work:** use the authorized request/assignment with the scoped commits and diff for intent and current state; require no artificial feature document.
   - **Non-small work:** identify the unique governing ODD feature document at `odd/tasks/<YYYY-MM-DD>-<feature-name>.md` from the task context and reconciled changed files, never merely by filename, date, or status; read its `## Specs`, relevant `## Tasks`, and `## Log` for intent and current state. A missing document or timing evidence is a blocker, not permission to document implementation retroactively.
   - **Explicit legacy migration** may consume its existing legacy input for intent; it is not an alternative workflow for new work and does not waive applicable ODD classification or timing requirements.
   Use ticket references from recent commit subjects where present. The Summary explains why, grounded in the applicable authorized intent rather than inferred from the diff alone. If classification, authority, intent, or the required document's applicability is ambiguous or missing, investigate accessible evidence, then stop and report unresolved gaps and inspected candidates to the coordinator/requester before drafting; never infer an answer.
3. Derive the title and body from the diff. When the current branch follows `type/scope/description` and its type or scope disagrees with the derived title, keep the diff-derived title and report both values explicitly: a branch is evidence of intent, not authority.
4. Before any draft or working-body write, obtain a read-only effective-ignore check for the exact intended path (`output/pr-draft.md` or `output/pr-working-body.md`) through the existing Git owner (Herald 📯 (Release Manager) when the roster is installed, otherwise the authorized requester). Confirm the actual path is ignored, including negation rules and whether it is already tracked; merely finding an ignore entry is not proof. Check a not-yet-created path prospectively. Not ignored, tracked, denied, failed, or inconclusive → stop and report the checked path and observed blocker to the coordinator/requester for separately authorized remediation by the existing ignore-configuration owner. This skill never edits `.gitignore` or other ignore configuration. While remediation is blocked, pending, or declined, create/overwrite neither draft, working body nor directory and do not hand off a stale file as ready. Resume only after a fresh successful check; this grants no new Git-command authority.
5. Write `output/pr-draft.md` in the shape below only after that check succeeds. Create `output/` if needed. Never write `pr-draft.md` at the repository root. It is the initial creation draft, not the post-review evidence document; the sole later working body is `output/pr-working-body.md`.
6. Hand off. When the roster is installed, report that `output/pr-draft.md` is ready for Herald 📯 (Release Manager) to create the PR, naming Inquisitor 🔎 (PR Reviewer) review at the immutable head as the completion condition, and print no publication command. Otherwise report the draft ready for the requester.

When the branch has no commits ahead of the base, report that there is nothing to draft; if uncommitted changes exist, point to `git-commit` first.

## Draft and body contract

### Title

`type(scope): concise summary under 70 characters`

- **type**: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, or `test`; `style` means formatting, not CSS or UI design.
- **scope**: one lowercase kebab-case token — the affected module, feature, layer, package, app side (`<app>-api`, `<app>-web`), or the shared concern behind a cross-cutting change (`deps`, `ci`, `repo`).
- Imperative mood, lowercase after the colon, no trailing period.

### Body

Read `references/_pr-evidence-format.md` in full before drafting. It is the canonical format for the completed body, including the mandatory findings and test-evidence tables.

```markdown
## Summary
- <what changed and why — one line each, at most three>

## Test plan
- [ ] <action and the observable expected result>
- [ ] <edge case or regression and its expected result>

## Findings / blockers
No review findings yet.
```

- **Summary**: the motivation, not a restatement of the diff.
- **Test plan**: at least two concrete, executable steps, each naming the action and its expected result. Every item is an unchecked `- [ ]` checkbox in the draft — never `[x]`, a result, or a claim that something ran.
- **Findings / blockers**: the initial draft states `No review findings yet.` with no table. After review, this section follows `references/_pr-evidence-format.md`: the mandatory findings table, or `No findings.` when the review produced none.
- **Line budget**: keep the initial draft under 20 lines. After review, the findings and test-evidence tables extend the body only as required — one row per finding or checked item, no duplicated prose, no padding.

### Breaking changes

When a commit title carries `!` or the diff removes or renames a public interface, add before the test plan:

```markdown
## Breaking changes
- <what breaks>
- Migration: <one-line path>
```

### Output shape

```text
Title: <title>

---

<body>
```

## Publication and review

This skill owns the pull-request content only: the title, the body, the format and the content-specific validation. The publication, evidence, attribution and persistence procedure — the immutable-head identity, the evidence preparation, the single publication write, the attribution scan and the persisted-body consistency — is `.opencode/skills/git-pr-workflow/SKILL.md`; read it before handing a draft off.

The two commands that belong to this skill are `prepare_pr_review.py initialize` and `prepare_pr_review.py validate`, with their arguments unchanged; their input schemas and exit codes are in `.opencode/skills/git-pr-workflow/references/_pr-workflow-inputs.md`.

The creation draft is written only to `output/pr-draft.md` and the sole working body to `output/pr-working-body.md`. This skill never publishes or mutates a pull request and never runs a Git or GitHub command.

## Rules

- Never run a Git or GitHub command: the workflow commands that read Git are executed by Herald 📯 (Release Manager) through `.opencode/skills/git-pr-workflow/SKILL.md`, and this skill's own commands read supplied files only.
- Authoring writes are limited to `output/pr-draft.md`, the one `output/pr-working-body.md`, and their `output/` parent directory when absent. Explicit assigned machine-evidence outputs may be created by the preparation tool through the existing authorized owner; this is not permission to invent further PR-description files. Do not write the repository root or edit `.gitignore`. Never publish or mutate a PR — creation, title, body, merge, comments and reviews included — and never run a state-mutating Git command.
- Do not tick a checkbox, claim executed evidence, or record a result in the initial creation draft. The designated writer's local review body instead follows `.opencode/skills/git-pr-workflow/SKILL.md` and `references/_pr-evidence-format.md`; no fabricated results.
- Do not force the title to match the branch; report the mismatch and keep the diff-derived title.
<!-- core:end -->
