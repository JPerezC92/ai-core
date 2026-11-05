# TypeScript — NestJS implementation guide

> **Status:** reference
> **Reviewed:** documentation only; implementation conformance not assessed

## Applicability and ownership

Applies to TypeScript/TSX backend application source using the NestJS reference architecture and import conventions for its tests (B1). Read `architecture/implementation/architecture.md` and `architecture/implementation/shapes/backend.md`. NestJS, database, Zod, and JSend names are preserved reference mappings, not destination bindings. Other frameworks/languages require their own mapping. Documentation review is not code-conformance evidence.

## Structure and dependency mapping

Bind backend folders to `domain/`, `application/use-cases/`, and `infrastructure/` (B1). All NestJS code is infrastructure-owned (C1).

For B4, a compact aggregate maps to `domain/order/order.entity.ts`, `order.repository.ts` and `shipping-address.value-object.ts`. At a second entity module, place root and child modules in `domain/order/entities/`; at a second value module use `domain/order/value-objects/`. Other roles map likewise inside `order/`. The repository port remains aggregate-local even if a role folder separates it physically from its root. A root-only aggregate has no artificial child directories.

## Domain and ports

- Entities use aggregate-local C10 filenames, a private constructor, `private readonly` storage, getter method per field and static `create()`/`reconstitute()` factories (C2, C8, B1). A transition returns `Order | OrderClosedError`, constructing a same-identity replacement. Copy mutable inputs and protect nested objects/collections; expose immutable values or defensive copies, not writable aliases. TypeScript `readonly`/`ReadonlyArray` alone is not runtime protection. Root methods may construct children internally while enforcing child/cross-part invariants. No `@nestjs/`, `drizzle-orm`, or infrastructure imports.
- C8 value objects use framework-free value-equality classes. Events use immutable payload objects and a protected read-only pending collection on the returned aggregate. Reconstitution validates stored state without creation replay; corrupt-state exceptions retain C5 semantics. Plain interfaces/type aliases map intentional records/projections, not entity behavior.
- Repository interfaces use aggregate-local `order.repository.ts`; export `const X_REPOSITORY = Symbol('X_REPOSITORY')`. `findById(): Promise<Order | null>` maps C9 lookup. Query interfaces return domain `OrderSummary` projections; other ports use `clock.port.ts`-style names. No framework/storage imports (B1/C2/C9).
- Errors use business-owned `order-closed.error.ts`-style paths (B4, C10); extend `DomainError`, with `readonly code` from `ERROR_CODES.*`, not a raw string. Constructor calls `super(ERROR_MESSAGES[ERROR_CODES.*](id))`.
- Register codes in `shared/domain/errors/error-codes.ts`: SCREAMING_SNAKE_CASE, `_NOT_FOUND`, `_ALREADY_EXISTS`, or another suffix with HTTP mapping. Register messages as lambdas, not plain strings, in `shared/domain/errors/error.messages.ts` (C2).

## Application operations

