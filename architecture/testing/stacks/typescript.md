# TypeScript testing guide

> **Status:** reference
> **Stack:** TypeScript/TSX; NestJS-style backend and React frontend reference architecture
> **Reviewed:** 2026-10-25 — `testing-architecture-layering`; entity-construction clause 2026-10-30; stale `domain/entities/` factory-import spelling retired in favour of the concept's own domain module (`<concept>.entity.ts`), no `T` ID added, removed or moved 2026-11-05; `architecture-agnostic-fallback` applicability and `T14`/`T24`–`T25` selection wording aligned to the agnostic fallback and the `T22`–`T23` `N/A` set narrowed, no `T` ID added, removed, moved or renumbered 2026-11-06; 2026-11-12 — `T2`/`T4`/`T5`/`T10` applied to the file-organization, unit-test, integration-test and end-to-end sections: centralized root-level `tests/` placement, the approved unit targets, the component-with-its-real-hook boundary, the repository adapter against a real isolated database and the three-phase browser end to end; the three levels, the reference bindings and the observable assertions are unchanged, and no `T` ID was added, removed, moved or renumbered
> **Contract:** `architecture/testing/architecture.md`

## Applicability and ownership

This guide applies to TypeScript and TSX backend and frontend code. It is a reference architecture: Vitest, supertest, React, and Playwright are reference choices, not destination-wide bindings. A destination owns its package manager, runner, and framework configuration in project-owned files.

It covers the backend use-case, parser, repository, and HTTP entry-point boundaries, and the frontend component/hook and service boundaries. It does not cover another language, a non-React UI, or a destination-specific framework adapter that has no selected guide.

Apply this guide's mechanisms only to the concerns they cover. Uncovered concerns follow the contract's T24–T25 selection route; they do not inherit React, NestJS, Vitest, or Playwright mechanisms merely because the source is TypeScript. Covered concerns remain bound by their applicable mappings.

A destination may replace the reference tool names, paths, or framework adapters with its own stack. It must preserve the rules this guide cites: `T1`–`T21` and `T24`–`T29`, and it must keep `T24`–`T25` routing an uncovered concern to the contract instead of inheriting this stack's mechanisms. `T22`–`T23` and `T30`–`T36` are declared `N/A` in the parity table below because they govern selection by a reviewer and the authoring of a new guide rather than this guide's content.

## Test pyramid mapping

Concrete instantiation of the contract's three levels and their assertion duty (`T2`–`T5`):

```text
BACKEND                              FRONTEND
───────────────────────────          ───────────────────────────
Unit: mock IRepository               Unit: mock Service
  test use case execute()              render <Component /> (hook inside)

Unit: mock parser library            Service integration: mock fetch
  test one parser mapping              test service methods directly

Integration: real isolated database
  test repository directly

E2E: supertest + TestDatabaseModule  E2E: Playwright, 3 phases
```

| Level | Target | Collaborators and doubles | Observable assertion |
|---|---|---|---|
| Unit — backend | One use case | Ports mocked with `MockProxy` | Returned values and returned domain errors |
| Unit — frontend | Component with its real hook | Service mocked at the service module | Screen output and user-visible behavior |
| Unit — parser | One parser | External parser library mocked | Mapping, coercion, extraction, and failure behavior |
| Integration — backend | One repository adapter | Real isolated database | Raw record to domain entity mapping |
| Integration — frontend | One service module | `fetch` stubbed at the transport | Raw JSON to typed output or returned domain error |
| End to end — backend | Assembled HTTP entry point | Real app with `TestDatabaseModule` | HTTP status and body contract |
| End to end — frontend | Assembled browser entry point | Real application and seeded/mutating data | Page behavior and no uncaught page errors |

**Key rule:** a frontend unit test keeps the hook and component together. Double the service module and never the hook module (`T17`).

## File organization

