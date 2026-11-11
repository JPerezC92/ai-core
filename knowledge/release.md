# Release

Release is a distinct workflow from ODD. This file is its home. Do not copy Herald 📯 (Release Manager), Inquisitor 🔎 (PR Reviewer), or `git-pr` procedures here. Those owners keep how; this file owns when.

### PR release readiness

Before opening a PR, Cipher 🔓 (Lead Orchestrator) assembles and verifies one release-readiness packet: the exact test-plan actions or commands with their observed results; every applicable gate status; the open-or-closed status of each task and of the feature; excluded or unrelated paths; unverified user-only controls; and each body claim against its evidence. Missing, contradictory, or stale evidence blocks PR creation until resolved — a partially verified packet is never an acceptable substitute. This applies to every PR, including docs-only changes, and introduces no tracker, no second approval ritual, and no change to existing authorizations or gates.

### Post-review finding actions

After each review round, Cipher 🔓 (Lead Orchestrator) uses the canonical combined rendered chat summary or, only when eligible, compact ready message in `knowledge/agents.md` `### PR review findings (adjudication)`. That owner defines finding presentation, accounting and readiness conditions; a raw findings list is not an acceptable handoff. Its fix-first rule, deferral authority, refutation evidence and loop cap remain unchanged, as do all existing gates; no tracker or additional approval step is introduced.

### Post-merge reporting

After merge, verify and report the outcome; do not automatically edit tracked files or create bookkeeping commits solely to record merge or cleanup facts. A separately requested post-merge documentation change remains authorized through the normal task-branch route, subject to existing authority and gates. Commit and cleanup mechanics remain with Herald 📯 (Release Manager) in `.opencode/agents/herald.md`; this timing rule changes no cleanup authorization or safeguards.

### Execution owners

- Git and GitHub operations of every kind — repository inspection, branch, worktree, staging, commit, push, PR creation, PR-body publication, delete — are executed by Herald 📯 (Release Manager) alone. Every other agent obtains Git- and GitHub-derived evidence from Herald 📯 (Release Manager) through Cipher 🔓 (Lead Orchestrator) and never runs the command.
- Review at an immutable head: Inquisitor 🔎 (PR Reviewer)
- PR body format: `.opencode/skills/git-pr/SKILL.md` and `.opencode/skills/git-pr/references/_pr-evidence-format.md`
- Cleanup proof: the native merge-proof procedure in `.opencode/agents/herald.md` step 8 — the PR's recorded merge commit reachable from the verified base, together with the verified PR identity and the pinned local and remote branch tips. It is evidence only, never authorization, and no separate validator runs.
- Finding presentation: `knowledge/agents.md` `### PR review findings (adjudication)`
