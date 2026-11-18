# Core Sync implementation boundaries and test reorganization

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-18
> **Objective:** Correct the confirmed Core Sync implementation-responsibility and architectural-boundary violations and reorganize its tests — including the byte-exact behavioral-parity corpus — onto the boundaries that own them, without losing regression coverage, in exactly one pull request.
> **Branch:** `fix/core-sync/implementation-and-test-boundaries` — authorized in this slice; created by Herald 📯 (Release Manager) from `main` at `65b869fcc53a6baa82ed769ab8850b89dfe3b6b4` after this record is written.
> **Delivery:** one PR, mandatory by user instruction; forecast ~1050 authored additions + deletions (production ~450, tests ~600), above the ~400 feature-level trigger, so the strategy is reviewable work-unit commits inside the one PR — the P5 production correction, the parity-corpus seam re-binding, the P6 level reorganization, then records and evidence.
> **Runner:** `pnpm --dir cli/aicore test`; `pnpm --dir cli/aicore test:e2e`; `pnpm --dir cli/aicore typecheck`; `pnpm format:check`; `pnpm lint`; `pnpm typecheck`; `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks`; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts odd/features`

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — Core Sync's production responsibilities sit in the layer that owns them. Exact requirement: "**P5:** Correct Core Sync implementation responsibilities and architectural boundaries." Acceptance: read the delivered Core Sync production modules against the implementation contract; no infrastructure module imports the delivery edge, adapter composition and domain-result serialization occur only at the delivery edge, the capability the application operations call speaks domain types rather than a command-line vector with process exit status and streams, and no application operation fabricates a command line that a second module parses back.
- S2 — The correction changes no externally observable synchronization behavior. Exact requirement: "Reorganize Core Sync testing, including the existing byte-exact parity corpus, without losing regression coverage." Acceptance: run the parity corpus at the delivered head and read its result; every case reports the same exit status, standard output, standard error and resulting destination tree it reported at the verified baseline.
- S3 — No unique regression assertion is lost. Exact requirement: "without losing regression coverage." Acceptance: read the delivered assertion-preservation mapping; every relocated or retired case names the assertion it protected and the surviving assertion or the demonstrated duplicate that replaces it, and no case count falls without one.
- S4 — The behavioral-parity corpus runs at the level it actually exercises. Exact requirement: "Reorganize Core Sync testing, including the existing byte-exact parity corpus". Acceptance: run the package's end-to-end command and read the suite layout; the whole parity corpus executes there and no parity case remains under the unit or integration suites.
- S5 — Every Core Sync test exercises the boundary it is filed at. Exact requirement: "**P6:** Reorganize Core Sync testing". Acceptance: read each delivered Core Sync test module and measure its level at the boundary it actually exercises; every module's filed level matches the level measured, and every subject with no legitimate level is named with its ruling rather than relabelled.
- S6 — A unit case that targeted an unapproved subject survives only once its assertion lives at an approved boundary. Exact requirement: "adequate regression protection and maintainable tests". Acceptance: read the delivered unit suite; each affected case is either absent with its assertion present on the consuming application operation's `execute()` unit, or retained with a recorded architecture ruling naming the level it belongs to.
- S7 — The delivery is exactly one pull request containing both corrections. Exact requirement: "Deliver P5 and P6 together in exactly ONE pull request." and "Do not split implementation remediation and test remediation into separate PRs." Acceptance: list the pull requests targeting `main`; exactly one exists and its base-to-head diff carries both the production correction and the test reorganization.
- S8 — No later phase is begun and no accepted earlier delivery is reopened. Exact requirement: "Do not begin P7 or reopen previously accepted P0–P4 implementations." Acceptance: inspect the base-to-head diff; no path outside Core Sync and its records changed, and no previously delivered correction in another package is reverted or redecided.
- S9 — Implementation starts from a verified baseline in which the prerequisite delivery is actually merged. Exact requirement: "Do not assume PR #197 has merged solely because its review passed." and "If #197 remains unmerged, do not create the P5/P6 branch from an outdated baseline." Acceptance: read the release owner's reported merge identity and compare it with the verified `origin/main` tip; the branch is created from that same revision.
- S10 — Unrelated working state is preserved and no destructive Git operation is used. Exact requirement: "Preserve unrelated staged, unstaged and untracked files." and "Do not perform destructive cleanup, stashing, resets or unsafe branch operations." Acceptance: compare the release owner's pre-branch and post-branch status reports; every unrelated path is byte-identical and no stash, reset, clean, forced checkout or worktree removal was performed.
- S11 — The reported distribution is measured and honest, and no exception is accepted. Exact requirement: "The objective is architectural correctness, adequate regression protection and maintainable tests — not achieving attractive numbers." Acceptance: read the delivered report and pull-request body; each test-owning unit's counts are stated at its verified boundaries, every remaining deviation from the ordering is named as unresolved, and no deviation is recorded as accepted.
- S12 — Every Git-derived fact in this record comes from the release owner. Exact requirement: "Herald 📯 is the only agent authorized to execute Git/GitHub operations." Acceptance: read this record's baseline and delivery entries; each Git state, revision and merge fact names the release owner as its source.

## Tasks

- T1 | S1 | delegated (production source correction under Forge 🔨 ownership; the Core Sync application, delivery, domain and infrastructure modules and their composition) — Forge 🔨 (Implementer) | open | commit: pending
- T2 | S2 | delegated (runner execution and behavior-preservation evidence under Forge 🔨 ownership; the package suites and the parity corpus) — Forge 🔨 (Implementer) | open | commit: pending
- T3 | S3, S4, S5, S6 | delegated (test authoring and reorganization under Forge 🔨 ownership; the four test levels and the parity-corpus seam) — Forge 🔨 (Implementer) | open | commit: pending
- T4 | S1 | delegated (C1, C2, C3, C4, C6 and scripts-shape P2/P4 conformance of the corrected Core Sync modules) — Bastion 🧱 (Backend & Scripts Architect) | open | commit: pending
- T5 | S3, S4, S5, S6, S11 | delegated (test-architecture risk: level reclassification, corpus relocation, assertion equivalence, measured distribution) — Crucible 🔥 (Test Architect) | open | commit: pending
- T6 | S11, S12 | inline (the governing record, the debt-register disposition and the distribution report, Cipher 🔓 owns the ODD lifecycle) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T7 | S7, S8, S9, S10 | delegated (sole Git executor: branch, focused commits, push, one pull request) — Herald 📯 (Release Manager) | open | commit: pending
- T8 | S2, S3, S5, S7, S8, S11 | delegated (independent review at the immutable pull-request head) — Inquisitor 🔎 (PR Reviewer) | open | commit: pending
- T9 | S11, S12 | delegated (record, debt-register and instruction-document consistency audit) — Sentinel 🛡️ (Quality Guardian) | open | commit: pending

## Log

- L1 — Original request, verbatim:

  # AICore — P5 + P6: Core Sync Architecture and Testing Remediation

  We are starting a NEW OpenCode session.

  ## Objective

  Continue the existing AICore architecture and testing remediation initiative.

  This delivery combines:
  - **P5:** Correct Core Sync implementation responsibilities and architectural boundaries.
  - **P6:** Reorganize Core Sync testing, including the existing byte-exact parity corpus, without losing regression coverage.

  **Deliver P5 and P6 together in exactly ONE pull request.**

  Do not split implementation remediation and test remediation into separate PRs.

  Do not begin P7 or reopen previously accepted P0–P4 implementations.

  The objective is architectural correctness, adequate regression protection and maintainable tests — not achieving attractive numbers.

  ---

  ## 1. Verify the repository state

  Herald 📯 is the only agent authorized to execute Git/GitHub operations.

  Before implementation, verify:
  - Current local branch and HEAD.
  - Current remote `main`.
  - Working-tree and worktree safety.
  - Whether PR #197 has actually been merged into `main`.
  - The current Core Sync source and test layout.
  - Existing architectural contracts and technical debts relevant to this slice.

  PRs #195 and #196 were previously merged, and PR #197 was reported ready for the user's merge decision.

  **Do not assume PR #197 has merged solely because its review passed.**

  If #197 remains unmerged, do not create the P5/P6 branch from an outdated baseline. Report that precise prerequisite.

  Preserve unrelated staged, unstaged and untracked files.

  Do not perform destructive cleanup, stashing, resets or unsafe branch operations.

  Read the actual contracts rather than relying on previous agent summaries, particularly:
  - Domain/application/infrastructure/delivery responsibilities.
  - C1, C3, C4 and C7.
  - T2, T4, T5, T8, T9, T10 and T21.
  - Test proportionality and the approved progressive-remediation rule.
  - ODD task creation, evidence, independent acceptance and closure.
  - Existing Git/GitHub role restrictions

- L2 — 2026-11-18 — Classification: **non-small**. Understood: the thirteen Core Sync production modules, the four test levels with the 65-case parity corpus and its seam, the implementation contract C1–C10, the scripts shape P1–P4, the testing contract T1–T36, the debt register and the durable feature files were read before this record existed. Risk-contained: no — the slice retypes a domain port, removes a composition/serialization boundary and re-levels the package's whole test suite. Resumable from request plus diff: no. This record is therefore the sole bootstrap write; no other mutation preceded it.
- L3 — 2026-11-18 — Baseline, from the release owner's read-only report. Local branch `main`, `HEAD` = local `main` = `origin/main` = `65b869fcc53a6baa82ed769ab8850b89dfe3b6b4`; `git status --short --branch` reports no divergence and zero staged, unstaged or untracked entries. **PR #197 is `MERGED`** with recorded merge commit `65b869fcc53a6baa82ed769ab8850b89dfe3b6b4`, identical to the `origin/main` tip and its squash subject carrying `(#197)`; PRs #195 (`8c1ed8dc`) and #196 (`2d7be824`) are also `MERGED` and present in the linear history. S9's prerequisite is therefore discharged. Three worktrees exist: this checkout plus two pre-existing detached-HEAD leftovers from the PR #192 work, which this change preserves untouched. No unrelated work exists, so nothing has to be isolated.
- L4 — 2026-11-18 — Independent architecture analysis by Bastion 🧱 over every production module of `cli/aicore`: `VIOLATIONS CONFIRMED`, four of them in this slice's scope — infrastructure statically imports the delivery edge (`src/infrastructure/core-sync-engine.ts:14,15` against C1); a module under `src/infrastructure/` both declares itself the composition root and serializes domain results into exit status, stdout and stderr (`:1-8,57-66,70-85,145-172` against scripts-shape P2 and C6); the capability port and its result record speak a command-line vector and process transport (`src/domain/ports/engine-runner.ts:17`, `src/domain/outcomes.ts:13-17` against C2/C10); and an application operation fabricates that vector for a second module to parse back (`src/application/synchronize-destination.ts:89-104` against C4/C6). It **refuted** C3 concern about command routing and argument validation — C3 expressly permits a composition root or CLI router to wire several operations, so only their placement is at issue — and refuted domain, application and `main.ts` impurity by bounded search. It classified `run-advanced-command.ts` as a pass-through wrapper (C3) but `OUTSIDE-P5` on the ground that a prior accepted slice delivered it deliberately. One INFO: the dependency bundle aliased through `ConstructorParameters<typeof VerifyDestinations>[0]`.
- L5 — 2026-11-18 — Independent test-architecture analysis by Crucible 🔥 over every test module: `EXCEPTION REQUIRED`, measured at the boundary each case exercises, not by directory — `unit 54 > integration 24 < end-to-end 83`, total 182, with 21 further cases belonging to no level. Literal runs: `pnpm --dir cli/aicore test` → 37 files, `160 passed | 4 skipped (164)`; `pnpm --dir cli/aicore test:e2e` → 10 files, `18 passed (18)`. It confirmed the 65-case parity corpus as T5 of the assembled engine rather than T4 of one adapter (DEBT-056's `cli/aicore` subject); confirmed the three DEBT-055 unapproved unit subjects plus a fourth; and identified two further silent-pass and weak-assertion defects in the e2e harness and one e2e case. The four skips are honest platform skips, never reported as passed.
- L6 — 2026-11-18 — Two architecture rulings requested and returned before implementation, because the correction design was not self-evident. Bastion 🧱 **refuted** the coordinator's proposed replacement port — a `SynchronizationCommand` seam over the three use cases is itself a C3 pass-through wrapper with no polymorphic need and duplicates `CommandName` — and instead ruled: retire the argv port and its transport record; inject the three existing application operations into their orchestrating collaborators directly; keep the request records in the application layer (C10 assigns request shapes to delivery, C8 bars transport records from domain); move the command-line mapping to the delivery edge that owns argv, not into the domain; remove the delivery import and the serialization call from infrastructure without relocating composition; and declare the dependency bundle explicitly rather than aliasing another operation's constructor. The coordinator's proposed port is therefore **not implemented**; the owner's minimal correction governs T1.
- L7 — 2026-11-18 — Test-level rulings, and one owner conflict recorded rather than papered over. Crucible 🔥 ruled: the two repository-artifact modules fold into the end-to-end module that already delivers the same observable effect, keeping the unique regex assertions at that level; the three reconciliation cases relocate to end to end with their one duplicate read-only case folded; the five `open-code-secrets` cases fold into the `ApplyCoreRevision` unit because that operation passes its own injected ports through; and `tests/integration/disposable-root.test.ts` **refuted** Bastion's own T4 ruling, because the level follows the subject and a shared test utility "never form[s] an additional level". Because that second question is test-architecture authority, the conflict is retained as unresolved rather than decided by the non-owning role: the file is kept unchanged so that no unique safety assertion is lost and no production behavior is invented to manufacture a level, it is counted at no level in the reported distribution, and it is named in this change's evidence as an open classification deviation. Neither owner's ruling approves an exception.
- L8 — 2026-11-18 — Durable feature files read and found unaffected in requirement terms: `odd/features/core-synchronization.md` gains, rewords and retires no requirement, and its R1, R12 and R16 are re-verified as still true by S2's evidence rather than re-ticked; `odd/features/architecture-contract.md` R10 and R17 and `odd/features/cheapest-test-boundary.md` R1 remain unticked, because their subjects are repository-wide and this change does not establish the repository-wide truth they assert — the Core Sync subject improves while the same defects remain in `system-one` and `odd-adviser`. No durable file is edited by this change; the evidence lives here.
- L9 — 2026-11-18 — Full-feature mirror: **pending recovery**, not synchronized. This project's recorded binding states that the first source-contract slice authorized no real feature mirror, that exact-mirror acceptance was retired, and that runtime adoption of full mirroring remains unverified; the backend also lacks exact-key upsert and compare-and-swap, so a complete payload readback cannot be proven. The authoritative record is this repository file, and the next bounded recovery action is a separately authorized mirror probe against the documented tool limits.
