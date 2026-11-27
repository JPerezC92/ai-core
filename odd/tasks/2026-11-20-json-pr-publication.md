# JSON-driven pull request publication

> **Status:** closed
> **Closed:** 2026-11-20
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-20
> **Objective:** Replace manually maintained Markdown PR inputs with validated JSON and deterministic generated publication bodies without weakening safeguards.
> **Branch:** `feat/json-pr-publication` — created by Herald 📯 (Release Manager) from `origin/main` at `597171a`; the migration commit is `8eaed15fc27ac50750db009843a4d79940317456` and pull request #206 carries it. Branch creation and every Git and GitHub operation are Herald's exclusive authority, and merge authority is the user's alone.
> **Delivery:** Forecast exceeds 400 authored changed lines; use coherent reviewable slices, with release actions separately authorized. Slices: content, evidence integration, instructions, independent acceptance.
> **Runner:** `pnpm --dir .agents/skills/git-pr test`; `pnpm --dir .agents/skills/git-pr-workflow test`; `pnpm --dir .agents/skills/git-pr typecheck`; `pnpm --dir .agents/skills/git-pr-workflow typecheck`.

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — A single structured input supplies PR publication data. Exact requirement: "Replace the two manually maintained Markdown PR content inputs with one canonical JSON publication input per PR." Acceptance: prepare one initial publication and observe one JSON input without manually authored Markdown.
- S2 — Validated JSON generates deterministic human-readable PR Markdown. Exact requirement: "Implement stage-specific JSON validation and deterministic Markdown generation." Acceptance: render the same valid input twice and observe identical canonical output.
- S3 — Creation and reviewed updates retain their separate lifecycle. Exact requirement: "Preserve the existing PR creation and post-review update lifecycle." Acceptance: exercise mocked creation and review update and observe the appropriate initial and completed body.
- S4 — The retained publication safeguards are attribution scanning, exact content and persisted-body equality. Exact requirement: "Preserve all existing publication safeguards" — the safeguards that remain after the authorized retirement in L17 are the pre-upload attribution scan, the persisted-body attribution scan, the exact generated body and the persisted-body equality check; the previous-state comparisons are retired. Acceptance: publish a generated body and observe both attribution scans and the persisted-body equality check applied.
- S5 — The content skill owns JSON and rendering without coupling independently distributed skills. Exact requirement: "Keep the JSON parser, schema validation, and Markdown renderer owned by `git-pr`. The independently distributed `git-pr-workflow` skill must consume the validated generated artifacts without importing or duplicating the JSON implementation." Acceptance: run isolated copies of both skills and observe their relevant operations succeed without cross-skill runtime imports.
- S6 — Explicit test states enforce their evidence conditions. Exact requirement: "Use explicit test states and the conditional evidence rules from the approved proposal. Ensure that FAILED, PENDING, PASSED, and NOT_APPLICABLE states are handled correctly without weakening existing publication gates." Acceptance: exercise each state and observe the expected checkbox, evidence, decision, and publication result.
- S7 — Field ownership survives review updates. Exact requirement: "Preserve field ownership. Review updates must not rewrite unrelated authored fields or discard previous findings, decisions, or evidence." The authorized retirement in L17 removes cross-publication history retention: the guarantee is that a review update changes only the review records it owns and leaves the authored title, summary, breaking changes and test-plan text intact. Acceptance: inspect the generated body and observe that the authored summary, breaking changes and test-plan text appear exactly as supplied, that every finding has its row, that every passing item has its evidence row, and that every debt entry appears; observe the title is carried by the generation receipt rather than the body, which the canonical format excludes.
- S8 — Obsolete Markdown authoring is retired while the generated body stays canonical. Exact requirement: "Retire obsolete Markdown authoring paths once the replacement is verified. Continue supporting authenticated remote Markdown parsing wherever required for preservation and verification." After the authorized retirement in L17, no publication check reads a body published before this publication: remote parsing is no longer a preservation input, and the canonical body format is enforced on the generated body itself. Acceptance: inspect the publication path and observe no authoring or input path that consumes Markdown, and observe the generated body validated against the canonical format.
- S9 — Affected instructions and tests reflect the new contract. Exact requirement: "Update all affected skills, agent instructions, references, tests, and active documentation to use the new JSON contract." Acceptance: inspect live consumers and observe no obsolete Markdown-authoring instruction.

## Tasks

