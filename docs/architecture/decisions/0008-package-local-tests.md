# ADR 0008 — Package-local tests for independently deployable applications

- **Status:** Accepted
- **Date:** 2026-11-12
- **Accepted:** 2026-11-12 — user approved the narrowly scoped clarification and directed it be applied before finalizing U1; the testing-architecture owner reviewed the owner text and confirmed it enforces this decision, with all five propagation targets carrying the rule.

## Context

T10 in `architecture/testing/architecture.md` states that "Every project keeps one root-level `tests/` directory holding exactly three level directories". The TypeScript testing guide repeats that rule in two places. Taken literally, the rule permits exactly one test root per repository, so any independently deployable application package inside the repository must place its tests in the repository-level `tests/` directory.

That placement conflicts with a requirement recorded by the project owner: each CLI application must be self-contained and portable, so that copying its directory into another repository carries its source code, tests and package configuration together. Tests held only at the repository root do not travel with the package.

The conflict is narrow. T10's remaining obligations do not oppose package-local tests: a `tests/` directory that is a *sibling* of `src/` is not "beside an implementation file" and is not "under a source tree", and the three level directories, the no-colocation rule, the no-role-named-folder rule and the shared-support convention all carry over unchanged. Only the words "one root-level" and "the project's single root-level" block the placement.

Two existing packages already place tests inside a production tree — `.opencode/plugins/odd-adviser/` and `mcp-servers/system-one/` keep specs beside their source modules. The debt register records this as DEBT-046. Those placements violate more of T10 than a sibling `tests/` directory would, so this decision also supplies a coherent target for that recorded debt.

## Decision

T10 is clarified so that it counts test-owning units rather than repositories. Exactly three obligations are preserved without change: one `tests/` directory per test-owning unit, exactly the three level directories `tests/unit/`, `tests/integration/` and `tests/e2e/`, and no test file beside an implementation file or under a source tree.

The unit's root decides where that directory sits: the repository root for repository-wide tests, and the package root for an independently deployable application.

Ownership stays with the test-architecture owner. The rule is carried by the testing contract, and the TypeScript testing guide restates it in the two places that name the location; both must change together or the guide contradicts the contract.

Authorization boundary: this decision changes where a test-owning unit's `tests/` directory may live. It does not authorise a new test level, a fourth level directory, co-located specs, a new test framework, or any change to dependency direction, IO boundaries or path safety.

## Alternatives

1. **Keep T10 unchanged and accept a recorded violation for the CLI package.** Rejected: the project owner requires portability, and a known violation on every new application package accumulates debt rather than resolving it.
2. **Keep application tests at the repository root and treat them as repository-wide.** Rejected: the tests would not travel with the package, defeating the stated objective, and copying the package would lose its verification.
3. **Co-locate specs beside source modules, as the two existing tooling packages do.** Rejected: this conflicts with T10's no-colocation clause, which this decision deliberately preserves, and it is the shape already recorded as DEBT-046.
4. **Defer the clarification until a second application package exists.** Rejected: the repository already contains one application package requiring the clarification, and deferral would force the same relocation twice.

## Consequences

Benefits: an application package can carry its own tests and configuration when copied, each package runs its tests independently, and the three-level rule is preserved rather than relaxed.

Costs: `architecture/` is a cleared raw directory root, so the clarified wording ships byte-for-byte to every destination project on its next synchronization. The contract and the guide must be edited in one work unit. A destination that reads T10 literally is unaffected in practice, because the clarified text still requires one `tests/` directory per unit and the same three levels.

Migration boundary: this record changes documentation only. No existing repository-wide tests move, no package is created, and no implementation is authorised by it. Applying it to a package is a separate authorized change.

Required review: the testing-architecture owner reviews that the owner text enforces this decision. Documentation acceptance does not establish implementation conformance.

**Precision follow-up, not a blocker.** T10 states that the unit's `tests/` directory holds "exactly three level directories", while the guides describe tests as living in `tests/unit/`, `tests/integration/` *or* `tests/e2e/`. A unit that carries tests at only some levels therefore has no unambiguous reading, and this repository's own root unit currently holds one file and no level directory — a placement that predates this decision and forms part of the layout debt already recorded as DEBT-046. The corrective wording, if authorised later, is one sentence after T10's level-directory sentence: a level directory holding no tests for that unit need not exist, the three levels remain the only levels, and no test file sits directly in the test root; the same sentence would be mirrored in both guides' `File organization` sections and in the guide template. The owner review accepted this record without that sentence, so it is recorded here rather than applied.

## Propagation

- `architecture/testing/architecture.md` → `## Test organization` → **T10**.
- `architecture/testing/stacks/typescript.md` → `## File organization` (the paragraph beginning "Every test lives under its test-owning unit's single `tests/` directory").
- `architecture/testing/stacks/typescript.md` → the `File organization` row of the stack-guide mapping table.
- `architecture/testing/stacks/python.md` → `## File organization` (the paragraph beginning "Every test lives under its test-owning unit's single `tests/` directory").
- `architecture/testing/stacks/python.md` → the `File organization` row of the stack-guide mapping table.
- `architecture/testing/stacks/_template.md` → `## File organization` (the sentence beginning "Every test lives under its test-owning unit's `tests/` directory").
