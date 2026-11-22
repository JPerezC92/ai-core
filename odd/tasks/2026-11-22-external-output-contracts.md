# External output contracts

> **Status:** active
> **Owner:** Cipher 🔓 (Lead Orchestrator)
> **Created:** 2026-11-22
> **Objective:** Add `C14 — External output contracts` to the common architecture contract as the single normative owner of the cross-interface output contract, and map it in the navigation, the shapes, the implementation guides and the reviewer runtimes, without changing any published contract and without a production-code change.
> **Branch:** docs/adr/0010-acceptance
> **Delivery:** Two reviewable units on the existing branch. Unit A — the 13 documentation paths and this record's creation (header, Specs, Tasks, L1–L3); forecast ≈330 authored additions and deletions, dominated by this record's verbatim request quote, against the ≈400 strategy trigger. Unit B — the record's post-gate evidence (gate verdicts, task commit references, the durable-file ticks and the closure entry) as a record-only commit. Each unit is revertible alone; no generated file is involved.
> **Runner:** node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks

Load and read the `odd-workflow` skill (`.agents/skills/odd-workflow/SKILL.md`) before creating or maintaining this record. Its creation, delivery, change and closure procedures are canonical; this template illustrates their layout, not another policy definition.

## Specs

- S1 — `C14` is the single normative owner of the cross-interface output contract, and no shape or implementation guide restates it. Exact requirement: "Introduce **C14 — External Output Contracts** in `.aicore/core/architecture/implementation/architecture.md` as the single normative owner of the cross-interface contract above." / "Do not introduce duplicate normative rules across shapes and implementation guides." / "Do not add a new architecture layer, runtime wrapper library, shared serializer, mandatory directory, dependency or migration." Acceptance: read `.aicore/core/architecture/implementation/architecture.md` and confirm exactly one `## C14` section carries the HTTP, CLI, MCP, frontend, other-channel, compatibility and verification rules; then read the three shapes and the four implementation guides and confirm none of them restates a `C14` rule.

- S2 — A new project-owned REST JSON API publishes the JSend envelope with the appropriate HTTP status, the AICore profile's stable error code, and the documented exceptions. Exact requirement: "For new, project-owned REST APIs that return JSON, **JSend is the default response-envelope format**." / "This applies across L1, L2 and L3 when the HTTP API responsibility exists." / "AICore's selected JSend profile requires a stable machine-readable error code inside `data`." / "`data.code` MUST be a documented, stable string identifier." / "`data.details` is optional and must follow the endpoint's documented schema when present." / "Do not return an HTTP 200 response to disguise a failed request." / "Do not generate arbitrary error identifiers." / "The `data.code` structure is an **AICore JSend profile convention**, not a claim that the original JSend specification mandates this field." / "Preserve existing stable domain error identifiers where suitable, mapping them at the HTTP interface boundary." / "`status` MUST be `"error"`." / "`message` MUST be a safe, documented client-facing message." / "Do not expose stack traces, database internals, secrets or sensitive implementation details." / "Logging and diagnostic correlation must remain separate from the public error message." / "Do not confuse `data.code` with JSend's optional top-level `code` field, which is traditionally numeric." / "Do not equate every 4xx response mechanically with a particular business error. Select the appropriate HTTP status and classify the failure according to its actual semantics." / "HTTP 204, HEAD responses, 304 and other bodyless responses MUST NOT contain a JSend body." / "File downloads, binary responses, server-sent events and streaming formats are not forced into JSend." / "GraphQL, gRPC, third-party APIs and other protocols retain their applicable contracts." / "Existing APIs retain their approved response contracts." / "When an existing API adds an endpoint, it follows that API's established contract rather than silently introducing a conflicting envelope." / "An explicitly approved alternative, such as RFC 9457 for HTTP errors, remains valid within its declared scope. Do not mix competing error envelopes arbitrarily within the same API contract." / "The endpoint must use the appropriate HTTP success status." / "Do not generate redundant response metadata unless the endpoint contract requires it." Acceptance: read `C14`'s HTTP clauses and confirm they state the success, fail and error shapes with their required fields, the `data.code` profile duty, the bodyless and streaming exclusions, the other-protocol retention, the approved-alternative validity, the existing-API continuity and the status-selection rule.

- S3 — A newly published REST JSON API operation defines its request, success and error schemas with stable error codes, published through OpenAPI or an established equivalent, with no global payload schema and no new tooling. Exact requirement: "For each newly published REST JSON API operation intended for consumption by another application, define:" / "Request schema, when there is an input payload." / "Success response schema, including its JSend envelope and `data` structure." / "Documented error response schemas and corresponding HTTP statuses." / "Required and optional properties and their types." / "Stable machine-readable error codes." / "Any relevant pagination or versioning conventions." / "Use OpenAPI for the API contract, or an already established equivalent contract source when justified by the project." / "Do not invent a global payload schema shared by unrelated business operations." / "Do not introduce a new OpenAPI generator or framework dependency solely because this policy is documented." Acceptance: read `C14`'s schema clause and confirm it requires those schema elements, names OpenAPI or an established equivalent, and excludes both a global payload schema and a new generator dependency.

