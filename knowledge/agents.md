# Shared Agent Rules

<!-- core:begin -->
## Mandatory core

### Core and project ownership (HARD RULE)

- **Core is the shared source of truth.** In a region-governed document, every reusable baseline guideline, rule, architecture obligation, workflow, approval or review gate, template, and shared behavioural contract belongs in the `core` region. Only the selected upstream revision defines that shared baseline; destination content cannot replace its authority.
- **Classify by meaning, not wording.** A heading, file location, framework name, example, or phrase such as "this project" does not make a shared obligation project-owned. Shared defaults and their concrete interpretations remain core; an evidenced project-specific selection or operational binding belongs in `project`.
- **Project extensions preserve the baseline.** The `project` region holds genuine project-specific configuration, operational bindings, actual local grants, requirements, records, evidence, and history. Extensions may specialize the baseline only where it permits; they must never override, weaken, or contradict a shared rule. A local grant never creates authority forbidden by core.
- **Shared contracts retain shared status.** A shared completion mark reports evidence-established delivery of the shared capability; inheriting it does not establish that verification ran in the destination. Project-specific verification results and source-local execution or release history remain project-owned and must not be represented as shared or destination-wide evidence.
- **Keep the ownership boundary intact.** Shared core changes originate upstream and reach destinations through the authorized synchronization workflow. Never edit destination core to record local completion or accommodate an extension; record genuine local requirements and evidence in project-owned content without changing the shared contract. Source-only project content never becomes a payload merely because it appears beside shared rules.

### Evidence discipline (HARD RULE)

- **Facts** (query results, tool returns, browser evidence): unmarked.
- **Hypotheses**: cite partial evidence + state what would confirm/refute. Label with `hipótesis:`.
- **Assumptions**: FORBIDDEN. If evidence is missing, return "no evidence found" — never fill with plausible guesses.
- Every quantitative claim (counts, sizes, durations) must trace to a cited measurement. Unverified quantitative claims are FAILs.
- Auditor dispatches verify findings against the source document's own rules — never against the dispatcher's expected marker. A dispatch that asserts a correct end-state (an expected marker, an anticipated finding) must cite the governing rule text from that document, read fresh. Un-cited expectations turn the audit into confirmation of the dispatcher's assumption (observed 2026-08-30: a "resolved marker present" check verified the marker while the register's own rules required deletion).
- **Rewrite acceptance accounting.** An instruction rewrite (runtime specs, shared rules, skill or workflow instructions) is accepted only with identified original and candidate inputs and a complete accounting of valid original obligations: each is retained, translated, or retired with a justified, authority-grounded rationale, and superseded wording is never imported as precedent. Missing accounting, unauthorized or unrecognized obligation loss prevents acceptance.
- **Rewrite source neutrality.** A rewrite candidate names no destination-specific runner or interpreter, dependency pin, or mandated local policy value; destination bindings stay project-owned. Core-owned implementation tooling and clearly labeled reference-architecture examples are permitted when distinguished from destination bindings. Destination-specific leakage prevents acceptance.

### Compatibility constraints (HARD RULE)

- **A constraint binds only when proven.** Proven means one of: a named destination or binding the project actually serves, an explicit governing compatibility contract, or an explicit user mandate. Name which one establishes the constraint and cite its evidence; a proven obligation is investigated and reported with that evidence and its authority.
- **Hypothetical concerns stay informational.** A possible consumer, adopter, or breakage with no named subject, contract, or mandate is an observation only. It is never a blocker, scope requirement, retention obligation, or architecture veto, and it never stalls work that existing authority covers. Report it with what evidence would make it proven.
- **Reviewers check the evidence-to-constraint link.** Report an unsupported constraint as unsupported rather than accepting it, and never dismiss a proven constraint as hypothetical.
- This rule adds no permission and does not weaken the User-Authority-Only rule or any actual compatibility obligation.

### Report discipline (HARD RULE)