- Every test lives under the project's single root-level `tests/` directory, in `tests/unit/`, `tests/integration/` or `tests/e2e/` (`T10`). No test file sits beside an implementation file, no `__tests__` directory lives inside a production module, and no test file lives under a source tree.
- Nested folders inside a level directory group tests by behavioural target and are chosen per project; this guide mandates none, and a role-named folder such as `parsers/`, `entities/`, `value_objects/` or `hooks/` is neither required nor approved as a level (`T10`).
- Backend use-case unit specs: `*.use-case.spec.ts`, one application use-case class with its ports doubled.
- Backend parser unit specs: `*.parser.spec.ts`, one parser with the external parser library doubled.
- Backend repository integration specs: `*.repository.integration.spec.ts`, one repository adapter against a real isolated database.
- Frontend component unit specs: `*.spec.tsx`, one component with its real hook and the service module doubled.
- Frontend service integration specs: `*.service.integration.spec.ts`, one service module with `fetch` stubbed at the transport.
- Backend end-to-end specs: `*.e2e-spec.ts` under `tests/e2e/`.
- Frontend browser specs: phase files under `tests/e2e/` — `smoke.spec.ts` for the smoke phase and `{module}.spec.ts` for the seeded-data and data-mutation phases.
- One behavior per `.spec.ts`, `.spec.tsx`, `.integration.spec.ts`, or `.e2e-spec.ts` file, and one per `describe` group inside it; a file or group holding several behaviors is a violation and is split by behavior (`T11`).
- File length never triggers that split, and a cohesive single-behavior file stays whole however long it grows (`T12`).

## Unit tests

### Backend use case

- Instantiate the use case directly with its mocked port: `useCase = new XUseCase(repository)`.
- Call `useCase.execute()` directly. Do not go through HTTP or a NestJS application.
- Mock the port with `MockProxy<IRepository>` from `vitest-mock-extended`; do not use `vi.fn()` or a manual mock.
- Assert returned domain errors, not thrown errors:

```typescript
expect(DomainError.isDomainError(result)).toBe(true);
expect(result).toBeInstanceOf(TaskNotFoundError);
```

- Do not use `expect(...).toThrow()` on a domain error; match the returned value with `toBeInstanceOf` as shown above (`T3`).
- Do not create `*.controller.spec.ts` files. A Nest controller only binds transport to the use case, so its HTTP contract is asserted at the end-to-end level and a controller unit test would duplicate it (`T8`).

### Backend parser

- Mock the external parser library with `vi.mock('xlsx', ...)`; no real spreadsheet file is required for a unit test.
- Cover field mapping, type coercion such as string to number, hyperlink extraction, and the documented error for an empty file.
- Call `vi.clearAllMocks()` in `beforeEach`.

### Frontend component and hook

- Mock the service module with `vi.mock('service-path')`; never mock the hook module.
- Use `MockProxy<typeof service>` from `vitest-mock-extended`. `vi.mocked()` or a manual cast is a violation.
- Render the component with `renderWithQueryClient(<Component />)`, not raw `render()`.
- Do not use `renderHook()` to test the hook in isolation. The hook is exercised through the component.
- Assert screen output with `screen.findByText(...)`, `screen.getByRole(...)`, or an equivalent user-visible query.
- Use the module factory (`{feature}.factory.ts`) for mock data; do not construct hardcoded inline objects in each test.

## Integration tests

### Backend repository

- Use `createTestDatabase()` and `migrateTestDatabase()`; do not add NestJS application overhead (`T4`).
- Instantiate the repository directly with the database: `repository = new XRepository(db)`.
- Do not use `Test.createTestingModule()`.
- Verify the transformation pipeline: raw database insert, repository method, domain entity output.
- Verify defaults, null handling, and that `findById` returns `null`, not throws, for a missing identifier.
- Use `beforeAll` for database setup. Add `beforeEach` and `deleteAll()` only when a test needs a clean slate.
- Do not use `MockProxy` at this level; use the real database.

### Frontend service

- The service's real dependency is a remote HTTP service that cannot be isolated in an integration test, so its transport is stubbed at that boundary (T4); this level proves the raw JSON to typed output mapping and the returned domain errors, not a live server.
- Stub `fetch` with `vi.stubGlobal('fetch', mockFetch)`; do not mock API-client internals.
- Call `vi.unstubAllGlobals()` and `vi.clearAllMocks()` in `afterEach`.
- Call the service methods directly, for example `const result = await featureService.getAll()`.
- On the happy path, verify raw JSON to typed output.
- A documented business-failure response maps to a returned typed domain error. Use the actual response contract and factory; a rejected network call is not evidence of a business failure (`T6`).
- A transport exception remains an exception, not a `FeatureServiceError` value. Use the test factory's boundary error and assert rejection identity (`T7`):

```typescript
mockFetch.mockRejectedValue(boundaryError);
await expect(featureService.getAll()).rejects.toBe(boundaryError);
```

## End-to-end tests

### Backend HTTP entry point

- Override `DatabaseModule` with `TestDatabaseModule`:

```typescript
.overrideModule(DatabaseModule).useModule(TestDatabaseModule)
```

