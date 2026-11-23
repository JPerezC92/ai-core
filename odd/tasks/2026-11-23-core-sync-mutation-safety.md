# Core Sync mutation safety

> **Status:** closed
> **Closed:** 2026-11-23
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-23
> **Objective:** Preflight effective synchronization mutations without changing valid safe behavior.
> **Branch:** `feat/odd/core-sync-mutation-safety`, created by Herald 📯 (Release Manager) from `c6fe1de8c8c22f5ef4ad85669d21b78b63f2040b`.
> **Delivery:** One security-sensitive delivery across twenty-two paths in nine commits — four application operations added, eight production files modified, four test specs added, five test files modified, and this record. The authored change is 3,633 additions and 529 deletions, far above the ~400-line strategy trigger; the chosen strategy was one focused commit per coherent work unit rather than one reviewable slice, because each unit — the mutation preflight, the two compatibility corrections, the decomposition and its review remediation — had to change together to keep validation and execution in agreement, and the independent reviews ran on each combined candidate. Rollback boundaries: the first twelve paths for the preflight work unit, four for the corrections, sixteen for the decomposition, eleven for its remediation and four for its cleanup. Slice boundaries: preflight, corrections, decomposition, remediation, cleanup, then the record-only commits.
> **Runner:** `pnpm --dir cli/aicore test` and `pnpm --dir cli/aicore test:e2e` for applicable safe disposable fixtures; `pnpm --dir cli/aicore typecheck`.

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — Actual unsafe synchronization mutations are refused before mutation. Exact requirement: "Only introduce refusals for actual mutations that violate the existing documented safety contract." Acceptance: run a disposable unsafe mutation scenario and observe refusal before any mutation.
- S2 — Early preflight prevents unsafe reads. Exact requirement: "Preserve the existing early preflight. The new mutation planning must not introduce unsafe reads or follow unvalidated symlinks, including when inspecting `.gitignore` to determine whether a write is necessary." Acceptance: exercise an unsafe ignore-file path in an isolated fixture and observe refusal before its contents are read.
- S3 — Safe operations retain behavior and ownership. Exact requirement: "Preserve all existing intended functionality, synchronization semantics, ownership rules, public contracts, and observable behavior for valid, safe operations." Acceptance: compare authorized safe examples before and after the change and observe identical outcomes.
- S4 — Post-synchronization OpenCode conditional mutations are planned without disturbing untouched credentials. Exact requirement: "Preserve the existing OpenCode/Cursor behavior, credential protection, and raw/region/merge retirement semantics." Acceptance: exercise a planned OpenCode configuration creation and an existing credential in isolated fixtures and observe required secret setup without reading or overwriting the credential.
- S5 — Retirement respects ownership. Exact requirement: "Preserve the rule that retired raw destinations may be removed, while region and merge destinations are not retired as Core-owned files." Acceptance: exercise retirement for each mode in disposable fixtures and observe only eligible raw destinations removed.
- S6 — Existing architectural boundaries are retained. Exact requirement: "Reuse the existing domain/application/infrastructure boundaries and comply with AICore's C11 complexity policy." Acceptance: inspect the candidate imports and responsibilities and observe no new architectural layer or unrelated functionality.
- S7 — The coordinating use cases orchestrate while four cohesive application operations own document determination, each command's payload changes, and execution preparation. Exact requirement: "I approve the revised four-operation decomposition and its proposed file scope" / "Preserve the original dependency ordering" / "Do not merely relocate code to make the coordinators shorter." Acceptance: read the two coordinators and the four operations and observe that each coordinator holds only its request handling, its own validation gates in their original order, the read preflight, execution of the validated envelope and the result message, while the document determination, the command-specific change rules and the execution preparation live in their own operations; and compare the candidate against the committed pre-decomposition implementation on equivalent isolated fixtures and observe identical results.

## Tasks

- T1 | S1, S2, S3, S4, S5, S6 | delegated (security-sensitive implementation and focused tests) — Forge 🔨 (Implementer) | done | commit: 4e94e5c3fbc521f1ea491224cc8e6ba8c567d4bd
- T2 | S1, S2, S3, S4, S5, S6 | delegated (independent material security and architecture review) — Bastion 🧱 (Backend & Scripts Architect) | done | commit: 4e94e5c3fbc521f1ea491224cc8e6ba8c567d4bd
- T3 | S1, S2, S3, S4, S5, S6 | inline (independent acceptance and durable requirement reconciliation) — Cipher 🔓 (Lead Orchestrator) | done | commit: 4e94e5c3fbc521f1ea491224cc8e6ba8c567d4bd
- T4 | S7 | delegated (the four application operations, both coordinators, the composition root and their focused unit specs) — Forge 🔨 (Implementer) | done | commit: 4e94e5c3fbc521f1ea491224cc8e6ba8c567d4bd
- T5 | S7 | delegated (independent test-architecture review of the new operation specs and the changed suites) — Crucible 🔥 (Test Architect) | done | commit: 4e94e5c3fbc521f1ea491224cc8e6ba8c567d4bd