For C3/C5/B2, use an undecorated TypeScript class, not a function/plain object: `<Verb><Object>UseCase` in `application/use-cases/<verb>-<object>.use-case.ts`, with public `execute(): Promise<Order | DomainError>` (or the operation's concrete result union). Constructor parameter types name repository/service interfaces. No `@Injectable()`, `@Controller()`, or other NestJS decorator. The empty lookup branch maps to `if (order === null) return new OrderNotFoundError(id)`; `NotFoundException` is excluded here and in repositories.

For C9, bind the transition result, narrow its error union, and explicitly save the replacement object. Transaction coordination uses an injected domain capability if needed; its infrastructure implementation supplies database transaction/session behavior. The application publication flow handles pending facts after successful persistence and names its reliability/failure strategy where required; no NestJS bus dependency is introduced into domain/application.

## Adapters and delivery

### Adapters and repositories

- `infrastructure/adapters/{entity}.adapter.ts`: `{Entity}Adapter` class, static `toDomain(record): EntityType`, only static methods. For entities this calls `reconstitute()`, not creation. DB types imported with `import type` from `@repo/database`. `order.row.ts`/`order.model.ts` remain infrastructure records; query adapters construct domain projections (C8–C10).
- `infrastructure/repositories/{entity}.repository.ts`: implements domain interface (`implements IXRepository`), no `@Injectable()`. Constructor receives `db: Database`, with no `@Inject` parameter decorator. Use adapter `toDomain()`, never inline entity construction; no business rules (C4/B3).

### Controllers

- `infrastructure/{module}.controller.ts`, never module root. Inject use cases directly; no service facade or facade `service.ts`.
- Success wraps as `return { status: 'success' as const, data }`. For use cases returning `T | DomainError`, check `if (result instanceof DomainError) throw result` at this delivery boundary.
- Success documentation uses `@ZodResponse({ status, description, type })`; errors use `@ApiResponse({ status: 4xx, type: JSendFailDto })`.
- Define JSend DTOs at file top: `class JSendXDto extends createZodDto(jsendSuccess(xSchema)) {}`. Serialization is controller-owned, not business-operation-owned (C5/C6/B3).
- Delivery payload modules, where separate types are needed, use `create-order.request.ts` and `order.response.ts` (C10). They map to/from domain parameters/results; JSend envelope DTOs keep their distinct transport role.

### Composition

`infrastructure/{module}.module.ts`, never module root; no service facade. Repository factory: `{ provide: X_REPOSITORY, useFactory: (db) => new XRepository(db), inject: [DATABASE_CONNECTION] }`. Use-case factory: `{ provide: XUseCase, useFactory: (repo) => new XUseCase(repo), inject: [X_REPOSITORY] }` (C4). No `@Injectable()` on operation or repository classes.

## Imports and language conventions

Every source/test layer follows this import rule: same-directory `./sibling` imports are allowed; all non-sibling imports use tsconfig aliases (`@tasks/...`, `@shared/...`, `@database/...`, `@repo/...`). Parent traversal (`../`, `../../`) and cross-folder `./subfolder/...` imports are forbidden (C1). No NestJS `NotFoundException` in repositories or operations, no root controller/module, no service facade.

### Concept-role filenames

The C10 vocabulary maps to kebab-case concepts plus dot-separated roles. This syntax table also supplies the JavaScript filename equivalent; it does not establish a reviewed JavaScript framework stack. React uses this same syntax table. Class `Order` is not renamed `OrderEntity`.

| C10 role | TypeScript | JavaScript filename equivalent |
|---|---|---|
| entity | `order.entity.ts` | `order.entity.js` |
| value object | `shipping-address.value-object.ts` | `shipping-address.value-object.js` |
| event | `order-placed.event.ts` | `order-placed.event.js` |
| repository | `order.repository.ts` | `order.repository.js` |
| port | `clock.port.ts` | `clock.port.js` |
| domain service | `pricing.domain-service.ts` | `pricing.domain-service.js` |
| policy | `pricing.policy.ts` | `pricing.policy.js` |
| error | `order-closed.error.ts` | `order-closed.error.js` |
| row | `order.row.ts` | `order.row.js` |
| model | `order.model.ts` | `order.model.js` |
| request | `create-order.request.ts` | `create-order.request.js` |
| response | `order.response.ts` | `order.response.js` |
| projection | `order-summary.projection.ts` | `order-summary.projection.js` |
| record | `order-snapshot.record.ts` | `order-snapshot.record.js` |
| query | `order-summary.query.ts` | `order-summary.query.js` |

C7/C10 pure-function modules use names such as `is-order-eligible.ts` and `calculate-price.ts` (or `.js`), not invented service/entity suffixes.

## Testing and runtime boundaries

Read `architecture/testing/architecture.md` and `architecture/testing/stacks/typescript.md`. Testing owns operation, repository, parser, and HTTP test boundaries and concrete doubles. Runtime specs retain file routing, scope, review, after-edit gates, execution, and uncertainty procedures.

## Obligation mapping

| Obligation | Concrete mapping | Applicability or uncovered decision |
|---|---|---|
| C1 Layers/dependencies | Structure | Framework code only in infrastructure. |
| C2 Domain/ports | Domain and ports | Entities with behavior and immutable identity, Symbol ports, centralized errors. |
| C3 Operation | Application operations | Undecorated class with interface injection. |
| C4 Mapping/composition | Adapters; Composition | Static mapping plus factory providers. |
| C5 Failures | Application operations; Controllers | Null → returned error → delivery throw. |
| C6 Serialization | Controllers | JSend DTO/response edge. |
| C7 Helpers | Common contract | No artificial class wrapper for a pure helper. |
| C8 Domain model | Domain and ports | Private construction, replacement unions, nested protection, value classes, records and pending events. |
| C9 Repositories/transactions | Domain and ports; Application operations; Adapters | Symbol interfaces, null lookup, projection return types, explicit replacement save and injected transaction capability. |
| C10 Naming | Concept-role filenames; Adapters; Controllers | Shared roles in TS/JS syntax with boundary-specific modules. |
| B1 Layout/domain | Structure; Domain and ports | Readonly fields, getters, null lookup; behavior, identity and the valid-instance factory are mapped by C2. |
| B2 Operation | Application operations | Null policy in operation. |
| B3 Infrastructure | Adapters and delivery | Repository port, static mapper, edge factories. |
| B4 Organization | Structure and dependency mapping; Domain and ports | Aggregate-local modules, internal role growth and protected child construction. |

## Open decisions

None identified for this mapping.
