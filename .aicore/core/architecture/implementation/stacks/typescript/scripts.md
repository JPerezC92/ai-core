# TypeScript scripts implementation guide

> **Status:** proposed
> **Reviewed:** pending

## Applicability and ownership

Applies to TypeScript and TSX scripts, CLIs, tooling packages and MCP servers that implement the scripts shape (`P1`–`P4`), including independently deployed tooling packages and feature-scoped skill scripts. A tooling package that also serves a backend application reads `.aicore/core/architecture/implementation/shapes/backend.md` as well; a browser user interface is not covered here and belongs to `.aicore/core/architecture/implementation/stacks/typescript/react.md`. Read `.aicore/core/architecture/implementation/architecture.md` and `.aicore/core/architecture/implementation/shapes/scripts.md` first. The Node.js runtime and a TypeScript compiler are the reference toolchain for the examples below, not destination bindings (`.aicore/core/architecture/README.md` → `## Contract boundaries`). No web framework, bundler, test runner or package manager is selected by this guide. Exact-path execution and edit authorization remains runtime-owned. Documentation review does not prove code conformance.

## Structure and dependency mapping

For `C1`/`C2`/`P1`, source modules map to `src/domain/`, `src/application/` and `src/infrastructure/`: data-only constants and pure transformations in `domain/`; one operation per module in `application/`; adapters, clients, loaders and repositories in `infrastructure/`, with outside-record-to-domain mapping modules under `infrastructure/adapters/` and repository adapters under `infrastructure/repositories/`. A directory exists only where its responsibility exists. The composition and entry module is `src/index.ts` or `src/main.ts`; wiring and handler conversion are illustrated under Adapters and delivery (`C4`, `C6`).

For `P4`, group domain modules by business concept. A compact aggregate may use `domain/order/order.entity.ts`, `order.repository.ts` and `shipping-address.value-object.ts`; a second entity module moves root and child modules into `domain/order/entities/`, and the port stays logically beside its root. A functional domain can instead use `domain/pricing/calculate-price.ts`. Boundary records keep the same ownership split: `infrastructure/` holds the storage-facing row and model records (`order.row.ts`, `order.model.ts`) while the delivery channel owns its request and response records (`create-order.request.ts`, `order.response.ts`), and domain read projections stay framework-free. These paths stay within `P3`'s deployment zone.

For `C12`/`C13`, the entry module is the composition root and may import concrete adapters; the delivery handler parses the channel input, maps it once, delegates to an operation and serializes the result without holding the decision. At L3 the handler imports no concrete adapter or IO helper even when both live under `infrastructure/`; an authorized independent folder is `interfaces/`. At L1 and L2 a script keeps its own organization, needs no layer folder and no operation class, and may orchestrate its effects directly (`C11`).

## Domain and ports

- Data-only constants modules contain exported `const` declarations and no functions, classes or IO; transformations are typed functions such as `calculatePrice(lines: readonly OrderLine[]): Money` (`P1`, `C7`).
- A `C8` entity is a class whose stored fields are runtime-private (`#id`) or held behind a private constructor with read-only accessors; the TypeScript `private` modifier is erased at runtime and alone does not protect state. A transition returns a same-identity replacement union such as `Order | OrderClosedError`. `readonly` and `ReadonlyArray` are compile-time only, so a mutable collection accepted as input is copied (`[...items]`) or frozen at construction, and an exposed collection is returned as a copy or frozen value.
- Factories are distinct static `create(...)` and `reconstitute(...)` methods; reconstitution validates stored state without replaying creation, and an unexpected invalid stored value follows a thrown exception rather than entering the annotated business-error union (`C5`, `C8`).
- Value objects implement their own equality over constituent values; events are immutable payload objects, and pending events live on the replacement aggregate as a readonly collection initialised empty by `reconstitute` (`C8`).
- Capability signatures are interfaces, for example `interface OrderRepository { findById(id: OrderId): Promise<Order | null> }`, `interface OrderQueries { summary(id: OrderId): Promise<OrderSummary | null> }` and `interface Clock { now(): Instant }`; the empty lookup is `null`, and a domain projection type carries read results (`C9`). A dependency-injection token is a `Symbol` only where a runtime container requires one.
- Business errors are classes or discriminated records carrying a stable `code` and `message` (`C2`, `C5`). Structured intermediate data uses a declared interface or type alias, never an untyped record.

## Application operations

For `C3`/`C5`, at L3 (`C11`) each application operation is a class in `application/<verb>-<object>.ts` named `<Verb><Object>` with no `UseCase` suffix, exposing one typed `execute()` and receiving its ports through constructor injection. Its return type is a domain result or error union such as `Order | OrderClosedError`. It imports no concrete adapter, IO helper or framework, has no base class, and holds no business rule that belongs to the domain. A pure helper that is not an operation stays an ordinary function (`C7`).

For `C9`, an operation reads the port, decides on absence (`if (order === null) return new OrderNotFoundError(id)`), narrows the transition result with a type guard such as `isOrderClosedError(result)`, and passes the successful replacement to `save`. Where a transaction capability exists it is an injected port whose adapter owns the concrete transaction in `infrastructure/`; the application coordinates the call and does not begin one itself.

