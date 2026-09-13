# Query Verification Design - Living Refinement

## Status and purpose

**Status: implemented — incident-only pilot (v1); broader design deferred.**

The implemented pilot is the `query-verification` OpenCode skill at `.opencode/skills/query-verification/`. It validates one incident-owned, sidecar-defined SQL verifier against an invocation-time query root and evaluates trusted normalized adapter output offline, producing a redacted, digest-bound case-evidence record with exactly one verdict: `verified`, `not_verified`, or `inconclusive`. Its normative contract is `references/protocol-v1.md` in that skill.

This living design records the approach to query verification across destination projects. The implemented pilot does not change the registers' paths, identifiers, schema, or runtime behavior, and it imposes no executable behavior on agents. AICore validates and evaluates local artifacts only; a destination-owned trusted adapter binds parameters and executes the query. AICore never connects to a database, executes SQL, reads credentials, invokes an adapter command, or holds persistent query-root configuration. Ticket-enabled destinations receive the skill and this design document as `only if ticket marker` items in the `migrate-core-to-project` manifest; the pilot adds no root dependency, lockfile, runtime configuration, credential, or destination query-library change.

**Deferred (not implemented):**

- Dev-team verifiers, Dev workflow integration, and the Dev problem-record lifecycle.
- External adapter execution, adapter commands, credentials, and connection strings.
- Centralized verifier discovery or a central index.
- Non-SQL sources, multiple result sets, and a general assertion language.
- Persistent query-root configuration.

The goal is to let an incident case safely reuse a diagnostic query without placing large, project-specific SQL in the symptom or problem registers.

## Core model

The symptom and problem registers, diagnostic-query library, verifier definitions, verifiers, and case evidence have different responsibilities:

| Surface | Responsibility |
|---|---|
| `knowledge/symptoms.md` | Durable symptom classes and canonical diagnostic routing. |
| `knowledge/problems.md` | Evidence-backed recurring problem patterns, their root causes, fixes, and team ownership. |
| Destination diagnostic-query library | Large reusable diagnostic queries, such as SQL, document, or script queries. |
| Verifier definition | Machine-readable YAML metadata that links a diagnostic query to query verification. |
| Verifier | A diagnostic query together with its verifier definition. |
| Case evidence | Retained ticket/task proof from a verification execution: the verifier ID, the verdict, the bound digests, and the redacted evidence values. The implemented pilot does not retain raw query output. |

A verifier can establish that a symptom is present for a particular case. It does not establish a root cause unless its declared result contract directly tests that cause.

## Portability contract

AICore must define the protocol, not prescribe a destination's query-library layout.

Each destination project will declare one base folder containing reusable diagnostic queries. Valid examples include `sql/queries/`, `support/diagnostics/`, and `operational-data/checks/`. Within that base folder, the destination may organize files by system, module, country, product, or any other local convention.

Every diagnostic query intended to verify a symptom must have a YAML verifier definition. The implemented incident pilot requires a sidecar file beside the diagnostic query:

```text
<declared-query-root>/
  <destination-defined-subfolders>/
    Festival_DiagnosticoMonto.sql
    Festival_DiagnosticoMonto.verifier.yaml
```

The sidecar layout is required for the implemented incident pilot. A centralized YAML index remains a deferred consideration if it can preserve the same verifier-definition contract and reliably map each definition to one diagnostic query.

Not every symptom requires query verification. A symptom may require logs, browser evidence, code inspection, or another diagnostic method. A verifier definition is required only for reusable query verification.

## Implemented incident pilot contract (v1)

The implemented pilot is closed, incident-only, SQL-source-only, and sidecar-only. Its normative contract lives in `.opencode/skills/query-verification/references/protocol-v1.md`; the static shapes are `verifier-sidecar-v1.yaml`, `adapter-output-v1.json`, and `case-evidence-v1.json` in the same folder.

| Element | Implemented v1 rule |
|---|---|
| Team | `team: incident` only. |
| Source | One normalized relative POSIX `.sql` path beneath the invocation-time `--query-root`. |
| Sidecar | One adjacent `.verifier.yaml` beside the source. |
| Safety | `safety.operation: read_only`; exactly one bounded result set. |
| Bindings | Declared named `:name` parameters only; no interpolation or concatenation. |
| Result set | Exactly one result set named `verification` with exactly one `verification_verdict` column. |
| Evidence | Configured `evidence_columns` retained, configured `redact_columns` replaced by `[REDACTED]`, verdict bound to verifier/source/definition digests. |
| Verdicts | Exactly `verified`, `not_verified`, or `inconclusive`. |
| Execution | The destination-owned adapter binds and executes; AICore validates and evaluates local artifacts only. |

