# Clean architecture

## Purpose and authority

This contract owns common architecture semantics. Application shapes own responsibility/layout specialization; implementation guides own syntax and library mappings. A language or library is never a layer and cannot suspend this contract. These are intended architecture decisions, not evidence that existing code conforms. Documentation approval and implementation verification are separate.

## C1 — Layers and dependencies

The same layers apply across languages: domain, application, infrastructure; static dependencies point inward, infrastructure → application → domain. Shape-specific folders bind these responsibilities without renaming the layers. The application imports only domain types and ports, never frameworks or concrete adapters. Runtime effects through injected domain ports are allowed: a runtime call graph is not the static-import graph.

## C2 — Domain and ports

Domain imports no framework or infrastructure. Entities and typed ports speak domain types, not raw external records. Domain business errors carry stable codes and messages. Concrete entity representation and port syntax belong in the selected shape/stack guide.

An entity — as distinct from a data-only record or a functional domain module — is a class with behavior that enforces its invariants, an immutable identity, and a factory that builds a valid instance; it exposes no public setters and no writable identity field. No state-transition convention is selected: do not add setters to enable state change.

## C3 — Application operation

Each use case is one named business operation exposing a single `execute()`. It depends on injected domain ports, not concrete IO. One operation per module or file; its name states a business outcome, and `Service`, `Manager`, `Helper`, `Processor`, and `Util` are not use-case names. Choose one operation shape per stack and apply it to every use case; a mixed vocabulary is a review finding. A composition root or CLI router may wire several operations but must not re-declare a use-case class. Policy belongs here or in domain, never in adapters or presentation. Data-only boundary/result records and functional domain modules are valid representations; enduring invariants and legal transitions belong in the domain, application-specific orchestration may stay in the use case, and adapters hold no business policy. A data-only record is anemic only when it claims to be the domain model while allowing public mutation and its rules are enforced elsewhere.

## C4 — Mapping and composition

Adapters map outside data to domain data through a single mapping/parsing step and contain no business rules. Composition supplies concrete adapters to use cases only at the edge.

## C5 — Failures

A business failure is a typed domain error returned as a value, never thrown by the business operation. Boundary exceptions (framework/transport) and programming exceptions (including IO crashes) remain exceptions; do not fabricate domain errors from arbitrary caught exceptions or impose exception-as-result wrappers. A documented business-failure response may be mapped to the corresponding domain error. Presentation may bind returned business errors and propagated exceptions to its error channel without reclassifying them.

## C6 — Serialization

Business operations consume and return domain types. Transport serialization belongs to the delivery edge (controller/handler/view), never inside `execute()`.

## C7 — Pure helpers

A pure helper needs no artificial use-case wrapper. A module that decides policy and calls infrastructure does need the application-operation boundary.

## Testing and execution

The current test-design authority is `architecture/testing/architecture.md`, with its selected stack guide. It alone owns test levels, organization, doubles, evidence, and test-guide parity. Agent runtime specs own execution authority, edit scope, checkpoints, review procedures, and uncertainty routing. This document grants none of those permissions.
