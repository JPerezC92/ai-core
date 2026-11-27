# Git execution procedures

The procedures Herald 📯 (Release Manager) follows for base synchronization, branch creation and switching, staging, commits, pushes, tags and stash work. Herald 📯 (Release Manager) is the sole Git and GitHub executor; the authority, scope, gates, dependency ownership and reporting obligations in `.opencode/agents/herald.md` bind this procedure in full and are not restated here.

## Applicability

Read this file before base synchronization, branch creation or switching, staging, committing, pushing, tagging, or any stash operation. The obligation to consult this owner binds the agent; no runtime mechanism enforces the read. A file already read in this session stays applicable — re-read it only when it changed, when the read was incomplete, or when its owner requires a fresh read.

## Base synchronization

Sync with `$BASE` at the remote boundaries: run `git fetch "$BASE_REMOTE"`, then `git rev-list HEAD.."$BASE" --count`, only at a push, pull-request or merge boundary or on an explicit Cipher 🔓 (Lead Orchestrator) request. An ordinary local commit performs no remote fetch and no base-sync check: the staging and commit steps keep only their remote-free checks, and this section runs immediately before the remote operation it guards. Two triggers:

- **Pre-push and pre-PR** (before any push, pull-request creation, or authorized pull-request-head update): if non-zero, run `git pull --ff-only "$BASE_REMOTE" "$BASE_BRANCH"` before pushing. If a fast-forward is unavailable, use the non-PR base-sync route below (Cipher 🔓 (Lead Orchestrator)-requested `git merge "$BASE"` into the current non-PR feature branch); if that route is unavailable or not authorized, stop and report the synchronization blocker. Never use a merge-capable pull or merge a pull request. The sole exception is the merge commit made by `.aicore/core/knowledge/pull-request-execution.md` → `## Cipher-authorized update of an open pull-request branch`: that procedure pins and validates the base itself, and this generic pull is not run for that merge commit.
- **Non-PR feature branch base sync** (on Cipher 🔓 (Lead Orchestrator)'s request, including a pre-implementation dispatch or a mid-flow push whose fast-forward is unavailable): if non-zero, run `git merge "$BASE"` only into the current non-PR feature branch, then report the result to Cipher 🔓 (Lead Orchestrator) before implementation resumes. This synchronization exception never targets `$BASE_BRANCH`, never runs in a pull-request lifecycle, and is not a pull-request merge.

Merge boundaries keep their own in-procedure base sync: the authorized pull-request-head update in `.aicore/core/knowledge/pull-request-execution.md` fetches the current base before merging and re-fetches it immediately before pushing, and the post-merge cleanup in the same document fetches `$BASE_REMOTE` before the base fast-forward. Those obligations stand unchanged and this section does not replace them.

## Commit message

Invoke the `git-commit` skill — it analyzes staged and unstaged changes, detects the commit style from `git log`, and writes `output/commit.txt`. Use that path as the commit-message source. Fall back to reading the diff directly only when `output/commit.txt` is absent or stale (pre-dates the current changeset), the skill has no unresolved blocker, and its effective-ignore preflight for that output has passed. Absence or staleness after a safety failure never permits fallback, writing a substitute draft, or committing from an old draft; report the actual blocker to Cipher 🔓 (Lead Orchestrator).

## Branch creation and switching

When a branch is needed, invoke the `git-branch-name` skill — it suggests a name in `type/scope/description` format. If the skill draft is unavailable and Cipher 🔓 (Lead Orchestrator) supplies a fallback name, require that same format and a commitlint-supported type; otherwise stop and report the naming blocker. Create with `git switch -c <name> "$BASE"` — the creation point is the explicitly verified base ref, not the current checkout — or switch to an existing authorized task branch only after establishing its exact identity, the authority for that creation or switch, and preservation of existing tracked, untracked and ignored work, exclusions and stashes. Verify that `$BASE` resolves to the intended base branch before creating: an incorrect, unresolvable or stale base blocks creation, and a branch inherited from the current checkout is never an acceptable substitute except for the user-confirmed base-branch recovery route in `.opencode/agents/herald.md` → `#### PR lifecycle`. An unsafe or unverified creation or switch blocks staging and committing; never force it or change existing refs to recover.

## Staging and commit

1. **Discover the change set.** Run `git status` to discover all unstaged and untracked changes. You own file discovery — Cipher 🔓 (Lead Orchestrator) does not need to enumerate paths. Classify each changed or untracked file as either **stage** or **flag**:
   - **Flag** (hold, report to Cipher 🔓 (Lead Orchestrator) before staging): `.env` files, credential or secret files (e.g. `*.pem`, `*.key`, `*secret*`, `*token*`), and files that are clearly unrelated to the task context Cipher 🔓 (Lead Orchestrator) described.
   - **Stage**: everything else — including config files (`.gitignore`, `*.json`, `*.yaml`, etc.) and any file that plausibly relates to the described task, even if not explicitly mentioned by Cipher 🔓 (Lead Orchestrator).
   - If flagged files exist, report them to Cipher 🔓 (Lead Orchestrator) with a brief reason and wait for confirmation before staging them. Never silently drop them.
2. **Stage.** Before any staging, read the actual symbolic branch with `git symbolic-ref --quiet --short HEAD` and verify it against the project's configured `$BASE_BRANCH` and the exact authorized task branch. Detached HEAD, a failed or unreadable branch or base configuration, missing task-branch context, a task branch equal to the base, or an unrelated current branch blocks staging and committing. If currently on the base, first complete the safe authorized creation or switch above; reread and require the symbolic branch to equal the authorized non-base task branch before staging. Record that verified branch, then run `git add` with explicit file paths derived from the `git status` output (the **stage** set, plus any flagged files Cipher 🔓 (Lead Orchestrator) confirms). Never use `git add -A` or `git add .`.
3. **Commit.** Immediately before every commit, repeat the symbolic-branch and configured-base/task-identity verification; require the same authorized non-base branch recorded before staging. A changed branch, detached HEAD, failed read or missing context stops the commit while preserving staged work. Only then run `git commit -F output/commit.txt`. Never use `--no-verify`, `--force`, `--no-gpg-sign`. Never write commit or pull-request drafts at the repository root.

## Push and tag

- Push: `git push "$BASE_REMOTE" <branch>`
- Tag: `git tag <name>` then `git push "$BASE_REMOTE" <name>` — ask Cipher 🔓 (Lead Orchestrator) for the tag name if not supplied

## Stash lifecycle

Only Herald 📯 (Release Manager) may park work with `git stash push` / `git stash save` (stack semantics — Git never erases existing stash entries on push) and recover it non-destructively with `git stash apply <ref>` — the entry survives as a durable backup. Every other agent that needs to park or recover work requests that operation from Herald 📯 (Release Manager) through Cipher 🔓 (Lead Orchestrator); it never runs a stash command itself. Erasure — `git stash pop`, `git stash drop`, `git stash clear`, `git update-ref -d refs/stash` — is denied to model agents and is user-only, run manually in the user's terminal.

The applied or unapplied verdict is mechanical via this section's stash status query (`git stash list` → `git stash show -u <ref> --name-only` → `git status --porcelain`): all stash paths present in worktree status = applied; any missing = unapplied; inconclusive → "cannot confirm mechanically". The read-only inventory commands (`git rev-parse refs/stash`, `git stash list`, `git stash show -u`) are not an unconditional permission: preflight each exact invocation against the effective available permission rules and run only a form those rules allow, as `.opencode/agents/herald.md` → `#### Git integrity` states. No probe or restore CLI exists; there is no guarded CLI restore route.
