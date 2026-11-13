---
name: git-branch-name
description: Suggest a git branch name in type/scope/description format based on current changes or task context. Use when the user wants to create a branch, asks "what should I call this branch", says "I'm starting work on X", or is about to begin a feature, fix, or refactor — even if they don't explicitly say "branch name".
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.1.1
  domain: git
---

## Steps

1. Inspect the repository: working-tree status, staged and unstaged changes, recent commit subjects, the branch list, and the current branch.
2. Read the change content — the whole change set when it is small, the highest-signal files otherwise — and treat it as authoritative for intent.
3. Detect a multi-package workspace from the project's own workspace markers before choosing the scope level.
4. Derive the type and scope from the changes. A current branch name that already follows the convention is evidence of intent, not authority: when the two disagree, the changes win.
5. Compose `type/scope/description` using the conventions below.
6. Report the suggested name followed by one line explaining the choice.

If the change set is empty, derive the name from in-progress work — the current branch and recent history — or ask the requester what work is starting. If the current branch is already a conventional feature branch, say whether it still matches; if it is the default branch, say a feature branch is required before committing.

## Format

`type/scope/description`

### Type

| Prefix | Use for |
|--------|---------|
| `build` | Build system or external dependency changes |
| `chore` | Maintenance or tooling outside source, tests, docs, build, and CI |
| `ci` | Continuous-integration configuration or scripts |
| `docs` | Documentation only |
| `feat` | New feature or capability |
| `fix` | Bug fix, including an urgent production fix |
| `perf` | Performance improvement |
| `refactor` | Restructuring without behavior change |
| `revert` | Revert a previous commit or PR |
| `style` | Formatting only, not CSS or UI design |
| `test` | Adding or updating tests only |

### Scope

Use one lowercase kebab-case token. It maps directly to the commit scope, so `feat/billing-api/add-endpoint` becomes `feat(billing-api): add endpoint`.

- **Single repo**: the affected module, feature, or layer, such as `auth`, `api`, `ui`, or `config`.
- **Shared core or package**: its package name, such as `core` or `ui-kit`.
- **Independent app**: its app name, such as `cli`.
- **Backend-only product app**: `<app>-api`, such as `billing-api`.
- **Frontend-only product app**: `<app>-web`, such as `billing-web`.
- **App with both sides**: `<app>-api` or `<app>-web` when one side changes; `<app>` only when one change genuinely spans both.
- **Cross-cutting work**: the shared concern that caused it, such as `deps`, `ci`, or `repo` — never a list of affected apps.

### Description

- Lowercase words separated by hyphens, at most four or five.
- Imperative mood: `add-search-filter`, not `added-search-filter`.

## Rules

- Suggest only. Do not create the branch, and do not stage, commit, push, or run any state-mutating Git command.
- Do not print a branch-creation command; the name is the deliverable.
- `hotfix` is not a type. Urgent production fixes use `fix`, and urgency belongs to the release process.
