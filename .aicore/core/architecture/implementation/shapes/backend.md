# Backend application shape

## Applicability

Backend business applications. Read `.aicore/core/architecture/implementation/architecture.md` first. Statement-layer ownership is defined in `.aicore/core/architecture/README.md` → `## Content model`. The layout and operation obligations below bind at L3 (`C11`); at L1 and L2 no layer folder and no operation form is imposed, and each obligation binds only where its responsibility exists.

## B1 — Layout and domain

Use `domain/` (C8 model kinds and ports), `application/` (one file per use case), and `infrastructure/` (adapters, repositories, composition). `infrastructure/adapters/` holds the adapter and outside-record-to-domain mapping modules and `infrastructure/repositories/` holds repository adapters; a directory is created only where its responsibility exists. A stack names the concrete operation location. Entities have a read accessor per field, preserving C8 alias protection. Port results follow C9: aggregate objects for repositories, domain projections for read ports, and appropriate domain types for other capabilities.

The controller and its request/response mapping carry the Interface responsibility (C12) and sit inside `infrastructure/` beside the adapters, isolated from them: a controller depends on application and domain modules and imports no repository, persistence adapter or IO helper, whatever folder they share (C13). Where C13's evidence authorizes an independent folder, it is `interfaces/` at the same level as the layer folders. A published JSON API's response contract follows the external output contract (C14); the envelope is transport-owned by the controller (`C6`, `C12`).

## B2 — Operation

The use case checks an empty port result and decides which domain error to return. Common single-`execute()`, domain-only imports, injection, and returned-failure rules apply.

## B3 — Infrastructure and delivery

A repository implements its domain port (C9) in `infrastructure/repositories/`. Adapters use one explicit outside-record-to-domain mapping function in `infrastructure/adapters/` (C4, C6), selecting reconstitution for persisted entities (C8). Persistence rows/models live in infrastructure; request/response records at its delivery edge (C10).

## B4 — Business-owned domain organization

Organize domain by nearest business ownership. An aggregate's named folder contains its root, children, owned value objects, events and repository port logically beside the root. A root-only aggregate needs no artificial child folders. One entity per file, including children; one rule-bearing type per module. No multi-concept `entities`, `models` or `value_objects` module buckets.

When a second module of a role exists at the same ownership level, introduce that role's subfolder there. Within an aggregate, `entities/`, `value-objects/`, `events/` or `repositories/` remain inside its folder; never move owned parts to global role buckets. Shared concepts use their nearest genuine business owner rather than arbitrary duplication. Guides spell native folder/file names using C10.

Review entities against C8: identify the invariant-enforcing behavior and legal transitions, or the owning root behavior for children; inspect construction, accessors and nested aliases for bypasses. A set of getters plus `create()` is not evidence of behavior. Apply C9 to repository scope and transaction ownership, not table-shaped convenience APIs.

## Testing selection

Read `.aicore/core/architecture/testing/architecture.md` and its applicable stack guide for operation, adapter, and assembled-entry-point tests.
