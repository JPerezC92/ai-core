# Backend application shape

## Applicability

Backend business applications. Read `architecture/implementation/architecture.md` first. Statement-layer ownership is defined in `architecture/README.md` → `## Content model`.

## B1 — Layout and domain

Use `domain/` (entities, ports, errors), `application/` (one file per use case), and `infrastructure/` (adapters, repositories, composition). A stack names the concrete operation location. Entities have a read accessor per field (`C2`). Ports return domain entities, not storage records. A missing lookup returns an empty result, never throws.

## B2 — Operation

The use case checks an empty port result and decides which domain error to return. Common single-`execute()`, domain-only imports, injection, and returned-failure rules apply.

## B3 — Infrastructure and delivery

A repository implements its domain port. Adapters use one outside-record-to-entity mapping function (`C4`, `C6`).

## Testing selection

Read `architecture/testing/architecture.md` and its applicable stack guide for operation, adapter, and assembled-entry-point tests.