## Broader verifier-definition contract (deferred)

This broader shape remains a design proposal and is not implemented. Each verifier definition may eventually define at least:

| Field | Purpose |
|---|---|
| `id` | Stable, destination-unique verifier identifier. |
| `team` | Owning team for the verifier. The current core uses `incident` and `dev`. |
| `source` | Diagnostic-query path relative to the destination's declared query root. |
| `symptoms` | One or more destination symptom IDs that the verifier can verify. |
| `purpose` | Short description of what the verifier proves or rules out. |
| `parameters` | Declared typed inputs, including source, requiredness, and redaction needs. |
| `assertions` | Result-set/field conditions that produce a verification verdict: verified, not-verified, or inconclusive. |
| `safety` | Operation type, required filters, and any environment preconditions. |
| `result_sets` | Named query-output result-set descriptions when a diagnostic query emits more than one output. |

Illustrative shape:

```yaml
id: incident.sb.festival-amount.v1
team: incident
source: SB/Festival_DiagnosticoMonto.sql
symptoms:
  - S-SB-FESTIVAL-AMOUNT-DIFFERENCE
purpose: Reconcile an order's persisted and reconstructed Festival amount.
parameters:
  - name: campaign_id
    type: integer
    required: true
  - name: consultant_identifier
    type: string
    required: true
    redaction: internal_identifier
  - name: country
    type: country
    required: true
    usage: connection_selection
assertions:
  - id: context-resolves
    pass_when: exactly_one_order_is_found
    on_failure: inconclusive
  - id: amount-differs
    observed_from: RS5.MontoFestivalCalculado vs RS2.MontoFestival
    pass_when: absolute_difference > 0.01
    on_pass: symptom_verified
safety:
  operation: read_only
  required_filters:
    - campaign_id
    - consultant_identifier
```

The sample is a design illustration of the deferred broader shape. The implemented incident pilot does not use `assertions`, `result_sets`, or `required_filters`; its closed v1 contract is the section above. Field names, comparison syntax, and any eventual broader schema remain to be defined before implementation.

## Query-verification flow

In the implemented incident pilot, the destination-owned adapter performs the execution step; the core skill performs only the local validate and evaluate steps. The full flow below remains the design target; steps marked **(deferred)** are not implemented by the pilot.

```text
New incident or development case
        |
        v
Classify the observed issue to a symptom ID
        |
        v
Locate a verifier (its verifier definition and diagnostic query) for the current team, symptom, and system/module
        |
        v
Validate and supply declared case-specific parameters
        |
        v
Run the verifier's bounded read-only diagnostic query as a verification execution (destination-owned adapter)
        |
        v
Evaluate the normalized output against the declared result contract to produce a verification verdict (core skill, offline)
        |
        +-- verified ------> link to an existing problem pattern when applicable
        +-- not_verified --> investigate a different cause
        +-- inconclusive --> collect the missing evidence; do not infer a pass
```

When the same symptom appears in a future case, an agent performs a verification execution of the same verifier with that case's values. A matching result contract produces a verification verdict that verifies a recurrence of the symptom condition; it does not automatically prove that the case shares a prior problem record's root cause. The core skill never runs the query itself.

## Current two-team workflow map

This is a readable map of the current AICore definitions. It does not introduce new behavior. Items marked **Gap** are not yet operationally defined.

### Incident team

| Step | Current flow | Outcome |
|---|---|---|
| 1 | New incident ticket | Ticket is read through the destination ticket tool. |
| 2 | Classify the observed issue | Match it to a symptom class in `knowledge/symptoms.md` (Required signals present, no Exclusion). |
| 3 | Identify register-first | Filter `knowledge/problems.md` to `Team: incident` rows by symptom + system + module + lifecycle, and evaluate every discriminator and exclusion. The ticket archive, patterns, KBA/RCA, and knowledge search are evidence-only, consulted after `no_match` — they never issue a verdict. |
| 4A | Exact match | Cite the matched `active` `P-NNN` and the known solution; request approval before applying it. |
| 4B | Structural or no match | Create the working analysis (`analysis/`) and have Investigator 🔍 (Incident Investigator) validate the inherited hypothesis (`structural`) or fresh hypotheses (`no_match`). |
| 5 | Confirmed incident evidence | Ledger 📒 (Record Keeper) records the ticket evidence; Quill 🪶 (Note Drafter) prepares the response. |
| 6 | New recurring problem | **Gap:** Scribe ✍️ (Docs & Problems Manager) owns the register by rule, but the complete Markdown `P-NNN` create/update and deduplication handoff is not defined. |
| 7 | Confirmed product defect | **Gap:** no defined handoff starts the Dev plan and implementation flow. |

