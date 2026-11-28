---
name: git-pr-workflow
description: Define the pull-request publication workflow — immutable-head identity, evidence preparation, attribution scanning, the single publication write, and persisted-body consistency — and delegate every Git and GitHub execution to Herald 📯 (Release Manager). Use when preparing a pull request for publication, handing a review off, or verifying a published pull-request body.
license: MIT
compatibility: opencode
metadata:
  author: Philip Perez Castro
  version: 2.1.1
  domain: git
---

<!-- core:begin -->

## Ownership

- The **delivery evidence owner** — the agent that prepared the change — owns every findings record, test-evidence record, test-item status, open-debt entry and the readiness statement in the publication input, and the generated body it produces; it authors and validates them and never delegates that authorship.
- The **content owner** is that same agent for its own delivery: it owns the title, the summary, the breaking changes and the test-plan item text in that same publication input; a later evidence update never rewrites those authored fields.
- **Herald 📯 (Release Manager)** is the sole Git and GitHub executor: it reads the repository and GitHub state, executes `gh pr create`, executes the single `gh pr edit <number> --body-file <generated body>` publication the evidence owner authorizes, and returns the persisted capture. It never authors, approves, repairs or modifies delivery evidence.
- **Cipher 🔓 (Lead Orchestrator)** prepares the evidence and the generated body, and executes no Git or GitHub command.
- **The user** is the final reviewer of a published pull request and the only person authorized to merge it. No agent performs that review on the user's behalf, and no agent merges a pull request by any mechanism.
- **An independent review is optional.** When the user requested one, its findings and verdict join the publication input as evidence with their dispositions. When none was requested, the input carries no verdict and the body ends without a verdict line; nothing stands in for it.

**Preparation paths per context.** Every `output/pr-publication.json` and generated-body path in this skill is the single-context default. A delivery that prepares more than one pull request supplies, for each context, its own distinct publication-input and body paths inside one preparation directory; that directory is the context's identity, and the existing exclusive-create behavior never overwrites an occupied path. Paths in the commands below substitute the context's own pair for the default.

**Generated artifacts.** The Markdown body is generated from the publication input by `git-pr`; no agent authors, edits or reuses a body as an input. Every generated body is an exclusive artifact with its own receipt `<body>.receipt.json`, so a later stage generates into a fresh body path and the earlier artifact remains as history.

**No prior-state comparison.** Generating and publishing a description depends only on the current publication input. No command compares a generated body with an earlier body, a prior publication input, a captured snapshot or a previously published description, and no receipt or snapshot keeps a digest of an earlier state. A review update is a fresh generation from the current input, not a diff against what was published before.

## Command ownership

- `.agents/skills/git-pr/scripts/prepare_pr_review.ts` owns the one content command: it prepares a body and its receipt from the JSON publication input.
- `.agents/skills/git-pr-workflow/scripts/prepare_pr_evidence.ts` owns the four workflow commands: `snapshot`, `prepare-snapshot`, `prepare-local` and `verify`.
- This skill's utilities run natively on Node.js `>=24.12.0` with one runtime dependency, `zod` (declared in `package.json`), no build step and no bundle; a destination provisions that one package beside the skill and runs the utilities as they stand. No development package is required at run time.
- The argument contracts, the supplied-file schemas and the exit codes live in `references/_pr-workflow-inputs.md`.

**Runtime dependency.** The skill declares exactly one runtime dependency, `zod` `4.6.7` in `package.json`. Every outside-document decoding step — the local inventory, the scanner snapshot and policy, and the `verify` capture pair — runs through Zod schemas in the infrastructure adapters; the domain and application layers hold typed records and business rules only. A destination provisions that package inside the skill directory (for example by running the package manager against `.agents/skills/git-pr-workflow/`, which creates `node_modules/zod`) and needs nothing else: there is no build step, no bundle and no development package at run time. The isolated-copy test copies `node_modules/zod` into its temporary copy, and asserts that only the declared runtime dependency is present.

## Sequence

The protocol has two stages over one content command. **Initial creation** publishes the generated creation body. **Evidence publication** then replaces that body once with the generated evidence body. Steps 5 to 9 belong to the evidence-publication stage: `prepare_pr_evidence.ts` and the scanner snapshot both require a positive `pr_number`, so no snapshot and no snapshot scan of the creation body is possible before step 3 creates the pull request, and none is implied by this sequence.

