---
name: verified-pr-cleanup
description: Read-only preflight for merged pull-request branch cleanup that reads live PR and Git state and, when a verdict exists, reports SAFE_TO_CLEAN or BLOCKED with every failed or inconclusive check, never mutating Git; a boundary failure is a separate stderr error channel and never BLOCKED. Use when an already-authorized post-merge cleanup needs independent merge-state verification before Herald 📯 (Release Manager) deletes a branch, or when a cleanup attempt must be halted on insufficient evidence.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.0.0
  domain: git
---

## Decision scope

The validator answers one question at one instant: does the evidence it can read currently support deleting this merged PR's branch? When a verdict exists, it reports exactly one of:

- `SAFE_TO_CLEAN` — every check passed and two complete reads of PR, ref, and worktree-occupancy state produced identical evidence.
- `BLOCKED` — at least one blocking check failed or is inconclusive; `reasons` lists the blocking failures and `checks` carries each check's detail.

No third JSON status exists. Argument validation and a boundary failure produce no verdict and no status JSON: the first exits `2` as a usage error, the second prints `Preflight boundary failure: <detail>` to stderr; neither is `BLOCKED` (see Prerequisites and Output and exit status below).

It performs no Git ref, object, worktree, stash, or remote mutation and never deletes a branch. Cleanup is a separate Herald 📯 (Release Manager) operation.

## Inputs

| Input | Meaning |
| --- | --- |
| PR number | Positive decimal GitHub pull-request number; `<pr>` in the command. |
| `--base-remote` | The project's configured base remote, written `$BASE_REMOTE` in the command. |
| `--base-branch` | The project's configured base branch, written `$BASE_BRANCH` in the command. |

Run the validator inside the repository checkout whose refs and linked worktrees must be validated. A missing or invalid input is a usage error, never a verdict. `$BASE_REMOTE` and `$BASE_BRANCH` are placeholders for the invoking project's configured base remote and branch; a destination project substitutes its own configured base remote and branch.

## Prerequisites

- The GitHub CLI (`gh`) must be installed on `PATH` and authenticated for the target repository; the validator reads live PR state through `gh pr view`.
- A missing executable or an authentication, authorization, or repository-read failure is a boundary failure: no decision exists, and it must not be reported as `BLOCKED` or as partial approval.

## Command

```
uv run --frozen python3 .opencode/skills/verified-pr-cleanup/scripts/verified_pr_cleanup.py <pr> --base-remote $BASE_REMOTE --base-branch $BASE_BRANCH
```

## Checks

The preflight passes only when all of these hold:

- The configured base remote resolves to exactly one GitHub repository, and its fetch and push URLs identify the same repository.
- The live PR is the requested number in that repository, its canonical URL matches, it is `MERGED`, and its base branch equals the configured base branch.
- A second complete read pins the same repository, PR number, head branch, immutable head OID, and base.
- Remote and local configured base refs exist and are equal; a stale or divergent base is reported as fetch needed.
- Each local and remote PR head ref is absent or equals the immutable PR head OID.
- Base, pinned head, and PR merge-commit objects are already available locally.
- The PR merge commit is an ancestor of the verified base, and the pinned PR head is also an ancestor of that base or passes changed-path parity on the pinned head through the same literal-pathspec proof Herald 📯 (Release Manager) uses in `.opencode/agents/herald.md` (`git --literal-pathspecs diff --quiet --exit-code ... -- "${CHANGED_PATHS[@]}"`). Merge-commit ancestry is mandatory; parity cannot substitute for it.
- The verified feature branch is not checked out in any worktree. Unrelated tracked, untracked, ignored, stash, or clean-worktree state never blocks branch-ref deletion; Herald 📯 (Release Manager) preserves that work and never resets or cleans it.
- No evidence changed between the two complete reads.

## Output and exit status

Standard output is one JSON object with `status`, `observed_at`, `point_in_time_only`, `reasons`, named `checks` (with `passed` and `detail`), `evidence`, `revalidate_before_each_mutation`, and the literal `authorization` note.

| Exit | Meaning |
| --- | --- |
| `0` | `status` is `SAFE_TO_CLEAN`. |
| `1` | `status` is `BLOCKED`, or a boundary failure was reported on stderr. |
| `2` | Argument validation rejected the invocation; no verdict exists. |

A boundary failure prints `Preflight boundary failure: <detail>` to stderr and emits no decision JSON. It is not `BLOCKED` and must not be read as one; report the failure and stop.

## SAFE_TO_CLEAN is evidence only

`SAFE_TO_CLEAN` is point-in-time evidence, not authorization or a command capability. It does not approve a PR merge, extend any cleanup authority, or replace the existing post-merge proof or OpenCode tool-permission decision. `revalidate_before_each_mutation` lists the checks to repeat immediately before each deletion operation.

## Read-only boundary

The validator runs only read-only Git and GitHub CLI queries, including repository URL, ref-format validation, `ls-remote`, `rev-parse`, `merge-base`, checked `diff`, `worktree list`, and `gh pr view` metadata. It never performs a fetch, switch, checkout, merge, push, delete, ref update, stash change, worktree change, or file deletion, and it calls no alternate executor. Its Git interaction writes nothing to Git refs, objects, index, stash, or worktree state. The `uv run --frozen` launcher that starts the command may create or reuse its own environment and cache outside that boundary; that launcher behavior is not validator output or verdict evidence.

## BLOCKED and fetch-needed handling

- `BLOCKED` is a halt: do not delete anything and do not treat any individual passing check as partial approval. Report `reasons` with the failed checks.
- A detail beginning `fetch needed:` means a required ref or commit object is missing or stale locally; the validator did not fetch. Fetch alone does not fix a stale local base. Under existing cleanup authority and accepted review, follow `.opencode/agents/herald.md` step 8: authenticate live merged repository/base/head identity, directly fetch, safely switch to base without overwriting user work, and fast-forward local base to the fetched base before re-running the validator. Local and remote base must agree and the PR head must be checked out nowhere. Divergence, unsafe switching or unavailable evidence blocks; never reset, clean or force away unique commits or uncommitted work.
- A boundary failure is also a halt. Report the exact failure; never convert missing evidence into a passing check or a go-ahead.
- Any new commit, push, merge, fetch, ref, or worktree change invalidates the result. Re-run the validator instead of reusing an earlier verdict.

## Invocation and authority

- Only Herald 📯 (Release Manager) should invoke this skill, before its existing post-merge branch deletion. If the invoking project scopes the validator entry point to Herald 📯 (Release Manager) in its OpenCode configuration, static permission matching applies to the command and cannot evaluate merge state.
- Actual deletion, base fast-forward, and remote cleanup remain Herald 📯 (Release Manager)'s existing workflow in `.opencode/agents/herald.md`, whose post-merge proof, worktree, force, merge, and user-authority gates still apply; unrelated stash state is not a cleanup blocker. This skill adds no cleanup command, shortcut, or permission.
- Load the project's exact effective permissions for Herald 📯 (Release Manager); its scoped direct cleanup command families do not validate branch targets. Existing explicit or standing cleanup authorization needs no duplicate conversational confirmation, but `SAFE_TO_CLEAN` is not a permission token and never bypasses an external deny or an applicable tool-permission decision. Other agents gain no permission.
- After `SAFE_TO_CLEAN`, follow step 8's immediate local/remote head and merge-proof revalidation before EACH direct single-feature-branch deletion. Skip an absent remote ref; stop on a mismatching remote tip. Verify ref absence and preservation of user work afterward. The validator never executes or wraps these mutations.
