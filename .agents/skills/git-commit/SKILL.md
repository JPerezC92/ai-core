---
name: git-commit
description: Generate a conventional commit message from git changes and write it to `output/commit.txt`. Use when the user wants to commit, write a commit message, prepare staged changes, or says "commit this", "make a commit", "what should my commit say", or "I'm ready to push".
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.3.2
  domain: git
---

## Steps

1. Inspect the repository: working-tree status, staged and unstaged changes, recent commit subjects, and the current branch.
2. Choose the scope of the message. When staged changes exist, describe only those; otherwise describe every unstaged change. With neither, report that there is nothing to commit and stop — never write an empty artifact.
3. Read the change content — the whole change set when it is small, the highest-signal files otherwise.
4. Match the style already in the history, including title shape, body grouping, and language. A convention-compliant current branch supplies the default `type(scope)` prefix, but the changes are authoritative: when the branch type or scope contradicts them, use the derived prefix and report the mismatch.
5. Before any draft write, obtain a read-only effective-ignore check for the exact `output/commit.txt` path through the existing Git owner (Herald 📯 (Release Manager) when the roster is installed, otherwise the authorized requester). Confirm the actual path is ignored, including negation rules and whether it is already tracked; merely finding an ignore entry is not proof. Check a not-yet-created path prospectively. Not ignored, tracked, denied, failed, or inconclusive → stop and report the checked path and observed blocker to the coordinator/requester for separately authorized remediation by the existing ignore-configuration owner. This skill never edits `.gitignore` or other ignore configuration. While remediation is blocked, pending, or declined, create/overwrite neither draft nor directory and do not hand off a stale file as ready. Resume only after a fresh successful check; this grants no new Git-command authority.
6. Write the message to `output/commit.txt` only after that check succeeds. Create `output/` if needed. Never write `commit.txt` at the repository root.
7. Hand off. When the project has the agent roster installed (its release-manager spec is present), report that `output/commit.txt` is ready for Herald 📯 (Release Manager) to stage and commit. Otherwise report that the file is ready for the requester. Never print or run the commit command yourself.

## Message format

### Title

`type(scope): concise summary under 72 characters`

- **type**: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, or `test`. `style` means formatting, not CSS or UI design.
- **scope**: one lowercase kebab-case token — the affected module, feature, layer, package, app side (`<app>-api`, `<app>-web`), or the shared concern behind a cross-cutting change (`deps`, `ci`, `repo`).
- The description starts with a lowercase verb.
- The title carries the why; the diff already shows the what.

### Body

- **Multi-package workspace**: group bullets by package or app path, and include only paths that actually changed.
- **Single repo**: flat bullets.
- Skip the body when the title alone is self-explanatory for a small, single-scope change.

### Breaking changes

Mark the title with `!` after the scope, and add a footer:

`BREAKING CHANGE: <what breaks> — migration: <path>`

## Rules

- The permitted writes are `output/commit.txt` and its `output/` parent directory when that directory is absent. Do not write the repository root, edit `.gitignore`, stage, unstage, commit, push, or run any state-mutating Git command.
- Never invent a change summary or write an empty artifact.
