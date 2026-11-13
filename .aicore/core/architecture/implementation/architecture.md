# Clean architecture

## Purpose and authority

Statement-layer ownership is defined in `.aicore/core/architecture/README.md` → `## Content model`. These are intended architecture decisions, not evidence that existing code conforms. Documentation approval and implementation verification are separate.

## C1 — Layers and dependencies

The same layers apply across languages: domain, application, infrastructure; static dependencies point inward, infrastructure → application → domain. A language or library is never a layer and cannot suspend this contract. Shape-specific folders bind these responsibilities without renaming the layers. The application imports only domain types and ports, never frameworks or concrete adapters. Runtime effects through injected domain ports are allowed: a runtime call graph is not the static-import graph.

## C2 — Domain and ports

Domain imports no framework or infrastructure. Entities and typed ports speak domain types, not raw external records. Domain business errors carry stable codes and messages. Concrete entity representation and port syntax belong in the selected shape/stack guide.

Entity representation and state changes follow C8; data-only records and functional domain modules remain distinct valid representations.

## C3 — Application operation

Each use case is one named business operation exposing a single `execute()`. It depends on injected domain ports, not concrete IO.

Every use case is a class in every language: a standalone function never stands in for a use-case class, however small the operation is. The class exposes one `execute()` and receives its required collaborators through constructor injection. Class-first does not license abstraction for its own sake: add no base class, interface, inheritance hierarchy, forwarding service layer or pass-through wrapper without a real polymorphic or behavioural need, and a helper, utility or other module-level function that is not an application operation stays a function. Presentation-layer components, hooks and general-purpose utilities are not use cases and are not made classes by this rule.

One operation per module or file; its name states a business outcome, and `Service`, `Manager`, `Helper`, `Processor`, and `Util` are not use-case names. A composition root or CLI router may wire several operations but must not re-declare a use-case class. Policy belongs here or in domain, never in adapters or presentation. Data-only boundary/result records and functional domain modules are valid representations; enduring invariants and legal transitions belong in the domain, application-specific orchestration may stay in the use case, and adapters hold no business policy. A data-only record is anemic only when it claims to be the domain model while allowing public mutation and its rules are enforced elsewhere.

## C4 — Mapping and composition

Adapters map outside data to domain data through a single mapping/parsing step and contain no business rules. Composition supplies concrete adapters to use cases only at the edge.

The split between domain and infrastructure is decided by who owns the rule, not by the fact that data changes shape. A transformation that is itself a business rule — the rule that decides the outcome — belongs in the domain; application-specific orchestration that applies such a rule stays in the use case (C3). A transformation between an external representation and domain data — a persistence record, a transport payload, a third-party response — belongs at the infrastructure boundary that owns that representation. Neither side hosts the other's rule, and infrastructure-specific mapping never enters a domain entity.

## C5 — Failures

A business failure is a typed domain error returned as a value, never thrown by the business operation. Boundary exceptions (framework/transport) and programming exceptions (including IO crashes) remain exceptions; do not fabricate domain errors from arbitrary caught exceptions or impose exception-as-result wrappers. A documented business-failure response may be mapped to the corresponding domain error. Presentation may bind returned business errors and propagated exceptions to its error channel without reclassifying them.

## C6 — Serialization

Business operations consume and return domain types. Transport serialization belongs to the delivery edge (controller/handler/view), never inside `execute()`.

## C7 — Pure helpers

A pure helper needs no artificial use-case wrapper. A module that decides policy and calls infrastructure does need the application-operation boundary.

## C8 — Domain model and legal change

Classify a type by identity, equality, invariant ownership, legal transitions and effects, not its name or the presence of a class declaration:

| Kind | Classification and obligations |
|---|---|
| Entity | A class whose stable identity distinguishes instances even when attributes coincide. Its behavior protects enduring invariants and legal changes; a factory creates a valid instance. No public setters or writable identity. A child entity may delegate enforcement to its aggregate root, but no supported child access or construction may bypass that root's invariants. |
| Value object | No independent identity; equality is by constituent values. Immutable and valid at construction, including nested state. Changes produce another valid value. |
| Aggregate | Where used, a consistency boundary containing a root entity and its owned parts. The root is the only mutation entry point and enforces cross-part invariants; other aggregates are referenced by identity, not mutable object ownership. A root alone can form an aggregate. |
| Domain event | Where used, an immutable fact already produced by successful domain behavior, with immutable payload. It is not a command, transport envelope or integration message. |
| Domain service | Domain behavior without a natural entity/value-object owner. Uses domain types and owns domain policy, not application orchestration or concrete IO. It does not provide an escape hatch for moving an entity's invariants to callers. |
| Pure rule module | Cohesive, IO-free domain functions named for their predicate or business calculation. Needs neither artificial entity state nor a service/use-case wrapper (C7). |
| Data-only record | Typed data without a claim to own identity-based behavior or legal transitions. Domain records and read projections are framework-free; storage and transport records belong outside domain. Mutability is determined by the record's use, not an entity label. |
| Port | A domain-owned typed contract for an external capability, expressed in domain types; implementation is outside domain. Repositories, query capabilities, clocks and other service contracts are distinct port roles. A port declaration performs no IO. |
| Domain error | A typed expected business rejection with stable code and message, returned as a value (C5); not a wrapper for unexpected exceptions. |

