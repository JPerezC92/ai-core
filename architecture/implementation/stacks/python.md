# Python implementation guide

> **Status:** reference
> **Reviewed:** documentation only; implementation conformance not assessed

## Applicability and ownership

Applies to Python backend tooling packages, standalone ticket tooling, and exactly assigned feature-scoped skill scripts; not an inferred browser/UI or web-framework architecture (P3). Read `architecture/implementation/architecture.md`, `architecture/implementation/shapes/scripts.md`, and, for backend applications, `architecture/implementation/shapes/backend.md`. Pydantic v2 and client examples below preserve existing reference choices, not destination tool bindings (`architecture/README.md` → `## Contract boundaries`). Exact-path execution/edit authorization remains runtime-owned. Documentation review does not prove code conformance.

## Structure and dependency mapping

Domain: data-only constant modules and pure transformation functions; ordinary framework-free classes for backend entities; ports declared as `Protocol` or `ABC`; typed stable-code domain errors (C2). Dataclasses or Pydantic models remain available for other roles, including DTOs, configuration, and non-backend-entity data (C2). Application: the module holding the named `execute()` operation. Infrastructure: loaders/builders/clients implementing ports, IO, and outside-data mapping. Composition/delivery: script or server `main.py` constructs adapters and calls the operation, then serializes domain results/errors (C4, C6).

## Domain and ports

- Transformations receive typed data rather than a filesystem path they open themselves. Constants modules contain only data: no functions, classes, or IO; put logic in another module (P1).
- Backend entities are ordinary framework-free domain classes with internal underscore-prefixed field storage. Each field has a read-only `@property`, matching the TypeScript per-field getters; expose no property setters or public writable identity fields. Identity remains immutable through the entity's supported operations. Underscore storage is an internal-access convention, not enforced privacy or proof of immutability; preserve identity rather than relying on that spelling alone. This does not impose universal frozen fields (B1, C2).
- Each backend entity exposes `@classmethod create(...)`, mapping the TypeScript static `create()` factory to Python class construction. The factory builds a valid instance by enforcing the entity's existing domain validity rules; this mapping introduces no new validity rules, error semantics, or constructor-access mechanism. Backend entities depend on neither Pydantic nor another framework; this representation choice does not ban dataclasses/Pydantic in unrelated roles (C2, B1).
- `Protocol`/`ABC` ports speak domain types; typed business errors carry stable codes/messages, not arbitrary exceptions (C2).
- Structured intermediate data uses `TypedDict` or the project's equivalent, not untyped `dict` (P1).
- An entity is a class with `create()` and behavior. `TypedDict` is structured intermediate or record data, not an entity; do not place behaviorless TypedDicts in `entities.py` (C2).

### Pydantic models

These conventions apply where Pydantic is used outside the backend-entity role; they do not mandate its adoption.

Use `ConfigDict(...)`, never legacy inner `class Config`. Constraints use `Field(min_length=...)`/`Field(alias=...)`, not ad-hoc `__init__` overrides. Validators use `@field_validator("name")` with `@classmethod`, not v1 `@validator`. Parse with `Model.model_validate(data)`, not `.parse_obj()`. Every nested structure with at least two fields has a sub-model, not `dict[str, Any]` plus inline key access. Closed schemas use `extra="forbid"`; only explicitly open sub-models use `extra="allow"`, with the reason in their docstring. Each model has a one-line descriptive docstring. The permitted model representation does not license framework-dependent business operations (C2).

## Application operations

One named operation exposes one `execute()`, takes typed parameters and injected domain IO ports, and returns a typed domain result/error, never raises for business failures (C3, C5). The operation module is `application/<verb>_<object>.py`, exposing one public `execute()`; a class is used only when state or injected collaborators justify it, is named `<Verb><Object>`, and carries no `UseCase` suffix (B2). It imports no concrete client/builder or filesystem/network library. Async operation binding is a destination/local choice where specified, not a universal rewrite of every pure function.

## Adapters and delivery

Concrete `open`, `Path.read_text`, `glob`, network libraries, and subprocess effects live in infrastructure IO helpers or the entry point, never domain/application. Loader/builder/client adapters map outside data into domain objects without business rules. The entry constructs adapters; its delivery handler serializes the domain result/error (for example to JSON), outside `execute()` (P2). Python has no React Query binding or NestJS controller requirement: a CLI/service handler is the relevant delivery edge.

