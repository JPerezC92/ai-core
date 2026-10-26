<!-- core:begin -->
# TypeScript testing guide

> **Status:** reference
> **Stack:** TypeScript/TSX; NestJS-style backend and React frontend reference architecture
> **Guide owner:** Crucible 🔥 (Test Architect)
> **Reviewed:** 2026-10-25 — `testing-architecture-layering`
> **Contract:** `architecture/testing/architecture.md`

## Applicability and ownership

This guide applies to TypeScript and TSX backend and frontend code. It is a reference architecture: Vitest, supertest, React, and Playwright are reference choices, not destination-wide bindings. A destination owns its package manager, runner, and framework configuration in project-owned files.

It covers the backend use-case, parser, repository, and HTTP entry-point boundaries, and the frontend component/hook and service boundaries. It does not cover another language, a non-React UI, or a destination-specific framework adapter that has no selected guide.

## Test pyramid mapping

Concrete instantiation of the agnostic levels:

```text
BACKEND                              FRONTEND
───────────────────────────          ───────────────────────────
Unit: mock IRepository               Unit: mock Service
  test use case execute()              render <Component /> (hook inside)

Integration: real in-memory DB       Service integration: mock fetch
  test repository directly             test service methods directly

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

**Key rule:** a frontend unit test keeps the hook and component together. Mock at the service boundary; never mock the hook.

## File organization

- Backend unit tests: `test/{module}/application/use-cases/*.spec.ts`.
- Backend integration tests: `test/{module}/infrastructure/*.repository.integration.spec.ts`.
- Backend parser tests: `test/{module}/infrastructure/*.parser.spec.ts`.
- Backend end-to-end tests: `test/{module}/*.e2e-spec.ts`.
- Frontend unit tests: `modules/{module}/__tests__/components/*.spec.tsx`.
- Frontend service integration tests: `modules/{module}/__tests__/services/*.service.integration.spec.ts`.
- Frontend end-to-end tests: `e2e/__tests__/*.spec.ts`.
- One behavior per test module and per class or describe-group. A multi-behavior module or group is a violation and must be split by behavior.
- There is no line cap; behavior, not size, sets the split boundary.

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

- Do not use `expect(...).toThrow()` for domain errors. Use cases return business failures.
- Do not create `*.controller.spec.ts` files. Controller unit tests are redundant; the HTTP end-to-end test covers the controller.

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

- Use `createTestDatabase()` and `migrateTestDatabase()`; do not add NestJS application overhead.
- Instantiate the repository directly with the database: `repository = new XRepository(db)`.
- Do not use `Test.createTestingModule()`.
- Verify the transformation pipeline: raw database insert, repository method, domain entity output.
- Verify defaults, null handling, and that `findById` returns `null`, not throws, for a missing identifier.
- Use `beforeAll` for database setup. Add `beforeEach` and `deleteAll()` only when a test needs a clean slate.
- Do not use `MockProxy` at this level; use the real database.

### Frontend service

- Stub `fetch` with `vi.stubGlobal('fetch', mockFetch)`; do not mock API-client internals.
- Call `vi.unstubAllGlobals()` and `vi.clearAllMocks()` in `afterEach`.
- Call the service methods directly, for example `const result = await featureService.getAll()`.
- On the happy path, verify raw JSON to typed output.
- A documented business-failure response maps to a returned typed domain error. Use the actual response contract and factory; a rejected network call is not evidence of a business failure.
- A transport exception remains an exception, not a `FeatureServiceError` value. Use the test factory's boundary error and assert rejection identity:

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

- Each module has `__tests__/helpers/{feature}.factory.ts`.
- The factory uses `faker` for data generation; no hardcoded values.
- The factory imports entity types from the shared package when one exists, otherwise from `domain/entities/`.
- The factory provides at least `create(overrides?)` and `createMany(count, overrides?)`.
- Use the same mocking library across backend and frontend: `vitest-mock-extended`.
- `vi.mocked()` or a manual cast anywhere is a violation; use `MockProxy`.
- Use the same test runner on both sides: Vitest. Do not mix in Jest or another unit runner.
- If two different tools perform the same job, treat it as a violation and consolidate.

## Execution and evidence

- The project's reviewed whole-suite command is the only execution authority. This guide does not authorize running tests or installing dependencies.
- Test discovery follows the project's reviewed runner configuration. The paths above are reference layout, not a grant to run a narrower directory.
- The architecture verdict is separate from the execution result. A green run does not establish conformance.
- Every feature-spec happy case and rejection case must trace to a test at the appropriate level.

## Cross-stack parity

| Contract section | Coverage | Difference or N/A reason |
|---|---|---|
| Applicability and ownership | Covered | TypeScript-specific framework names are reference choices; the destination owns bindings. |
| Test pyramid mapping | Covered | Backend and frontend map to the same three levels. |
| File organization | Covered | Exact paths are reference layout; a destination may adapt them in its project extension. |
| Unit tests | Covered | Use-case, parser, and component/hook units are defined. |
| Integration tests | Covered | Repository and service adapter boundaries are defined. |
| End-to-end tests | Covered | HTTP and browser entry points are defined. |
| Test data and doubles | Covered | Factories, `faker`, `MockProxy`, and one-runner consistency are defined. |
| Execution and evidence | Covered | Execution stays project-owned; architecture and execution verdicts stay separate. |
| Cross-stack parity | Covered | The guide uses the shared contract and covers backend and frontend scope. |
| Open decisions | Covered | None; the reference decisions are resolved for this guide. |

## Open decisions

None. Destination-specific runner and framework bindings remain project-owned; they are not open decisions in this reference guide.

<!-- core:end -->

<!-- project:begin -->
## Project extensions

A destination may replace the reference tool names, paths, or framework adapters with its selected stack. It must preserve the levels, boundaries, returned-business-failure rule, one-behavior rule, factory rule, and execution/verdict separation.
<!-- project:end -->
