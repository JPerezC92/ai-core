<!-- core:begin -->
# TypeScript — React implementation guide

> **Status:** reference
> **Reviewed:** documentation only; implementation conformance not assessed

## Applicability and ownership

Applies to TypeScript/TSX React feature code and its imports in source/tests. Read `architecture/clean-architecture.md` and `architecture/shapes/frontend.md`. React Query, sonner, Zod, Tailwind, and API-client names are the preserved reference architecture, not destination tool bindings. Other UI stacks require their own mapping. Documentation review does not establish code conformance.

## Structure and dependency mapping

Keep the frontend shape's feature folders. Runtime flow: Component → Hook (driving adapter) → ordinary `execute()` → injected domain port → Service (driven adapter) → HTTP/local data. The operation lives in `modules/{feature}/hooks/use-{feature}.ts`, co-located with its Hook. Co-location permits framework/composition imports for the Hook, never framework/concrete-service dependencies inside the operation.

## Domain and ports

- Always provide `domain/errors/{feature}-service.error.ts`. Define a module-specific `{Feature}ServiceError` class extending `Error` (for example `TasksServiceError`), never a generic shared class literally named `FeatureServiceError`.
- Carry a stable business code. Constructor uses `super(message)` and sets `this.name` to the actual class name; it never throws. Do not represent arbitrary transport/parsing/programming exceptions with this class.
- Detect shared types first: when a same-language shared package exists (e.g. `@repo/reports/frontend`), import entity types there, with no duplicate local types. Otherwise define them in `domain/entities/{entity}.ts`, never inline in services/hooks/components. Entity types — locally defined in `domain/entities/{entity}.ts` or imported from the shared package — are data-only domain records by design — not rule-holding entities: they carry data and enforce no invariants.
- Domain includes the typed service port; domain and service contain no React imports. Types/schemas come from the shared package if present, otherwise domain entities.

## Application operations

`execute()` is an ordinary plain function or object method, not a Hook. It calls the injected domain service port and returns domain data or the module's typed error. It never calls React Query, `useState`, `useEffect`, any Hook, `fetch`, or `apiClient`. The Hook's composition supplies the concrete adapter and calls the operation from `queryFn`/`mutationFn`.

## Adapters and delivery

### Service

- `modules/{feature}/services/{feature}.service.ts` exports a plain object (`export const xService = { ... }`), never a class; no React imports or local inline types/interfaces, no business logic.
- With HTTP: request unknown (`apiClient.get<unknown>(...)`), then unwrap/validate once with `parseJsendData(zodSchema, raw)`. No type casts or `as T`. Return `Promise<T | {Feature}ServiceError>`, never a raw `Error` value. Implement `architecture/shapes/frontend.md` → `F2 — Operation and adapter` by mapping documented business-failure responses to returned `{Feature}ServiceError` values, not thrown/rejected business failures. Do not blanket-catch unrelated exceptions into domain errors; preserve their exception identity.
- Without backend/HTTP: remain synchronous, returning `T | {Feature}ServiceError`, not `Promise<T>`. No `async`, `await`, `fetch`, or HTTP. A typed data service may be `export const featureService = { getAll: (): EntityType[] | TasksServiceError => localDataArray };` with typed domain imports. Do not invent a failure just to fill the union. Exceptions may propagate unchanged.

### Hook

- Query keys live in `keys.ts` with `as const`, not inline strings. Fetch Hooks use `useQuery` and those keys.
- `queryFn`/`mutationFn` checks `if (result instanceof TasksServiceError) throw result`. Only this presentation binding turns returned business errors into React Query error state; propagated exceptions reach it without domain reclassification.
- Mutation `onSuccess` invalidates relevant queries. `onError` only calls `console.error()`, never `toast.*`. Filter Hooks use `useMemo`.
- No direct `apiClient`/`fetch`; call through the operation's injected service port. For the Hook/component test boundary, read `architecture/testing/stacks/typescript.md` → `Unit tests` → `Frontend component and hook`.

### Component

- Read React Query data/error state and invoke Hooks, never services/transport directly. Do not wrap Hook calls in try/catch for errors.
- Import `toast` from `sonner`; only components call `toast.success()`/`toast.error()`, never Hooks.
- Delete buttons include `bg-red-600 hover:bg-red-700`, not `bg-destructive`. Delete confirmation uses `AlertDialog`; create/edit forms use `Dialog`.
- Modals are controlled by `open` plus `onOpenChange`; forms reset when `onOpenChange(false)` is called. No uncontrolled modals.
- Transport serialization remains at presentation/delivery, not inside `execute()`.

## Imports and language conventions

Import rules apply to every layer and tests: same-directory `./sibling` imports are allowed; all non-sibling imports use project aliases (`@/modules/...`, `@/shared/...`, `@/lib/...`, `@repo/...`; theme/i18n aliases likewise). Parent traversal (`../`, `../../`) and cross-folder `./subfolder/...` imports are forbidden.

For same-language backend/frontend, retain the same validation library (e.g. Zod). Mocking-library, runner-consistency, and test-cast rules are owned by `architecture/testing/stacks/typescript.md` → `Test data and doubles`; read that section rather than treating this implementation guide as a second testing authority.

## Testing and runtime boundaries

Read `architecture/testing/architecture.md` and `architecture/testing/stacks/typescript.md`. They own component/Hook units, service integration, and assembled-browser tests. Execution authority, edit scope, gates, dependencies, and uncertainty handling remain runtime-owned.

## Obligation mapping

| Obligation | Concrete mapping | Applicability or uncovered decision |
|---|---|---|
| C1 Layers/dependencies | Structure and dependency mapping | Co-location does not permit operation framework imports. |
| C2 Domain/ports | Domain and ports | Feature-specific error, shared/local data-only domain records; no rule-holding entities. |
| C3 Operation | Application operations | Ordinary function/object method, not a Hook. |
| C4 Mapping/composition | Service and Hook | Unknown HTTP input, one parse; synchronous local-data branch. |
| C5 Failures | Domain and ports; Service and Hook | Frontend F2 maps documented service failures to returned typed errors, never business-failure throws; unrelated exceptions retain identity. Query-state conversion is presentation-only. |
| C6 Serialization | Component | Delivery edge, not operation. |
| C7 Helpers | Common contract | Pure helpers are not forced into React Hooks/use cases. |
| F1 Layout/domain | Structure; Domain and ports | Feature folders retained. |
| F2 Operation/adapter | Application operations; Service | Port injection and zero-business adapter. |
| F3 Presentation | Hook; Component | Query state, notifications, controlled dialogs. |

## Open decisions

None identified for this mapping.
<!-- core:end -->

<!-- project:begin -->
## Project extensions
<!-- project:end -->
