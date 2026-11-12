# <Stack> testing guide

> **Status:** proposed
> **Stack:** <language, framework, and application shape>
> **Reviewed:** pending
> **Contract:** `architecture/testing/architecture.md`

> **Template use:** Copy this file to `architecture/testing/stacks/<stack>.md` and fill every section. Keep the heading order. A section is complete or explicitly `N/A` with a language, runtime, or scope reason stating why the obligation cannot be achieved by guide content. Do not remove a section because the stack appears simpler. Delete these template-use instructions and the placeholders after review.

## Applicability and ownership

State the exact language, application shapes, and file types this guide covers. Name the project-owned tool selection boundary: the guide may recommend a reference runner, but the destination owns its reviewed runner and configuration. Name what this guide does not cover.

A destination may add its selected runner, framework adapter, or local tool binding. It must not weaken the shared contract.

## Test pyramid mapping

| Level | Target | Collaborators and doubles | Observable assertion |
|---|---|---|---|
| Unit | <one application use-case class, one parser/loader whose responsibility is converting an external representation into domain data, or one component with its real hook> | <what is doubled> | <what is asserted> |
| Integration | <one adapter or boundary> | <real isolated dependency; transport stub only for a capability whose dependency cannot be isolated> | <mapping assertion> |
| End to end | <assembled entry point> | <real composition and adapters> | <observable result> |

Explain any stack-specific meaning of a level. Do not rename a level or move a boundary.

## File organization

- Test root and level directories:
- Unit:
- Integration:
- End to end:
- Discovery and naming:
- One behavior per module or class:

Name exact paths or path patterns. Every test lives under its test-owning unit's `tests/` directory — the repository root for repository-wide tests, or the package root for an independently deployable application — in its `unit/`, `integration/` and `e2e/` level directories; no test lives inside a production directory, and nested folders group tests by behavioural target rather than by production file. State the project-wide discovery rule and whether a per-directory allowlist exists.

## Unit tests

List the concrete rules for this stack:

- What is instantiated directly.
- Which collaborators are doubled.
- Which mocking facility is used, and which alternatives are prohibited.
- How returned business failures are asserted.
- Which higher-level tests are explicitly not substituted for a unit test.
- Any stack-specific file or assertion conventions.

Include one minimal example that demonstrates the boundary, not a full test suite.

## Integration tests

List the concrete rules:

- Which adapter or boundary is exercised.
- When a real dependency is used and when the transport is stubbed.
- Isolation and cleanup requirements.
- Mapping, defaults, null, and missing-value behavior.
- Which doubles are prohibited here.
- Any stack-specific fixture or database conventions.

Include one minimal example that demonstrates the boundary.

## End-to-end tests

List the concrete rules:

- Which assembled entry point is exercised.
- Which phases or environments are required.
- Which real adapters and composition are used.
- How failures and error output are asserted.
- Which unit or integration concerns are explicitly not duplicated here.

Include one minimal example that demonstrates the entry point.

## Test data and doubles

- Factory or shared test-data helper:
- Required factory methods:
- Entity construction through the entity factory/`create()`; direct field assignment to build an entity is prohibited:
- Data-generation policy:
- One mocking library or facility per collaborator boundary:
- Hermeticity rules:
- Prohibited inline literals or shared mutable state:

State how the guide avoids duplicating data construction across tests.

## Execution and evidence

- Reviewed runner ownership:
- Test discovery:
- Execution command ownership:
- Test-architecture verdict versus execution result:
- Required traceability from feature specs to tests:
- What counts as missing evidence:

Do not grant execution authority in this guide. Name the project configuration surface that owns the runner command.

## Cross-stack parity

Complete this table for every contract section. Every row cites the contract rule identifiers the guide achieves; a coverage claim without a cited identifier is a defect. Follow `architecture/README.md` → `## Content model`.

| Contract section | Cited rule IDs | Language-specific achievement or N/A reason |
|---|---|---|
| Applicability and ownership | <T-IDs> | <how this stack achieves them, or the N/A reason> |
| Test pyramid mapping | <T-IDs> | <how this stack achieves them, or the N/A reason> |
| File organization | <T-IDs> | <how this stack achieves them, or the N/A reason> |
| Unit tests | <T-IDs> | <how this stack achieves them, or the N/A reason> |
| Integration tests | <T-IDs> | <how this stack achieves them, or the N/A reason> |
| End-to-end tests | <T-IDs> | <how this stack achieves them, or the N/A reason> |
| Test data and doubles | <T-IDs> | <how this stack achieves them, or the N/A reason> |
| Execution and evidence | <T-IDs> | <how this stack achieves them, or the N/A reason> |
| Cross-stack parity | <T-IDs> | <how this stack achieves them, or the N/A reason> |
| Open decisions | <T-IDs> | <how this stack achieves them, or the N/A reason> |

A difference is allowed only for language semantics and must be declared in the parity table above. `N/A` is allowed for a language, runtime, or scope reason; a scope-based `N/A` states why the obligation cannot be achieved by guide content under this guide's scope. A thinner section is not a difference. State only how this stack achieves a cited rule; never restate the rule, here or in the body.

## Open decisions

Record decisions that are genuinely unresolved, with the evidence needed to resolve them and the owner. Do not use this section to hide a missing rule. If there are none, write `None.`
