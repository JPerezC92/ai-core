# TypeScript — React implementation guide

> **Status:** reference
> **Reviewed:** documentation only; implementation conformance not assessed

## Applicability and ownership

Applies to TypeScript/TSX React feature code and its imports in source/tests (F1, F2, C3). Read `architecture/implementation/architecture.md` and `architecture/implementation/shapes/frontend.md`. React Query, sonner, Zod, Tailwind, and API-client names are the preserved reference architecture, not destination tool bindings. Other UI stacks require their own mapping. Documentation review does not establish code conformance.

## Structure and dependency mapping

Keep the frontend shape's feature folders. Runtime flow: Component → Hook (driving adapter) → operation class `execute()` → injected domain port → Service (driven adapter) → HTTP/local data (F1, F2, C3). Each operation class lives in its own module under `modules/{feature}/hooks/`, one operation per module, named `<verb>-<object>.use-case.ts` after the shared concept-role table, in a module separate from the Hook's module. The operation module imports only domain types and its injected port; the Hook's module carries the framework and composition imports and constructs the operation with the concrete adapter.

For F4, intentional data modules use paths such as `domain/order/order-summary.projection.ts` or `order-snapshot.record.ts`. Actual aggregates use `domain/order/order.entity.ts` beside `order.repository.ts`; a second entity moves root/child modules into `domain/order/entities/`, and a second owned value uses `domain/order/value-objects/`. Other role folders grow inside the same business owner. No child scaffolding is needed for a root-only model.

## Domain and ports

- Always provide `domain/errors/{feature}-service.error.ts`. Define a module-specific `{Feature}ServiceError` class extending `Error` (for example `TasksServiceError`), never a generic shared class literally named `FeatureServiceError`.
- Carry a stable business code. Constructor uses `super(message)` and sets `this.name` to the actual class name; it never throws. Do not represent arbitrary transport/parsing/programming exceptions with this class (F1, C2).
- Detect shared types first: when a same-language shared package exists (e.g. `@repo/reports/frontend`), import its appropriate domain types without duplicates. Otherwise define concept-specific record/projection modules in the feature domain, never inline in services/hooks/components. Type aliases/interfaces map data-only records, not C8 entities (F1, F4, C10).
- Domain includes typed service/query ports; domain and service contain no React imports. Types/schemas come from the shared package if present, otherwise feature domain records/models (F1, C2). A service/query interface remains applicable without an aggregate repository; domain-owned `OrderSummary` is a projection return type, not the HTTP response schema (C9).
- If C8 rule-bearing models are used, map entities to framework-free classes with private construction, readonly private fields, read accessors and `create()`/`reconstitute()` factories. Behavior returns `Order | OrderClosedError` replacements. Protect nested values using immutable children and copied/protected collections; TypeScript `readonly` alone does not prevent runtime alias mutation. Value objects use value equality; pending event payloads and collections are immutable on the returned aggregate. Reconstitution does not create events. Pure calculations remain ordinary typed functions. This conditional mapping does not turn data records into entity classes.

## Application operations

The operation is an undecorated plain class with an `execute()` method — never a Hook and never a standalone function — whose `execute()` calls the injected domain service port and returns domain data or the module's typed error (C3, C1, C5). It receives the service port through a constructor parameter, never a setter or a module-level global, and the Hook's composition constructs it with the concrete adapter before calling `operation.execute()` from `queryFn`/`mutationFn`. It never calls React Query, `useState`, `useEffect`, any Hook, `fetch`, or `apiClient`, and it extends no base class and defines no interface, hierarchy or forwarding wrapper. A React component, a Hook and a general-purpose utility are not application use cases and are not turned into classes by this rule (C3).

Where local aggregate persistence is actually used, C9 maps to injected repository/transaction interfaces: narrow a transition's result union and save the returned replacement, not the unchanged original. A backend-owned transaction is not spread across unrelated HTTP calls or claimed atomic by a Hook. Query/service-only features need no invented repository or UoW. Any local event publication flow stays outside domain and specifies delivery failure handling where required.

## Adapters and delivery

### Service

- `modules/{feature}/services/{feature}.service.ts` exports a plain object (`export const xService = { ... }`), never a class; no React imports or local inline types/interfaces, no business logic.
- With HTTP: request unknown (`apiClient.get<unknown>(...)`), then unwrap/validate once with `parseJsendData(zodSchema, raw)`. No type casts or `as T`. Return `Promise<T | {Feature}ServiceError>`, never a raw `Error` value. Implement `architecture/implementation/shapes/frontend.md` → `F2 — Operation and adapter` by mapping documented business-failure responses to returned `{Feature}ServiceError` values, not thrown/rejected business failures. Do not blanket-catch unrelated exceptions into domain errors; preserve their exception identity.
- Without backend/HTTP: remain synchronous, returning `T | {Feature}ServiceError`, not `Promise<T>` (F2). No `async`, `await`, `fetch`, or HTTP. A typed data service may be `export const featureService = { getAll: (): OrderSummary[] | TasksServiceError => localDataArray };` with typed domain projection imports. Do not invent a failure just to fill the union.
- C10 delivery types such as `CreateOrderRequest`/`OrderResponse` map in the service edge to/from domain parameters and records. If an adapter accesses local persistence, `OrderRow`/`OrderModel` stay there and entity mapping calls `reconstitute()` (C4, C8, C9). None is an alias for the domain entity.
- Transport payload handling — request and response bodies, their JSON shape and their validation — stays at this edge; the operation consumes and returns domain types only (C6).