- S4 — A CLI uses native command-line semantics: exit codes, stdout/stderr separation, and documented machine-readable JSON with the standard diagnostic shape where it offers `--json`. Exact requirement: "CLIs MUST use native command-line semantics rather than JSend." / "Exit code `0` indicates success." / "A nonzero exit code indicates failure." / "`stdout` carries the primary successful output." / "`stderr` carries errors and diagnostics." / "Progress messages and logs MUST NOT corrupt a machine-readable stdout stream." / "A CLI that participates in pipelines must preserve predictable stream behavior." / "Do not impose arbitrary global exit-code numbers beyond success versus failure. Additional exit codes must be documented when consumers depend on them." / "A CLI MAY provide `--json` when automation consumers need structured output. It is not required for every tiny script." / "Successful stdout MUST contain valid JSON following a documented command-specific schema." / "Do not add a mandatory JSend envelope." / "The command must not interleave logs or progress text with its JSON output." / "For failures, exit nonzero, leave stdout free of partial success data and emit a structured diagnostic to stderr." / "The error code must be stable and documented." / "Existing CLI consumers and output formats remain unchanged unless migration is explicitly authorized." / "JSON Lines or another streaming representation may be used when the command's documented streaming behavior requires it; do not mislabel such output as a single JSON document." Acceptance: read `C14`'s CLI clauses and confirm they state the exit-code rule, the stream separation, the optional `--json` duty with its command-specific schema, the nonzero-exit stderr diagnostic with its `error` object holding a stable `code` and a `message`, the streaming exception, the existing-contract continuity and the absence of a mandatory envelope.

- S5 — An MCP implementation follows its negotiated protocol version and native tool-result semantics, with structured output schemas and correct error classification. Exact requirement: "MCP implementations MUST follow their negotiated protocol version and native tool-result semantics." / "Do not apply JSend as an additional universal wrapper." / "A tool returning structured data SHOULD use `structuredContent` when supported and useful to its consumers." / "Its structured output MUST conform to the declared `outputSchema` whenever one is provided." / "This value belongs in the MCP tool result's `structuredContent`, not in a fabricated application-level JSend envelope." / "Preserve the required MCP `content` behavior and any applicable backward-compatibility representation." / "The MCP result's outer fields must conform to the negotiated protocol version." / "Distinguish:" / "Protocol-level JSON-RPC errors, such as invalid protocol requests or unavailable tools." / "Errors occurring during tool execution, represented through MCP tool-result error semantics such as `isError: true`." / "Do not represent tool-execution errors as successful tool results merely because a handler caught an exception." / "Do not automatically classify every legitimate "not found" outcome as a protocol error. The tool's published behavior determines whether absence is an ordinary result or an execution failure." / "Do not create redundant JSend statuses inside `structuredContent`." / "`resultType` and other version-dependent fields MUST only be required where the negotiated MCP version requires them." / "Do not impose the latest MCP wire format on implementations negotiated to earlier versions." / "`outputSchema` MUST be honored when declared, without requiring artificial schemas for tools whose output does not need structured results." / "For MCP servers using stdio, stdout remains reserved for MCP protocol messages." Acceptance: read `C14`'s MCP clauses and confirm they state the negotiated-version duty, the `structuredContent` and `outputSchema` mapping, the protocol-error versus tool-execution-error distinction, the version-dependent-field rule, the stdio stdout reservation and the absence of any envelope requirement.

- S6 — A frontend consumes the API's published contract at one mapping boundary and keeps envelopes out of components, hooks and operations. Exact requirement: "Frontend applications MUST consume their API's actual published contract." / "Interpret `status` and `data` at the HTTP client or existing mapping boundary." / "Validate or type the returned payload according to the application's established approach." / "Translate the transport representation into the frontend's existing data and error model where appropriate." / "Do not require internal React components, Hooks, or application operations to return JSend objects." / "Do not duplicate JSend parsing across multiple components when a genuine shared boundary already exists." / "Preserve F2/F3." / "For L1/L2 implementations, a simple API-client function may perform the mapping without creating an extra directory, wrapper class, or artificial application layer." / "Do not silently modify how existing frontends consume published APIs." Acceptance: read `C14`'s frontend clauses and confirm they state the single-boundary interpretation, the prohibition on envelopes in components, hooks and operations, the no-duplicate-parsing rule, the F2/F3 preservation, the L1/L2 simple-mapping allowance and the existing-frontend continuity.

