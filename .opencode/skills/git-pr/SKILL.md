---
name: git-pr
description: Draft a pull request title and body by analyzing branch commits and the diff versus the project's base branch ($BASE), writing output to `output/pr-draft.md`. Use when the user wants to open a PR, create a pull request, draft a PR description, or says "I'm done with this branch" / "ready to merge" / "submit my changes".
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.8.1
  domain: git
---

## Steps

1. Establish scope: the commits on the branch and the complete diff from the merge base with the project's configured base ref (`$BASE`, substituted with the project's actual base) to the current head, sampling the highest-signal files when the change set is large. That diff is the only scope evidence; a whitespace or staging diagnostic never is. An unresolvable or ambiguous configured base stops the draft and is reported as a blocker; never substitute a base of your own choosing.
2. Read `knowledge/agent-workflow.md` and apply `### ODD protocol` for classification; do not restate that protocol here. Establish authorized intent from the request/assignment, branch/task context, scoped commits and reconciled diff:
   - **Small work:** use the authorized request/assignment with the scoped commits and diff for intent and current state; require no artificial feature document.
   - **Non-small work:** identify the unique governing ODD feature document at `odd/tasks/<feature-name>.md` from the task context and reconciled changed files, never merely by filename, date, or status; read its `## Specs`, relevant `## Tasks`, and `## Log` for intent and current state. A missing document or timing evidence is a blocker, not permission to document implementation retroactively.
   - **Explicit legacy migration** may consume its existing legacy input for intent; it is not an alternative workflow for new work and does not waive applicable ODD classification or timing requirements.
   Use ticket references from recent commit subjects where present. The Summary explains why, grounded in the applicable authorized intent rather than inferred from the diff alone. If classification, authority, intent, or the required document's applicability is ambiguous or missing, investigate accessible evidence, then stop and report unresolved gaps and inspected candidates to the coordinator/requester before drafting; never infer an answer.
3. Derive the title and body from the diff. When the current branch follows `type/scope/description` and its type or scope disagrees with the derived title, keep the diff-derived title and report both values explicitly: a branch is evidence of intent, not authority.
4. Before any draft write, obtain a read-only effective-ignore check for the exact `output/pr-draft.md` path through the existing Git owner (Herald 📯 (Release Manager) when the roster is installed, otherwise the authorized requester). Confirm the actual path is ignored, including negation rules and whether it is already tracked; merely finding an ignore entry is not proof. Check a not-yet-created path prospectively. Not ignored, tracked, denied, failed, or inconclusive → stop and report the checked path and observed blocker to the coordinator/requester for separately authorized remediation by the existing ignore-configuration owner. This skill never edits `.gitignore` or other ignore configuration. While remediation is blocked, pending, or declined, create/overwrite neither draft nor directory and do not hand off a stale file as ready. Resume only after a fresh successful check; this grants no new Git-command authority.
5. Write `output/pr-draft.md` in the shape below only after that check succeeds. Create `output/` if needed. Never write `pr-draft.md` at the repository root or create a second PR-description artifact.
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

### Post-PR evidence contract

Read `references/_pr-evidence-format.md` in full before writing post-review evidence. It is canonical for the findings, test-evidence, open-debt, and verdict sections.

After the PR exists, its body remains the sole evidence surface — never comments, reviews, or a second document. Before any checkbox changes from `- [ ]` to `- [x]`, the current-head evidence block and one row for that item must exist. The block records the PR number, immutable head SHA, base, and literal scope command once; the table maps every checked test-plan item to exactly one row with the exact item text, literal action/input, verdict-only observed result, and actual executor.

**Verdict-only observed output.** Record the human-readable verdict — for a test run, the pass/fail summary line and exit code where relevant. Never paste progress bars, per-test dots, stack traces, or raw dumps unless the requester explicitly asks.

**Manual actions.** A genuinely performed manual check records its literal action or input, observed result and actual executor. Include a command only when one actually ran; never invent one, and never let a bare tick directive or a manual/optional label stand in for a performed check.

**Atomic join.** The single designated evidence writer validates the complete current-head block first, then persists the rows and their matching ticks in one body write and live-rereads the same head and body. The same join owns every post-review findings, evidence, open-debt, and verdict write; no other post-review body writer updates them. A changed head, divergent body, or failed reread rejects the write and blocks acceptance; missing or partial evidence leaves the item unchecked.

**Execution ownership.** An execution owner that runs an item but does not own the PR body never reports the PR complete. The item stays unchecked until the designated writer has persisted the row and tick at the review join.

**Separate prose corrections.** A later authorized factual prose correction belongs to its own serialized writer, only after observed release of the evidence writer, and must preserve every findings/evidence/open-debt/verdict row, every tick, and unrelated prose.

## Rules

- The permitted writes are `output/pr-draft.md` and its `output/` parent directory when that directory is absent. Do not write the repository root or edit `.gitignore`. Never publish or mutate a PR — creation, title, body, merge, comments and reviews included — and never run a state-mutating Git command.
- Do not tick a checkbox, claim executed evidence, or record a result in the draft.
- Do not force the title to match the branch; report the mismatch and keep the diff-derived title.
