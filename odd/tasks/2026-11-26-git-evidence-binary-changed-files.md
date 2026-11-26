# Git evidence preparation for binary changed files

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-26
> **Objective:** Correct the distributed `git-pr-workflow` evidence preparation so a legitimate binary changed file no longer fails textual processing, while every changed path remains in the changed-file inventory.
> **Branch:** fix/git-pr-workflow-binary-changed-files
> **Delivery:** single inline unit; forecast ~150 authored additions + deletions (generated files excluded); slice boundaries: (1) Git classification and inventory correction plus its input reference, (2) regression fixtures and tests, (3) verification, review and delivery evidence.
> **Runner:** pnpm --dir .agents/skills/git-pr-workflow exec vitest run

## Specs

- S1 — A changeset that contains a binary file completes evidence preparation instead of failing. Exact requirement: `When a Git changeset contains a binary file, such as a PNG screenshot, the evidence preparation workflow fails with: git read failure: git output was not valid UTF-8`. Acceptance: run the local preparation command against a fixture repository whose commit range adds a binary file, and read the exit status; it is 0 with `{"status": "prepared", "command": "prepare-local"}`.
- S2 — Every changed path stays in the changed-file inventory, including binary ones. Exact requirement: `Retain every changed path in the inventory, including binary files.` Acceptance: read the emitted snapshot for a mixed changeset and compare its changed-file paths with the exact diff inventory; the binary path is present among them.
- S3 — Textual processing is skipped only for paths Git itself classifies as binary. Exact requirement: `Do not rely exclusively on hardcoded file extensions to identify binary files.` Acceptance: read the binary classification for a mixed changeset that also changes a non-UTF-8 file whose extension is textual; the non-UTF-8 path is absent from the classification while the binary path is present.
- S4 — Malformed textual content is still rejected, never reclassified as binary. Exact requirement: `Continue rejecting malformed textual input where the current contract requires rejection. Do not silently classify malformed text as binary merely to bypass validation.` Acceptance: run the local preparation command against a changeset that changes a non-UTF-8 text file; it exits 2 with `git read failure: git output was not valid UTF-8` and produces no snapshot.
- S5 — Existing attribution, generated-body and persisted-body verification gates are unchanged. Exact requirement: `Preserve existing attribution checks. Preserve existing generated-body and persisted-body verification.` Acceptance: run the skill's suite; the attribution scan and persisted-body verification cases pass while a prepared snapshot that carries a binary path is scanned without a match.
- S6 — Existing addition, modification, deletion and rename behavior is preserved. Exact requirement: `Preserve applicable file addition, modification, deletion, and rename behavior.` Acceptance: run the local preparation command against a changeset that adds, modifies, deletes and renames paths; the snapshot carries the rename destination, the deleted path and the modified path content.

## Tasks

