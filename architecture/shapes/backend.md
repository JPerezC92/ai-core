# Backend application shape

## Applicability

Backend business applications. Read `architecture/clean-architecture.md` first. This shape owns backend layout and responsibility details; the stack guide supplies language/framework syntax.

## B1 — Layout and domain

Use `domain/` (entities, ports, errors), `application/` (one file per use case), and `infrastructure/` (adapters, repositories, composition). A stack names the concrete operation location. Entities have immutable identity fields, a read accessor per field, and a factory building valid instances. An entity's behavior enforces its own invariants, and no public setter or writable identity field is permitted. Ports return domain entities, not storage records. A missing lookup returns an empty result, never throws.

## B2 — Operation

The use case checks an empty port result and decides which domain error to return. Common single-`execute()`, domain-only imports, injection, and returned-failure rules apply.

## B3 — Infrastructure and delivery

A repository implements its domain port and contains no business rules. Adapters use one outside-record-to-entity mapping function. Composition wires adapters to use cases at the edge; controllers/handlers serialize results there, not in the operation.

## Testing selection

Read `architecture/testing/architecture.md` and its applicable stack guide for operation, adapter, and assembled-entry-point tests.