### Development team

| Step | Current flow | Outcome |
|---|---|---|
| 1 | Dev issue found | The issue may come from an audit, dependency/configuration failure, build/test failure, or application defect. |
| 2 | Classify an unexpected tool error | Shared rules direct the agent to match a symptom class and search `Team: dev` records. |
| 3 | Begin programming work | `plan-enforce` creates a plan before Forge 🔨 (Implementer) writes code. |
| 4 | Implement and verify | Forge 🔨 (Implementer) implements; the applicable architect/test gates review the change. |
| 5 | Release flow | Herald 📯 (Release Manager) handles authorized Git work; Inquisitor 🔎 (PR Reviewer) reviews the PR boundary. |
| 6 | Search or reuse known Dev problems | **Gap:** `plan-enforce` and Forge 🔨 (Implementer) do not currently enforce the `Team: dev` symptom/problem lookup. |
| 7 | File a new Dev problem | **Gap:** shared rules require filing a novel `P-NNN`, but no Dev-specific owner, handoff, or enrichment lifecycle defines how a `Team: dev` record is created and maintained. |

### Intended shared query-verification path

| Start | Find | Verify | Result |
|---|---|---|---|
| Incident ticket (implemented pilot) | Symptom ID, team, system/module | Verifier (its verifier definition and destination-owned diagnostic query) with current-case parameters bound by the destination adapter | Verification verdict: `verified`, `not_verified`, or `inconclusive` |
| Dev issue (deferred) | Symptom ID, team, system/module | Verifier with current-case parameters | Verification verdict: `verified`, `not_verified`, or `inconclusive` |

When the verification verdict is `verified`, the agent may link to an existing problem record and recommend its recorded fix. It must not apply a fix or claim root-cause equivalence without the required evidence and approval. The implemented pilot covers the incident row only; the Dev row is deferred.

## Register interaction

This query-verification design augments rather than replaces the existing registers:

- A symptom entry may reference one or more verifier IDs as part of its canonical diagnostic routing.
- A problem record may cite a verifier ID only after case evidence confirms a recurring root-cause pattern.
- A ticket/task retains the verifier evidence record from its verification execution: the verifier ID, the verdict, the source and definition digests, and the redacted evidence values. Raw query output, rendered SQL, parameter values, and credentials are not retained by the pilot.
- A new problem record is not created merely because a verifier exists or a symptom is observed.
- Repeated cases that satisfy the same root-cause evidence enrich or link to the existing problem record instead of creating duplicates.

## Verification and evidence constraints

The implemented incident pilot retains the existing shared query safeguards in `knowledge/agents.md`:

- Queries are bounded and include relevant filter fields in their evidence projection.
- The target schema and environment are verified before use by the destination adapter; the core skill performs lexical safety checks only.
- Values from a prior ticket are never copied into a new case; all parameters come from the current case and are bound by the destination adapter.
- A verifier definition must declare whether its diagnostic query is read-only. Destructive or mutating scripts are never verifiers; the pilot rejects any `safety.operation` other than `read_only`.
- Parameter rendering is typed and controlled; unbounded text interpolation and dynamic SQL concatenation are not accepted, and the core never renders a parameter value.
- A reusable diagnostic query does not retain customer-specific query output. The pilot retains only the redacted, digest-bound evidence record; raw output belongs to destination policy.
- The verdict is exactly `verified`, `not_verified`, or `inconclusive`; missing, zero, or multiple context rows and any malformed or mismatched input produce `inconclusive`, never a silent pass.

## Refinement backlog

Status of each open decision after the incident-only pilot. Items marked **Addressed (v1)** are implemented for the incident pilot; the remaining items stay open for the deferred broader design.

1. **Addressed (v1):** the query root is supplied per validation invocation with `--query-root`; no persistent configuration surface exists.
2. **Addressed (v1):** verifier definitions are sidecar-only. Centralized indexing is deferred.
3. **Addressed (v1):** the closed sidecar schema, source-safety checks, and result contract are defined in `.opencode/skills/query-verification/references/protocol-v1.md`. A general assertion language is deferred.
4. Define how destination business symptom IDs extend the generic AICore symptom classes.
5. Define a safe, language-aware parameter-rendering mechanism for SQL and non-SQL diagnostic queries. The pilot requires adapter-side named binding and performs no rendering.
6. **Addressed (v1):** the case-evidence format, source/definition/evidence digests, and redaction requirements are defined in the protocol references.
7. Define admission, review, and retirement rules for verifiers.