- S7 — An internal game, UI or engine channel uses types appropriate to its consumers and inherits no HTTP, CLI or MCP convention. Exact requirement: "Internal game operations, UI events, state changes and engine callbacks are not HTTP APIs." / "Do not impose JSend or CLI/MCP response conventions on them." / "Use explicit types or schemas appropriate to their consumers." / "If a game exposes an HTTP API, CLI or MCP tool, that external interface follows the corresponding contract defined above." Acceptance: read `C14`'s other-channel clause and confirm it states the non-HTTP status of internal channels, the type-based alternative and that a published external interface follows its own contract.

- S8 — A producer and its consumer agree on the payload contract, and a published contract stays compatible without explicit authorization. Exact requirement: "The producer and consumer MUST agree on the actual payload contract, not only on the envelope." / "Document:" / "Output shape." / "Required and optional values." / "Field types and semantics." / "Error identifiers." / "Relevant protocol statuses." / "Versioning and compatibility expectations where needed." / "Existing published response formats MUST NOT be changed incompatibly without explicit authorization and a migration plan." / "Do not silently:" / "Rename or remove fields." / "Change required fields to incompatible types." / "Change successful responses into new envelopes." / "Change error-code semantics." / "Change CLI output streams or exit codes relied upon by consumers." / "Change MCP tool-result schemas unexpectedly." Acceptance: read `C14`'s compatibility clauses and confirm they require producer/consumer agreement on the payload and forbid an incompatible change without explicit authorization and a migration plan.

- S9 — The architectural ownership of the contract stays where it is, and verification uses the existing testing infrastructure without new tooling. Exact requirement: "Preserve C4, C5, C6 and C12:" / "Domain and Application remain independent of protocol-specific serialization." / "The appropriate Interface boundary owns external response translation." / "Infrastructure maps its own external representations without taking over channel serialization." / "L1/L2 do not inherit artificial Clean Architecture structures merely to satisfy an output-format rule." / "Use focused contract verification for newly introduced or intentionally changed external interfaces." / "Use existing testing infrastructure and applicable test contracts." / "Do not create a new framework, validator, test package, synthetic end-to-end environment, or per-file tests merely to enforce this documentation policy." Acceptance: read `C14`'s ownership and verification clauses and confirm each cited ownership rule is preserved, that no structure is mandated, and that no framework, validator or test package is introduced; then confirm the testing contract's `T` rules are unchanged.

- S10 — The navigation, the guide template, every applicable implementation guide, the shapes and the reviewer runtimes recognize `C14`, with no new shape or testing obligation identifier. Exact requirement: "Update `.aicore/core/architecture/README.md` to recognize C14 in the existing navigation, rule range and mapping obligations." / "Update backend, scripts and frontend shape references only where necessary to identify applicability. Do not duplicate C14's normative wording under new B/F/P rules." / "Align existing implementation guides, especially NestJS/JSend, with the new contract. Preserve language- and framework-specific mappings rather than copying the full rule." / "Update any required guide template or parity mapping so C14 has explicit coverage." / "Handle testing requirements through their existing testing owners; avoid inventing a duplicate testing authority." / "Do not create a new architecture family or add loose normative files at the architecture root." / "Do not introduce a mandatory `interfaces/` directory." Acceptance: search the core navigation, the three shapes, the guide template and the three guides and confirm each carries an explicit `C14` reference with no new `B`/`F`/`P`/`T` identifier; then confirm the three reviewer runtimes carry `C14` in their obligation-ID range.

- S11 — The new output-contract decision and its evidence live in this record, and the accepted ADR 0010, the closed records and `R17` are unchanged. Exact requirement: "Preserve ADR 0010 as Accepted, effective 2026-11-22." / "Do not modify its original decision or acceptance evidence." / "Do not create ADR 0011." / "Preserve previously closed ODD records and their historical statements." / "Record the new output-contract decision and its evidence in the new ODD record." / "Do not modify or claim completion of R17." Acceptance: read `docs/architecture/decisions/0010-architecture-selection-and-interface-boundary.md` and `odd/tasks/2026-11-21-architecture-selection-policy.md` and confirm the accepted status, the acceptance date and the historical entries are unchanged; then read `odd/features/architecture-contract.md` and confirm `R17` is still unticked and that no other requirement changed.

## Tasks

