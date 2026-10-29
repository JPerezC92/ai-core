<!-- core:begin -->
# TypeScript — NestJS implementation guide

> **Status:** reference
> **Reviewed:** documentation only; implementation conformance not assessed

## Applicability and ownership

Applies to TypeScript/TSX backend application source using the NestJS reference architecture and import conventions for its tests. Read `architecture/clean-architecture.md` and `architecture/shapes/backend.md`. NestJS, database, Zod, and JSend names are preserved reference mappings, not destination bindings. Other frameworks/languages require their own mapping. Documentation review is not code-conformance evidence.

## Structure and dependency mapping

Bind backend folders to `domain/`, `application/use-cases/`, and `infrastructure/`. Pure TypeScript domain/application import no framework or infrastructure. All NestJS code is infrastructure-owned; runtime port calls do not permit concrete imports inward.

## Domain and ports

- Entities: `domain/entities/{entity}.entity.ts`; constructor fields `private readonly`, getter method per field, static `create()` factory. No `@nestjs/`, `drizzle-orm`, or infrastructure imports.
- Repository interfaces: `domain/repositories/{entity}.repository.interface.ts`; export `const X_REPOSITORY = Symbol('X_REPOSITORY')`. Return domain entities, not DB records; `findById(): Promise<Entity | null>` never throws for missing data. No framework/storage imports.
- Errors: `domain/errors/{entity}-{suffix}.error.ts`; extend `DomainError`, with `readonly code` from `ERROR_CODES.*`, not a raw string. Constructor calls `super(ERROR_MESSAGES[ERROR_CODES.*](id))`.
- Register codes in `shared/domain/errors/error-codes.ts`: SCREAMING_SNAKE_CASE, `_NOT_FOUND`, `_ALREADY_EXISTS`, or another suffix with HTTP mapping. Register messages as lambdas, not plain strings, in `shared/domain/errors/error.messages.ts`.

## Application operations

Use a pure TypeScript class, not function/plain object; one `execute()`. The class is `<Verb><Object>UseCase` in `application/use-cases/<verb>-<object>.use-case.ts`, with one public `execute()`. Constructor receives repository/service interfaces, not concrete classes. Only domain imports, no `@Injectable()`, `@Controller()`, or other NestJS decorator. Return domain errors, never `throw new XError()`. When `findById` returns null, the operation checks it and returns its domain not-found error; repositories must not throw `NotFoundException`.

## Adapters and delivery

### Adapters and repositories

- `infrastructure/adapters/{entity}.adapter.ts`: `{Entity}Adapter` class, static `toDomain(record): EntityType`, only static methods. DB types imported with `import type` from `@repo/database`.
- `infrastructure/repositories/{entity}.repository.ts`: implements domain interface (`implements IXRepository`), no `@Injectable()`. Constructor receives `db: Database`, with no `@Inject` parameter decorator. Use adapter `toDomain()`, never inline entity construction; no business rules.

### Controllers

- `infrastructure/{module}.controller.ts`, never module root. Inject use cases directly; no service facade or facade `service.ts`.
- Success wraps as `return { status: 'success' as const, data }`. For use cases returning `T | DomainError`, check `if (result instanceof DomainError) throw result` at this delivery boundary.
- Success documentation uses `@ZodResponse({ status, description, type })`; errors use `@ApiResponse({ status: 4xx, type: JSendFailDto })`.
- Define JSend DTOs at file top: `class JSendXDto extends createZodDto(jsendSuccess(xSchema)) {}`. Serialization is controller-owned, not business-operation-owned.

### Composition

`infrastructure/{module}.module.ts`, never module root; no service facade. Repository factory: `{ provide: X_REPOSITORY, useFactory: (db) => new XRepository(db), inject: [DATABASE_CONNECTION] }`. Use-case factory: `{ provide: XUseCase, useFactory: (repo) => new XUseCase(repo), inject: [X_REPOSITORY] }`. No `@Injectable()` on operation or repository classes.

## Imports and language conventions

Every source/test layer follows this import rule: same-directory `./sibling` imports are allowed; all non-sibling imports use tsconfig aliases (`@tasks/...`, `@shared/...`, `@database/...`, `@repo/...`). Parent traversal (`../`, `../../`) and cross-folder `./subfolder/...` imports are forbidden. No NestJS `NotFoundException` in repositories or operations, no root controller/module, no service facade.

## Testing and runtime boundaries

Read `architecture/testing/architecture.md` and `architecture/testing/stacks/typescript.md`. Testing owns operation, repository, parser, and HTTP test boundaries and concrete doubles. Runtime specs retain file routing, scope, review, after-edit gates, execution, and uncertainty procedures.

## Obligation mapping

| Obligation | Concrete mapping | Applicability or uncovered decision |
|---|---|---|
| C1 Layers/dependencies | Structure | Framework code only in infrastructure. |
| C2 Domain/ports | Domain and ports | Entities, Symbol ports, centralized errors. |
| C3 Operation | Application operations | Undecorated class with interface injection. |
| C4 Mapping/composition | Adapters; Composition | Static mapping plus factory providers. |
| C5 Failures | Application operations; Controllers | Null → returned error → delivery throw. |
| C6 Serialization | Controllers | JSend DTO/response edge. |
| C7 Helpers | Common contract | No artificial class wrapper for a pure helper. |
| B1 Layout/domain | Structure; Domain and ports | Readonly fields, getters, factory, null lookup. |
| B2 Operation | Application operations | Null policy in operation. |
| B3 Infrastructure | Adapters and delivery | Repository port, static mapper, edge factories. |

## Open decisions

None identified for this mapping.
<!-- core:end -->

<!-- project:begin -->
## Project extensions
<!-- project:end -->
