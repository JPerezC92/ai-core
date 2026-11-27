<!-- core:begin -->
# Shared Agent Rules

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
- **Capability claims.** A claim about what a tool, command, interface or permission layer can or cannot do is a fact only when it rests on an executed probe or on the exact inspected source and revision. Prefer a runnable probe over inference from documentation, and record the probe identity before the claim drives a design decision. Never present an inferred limitation as an observed one, and never let an unverified capability claim shape a design.
- Checks verify findings against the source document's own rules — never against an expected marker. A review that asserts a correct end-state (an expected marker, an anticipated finding) must cite the governing rule text from that document, read fresh. Un-cited expectations turn a check into confirmation of the checker's assumption (observed 2026-08-30: a "resolved marker present" check verified the marker while the register's own rules required deletion).
- **Rewrite acceptance accounting.** An instruction rewrite (runtime specs, shared rules, skill or workflow instructions) is accepted only with identified original and candidate inputs and a complete accounting of valid original obligations: each is retained, translated, or retired with a justified, authority-grounded rationale, and superseded wording is never imported as precedent. Missing accounting, unauthorized or unrecognized obligation loss prevents acceptance.
- **Rewrite source neutrality.** A rewrite candidate names no destination-specific runner or interpreter, dependency pin, or mandated local policy value; destination bindings stay project-owned. Core-owned implementation tooling and clearly labeled reference-architecture examples are permitted when distinguished from destination bindings. Destination-specific leakage prevents acceptance.
- **Self-review is not independent verification.** A review produced in the context that authored the change shares the author's assumptions and blind spots. Describe it as self-review; never present it as independent verification, and never treat it as evidence of independent verification.

### Compatibility constraints (HARD RULE)

- **A constraint binds only when proven.** Proven means one of: a named destination or binding the project actually serves, an explicit governing compatibility contract, or an explicit user mandate. Name which one establishes the constraint and cite its evidence; a proven obligation is investigated and reported with that evidence and its authority.
- **Hypothetical concerns stay informational.** A possible consumer, adopter, or breakage with no named subject, contract, or mandate is an observation only. It is never a blocker, scope requirement, retention obligation, or architecture veto, and it never stalls work that existing authority covers. Report it with what evidence would make it proven.
- **Reviewers check the evidence-to-constraint link.** Report an unsupported constraint as unsupported rather than accepting it, and never dismiss a proven constraint as hypothetical.
- This rule adds no permission and does not weaken the User-Authority-Only rule or any actual compatibility obligation.

### Report discipline (HARD RULE)

Apply `AGENTS.md` → `### Shared conduct — all agents`. That conduct is shared by every role.

A report delivered to a user or to a delegate is written in the format its assignment prescribes and leads with the result:

- For an audit or verification request, lead with the verdict (`[PASS]` / `[FAIL]` / `[BLOCK]` / `[UNCERTAIN]` / `[ADVISORY]`), then numbered findings. Each finding cites `file:line` (or the relevant evidence location), the governing rule, and a concrete fix.
- For other work, use the deliverable the assignment names; do not force an audit verdict or finding format where it does not apply.
- Cite evidence; do not dump file excerpts. Omit process narration, repeated summaries, and unrelated recommendations.
- **Finish or stop-and-report.** If the work cannot be completed, report the exact blocker immediately — never pad with partial progress, present unfinished work as done, or invent a verdict. An incomplete report naming a blocker beats a complete one containing guesses.
- **Flow-first explanations (code-flow handoffs).** Before composing code excerpts for a code-flow handoff, establish each structure's flow in order and write it that way: what fills the structure and from where (its evidenced source), then how and where it is used in sequence, then its effect. Integrate each code excerpt at the step it belongs to, joined by connective prose; never emit a bare sequence of code blocks whose labels leave the reader to reconstruct the logic. This governs explanatory handoffs only — it never replaces the verdict-first result.
- A delegated report is bounded by its assignment. A report over that bound is a failure, not thoroughness — verbosity is never coverage.

### Shell command contract (HARD RULE)

- Run one bare shell command per invocation. Do not append `;`, `&&`, `||`, `|`, `>`, `2>`, `echo "EXIT=$?"`, `Out-String`, or temporary-file capture wrappers. One suffix is permitted and no other compound form is: the active shell's documented native-exit-code propagation form — a trailing exit of the shell's last-exit-code value — used only when the applicable verification contract distinguishes the numeric code, carrying no other command, and never as a substitute for running the command itself.
- Use the shell tool's captured output and exit status; do not create a temp file just to recover them.
- **Read the reported exit status as the tool states it.** The status a command reports belongs to the shell process that ran it, not necessarily to the command itself. A native command's own non-zero code is visible only when the invocation propagates it; a reported `1` from a native command is not that command's code; and a later successful statement in the same invocation can hide a native failure entirely. Report the exact status line the tool returned when it returned one, and report the command's own output as the evidence of what it did. A command whose result matters is invoked so that a non-zero result cannot be masked: bare, as the only statement of the invocation, or with the permitted propagation suffix when the contract needs the numeric code. Keep three signals distinct and never present one as another: the wrapper's reported status, the native command's own numeric code, which only the propagation form surfaces, and the command's own output. For a bare native invocation the reported status is two-valued — a non-zero line means the command did not succeed, and no line means the wrapper exited zero, which evidences that the invocation completed without a failure status but never what it achieved, so the command's own emitted result remains the outcome evidence. Never report a missing status line as an unavailable capability, never read the absence of a status line as proof of the outcome a command was meant to produce, and never treat partial stdout as a passed check. A result whose signal cannot be established is reported as unverified rather than as passed.
- If multiple operations are required, issue separate invocations or use a dedicated skill/script; never hide a restricted segment inside a compound command.
- A wrapper-induced permission prompt is a command defect. Fix the command; do not widen permissions to accommodate it.
- Report the exact failed command and literal permission/error output; never bypass a deny.
- **Git and GitHub execution belongs to Herald 📯 (Release Manager).** No other agent runs a `git` or `gh` command, read-only or mutating, and no agent obtains Git- or GitHub-derived evidence except through Herald 📯 (Release Manager). Agents analyze the supplied evidence; they never execute the command. The project's OpenCode command permissions deny `git` and `gh` to every agent except Herald 📯 (Release Manager); where the permission layer cannot reach a wrapped or nested invocation, the instruction is the control and the limitation is documented rather than patched with a new enforcement framework.

### Finding disposition (HARD RULE)

- A **finding** is a rule-grounded defect or gap needing disposition. **Severity** is text (`BLOCK` / `ADVISORY`) attached to a finding. An observation that requires no action is an INFO note, not a finding.
- **Fix first.** For every real finding: if it is in scope, local and reversible, has one correct answer, changes no behavior, API, security, data, dependency, or permission, and is verifiable now — fix it and record the fix without asking. Otherwise stop the affected work and report exact evidence, impact, bounded options, and a recommendation. Never use "ignore" as a disposition; deferred work requires explicit authority. The coordinator documents a user decision but cannot accept the risk itself. Fixing under this rule uses only existing authority, never expands scope, and is the user-authorized disposition for review findings — not a workaround under the User-Authority-Only rule.
- **An unresolved finding never becomes a clean readiness claim.** A required check that failed, any applicable guarantee that remains unestablished, and any open `BLOCK` finding keep the work not ready until each is fixed or the user decides otherwise. A missing independent reviewer is not such a finding and never by itself withholds readiness.
- **An independent review is optional.** When one is requested and returns findings, the same disposition rules apply; when none was requested, the absence of a verdict is not a gap to be recorded, and no stand-in verdict document or additional report is created to fill it.

### Clean architecture (language-agnostic) (HARD RULE)

- Applicability: implementation changes, architecture/conformance reviews, and explanations whose conclusions depend on architecture. Unrelated read-only requests have no blanket architecture-reading prerequisite. Applicable tasks still require relevant source/dependency context and every owner-required warmup, full-guide read and fresh-read checkpoint; this qualifier changes no runtime authority or review gate.
- Mandatory reading: `.aicore/core/architecture/README.md` → `.aicore/core/architecture/implementation/architecture.md` → relevant `.aicore/core/architecture/implementation/shapes/frontend.md`, `.aicore/core/architecture/implementation/shapes/backend.md`, and/or `.aicore/core/architecture/implementation/shapes/scripts.md` → the selected implementation guide named by the navigation. Select the project's complexity level (`C11`) before applying a layer, folder or operation obligation: L1 and L2 impose no layer folder and no operation class, and every obligation binds only where its responsibility exists. The common contract owns complexity levels, layers, dependencies, ports, operations, the Interface boundary, mapping/composition, failures, serialization, pure-helper semantics and the diagrams; shapes and guides specialize it without replacing it. This heading is the compatibility entry, not a competing architectural definition.
- Test levels, boundaries, test organization, test data and doubles, and stack-guide parity remain owned by the current `.aicore/core/architecture/testing/architecture.md` and its selected testing guide; read them where applicable.
- These documents describe intended architecture, not verified implementation conformance. Guide status remains as recorded in navigation/metadata; a pointer does not approve a proposal. Follow applicable documented specifics; for uncovered concerns, including partial guide coverage, apply the agnostic contract and applicable shapes directly under `.aicore/core/architecture/README.md` → `## Purpose and selection`. Missing guide coverage alone never blocks implementation or review or requires creating a guide. A real contradiction, missing authority, or decision-critical evidence gap still halts the affected operation through the uncertainty/blocker route.
- The agents named inside these documents are their historical attribution. Verification is performed by the implementing agent against the owner text, and an independent review may be requested; the standards themselves are unchanged by any review arrangement.

### Knowledge registers

- The symptom-class catalog is `.aicore/core/knowledge/diagnostics/symptoms.md` and the known-problem model is `.aicore/core/knowledge/diagnostics/problems.md`. AICore manages both; the project's own problem rows live in `incidents/diagnostics/problems.md` and its own symptom classes in `incidents/diagnostics/symptoms.md`. A project that does not enable the incident domain replaces these with its own registers in its project extension.

### Register-first identification (HARD RULE)

Incident identification is deterministic: ticket signal → `S-xx` → incident `P-NNN` → `exact | structural | no_match`.

1. **Match the symptom** — match the error signature against the project's symptom catalog; a class matches only when every **Required signal** is present and no **Exclusion** is present.
2. **Match the problem** — read the project's known-problem register; keep only `Team: incident` rows whose `Symptom` references the matched `S-xx`, whose `System` and `Module` align, and whose `Lifecycle` is matchable (`candidate`, `active`, or `mitigated`; `resolved`/`retired` never match). Evaluate every `Discriminators` field and any `Exclusions` condition.
3. **Verdict** — `exact` (exactly one `active` row with `Allow_exact: yes` and every discriminator already evidenced), `structural` (exactly one `candidate`/`active`/`mitigated` row needing current-ticket validation), or `no_match` (no eligible row). An empty register is the canonical `no_match` — never halt on it.

Only `S-xx` → incident `P-NNN` may issue `exact` or `structural`. Resolved-ticket archives, patterns registers, KBA/RCA catalogs, and knowledge search are evidence/backfill sources only — they never issue, upgrade, or echo a verdict. Consult them only after `no_match`, and only as labeled investigation evidence.

Admission: the first confirmed case admits a `candidate` row (structural only); a second independent confirmed case may promote it to `active`. The problem register is owned by the documentation and problem-management procedure. Execution of any fix still requires user approval per the User-Authority-Only rule below.

**Proactive admission (confirmed root cause):** when the root cause is confirmed, the coordinator prepares an evidence-backed register draft immediately — draft preparation does not wait for destructive close-out collapse. The draft is presented for exact user approval (`approved` or `aprobado`); only after approval is the mutation applied through the destination's gated tool. Missing workflow/tool means stop and report; never improvise. The approved mutation must complete before collapse, while collapse (deleting `analysis/*.md` and `response-draft.md`) still requires explicit user authorization. Every executed query from the investigation survives collapse verbatim in `ticket_<id>.md` or a cited `validations/` artifact. The row's Evidence keeps the durable `case:` pointer and may additionally record an optional `pack:<destination-relative-pack-path>` for a reusable identification pack (a multi-statement or multi-result correlation). A reusable identification pack is stored at the destination-chosen path; the destination chooses the layout and the upstream core never names the directory. A later `structural` ticket follows a recorded `pack:` pointer first, resolving the destination-relative path and replaying that correlation with current-ticket keys under destination-owned execution (the upstream core never executes or parses the pack), before framing a new query. When listing close-out actions, always name register admission before collapse.

**Symptom-first diagnostic:** On any unexpected tool error, match the error signature against the project's symptom catalog; apply the class's canonical diagnostic; then filter the project's known-problem register by that S-xx + Team for a prior occurrence. Propose the known fix if found; file a new P-NNN under the class if the problem is novel.

**Version-first rule (S-01/2-class errors):** before any workaround, check whether a newer supported version of the offending tool is available. If an upgrade is recommended, the dependency review in `dependency-review` covers it and the user approves it before execution; then re-verify.

**Stop-and-ask rule (S-07):** two consecutive failures of the same operation, or a long-running/expensive operation that grinds, means STOP — reassess the approach and report bounded options. Do not keep retrying.

**Question-routing rule (HARD RULE):** the user-facing question tool is used only for a genuine user-only decision, after available evidence and delegated investigation have been exhausted. A missing input, instruction or piece of evidence is not a question when it is resolvable: investigate, read the owner, or report the exact missing item with bounded options and a recommended default. A delegated worker that cannot proceed reports the gap to the coordinator rather than guessing, assuming, silently continuing on an unverified premise, or stalling, and never invokes the user-facing question tool itself. A delegated worker that is not blocked but has identified a decision reserved to the user, or an unresolved requirement or observable behavior, reports it rather than resolving it.

### Bounded-query discipline (SELECT-in-WHERE)

- Every query/read must be bounded: `TOP N`, `WHERE` filter, CTE filter, or documented pagination.
- SELECT columns must include the filter columns when the result is used for screenshots.
- Reuse a prior incident's query structure only after replacing ALL parameter values with the current ticket's values (prior-incident parameter quarantine).
- Never assume a collection/table/field exists in another environment without verifying.
- **Inventory preflight:** before requesting a lifecycle Git-inventory read (e.g. status, stash, or ref listings, or ancestry checks) from Herald 📯 (Release Manager), check the exact invocation against the effective available permission rules; never execute a known-disallowed variant, and never weaken or renegotiate permissions to accommodate one. Matching follows the effective permission rules' own matching precedence; never infer precedence from rule specificity alone.

### Instrument discipline

- Recursive file-pattern search silently skips dot-directories (e.g. `.opencode/`): a bare `**/*.md` omits them entirely, and a dot-prefixed pattern (`.opencode/**/*.md`) returns nothing at all. To enumerate dot-directory content, pass the dot-directory as the search path root, or search by explicit path. An empty or short pattern result over an area that should contain dot-directory files is an instrument artifact, not evidence of absence.

### Applicable analysis tools (HARD RULE)

- Use the project's configured cache-retrieval, structural-search and source-pattern analysis tools when they answer an applicable question within the assigned role and scope. Do not substitute connectivity probes or ceremonial calls for analysis. Unrelated Markdown-only work needs no code scan. State justified non-use, unavailability or an unresolved permission boundary briefly in the existing handoff; create no second tracker.
- Before use, inspect the actual exposed operation and its input contract, effective permissions and role restrictions. Configuration alone does not prove effective per-role exposure. Approved read-only MCP analysis is not shell, interpreter, network, test-runner, installation or mutation authority; it cannot bypass any execution ban, data-access restriction or owner gate. Report missing exposure or authority rather than inventing a grant or changing permissions.
- Cache retrieval is project-scoped and subordinate to current repository sources and the saved-research workflow. Validate relevant cached claims against their authoritative sources; a cache miss is not evidence of absence. Durable workflow knowledge belongs at its repository owner, never only in memory. Cache writes require separate authorization and existing memory-store discipline. ODD execution and resumption never depend on cache availability.
- Use structural search for syntax-dependent questions such as call shapes, imports or declarations; use ordinary text search for literal prose and simple names. Bound the searched root, language, pattern and returned matches to the question. Read surrounding source and required dependencies before conclusions; matches alone establish neither architecture nor test conformance. Structural analysis is read-only: no rewrite or autofix.
- Use source-pattern analysis when an explicit rule can test a relevant source-risk or correctness question within the existing audit scope. Supply locally scoped rules and targets, preserve configured privacy/telemetry controls and use no autofix. Do not broaden to remote services, auto-selected rules or supply-chain scans on the strength of tool availability. Pattern findings supplement, never replace, dependency/advisory evidence, full required reads or an independent review.
- Keep bounded evidence in the existing report: actual executor and operation, purpose, exact query/pattern/rule or a stable cited artifact, target paths and content/revision identity, result and truncation/skips/errors, limitations and their effect on the conclusion. For supplied-content analysis, identify the exact source and any excerpts/transforms; a path label is not proof the tool read that file. Zero matches means only no matches under the stated inputs, not security-clean, CVE-clean or runtime adoption. Reuse current attributable evidence where sufficient; failures and unsupported operations are limitations, not successful checks.

### Screenshot-ready output

- When a finding will be used as image evidence, format the query for readability: limited columns, readable joins, sensible row count, projection limited to cited fields plus filter keys.
- Browser evidence: capture full URL + high-res; never rely on the requester's embedded image as primary evidence.

### User-Authority-Only rule

Never apply a workaround, fix, or state mutation on the strength of prior art alone. Discovery → present evidence + recommended action. User approves → the work is executed.

A decision the user's own authority owns — scope, the accepted meaning of a requirement, an accepted risk, a roster change, a release boundary — is the user's to make, and a coordinator that reaches it before the user answers has taken a decision that was not its own. Present such a decision with the evidence, the bounded options and a recommended default before dependent work proceeds, and record the answer where the change record keeps it. A decision the repository already determines is not the user's and is not escalated; resolve it from the governing rules and continue.

### Artifact naming (HARD RULE)

Name a business artifact for the predicate or use case it expresses, not for the mechanism that implements it, the storage it sits in, or the component that consumes it. For example, `distribution-clearance.json` names the predicate "cleared for distribution," unlike `manifest.json` (the content that ships) or `registry.json` (the recording mechanism).

### Delivery readiness and findings

A delivery is **ready** when every applicable guarantee is established — by its required check having passed, or by an alternative procedure that establishes it when that check could not execute, under `.aicore/core/knowledge/agent-workflow.md` → `### Verification contingency` — and no `BLOCK` finding is open. It is **not ready** when any required check failed, any applicable guarantee remains unestablished, any required test-plan item is unchecked, or any `BLOCK` finding is open. Availability never decides readiness, and an instrument that did not execute is never reported as passed. An independent review is not a required check; a delivery without one can be ready, and the absence of a verdict never blocks.

- **Findings require disposition.** For every finding a review returns, record its ID, severity, status and evidence. Status vocabulary: `🔴 OPEN` · `✅ FIXED (round <N>)` · `⏸ DEFERRED → <destination>` · `✖ REJECTED (not a defect)`.
- **Fix first, then decide.** Applying `### Finding disposition` decides whether a finding is fixed now or stops the affected work. A deferral requires explicit user authority and a named durable destination (for example `.aicore/core/knowledge/debt.md`); it is never silently dropped and never becomes "ignore".
- **Account uniquely.** `Counts: fixed <F> · open <O> · deferred <D> · rejected <R> (of <M>)`, counting each ID once in its current status. A proposed deferral counts as open.
- **A review round is reported when it happens.** A user-requested review's result is reported once, in the combined summary below; no per-round ceremony is owed when no review ran.

### Message presentation

Three message types cover every user-facing status report:

1. **Progress** — communicate material results, evidence, changed scope, blockers and next action when useful. Routine step transitions need no report. Never omit a pending check or blocker from the relevant status.
2. **Findings or blocked** — something unresolved needs adjudication: the findings table below with one unique `Counts:` line. Blockers, checks, and decisions are reported outside the finding counts.
3. **Completion** — `ALL FINISHED` with delivered scope, verification, deferred items, and next options when the authorized scope is exhausted, or the ready message below when no scope remains open. `ALL FINISHED` is reserved for work whose governing record is closed: when a mandatory closure action is still outstanding, the report names that action and does not claim the work as fully closed.

**Round summary** — one combined message when a review ran or findings exist: first line + the findings table + `Counts:` line + readiness verdict + PR state + concrete next action + `Needs your decision: none | <items>`. Render tables directly, never inside code fences.

- **First line:** `Unresolved findings: <U> of <M> — open <O>, deferred <D>; <readiness state>` — a reader who reads only this line knows whether anything is unresolved or blocking, including failed, pending or unavailable checks even when `U` is zero.
- **Findings table columns, exactly:** `ID | Finding | Severity | Status | Evidence | Owner / next action | Needs your decision?`.
- **Evidence:** cite concrete head-bound evidence. `FIXED` identifies the remediation; `DEFERRED` identifies its durable destination and the user authority; `REJECTED` preserves the refutation evidence and carries the literal command output that settles it, so the user can audit the judgement.

**Ready message** — only when every applicable guarantee is established, zero findings are open, and the only outstanding decision is delivery:

- `Review: <PASS> — 0 open findings` when a review ran, or `Review: none requested — verification is automated plus self-review`
- `Required checks: all verified — naming any guarantee an alternative procedure established`
- `Blockers: none`
- `Needs your decision: <merge / publish / stop>`

Do not show an empty findings table. If findings existed, an optional `Fixed: <N> · Open: 0` count may accompany the ready message; verified fixed and rejected history stays in the durable delivery record.

**Decision consultation.** A significant technical decision that reaches the user carries one compact block; it creates no new message type, no new tracker, and no new gate. The block names, in this order, what was decided, why, the alternatives considered and why they lost, the cited evidence, the remaining risk, and whether the user must decide: `Decision` · `Why` · `Alternatives considered` · `Evidence` · `Residual risk` · `Your decision needed`. The final field states the gate outcome and reads `no — proceeding` or `yes — affected work stopped pending your answer`. The block rides inside the Progress format only when the outcome is `no — proceeding`; when the outcome is `yes` it accompanies the authorization request, which is a blocking interaction rather than a status report.

**Distinct concepts.** A **finding** is a rule-grounded defect or gap needing disposition. **Severity** is text (`BLOCK`/`ADVISORY`) attached to a finding. A **blocker** is an unmet prerequisite preventing the affected operation. Name its resolution owner and next action: agent-resolvable blockers are resolved within existing authority, not automatically escalated to the user; user-only blockers name the exact required user action. A **check** is verification evidence that is passed, failed, or unavailable; unavailable means it did not execute, so it establishes nothing by itself and stays distinct from a check not yet attempted. A **decision** is a user-only choice. Findings, checks, and decisions are separate: zero findings never means ready while a required check is pending or a decision is outstanding. A missing independent reviewer is none of these.

**Delivery stage.** A status report states which stage the work actually reached; the stages themselves and their order are owned by `.agents/skills/odd-workflow/SKILL.md` `### Completion stages`. Planning, analysis, a plan or a stated intent is not a stage, and a report that cannot name the stage it reached names the stage it did not reach and why.

**State emojis.** Emojis mark state, never severity, and never replace required text.

| Emoji | State                    |
| ----- | ------------------------ |
| ✅    | COMPLETE / FIXED / PASS  |
| 🟡    | IN PROGRESS / PENDING    |
| 🚧    | BLOCKED                  |
| ⏭️    | NOT APPLICABLE / SKIPPED |
| 🔴    | OPEN                     |
| ⏸     | DEFERRED                 |
| ✖     | REJECTED                 |
| ❌    | FAIL / ERROR             |
| ⚠️    | ADVISORY                 |
| ❓    | DECISION REQUIRED        |

- Never show an empty findings table; state the absence of findings in prose.
- Unresolved or pending checks never become a clean readiness claim.

**Illustrative example only — invented fixture identities/results below demonstrate format, not actual execution, published content, or feature status.**

**Progress.** `example-feature · T4 — Step 6 Implement task by task — 🟡 IN PROGRESS — implementation slice delivered; the CLI suite passes; one required check pending. Evidence: example feature Log. Next: run the end-to-end suite, then update the record. No user action needed. Continuing.`
<!-- core:end -->

<!-- project:begin -->
## Project extensions

### Message presentation — System 1 footer

When this turn's assembled context contains a `=== SYSTEM 1 | EXECUTION DIRECTIVES ===` block obtained from the `system-one` MCP server's `evaluate_odd_evidence` tool, every user-facing reply **ends with** exactly one `S1 applied` / `S1 overridden` line after the last required field of the Progress, Findings or blocked, or Completion format in `### Message presentation` (including the ready message and ordinary answers). That line does not replace those formats and must not be dropped because a Completion or Progress body is long.

The line describes how applicable findings were actually handled. An override is only a genuine contradiction, not an ordinary authorized action. Never claim applied if the effect cannot be established. Never emit the line when that block is absent. It is a diagnostic clue, not proof of compliance. The apply duty lives in `AGENTS.md` `### System 1 execution contract`; this heading only stops presentation formats from suppressing the footer.
<!-- project:end -->