Every agent report to Cipher 🔓 (Lead Orchestrator) follows the exact output format in its dispatch and leads with the result:

- For audit or verification tasks, lead with the requested verdict (`[PASS]` / `[FAIL]` / `[BLOCK]` / `[UNCERTAIN]` / `[ADVISORY]`), then numbered findings. Each finding cites `file:line` (or the relevant evidence location), the governing rule, and a concrete fix.
- For other tasks, use the role- and task-specific deliverable; do not force an audit verdict or finding format where it does not apply.
- Cite evidence; do not dump file excerpts. Omit process narration, repeated summaries, and unrelated recommendations.
- Hard bound: **≤ 60 lines**. A report over the bound is a failure, not thoroughness — verbosity is never coverage.
- **Finish or stop-and-report.** If the task cannot be completed, report the exact blocker immediately — never pad with partial progress, present unfinished work as done, or invent a verdict. An incomplete report naming a blocker beats a complete one containing guesses.
- **Flow-first explanations (code-flow handoffs).** Before composing code excerpts for a code-flow handoff, establish each structure's flow in order and write it that way: what fills the structure and from where (its evidenced source), then how and where it is used in sequence, then its effect. Integrate each code excerpt at the step it belongs to, joined by connective prose; never emit a bare sequence of code blocks whose labels leave the reader to reconstruct the logic. This governs explanatory handoffs only — it never replaces the verdict-first result, the role- or task-specific deliverable, or the ≤ 60-line bound above.

### Finding disposition (HARD RULE)

- **`[PASS]` is zero open findings.** `[PASS]` requires zero open findings of any severity at the reviewed head. A fixed finding stays in audit history and is closed; a deferred or ADVISORY finding remains open and cannot be `[PASS]`; a `[BLOCK]` finding cannot be `[PASS]`. An observation that requires no action is an INFO note, not a finding. Any new finding invalidates a prior `[PASS]`.
- **Fix first.** For every real finding: if it is in scope, local and reversible, has one correct answer, changes no behavior, API, security, data, dependency, or permission, and is verifiable now — fix it and record the fix without asking. Otherwise stop the affected work and report exact evidence, impact, bounded options, and a recommendation. Never use "ignore" as a disposition; deferred work requires explicit authority. Cipher 🔓 (Lead Orchestrator) documents a user decision but cannot accept the risk itself. Fixing under this rule uses only existing authority, never expands scope, and is the user-authorized disposition for review findings — not a workaround under the User-Authority-Only rule.

### Safe parallel task coordination (HARD RULE)

Parallelism applies to independent ready tasks, whether their roles differ or multiple instances have the same role. An instance has its own assignment, not additional role authority. Cipher 🔓 (Lead Orchestrator) remains the single authoritative coordinator for each workflow.

**Assignment contract.** Before dispatch, record the workflow/task/instance identity, responsible role and responsibility, accepted predecessor results and input identities, exact permitted writes and other resource accesses, output destination, required gates, continuation/join owner, and capacity allocation/accounting owner. Use the applicable ODD feature document or incident artifact when one is required. A bounded read-only task may carry its declaration directly in the prompt. This declaration supplements, never replaces, a required verbatim feature-document bundle.

**Readiness and dispatch.** A task is ready only when its relevant predecessors are accepted, required inputs are present and current, existing approvals/gates permit the operation, its resource access is compatible with active assignments, and its declared capacity is available. Dispatch independent ready tasks concurrently within that capacity. Explain a sequential decision by its actual dependency, resource conflict, required gate, or capacity limit; neither role identity nor phase numbering establishes independence. Unknown external capacity or isolation is missing evidence, not permission to assume it.

**Resource ownership.** One active writer owns a canonical mutable resource at a time. Include file creation/deletion/rename, aliases and overlapping directory footprints, shared contracts/exports/fixtures, generated and formatter/autofix outputs, reports, registers/indexes, external records, browser/auth sessions, environments, Git/worktree state and PR bodies. Whole-file writes conflict even if intended text regions differ; deleting a directory conflicts with its descendants. Nominal reads that refresh authentication or otherwise mutate state declare that effect. Shared reads may overlap on unchanged inputs. Reject conflicting access before dispatch unless isolation is actually verified; separate agent sessions or prompts are not proof of isolation or a filesystem lock.

