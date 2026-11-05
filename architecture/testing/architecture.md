# Testing architecture

## Purpose

This is the language-agnostic contract for test design and test-architecture review. It defines the test levels, boundaries, organization, and evidence rules that every stack guide must implement.

Authority is split deliberately:

- `architecture/implementation/architecture.md` owns the layer and dependency contract.
- This document owns the test-level, boundary, and parity contract.
- `architecture/testing/stacks/<stack>.md` owns concrete syntax, file paths, tools, and examples for one stack.
- `architecture/README.md` → `## Content model` defines which layer owns a rule statement and the identifier scheme.

**T1** — A stack guide applies this contract. It does not redefine the levels or weaken a boundary.

## Test levels

### Unit

**T2** — Exercise the smallest unit with its collaborators replaced by test doubles. For an application operation, that is the operation's `execute()` with its ports doubled. For a UI unit, that is the smallest testable component with its service or data boundary doubled.

**T3** — Assert observable values and behavior. A business failure is a returned domain value, never a thrown exception.

### Integration

**T4** — Exercise one adapter across its boundary: use the real dependency when it can be isolated, otherwise stub the boundary at its transport. Assert the mapping pipeline from outside data to domain values. An integration test does not become a unit test because the dependency is in memory, and it does not become an end-to-end test because it crosses one real boundary.

### End to end

**T5** — Exercise the assembled entry point with its real composition and adapters. Assert the observable result at that entry point, not internal implementation details.

## Boundaries and failures

- **T6** — A returned business failure is distinct from a boundary or programming exception. A boundary or programming exception must not be modeled or returned as a domain error.
- **T7** — A boundary test may verify that an exception propagates. A presentation binding may route either kind to an error state without changing its classification.
- **T8** — Test the boundary that owns the behavior. Do not use a higher-level test to compensate for an untested lower-level boundary.
- **T9** — A passing test execution, a token or keyword presence check, or a coverage number never establishes test-architecture conformance.

## Test organization

- **T10** — Test file organization mirrors the layers: unit tests sit with the application operation or domain responsibility, UI unit tests sit with the component they exercise, integration tests sit with the infrastructure adapter, and end-to-end tests sit in the project's end-to-end location.
- **T11** — One behavioral concern per test module, and one per class or describe-group within it. Behavior, not file size, sets the split boundary.
- **T12** — There is no line cap. A cohesive single-behavior module may stay whole; a module or class that accumulates distinct behaviors must be split by behavior.
- **T13** — Each test level keeps its stack guide's naming and discovery convention.
- **T14** — Missing scoped evidence for a file covered by a stack guide is a `[FAIL]`; `[UNCERTAIN]` is reserved for a file with no applicable guide or a file outside the declared scope.

## Test data and doubles

- **T15** — Test data comes from a factory or shared test-data helper, never inline literals.
- **T16** — Use one mocking library across the whole suite. The stack guide names it; do not mix libraries for the same job.
- **T17** — Do not mock the unit under test. Replace collaborators at the boundary named by the stack guide.
- **T18** — Keep tests hermetic: a test must not depend on another test's residue, a developer's machine state, or an uncontrolled external service.

## Execution and evidence

**T19** — The project owns its reviewed test commands and its test-runner configuration. This contract and its stack guides do not grant execution authority, install dependencies, or select a destination's runner.

**T20** — A destination adds its selected stack guide or local tool binding in its own project-owned configuration; it must not weaken this contract. A destination-specific runner or framework binding does not become a universal rule.

**T21** — A test-architecture verdict is separate from a test-execution result. A passing execution does not establish architecture conformance; a verdict is never inferred from an execution result alone.

## Stack-guide selection

1. **T22** — Read this contract.
2. **T23** — Identify the code's stack and application shape.
3. **T24** — Read the applicable guide in `architecture/testing/stacks/`.
4. **T25** — If no applicable guide exists, emit `[UNCERTAIN]` and report the missing guide. Do not infer a runner, a rule, or a file convention from another language.

**T26** — A guide is `proposed` until it has passed review, `reference` while it is the reviewed implementation, and `superseded` when replaced. A `proposed` guide cannot support a verdict.

## Stack guides

| Stack | Guide | Status | Scope | Parity evidence |
|---|---|---|---|---|
| TypeScript | `stacks/typescript.md` | reference | TypeScript/TSX backend and frontend reference architecture | Reviewed 2026-10-25; entity-construction clause 2026-10-30; documentation-only change reviewed 2026-10-30 (owner field retired; destination guidance relocated); 10/10 sections; cross-stack table complete. Reviewed 2026-11-01: `T`-rule citations added throughout the body and the parity table, the parity table reworked to cite rule IDs per row, and the hermeticity (`T18`) and missing-evidence (`T14`) obligations mapped by ID instead of restated. Reviewed 2026-11-05: the stale `domain/entities/` factory-import spelling in `Test data and doubles` was retired in favour of the concept's own domain module (`<concept>.entity.ts`), with no `T` rule added, removed or moved. |
| Python | `stacks/python.md` | reference | Python application, script, and CLI reference architecture | Reviewed 2026-10-25; entity-construction clause 2026-10-30; documentation-only change reviewed 2026-10-30 (owner field retired; destination guidance relocated; reference case reworded source-neutrally); 10/10 sections; cross-stack table complete. Reviewed 2026-11-01: `T`-rule citations added throughout the body and the parity table, the parity table reworked to cite rule IDs per row, and the former restatement of the hermeticity rule rewritten as a Python-specific mapping (`T18`). |

**T27** — The index is part of the parity contract. Adding or changing a guide requires updating this table and the parity evidence.

## Cross-stack parity

**T28** — Every stack guide uses `stacks/_template.md` and keeps the same heading order and rule granularity:

1. Applicability and ownership
2. Test pyramid mapping
3. File organization
4. Unit tests
5. Integration tests
6. End-to-end tests
7. Test data and doubles
8. Execution and evidence
9. Cross-stack parity
10. Open decisions

**T29** — A section is complete or explicitly marked `N/A` with a language or runtime reason. A missing section, a thinner rule, or an inherited generic-only section is a defect. Differences are allowed only for language semantics and must be declared in the guide's parity table.

## Adding a stack guide

1. **T30** — Create an authorized ODD feature; do not add a guide as incidental work.
2. **T31** — Copy `architecture/testing/stacks/_template.md`.
3. **T32** — Research the stack's official documentation and inspect representative repository tests.
4. **T33** — Map every template section to the agnostic contract; mark every non-applicable section `N/A` with a reason.
5. **T34** — Label the guide `proposed` until the applicable architecture owner, the test architect, and the owner of the governing ODD feature review it.
6. **T35** — Record the parity review and evidence before changing the status to `reference`.

**T36** — Research is not approval. An unverified guide must not be used to issue a verdict.

## References

- `architecture/implementation/architecture.md` — clean architecture and failure classification.
- `architecture/README.md` → `## Content model` — which layer owns a rule statement, and the identifier scheme.
- `architecture/testing/stacks/_template.md` — the only stack-guide template.
