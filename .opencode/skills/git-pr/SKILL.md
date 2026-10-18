---
name: git-pr
description: Draft a pull request title and body by analyzing branch commits and the diff versus the project's base branch ($BASE), writing output to `pr-draft.md`; if that path is not ignored, preview and request approval before adding it to `.gitignore`. Use when the user wants to open a PR, create a pull request, draft a PR description, or says "I'm done with this branch" / "ready to merge" / "submit my changes".
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.6.1
  domain: git
---

## Steps

1. Establish scope: the commits on the branch and the complete diff from the merge base with the project's configured base ref (`$BASE`, substituted with the project's actual base) to the current head, sampling the highest-signal files when the change set is large. That diff is the only scope evidence; a whitespace or staging diagnostic never is. An unresolvable or ambiguous configured base stops the draft and is reported as a blocker; never substitute a base of your own choosing.
2. Find the governing plan — a single file under `plans/` or `plans/<slug>/plan.md`, active or completed — and read its Context for the motivation. Use ticket references from recent commit subjects where present. The Summary explains why, which usually lives there rather than in the diff.
3. Derive the title and body from the diff. When the current branch follows `type/scope/description` and its type or scope disagrees with the derived title, keep the diff-derived title and report both values explicitly: a branch is evidence of intent, not authority.
4. Check the effective ignore rules for `pr-draft.md`. When it is not ignored, preview the exact `.gitignore` line and request explicit approval for that second write. Declined → write neither file and report the blocker. Approved → append the entry only when missing, confirm the path is now ignored, and continue.
5. Write `pr-draft.md` at the repository root in the shape below. Never create a second PR-description artifact.
6. Hand off. When the roster is installed, report that `pr-draft.md` is ready for Herald 📯 (Release Manager) to create the PR, naming Inquisitor 🔎 (PR Reviewer) review at the immutable head as the completion condition, and print no publication command. Otherwise report the draft ready for the requester.

When the branch has no commits ahead of the base, report that there is nothing to draft; if uncommitted changes exist, point to `git-commit` first.

## Draft and body contract

### Title

`type(scope): concise summary under 70 characters`

- **type**: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, or `test`; `style` means formatting, not CSS or UI design.
- **scope**: one lowercase kebab-case token — the affected module, feature, layer, package, app side (`<app>-api`, `<app>-web`), or the shared concern behind a cross-cutting change (`deps`, `ci`, `repo`).
- Imperative mood, lowercase after the colon, no trailing period.

### Body

```markdown
## Summary
- <what changed and why — one line each, at most three>

## Test plan
- [ ] <action and the observable expected result>
- [ ] <edge case or regression and its expected result>
```

- **Summary**: the motivation, not a restatement of the diff.
- **Test plan**: at least two concrete, executable steps, each naming the action and its expected result. Every item is an unchecked `- [ ]` checkbox in the draft — never `[x]`, a result, or a claim that something ran.
- Keep the whole body under 20 lines.

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

After the PR exists, its body remains the sole evidence surface — never comments, reviews, or a second document. Before any checkbox changes from `- [ ]` to `- [x]`, one complete row is required:

````markdown
## Test evidence
- Test-plan item: `<exact checkbox text>`
  - PR: `#<number>`
  - Commit under test / immutable head SHA: `<head-sha>`
  - Base: `$BASE`
  - Scope command: `git diff "$BASE"...<head-sha>`
  - Input: `<literal performed input>`
  - Command (only when actually executed): `<literal executed command>`
  - Observed output: `<literal observed verdict>`
  - Executor: `<person or agent>`
````

**Verdict-only observed output.** Record the human-readable verdict — for a test run, the pass/fail summary line and exit code where relevant. Never paste progress bars, per-test dots, stack traces, or raw dumps unless the requester explicitly asks.

**Manual actions.** A genuinely performed manual check records its literal action or input, observed result and actual executor. Include a command only when one actually ran; never invent one, and never let a bare tick directive or a manual/optional label stand in for a performed check.

**Atomic join.** The single designated evidence writer validates the complete head-bound row first, then persists the row and its matching tick in one body write and live-rereads the same head and body. A changed head, divergent body, or failed reread rejects the write and blocks acceptance; missing or partial evidence leaves the item unchecked.

**Execution ownership.** An execution owner that runs an item but does not own the PR body never reports the PR complete. The item stays unchecked until the designated writer has persisted the row and tick at the review join.

**Separate prose corrections.** A later authorized factual prose correction belongs to its own serialized writer, only after observed release of the evidence writer, and must preserve evidence rows, ticks and unrelated prose.

## Rules

- Write only `pr-draft.md` plus the separately approved ignore entry. Never publish or mutate a PR — creation, title, body, merge, comments and reviews included — and never run a state-mutating Git command.
- Do not tick a checkbox, claim executed evidence, or record a result in the draft.
- Do not force the title to match the branch; report the mismatch and keep the diff-derived title.
