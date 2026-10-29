# Release

<!-- core:begin -->
## Mandatory core

Release is a distinct workflow from ODD. This file is its home. Do not copy Herald 📯 (Release Manager), Inquisitor 🔎 (PR Reviewer), or `git-pr` procedures here. Those owners keep how; this file owns when.

### PR release readiness

Before opening a PR, Cipher 🔓 (Lead Orchestrator) assembles and verifies one release-readiness packet: the exact test-plan actions or commands with their observed results; every applicable gate status; the open-or-closed status of each task and of the feature; excluded or unrelated paths; unverified user-only controls; and each body claim against its evidence. Missing, contradictory, or stale evidence blocks PR creation until resolved — a partially verified packet is never an acceptable substitute. This applies to every PR, including docs-only changes, and introduces no tracker, no second approval ritual, and no change to existing authorizations or gates.

### Post-review finding actions

After each review round, Cipher 🔓 (Lead Orchestrator) uses the canonical combined rendered chat summary or, only when eligible, compact ready message in `knowledge/agents.md` `### PR review findings (adjudication)`. That owner defines finding presentation, accounting and readiness conditions; a raw findings list is not an acceptable handoff. Its fix-first rule, deferral authority, refutation evidence and loop cap remain unchanged, as do all existing gates; no tracker or additional approval step is introduced.

### Execution owners

- Git (branch, push, PR, delete): Herald 📯 (Release Manager)
- Review at an immutable head: Inquisitor 🔎 (PR Reviewer)
- PR body format: `.opencode/skills/git-pr/SKILL.md` and `.opencode/skills/git-pr/references/_pr-evidence-format.md`
- Cleanup proof command: `AGENTS.md` project `### Merged-branch cleanup preflight` and the `verified-pr-cleanup` skill
- Finding presentation: `knowledge/agents.md` `### PR review findings (adjudication)`
<!-- core:end -->

<!-- project:begin -->
## Project extensions

### Standing merged-branch cleanup

This project standing-authorizes Herald 📯 (Release Manager) to delete the merged feature branch after proven merge. Evidence: `odd/tasks/verified-merged-branch-cleanup.md` L2. Do not ask again. `SAFE_TO_CLEAN` is point-in-time evidence, not this grant. Local commits remain under `AGENTS.md` project `### Local commit authorization`. Push, PR, merge, tag, release, and archive remain separately authorized.
<!-- project:end -->
