# <Stack> testing guide

> **Status:** proposed
> **Stack:** <language, framework, and application shape>
> **Reviewed:** pending
> **Contract:** `architecture/testing/architecture.md`

> **Template use:** Copy this file to `architecture/testing/stacks/<stack>.md` and fill every section. Keep the heading order. A section is complete or explicitly `N/A` with a language or runtime reason. Do not remove a section because the stack appears simpler. Delete these template-use instructions and the placeholders after review.

## Applicability and ownership

State the exact language, application shapes, and file types this guide covers. Name the project-owned tool selection boundary: the guide may recommend a reference runner, but the destination owns its reviewed runner and configuration. Name what this guide does not cover.

A destination may add its selected runner, framework adapter, or local tool binding. It must not weaken the shared contract.

## Test pyramid mapping

| Level | Target | Collaborators and doubles | Observable assertion |
|---|---|---|---|
| Unit | <smallest unit> | <what is doubled> | <what is asserted> |
| Integration | <one adapter or boundary> | <real dependency or transport stub> | <mapping assertion> |
| End to end | <assembled entry point> | <real composition and adapters> | <observable result> |

Explain any stack-specific meaning of a level. Do not rename a level or move a boundary.

## File organization

- Unit:
- Integration:
- End to end:
- Discovery and naming:
- One behavior per module or class:

Name exact paths or path patterns. State the project-wide discovery rule and whether a per-directory allowlist exists.

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

Complete this table for every contract section:

| Contract section | Coverage | Difference or N/A reason |
|---|---|---|
| Applicability and ownership | <covered / N/A> | <reason> |
| Test pyramid mapping | <covered / N/A> | <reason> |
| File organization | <covered / N/A> | <reason> |
| Unit tests | <covered / N/A> | <reason> |
| Integration tests | <covered / N/A> | <reason> |
| End-to-end tests | <covered / N/A> | <reason> |
| Test data and doubles | <covered / N/A> | <reason> |
| Execution and evidence | <covered / N/A> | <reason> |
| Cross-stack parity | <covered / N/A> | <reason> |
| Open decisions | <covered / N/A> | <reason> |

A difference is allowed only for language or runtime semantics. A thinner section is not a difference.

## Open decisions

Record decisions that are genuinely unresolved, with the evidence needed to resolve them and the owner. Do not use this section to hide a missing rule. If there are none, write `None.`