- T1 | S1, S2, S3, S4, S6 | inline (single contained defect in one skill's infrastructure and application layers) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T2 | S1, S2, S3, S4, S5, S6 | inline (regression coverage for the corrected behavior) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T3 | S5 | inline (verification, requested independent review and delivery evidence) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending

## Log

- L1 — original request, verbatim:

````
A defect in the AICore-distributed `git-pr-workflow` skill has been identified during the preparation of PR #197 in TISmart Support.

I need you to investigate and correct this defect at its authoritative source in AICore.

## 1. Reported problem

The TISmart Support agent identified the following components:

- `.agents/skills/git-pr-workflow/scripts/pr_review/infrastructure/git_reader.ts`
- `.agents/skills/git-pr-workflow/scripts/prepare_pr_evidence.ts`
- Associated evidence preparation, snapshot validation, and attribution scanning components.

When a Git changeset contains a binary file, such as a PNG screenshot, the evidence preparation workflow fails with:

`git read failure: git output was not valid UTF-8`

The reported cause is that the implementation attempts to decode binary file contents as UTF-8 text.

Git itself successfully handles the binary file. The commit, push, and PR creation are not the problem. The failure occurs in AICore's evidence preparation and mandatory publication verification workflow.

Verify this diagnosis against the actual implementation before making changes.

## 2. Expected behavior

The intended correction is simple:

**Binary files must be excluded from operations that require textual file contents, but they must remain included in the complete changed-file inventory.**

For example:

| File | Include in inventory | Process as text |
|---|---|---|
| main.ts | Yes | Yes |
| SKILL.md | Yes | Yes |
| config.json | Yes | Yes |
| evidence.png | Yes | No |
| report.pdf | Yes | No |
| archive.zip | Yes | No |

The presence of a legitimate binary artifact must not prevent the Git workflow from preparing evidence, verifying attribution, or completing the publication process.

This does not authorize bypassing any existing security or publication policies applicable to binary files.

## 3. Investigate before implementing

Determine:

- Which Git operation retrieves binary file contents.
- Why the workflow attempts to decode those contents.
- Which operations actually require textual file contents.
- Which operations only require the changed-file inventory.
- How Git already distinguishes textual changes from binary changes.
- Whether local and snapshot preparation modes have the same limitation.

Evaluate whether existing Git mechanisms, such as `git diff --numstat`, can provide the required distinction without introducing additional infrastructure.

Do not assume that the destination agent's suggested implementation is necessary.

## 4. Implementation requirements

Prefer the smallest correction that satisfies the existing workflow contract.

The implementation must:

- Retain every changed path in the inventory, including binary files.
- Skip textual-content processing for correctly identified binary files.
- Preserve strict UTF-8 validation wherever textual content is required.
- Preserve existing attribution checks.
- Preserve existing generated-body and persisted-body verification.
- Preserve applicable file addition, modification, deletion, and rename behavior.
- Continue rejecting malformed textual input where the current contract requires rejection.

Do not silently classify malformed text as binary merely to bypass validation.

Do not rely exclusively on hardcoded file extensions to identify binary files.

Do not fabricate textual contents for binary files.

Do not introduce any of the following unless the investigation establishes a genuine contractual requirement:

- Additional content hashes.
- Binary file size tracking.
- New evidence descriptors.
- New schemas.
- New configuration options.
- Additional dependencies.
- New architectural abstractions.

The objective is to correct an implementation defect, not redesign the Git evidence workflow.

## 5. Preserve existing contracts

The only authorized behavioral correction is that legitimate binary files must no longer cause text-processing failures in the Git evidence workflow.

Preserve all other valid functionality, observable contracts, security guarantees, and mandatory publication gates.

Do not weaken verification to accommodate binary files.

If the existing evidence contract explicitly requires textual contents for every changed path and cannot represent binary files without a material contract change, explain the conflict and propose the smallest viable correction before proceeding.

Consult me only if such a material decision is genuinely required.

## 6. Regression validation

Use the existing test framework and proportionate fixtures.

Demonstrate that:

- Text-only changesets continue to work.
- Binary-only changesets can be processed.
- Mixed textual and binary changesets can be processed.
- Binary paths remain in the changed-file inventory.
- Binary contents are not incorrectly decoded as UTF-8.
- Existing textual attribution detection continues to work.
- Generated-body and persisted-body verification remain mandatory and functional.
- Invalid textual input continues to be handled according to the existing contract.

Evaluate both local and snapshot preparation paths where applicable.

Use small synthetic binary fixtures. Do not access TISmart Support operational screenshots or production data.

Do not create unnecessary testing infrastructure or duplicate existing coverage.

## 7. Architecture and scope

Follow the current AICore architecture, TypeScript standards, shared tooling conventions, skills-first workflow, and ODD workflow.

Apply architecture proportionately.

Work exclusively in AICore.

Do not:

- Modify TISmart Support or other destination repositories.
- Trigger synchronization to destination repositories.
- Modify unrelated skills.
- Remediate unrelated technical debt.
- Redesign the Git workflow.
- Change the publication contract unnecessarily.
- Introduce exceptions specific to TISmart Support PR #197.

This correction must benefit all repositories receiving the distributed `git-pr-workflow` skill.

## 8. Execution and delivery

You are authorized to investigate and implement the minimum correction described above, provided it preserves the existing contracts.

Do not request approval for implementation details already governed by the project standards.

If the correction requires a material change to architecture, public contracts, security guarantees, or evidence schemas, explain why and consult me.

Herald remains the exclusive authority for Git and GitHub operations.

Create one dedicated branch and one PR for this correction.

Inspect and preserve any unrelated existing local changes. Do not include them in this dedicated PR without my authorization.

Complete the independent review required by the current skills-first workflow.

Do not merge the PR.

## 9. Final report

Provide:

1. Confirmed root cause and exact failing Git operation.
2. Explanation of how textual and binary files are distinguished.
3. Minimum implementation correction.
4. Exact changed files.
5. Confirmation that binary paths remain in the inventory.
6. Confirmation that existing contracts and mandatory gates are preserved.
7. Regression tests and their results.
8. Independent review findings and dispositions.
9. PR URL, branch, and final head SHA.
10. Synchronization implications for destination repositories.
11. Remaining blockers or limitations.
12. Explicit final completion status.

Do not declare READY FOR MERGE while mandatory gates or blocking findings remain unresolved.

Keep the solution simple: skip binary contents when processing text, retain the complete file inventory, and preserve the existing workflow.

Proceed.
````

- L2 — Investigation outcome: confirmed root cause is `GitReader.readFile` (`git show <commit>:<path>`), whose captured stdout is decoded with a fatal UTF-8 `TextDecoder`; `CollectLocalInventory` calls it for every non-deleted changed path, so one binary blob aborts `prepare-local` with `git read failure: git output was not valid UTF-8`. Git already classifies a change as binary in `git diff --numstat` (two `-` fields), which honours `.gitattributes`; the snapshot path takes an already-decoded JSON input and needs no change. Correction: read that classification and skip only the body read for a path Git reports as binary, keeping the path in the inventory with empty content (the same representation already used for deleted paths), so no schema, field, dependency or abstraction is added. Detail: this record, `## Specs`.
