# Root contract-suite retirement

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-14
> **Objective:** Retire the redundant root `tests/` workspace, its hardcoded registries and duplicated helpers, and the obsolete first-party Python artifacts, while leaving synchronization semantics and the CLI's own coverage unchanged.
> **Branch:** `chore/tests/retire-contract-suite`
> **Delivery:** one focused PR as the user mandated; authored additions + deletions forecast ≈ 700 deleted / ≈ 45 added (generated files and `pnpm-lock.yaml` importer churn excluded). The forecast exceeds the advisory ~400-line threshold; no chained slice is used because the user required a single focused PR and the change is deletion-dominant and internally coherent.
> **Runner:** `pnpm --dir cli/aicore test` (surviving synchronization suite); `pnpm --dir cli/aicore typecheck`; `node .agents/skills/odd-workflow/scripts/validate_feature.ts .aicore/core/odd/tasks`; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts .aicore/core/odd/features`. No repository-root suite remains after this change.

## Specs

- S1 — The root contract workspace no longer exists as a package or a workspace member. Exact requirement: "Remove the root tests/ workspace and its unnecessary package configuration." Acceptance: list the workspace members and the checkout root; `tests/` is absent and no workspace entry or root script names it.
- S2 — No active surface still references the removed suite or its helpers. Exact requirement: "Remove obsolete hardcoded test registries and duplicated helper implementations." Acceptance: search the tracked tree for the removed package name, its command and its helper paths; zero matches outside historical ODD records and feature Logs.
- S3 — A markerless source remains valid and is distributed in full, a marked source follows the region rules, and a malformed marker pair keeps its refusal; no marker requirement is introduced for agent specifications. Exact requirement: "A source file WITHOUT region markers is valid and must be shipped in full." / "Do not introduce a requirement that all agent specifications contain markers." / "Do not change production synchronization semantics." Acceptance: run the CLI synchronization suite and read the marker-contract outcomes; the markerless-source, marked-source and malformed-source cases pass with unchanged production code, and no new source-conformance check exists in the tree.
- S4 — The CLI's existing marker coverage is preserved and is not recreated elsewhere. Exact requirement: "Preserve existing CLI synchronization tests covering markerless, marked, and malformed files. Do not recreate the deleted root test suite elsewhere." Acceptance: enumerate the CLI marker-contract cases and run them; the markerless, malformed, reversed-pair and fenced-literal cases exist and pass, and no suite outside the CLI asserts repository agent documents.
- S5 — Obsolete first-party Python artifacts are gone and intentional Python-backed tooling is untouched. Exact requirement: "Complete the previously authorized obsolete Python artifact cleanup, leaving intentional Python-backed tooling untouched." Acceptance: inspect the checkout root and the two tooling projects; the root `.pytest_cache`, `__pycache__` and the retired `.venv` contents are removed, no first-party `.py` file is tracked, and both tooling projects still carry their manifest, lockfile and environment. A single file that a live local process still holds open is not counted as removed; it is reported as a blocked residue with its resolution owner.
- S6 — The work ships as one focused pull request that is not merged by any agent. Exact requirement: "Keep everything in one focused PR" / "Do not merge; merge authority remains mine." Acceptance: one PR is reported with its URL and reviewed head; its state is open and unmerged.

## Tasks

- T1 | S1 | inline (mechanical deletion of a package and its workspace/config wiring; no design decision) — Cipher 🔓 (Lead Orchestrator) | done | commit: bd4737bbbd0f2b35072c04a3b4f26d47e4c60403
- T2 | S2 | inline (prose and permission-row edits across already-read files; owner of the wording) — Cipher 🔓 (Lead Orchestrator) | done | commit: bd4737bbbd0f2b35072c04a3b4f26d47e4c60403
- T3 | S3, S4 | delegated (owns the whole-suite command and its execution) — Forge 🔨 (Implementer) | done | commit: bd4737bbbd0f2b35072c04a3b4f26d47e4c60403
- T4 | S5 | inline (working-tree removal of ignored artifacts; no Git content) — Cipher 🔓 (Lead Orchestrator) | done | commit: bd4737bbbd0f2b35072c04a3b4f26d47e4c60403
- T5 | S6 | delegated (sole Git and GitHub executor) — Herald 📯 (Release Manager) | done | commit: bd4737bbbd0f2b35072c04a3b4f26d47e4c60403

## Log

- L1 — 2026-11-14 — Original request, verbatim:

  > Cipher 🔓 — Correcting the direction: eliminate unnecessary testing infrastructure.
  >
  > I do not want to preserve the root tests/ package simply because its tests existed in Python or because they currently pass.
  >
  > My preferred architectural outcome is to DELETE the root tests/ workspace entirely.
  >
  > The investigation established that several tests freeze incidental documentation, duplicate version metadata, simulate permission enforcement, or reproduce existing parsing logic.
  >
  > Stop treating preservation of the nine-test count as a requirement.
  >
  > ### Required evaluation
  >
  > Identify only the guarantees that would genuinely be lost if root tests/ disappeared.
  >
  > For each guarantee, determine whether:
  > - An existing executable owner already enforces it.
  > - The corresponding requirement is still necessary.
  > - Its absence would create a concrete, material regression risk.
  >
  > Do not automatically replace every removed test.
  >
  > If a necessary control is missing, propose the smallest check within an existing owner. Do not create another package, standalone test suite, custom parser, or generalized validation framework.
  >
  > In particular:
  > - Agent specification creation and validation should remain the responsibility of op-agent-creator.
  > - Synchronization behavior belongs to the CLI.
  > - Permission security must not be represented as harness-enforced simply because a custom matcher passes.
  > - Exact agent-version snapshots should not be preserved without an independent authoritative baseline.
  >
  > ### Python cleanup
  >
  > Complete the missing inventory of remaining first-party Python files, dependencies, generated artifacts, and obsolete references.
  >
  > Distinguish obsolete Python tooling from intentional support for Python destination projects.
  >
  > ### Desired outcome
  >
  > Prefer:
  > 1. Remove the root tests/ workspace and its unnecessary package configuration.
  > 2. Remove obsolete hardcoded test registries and duplicated helper implementations.
  > 3. Retain only genuinely necessary checks through existing owners, where justified.
  > 4. Remove remaining obsolete first-party Python tooling and references.
  >
  > Do not rewrite historical ODD records.
  >
  > ### Scope and authorization
  >
  > This is authorization to produce a minimal deletion-oriented implementation proposal, NOT yet to delete files.
  >
  > Return the exact proposed deletion list, any indispensable missing controls, the Python cleanup inventory, and the smallest implementation scope.
  >
  > Do not start another broad architecture investigation or defend the existing suite simply because it is already implemented.
  >
  > I will decide whether to authorize the deletion after reviewing the specific consequences.
  >
  > Herald remains the sole Git/GitHub executor. Preserve ODD and my exclusive merge authority.

- L2 — 2026-11-14 — User correction and implementation authorization, verbatim:

  > Cipher 🔓 — Critical correction to my previous authorization.
  >
  > I explicitly REJECT the proposed G1 protection requiring every agent specification to contain region markers.
  >
  > The intended core-sync behavior is:
  >
  > - A source file WITHOUT region markers is valid and must be shipped in full.
  > - A source file WITH valid region markers follows the existing region synchronization rules.
  > - Malformed or unmatched region markers follow the existing validation/error contract.
  >
  > Do not introduce a requirement that all agent specifications contain markers.
  >
  > Do not change production synchronization semantics.
  >
  > Do not add an extra source-conformance test that rejects valid markerless files.
  >
  > Proceed with the previously authorized removal of the unnecessary root tests/ workspace, its obsolete configuration, and active references.
  >
  > Preserve existing CLI synchronization tests covering markerless, marked, and malformed files. Do not recreate the deleted root test suite elsewhere.
  >
  > Complete the previously authorized obsolete Python artifact cleanup, leaving intentional Python-backed tooling untouched.
  >
  > Keep everything in one focused PR, preserve ODD, and follow Herald's exclusive Git/GitHub authority.
  >
  > Do not merge; merge authority remains mine.
  >
  > Report only the implementation results, affected test results, PR URL, reviewed head, and genuine blockers.

- L3 — 2026-11-14 — Durable-file reading and retirement decision. Read `.aicore/core/odd/features/typescript-testing.md` and `agent-workforce.md`. `typescript-testing.md` R7 is retired by this change: its condition — a migrated suite is replaced by a Vitest suite that asserts the same behaviour — no longer describes the repository once the ported root suite is deleted by user decision, and the migration history stays with the 2026-11-14 Python-retirement record. R1–R6 are unaffected and keep their ticks. `agent-workforce.md` is read and unaffected: R1 (SemVer `version` on every roster spec) and R3 (authoring skill plus independent audit) hold without the removed suite. No new durable feature file is created, because no enduring capability named by this change survives it.
- L4 — 2026-11-14 — Authorization and scope. The user authorized deletion (L2) after a proposal; the proposal's G1 marker control is rejected and is not implemented. Classification: non-small (multi-surface removal with owner gates). Bootstrap write: this record plus the durable-file update. Execution continues within the authorized scope; no production synchronization code changes.
- L5 — 2026-11-14 — Implementation. Deleted the seven tracked `tests/` files and the directory; removed the workspace entry, the root `test:contracts` script and the `tests` typecheck leg; removed the two Crucible/Forge shell grants that named the deleted command; rewrote every active reference (root runtime, README, PROJECT-STRUCTURE, tooling doc, Warden/Crucible/Forge/Inquisitor/Bastion project regions, Sentinel and shared-rules core citations, op-agent-creator authoring text). No production synchronization code, no sync semantics and no marker requirement was introduced. Sentinel `1.21.1 → 1.21.2` and op-agent-creator `1.5.0 → 1.5.1` bumped as compatible corrections for the distributed-text edits; the first draft over-declared both as minor bumps, and the independent audit corrected the class before delivery. Evidence: the committed diff of this work unit.
- L6 — 2026-11-14 — Verification. `pnpm --dir cli/aicore test` exit 0, 26 files, 116 passed, 3 skipped, 4.94s; focused `pnpm --dir cli/aicore test tests/integration/core-sync-parity/marker-contract.parity.spec.ts --reporter=verbose` exit 0, 8 passed, including "a markerless source's whole post-frontmatter body is its core", "a source carrying project markers without a core pair is malformed and fails closed", "a source whose core pair is reversed is malformed and fails closed" and the fenced-literal case; `pnpm --dir cli/aicore typecheck` exit 0; `pnpm install --lockfile-only --ignore-scripts` exit 0 with no `tests` importer remaining and eight importers reported; feature-record validator exit 0. Evidence: the PR body and Forge's verification returns for this work unit.
- L7 — 2026-11-14 — Python artifact cleanup. Working tree only, all ignored and untracked: `tests/`, `.pytest_cache/` and root `__pycache__/` removed; root `.venv/` reduced to a single locked `Scripts/python.exe`. The two MCP tooling projects and their environments were left untouched, and no first-party `.py` file is tracked. Evidence: Forge's inventory return and `Test-Path` results recorded in the PR body.
- L8 — 2026-11-14 — Blocker, not a failure. Root `.venv/Scripts/python.exe` cannot be deleted: process 42536 runs it as the VS Code black-formatter language server, so the interpreter is held open. Resolution owner: the user (reload or close the VS Code window, then delete the remaining file). The artifact is ignored and untracked and does not affect the tree or the pull request.
- L9 — 2026-11-14 — Delivery. Pull request #187 (`https://github.com/JPerezC92/ai-core/pull/187`) carries the work on `chore/tests/retire-contract-suite`; creation head `bd4737bbbd0f2b35072c04a3b4f26d47e4c60403`, state open and unmerged. Merge authority remains the user's. Evidence: the PR body and the verification returns summarized at L6.
- L10 — 2026-11-14 — Blocked: the independent semantic review of the delivered candidate, and the user's merge decision, are the open closure prerequisites; this record stays active until both exist. Scheduled closure owner is Cipher 🔓 (Lead Orchestrator), and the verdict is published in the pull-request body at its reviewed head.