1. The content owner authors the publication input — `output/pr-publication.json` — through `git-pr`, in the shape of `.agents/skills/git-pr/references/_pr-publication-input.md`. No Markdown is authored.
2. The writer generates the creation body and its receipt: `prepare_pr_review.ts --input output/pr-publication.json --output output/pr-working-body.md`. The command creates the body exclusively, writes `output/pr-working-body.md.receipt.json` beside it and prints the receipt `{"status":"prepared","title":"<title>"}`. This is the one authoritative rejection point for an invalid input.
3. **Initial creation.** The writer inspects the exact bytes of the generated creation body for attribution. That inspection is the always-on attribution prohibition of `.opencode/agents/herald.md` `#### PR lifecycle`; it is not the step 7 scan, and it is never reported as one. Herald 📯 (Release Manager) then creates the pull request from that creation body and the title recorded in its receipt, and returns the persisted capture. The creation body keeps the canonical creation shape, including the `No review findings yet.` findings placeholder, and carries no evidence-stage result.
4. Herald 📯 (Release Manager) establishes the immutable head identity — PR number, URL, head OID, base branch and state — from the authenticated live capture of the pull request created at step 3, and pins them for the whole flow.
5. The writer generates the evidence body into a fresh body path from the current publication input, by the same command as step 2: the writer records the review findings, evidence and verdict in the publication input and generates a fresh body with its own receipt. The creation body and its receipt remain as history.
6. Herald 📯 (Release Manager) prepares the immutable review evidence: `prepare_pr_evidence.ts prepare-local --pr <number> --base $BASE --receipt <evidence body>.receipt.json --body <evidence body> --output SNAPSHOT`, where `<number>` is the number pinned at step 4 and the receipt and body are the step 5 pair. `prepare-snapshot` and `snapshot` are the supplied-inventory and supplied-scanner-shape alternatives; reuse `scripts/scan_attribution.ts` through its existing authorized route. The receipt supplies the generated title; this workflow never reads the publication input and never compares the supplied artifacts with an earlier state.
7. The writer scans the exact bytes it will publish: run the attribution scanner over the prepared snapshot, whose title and body artifacts are the generated title and the generated evidence body. Any attribution match blocks the upload.
8. Herald 📯 (Release Manager) executes the ONE evidence-publication write against the exact generated evidence-body file, and returns the persisted capture. The initial `gh pr create` at step 3 is a separate creation operation and is not a second publication write.
9. The writer verifies persistence: `prepare_pr_evidence.ts verify --baseline BASELINE --current PERSISTED --body <evidence body>`, then scans the actual persisted body for attribution and completes the final live reread. `BASELINE` is the intended capture the writer holds for this publication — the authenticated live observation of the pull request it is publishing against — and `PERSISTED` is the fresh capture Herald 📯 (Release Manager) returns after the write; both are supplied in the same seven-field form. The writer — not the executor — performs these steps. The persisted capture must carry exactly the intended capture's field set and values, and its body must equal the published body bytes.

## Required properties

- Exactly one evidence-publication write happens; initial creation is a separate `gh pr create`, and there is never an intermediate body upload.
- A changed head, a divergent body, a failed upload or a failed reread blocks acceptance.
- A missing or partial evidence record leaves the item pending.
- The attribution scan of the evidence body before its publication and the attribution scan of the persisted body after it are both mandatory; neither replaces the other, and a delivery whose evidence body has not passed both is never reported ready. A generated creation body is covered by the always-on attribution prohibition it is inspected under at step 3, not by this scan, because the scanner snapshot requires a PR number that creation has not yet produced.
- The persisted description must equal the intended body bytes exactly. That check confirms GitHub persisted the content of this publication; it is not a comparison against an earlier body.
- The publication input remains the authoritative content and the generated body is its artifact; GitHub is the publication destination, not a source for reconstructing prose.

## Stop conditions

- The head moved since it was pinned.
- A capture is not authenticated, or is not the pinned one.
- The supplied receipt, body or inventory is missing, unreadable, or not the prepared artifact.
- A validation or readback fails.
- The persisted body carries an attribution match.
- An evidence record does not correspond to a checked item.
- The PR state is other than open at review time.

## Rules

- This skill executes no Git or GitHub command — Herald 📯 (Release Manager) runs every command it names.
- It never authors or repairs review evidence, and never authors Markdown publication content.
- It never introduces an authorization system of its own.
- It adds no new validator, state machine or wrapper.
- It asks for, stores and compares no prior publication state: no prior-publication input, no decisions file, no receipt digest, no snapshot digest, no protected-section exception and no previous body. Every decision travels in the publication input.
- The canonical body format stays in `.agents/skills/git-pr/references/_pr-evidence-format.md`, and the publication input contract stays in `.agents/skills/git-pr/references/_pr-publication-input.md`.
- This contract never merges a pull request, by any mechanism including the GitHub API and browser automation; the merge belongs to the user alone and no step in this sequence performs it.
<!-- core:end -->
