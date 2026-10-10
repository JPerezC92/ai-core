# User story — post-merge-branch-cleanup

> **Created:** 2026-09-15
> **Title:** Merge-style-aware post-merge branch cleanup
> **Status:** active
> **version:** 1.0.0
> **Epic:** developer-tooling
> **Affected areas:** `.opencode/skills/plan-enforce/`, `.opencode/agents/herald.md`

## Persona

- A maintainer who has confirmed a PR merge and needs the merged branch cleaned up without ever deleting a branch whose changes are not actually in `main`.

## Goal

- **G:** A user-confirmed merged branch is deleted only after a fail-closed proof that its content is in `origin/main`, for merge-commit, squash, and rebase merges alike.
  - Done when: the shared plan-enforce/Herald 📯 (Release Manager) sequence requires live `MERGED` PR metadata, an immutable head pin, merge-commit ancestry when present, branch-tip ancestry for `git branch -d`, and per-path content parity (`git diff --quiet --exit-code`) before any `git branch -D`, with every metadata, fetch, extraction, ancestry, or diff error blocking deletion. Evidence: `.opencode/skills/plan-enforce/SKILL.md` `User confirms PR merge` lifecycle rule; `.opencode/agents/herald.md` `#### Execution steps` item 8 and `#### PR lifecycle`.

## Scenario

- A PR is squash-merged (the branch tip is not an ancestor of `main`). The maintainer confirms the merge. The cleanup first reads live PR metadata, pins the immutable head, checks merge-commit ancestry, and — because branch-tip ancestry fails for a squash merge — materializes the changed paths and requires an empty per-path parity diff before force-deleting the local branch and deleting the remote branch when it still exists.

## Acceptance criteria

- ✅ The plan-enforce `User confirms PR merge` rule requires live `MERGED` metadata, an immutable `headRefOid` pin matched to `$BRANCH`, merge-commit ancestry when present, branch-tip ancestry for `git branch -d`, and per-path content parity (`git diff --name-only -z` into `CHANGED_PATHS` plus `git diff --quiet --exit-code` exiting 0) before `git branch -D`. Evidence: `.opencode/skills/plan-enforce/SKILL.md`, row `User confirms PR merge`.
- ✅ Herald 📯 (Release Manager) implements the same fail-closed sequence and keeps user-only merge authority. Evidence: `.opencode/agents/herald.md` `#### Execution steps` item 8 and `#### PR lifecycle` hard rules.
- ✅ Any metadata, fetch, head-mismatch, merge-base, path-extraction, ancestry, or diff error blocks deletion; `git branch -D` is authorized only after the content-parity proof, the local delete is `-d` on the ancestry path, and the remote branch is deleted only when it still exists. Evidence: `.opencode/skills/plan-enforce/SKILL.md` `User confirms PR merge` lifecycle rule and `.opencode/agents/herald.md` `#### Execution steps` item 8 / `#### PR lifecycle`.
- ✅ The plan-enforce skill discovers the capability from its trigger metadata. Evidence: `.opencode/skills/plan-enforce/SKILL.md` frontmatter description and `## When to use me` (user-confirmed PR merge trigger).

## Change log

- 2026-10-09 — aicore-all-files-pr-20261008: made remote-branch deletion conditional on its continued existence as part of the fail-closed cleanup contract.
- 2026-09-15 — debt-001-citation-currency-20260915: created the feature definition for merge-style-aware, fail-closed post-merge branch cleanup.

## Resolved decisions

- 2026-09-15 — The cleanup proof is content parity on the immutable PR head rather than ancestry alone, because squash and rebase merges leave the branch tip outside `origin/main`.
- 2026-09-15 — The branch tip must equal the pinned `headRefOid`, so cleanup proves the exact reviewed head rather than a possibly advanced local branch.
- 2026-09-15 — Deleting a branch is destructive, so it stays user-confirmed and fail-closed: no proof, no deletion.