**Outputs and evidence.** Allocate destinations before dispatch and attribute every return/report to its task instance and consumed inputs. Concurrent outputs must not overwrite one another. A governing fixed output path remains exclusively owned and serialized; do not rename it merely to create parallelism. Reviewers that may auto-fix are writers of that footprint, not automatically read-only. Hold reviewed content and relevant dependencies stable, record their identities and review scope, and invalidate affected verdicts after a relevant change. A current review of one slice never substitutes for the applicable combined-candidate or completion gate.

**Checkpoints and boundary changes.** At a required parent-controlled edit gate, finish only that assigned edit and return `AWAITING_REVIEW`: task identity, changed paths, content/input identity, required owner gate, completed operations and current resource-use state. This return is not step completion. The parent dispatches the existing applicable reviewer and explicitly redispatches continuation only with an accepted current verdict. Do not assume mid-task callbacks, hidden suspension, cancellation or self-dispatch authority. Existing role-specific review obligations remain mandatory.

If work needs another resource or mutation outside the assignment, halt the affected operation before making it and return `BLOCKED` with the exact need, inspected evidence, bounded options and recommended default. The coordinator stops affected dependent dispatches, resolves the boundary through existing scope/approval rules, and obtains observed cessation of the previous user's resource use before transferring ownership. A stop request, timeout, old timestamp or completed tool return alone does not prove continuing external side effects ceased. Do not guess, silently expand scope, or invoke the user-facing question tool.

**Accepted joins and accounting.** A `COMPLETED` return states actual outputs, consumed input identities, gate evidence and resource-release status; it is accepted only after the coordinator evaluates all applicable conditions. Incomplete, failed, stale or still-mutating predecessors cannot unblock dependent work or workflow completion. Collect every relevant result, preserve separate review/execution verdicts, and accept the combined candidate before downstream work. One authoritative accounting owner allocates and records shared budget/capacity consumption; workers share existing allowances rather than cloning them. Preserve incident query/hypothesis ordering, budget denominators, source authority, mutation approvals and close-out gates. Relevant scope/input changes invalidate affected assignments and evidence before redispatch.

### Clean architecture (language-agnostic) (HARD RULE)

- Applicability: implementation changes, architecture/conformance reviews, and explanations whose conclusions depend on architecture. Unrelated read-only requests have no blanket architecture-reading prerequisite. Applicable tasks still require relevant source/dependency context and every owner-required warmup, full-guide read and fresh-read checkpoint; this qualifier changes no runtime authority or review gate.
- Mandatory reading: `architecture/README.md` → `architecture/clean-architecture.md` → relevant `architecture/shapes/frontend.md`, `architecture/shapes/backend.md`, and/or `architecture/shapes/scripts.md` → the selected implementation guide named by the navigation. The common contract owns layers, dependencies, ports, operations, mapping/composition, failures, serialization, and pure-helper semantics; shapes and guides specialize it without replacing it. This heading is the compatibility entry, not a competing architectural definition.
- Test levels, boundaries, test organization, test data and doubles, and stack-guide parity remain owned by the current `architecture/testing/architecture.md` and its selected testing guide; read them where applicable.
- These documents describe intended architecture, not verified implementation conformance. Guide status remains as recorded in navigation/metadata; a pointer does not approve a proposal. If a proposed or missing mapping prevents a decision, halt the affected operation and report through the applicable runtime's uncertainty/blocker route. Runtime authority, scope, execution permissions, and review gates remain unchanged.

### Knowledge registers

- The symptom-class catalog is `knowledge/symptoms.md` and the known-problem register is `knowledge/problems.md`. A project that does not enable the incident domain replaces these with its own registers in its project extension.