## Log

- L1 — 2026-11-23 — Original request, verbatim: "I authorize implementation of **Unit A (ARCH-002) only**, according to the final approved design.

  The authorization includes the six expected production files, the three expected test files, the required ODD records, focused disposable-fixture tests, and independent architecture/security review.

  **Non-negotiable constraints:**
  1. Preserve all existing intended functionality, synchronization semantics, ownership rules, public contracts, and observable behavior for valid, safe operations.
  2. Only introduce refusals for actual mutations that violate the existing documented safety contract.
  3. Preserve the existing early preflight. The new mutation planning must not introduce unsafe reads or follow unvalidated symlinks, including when inspecting `.gitignore` to determine whether a write is necessary.
  4. Reuse the existing domain/application/infrastructure boundaries and comply with AICore's C11 complexity policy.
  5. Do not introduce new architectural layers, frameworks, unrelated refactoring, or functionality.
  6. Preserve the existing OpenCode/Cursor behavior, credential protection, and raw/region/merge retirement semantics.
  7. Use isolated, disposable fixtures. Do not execute filesystem safety tests against real destination projects.
  8. Follow the established ODD workflow and obtain the required independent review before declaring completion.
  9. Herald remains the exclusive executor for Git/GitHub operations. Follow the repository's existing approval gates.
  10. If the required production-file scope materially expands or a functional change becomes necessary, stop and request explicit authorization.

  ARCH-003 and Units B–E remain unauthorized. Do not modify their behavior as part of Unit A.

  After implementation, report:
  - Exact files changed.
  - Architectural compliance evidence.
  - Functional-equivalence test results.
  - Safety regression test results.
  - Independent reviewer findings and their resolution.
  - Remaining risks or limitations.
  - Final completion status.

  Do not declare the work complete unless the required verification and review have passed."
- L2 — 2026-11-23 — Prior accepted design requires planning conditional secret writes against the post-synchronization configuration and excluding untouched destination-owned paths; early preflight must precede any unsafe read. Full feature mirror pending recovery; no readback established. Durable requirements affected: `odd/features/core-synchronization.md` R10, R11, R12, R18, R22 and `odd/features/core-sync-source-lifecycle.md` R1, R3, R4, R8, R9, R10; re-verification pending.
- L3 — 2026-11-23 — Scope amendment, verbatim: "I authorize the proposed minimal Unit A scope amendment.

  The additional authorized files are:
  - `cli/aicore/src/infrastructure/synchronization/local-filesystem-layout.ts`
  - `cli/aicore/tests/integration/local-filesystem-layout.test.ts`

  This authorization extends the existing Unit A implementation scope only.

  **Non-negotiable requirements:**
  1. Preserve all existing Core Sync functionality, root-selection semantics, blocker content, synchronization behavior, and public contracts for valid, safe operations.
  2. Keep root selection and filesystem operations owned by the existing infrastructure adapter.
  3. Reuse the existing domain-owned `syncReconciliationBlocker()` transformation. Do not duplicate root-selection or blocker-generation logic in application services.
  4. Provide the minimum mechanism necessary to determine the effective post-payload root-blocker mutation before the first filesystem mutation.
  5. Preserve explicit `document.root` behavior and the existing `AGENTS.md` detection rules.
  6. Preserve the existing early safety preflight. Planning must not introduce unsafe filesystem reads, including reads through unvalidated symlinks or aliases.
  7. Exclude genuine no-op operations from mutation-only refusals. Do not introduce new refusals for untouched destination-owned content.
  8. Do not introduce new architectural layers, generic filesystem planning frameworks, unnecessary abstractions, or unrelated refactoring. Follow AICore's C11 complexity policy.
  9. Add focused disposable-fixture tests covering root creation, explicit root selection, existing root content, unchanged blocker content, actual blocker mutations, and relevant filesystem safety cases.
  10. Continue the previously authorized Unit A implementation, functional-equivalence verification, ODD workflow, and independent architecture/security review.

  The original six production files and previously authorized tests remain in scope.

  **ARCH-003 and Units B–E remain unauthorized.**

  If additional production files become necessary, or functional behavior must change beyond the existing documented safety refusals, stop and request explicit authorization before expanding the scope.

  Do not stop after implementing the root-blocker adjustment. Complete the remaining authorized Unit A work and report its final verification status.

  Only declare **FINALIZED** after implementation, focused tests, functional-equivalence verification, and independent review have passed." Root owner is `local-filesystem-layout.ts:84–120`; domain transformation is `reconciliation.ts:146–170`. Replanned rollback boundary adds the two named paths; tests and independent review remain pending, mirror remains pending.