- Register `DomainErrorFilter` as a global filter:

```typescript
app.useGlobalFilters(new DomainErrorFilter());
```

- Assert errors in the JSend fail shape:

```typescript
expect(response.body).toMatchObject({
  status: 'fail',
  data: { message: '...', code: ERROR_CODES.X },
});
```

- Assert successful responses with `response.body.status === 'success'`.

### Frontend browser entry point

- Place tests in the correct phase file:
  - `smoke.spec.ts` — page load only, no data assertions.
  - `{module}.spec.ts` in the seeded-data phase — interactions with seeded database data.
  - `{module}.spec.ts` in the data-mutation phase — upload and delete operations.
- Browser specs live under `tests/e2e/`; the phase separation is carried by the reviewed Playwright configuration, and a project that separates the phases by folder may group them under `tests/e2e/smoke/`, `tests/e2e/seeded/` and `tests/e2e/mutation/` because the three phases are approved behavioural targets (`T10`).
- Every seeded-data and data-mutation spec includes a `pageerror` listener. The smoke phase is exempt because it only loads the page.

```typescript
let pageErrors: string[];
test.beforeEach(async ({ page }) => {
  pageErrors = [];
  page.on('pageerror', (error) => pageErrors.push(error.message));
});
test.afterEach(async () => {
  expect(pageErrors).toHaveLength(0);
});
```

## Test data and doubles

- Shared factories live under the test root, for example `tests/support/{feature}.factory.ts`, and never inside a production module (`T10`, `T15`).
- The factory uses `faker` for data generation; no hardcoded values.
- The factory imports entity types from the shared package when one exists, otherwise from the concept's own domain module (`<concept>.entity.ts`).
- The factory provides at least `create(overrides?)` and `createMany(count, overrides?)`.
- When the test needs an entity rather than a data-only record, the factory builds it through the entity factory/`create()`; never assign entity fields directly to construct test data.
- Use the same mocking library across backend and frontend: `vitest-mock-extended` (`T16`).
- `vi.mocked()` or a manual cast anywhere is a violation; use `MockProxy`.
- Use the same test runner on both sides: Vitest. Do not mix in Jest or another unit runner.
- If two different tools perform the same job, treat it as a violation and consolidate.
- Keep each spec independent of every other spec: `vi.clearAllMocks()` in `beforeEach` for parser and unit modules, `vi.clearAllMocks()` plus `vi.unstubAllGlobals()` in `afterEach` for service modules, `deleteAll()` in `beforeEach` where a repository module needs a clean slate, and a `pageErrors` array re-created in `test.beforeEach` for each browser spec. Order never matters: a spec run alone passes the same way it does in the full suite, because every module seeds its own factory data, the parser library and `fetch` are stubbed, and integration rows come from `createTestDatabase()` rather than a developer's database (`T18`).

## Execution and evidence

- The reviewed whole-suite command for the TypeScript workspace is the only execution path for the specs above; this guide names no command and installs nothing (`T19`).
- Discovery uses the reviewed Vitest and Playwright configuration, not the reference paths, which describe layout and imply no narrower directory run (`T13`).
- A test-architecture verdict is reported per spec file; a Vitest coverage report or a green Playwright phase is execution evidence reported beside that verdict and never the verdict itself (`T9`, `T21`).
- Every feature-spec happy case and rejection case traces to a spec at the level that owns its behavior (`T8`).
- Missing scoped evidence is judged per file on this stack. A `.spec.ts`, `.spec.tsx`, `.integration.spec.ts`, or `.e2e-spec.ts` file inside a module this guide covers, without the evidence its declared level requires, is `[FAIL]`. For uncovered concerns, use the agnostic review route rather than treating absence of this guide's coverage as an uncertainty verdict (`T14`, `T25`).

## Cross-stack parity