## Adapters and delivery

For `C4`, an adapter in `infrastructure/adapters/` maps outside data to domain data, for example `orderFromRow(row: OrderRow): Order` returning `Order.reconstitute(...)`, and the repository adapter that uses the storage record lives in `infrastructure/repositories/`. These mapping functions carry no business rule: the rule that decides an outcome stays in the domain or the operation.

For `C5`/`C6`/`C14`, the handler converts a channel payload to operation parameters and the operation result to the channel's published representation, performing one mapping step and no business decision. A CLI entry writes its single machine-readable document to standard output, writes diagnostics to standard error, and sets a non-zero exit status through `process.exitCode`; an MCP entry returns its tool result shape; an HTTP entry keeps its own response contract. Serialization is an explicit conversion, not a framework hook; no serializer is selected here.

For `C4` composition, the entry module constructs the concrete adapter and passes it to the operation constructor, then invokes the handler. Composition is permitted only at that point; every other module receives ready collaborators (`C12`).

## Imports and language conventions

### Deployment zones

- Each deployment package is self-contained with its own `package.json` and `tsconfig.json`. A package never imports another deployment package's source, build output or internal alias namespace; where one package consumes another, the consumer declares it as a dependency and addresses it through that package's published entry points (`P3`, `C1`).
- A deployment zone that is also published declares its public surface in `exports`, with a type condition and a runtime condition, and publishes no deep path into its internal layout.
- Feature-scoped skill scripts keep their own dependency declaration and alias namespace and are not reached by another zone's internal specifiers. Exact-path execution authority remains runtime-owned.

### Specifier scope

Three kinds of specifier are never conflated.

1. **Internal references** name a module of the same package — a relative specifier that stays in the importing module's directory or descends into one of that directory's child directories, or a private package alias — and are not addressable from outside that package.
2. **Declared external dependencies** are runtime built-in modules, third-party packages and other workspace packages; they are named by the dependency identity the manifest declares and resolved through that dependency's published entry points, never through the importing package's private alias map and never through a filesystem path into another package's tree.
3. **The package's public surface** is exactly what `exports` publishes; adding a public entry point is an `exports` change, not an alias change.

### Source extensions and the alias mechanism

- A specifier that names a project file carries its source extension — `.ts`, `.tsx`, `.mts`, `.cts` — on relative and aliased references alike. Parent-directory traversal (`../`) is not used. A relative specifier may stay in the importing module's directory or descend into a child directory of that directory; a private alias remains the preferred form where it makes a cross-directory or cross-layer reference clearer, and a reference that would otherwise depend on the importing file's depth goes through the package's declared mechanism. Neither form authorizes a dependency the architecture forbids: the direction permitted between layers and zones is governed by the common contract and the applicable shape, not by the syntax of the specifier, so a relative child-directory import is not by itself a boundary violation. A language- or framework-specific guide may impose a stricter import convention for the shape it covers.
- One alias mechanism per package, declared in the package's own `package.json` `imports` map under `#` keys, is the recommended concrete mechanism: the compiler resolves that map from the manifest, and a runtime or bundler resolves it only where that runtime or bundler actually supports the resolution. Where a runtime or bundler requires additional resolver configuration, that configuration is supplied explicitly and validated; a passing type check is not evidence that the runtime resolves the alias.
- Two map shapes are usable and are not mixed inside one package: an extensionless key where the extension arrives in the specifier (`"#domain/*": "./src/domain/*"` resolving `#domain/constants.ts`), or a key carrying the `.ts` trailer where the extension arrives in the target (`"#domain/*.ts": "./src/domain/*.ts"`).
- A directly executed package points its map at source files. A compiled package points it at build output using the trailer form (`"#domain/*.ts": "./dist/domain/*.js"`), because a compiled target must not receive the source extension; with `rootDir` and `outDir` corresponding to the source and output layout, the compiler maps that compiled target back to the source file, so type checking does not require a build first.

### Production modes

| Mode             | Relative specifiers            | Private aliases                          | Emitted output                    |
| ---------------- | ------------------------------ | ---------------------------------------- | --------------------------------- |
| Direct execution | `./x.ts`; `tsc` runs `noEmit`  | map targets source                       | none; the runtime strips types    |
| Bundled          | `./x.ts`, `./x.tsx`            | map targets source; bundler must resolve | bundler output                    |
| Compiled         | `./x.ts` rewritten to `./x.js` | map key carries `.ts`; targets output    | JavaScript, declarations and maps |

Three consequences follow. A directly executed package needs no build step and no additional loader, and `.tsx` is not executable that way at all, so JSX belongs only to bundled code. A bundled package may use `.tsx` and may use native aliases only where its bundler resolves them without a further resolver. A compiled package enables `rewriteRelativeImportExtensions` so relative `.ts` specifiers become `.js` while `#` specifiers stay verbatim; it does not need `allowImportingTsExtensions`, and its emitted declarations keep both forms and resolve against their sibling declaration files, so the package does not have to ship sources.