## Implementation entry criteria

The incident-only pilot is implemented and meets the criteria below. The deferred broader design is ready for implementation planning only when the remaining criteria are agreed for the expanded scope.

- A destination can declare its diagnostic-query root without modifying AICore source for its local layout. **Met (v1):** `--query-root` is supplied per validation invocation.
- Every verifier has a stable verifier definition and a diagnostic-query source path. **Met (v1):** adjacent sidecar plus root-relative `.sql` source.
- The distinction between symptom verification and root-cause confirmation is explicit. **Met (v1):** a `verified` verdict is symptom evidence only.
- Query safety, parameter handling, and evidence retention have enforceable rules. **Met (v1)** for incident SQL verifiers.
- The incident and development team ownership/handoff model is defined. **Partially met:** incident is implemented; Dev integration remains deferred.

## Advisory dispositions and governance (2026-09-10)

The pilot's post-implementation advisories are closed or recorded as verified no-action items. Each disposition is evidence-backed by an executable check or a versioned governance surface; no dependency, lockfile, register, protocol, or ticket behavior changed.

| Advisory | Disposition | Evidence |
|---|---|---|
| The shipped valid adapter fixture was not independently usable | **Resolved.** The fixture's `source_digest` equals the SHA-256 of the unchanged `incident-check.sql` bytes (`sha256:1e098701a3d6952bf6bae5a05d899527051e40f384e344e607981f4ffb7a218a`), so the fixture trio evaluates directly to `verified`. | The query-verification suite exits 0 with 73 tests; a drift assertion fails if the declared fixture digest diverges from the recomputed source digest. |
| Vault 🔐 (Catalog Steward) extraction rule QC-27 required a literal `.md` path | **Resolved.** QC-27 accepts a named, non-executable reference artifact under `references/` in Markdown, YAML, JSON, or another named machine-readable format when the skill explicitly references it. Executable code stays in `scripts/`; opaque or unnamed artifacts do not satisfy extraction. | Vault 🔐 (Catalog Steward) runtime spec `1.1.0` (minor bump for the new enforceable capability). |
| README register labels and skill count were stale | **Resolved.** README labels now match the register H1s — `Diagnostic Symptom Catalog` and `Known Problem Pattern Register` — and a note records that the migration manifest intentionally excludes `migrate-core-to-project` itself, so its skill rows number 9 against the 10-skill inventory. | `README.md`; migration-manifest selection behavior is unchanged. |
| A plan phase could name a verification command without a traceable executor | **Resolved.** `plan-enforce` `1.11.1` requires one canonical `## Verify commands` table with exactly the `Executor` and `Command` columns and one declared executor per command. The static validator enforces declared traceability only; phase review audits executor authority. | `validate_plan.py` and its regression suite: 29 tests pass, including 8 executor-command table cases (7 rejection + 1 acceptance). |
| Python stdlib `unittest` test gating had no owner | **Resolved.** Bastion 🧱 (Backend & Scripts Architect) owns the gate: an exact plan-manifested stdlib `unittest` file requires the plan's declared runnable `python3` command plus Bastion 🧱 (Backend & Scripts Architect) [PASS]; Crucible 🔥 (Test Architect) is dispatched for the test-file edit and its actual rule-applicability verdict is recorded as-is, never relabeled. | Bastion 🧱 (Backend & Scripts Architect) runtime spec `1.1.0` (minor bump for the new enforceable capability); `pytest` is not required or added. |
| Crucible 🔥 (Test Architect) had no Python test-architecture branch | **Resolved — supersedes the row above.** Crucible 🔥 (Test Architect) carries an additive `## PYTHON STDLIB UNITTEST TESTS` branch that returns `[PASS]`/`[FAIL]` for exact active-plan Python stdlib `unittest` files; `[UNCERTAIN]` is not acceptable for that scope. `plan-enforce` `1.11.1` requires the declared literal `python3` command plus Bastion 🧱 (Backend & Scripts Architect) `[PASS]` and Crucible 🔥 (Test Architect) `[PASS]`/`[FAIL]`. | `.opencode/agents/crucible.md` `1.1.0`; `.opencode/agents/bastion.md` `1.2.0`; `.opencode/skills/plan-enforce/SKILL.md` `1.11.1`; Crucible 🔥 (Test Architect) returned `[PASS]` for all three existing Python stdlib `unittest` suites. |
| An archived advisory record claimed a mechanical-fix count | **No count retained.** No source artifact substantiates a mechanical-fix count, so this living design retains none and carries no count claim forward. | No substantiating source artifact exists. |
| Generated `__pycache__` bytecode on disk | **No action.** Covered by the root `.gitignore` `__pycache__/` entry and not a committed artifact. | Root `.gitignore`. |
| Register title edits | **No action here.** The `knowledge/symptoms.md` and `knowledge/problems.md` title changes belong to the completed `query-verification-naming-20260910` plan and are not modified by this advisory closure. | Register H1s are unchanged by this work. |