Entities and value objects may contain public or private methods for domain behaviour, invariant enforcement, business transformations, and domain-native state access. They must not contain methods that map to or from external representations, including JSON or transport payloads, database rows, ORM models, or third-party schemas. Such mapping belongs to the infrastructure adapter or delivery boundary responsible for that representation (C4, C6).

For an entity transition, a named behavior checks the requested change and returns a new valid instance with the same identity or a typed domain error value. The original remains unchanged. Protect the entire owned graph: nested mutable collections, child objects and exposed aliases must not permit caller mutation of either version. Read-only field declarations alone are insufficient. A child may have no separate transition method when its root performs the change and enforces its invariants; this is explicit root ownership, not application-owned rules.

Creation establishes identity and creation eligibility. Reconstitution restores persisted identity and validates applicable state invariants, not today's creation eligibility; it must not replay creation events or effects. Invalid persisted state is unexpected corrupt data, not a business rejection and not permission to coerce state silently (C5). Construction paths and accessors must preserve these protections.

Where events are used, successful behavior carries pending immutable facts on the returned aggregate in an immutable collection with immutable elements; a failed transition creates no success fact. Domain behavior never publishes them. Reconstruction starts without replayed creation facts. Publication and transaction coordination follow C9.

Review asks: which behavior enforces each invariant; which transitions are legal; how are identity, children and nested aliases protected; can construction or exposed data bypass enforcement? Getters and a factory alone do not answer these questions. A publicly mutable domain-named bag with rules in its callers is a record if intentionally data-only, otherwise a nonconforming model, not a compliant entity. Do not invent aggregates, events or rich classes for CRUD, records or pure calculations that do not use them.

## C9 — Repositories, projections and transactions

A repository is a collection-like persistence port for one aggregate-root type, not one instance, table or child. Where aggregate persistence is used, define one repository port per root type; children are loaded and saved through their root. It accepts/returns domain objects and identifiers; absence is an empty lookup result, never an exception. Application policy decides whether absence is a business error. A repository has no business policy and performs no commit. Its infrastructure adapter maps persisted state to a valid reconstituted domain object through the explicit C4 mapping step.

A query port may instead return framework-free, domain-owned read projections without rehydrating aggregates. A projection describes a read use case, not storage layout or transport serialization (C1, C6). Other capability ports need not pretend to be repositories. No port leaks rows, ORM models or delivery payloads. Only explicitly contracted persistence conflicts may map to corresponding typed expected outcomes; arbitrary IO, mapping or corrupt-data exceptions retain C5 semantics.

The application coordinates the atomic transaction scope and commit/rollback across involved ports; infrastructure supplies the transaction mechanism. An optional domain-owned unit-of-work port may expose that capability when needed; an existing session/transaction facility may suffice. Never hide commit in a repository or require a custom unit-of-work abstraction. For immutable transitions, explicitly persist the returned replacement; ORM tracking of the unchanged original is not persistence of the new state.

Coordinate successful persistence with event publication outside domain so a failed transaction does not publish success facts. Publishing after commit is ordering, not guaranteed delivery: where reliable delivery is required, specify the persistence/publication strategy and failure handling. No bus, outbox or universal delivery mechanism is mandated. Test doubles remain governed solely by the testing contract.

## C10 — Semantic concept-role naming

Use a business concept plus its actual role, with one shared vocabulary. Classes keep business names such as `Order`, not `OrderEntity`. Shapes own folder placement; guides own language filename syntax. The semantic roles below apply across languages; do not add redundant technical suffixes such as repository-interface or entity-model.

| Role | Concept example and meaning |
|---|---|
| entity | `Order`: identity-bearing model |
| value object | `ShippingAddress`: identity-free value |
| event | `OrderPlaced`: produced domain fact |
| repository | `OrderRepository`: aggregate persistence contract/adapter, distinguished by layer |
| port | `Clock`: other capability contract |
| domain service | `Pricing`: actual ownerless domain behavior |
| policy | `PricingPolicy`: an actual business policy, not a label for every pure function |
| error | `OrderClosed`: expected business rejection |
| row | `OrderRow`: raw persisted shape, infrastructure-owned |
| model | `OrderModel`: persistence/ORM model, infrastructure-owned; never a generic domain model bucket |
| request | `CreateOrderRequest`: action-specific inbound delivery payload |
| response | `OrderResponse`: outbound delivery representation |
| projection | `OrderSummary`: framework-free domain-owned read shape |
| record | A concept-specific intentional data record where no more precise role applies |
| query | A concept-specific read capability port |

Pure functions/modules use the predicate or business calculation they express, without fabricated entity/service roles. Apply roles only to artifacts actually needed; do not create unused requests, wrappers or records to fill a naming table. Boundary records do not become domain-owned because they mention a domain concept: rows/models stay in infrastructure, request/response shapes at delivery. Each maps explicitly to/from domain data under C4–C6, never passing as the domain entity itself.

## Testing and execution

The current test-design authority is `.aicore/core/architecture/testing/architecture.md`, with its selected stack guide. It alone owns test levels, organization, doubles, evidence, and test-guide parity. Agent runtime specs own execution authority, edit scope, checkpoints, review procedures, and uncertainty routing. This document grants none of those permissions.