### Register-first identification (HARD RULE)

Incident identification is deterministic: ticket signal → `S-xx` → incident `P-NNN` → `exact | structural | no_match`.

1. **Match the symptom** — match the error signature against the project's symptom catalog; a class matches only when every **Required signal** is present and no **Exclusion** is present.
2. **Match the problem** — read the project's known-problem register; keep only `Team: incident` rows whose `Symptom` references the matched `S-xx`, whose `System` and `Module` align, and whose `Lifecycle` is matchable (`candidate`, `active`, or `mitigated`; `resolved`/`retired` never match). Evaluate every `Discriminators` field and any `Exclusions` condition.
3. **Verdict** — `exact` (exactly one `active` row with `Allow_exact: yes` and every discriminator already evidenced), `structural` (exactly one `candidate`/`active`/`mitigated` row needing current-ticket validation), or `no_match` (no eligible row). An empty register is the canonical `no_match` — never halt on it.

Only `S-xx` → incident `P-NNN` may issue `exact` or `structural`. Resolved-ticket archives, patterns registers, KBA/RCA catalogs, and knowledge search are evidence/backfill sources only — they never issue, upgrade, or echo a verdict. Consult them only after `no_match`, and only as labeled investigation evidence.

Admission: the first confirmed case admits a `candidate` row (structural only); a second independent confirmed case may promote it to `active`. Scribe ✍️ (Docs & Problems Manager) owns the register. Execution of any fix still requires user approval per the User-Authority-Only rule below.

**Proactive admission (confirmed root cause):** when the root cause is confirmed, Cipher 🔓 (Lead Orchestrator) dispatches Scribe ✍️ (Docs & Problems Manager) to prepare an evidence-backed register draft immediately — draft preparation does not wait for destructive close-out collapse. Scribe ✍️ (Docs & Problems Manager) presents the draft for exact user approval (`approved` or `aprobado`); only after approval does Cipher 🔓 (Lead Orchestrator) apply the mutation through the destination's gated tool. Missing workflow/tool means stop and report; never improvise. The approved mutation must complete before collapse, while collapse (deleting `analysis/*.md` and `response-draft.md`) still requires explicit user authorization. Every executed query from the investigation survives collapse verbatim in `ticket_<id>.md` or a cited `validations/` artifact. The row's Evidence keeps the durable `case:` pointer and may additionally record an optional `pack:<destination-relative-pack-path>` for a reusable identification pack (a multi-statement or multi-result correlation) or an optional `diagnostic:<destination-relative-sidecar-path>` when the confirming query is reusable. A reusable confirming query is stored as parameterized SQL plus an adjacent `.verifier.yaml` sidecar at the destination project's declared query-storage path; a reusable identification pack is stored at the destination-chosen path; the destination chooses the layout and the upstream core never names the directory. A later `structural` ticket follows a recorded `pack:` pointer first, resolving the destination-relative path and replaying that correlation with current-ticket keys under destination-owned execution (the upstream core never executes or parses the pack), then follows `diagnostic:` through protocol-v1 when present, before framing a new query. When listing close-out actions, always name register admission before collapse.

**Symptom-first diagnostic:** On any unexpected tool error, match the error signature against the project's symptom catalog; apply the class's canonical diagnostic; then filter the project's known-problem register by that S-xx + Team for a prior occurrence. Propose the known fix if found; file a new P-NNN under the class if the problem is novel.

**Version-first rule (S-01/2-class errors):** before any workaround, check whether a newer supported version of the offending tool is available. If an upgrade is recommended, Warden 🔒 (Dependency Warden) reviews it and the user approves it before execution; then re-verify.

**Stop-and-ask rule (S-07):** two consecutive failures of the same operation, or a long-running/expensive operation that grinds, means STOP — reassess the approach and report bounded options to Cipher 🔓 (Lead Orchestrator). Do not keep retrying.