- T1 | S1, S2, S3, S4, S5, S6, S7, S8, S9 | inline (the common contract is one owner file with no delegated author; one coherent candidate avoids conflicting edits to the same file) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T2 | S10 | inline (the navigation, the guide template, the three shapes and the three guides form one dependent set of identifier and citation updates) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T3 | S10 | inline (the reviewer runtime obligation-ID ranges and their version bumps are coordinator-authored runtime specifications) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T4 | S11 | inline (the durable feature file and this record) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T5 | S1, S2, S3, S4, S5, S6, S7, S8, S9, S10 | delegated (architecture-owner gates: Bastion 🧱 (Backend & Scripts Architect) for the common contract, the backend and scripts shapes and the NestJS/Python guides; Atrium 🏛️ (Frontend Architect) for the frontend shape and the React guide; Crucible 🔥 (Test Architect) for testing-contract compatibility and the agent-runtime changes) — Cipher 🔓 (Lead Orchestrator) | open | commit: pending
- T6 | S10, S11 | delegated (independent record, durable-requirement and agent-document audit) — Sentinel 🛡️ (Quality Guardian) | open | commit: pending
- T7 | S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11 | delegated (sole Git and GitHub executor: the implementation commits and the branch push; the pull-request title, description and independent review are the release stage published on PR #211 and verified in its body) — Herald 📯 (Release Manager) | open | commit: pending

Task-row illustration: `open` → `in progress` → `done`; `commit: pending` while unfinished, a 7–64 character hexadecimal commit reference when done. See the skill's creation, delivery-forecast and closure procedures for task evidence, coherent multi-task commits, strategy thresholds and closure checks.

## Log

- L1 — 2026-11-22 — Original request, quoted verbatim. The full normative contract text is quoted at L3; this entry holds the request's objective, authority, scope and boundaries.

  > # AICore — Implement the Defined Output Contract Policy in PR #211

  > ## 1. Objective and authority

  > We are standardizing application output contracts across AICore.  > This is an architectural requirement, not an exploratory research task.  > The architectural decisions are defined below. **Do not delegate these decisions to another agent, reopen the selection of standards, or replace them with your preferred alternatives.**  > Your responsibilities are to verify compatibility with the repository's existing contracts, identify the exact canonical documentation changes, and implement the approved scope through the established ODD workflow.  > ### Existing PR

  > https://github.com/JPerezC92/ai-core/pull/211  > Branch: `docs/adr/0010-acceptance`  > Continue using **PR #211**. Do not create another PR or implementation branch.  > Preserve ADR 0010's accepted decision, acceptance date, and original scope.  > The output-contract policy is a separate architectural decision within the same PR, not a retrospective expansion of ADR 0010.  > ## 8. Canonical documentation ownership

  > AICore already uses a three-level documentation ownership model:  > 1. Common architecture contract.
  > 2. Application-shape obligations.
  > 3. Stack-specific implementation guides.

  > Respect this hierarchy.  > My selected implementation approach is:  > - Introduce **C14 — External Output Contracts** in `.aicore/core/architecture/implementation/architecture.md` as the single normative owner of the cross-interface contract above.
  > - Update `.aicore/core/architecture/README.md` to recognize C14 in the existing navigation, rule range and mapping obligations.
  > - Update backend, scripts and frontend shape references only where necessary to identify applicability. Do not duplicate C14's normative wording under new B/F/P rules.
  > - Align existing implementation guides, especially NestJS/JSend, with the new contract. Preserve language- and framework-specific mappings rather than copying the full rule.
  > - Update any required guide template or parity mapping so C14 has explicit coverage.
  > - Handle testing requirements through their existing testing owners; avoid inventing a duplicate testing authority.

  > Do not create a new architecture family or add loose normative files at the architecture root.  > Do not introduce a mandatory `interfaces/` directory.  > If repository governance requires an ADR for the new normative decision, report the exact requirement before introducing one. Never reinterpret or rewrite ADR 0010 as the owner of this separate decision.  > ## 10. Execution boundary

  > The architectural contract above is fixed for this proposal. Do not return an alternative standards selection.  > First perform a focused read-only repository preflight:  > 1. Verify the current PR #211 state and the canonical documentation owners.
  > 2. Identify the exact paths that need modification to implement C14 and its mappings.
  > 3. Identify any direct contradiction between this contract and an existing accepted rule or required governance process.
  > 4. Report the minimum edit plan, exact file scope and verification plan.

  > Do not conduct an open-ended architecture research exercise.  > **Do not modify files until I explicitly approve that exact implementation scope.**

- L2 — 2026-11-22 — User approval of the exact scope and the publication authorization, quoted verbatim. Outcome: the 14-path scope is approved, the standards selection is final, PR #211 continues, the one-time title update is authorized with a narrowly scoped exception rule, and the merge remains the user's alone.

  > The proposed 14-file implementation scope is approved, subject to the constraints below.  > We are continuing in the existing PR #211:  > https://github.com/JPerezC92/ai-core/pull/211  > Do not create another PR or implementation branch.  > ## 1. Approved architectural decision

  > Implement **C14 — External Output Contracts** according to the normative contract provided in my previous instructions.  > The standards selection is final for this task:  > - **REST JSON APIs:** JSend is the default response envelope for new project-owned APIs, with correct HTTP semantics, explicit payload schemas, stable AICore error codes and documented exceptions.
  > - **CLI:** Native exit codes, stdout/stderr separation, documented machine-readable JSON where supported, and stable error diagnostics.
  > - **MCP:** Native MCP/JSON-RPC results, negotiated protocol compatibility, structured output schemas and correct error classification. No mandatory JSend envelope.
  > - **Frontend:** Consume published API contracts without introducing JSend requirements into internal React components or operations.
  > - **Games and other interfaces:** Use appropriate typed contracts without imposing HTTP-specific response envelopes.

  > The producer and consumer must agree on the actual payload schema, not merely the outer response format.  > Preserve existing published contracts unless an incompatible migration is explicitly authorized.  > Do not reopen the selection of standards or replace these decisions with alternative recommendations.  > ## 4. PR #211 — Herald is responsible for GitHub publication

  > **Herald is the exclusive agent responsible for all Git and GitHub operations.**  > I explicitly authorize the following PR #211 publication operations:  > - Commit the authorized implementation.
  > - Push the existing PR branch.
  > - Regenerate and update the PR description through the established publication workflow.
  > - Verify the exact published diff, base, head and description.
  > - Update the PR title to the following exact value, subject to the authorization boundary below:

  > `docs(architecture): accept ADR 0010 and standardize output contracts`  > ### Narrowly scoped title authorization

  > I authorize a one-time, PR-specific title update by Herald for PR #211.  > This is not authorization to modify other PR titles, relax Git/GitHub security, bypass the permission system or change Herald's general governance.  > **Before attempting the title update, Herald must verify whether the existing prohibition on PR title mutation permits an explicitly user-authorized exception.**  > If the prohibition is absolute or the permission layer blocks the action:  > 1. Do not bypass the restriction.
  > 2. Do not delegate the operation to another agent.
  > 3. Do not silently modify Herald's instructions, permissions or runtime configuration.
  > 4. Report the exact restriction and the minimum governance change that would be necessary.
  > 5. Continue only with independently authorized operations; leave the title update explicitly blocked.
  > 6. Do not report READY FOR MERGE while this required publication condition remains unresolved.

  > Do not create a second PR to work around the restriction.  > The user retains exclusive authority over the merge decision.  > ## 6. Strict execution boundaries

  > - Work only within PR #211.
  > - No automatic merge.
  > - No unrelated refactoring.
  > - No migration of existing API, CLI, MCP or frontend implementations.
  > - No additional tooling or tests without demonstrated necessity and authorization.
  > - No changes outside the approved 14-file scope without renewed approval.
  > - No changes to general Git/GitHub permissions.

- L3 — 2026-11-22 — The request's normative contract text, quoted verbatim. It is the requirement source for S2–S9 and is preserved with L4 so every quoted Spec fragment has its source in this Log; its operative rule is delivered as `C14` in `.aicore/core/architecture/implementation/architecture.md`.

  > ## 2. Normative contract — API HTTP

  > ### 2.1 Applicability

  > For new, project-owned REST APIs that return JSON, **JSend is the default response-envelope format**.  > This applies across L1, L2 and L3 when the HTTP API responsibility exists.  > The rule does not mandate an additional architecture layer, wrapper class, service, or dependency-injection mechanism.  > ### 2.2 Success

  > A successful JSON response MUST follow the JSend success structure:  > `json
  > {
  >   "status": "success",
  >   "data": {
  >     "id": 123,
  >     "name": "Product A"
  >   }
  > }
  > `  > Requirements:  > - `status` is `"success"`.
  > - `data` is required.
  > - `data` contains the response payload defined by the endpoint contract.
  > - `data` may be `null` where the endpoint successfully returns no payload but uses a JSON response.
  > - The endpoint must use the appropriate HTTP success status.
  > - Do not generate redundant response metadata unless the endpoint contract requires it.

  > ### 2.3 Expected failures

  > For rejected input, invalid business preconditions, or other documented request failures, use JSend `fail` with an appropriate HTTP 4xx status.  > AICore's selected JSend profile requires a stable machine-readable error code inside `data`.  > `json
  > {
  >   "status": "fail",
  >   "data": {
  >     "code": "PRODUCT_NOT_FOUND",
  >     "details": {
  >       "productId": "Product does not exist"
  >     }
  >   }
  > }
  > `  > Contract:  > - `status` MUST be `"fail"`.
  > - `data.code` MUST be a documented, stable string identifier.
  > - `data.details` is optional and must follow the endpoint's documented schema when present.
  > - Do not return an HTTP 200 response to disguise a failed request.
  > - Do not generate arbitrary error identifiers.

  > The `data.code` structure is an **AICore JSend profile convention**, not a claim that the original JSend specification mandates this field.  > Preserve existing stable domain error identifiers where suitable, mapping them at the HTTP interface boundary.  > ### 2.4 Processing errors

  > For server-side processing failures, use JSend `error` and the appropriate HTTP 5xx status.  > `json
  > {
  >   "status": "error",
  >   "message": "Internal server error",
  >   "data": {
  >     "code": "INTERNAL_ERROR"
  >   }
  > }
  > `  > Contract:  > - `status` MUST be `"error"`.
  > - `message` MUST be a safe, documented client-facing message.
  > - The AICore profile requires `data.code` as a stable string error identifier.
  > - Do not expose stack traces, database internals, secrets or sensitive implementation details.
  > - Logging and diagnostic correlation must remain separate from the public error message.

  > Do not confuse `data.code` with JSend's optional top-level `code` field, which is traditionally numeric.  > Do not equate every 4xx response mechanically with a particular business error. Select the appropriate HTTP status and classify the failure according to its actual semantics.  > ### 2.5 HTTP semantics and exceptions

  > JSend does not supersede HTTP.  > - Use appropriate HTTP status codes.
  > - HTTP 204, HEAD responses, 304 and other bodyless responses MUST NOT contain a JSend body.
  > - File downloads, binary responses, server-sent events and streaming formats are not forced into JSend.
  > - GraphQL, gRPC, third-party APIs and other protocols retain their applicable contracts.
  > - Existing APIs retain their approved response contracts.
  > - When an existing API adds an endpoint, it follows that API's established contract rather than silently introducing a conflicting envelope.
  > - An explicitly approved alternative, such as RFC 9457 for HTTP errors, remains valid within its declared scope. Do not mix competing error envelopes arbitrarily within the same API contract.

  > ### 2.6 Schema requirements

  > JSend alone is not sufficient to guarantee compatibility.  > For each newly published REST JSON API operation intended for consumption by another application, define:  > - Request schema, when there is an input payload.
  > - Success response schema, including its JSend envelope and `data` structure.
  > - Documented error response schemas and corresponding HTTP statuses.
  > - Required and optional properties and their types.
  > - Stable machine-readable error codes.
  > - Any relevant pagination or versioning conventions.

  > Use OpenAPI for the API contract, or an already established equivalent contract source when justified by the project.  > Do not invent a global payload schema shared by unrelated business operations.  > Do not introduce a new OpenAPI generator or framework dependency solely because this policy is documented.  > ## 3. Normative contract — CLI

  > CLIs MUST use native command-line semantics rather than JSend.  > ### 3.1 Output streams

  > - Exit code `0` indicates success.
  > - A nonzero exit code indicates failure.
  > - `stdout` carries the primary successful output.
  > - `stderr` carries errors and diagnostics.
  > - Progress messages and logs MUST NOT corrupt a machine-readable stdout stream.
  > - A CLI that participates in pipelines must preserve predictable stream behavior.

  > Do not impose arbitrary global exit-code numbers beyond success versus failure. Additional exit codes must be documented when consumers depend on them.  > ### 3.2 Machine-readable JSON

  > A CLI MAY provide `--json` when automation consumers need structured output. It is not required for every tiny script.  > When a new CLI exposes `--json`:  > - Successful stdout MUST contain valid JSON following a documented command-specific schema.
  > - Do not add a mandatory JSend envelope.
  > - The command must not interleave logs or progress text with its JSON output.
  > - For failures, exit nonzero, leave stdout free of partial success data and emit a structured diagnostic to stderr.

  > Use this standard AICore diagnostic shape for new JSON-mode CLIs:  > ```json
  > {
  >   "error": {
  >     "code": "PROJECT_NOT_FOUND",
  >     "message": "Project directory not found"
  >   }
  > }
  > ```> The error code must be stable and documented.  > Existing CLI consumers and output formats remain unchanged unless migration is explicitly authorized.  > JSON Lines or another streaming representation may be used when the command's documented streaming behavior requires it; do not mislabel such output as a single JSON document.  > ## 4. Normative contract — MCP
```

  > MCP implementations MUST follow their negotiated protocol version and native tool-result semantics.  > Do not apply JSend as an additional universal wrapper.  > ### 4.1 Successful tool execution

  > A tool returning structured data SHOULD use `structuredContent` when supported and useful to its consumers.  > Its structured output MUST conform to the declared `outputSchema` whenever one is provided.  > Example of structured payload:  > `json
  > {
  >   "id": 123,
  >   "name": "Product A"
  > }
  > `  > This value belongs in the MCP tool result's `structuredContent`, not in a fabricated application-level JSend envelope.  > Preserve the required MCP `content` behavior and any applicable backward-compatibility representation.  > The MCP result's outer fields must conform to the negotiated protocol version.  > ### 4.2 Errors

  > Distinguish:  > 1. Protocol-level JSON-RPC errors, such as invalid protocol requests or unavailable tools.
  > 2. Errors occurring during tool execution, represented through MCP tool-result error semantics such as `isError: true`.

  > Do not represent tool-execution errors as successful tool results merely because a handler caught an exception.  > Do not automatically classify every legitimate "not found" outcome as a protocol error. The tool's published behavior determines whether absence is an ordinary result or an execution failure.  > Do not create redundant JSend statuses inside `structuredContent`.  > ### 4.3 Protocol version compatibility

  > - `resultType` and other version-dependent fields MUST only be required where the negotiated MCP version requires them.
  > - Do not impose the latest MCP wire format on implementations negotiated to earlier versions.
  > - `outputSchema` MUST be honored when declared, without requiring artificial schemas for tools whose output does not need structured results.
  > - For MCP servers using stdio, stdout remains reserved for MCP protocol messages.

  > ## 5. Normative contract — Frontend

  > Frontend applications MUST consume their API's actual published contract.  > When consuming an API that uses JSend:  > - Interpret `status` and `data` at the HTTP client or existing mapping boundary.
  > - Validate or type the returned payload according to the application's established approach.
  > - Translate the transport representation into the frontend's existing data and error model where appropriate.
  > - Do not require internal React components, Hooks, or application operations to return JSend objects.
  > - Do not duplicate JSend parsing across multiple components when a genuine shared boundary already exists.

  > Preserve F2/F3.  > For L1/L2 implementations, a simple API-client function may perform the mapping without creating an extra directory, wrapper class, or artificial application layer.  > Do not silently modify how existing frontends consume published APIs.  > ## 6. Normative contract — Games and other application channels

  > Internal game operations, UI events, state changes and engine callbacks are not HTTP APIs.  > Do not impose JSend or CLI/MCP response conventions on them.  > Use explicit types or schemas appropriate to their consumers.  > If a game exposes an HTTP API, CLI or MCP tool, that external interface follows the corresponding contract defined above.  > ## 7. Cross-cutting contract guarantees

  > These obligations apply whenever a published output contract exists, independently of the project's architectural complexity level.  > ### Producer/consumer compatibility

  > The producer and consumer MUST agree on the actual payload contract, not only on the envelope.  > Document:  > - Output shape.
  > - Required and optional values.
  > - Field types and semantics.
  > - Error identifiers.
  > - Relevant protocol statuses.
  > - Versioning and compatibility expectations where needed.

  > ### Stability

  > Existing published response formats MUST NOT be changed incompatibly without explicit authorization and a migration plan.  > Do not silently:  > - Rename or remove fields.
  > - Change required fields to incompatible types.
  > - Change successful responses into new envelopes.
  > - Change error-code semantics.
  > - Change CLI output streams or exit codes relied upon by consumers.
  > - Change MCP tool-result schemas unexpectedly.

  > ### Architectural ownership

  > Preserve C4, C5, C6 and C12:  > - Domain and Application remain independent of protocol-specific serialization.
  > - The appropriate Interface boundary owns external response translation.
  > - Infrastructure maps its own external representations without taking over channel serialization.
  > - L1/L2 do not inherit artificial Clean Architecture structures merely to satisfy an output-format rule.

  > ### Verification

  > Use focused contract verification for newly introduced or intentionally changed external interfaces.  > Examples:  > - HTTP: status code, JSend envelope, payload schema and error mapping.
  > - CLI: exit code, stdout/stderr separation and documented JSON output.
  > - MCP: tool-result shape, declared output schema and correct error classification.
  > - Frontend: compatibility with the published API schema.

  > Use existing testing infrastructure and applicable test contracts.  > Do not create a new framework, validator, test package, synthetic end-to-end environment, or per-file tests merely to enforce this documentation policy.

- L4 — 2026-11-22 — The request's and the approval's remaining sections, quoted verbatim. They carry the source for the S1, S11 and S12 requirement fragments and for the review and completion duties.

  > ## 9. PR #211 scope and governance
  >
  > Continue in the existing PR #211.  > The previous PR review PASS was obtained for the ADR acceptance scope only. It is superseded as final acceptance once the PR is expanded.  > Requirements:  > - Preserve the accepted ADR 0010 content and date.
  > - Keep the output-contract decision explicitly separate.
  > - Use the existing ODD workflow with accurate records and evidence.
  > - Do not rewrite previously closed historical entries to suggest the new output contract was part of their original scope.
  > - Update the PR title and body to describe the actual expanded change.
  > - Reconcile all required verification and independent reviews against the final immutable HEAD.
  > - Herald alone performs Git/GitHub operations.
  > - Do not merge the PR.
  > - Do not migrate existing applications or deploy the new contract to destination repositories.
  >
  > ## 2. Authorized documentation changes
  >
  > Proceed with the 14 paths from your approved preflight:  > 1. `.aicore/core/architecture/implementation/architecture.md` — add C14 as the single normative owner.
  > 2. `.aicore/core/architecture/README.md` — update navigation and rule ranges.
  > 3. `implementation/shapes/backend.md` — C14 applicability.
  > 4. `implementation/shapes/scripts.md` — C14 applicability.
  > 5. `implementation/shapes/frontend.md` — C14 applicability.
  > 6. `implementation/stacks/_template.md` — mapping and reference.
  > 7. `implementation/stacks/typescript/nestjs.md` — JSend profile and HTTP-specific implementation mapping.
  > 8. `implementation/stacks/typescript/react.md` — frontend contract consumption.
  > 9. `implementation/stacks/python.md` — CLI, HTTP and MCP applicability.
  > 10. `.opencode/agents/bastion.md` — C14 recognition.
  > 11. `.opencode/agents/atrium.md` — C14 recognition.
  > 12. `.opencode/agents/crucible.md` — C14 recognition.
  > 13. `odd/features/architecture-contract.md` — R27–R29; preserve R17.
  > 14. `odd/tasks/2026-11-22-external-output-contracts.md` — new governing ODD record.
  >
  > Paths 3–9 are relative to `.aicore/core/architecture/implementation/`.  > Do not introduce duplicate normative rules across shapes and implementation guides.  > Do not add a new architecture layer, runtime wrapper library, shared serializer, mandatory directory, dependency or migration.  > No production code changes are authorized.  > ## 3. ADR and historical records
  >
  > - Preserve ADR 0010 as Accepted, effective 2026-11-22.
  > - Do not modify its original decision or acceptance evidence.
  > - Do not create ADR 0011.
  > - Preserve previously closed ODD records and their historical statements.
  > - Record the new output-contract decision and its evidence in the new ODD record.
  > - Do not modify or claim completion of R17.
  >
  > ## 5. Review and verification
  >
  > Follow the existing ODD process.  > Required architecture reviews:  > - **Bastion:** C14, backend/scripts, NestJS/Python, template and applicability.
  > - **Atrium:** frontend shape and React implementation mapping.
  > - **Crucible:** testing-contract compatibility and the relevant agent-runtime changes, without introducing unnecessary new testing requirements.
  > - **Sentinel:** documentation ownership, identifiers, durable requirements, ODD records and agent-runtime changes.
  > - **Inquisitor:** independent PR review at the final immutable HEAD.
  >
  > Use the existing validators, formatting checks, identifier checks and evidence requirements.  > Do not fabricate validation results or claim that unchanged testing contracts were re-verified without evidence.  > The previous PR #211 PASS only covered the earlier ADR-acceptance scope and is not sufficient for the expanded implementation.  > ## 7. Completion requirements
  >
  > At completion, report:  > 1. Exact files changed.
  > 2. Final C14 contract and mapping coverage.
  > 3. Validation evidence and review verdicts.
  > 4. Final commit SHA.
  > 5. PR #211 publication status.
  > 6. Exact live PR title and description verification.
  > 7. Any unresolved permission or governance blockers.
  > 8. Remaining limitations.
  >
  > Only declare **FINALIZED — READY FOR MERGE** when the authorized implementation and all required publication and review gates are complete.  > Otherwise, report **BLOCKED** with the precise unresolved condition and required user decision.  > Never merge without my explicit approval.

- L5 — 2026-11-22 — Round-1 architecture-owner gates, the corrections applied, and the durable-file account.

  > Verdict: Bastion 🧱 (Backend & Scripts Architect) `[FAIL]` with three findings — the NestJS guide claimed the `fail`/`error` envelope achievement without naming its producer, the Python guide restated the rule instead of naming its mechanisms, and the backend shape restated `C6`/`C12`. Atrium 🏛️ (Frontend Architect) `[FAIL]` with two findings — the React guide mapped `C14` to JSend unconditionally, and the frontend shape and guide restated the prohibition. Crucible 🔥 (Test Architect) `[PASS]` with zero open findings and no testing change required. Sentinel 🛡️ (Quality Guardian) `[FAIL]` with four findings — a bare roster form in a task row, requirement fragments whose source was missing from the Log, the same rule restatement in the shapes and guides, and the missing durable-file account.

  > Correction: every finding was in scope, local, reversible and single-answer, so all were corrected in this work unit. The NestJS guide now names the global exception filter that binds a thrown domain error to the `fail` shape and an unexpected exception to the `error` shape; the Python guide names its stdout, stderr and exit mechanisms; the backend shape cites `C6`/`C12` instead of restating them; the frontend shape and the React guide cite `C14` without restating it and scope the JSend mapping to a contract that uses JSend; the task row uses the full roster form; and L4 supplies the omitted request and approval sections, so every quoted Spec fragment now has its source in this Log.

  > Durable-file account: `odd/features/architecture-contract.md` gained `R27`–`R29`, the output-contract requirements. `R17` was left unticked and untouched, no other requirement was added, reworded, retired or re-verified, and the file's derived status stays `partial`. The ticks on `R27`–`R29` assert the delivered requirements and are backed by the owner gates' verification recorded at L6.

  > Verification on the corrected bytes: `node .agents/skills/odd-workflow/scripts/validate_feature.ts odd/tasks` → all records ok; `node .agents/skills/odd-workflow/scripts/validate_feature_file.ts odd/features` → all records ok, `architecture-contract.md` derived status `partial`; `node .agents/skills/op-skill-creator/scripts/check_markdown_text.ts --policy .aicore/core/knowledge/unicode-policy.json` over the changed paths → no findings; `pnpm exec biome format` over the 14 authorized paths → no fixes applied.