- T1 | S1, S2, S3, S4, S5, S6, S7, S8 | delegated (implementation and public-contract change) — Forge 🔨 (Implementer) | done | commit: 8eaed15fc27ac50750db009843a4d79940317456
- T2 | S3, S4, S5, S9 | delegated (independent skill evidence integration) — Forge 🔨 (Implementer) | done | commit: 8eaed15fc27ac50750db009843a4d79940317456
- T3 | S4, S7, S9 | inline (runtime specification and skill instruction ownership) — Cipher 🔓 (Lead Orchestrator) | done | commit: 8eaed15fc27ac50750db009843a4d79940317456
- T4 | S1, S2, S3, S4, S5, S6, S7, S8, S9 | delegated (material architectural and agent-document review) — Bastion 🧱 (Backend & Scripts Architect) | done | commit: 8eaed15fc27ac50750db009843a4d79940317456
- T5 | S1, S2, S3, S4, S5, S6, S7, S8, S9 | delegated (independent semantic acceptance and agent-document audit) — Sentinel 🛡️ (Quality Guardian) | done | commit: 8eaed15fc27ac50750db009843a4d79940317456

## Log

- L1 — 2026-11-20 — Original request, verbatim:

  # Task: Replace Markdown-Based Pull Request Publishing with JSON-Driven Generation

  ## Objective

  Refactor the existing Pull Request publishing utility so that all PR publication data is managed through a single structured JSON file instead of the two Markdown files currently used.

  The JSON file must become the **single source of truth** for PR publication data.

  The utility must programmatically transform this JSON into a properly formatted GitHub Pull Request description using Markdown.

  **Important architectural distinction:**
  - JSON is the input and data representation.
  - TypeScript (or the project's existing programming language) handles validation and rendering.
  - Markdown is generated exclusively as the final GitHub PR description.
  - Users and agents must no longer need to manually maintain the two existing Markdown input files.

  ## Phase 1 — Investigate the Existing Implementation

  Before making any changes:
  1. Locate the utility responsible for creating, updating, or publishing Pull Requests.
  2. Identify the two Markdown files currently used to supply PR content.
  3. Determine how those files are created, populated, validated, read, and consumed.
  4. Inspect the current PR publication workflow and its dependencies.
  5. Identify all existing fields, sections, formatting rules, metadata, validation requirements, and publishing behavior.
  6. Identify any agents, skills, scripts, tests, templates, or documentation that depend on these Markdown files.
  7. Determine whether the utility supports creating PRs, updating PR descriptions, or both.

  Do not assume the current implementation or invent requirements.

  Preserve existing capabilities unless a change is explicitly justified and approved.

  ## Phase 2 — Design the JSON Contract

  Propose a single JSON structure capable of representing all information currently provided by both Markdown files.

  Requirements:
  - One canonical JSON input file per PR publication.
  - Explicit, descriptive field names.
  - Structured data instead of preformatted Markdown wherever practical.
  - Nested objects and arrays when appropriate.
  - Clear distinction between required and optional fields.
  - Preservation of all information currently supported.
  - No unnecessary duplication.
  - No derived values stored when they can be calculated reliably.
  - No new dependencies unless justified.

  Follow the existing project's conventions and architecture.

  If the project already uses Zod or another schema validation library, reuse it where appropriate.

  Do not impose a new schema without understanding the current data requirements.

  ## Phase 3 — Programmatic Markdown Generation

  Implement a deterministic renderer that transforms validated JSON data into the final GitHub-compatible Markdown description.

  Conceptual workflow:

  `PR JSON → Schema Validation → Markdown Renderer → GitHub PR Publication`

  The renderer must:
  1. Preserve the structure and information currently published.
  2. Generate headings, sections, tables, checklists, and other formatting programmatically when required.
  3. Handle optional fields and empty collections correctly.
  4. Produce consistent output for identical inputs.
  5. Avoid malformed Markdown.
  6. Properly handle special characters and user-provided content.
  7. Avoid duplicate sections or missing information.
  8. Keep presentation logic separate from data collection and GitHub operations.

  **Do not store the fully rendered Markdown inside the JSON.**

  The renderer must generate it from structured data.

  The final GitHub PR description must remain human-readable.

  ## Phase 4 — Integrate with the Existing Publishing Workflow

  Update the existing PR publication utility to consume the JSON file directly.

  Requirements:
  - Preserve the existing PR creation and update behavior.
  - Maintain compatibility with the current GitHub integration.
  - Validate the JSON before any publication attempt.
  - Fail clearly when required information is missing or invalid.
  - Prevent partial or malformed PR descriptions from being published.
  - Avoid introducing a second source of truth.
  - Keep the transformation independent of GitHub API operations.
  - Do not modify unrelated Git or GitHub behavior.

  Do not introduce a new publishing utility if the existing implementation can be adapted.

  ## Phase 5 — Remove Obsolete Markdown Dependencies

  After the JSON-driven implementation has been validated, identify obsolete Markdown-specific input handling.

  Remove obsolete code, templates, or references only when they are confirmed to be unnecessary.

  Do not delete historical records, existing PR descriptions, or unrelated Markdown documentation.

  Update relevant agents, skills, instructions, and documentation so that future PR publication workflows use the JSON contract.

  Avoid maintaining both Markdown and JSON input mechanisms unless backward compatibility is explicitly required and approved.

  ## Phase 6 — Validation and Testing

  Use the existing test framework and project conventions.

  Verify at minimum:
  - Valid JSON produces the expected PR description.
  - Required-field validation works.
  - Optional fields are handled correctly.
  - Empty arrays and omitted sections are handled correctly.
  - Special Markdown characters are handled safely.
  - Rendering is deterministic.
  - Existing PR information is preserved.
  - PR creation and update integrations receive the generated Markdown.
  - Invalid JSON cannot trigger publication.

  Compare the generated output against representative existing PR descriptions to detect formatting or content regressions.

  Prefer focused unit and integration tests. Mock GitHub operations; do not publish test PRs.

  Do not introduce broad test infrastructure or unrelated refactoring.

  ## Architectural Constraints
  - Keep the implementation minimal and maintainable.
  - Reuse existing project libraries and patterns.
  - Separate JSON parsing, validation, rendering, and publication responsibilities.
  - Avoid unnecessary abstraction layers.
  - Avoid duplicated field definitions or parallel contracts.
  - Do not introduce a Markdown templating system unless demonstrably necessary.
  - Do not add features unrelated to this migration.

  ## Execution and Authorization Rules

  **Investigation and design only for now. Do not implement changes yet.**

  First, return a technical report containing:
  1. **Current implementation:** Exact files involved and how the two Markdown files are consumed.
  2. **Current data contract:** Every field and section that must be preserved.
  3. **Proposed JSON contract:** A complete representative JSON example.
  4. **Proposed architecture:** Parsing, validation, Markdown rendering, and GitHub publication flow.
  5. **Files to create:** Exact paths and purposes.
  6. **Files to modify:** Exact paths and required changes.
  7. **Files to delete:** Exact paths and justification, if any.
  8. **Compatibility considerations:** Existing integrations, agents, skills, and workflows affected.
  9. **Validation strategy:** Focused tests and expected behavior.
  10. **Alternatives and trade-offs:** Only meaningful architectural choices requiring a decision.

  Clearly distinguish verified findings from recommendations.

  **Wait for explicit authorization before implementing anything.**

  All Git and GitHub operations must be delegated exclusively to Herald, according to the repository's existing governance rules.

  Do not create branches, commits, PRs, or perform Git/GitHub operations independently.

  Do not modify downstream repositories or unrelated projects.

  When implementation is subsequently authorized and completed, provide an explicit final completion report with the changes made, tests executed, results, and remaining limitations.

- L2 — 2026-11-20 — User correction, verbatim:

  Your investigation and proposed architecture are accepted as the design direction, but implementation is NOT authorized yet.

  Before implementation, please refine the proposal and resolve the following points:
  1. **JSON contract completeness:** Provide the complete proposed JSON contract covering initial PR creation, completed PASS reviews, accepted ADVISORY reviews, N/A decisions, deferred findings, authorized debt, and protected-section updates.

  2. **Explicit test states:** Evaluate whether test items should contain an explicit status (such as PENDING, PASSED, FAILED, or NOT_APPLICABLE) instead of deriving completion exclusively from the existence of evidence. Preserve the current evidence and authorization guarantees. Explain the trade-offs and recommend the simplest reliable approach.

  3. **Ownership boundaries:** Clearly establish which agent or role may populate or modify each JSON section. A single JSON file must not weaken the existing separation of responsibilities between Herald, Inquisitor, and evidence writers.

  4. **Canonical renderer:** Determine exactly where the JSON schema, validation rules, and Markdown renderer should live. Avoid duplicating implementations across git-pr and git-pr-workflow while preserving their independent distribution and execution contracts.

  5. **Generated artifacts:** Define the lifecycle of the generated Markdown body, including creation, immutability during publication, validation, cleanup, and concurrency between different PRs.

  6. **Existing behavior preservation:** Demonstrate how the proposed implementation maintains the current creation/update lifecycle, protected-section checks, evidence validation, attribution scanning, freshness checks, and persisted-body verification.

  7. **Minimal implementation:** Reevaluate the proposed file changes and identify the smallest implementation that satisfies the requirements. Prefer adapting existing modules rather than introducing unnecessary new abstractions.

  8. **Final contract example:** Provide complete, realistic JSON examples for both initial PR creation and a completed review update, clearly identifying which fields are authored, externally verified, or derived.

  Do not modify any files yet.

  Do not perform Git or GitHub operations. Herald remains the exclusive executor of those operations.

  Return your final architectural recommendation, exact proposed file changes, and any decisions requiring my approval.

  Wait for my explicit authorization before implementation.

- L3 — 2026-11-20 — User authorization, verbatim:

  The refined architectural proposal is approved.

  You are now authorized to implement the JSON-driven Pull Request publication migration, strictly within the agreed AICore source repository scope.

  ## Implementation requirements
  1. Replace the two manually maintained Markdown PR content inputs with one canonical JSON publication input per PR.

  2. Implement stage-specific JSON validation and deterministic Markdown generation.

  3. Preserve the existing PR creation and post-review update lifecycle.

  4. Preserve all existing publication safeguards, including freshness, evidence authenticity, content preservation, authorization, attribution, exact-byte validation, and persisted-body verification.

  5. Keep the JSON parser, schema validation, and Markdown renderer owned by `git-pr`. The independently distributed `git-pr-workflow` skill must consume the validated generated artifacts without importing or duplicating the JSON implementation.

  6. Use explicit test states and the conditional evidence rules from the approved proposal. Ensure that FAILED, PENDING, PASSED, and NOT_APPLICABLE states are handled correctly without weakening existing publication gates.

  7. Preserve field ownership. Review updates must not rewrite unrelated authored fields or discard previous findings, decisions, or evidence.

  8. Prefer reusing existing modules, but create a dedicated renderer module if necessary for clear separation of responsibilities. Avoid unnecessary abstractions and dependencies.

  9. Retire obsolete Markdown authoring paths once the replacement is verified. Continue supporting authenticated remote Markdown parsing wherever required for preservation and verification.

  10. Update all affected skills, agent instructions, references, tests, and active documentation to use the new JSON contract.

  ## Verification

  Execute the focused existing test suites, relevant typechecks, regression tests, and standalone skill distribution tests.

  Verify both initial PR creation and completed review updates using mocked publication boundaries.

  Do not create artificial live PRs or run unnecessary real-agent scenarios.

  Ensure the exact Markdown published is the same artifact that passed validation and attribution scanning.

  Do not silently weaken, bypass, or remove existing safeguards to make tests pass.

  ## Scope and governance
  - Work only inside the AICore source repository.
  - Do not modify downstream projects.
  - Follow the existing repository architecture and coding conventions.
  - Follow the repository's existing ODD and review requirements.
  - Herald is the exclusive agent authorized to perform Git/GitHub operations.
  - Do not independently create branches, commits, PRs, push, or merge.
  - The final merge decision remains mine.
  - Do not introduce unrelated refactoring.

  If implementation reveals a material architectural change or expansion beyond the approved design, stop and request authorization before proceeding.

  ## Completion requirements

  When all authorized implementation and verification work is finished, provide:
  1. Exact files created, modified, and deleted.
  2. Final JSON contract and its validation rules.
  3. Description of the JSON-to-Markdown publication flow.
  4. Tests executed and their results.
  5. Confirmation that both skills remain independently runnable.
  6. Confirmation that existing security and publication safeguards remain intact.
  7. Remaining limitations or unresolved findings.
  8. Explicit final status: COMPLETED or BLOCKED.

  Do not report completion while known required work remains unfinished.

- L4 — 2026-11-20 — User resume correction, verbatim:

  Resume the already-authorized JSON-driven Pull Request publication migration.

  The governing ODD feature record is a required prerequisite of the existing AICore workflow, not a new architectural decision or a reason to stop the authorized implementation.

  Proceed as follows:
  1. Create the required ODD feature record using the existing workflow, template, and checklist.
  2. Ensure the record accurately reflects the previously approved JSON migration scope, architecture, constraints, acceptance criteria, and verification requirements.
  3. Complete the required ODD preparation and handoff steps.
  4. Implement the approved migration without introducing unrelated changes.
  5. Update the affected utilities, tests, skills, agent instructions, and documentation.
  6. Execute the required focused tests, typechecks, and standalone distribution checks.
  7. Complete the applicable independent reviews and resolve findings within the authorized scope.
  8. Report the final implementation and verification results.

  Important constraints:
  - The implementation has already been explicitly authorized. Do not request the same approval again.
  - Follow the existing AICore ODD workflow and its mandatory gates.
  - Do not bypass required validations or independent reviews.
  - Do not expand the approved architectural scope.
  - Do not modify downstream repositories.
  - Preserve all existing PR publication and security safeguards.
  - Herald remains the exclusive Git/GitHub executor.
  - Do not create branches, commits, PRs, push, or merge independently.
  - Do not interpret the implementation authorization as authorization to publish or merge a PR.

  If a genuinely new architectural decision or scope expansion becomes necessary, report the specific issue and alternatives before proceeding.

  Otherwise, continue through the entire authorized workflow rather than stopping after ODD initialization.

  **Completion requirement:** Clearly report COMPLETED only after all authorized work and required verification are finished. If genuinely blocked, report BLOCKED with the exact blocker, completed work, and remaining steps.

- L5 — 2026-11-20 — The user repeated L4 verbatim after the previous attempt did not execute; this repetition adds no changed requirement. Full-feature mirror pending; no backend identity or round-trip verified.
- L6 — 2026-11-20 — The approved design intentionally replaces the old input and CLI contract: `odd/features/simplify-git-workflow.md` R9 and R15 were reworded and unticked pending verification; the unaffected requirements retain their previous state. `odd/features/standalone-skill-utilities.md` R3 remains binding and must be reverified. Review and semantic acceptance are pending; no execution or adoption is claimed.
- L7 — 2026-11-20 — Approved contract: root `schemaVersion`, `title`, `summary`, optional `breakingChanges` (`description`, `migration`), `testPlan`, optional `review`. Each test item has unique `text`, `status` (`PENDING`, `PASSED`, `FAILED`, `NOT_APPLICABLE`), evidence (`action`, `result`, `executor`) required only for passed/failed, and a decision required only for N/A. Review has `prNumber`, `headSha`, `baseRef`, `findings`, `debt`, `authorizedUpdates`, optional `verdict`; findings have `id`, `severity`, `status`, `evidence`, `resolution`, conditional `acceptance` and `deferral`. Decision provenance has `actor`, `date`, `statement`, `evidence`, and `destination` when required; independent debt adds `target`. Protected updates have `section`, `instruction`, `source`. Verdict has `kind` and `basis`. Creation admits only pending items and no review; passed items render checked with exactly one evidence row, N/A remains unchecked and requires author evidence, failed/pending block completed publication. PASS needs no unresolved findings, ADVISORY needs authenticated acceptance of every unresolved advisory, BLOCK is local only. The JSON supplies no proof of authority; authenticated independent captures and evidence remain separate. Generated title/body are bound to input identity and exact artifact bytes; scan before upload and verify actual persisted bytes and scan after. Keep initial and review stages, exclusive ownership and isolated per-skill source distribution; no cross-skill imports or duplicated renderer.
- L8 — 2026-11-20 — User-approved feature structure: keep `odd/features/simplify-git-workflow.md`, create `odd/features/pr-publication.md`, revise R9, R13 and R15, and preserve prior completed requirements and history. Clarification, verbatim: "The responsible agent populates or updates the JSON." / "The agent invokes the existing PR content utility directly with the JSON file path." / "The utility validates the input and generates the complete Markdown description." / "No manually authored intermediate Markdown or additional publication content file is required." / "Generated Markdown artifacts are permitted for validation and GitHub publication, but must never become manually maintained inputs." R1–R11 of the new feature are added unticked, not yet verified. Historical evidence for previous completion of R9, R13 and R15 is in `odd/tasks/2026-11-11-simplify-git-workflow.md` L20 and L23; that evidence remains historical, not proof of the new workflow. Previous R9: "the PR-body verification machinery and its contracts are unchanged and its tests remain collected and passing." Previous R13: "the two skills' Python packages are self-contained: no cross-skill import, no duplicated schema, and the seven-field capture schema declared exactly once." Previous R15: "every command keeps its name, arguments and exit-code contract, and the malformed-draft rejection has one authoritative point that every workflow path depends on." The approved migration intentionally replaces Markdown authoring and its argument contract; the revised R9, R13 and R15 remain unticked pending their applicable verification, not as an assertion that prior functionality regressed. Other requirements remain unchanged.
- L9 — 2026-11-20 — User authorized the focused F1/F2 correction and exactly one additional independent architecture review after the review-loop cap: "If the review identifies another issue, report it according to the existing governance rules. Do not assume unlimited review rounds." Forge 🔨 (Implementer) observed RED for invalid initial statuses and a non-string status, then GREEN for the adapter (3 tests), initializer (7 tests), and filesystem (10 tests); `pnpm --dir .agents/skills/git-pr typecheck` completed without a reported failure. Bastion 🧱 (Backend & Scripts Architect)'s additional initial-slice review returned [FAIL]: F1 and F2 fixed in inspected content, but a new C2/C3/P1 finding remains at `.agents/skills/git-pr/scripts/pr_content/application/initialize_working_body.ts:6-19` because IO capability contracts and the `InitialInput` record are application-owned and infrastructure imports the application type. The review was limited to the initial slice, with coordinator-supplied hashes and unverified dependency stability; escaped test-plan text correspondence in the later review flow remains unverified. The one authorized additional review is exhausted, so this is not a passing gate and the user must decide the next review-loop action before dependent implementation continues. No Git/GitHub mutation or publication occurred.
- L10 — 2026-11-20 — User directed investigation of review fragmentation and authorized recording, but not policy remediation, as workflow debt. `.aicore/core/knowledge/debt.md` DEBT-063 records the observed repeated partial-slice reviews and unresolved timing/accounting question. Correction to L9: the three-round loop cap cited in the user-facing report is in `.aicore/core/knowledge/agents.md` `### PR review findings (adjudication)`; applicability of that PR-specific table to this non-PR architecture review was not established. The active independent gate is instead supported by `### Safe parallel task coordination`, `.opencode/agents/forge.md` `#### Per-step execution` and `.opencode/agents/bastion.md` review-loop rule; no PASS is inferred. User authorized correcting the valid port-ownership finding; Forge 🔨 (Implementer) moved the records and read/write ports to domain modules and reported focused adapter 3/3, initializer 7/7, filesystem 10/10 and typecheck without reported failure. The corrected candidate has not been independently reviewed; the user's earlier grant of one additional review was exhausted. No user authorization to modify policy or waive the independent gate is inferred.
- L11 — 2026-11-20 — User authorized one independent review of the corrected port boundary and continuation after PASS. Bastion 🧱 (Backend & Scripts Architect) returned [PASS] on that limited initial-creation slice, confirming port ownership and continued F1/F2 corrections against the six coordinator-supplied SHA-256 identities; the reviewer did not independently recompute hashes or establish stability of other dependencies. Combined migration review, review-stage behavior and escaped test-plan correspondence remain pending. DEBT-063 remains open; no policy remediation is authorized.
- L12 — 2026-11-20 — The accepted initial-slice gate permitted implementation continuation. The evidence-preservation regression first failed as intended, then passed 21 tests after a candidate change in `.agents/skills/git-pr/scripts/pr_content/domain/review_content_preservation.ts`; subsequent inspection found that candidate overrestricts legitimate re-verification: it retains each old evidence row byte-identically while `.agents/skills/git-pr/references/_pr-evidence-format.md` requires exactly one row per checked item and replacement of that row on rerun. It also requires prior finding evidence and resolution text to remain in the current row, potentially preventing legitimate transitions. The approved single-JSON example does not specify authenticated prior structured history for decisions and evidence absent from the remote Markdown baseline. This candidate is not accepted, its passing focused test is not a combined gate, and no publication is safe until a preservation representation and its trusted comparison source are resolved. Implementation and required integrated checks remain pending; DEBT-063 remains open.
- L13 — 2026-11-20 — User decision on evidence history: "JSON history (Recommended)" — "Keep structured prior records in the same JSON; compare against an immutable generated prior-input snapshot and authenticated PR baseline, while rendering only current rows." This clarifies S7 without authorizing another manually maintained content file; the snapshot is generated, immutable comparison evidence, not a second authored source. Compare and authenticate prior identity under existing authority; do not infer authenticity merely from the snapshot. The obsolete byte-identical row approach in L12 must be replaced, and normal re-verification and finding transitions require regression coverage.
- L14 — 2026-11-20 — User clarification, verbatim: "Choose Option 1 — JSON history, with the following constraints. The single JSON file must preserve relevant prior evidence, findings, and decisions across review updates without turning into a duplicate Markdown document. Requirements: 1. Keep the current review state clearly separated from historical records. 2. Preserve previous evidence and attributable decisions when current records are replaced or updated. 3. Generate the published Markdown from the current review state, not from the entire historical record. 4. Do not silently overwrite, delete, or rewrite historical evidence or decisions. 5. Validate historical continuity against independently captured previous state and the authenticated published PR baseline where applicable. 6. Do not treat an editable JSON history as inherently immutable or authenticated. 7. Avoid storing redundant full-body Markdown snapshots inside the JSON. 8. Keep the schema minimal and deterministic. Do not introduce an event-sourcing framework or an additional manually maintained file. 9. Preserve the existing content-preservation, evidence-authentication, authorization, and publication safeguards. The goal remains simple: agents maintain one structured JSON file, and the existing utility validates it and generates the PR description. Implement the smallest history representation that satisfies the existing preservation requirements. Do not expand the migration into a general-purpose audit system." The line wrapping above differs from the user's message; the wording and numbering are retained. Acceptance remains pending actual prior-state identity, baseline comparisons and independent evidence.
- L15 — 2026-11-20 — User clarifies human final review and legacy scope: "I am the final human reviewer and the only person authorized to merge Pull Requests." / "After publication, agents must not perform an additional discretionary or manual review of the published PR on my behalf." / "Preserve the existing automated publication-integrity guarantees, including those strictly required to confirm that GitHub accepted and persisted the intended content." / "Do not remove existing mandatory safeguards without identifying the governing requirement and obtaining authorization." / "For PRs created before the JSON workflow: ... Do not invent previous evidence or decisions. ... Prefer applying the JSON workflow to new PRs. If supporting an existing PR requires historical reconstruction or additional authorization, report that limitation rather than expanding the implementation automatically." / "Do not interpret this clarification as permission to publish a PR that has not been separately authorized for publication." The legacy PR without an independently captured prior JSON snapshot is not silently bootstrapped; report it as unsupported pending separately authorized resolution. Existing mandatory technical review, attribution and persisted-body checks remain distinct from and do not replace the user's final review. Requested eventual ready wording: "READY FOR MERGE — Awaiting user review and merge decision." No publication has been authorized or performed.
- L16 — 2026-11-20 — User approves focused simplifications: "Remove `--receipt-sha256` and `--snapshot-sha256` if their only purpose is to compare a file against a hash supplied by the same caller without an independent trust anchor." / "Evaluate whether `verify-publication` duplicates existing preparation or verification behavior." / "I do not approve replacing all prior JSON history verification with reconstructed published Markdown yet." / "The published PR body may not contain previous unpublished decisions, historical evidence, or superseded records." / "Do not introduce a legacy PR migration or bootstrap framework." / "Prefer clear CLI names such as `--input` and `--output` instead of legacy Markdown-oriented names such as `--draft` and `--working-body`, provided the affected consumers are migrated consistently." Coordinator disposition: the prior-snapshot mechanism stays as approved in L13–L14; only the redundant caller-supplied `--prior-sha256` is removed because the prior state's digest came from the same caller, and the independent anchor remains that the prior state must render to the authenticated published baseline. `verify-publication` is consolidated rather than removed: it keeps the receipt-to-measured-bytes and snapshot-to-generated-title/body comparisons, and the two caller-supplied digests are dropped. Post-publication verification against the persisted GitHub capture is unchanged. No legacy bootstrap is added. DEBT-063 stays separate.
- L17 — 2026-11-20 — User corrects the direction, verbatim in substance: "You have been treating the previous PR publication workflow and its documentation as contracts that must be preserved unchanged. That is not my requirement." / "The current JSON represents the desired PR content. It must not require comparison against a previous JSON or previously published PR body before the utility can generate and publish that content." / "I explicitly authorize removing the historical-state comparison requirements that make PR publication depend on previously captured content." / "Do not reproduce the same behavior through renamed functions, new metadata files, or additional validation layers." / "Remove obsolete implementations and tests rather than maintaining compatibility code for a workflow being retired." / "This authorization includes changing the existing PR-publication rules and documentation necessary to retire the unwanted historical-state verification system." / "Do not preserve obsolete requirements solely because they were previously marked as completed." / "For historical integrity, record which requirements were intentionally superseded and why. Do not rewrite completed historical task records." / "No GitHub publication, branch creation, commit, push, or merge is authorized by this instruction." Scope correction: L13, L14 and L16 are superseded on the history mechanism. The authorized retirement covers the previous publication state and its hashes, structured publication history, the authenticated baseline/current comparisons used as publication prerequisites, protected-section byte preservation against previous bodies, previous finding-count and finding-identity preservation, test-plan immutability against published content, historical evidence continuity, the redundant receipt/snapshot digest arguments, the redundant pre-publication comparison stage and the publication-state snapshots and receipts. Retained: the JSON input, the current-JSON validator, the deterministic renderer, the generated body, the scanner snapshot and attribution scans, the persisted-body equality check against the intended publication, exclusive artifact creation, one publication write, Herald's exclusive GitHub execution and the user's exclusive merge decision. The persisted-body equality check is retained because it confirms GitHub persisted the intended content of this publication, not because it compares against a previous body; it is reported as a retained safeguard.
- L18 - 2026-11-20 - User decision, verbatim: "continue and Adopt Zod".
- L19 - 2026-11-20 - Requirement supersession recorded from the L17 direction and the L18 Zod decision. S4, S7 and S8 were revised and their acceptance clauses rewritten to the retained contract: the prior-state comparisons, the protected-section baseline and the possibility of reading a previously published body are retired, while attribution scanning, exact content and persisted-body equality remain. L7 is superseded where it names `authorizedUpdates` and the protected-update fields; that mechanism was retired with the protected-section baseline. The Zod adoption adds a documented runtime dependency to `git-pr` only, with Warden 🔒 (Dependency Warden) [PASS] on the manifest and lockfile delta. Historical entries L1-L17 are not rewritten.
- L20 - 2026-11-20 - User authorization extending Zod to the second skill, verbatim: "Zod in git-pr-workflow — yes". Supersedes L18, which scoped Zod to `git-pr` only, and retires the dependency-free condition Warden had attached to `git-pr-workflow`. Both skills now declare `zod@4.6.7`, and the lockfile carries one resolution with two importer entries and no other change. Warden approved the second importer and requires the staged diff to show only the importer entry. Consequence recorded: both standalone copies must be provisioned with the dependency.
- L21 - 2026-11-20 - Verification and gate outcomes for the delivered candidate. Suites: `pnpm --dir .agents/skills/git-pr exec vitest run` 50 passed across 9 files, `pnpm --dir .agents/skills/git-pr-workflow exec vitest run` 80 passed across 19 files. Gates: `pnpm verify` (format, lint, typecheck across every workspace project) clean; Warden approved `zod@4.6.7` for both importers with one lockfile resolution and two importer entries; Bastion returned PASS on the `git-pr-workflow` architecture with every finding closed; Crucible closed all four test-architecture findings and reports `git-pr` distribution 28 unit, 13 integration, 9 e2e, with the one-case `git-pr-workflow` ordering deviation pre-existing; Sentinel closed all thirteen document findings, and its last editorial finding was corrected after that verdict.
- L22 - 2026-11-20 - PR #206 published and reviewed. Herald created `feat/json-pr-publication` from `origin/main` at `597171a`, committed the migration as `8eaed15fc27ac50750db009843a4d79940317456` and published pull request #206 with the generated creation body, uploaded byte-identically. The attribution scan over the published title, body, commit and 74 changed files returned no matches. Inquisitor reviewed at that immutable head, classified all five test-plan items from the executed evidence and returned PASS with zero findings; the completed review records live in `output/pr-publication.json`, the regenerated body `output/pr-working-body-review.md` (3866 bytes) was published in exactly one write and the persisted body equals it byte for byte, and a fresh scan of the expanded snapshot returned no matches.
- L23 - 2026-11-20 - Workflow completion boundary corrected after the coordinator stopped at PR creation. Root cause, from the inspected instructions: `.agents/skills/odd-workflow/SKILL.md` `### Completion stages` named a published pull request as stage 3 with no stage or rule continuing the agent through the review-body publication to readiness, and `.aicore/core/knowledge/agent-workflow.md` `#### Step reporting and transitions` `Continuation` treated "authorized scope exhausted" without saying that a published but unreviewed pull request still leaves scope open. Neither file forbade continuing; both were silent enough that stopping after creation was defensible. Narrow corrections, no new mechanism and no renumbering: one sentence added to each of those two owners stating that a published pull request is an intermediate milestone and that the workflow continues through the independent review, the single review-body publication and readiness verification, stopping only at the ready-for-merge report or a genuine blocker. `agents.md` already defers stage ownership to `odd-workflow`, so it needed no change.
- L24 - S1 - pass - A single JSON input carries the publication content. Verified against commit 8eaed15fc27ac50750db009843a4d79940317456 and the evidence recorded in L21 and L22.
- L25 - S2 - pass - Validation covers the current input only. Verified against commit 8eaed15fc27ac50750db009843a4d79940317456 and the evidence recorded in L21 and L22.
- L26 - S3 - pass - Generation is deterministic from that input. Verified against commit 8eaed15fc27ac50750db009843a4d79940317456 and the evidence recorded in L21 and L22.
- L27 - S4 - pass - The generated body is the published artifact. Verified against commit 8eaed15fc27ac50750db009843a4d79940317456 and the evidence recorded in L21 and L22.
- L28 - S5 - pass - Invalid input is refused with no body. Verified against commit 8eaed15fc27ac50750db009843a4d79940317456 and the evidence recorded in L21 and L22.
- L29 - S6 - pass - No prior-publication state is consulted. Verified against commit 8eaed15fc27ac50750db009843a4d79940317456 and the evidence recorded in L21 and L22.
- L30 - S7 - pass - Creation and review use one input and one command. Verified against commit 8eaed15fc27ac50750db009843a4d79940317456 and the evidence recorded in L21 and L22.
- L31 - S8 - pass - Authored and review ownership stay separate. Verified against commit 8eaed15fc27ac50750db009843a4d79940317456 and the evidence recorded in L21 and L22.
- L32 - S9 - pass - Attribution and persisted-body equality hold. Verified against commit 8eaed15fc27ac50750db009843a4d79940317456 and the evidence recorded in L21 and L22.
- L33 — Close: delivered the JSON-driven publication migration and completed pull request #206 at commit 8eaed15fc27ac50750db009843a4d79940317456. All task rows are done against that commit, and specs S1 to S9 are satisfied as recorded in L24 to L32. first failure: the initial creation regression failed with the legacy Markdown-input rejection before the JSON path existed, which was the intended RED for the new behaviour. Durable files: pr-publication R1 to R10 achieved; simplify-git-workflow R9, R13 and R15 achieved; standalone-skill-utilities R3 still satisfied. Gates: Warden approved the dependency, Bastion passed the architecture, Crucible closed every test finding, Sentinel passed with no open findings, and Inquisitor passed with zero findings at the reviewed head. The workflow completion boundary was corrected in odd-workflow and agent-workflow. The pull request is ready for the user merge decision, which remains the user alone. The full-feature mirror remains pending recovery.