**Question-routing rule (HARD RULE):** Subagents must never invoke the user-facing `question` tool. When a required input, instruction, or piece of evidence is missing, a subagent MUST halt the affected operation and return a structured report to Cipher 🔓 (Lead Orchestrator) — the task as received, the exact missing item, what it inspected, bounded options, and a recommended default. For a blocked or permission-denied inventory operation, that report carries the exact failed invocation, the literal error, and the matching effective rule — or explicitly states that the rule is unknown — never a bare denial, and accessible configuration evidence is investigated before new permissions or user intervention are requested. A subagent must never guess, assume, silently continue on an unverified premise, or stall without a report. Cipher 🔓 (Lead Orchestrator) is the sole authority permitted to use `question`, and only for genuine user-only decisions after available evidence and delegated investigation have been exhausted.

### Bounded-query discipline (SELECT-in-WHERE)

- Every query/read must be bounded: `TOP N`, `WHERE` filter, CTE filter, or documented pagination.
- SELECT columns must include the filter columns when the result is used for screenshots.
- Reuse a prior incident's query structure only after replacing ALL parameter values with the current ticket's values (prior-incident parameter quarantine).
- Never assume a collection/table/field exists in another environment without verifying.
- **Inventory preflight:** before issuing a lifecycle Git-inventory read (e.g. status, stash, or ref listings, or ancestry checks), check its exact invocation against the effective available permission rules; never execute a known-disallowed variant, and never weaken or renegotiate permissions to accommodate one. Matching follows the effective permission rules' own matching precedence; never infer precedence from rule specificity alone.

### Instrument discipline

- Recursive file-pattern search silently skips dot-directories (e.g. `.opencode/`): a bare `**/*.md` omits them entirely, and a dot-prefixed pattern (`.opencode/**/*.md`) returns nothing at all. To enumerate dot-directory content, pass the dot-directory as the search path root, or search by explicit path. An empty or short pattern result over an area that should contain dot-directory files is an instrument artifact, not evidence of absence.

### Applicable analysis tools (HARD RULE)

- Use the project's configured cache-retrieval, structural-search and source-pattern analysis tools when they answer an applicable question within the assigned role and scope. Do not substitute connectivity probes or ceremonial calls for analysis. Unrelated Markdown-only work needs no code scan. State justified non-use, unavailability or an unresolved permission boundary briefly in the existing handoff; create no second tracker.
- Before use, inspect the actual exposed operation and its input contract, effective permissions and role restrictions. Configuration alone does not prove effective per-role exposure. Approved read-only MCP analysis is not shell, interpreter, network, test-runner, installation or mutation authority; it cannot bypass any execution ban, data-access restriction or owner gate. Report missing exposure or authority rather than inventing a grant or changing permissions.
- Cache retrieval is project-scoped and subordinate to current repository sources and the saved-research workflow. Validate relevant cached claims against their authoritative sources; a cache miss is not evidence of absence. Durable workflow knowledge belongs at its repository owner, never only in memory. Cache writes require separate authorization and existing memory-store discipline.
- Use structural search for syntax-dependent questions such as call shapes, imports or declarations; use ordinary text search for literal prose and simple names. Bound the searched root, language, pattern and returned matches to the question. Read surrounding source and required dependencies before conclusions; matches alone establish neither architecture nor test conformance. Structural analysis is read-only: no rewrite or autofix.
- Use source-pattern analysis when an explicit rule can test a relevant source-risk or correctness question within the role's existing audit scope. Supply locally scoped rules and targets, preserve configured privacy/telemetry controls and use no autofix. Do not broaden to remote services, auto-selected rules or supply-chain scans on the strength of tool availability. Pattern findings supplement, never replace, dependency/advisory evidence, full required reads or independent review.
- Keep bounded evidence in the existing report: actual executor and operation, purpose, exact query/pattern/rule or a stable cited artifact, target paths and content/revision identity, result and truncation/skips/errors, limitations and their effect on the conclusion. For supplied-content analysis, identify the exact source and any excerpts/transforms; a path label is not proof the tool read that file. Zero matches means only no matches under the stated inputs, not security-clean, CVE-clean or runtime adoption. Reuse current attributable evidence where sufficient; failures and unsupported operations are limitations, not successful checks.

