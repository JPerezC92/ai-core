---
name: git-pr-workflow
description: Define the pull-request publication workflow — immutable-head identity, evidence preparation, attribution scanning, the single publication write, and persisted-body consistency — and delegate every Git and GitHub execution to Herald 📯 (Release Manager). Use when preparing a pull request for publication, handing a review off, or verifying a published pull-request body.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 1.1.0
  domain: git
---
<!-- core:begin -->

## Ownership

- The **designated evidence writer** (Inquisitor 🔎 (PR Reviewer) when the roster is installed) owns every findings row, test-evidence row, checkbox tick, open-debt entry and the verdict; it authors and validates `output/pr-working-body.md` and never delegates that authorship.
- **Herald 📯 (Release Manager)** is the sole Git and GitHub executor: it reads the repository and GitHub state, executes `gh pr create`, executes the single `gh pr edit <number> --body-file output/pr-working-body.md` publication the writer authorizes, and returns the persisted capture. It never authors, approves, repairs or modifies review evidence.
- **Cipher 🔓 (Lead Orchestrator)** coordinates the sequence and the handoffs, and executes no Git or GitHub command.

## Command ownership

- `.agents/skills/git-pr/scripts/prepare_pr_review.py` owns the two content commands: `initialize` and `validate`. Their names and arguments are unchanged.
- `.agents/skills/git-pr-workflow/scripts/prepare_pr_evidence.ts` owns the four workflow commands: `prepare-local`, `prepare-snapshot`, `snapshot` and `verify`. Their names, arguments and exit codes are unchanged from the previous single CLI.
- This skill's utilities run natively on Node.js `>=24.12.0` with no runtime dependency, no build step and no bundle; a destination runs them as they stand, with nothing installed.
- The argument contracts, the supplied-file schemas and the exit codes live in `references/_pr-workflow-inputs.md`.

## Sequence

1. The content owner drafts the title and body into `output/pr-draft.md` through `git-pr`.
2. Herald 📯 (Release Manager) establishes the immutable head identity — PR number, URL, head OID, base branch and state — from the authenticated live capture, and pins them for the whole flow.
3. The writer initializes the single body-only document: `prepare_pr_review.py initialize --draft output/pr-draft.md --working-body output/pr-working-body.md`. This is the one authoritative rejection point for a malformed creation draft.
4. Herald 📯 (Release Manager) prepares the immutable review evidence: `prepare_pr_evidence.ts prepare-local --pr <number> --base $BASE --draft output/pr-draft.md --working-body output/pr-working-body.md --output SNAPSHOT`. `prepare-snapshot` and `snapshot` are the supplied-inventory and supplied-scanner-shape alternatives; reuse `scripts/scan_attribution.ts` through its existing authorized route.
5. The writer accumulates the canonical review sections in `output/pr-working-body.md`, joins each row and tick together, and validates the candidate: `prepare_pr_review.py validate --baseline BASELINE --current CURRENT --working-body output/pr-working-body.md` with `--decisions DECISIONS` when exclusions, acceptance or debt require it. `BASELINE` and `CURRENT` must be two independently captured observations of the same pull request: passing one capture as both arguments satisfies the equality comparison without proving anything, and so invalidates the freshness check.
6. Herald 📯 (Release Manager) executes the ONE publication write against the exact validated body file, and returns the persisted capture.
7. The writer validates the persisted capture against the capture schema before verifying: `prepare_pr_review.py validate --baseline PERSISTED --current PERSISTED --working-body output/pr-working-body.md`. Passing the persisted capture as both captures applies the full seven-field schema to it and re-checks the published body's structure, without duplicating the schema in this skill. This same-capture call is a schema application only and establishes no freshness, because both arguments are deliberately the same observation.
8. The writer verifies persistence: `prepare_pr_evidence.ts verify --baseline BASELINE --current PERSISTED --working-body output/pr-working-body.md`, then scans the actual persisted body for attribution and completes the final live reread. The writer — not the executor — performs these steps.

## Required properties

- Exactly one publication write happens; there is never an intermediate body upload.
- A changed head, a divergent body, a failed upload or a failed reread blocks acceptance.
- A missing or partial evidence row leaves the item unchecked.
- The persisted-body attribution scan and the final live reread are both mandatory before any gate.
- The final local working body is scanned for attribution over the exact bytes being uploaded, immediately before the single publication, and an attribution match blocks that upload. That scan neither replaces nor is replaced by the scan of the persisted body; both are required.
- The local draft and working body remain the authoritative content; GitHub is the publication destination, not a source for reconstructing prose.

## Stop conditions

- The head moved since it was pinned.
- A capture is not authenticated, or is not the pinned one.
- A validation or readback fails.
- The persisted body carries an attribution match.
- An evidence row does not correspond to a checked item.
- The PR state is other than open at review time.

## Rules

- This skill executes no Git or GitHub command — Herald 📯 (Release Manager) runs every command it names.
- It never authors or repairs review evidence.
- It never introduces an authorization system of its own.
- It adds no new validator, state machine or wrapper.
- The canonical body format stays in `.agents/skills/git-pr/references/_pr-evidence-format.md`.
- This contract never merges a pull request, by any mechanism including the GitHub API and browser automation; the merge belongs to the user alone and no step in this sequence performs it.
<!-- core:end -->
