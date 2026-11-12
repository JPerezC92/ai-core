# ADR 0009 — TypeScript test framework convention

- **Status:** Proposed — pending review and explicit approval
- **Date:** 2026-11-12

## Context

AICore's TypeScript testing surfaces currently use different runners, and nothing in the shared architecture selects one for the repository as a whole.

The synchronization CLI at `cli/aicore/` ships `node:test` with `node:assert/strict` and was deliberately built with zero runtime dependencies, because Node 24 strips types natively and no bundler, tsconfig-driven paths or test framework was needed to deliver it. Two other TypeScript packages — `.opencode/plugins/odd-adviser/` and `mcp-servers/system-one/` — carry their own manifests and their own local `typescript` and `@types/node` versions. `architecture/testing/stacks/typescript.md` describes Vitest, supertest, React and Playwright as **reference choices, not destination-wide bindings**, and states that a destination owns its runner and framework configuration — so the guide's Vitest references have never obligated this repository to use Vitest.

The consequence is a real inconsistency: the same repository runs two different assertion styles and two different runner conventions across its TypeScript surfaces, and every future TypeScript test has to guess which one applies.

The user first established the convention on 2026-11-12 with the migration deferred to the engine-migration unit, then the same day superseded that deferral: "The migration to Vitest was repeatedly deferred until U5. I no longer want that deferral." and "**Vitest is my chosen TypeScript testing framework, and I want the existing AICore CLI tests migrated now.**" The migration is therefore a separately authorized change of its own, not an expansion of the synchronization CLI change.

## Decision

Vitest is AICore's TypeScript testing framework, and the synchronization CLI's existing TypeScript suites migrate to it now.

- Migrated and future TypeScript tests import `describe`, `test`, `beforeEach`, `afterEach` and `expect` from `vitest`.
- Vitest's `expect` is preferred over Node's `assert` for consistency.
- Vitest's built-in mocks are used where mocking is necessary.
- `vitest-mock-extended` is adopted where the normative TypeScript testing guide requires a typed port double, and otherwise only where a concrete need justifies it.
- Node's test runner and Vitest are not mixed within the same test suite.

The migration is a single coherent change: runner, assertions, configuration and test scripts move together. A mechanical replacement of `assert` with `expect` while continuing to run `node:test` is explicitly not acceptable, and Vitest must not become a justification for creating mocks, fixtures, abstractions or additional test cases that the tests do not need.

These existing guarantees survive the migration unchanged: tests are independent and order-independent; each test owns its own mutable fixtures; no mutable state is reused across test cases; tests support safe parallel execution; cleanup stays bounded to verified disposable resources; no filesystem test uses the real AICore checkout or another real project as a destructive fixture; and the `T2`, `T8`, `T9`, `T11` and `T18` guarantees in `architecture/testing/architecture.md` continue to hold.

Authorization boundary: this decision selects the framework and authorizes the migration of the CLI package's TypeScript suites. It does not authorize any further change to a testing contract, does not authorize the migration of the other TypeScript packages in this repository, and does not begin the engine migration.

## Alternatives

- **Defer the migration to the engine-migration unit.** Considered and then superseded by explicit user decision on 2026-11-12. The original rationale was that one unit would migrate the runner and replace the engine together, avoiding a second pass over the same suites; the user rejected the repeated deferral.
- **Adopt Vitest during the synchronization CLI work.** Rejected earlier. That change explicitly excluded a Vitest migration, new testing dependencies and additional architecture changes.
- **Keep `node:test` permanently.** Rejected as a preference mismatch: it leaves two assertion styles and two runner conventions across TypeScript surfaces, which is the inconsistency this decision removes.
- **Mechanical `assert` → `expect` replacement under `node:test`.** Rejected by the decision itself. It produces Vitest-style assertions on a Node runner — the least consistent of the available states, and the one most likely to hide a behaviour change inside an import rewrite.
- **Jest.** Not selected. The repository's TypeScript stack guide already rules out mixing another unit runner alongside Vitest.

## Consequences

Benefits: one runner, one assertion style and one mocking convention across AICore's TypeScript surfaces; the stack guide's Vitest description stops being merely a reference choice and becomes the repository's actual convention; future TypeScript tests no longer have to guess.

Costs and risks: the CLI package gains development dependencies, so its zero-dependency property does not survive — a real change to the package's supply-chain surface, which is why the dependency gate applies before the manifest diff is staged. The migration touches every existing TypeScript test module and must prove behaviour and coverage are retained rather than asserted: a `node:test` suite that passes says nothing about how it behaves under Vitest, so migrated tests must be observed to execute and pass. The Vitest runner's own defaults must be compared against the previous runner's behavior before they are trusted, particularly for filesystem fixtures, because the previous runner's concurrency and isolation semantics are the baseline that the migration must not exceed.

## Propagation

**No normative change.** The TypeScript testing guide already enforces this decision's rule; it does not need to be edited, and editing a distributed reference guide to carry a repository-local binding would violate the shared-content boundary.

The reasoning, read from the owner text:

- `architecture/testing/stacks/typescript.md` → `## Test data and doubles` already states "Use the same test runner on both sides: Vitest. Do not mix in Jest or another unit runner", so a repository whose TypeScript suites run under Vitest complies rather than departs.
- The same section and `## Unit tests` → `### Backend use case` already require `vitest-mock-extended` as the single mocking facility for a use case whose port is doubled, so adopting it for the CLI's port doubles complies with the owner rather than narrowing it.
- `## Applicability and ownership` already states that the guide's tools are "reference choices, not destination-wide bindings" and that "A destination owns its package manager, runner, and framework configuration in project-owned files", so AICore's own binding of Vitest belongs in AICore's own package configuration and needs no shared text.
- `architecture/testing/architecture.md` is the language-agnostic contract and stays framework-neutral; it is not a propagation target and was not modified.

The binding itself is project-owned content: the CLI package's own manifest, runner configuration and test scripts. The independent owner check that this owner text enforces the decision is recorded in the change record that performs the migration.