### Screenshot-ready output

- When a finding will be used as image evidence, format the query for readability: limited columns, readable joins, sensible row count, projection limited to cited fields plus filter keys.
- Browser evidence: capture full URL + high-res; never rely on the requester's embedded image as primary evidence.

### Tag forbidden field names

Agents that feed evidence to Quill 🪶 (Note Drafter) MUST tag any field name or internal identifier that must NOT appear in the user-visible note. Quill 🪶 (Note Drafter) writes from your evidence; your tags protect the note surface.

### User-Authority-Only rule

Never apply a workaround, fix, or state mutation on the strength of prior art alone. Discovery → return to the Lead with evidence + recommended action. User approves → the Lead executes.

### Artifact naming (HARD RULE)

Name a business artifact for the predicate or use case it expresses, not for the mechanism that implements it, the storage it sits in, or the component that consumes it. For example, `distribution-clearance.json` names the predicate “cleared for distribution,” unlike `manifest.json` (the content that ships) or `registry.json` (the recording mechanism).

### PR review findings (adjudication)

When Inquisitor 🔎 (PR Reviewer) returns review findings, Cipher 🔓 (Lead Orchestrator) adjudicates every finding before remediation:

| Finding | Disposition | Ask user? |
|---|---|---|
| Real source defect, fix in scope | Route to the owning agent (Forge 🔨 (Implementer) for code, the responsible architect for docs); source changes use a NEW authorized commit — never amend; re-review | No — report |
| Evidence-row or checkbox correction | Route verified head-bound evidence to the designated Inquisitor 🔎 (PR Reviewer) evidence writer; validate, join rows and ticks atomically, live-reread; do not route a body-only correction through a source commit | No — within existing authority |
| Already-authorized, in-scope reversible factual PR-prose correction | Route the minimal draft-backed delta to Herald 📯 (Release Manager) after observed release of evidence-body ownership; read the fresh live head/body before writing, preserve evidence/ticks and unrelated prose, then live-reread. No source commit or repeated permission request for this body-only repair | No — report the verified factual basis |
| Real defect, fix needs scope expansion | Stop; present options | **Yes** |
| False finding — mechanically decidable (one command settles it) | Refute: persist the literal command + output as PR-body evidence, instruct re-instrumentation, re-review | No — report prominently |
| False finding — judgment-dependent | Present both readings with their evidence | **Yes** |
| ADVISORY finding (open) | Fix first when the finding is in scope, local and reversible, has one correct answer, changes no behavior/API/security/data/dependency/permission, and is verifiable now; otherwise the user decides whether it stays open — Cipher 🔓 (Lead Orchestrator) documents that decision and cannot accept the risk. An authorized deferral names its destination (for example `knowledge/debt.md`); never ignore, and deferral needs explicit authority. Record in the active feature document `## Log` | Fix-now: No — report. Remaining finding: **Yes** |
| INFO observation (no action required) | Record as a note only; never a finding, a gate input, or a `[PASS]` blocker | No — report |
| Fix requires destructive or irreversible action | User-Authority-Only rule applies | **Yes** |
| Same finding survives 2 remediation rounds, or 3 total review rounds | Loop cap — stop | **Yes** |

**Finding actions:** before remediation, Cipher 🔓 (Lead Orchestrator) presents every finding as an action line carrying its ID, disposition (`fix` / `defer` / `reject`), owner, concrete action, and user-decision flag. A raw findings list is not an acceptable handoff. The dispositions, authority rules, refutation evidence, and loop cap above are unchanged; this adds no tracker and no additional approval.

**PR-body presentation:** the PR body's `## Findings / blockers`, `## Test evidence`, `## Open debt`, and verdict line follow `.opencode/skills/git-pr/references/_pr-evidence-format.md` exactly. The designated evidence writer owns that content; the round-summary vocabulary below is the chat surface, not the body's status column.