- L4 — 2026-11-23 — Correction, verbatim: "Before proceeding, distinguish between:
  - An operation that will not perform a filesystem mutation.
  - An operation that performs a filesystem write even if its resulting content is unchanged.

  In particular, inspect the existing difference between `ApplyCoreRevision` and `EnrollDestinations` for raw destinations.

  Do not change either command's existing write semantics merely to simplify the preflight.

  A planned write remains subject to the safety contract even when its bytes match the current file."
  The user further directs a verified root-blocker projection vertical slice before guard integration; preserve the existing architecture and all previously authorized Unit A constraints. Mirror recovery and tests remain pending.
- L5 — 2026-11-23 — User correction, verbatim: "Do not implement a credential-path-specific refusal yet.

  I am concerned that this approach may introduce magic strings, duplicate path knowledge, and change existing Core Sync functionality.

  **The objective remains implementation correction, not functional modification.**

  Before proceeding, distinguish these existing contracts:
  1. Generic path validation and filesystem write safety.
  2. Raw-binding synchronization semantics.
  3. OpenCode-specific secret initialization and preservation.

  The existing `ensureOpenCodeSecrets()` behavior must preserve existing credential files. However, do not automatically assume that its specific protection rule applies to every raw binding in the synchronization domain.

  ### Architecture requirements
  - Do not hardcode `.secrets/context7-api-key` checks in generic domain validators, guards, or synchronization use cases.
  - Do not introduce a new reserved-path policy without explicit authorization.
  - Keep path-specific knowledge within its existing owning component.
  - Reuse existing named constants where appropriate.
  - Do not duplicate path definitions across layers.
  - Keep the generic write-target guard focused on filesystem safety and actual planned mutations.
  - Preserve the existing raw synchronization contract unless a separately authorized policy explicitly changes it.
  - Follow AICore's C11 complexity policy. Do not introduce additional abstraction layers merely to eliminate string literals.

  ### Required analysis

  Determine whether the existing no-read/no-overwrite guarantee is scoped to OpenCode secret initialization or is an authoritative global restriction on all Core Sync operations.

  Cite the exact governing documentation and implementation.

  Explain whether a raw binding to this path is currently permitted intentionally, merely technically accepted, or explicitly prohibited by another existing contract.

  If there is no global restriction, do not invent one as part of ARCH-002.

  If the contracts genuinely conflict, present the smallest policy decision required, its compatibility impact, and its proper architectural owner.

  ### Unit A

  Continue implementing the already authorized generic mutation-preflight correction wherever this conflict does not affect the work.

  Do not introduce credential-specific refusals until the governing contract is established and any necessary functional change receives explicit approval.

  Do not change ARCH-003 or Units B–E.

  Do not declare Unit A complete until all required safety and functional-equivalence verification passes." The helper's own no-read/no-overwrite behavior is evidenced in `open-code-secrets.ts:1–9,68–96`; generic raw enrollment reads and may overwrite a destination in `enroll-destinations.ts:248–267`. R22 in `odd/features/core-synchronization.md:30` states secret contents are never distributed or overwritten without defining conflicting raw-binding disposition. No intentional permission or explicit exclusion is established; policy remains unresolved and no reserved-path change is authorized. Generic preflight remains in scope.