| Contract section | Cited rule IDs | Language-specific achievement or N/A reason |
|---|---|---|
| Applicability and ownership | `T1`, `T20`, `T24`, `T25`, `T26` | Scope is TypeScript/TSX backend and frontend: the use-case, parser, repository, and HTTP entry-point boundaries plus the component/hook and service boundaries. Vitest, supertest, React, and Playwright are reference choices; a destination rebinds its package manager, runner, and framework adapters in project-owned files. Status `reference`. A non-TypeScript file, a non-React UI, or an adapter with no selected guide is out of scope: `T24`–`T25` route it to the contract and the applicable implementation contract/shapes, so uncovered coverage alone never becomes an uncertainty verdict. |
| Test pyramid mapping | `T2`, `T3`, `T4`, `T5` | Three levels per side: mocked-port use case, mocked-external-library parser and mocked-service component units, real-isolated-database repository and stubbed-`fetch` service integration, `supertest` plus `TestDatabaseModule` HTTP and three-phase Playwright browser end to end. Assertions are returned values, screen queries, mapped domain entities, JSend bodies, and page-error counts. |
| File organization | `T10`, `T11`, `T12`, `T13` | Every test lives under the single root-level `tests/` directory in `tests/unit/`, `tests/integration/` or `tests/e2e/`; no test file sits beside an implementation file and no `__tests__` directory lives inside a production module. Nested folders group tests by behavioural target and are chosen per project, with no role-named folder mandated. The `.spec.ts`, `.integration.spec.ts`, `.e2e-spec.ts`, and `.spec.tsx` suffixes carry level and discovery, with browser specs under `tests/e2e/`. One behavior per file and per `describe` group; length never splits a cohesive file. |
| Unit tests | `T2`, `T3`, `T17` | Direct construction and direct `execute()`, never through HTTP or a Nest application; `MockProxy<IRepository>` from `vitest-mock-extended` instead of `vi.fn()` or a manual mock; a backend parser unit with the external parser library mocked at its boundary, asserting field mapping, type coercion, extraction and the documented failure result; components rendered with `renderWithQueryClient` and asserted through `screen.findByText`/`getByRole`; returned domain errors matched with `DomainError.isDomainError` and `toBeInstanceOf`, never `toThrow()`; the service module doubled, the hook never. |
| Integration tests | `T4`, `T6`, `T7` | `createTestDatabase()`/`migrateTestDatabase()` with a directly constructed repository and no `Test.createTestingModule()`; `vi.stubGlobal('fetch', …)` for the service level, whose real dependency is a remote HTTP service that cannot be isolated, so its transport is stubbed at that boundary (T4); a documented failure body maps to a returned typed domain error while a rejected transport stays a rejection, asserted with `.rejects.toBe(boundaryError)`. |
| End-to-end tests | `T5`, `T7`, `T8` | `DatabaseModule` overridden by `TestDatabaseModule`, `DomainErrorFilter` registered globally, JSend `fail` and `success` bodies asserted. Declared difference: a Nest controller only binds transport to the use case, so its HTTP contract is asserted here and no `*.controller.spec.ts` exists. Browser specs split across smoke, seeded-data, and data-mutation phases, with a `pageerror` listener outside smoke. |
| Test data and doubles | `T15`, `T16`, `T18` | `tests/support/{feature}.factory.ts` shared factories, outside any production module, built on `faker` with `create()`/`createMany()` and entity construction through the entity factory; `vitest-mock-extended` is the single mocking facility, so `vi.mocked()` or a manual cast is a violation; Vitest is the single runner. Per-test isolation is `vi.clearAllMocks()` in `beforeEach`/`afterEach`, `vi.unstubAllGlobals()` in `afterEach`, `deleteAll()` where a repository module needs a clean slate, and a `pageErrors` array re-created in `test.beforeEach`. |
| Execution and evidence | `T9`, `T14`, `T19`, `T21`, `T25` | The reviewed whole-suite command for the TypeScript workspace is the only execution path, and discovery follows the reviewed Vitest and Playwright configuration rather than the reference paths. A verdict is reported per spec file; a Vitest coverage report or a green Playwright phase is execution evidence beside it. `T14` is cited here rather than under File organization because the verdict scope belongs with the evidence rules: a covered module's spec file lacking its level's evidence is `[FAIL]`; an uncovered concern uses the contract's `T25` selection route, not an automatic uncertainty verdict. |
| Cross-stack parity | `T27`, `T28`, `T29` | The ten sections keep the template order and rule granularity, every row here cites the identifiers it achieves, and the reference-path and reference-tool differences are declared rather than inherited generic-only. Parity evidence for this guide is the contract's `## Stack guides` row plus this table. |
| Open decisions | `T22`, `T23`, `T30`–`T36` | N/A — these govern stack-guide selection by a reviewer and the authoring of a new guide; none constrains this guide's body. `T24`–`T25` are not N/A: they are achieved above, in `Applicability and ownership` and in the `Execution and evidence` row. No open decisions remain: destination runner and framework bindings are project-owned, not unresolved here. |

## Open decisions

None. Destination-specific runner and framework bindings remain project-owned; they are not open decisions in this reference guide.