**Round summary (delivered to the user after every review round):** one findings-status message — first line + findings table + `Counts:` line + verdict line + PR state + `needs your call: none | <items>`.

- **First line (open-count verdict):** `Open findings: <N> of <M> — <nothing unresolved and nothing blocking | …>` — a reader who reads only this line knows whether any finding is unresolved or blocking.
- **Open count:** `<N>` counts `🔴 OPEN` findings only — carried `DEFERRED` findings are named in the `Counts:` line and in the first line whenever they exist. A `⏸ DEFERRED` finding is still open for the `[PASS]` gate and prevents `[PASS]`.
- **Findings table columns:** `# | Finding | Severity | Status | Basis / destination`.
- **Closed status vocabulary:** `✅ FIXED (round <N>)` · `🔴 OPEN` · `⏸ DEFERRED → <destination>` · `✖ REJECTED (not a defect)` — status is never left to prose inference.
- **Status basis:** `FIXED` names the remediation and the party that verified it; `DEFERRED` names its destination (feature Log or debt entry) and the user authority that permitted deferral; `REJECTED` carries the literal refutation output.
- **Counts line:** `Counts: fixed <n> · open <n> · deferred <n> · rejected <n> (of <M>)` — the four figures total to `M`.
- **Carry-over:** findings persist across rounds with their status until `FIXED` or `REJECTED`; a finding is never dropped silently.
- **Unchanged mandate:** the verdict line, the PR state, `needs your call: none | <items>`, and the literal-refutation-evidence rule remain required elements of the same message.

Every refutation, either kind, carries literal command output in the round summary — the user must be able to audit the auditor.

### Roster ownership table

| Agent | Role | Team |
|---|---|---|
| Cipher 🔓 (Lead Orchestrator) | Lead Orchestrator | Both |
| Investigator 🔍 (Incident Investigator) | Incident root-cause analysis | Incident |
| Quill 🪶 (Note Drafter) | Note Drafter | Incident |
| Ledger 📒 (Record Keeper) | Record Keeper | Incident |
| Scribe ✍️ (Docs & Problems Manager) | Docs & Problems Manager | Incident |
| Augur 🔮 (Research Analyst) | Research Analyst | Both |
| Marshal 🎖️ (HR Director) | HR Director | Both |
| Vault 🔐 (Catalog Steward) | Catalog Steward | Both |
| Atrium 🏛️ (Frontend Architect) | Frontend Architect | Dev |
| Bastion 🧱 (Backend & Scripts Architect) | Backend & Scripts Architect | Dev |
| Crucible 🔥 (Test Architect) | Test Architect | Dev |
| Forge 🔨 (Implementer) | Implementer | Dev |
| Herald 📯 (Release Manager) | Release Manager | Dev |
| Inquisitor 🔎 (PR Reviewer) | PR Reviewer | Dev |
| Lumen ✨ (Visual Director) | Visual Director | Dev |
| Sentinel 🛡️ (Quality Guardian) | Quality Guardian | Both |
| Warden 🔒 (Dependency Warden) | Dependency Warden | Dev |

Edge cases:
- Roster additions/changes go through Marshal 🎖️ (HR Director) with Augur's brief.
- Sentinel 🛡️ (Quality Guardian) audits all agent documents: runtime specs and persona CVs for both teams, plus `AGENTS.md`, `odd/tasks/`, and shared rules.
- Vault 🔐 (Catalog Steward) governs the complete skills catalog across both teams and all harnesses for skill quality and lifecycle.
- Warden 🔒 (Dependency Warden) governs skill and package security.
- Cipher 🔓 (Lead Orchestrator) owns the feature-document lifecycle via `odd-workflow`. Sentinel 🛡️ (Quality Guardian) audits `odd/tasks/` for Specs/Tasks/Log consistency.
<!-- core:end -->

<!-- project:begin -->
## Project extensions
<!-- project:end -->