### Hook

- Query keys live in `keys.ts` with `as const`, not inline strings. Fetch Hooks use `useQuery` and those keys.
- `queryFn`/`mutationFn` checks `if (result instanceof TasksServiceError) throw result`. Only this presentation binding turns returned business errors into React Query error state; propagated exceptions reach it without domain reclassification (F3, C5).
- Mutation `onSuccess` invalidates relevant queries. `onError` only calls `console.error()`, never `toast.*`. Filter Hooks use `useMemo`.
- No direct `apiClient`/`fetch`; call through the operation's injected service port. For the Hook/component test boundary, read `architecture/testing/stacks/typescript.md` → `Unit tests` → `Frontend component and hook`.

### Component

- Read React Query data/error state and invoke Hooks, never services/transport directly. Do not wrap Hook calls in try/catch for errors (F3).
- Import `toast` from `sonner`; only components call `toast.success()`/`toast.error()`, never Hooks.
- Delete buttons include `bg-red-600 hover:bg-red-700`, not `bg-destructive`. Delete confirmation uses `AlertDialog`; create/edit forms use `Dialog`.
- Modals are controlled by `open` plus `onOpenChange`; forms reset when `onOpenChange(false)` is called. No uncontrolled modals.

## Imports and language conventions

Import rules apply to every layer and tests: same-directory `./sibling` imports are allowed; all non-sibling imports use project aliases (`@/modules/...`, `@/shared/...`, `@/lib/...`, `@repo/...`; theme/i18n aliases likewise). Parent traversal (`../`, `../../`) and cross-folder `./subfolder/...` imports are forbidden (C1).

For same-language backend/frontend, retain the same validation library (e.g. Zod). Mocking-library, runner-consistency, and test-cast rules are owned by `architecture/testing/stacks/typescript.md` → `Test data and doubles`; read that section rather than treating this implementation guide as a second testing authority.

C10's language syntax is the shared table at `architecture/implementation/stacks/typescript/nestjs.md` → `Concept-role filenames`: kebab-case concept plus dot role and `.ts` (or the explicitly shown `.js` equivalent). The operation class uses that table's use-case row. That table supplies filenames only, not NestJS dependencies or JavaScript framework approval. F4 domain records use `.record.ts` or the more precise `.projection.ts`, actual entities `.entity.ts`; class names remain business names. Pure predicates/calculations keep their business-function names (C7).

## Testing and runtime boundaries

Read `architecture/testing/architecture.md` and `architecture/testing/stacks/typescript.md`. They own component/Hook units, service integration, and assembled-browser tests. Execution authority, edit scope, gates, dependencies, and uncertainty handling remain runtime-owned.

## Obligation mapping

| Obligation | Concrete mapping | Applicability or uncovered decision |
|---|---|---|
| C1 Layers/dependencies | Structure and dependency mapping | Co-location does not permit operation framework imports. |
| C2 Domain/ports | Domain and ports | Feature-specific error, shared/local records and conditional framework-free models. |
| C3 Operation | Application operations | Undecorated class with `execute()` and a constructor-injected port, not a Hook and not a standalone function; no base class, interface, hierarchy or forwarding wrapper. |
| C4 Mapping/composition | Domain and ports; Service and Hook | Rule ownership: a rule-bearing domain model owns the rule (C8) and the service owns none; unknown HTTP input parsed once; synchronous local-data branch. |
| C5 Failures | Domain and ports; Application operations; Service and Hook | Frontend F2 maps documented service failures to returned typed errors, never business-failure throws; unrelated exceptions retain identity. Query-state conversion is presentation-only. |
| C6 Serialization | Service | Transport payload handling stays at the service edge, not in the operation. |
| C7 Helpers | Application operations; Imports and language conventions | Pure helpers keep their business-function names and are not forced into React Hooks or use cases. |
| C8 Domain model | Domain and ports | Interfaces for records; conditional private entity factories, immutable replacements/nested values and pending facts. |
| C9 Repositories/transactions | Domain and ports; Application operations; Service | Applicable service/query ports; conditional local aggregate persistence, no invented client-side transaction over HTTP. |
| C10 Naming | Imports and language conventions; Service | Shared TS/JS syntax table, precise record/projection and boundary roles. |
| F1 Layout/domain | Structure; Domain and ports | Feature folders retained. |
| F2 Operation/adapter | Application operations; Service | Port injection and zero-business adapter. |
| F3 Presentation | Hook; Component | Query state, notifications, controlled dialogs. |
| F4 Organization | Structure and dependency mapping; Domain and ports | Feature/business-local modules and internal role growth, shared-type reuse. |

## Open decisions

None identified for this mapping.
