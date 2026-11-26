# Release

Release is a distinct workflow from ODD. This file is its home. Do not copy Herald 📯 (Release Manager) procedures here. Those owners keep how; this file owns when.

### PR release readiness

Before opening a PR, the coordinator assembles and verifies one release-readiness packet: the exact test-plan actions or commands with their observed results; every applicable check's status, and for a check that could not execute, the guarantee it exists to establish together with the permitted alternative procedure that established it; the open-or-closed status of each task and of the feature; excluded or unrelated paths; unverified user-only controls; and each body claim against its evidence. Missing, contradictory, or stale evidence blocks PR creation until resolved — a partially verified packet is never an acceptable substitute. This applies to every PR, including docs-only changes, and introduces no tracker, no second approval ritual, and no change to existing authorizations or gates.

The governing ODD record's closure is a precondition of the packet, not an item inside it: the record is closed and its closure committed, and the release executor proves that from committed state before any pull-request route begins. A packet cannot substitute for that proof, and reporting readiness covers only the pull request itself — its required checks and their evidence.

**An independent review is not part of the packet.** When the user requests one, its findings join the packet as findings with their dispositions; when none is requested, the packet is complete without it, and no stand-in verdict is recorded.

### Delivery evidence

The PR body carries the delivery evidence: `## Summary`, a `## Test plan` of `- [ ]` items, `## Findings / blockers`, `## Test evidence`, and `## Open debt`. The canonical presentation is `.agents/skills/git-pr/references/_pr-evidence-format.md`; assembly and publication are `.agents/skills/git-pr-workflow/SKILL.md`.

- Every required test-plan item is checked with the observed result that verifies it. An unchecked required item means the delivery is **not ready**.
- Every finding carries its ID, severity, status and evidence. An open `BLOCK` finding means **not ready**.
- The trailing verdict line (`[PASS] — basis`, `[ADVISORY] — basis`, `[BLOCK] — basis`) states delivery readiness and the evidence it rests on. Its basis names whether an independent review ran. **The line is optional**: a delivery with no requested review is valid and the body ends without a verdict line.
- **The absence of a verdict never hides a failure.** A missing verdict is never grounds for readiness, and a failed required check, an applicable guarantee that remains unestablished, an unchecked item, or an open `BLOCK` finding keeps the delivery not ready whether or not a verdict line is present.
- Verification evidence is attributed truthfully: the executor, the exact command and the observed result. An author's self-review is described as self-review and never as independent verification.

### Finding actions

After a review round, or when a user report or failed check produces findings, apply `.aicore/core/knowledge/agents.md` `### Finding disposition` and `### Delivery readiness and findings`. Fix-first decides each finding; a deferral needs explicit user authority and a named durable destination; refutation preserves the evidence that settles it. No tracker or additional approval step is introduced.

### Post-merge reporting

After merge, verify and report the outcome; do not automatically edit tracked files or create bookkeeping commits solely to record merge or cleanup facts. A separately requested post-merge documentation change remains authorized through the normal task-branch route, subject to existing authority and gates. Commit and cleanup mechanics remain with Herald 📯 (Release Manager) in `.opencode/agents/herald.md`; this timing rule changes no cleanup authorization or safeguard.

### Execution owners

- Git and GitHub operations of every kind — repository inspection, branch, worktree, staging, commit, push, PR creation, PR-body publication, delete — are executed by Herald 📯 (Release Manager) alone. Every other agent obtains Git- and GitHub-derived evidence from Herald 📯 (Release Manager) and never runs the command.
- PR publication procedure: `.agents/skills/git-pr-workflow/SKILL.md` (content preparation stays in `.agents/skills/git-pr/SKILL.md`)
- PR body format: `.agents/skills/git-pr/SKILL.md` and `.agents/skills/git-pr/references/_pr-evidence-format.md`; the presentation standard is `git-pr`'s reference
- Cleanup proof: the native merge-proof procedure in `.opencode/agents/herald.md` step 8 — the PR's recorded merge commit reachable from the verified base, together with the verified PR identity and the pinned local and remote branch tips. It is evidence only, never authorization, and no separate validator runs.
- A pull-request merge is never an agent operation. Merging is the user's alone under every instruction.
- Finding presentation: `.aicore/core/knowledge/agents.md` `### Delivery readiness and findings`