## Imports and language conventions

### Deployment zones

- Each backend tooling deployment package is self-contained with its own `__init__.py`. No imports across these packages, including shared-code imports. Within an allowed deployment zone, same-package sibling imports may use `from .sibling import ...`; imports from any other package use absolute package paths. Parent-relative `..` traversal is prohibited. Absolute spelling does not permit otherwise forbidden cross-zone or cross-deployment-package imports (P3, C1).
- Standalone ticket scripts have no `__init__.py`; `sys.path.insert(0, str(ROOT))` plus sibling-name import is the established accepted convention. Ticket and backend tooling zones must not import one another.
- Feature-scoped skill scripts do not import ticket/backend tooling zones. No `from mcp_servers import ...` cross-zone imports. Feature scope and after-edit reviewer obligations remain runtime-owned.
- A feature-scoped skill-script package carries `__init__.py` at its package root and in each layer directory. A test-only directory directly under the skill's `scripts/` directory (for example each skill's `scripts/e2e/`) carries none, because the same top-level directory name repeated across skills would shadow another skill's package; a test-only directory nested inside a uniquely named package keeps its initializer, since the parent-qualified name is unique. This is a structural convention, not a packaging or distribution claim.
- Entry-point exemption (OQ5): `sys.path.insert(0, ...)` in entry scripts and server `main.py` is accepted startup convention, not a module-boundary/parent-traversal violation (P3).

### Typing and modules

Every function has parameter and return annotations; no untyped parameters or bare `-> None` where a meaningful type exists. `Optional[X]` and `X | None` are both accepted: choose one style per file and do not mix in one signature. Require `from __future__ import annotations` where forward references are used. No wildcard imports. Each file has a module docstring of at least one sentence. No inline credential strings or hardcoded paths; use `Path(__file__).parent`, environment variables, or constants modules.

## Testing and runtime boundaries

Read `architecture/testing/architecture.md` and `architecture/testing/stacks/python.md`; they own unit/integration/entry-point boundaries, factories, isolation, discovery, and doubles. Python test files retain both language-owner and test-owner gates in runtimes; guides do not grant execution or select destination commands. Test-runner dependencies remain separate from runtime dependencies under the applicable runtime/dependency procedure.

## Obligation mapping

| Obligation | Concrete mapping | Applicability or uncovered decision |
|---|---|---|
| C1 Layers/dependencies | Structure; Adapters and delivery | Python modules implement the same inward dependency graph. |
| C2 Domain/ports | Domain and ports | Framework-free backend classes with behavior and immutable identity, underscore storage, read-only `@property`, `@classmethod create`; Protocol/ABC ports. |
| C3 Operation | Application operations | Typed callable with injected ports, no invented framework class. |
| C4 Mapping/composition | Adapters and delivery | Loaders/builders/clients and entry wiring. |
| C5 Failures | Application operations; delivery | Typed returned errors; exceptions remain exceptions. |
| C6 Serialization | Adapters and delivery | CLI/service handler, not business JSON serialization. |
| C7 Helpers | Application operations | Typed pure transformations need no wrapper. |
| P1 Responsibilities | Structure; Domain; Application | Data-only constants and typed transformations. |
| P2 IO/delivery | Adapters and delivery | Explicit IO helpers and assembled entry. |
| P3 Deployment | Deployment zones | Three independent zones and startup exceptions. |
| B1 Backend domain/layout | Structure; Domain and ports | Backend layout, per-field read accessors, port returning domain entities, and empty-result lookup preserved. |
| B2 Backend operation | Application operations | Policy decides empty-result failure. |
| B3 Backend infrastructure | Adapters and delivery | Single mapping and edge wiring, no mandatory NestJS factories. |
| F1–F3 Frontend shape | Not selected | This guide covers CLI/backend, not a Python UI runtime; no Hook/toast equivalent invented. |

## Open decisions

1. No Python HTTP framework, repository library, error registry layout, or serializer framework was selected in the source. A future selected adapter needs its documented mapping; CLI delivery is not an unexplained substitute for a web framework.