- L6 — 2026-11-23 — Implementation and verification, outcome and pointer. The effective-mutation preflight is connected: both operations build the ordered payload and deletion effects, clear the paths they read before reading them, project the post-payload root blocker and the OpenCode secret writes, and validate the complete actual mutation set before the first mutation; the root-blocker projection, the secret planner and the guard's read and mutation phases are no longer disconnected. Verification observed by the coordinator on this candidate: `pnpm --dir cli/aicore test` 24 files, 189 passed and 1 skipped; `pnpm --dir cli/aicore test:e2e` 17 files, 26 passed; `pnpm --dir cli/aicore typecheck` exit 0; `pnpm lint` exit 0; the Biome format check clean over the changed paths. The whole-package and end-to-end suites are the equivalence evidence for safe operations: the pre-existing exit contract, generated contents, deletion behavior, ownership rules and credential handling are unchanged. Detail lives in the committed diff and the test suites.
- L7 — 2026-11-23 — Independent review round 1, outcome and pointer. The independent architecture and security reviewer returned [FAIL] with five findings against the eleven reviewed paths: the mutations phase no longer observed the resolved root file, so the root/non-region alias refusal stopped running; the read preflight covered only file-typed destinations, so a directory at a managed destination drifted instead of being refused; the ignore file was read without being cleared when the destination receives no secret setup; the planner and the executor disagreed about the secrets directory, so a creation that would never be performed was refused; and the last-pending-effect rule existed twice across layers. All five were corrected in this work unit, together with the exit-2 diagnostic wording for a directory-create target. The reviewer also refuted one of its own premises in round 2: the byte-decoding difference it reported does not exist, because `TextDecoder` with `ignoreBOM: true` keeps a BOM exactly as the executor's read does, so that correction changed where the rule lives and nothing else. Detail lives in the reviewer's findings and the committed diff.
- L8 — 2026-11-23 — Independent review round 2, outcome and pointer. The same reviewer returned [PASS] with all five findings closed, no new rule violation and no dead or unreachable code; it confirmed every actual mutation is validated before the first mutation, untouched paths are excluded, reads are cleared first, one path identity is used across the projections, apply still queues an equal-byte raw write while enrollment still skips it, the credential file is never read or overwritten, Cursor still writes no secret material, and a directory occupying the ignore file still surfaces as a write-time failure at exit 1 rather than an unsafe write target at exit 2. Two information notes are recorded without action: the read preflight now refuses a managed destination whose path contains a symbolic link, including a linked parent that resolves inside the destination root, which the previous preflight allowed — a tightening that conforms to R11 and to the domain rule's own wording and is disclosed here as a compatibility note; and the exit-2 diagnostic for a non-regular managed destination now reads "read path is not a regular file" instead of "destination payload write target is not a regular file", the same exit class with no published text pinned. The reviewer could not hash the snapshot; the coordinator hashed the reviewed paths before and after each round and the values matched.
- L9 — 2026-11-23 — Pre-existing gap outside this authorization, and the unresolved requirement tension. The engine's filesystem-error set omits `EEXIST`, so a `.secrets` path occupied by a regular file surfaces as an unhandled exception at exit 1 instead of the "core-sync I/O error" rendering; the independent review confirmed this behavior is pre-existing and unchanged by this work, and it belongs to the error-classification area this authorization excludes, so it is reported rather than changed. Separately, R22's clause that secret contents are never distributed or overwritten does not define the disposition of a raw binding that targets the credential path; that tension is pre-existing, is neither introduced nor resolved by this work, and no reserved-path policy was added. This change does not claim R22 fully satisfied.
- L10 — 2026-11-23 — Durable requirement reconciliation. The affected durable files were read and are unchanged by this work: `odd/features/core-synchronization.md` R11, R12, R18 and R22 and `odd/features/core-sync-source-lifecycle.md` R1, R3, R8, R9 and R10 keep their ticks. No requirement was added, reworded or retired, so no durable file carries a change. R11, R12, R18 and the lifecycle requirements are re-verified by the suites above; R22's affected clauses — the secret directory created when missing, an existing credential keeping its exact contents and never being read, a missing credential created empty, and an effective ignore rule — are re-verified, while the clause's interaction with a raw binding that targets the credential path remains unresolved and is not claimed satisfied here. That question belongs to the Core Sync contract and needs the user's ruling.
- L11 — 2026-11-23 — First failure and its resolution. The first failure this change produced was the end-to-end case that reports a write-time filesystem failure: the new preflight reclassified a directory occupying the ignore file as an unsafe write target, so the run exited 2 instead of the documented drift exit 1 with the I/O diagnostic. It was reproduced against the pre-change expectation, corrected by keeping the write-time classification for that path while retaining every other refusal, and the case passes. The independent review then found the remaining regressions listed at L7, each reproduced before its correction.
- L12 — 2026-11-23 — Full-feature mirror. Pending recovery, not synchronized: the memory backend has no exact feature-key upsert, no explicit read-scope selection and no compare-and-swap, so no byte-verified mirror of this record exists and none is claimed. The authoritative file is complete in the repository.
- L13 — 2026-11-23 — Test-architecture review, outcome and pointer. The independent test-architecture reviewer returned [FAIL] on round 1 with one T15 violation — six re-stated destination and source root literals in the enrollment unit spec — and seven advisories; the violation and the mechanical advisories were corrected in this work unit, one advisory's proposed deletion was retained with a stated distinct observable instead of being deleted, round 2 returned [ADVISORY] with every finding closed plus one new low advisory about an inaccurate header clause, and round 3 returned [PASS] with zero open findings. The reviewer corrected the coordinator's own disposition wording: the retained case is a read-phase call asserting the read refusal text, the guard-boundary proof of the payload-owned read rule and the payload side of the owner-contrast pair, while the mutation-phase text is pinned by a separate case. The reviewed modules' level placement, mocking library, factory sourcing, hermeticity and observable-outcome positioning conform to the contract and the TypeScript guide, and the package's test distribution remains unit 102, integration 81 and end to end 26.
- L14 — 2026-11-23 — Items routed outside this change. The literal one-concern-per-module reading of T11 remains unmet by the two multi-concern integration modules, which now disclose their concerns in-file; if that literal reading is adopted, the deviation needs the user's recorded acceptance. The same re-stated root-literal pattern this change fixed in the enrollment spec survives in three other unit specs and in the CLI test-support factory, and the engine's filesystem-error set still omits EEXIST; both are outside this authorization and are reported for their owners. The repository format check fails only on two pre-existing 2026-11-20 records that this change never touched.
- L15 — S1 — passed: every actual mutation — payload writes, eligible retired-raw deletions, the bindings save, the conditional report, the root blocker write and the conditional secret file or directory — is validated before the first mutation, an unsafe plan is refused with nothing written, and untouched paths are excluded; the evidence ran against the committed candidate `363f5442f2b0153111692b6d9b6c2907469cddb5` through the guard integration cases and the assembled-operation refusal cases.
- L16 — S2 — passed: the read preflight clears every path whose contents are read before it is read — the payload destinations, the root file and the ignore file — refusing a link, an escape from the destination root or a non-regular managed destination, and the ignore file is read only when the read preflight cleared it; the evidence ran against `363f5442f2b0153111692b6d9b6c2907469cddb5`.
- L17 — S3 — passed: valid, safe operations keep their previous results — generated contents, deletion behavior, the published exit contract, ownership rules and credential handling — proven by the whole package suite and the end-to-end suite against `363f5442f2b0153111692b6d9b6c2907469cddb5`, including the pinned write-failure case that must still surface as a write-time failure at the drift exit status.
- L18 — S4 — passed: the OpenCode secret setup plans its writes from the post-synchronization state, including a configuration this same run creates, an existing credential is never read and never overwritten, and Cursor writes no secret material; the evidence ran against `363f5442f2b0153111692b6d9b6c2907469cddb5`.
- L19 — S5 — passed: only an eligible retired raw destination is removed, while a region-managed and a merge-managed destination stay destination-owned and preserved; the evidence ran against `363f5442f2b0153111692b6d9b6c2907469cddb5`.
- L20 — S6 — passed: the domain rule stays in the domain, the filesystem facts stay in infrastructure and the orchestration stays in the application, no new layer or framework was introduced, the existing root resolver and the existing blocker transformation are reused, and the independent architecture and security review returned [PASS] with zero open findings against `363f5442f2b0153111692b6d9b6c2907469cddb5`.
- L21 — 2026-11-23 — First delivery round closed: the delivered bytes were committed at `363f5442f2b0153111692b6d9b6c2907469cddb5` on `feat/odd/core-sync-mutation-safety`; the independent architecture and security review and the independent test-architecture review both returned [PASS] with zero open findings against those bytes, the whole package and end-to-end suites pass, and the items recorded at L9 and L14 are routed to their owners rather than closed here. This entry is superseded by the release-readiness assessment at L24, which reopened the record for the corrections at L23.
- L22 — 2026-11-23 — Full-feature mirror refreshed after closure, superseding the pending state at L12. The complete closed record is stored as memory note `qSJXO3sGrot3` in the project `github.com-personal/JPerezC92/ai-core`, tagged `feature-mirror`, `core-sync-mutation-safety` and `odd`, with the identity line carrying the locator, the branch, the work-unit commit, the closure commit, the source SHA-256 `6879342B77009C75AF0E1ECE3B2A1B8710ABD211140799B112ADCF7AAA04FF34` and the source byte count 24615. Comparison method and limits: a fresh exact-identity search returned the stored payload and it was read back in full — the header, all six specifications, all three task rows and every Log entry L1 through L21, ending with the Close entry — and that payload was compared against the repository file section by section and entry by entry. The backend appends its own tag suffix to the stored text and exposes neither a byte length nor a checksum for the payload, so exact byte-equality with the file is not proven and is not claimed; the file's own SHA-256 is recorded above as the content identity. This mirror is a recovery copy subordinate to the repository file, which remains authoritative.
- L23 — 2026-11-23 — User correction, verbatim: "# Unit A — Correct Release Blockers B1 and B2

  The release-readiness assessment identified two blockers that must be corrected before Unit A can be considered ready for PR review.

  I authorize **minimal corrections to B1 and B2 only**, within the existing Unit A scope.

  ## B1 — Remove the Unauthorized Symlink Restriction

  ARCH-002 was never intended to introduce new symlink functionality, new filesystem capabilities, or additional restrictions beyond the documented contract.

  Correct the newly introduced ancestor-symlink refusal in `write-target-guard.ts`.

  Requirements:
  - Restore the previously supported behavior for paths whose symlinked ancestors resolve safely within the destination root.
  - Preserve all existing documented symlink, containment, source-tree, inode-alias, and target-type restrictions.
  - Do not introduce symlink creation, management, resolution features, or new filesystem abstractions.
  - Do not weaken protections that existed before Unit A.
  - Ensure `check`, `apply`, and `init` enforce consistent existing safety rules.
  - Preserve the documented refusal behavior and CLI contracts.

  **This is a compatibility correction, not authorization to expand symlink support.**

  ## B2 — Restore Architectural Ownership

  The read-phase guard currently makes safety decisions in infrastructure that belong to the domain.

  Correct this responsibility violation.

  Requirements:
  - Infrastructure collects filesystem facts.
  - Domain evaluates safety rules and produces the corresponding decisions and diagnostics.
  - Application coordinates the existing operations.
  - Reuse the existing domain rule module in `write-targets.ts`.
  - Remove duplicated decisions from `write-target-guard.ts`.
  - Preserve existing error classification, refusal semantics, and observable outputs.
  - Do not introduce new layers, frameworks, port families, or unnecessary abstractions.

  Follow AICore's existing C11 complexity policy.

  ## Strict Scope
  - Correct only B1 and B2.
  - Preserve all existing intended functionality.
  - Do not change raw synchronization or retirement semantics.
  - Do not modify credential policies or introduce path-specific magic strings.
  - Do not resolve R22 as part of these corrections.
  - Do not change ARCH-003 or Units B–E.
  - Do not perform unrelated refactoring.
  - Do not expand the approved production scope without explicit authorization.

  ## Verification

  Add or adjust focused regression tests demonstrating:
  1. Existing safe symlink-ancestor layouts remain accepted.
  2. Existing unsafe symlink and path-alias cases remain refused.
  3. `check`, `apply`, and `init` remain consistent with the documented safety rules.
  4. Read-phase decisions are owned by the domain, not duplicated in infrastructure.
  5. Existing valid synchronization behavior remains unchanged.
  6. The full ARCH-002 safety correction remains effective.

  Run the relevant focused tests, typecheck, lint, and applicable isolated filesystem safety tests.

  Use disposable fixtures only.

  Obtain a fresh independent architecture/security review against the final committed bytes. The previous PASS does not automatically cover these corrections.

  Follow the existing ODD workflow. Herald remains the exclusive executor of Git/GitHub operations.

  Do not push, create a PR, or merge without separate authorization." The corrections stay inside the authorized production and test paths; the record reopens for them, and T11 and R22 are not authorization for any change.