### Recorded audit verdicts

| Audit | Scope | Verdict |
|---|---|---|
| Vault 🔐 (Catalog Steward) | Both changed skills | ADVISORY — all gate items pass; findings corrected, no blocking defect |
| Sentinel 🛡️ (Quality Guardian) | Documentation, plan, story, and agent surfaces | ADVISORY (mechanical naming fixes applied; no blocking defect) |
| Bastion 🧱 (Backend & Scripts Architect) | Changed Python | PASS |
| Crucible 🔥 (Test Architect) | Changed Python test files | `[UNCERTAIN]` — TypeScript-specific rules inapplicable to stdlib `unittest`; recorded as-is, never relabeled PASS |

**Governance decision.** Python stdlib `unittest` test gating is owned by Bastion 🧱 (Backend & Scripts Architect), not deferred pending pytest. Crucible 🔥 (Test Architect)'s stack-specific applicability result is recorded without relabeling — a `[UNCERTAIN]` verdict is a reported governance fact, never converted to PASS.

**Superseding governance decision (2026-09-10).** Crucible 🔥 (Test Architect) now audits exact active-plan Python stdlib `unittest` files through its additive `## PYTHON STDLIB UNITTEST TESTS` branch and returns `[PASS]` or `[FAIL]`; `[UNCERTAIN]` is no longer acceptable for that scope, and missing scoped evidence is a `[FAIL]`. Bastion 🧱 (Backend & Scripts Architect) retains Python implementation and script architecture and defers Python test architecture to Crucible 🔥 (Test Architect). `plan-enforce` `1.11.1` requires the declared literal `python3` command plus both verdicts. Every existing TypeScript/JavaScript, Vitest, and Playwright rule remains unchanged and in force. Crucible 🔥 (Test Architect) returned `[PASS]` for all three existing Python stdlib `unittest` suites; that audit is retained as a report artifact and is not cited by path here. No mechanical-fix count is retained, because no source artifact substantiates one.

## Refinement history

| Date | Decision or question | Status |
|---|---|---|
| 2026-09-09 | Large reusable diagnostic queries stay in destination-owned diagnostic-query libraries rather than Markdown registers. | Proposed |
| 2026-09-09 | Query verification requires a YAML verifier definition that maps symptom(s), inputs, assertions, and safety constraints to a diagnostic query. | Proposed |
| 2026-09-09 | AICore should define a portable contract; destination projects choose their diagnostic-query-root path and internal organization. | Proposed |
| 2026-09-09 | Added a current two-team workflow map and recorded the missing Dev-specific register lifecycle and Support-to-Dev handoff. | Proposed |
| 2026-09-10 | Implemented the incident-only, sidecar-only SQL pilot: core validates and evaluates local artifacts; the destination adapter binds and executes; `--query-root` is invocation-time only. | Implemented (incident pilot) |
| 2026-09-10 | Deferred Dev integration, external adapter execution, centralized discovery, non-SQL sources, multiple result sets, and general assertions. | Deferred |
| 2026-09-10 | Integrated the optional incident investigate-step verifier-evidence route (one existing Query-budget slot) and published the pilot as a ticket-marker migration skill plus design document. | Implemented (incident pilot) |
| 2026-09-10 | Closed the fixture-validity, QC-27 static-reference, README label/count, executor-traceability, and Python stdlib-test-gate advisories; recorded `__pycache__` and register-title attribution as verified no-action items. | Resolved |
| 2026-09-10 | Crucible 🔥 (Test Architect) gained an additive Python stdlib `unittest` audit branch returning `[PASS]`/`[FAIL]` for exact active-plan Python test files; `plan-enforce` now requires both Bastion 🧱 (Backend & Scripts Architect) and Crucible 🔥 (Test Architect) verdicts. | Supersedes the earlier Bastion-only gate |
| 2026-09-10 | The living design record retains no mechanical-fix count; no source artifact substantiates one. | No count retained |