### Alias permission

A compiler `paths` alias is permitted only where the selected build or runtime pipeline actually resolves it. A passing type check does not establish that: a runtime resolves package manifests, not compiler aliases, and a bundler resolves them only when its own configuration mirrors them. A project that cannot demonstrate resolution in the pipeline it ships keeps the package-manifest mechanism instead. A cross-package dependency is never expressed as a compiler alias.

### Concept-role filenames

`C10`'s TypeScript spelling is the shared table at `.aicore/core/architecture/implementation/stacks/typescript/nestjs.md` → `Concept-role filenames`, which this guide cites rather than duplicating. That table supplies filenames only; it selects no framework and grants no backend architecture here.

## Testing and runtime boundaries

Read `.aicore/core/architecture/testing/architecture.md` and `.aicore/core/architecture/testing/stacks/typescript.md`; they own unit, integration and entry-point boundaries, fixtures, isolation and doubles. This guide adds no test rule. Execution authority, edit scope, gates, dependency ownership and uncertainty handling stay in agent runtimes, and a test-runner dependency remains separate from runtime dependencies under the applicable dependency procedure.

## Obligation mapping

| Obligation                     | Concrete mapping                                                    | Applicability or uncovered decision                                                                                                                                           |
| ------------------------------ | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| C1 Layers/dependencies         | Structure and dependency mapping; Deployment zones; Specifier scope | Layer modules with inward-facing static imports; a public entry point is the only cross-package edge.                                                                         |
| C2 Domain/ports                | Domain and ports                                                    | Runtime-private storage, factory methods, interfaces as capability contracts, typed error objects.                                                                            |
| C3 Operation                   | Application operations                                              | One class per operation with `execute()`, constructor-injected ports, no base class; the class rule binds only at L3.                                                         |
| C4 Mapping/composition         | Adapters and delivery                                               | Mapping functions without business rules, composition in the entry module, one mapping step at the boundary.                                                                  |
| C5 Failures                    | Application operations; Adapters and delivery                       | Result-or-error unions narrowed by a type guard; expected failures returned, unexpected exceptions left as exceptions.                                                        |
| C6 Serialization               | Adapters and delivery                                               | Explicit conversion to the channel's representation; no dependency on a serializer is selected.                                                                               |
| C7 Helpers                     | Domain and ports; Application operations                            | Plain typed functions for predicates and calculations; no wrapper type is introduced.                                                                                         |
| C8 Domain model                | Domain and ports                                                    | Same-identity replacement unions, copied or frozen collections, `create`/`reconstitute`, readonly event payloads, value equality.                                             |
| C9 Repositories/transactions   | Domain and ports; Application operations                            | Port interfaces with `Promise` results, `null` for an empty lookup, replacement save, injected transaction capability where one exists.                                       |
| C10 Naming                     | Concept-role filenames                                              | Cites the shared TypeScript role table; this guide introduces no second vocabulary.                                                                                           |
| C11 Complexity level           | Applicability and ownership; Structure and dependency mapping       | L1 and L2 impose no layer folder and no operation class; layer and operation obligations bind at L3.                                                                          |
| C12 Interface boundary         | Structure and dependency mapping; Adapters and delivery             | The entry module composes; the handler parses, maps once, delegates and serializes without holding the decision.                                                              |
| C13 Interface placement        | Structure and dependency mapping                                    | The handler stays beside the adapters importing none of them; an independent `interfaces/` folder exists only where the contract authorizes it.                               |
| C14 External output contracts  | Adapters and delivery                                               | A CLI entry writes one document to standard output, diagnostics to standard error and a non-zero exit status on failure; MCP and HTTP entries keep their own published shape. |
| P1 Responsibilities            | Structure and dependency mapping; Domain and ports                  | Data-only constants and typed pure transformations.                                                                                                                           |
| P2 IO and delivery             | Adapters and delivery                                               | Named IO helpers in infrastructure; the entry module assembles them.                                                                                                          |
| P3 Deployment boundaries       | Imports and language conventions → Deployment zones                 | Self-contained packages; cross-package references only through published entry points.                                                                                        |
| P4 Business-owned organization | Structure and dependency mapping; Concept-role filenames            | Concept-owned domain folders with role-suffixed filenames; functional modules retained.                                                                                       |
| B1–B4 Backend shape            | Not mapped here                                                     | This guide covers the scripts shape; the backend shape is mapped by the NestJS reference guide, not inferred from this one.                                                   |
| F1–F4 Frontend shape           | Not mapped here                                                     | A browser user interface belongs to the React reference guide; no Hook, component or browser transport equivalent is invented here.                                           |

## Open decisions

1. Which map shape a project adopts — extensionless key or `.ts`-trailered key — is a project choice; this guide permits either and forbids mixing both in one package.
2. Whether a scripts package is bundled, compiled or directly executed is a project decision that follows its distribution mode; this guide states the requirement for each mode and selects none.
3. No bundler, package manager, monorepo orchestrator, serializer or dependency-injection container is selected. A project that adopts one documents the resolution it actually provides, because an alias is permitted only where its pipeline resolves it.