- L24 — 2026-11-23 — Release-readiness assessment outcome and the reopening reason. The assessment read-only verified the branch scope against its base — exactly twelve paths across the three commits, a clean tree, ARCH-003 and Units B–E untouched, and the seven production hashes identical to the values bound to the independent [PASS] — and confirmed that the format-gate failures are pre-existing and that R22 remains explicitly unresolved. It raised two blockers. B1: the read and mutation phases refuse any path carrying a symbolic-link component, including an ancestor whose resolution stays inside the destination root; no governing rule requires that class — the Core Sync contract, the durable R11 requirement and the domain rule's own header all name the target-level link and the resolved-path classes only — and the pre-existing phase-less branch still used by `check` does not apply it, so `check` and `apply` disagreed on the same layout. B2: the read phase decides three refusals and authors their diagnostics inside the infrastructure adapter, contradicting the ownership stated by both the domain rule module and the adapter's own header. Both were recorded by the reviewers as notes rather than as cleared findings, and an independent [PASS] does not resolve a separately documented policy exception, so the record reopens for the corrections authorized at L23.
- L25 — 2026-11-23 — Scope amendment authorizing the application-layer decomposition, and its binding safeguards. Verbatim direction of record: "I approve the revised four-operation decomposition and its proposed file scope, including: Four new application operation files. The two existing coordinating use cases. `cli/aicore/src/main.ts` for composition-root wiring. Four new focused unit-test files. The four previously identified existing test files, only where changes are needed. The existing Unit A ODD record." The safeguards it fixes: the document operation must not finalize the pinned document from a pending state the command's payload planner has not yet calculated — the required dependency order is determine the effective document, then calculate the command-specific payload changes and updated pending, then assemble the final pinned document, then prepare and validate the execution plan, then execute; each command's validation-gate order and error precedence are preserved; the two planners keep their distinct rules without boolean policies, magic strings, reserved paths or a shared conditional engine; `syncBlocker()` and `ensureOpenCodeSecrets()` remain the execution mechanisms with their execution-time checks intact; domain, application, infrastructure and composition keep their existing owners; the refactored candidate is compared against the committed pre-decomposition implementation on equivalent isolated fixtures; and `synchronization.factory.ts`, ARCH-003, Units B–E, R22 and T11 stay outside the scope. This record carries the amendment as S7 with tasks T4 and T5, and no second record or initiative is created.
- L26 — 2026-11-23 — Delivery outcome: B1, B2 and the approved decomposition, their reviews and their final verification. The corrections and the decomposition were delivered in five commits on `feat/odd/core-sync-mutation-safety` above base `c6fe1de8c8c22f5ef4ad85669d21b78b63f2040b`: the original work unit `363f5442`, the B1/B2 correction `af905a7a`, the decomposition `9686b532`, its review remediation `314eec24` and the final cleanup `4e94e5c3fbc521f1ea491224cc8e6ba8c567d4bd`. Every coordinator now orchestrates — request and bindings handling, its own gates in their original order, the destination read preflight, execution of the validated mutation set and the result message — while four application operations own the responsibilities they are named for: `PlanSynchronizationDocument` determines the effective document and its distributable, retired and reconciliation-blocked classification without finalizing a pinned document or accepting a pending value; `PlanUpdateChanges` and `PlanEnrollmentChanges` keep each command's distinct payload rules verbatim, including apply's always-queued raw write and enrollment's equal-byte skip, region creation versus markerless refusal, region refresh skip, merge creation only on a fresh binding, report entries, pending appends and created paths; `PrepareSynchronizationExecution` performs the secret preparation, the ignore-read preflight, the secret planning, the root-blocker projection, the complete mutation envelope and the final preflight, returning only success or a refusal while `syncBlocker()` and `ensureOpenCodeSecrets()` remain the executors with their execution-time checks. The duplicated read-path projection has one home, and the executed deletions are the planner's own validated entries, so validation and execution share one derivation. Reviews at the final bytes: the architecture and security reviewer returned [PASS] with every advisory closed and only a comment-vocabulary note, which was corrected; the test-architecture reviewer returned [PASS] after closing one T15 violation, one T8 duplication and one new redundancy finding, and accepted the pre-existing `local-filesystem-layout` concern as a routed baseline item under the user's exclusion of T11 work. Final verification observed by the coordinator on the delivered bytes: `pnpm --dir cli/aicore test` 28 files, 214 passed and 1 skipped; `pnpm --dir cli/aicore test:e2e` 17 files, 26 passed; `pnpm --dir cli/aicore typecheck` exit 0; `pnpm lint` exit 0; the project formatter clean over the changed paths, tests and this record. Gate-order equivalence against the pre-decomposition revision is coordinator-verified: both coordinators' refusal sequences and the execution order (text writes, byte writes, deletions, secrets, report, bindings, blocker) match the earlier revision position for position, including enrollment's read preflight preceding its clearance-presence check; the architecture reviewer could not read that baseline itself because Git and shell are denied to its role, so its independent confirmation of that single sub-point is unavailable and is disclosed rather than claimed.
- L27 — S1 — passed at the final bytes: every actual mutation — payload writes, eligible retired-raw deletions, the bindings save, the conditional report, the root blocker write and the conditional secret file or directory — is validated before the first mutation, an unsafe plan is refused with nothing written, and untouched paths are excluded; the evidence ran against `4e94e5c3fbc521f1ea491224cc8e6ba8c567d4bd`.
- L28 — S2 — passed at the final bytes: the read preflight clears every path whose contents are read before it is read — the destination reads, the root file and the ignore file — and the ignore file is read only when the preflight cleared it; evidence against `4e94e5c3fbc521f1ea491224cc8e6ba8c567d4bd`.
- L29 — S3 — passed at the final bytes: valid safe operations keep their previous results — generated contents, deletion behavior, the published exit contract, ownership rules and credential handling — proven by the whole package suite and the end-to-end suite against `4e94e5c3fbc521f1ea491224cc8e6ba8c567d4bd`, including the pinned write-failure case and the pre-decomposition gate order.
- L30 — S4 — passed at the final bytes: the OpenCode secret setup is planned from the post-synchronization state, including a configuration the same run creates, an existing credential is never read and never overwritten, and Cursor writes no secret material; evidence against `4e94e5c3fbc521f1ea491224cc8e6ba8c567d4bd`.
- L31 — S5 — passed at the final bytes: only an eligible retired raw destination is removed, while a region-managed and a merge-managed destination stay destination-owned and preserved, and the removal is executed from the planner's own validated deletion entries; evidence against `4e94e5c3fbc521f1ea491224cc8e6ba8c567d4bd`.
- L32 — S6 — passed at the final bytes: domain rules and diagnostics live in the domain, filesystem facts in the infrastructure adapters, orchestration and the four operations in the application layer, and wiring only in the composition root; no new layer, port family, artificial interface or pass-through wrapper was introduced; the independent architecture and security review returned [PASS] at `4e94e5c3fbc521f1ea491224cc8e6ba8c567d4bd`.
- L33 — S7 — passed at the final bytes: the two coordinators hold only their request handling, their own gates in the original order, the read preflight, execution of the validated mutation set and the result message, while document determination, each command's change rules and execution preparation live in their own operations in the dependency order the amendment fixed; no case count was padded and no assertion weakened — the suite ends at 214 passed and 1 skipped after two genuinely redundant cases were removed on the review's finding; evidence against `4e94e5c3fbc521f1ea491224cc8e6ba8c567d4bd`.
- L34 — Close: the delivered bytes are committed at `4e94e5c3fbc521f1ea491224cc8e6ba8c567d4bd` on `feat/odd/core-sync-mutation-safety`, five commits above base `c6fe1de8c8c22f5ef4ad85669d21b78b63f2040b`; the independent architecture and security review and the independent test-architecture review both returned [PASS] against those bytes, the whole package suite, the end-to-end suite, typecheck, lint and the formatter pass, and the items recorded at L9, L14 and the reviewers' carried limits are routed to their owners rather than closed here. The full-feature mirror holds the record as of the first closure, verified at L22; its refresh for this final revision was not performed and is pending, with the same method and limits recorded there.
- L35 — 2026-11-23 — Mirror refresh determination, and the delivery reconciliation it belongs to. The closure contract requires the full mirror to be refreshed after material intent, task and evidence changes, work-unit commits and closure, so this record's final revision does require one. It was not written, on evidence rather than preference: the record is 40,734 bytes across 241 lines and its longest line — this delivery-outcome entry — measures 3,144 characters, while the available read surface returns a line only up to 2,000 characters and did return it truncated, so the complete document cannot be reproduced byte-exactly through that surface; the memory backend additionally exposes no byte length and no checksum, as recorded at L22, so a written copy could not be read back and proven byte-intact. The contract states that a write whose readback cannot be established as byte-intact is an unverifiable synchronization and is forbidden, so no write was made and the previously verified mirror stands only for the earlier revision it captured. The authoritative file remains complete in the repository, which is not stale. Next bounded action: refresh the mirror once a surface can reproduce the full payload and a readback can be verified, which the current backend and reader cannot. This reconciliation also recorded the delivery inventory — twenty-two paths across the eight commits, superseding the narrower per-commit list in the earlier delivery report — the exact wiring-only diff of `tests/integration/sync-lifecycle-workflow.test.ts`, which the user must still authorize as a scope amendment, and the independent gate-order verification at L36.
- L36 — S7 — passed at the final bytes, with the ordering evidence independently verified: the architecture and security reviewer compared the final coordinators and the four operations against a baseline gate sequence Herald 📯 (Release Manager) prepared from the pre-decomposition revision, and reported every gate present exactly once, in the same relative order, returning the same failure class, with the execution order unchanged for both commands, including enrollment's distinctive root check before the read preflight and the read preflight before the clearance-presence check; evidence against `4e94e5c3fbc521f1ea491224cc8e6ba8c567d4bd`.
- L37 — 2026-11-23 — Scope amendment authorized, and the inventory corrected. Verbatim: "I authorize the previously disclosed scope amendment for: `cli/aicore/tests/integration/sync-lifecycle-workflow.test.ts`. Approval is limited to the reported +11/−3 dependency-injection wiring change. No test assertions, fixtures, expected behavior, or additional production changes are authorized. This remains part of the existing Unit A branch and eventual PR." The authorized change is the three added imports plus the hoisted `sources`, `destinations` and `guard` and the three operations passed into `ApplyCoreRevision`; it touches no `describe`, `test`, `expect`, fixture or covered behaviour. **Inventory correction:** the branch modifies **eight** production files, not seven — `apply-core-revision.ts`, `enroll-destinations.ts`, `open-code-secrets.ts`, `domain/synchronization/ports.ts`, `domain/synchronization/write-targets.ts`, `infrastructure/synchronization/local-filesystem-layout.ts`, `infrastructure/synchronization/write-target-guard.ts` and `main.ts` — and adds four; with the four added test specs, the five modified test files and this record the complete branch is twenty-two paths across nine commits, 3,633 additions and 529 deletions. The earlier delivery report miscounted that line while listing all eight names, and the Delivery header carried the first work unit's narrower figures; both are corrected here. **Byte consistency confirmed:** `git diff --name-status 4e94e5c3fbc521f1ea491224cc8e6ba8c567d4bd..HEAD` lists only this record, so the committed production and test bytes are identical to the bytes both independent reviewers passed.
- L38 — 2026-11-23 — Mirror refreshed, with the capability question answered by probe and the limits stated. A throwaway note carrying one 3,400-character line with distinctive head and tail markers was written and read back through the supported memory operations, and the readback returned the entire line including both markers and its closing suffix, so the mirror path transfers and returns long lines without truncation; the earlier obstacle was this session's file reader, not the mirror mechanism, and the probe note was removed after use. The complete record through L37 was then written to the existing mirror `qSJXO3sGrot3` with an identity line naming the locator, the project, the closed status, the branch, the reviewed production commit, the nine branch commits, the source SHA-256 `08E5E54CDF046B0C3740819AF067745D1FC5B149FCE2A934B9515786B795BD63` and the source size 45,047 bytes. The write returned the full stored payload, and it was compared against the repository file section by section and entry by entry: the header with the corrected Delivery figures, all seven specifications, all five task rows and every Log entry from L1 through L37, including the 3,144-character L26 in full. Limits, stated rather than implied: the backend exposes no byte length and no checksum, and the stored payload carries the prepended identity line and the backend's own tag suffix, so byte-equality with the file is not proven and is not claimed; this entry postdates the mirrored revision by design, exactly as L22 did, so a later refresh would be needed to carry it.
