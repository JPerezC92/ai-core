# Python implementation guide

> **Status:** reference
> **Reviewed:** documentation only; implementation conformance not assessed

## Applicability and ownership

Applies to Python backend tooling packages, standalone ticket tooling, and exactly assigned feature-scoped skill scripts; not an inferred browser/UI or web-framework architecture (P3). Read `architecture/implementation/architecture.md`, `architecture/implementation/shapes/scripts.md`, and, for backend applications, `architecture/implementation/shapes/backend.md`. Pydantic v2 and client examples below preserve existing reference choices, not destination tool bindings (`architecture/README.md` → `## Contract boundaries`). Exact-path execution/edit authorization remains runtime-owned. Documentation review does not prove code conformance.

## Structure and dependency mapping

For C1/C2/P1, Python modules map to `domain/`, `application/` and `infrastructure/`: constants and typed functions, ordinary entity classes, and `Protocol`/`ABC` declarations in `domain/`; use-case classes in `application/`; adapters, repositories, loaders, builders and clients in `infrastructure/`. `infrastructure/adapters/` holds the adapter and outside-record-to-domain mapping modules; `infrastructure/repositories/` holds repository adapters implementing a domain port; a loader, builder or client for another external capability sits in `infrastructure/<capability>/`, or directly in `infrastructure/` when it is the only one (B1, P2). Dataclasses or Pydantic models remain available for DTOs, configuration and other non-backend-entity roles. Script/server `main.py` is the Python composition location; constructor wiring and handler conversion are illustrated under Adapters and delivery (C4, C6).

For B4/P4, a compact aggregate may use `domain/order/order_entity.py`, `order_repository.py`, and `shipping_address_value_object.py`. A second entity module moves the root and child modules into `domain/order/entities/`; a second owned value moves value modules into `domain/order/value_objects/`. Apply the same internal growth mapping to `events/`, `repositories/` and other roles. The port stays logically beside its root within `order/`, even when their role folders differ. A functional domain can instead use `domain/pricing/calculate_price.py`; records use concept-specific modules. These paths stay within P3's deployment zone.

## Domain and ports

- P1 transformations use signatures such as `def calculate_price(lines: tuple[OrderLine, ...]) -> Money`. Constants modules contain only data assignments: no functions, classes or IO; function definitions live in another module.
- Backend entities use ordinary Python classes rather than Pydantic models, underscore-prefixed storage and a read-only `@property` per field (B1, C2). A C8 transition can have signature `def close(self) -> Order | OrderClosedError` and construct `Order(self._id, ...)` for its success branch. Store incoming collections with `tuple(items)` when their elements are immutable; a mutable field exposed for reading instead needs a defensive copy. Python underscore spelling offers no access enforcement, and tuple conversion does not freeze mutable elements. These mechanisms implement C8 without prescribing frozen dataclasses for unrelated records.
- Map C8 factories to distinct `@classmethod create(...)` and `@classmethod reconstitute(...)` methods. A shared state-validation helper invoked by `__init__` can cover both entry paths, with creation-only eligibility in `create`. A root method can build replacement child instances internally using that helper. For C5/C8 corrupt-state handling, an unexpected invalid stored value can follow a `raise ValueError(...)` path rather than enter the annotated business-error union; this example does not select a universal exception class.
- `Protocol`/`ABC` capability signatures use annotated parameters and return types; error classes expose typed `code: str` and `message: str` attributes (C2, C5).
- Structured intermediate data uses `TypedDict` or the project's equivalent, not untyped `dict` (P1).
- For C8, value classes implement `__eq__` over their constituent values; `@dataclass(frozen=True)` is one standard-library option for value objects/events, provided nested fields use immutable values rather than mutable `dict`/list aliases. Pending events map to a `tuple[OrderPlaced, ...]` attribute on the replacement aggregate, initialized to `()` by `reconstitute`. `TypedDict` declarations map records/projections; ordinary annotated `def` functions map P1/C7 rules.
- C9 `Protocol`/`ABC` signatures can use `def find_by_id(self, order_id: OrderId) -> Order | None`, `def summary(self, order_id: OrderId) -> OrderSummary | None`, and `def now(self) -> Instant` for a clock port. Asynchronous capabilities use the corresponding `async def` signatures.

### Pydantic models

These conventions apply where Pydantic is used outside the backend-entity role; they do not mandate its adoption.

Use `ConfigDict(...)`, never legacy inner `class Config`. Constraints use `Field(min_length=...)`/`Field(alias=...)`, not ad-hoc `__init__` overrides. Validators use `@field_validator("name")` with `@classmethod`, not v1 `@validator`. Parse with `Model.model_validate(data)`, not `.parse_obj()`. Every nested structure with at least two fields has a sub-model, not `dict[str, Any]` plus inline key access. Closed schemas use `extra="forbid"`; only explicitly open sub-models use `extra="allow"`, with the reason in their docstring. Each model has a one-line descriptive docstring (C2).

## Application operations

For C3/C5/B2, each use case is a class in `application/<verb>_<object>.py`, named `<Verb><Object>` with no `UseCase` suffix, exposing a typed public `execute()` and receiving its ports through constructor injection; a pure helper that is not an application operation remains an ordinary function under C7. Its annotations use domain result/error unions such as `Order | OrderClosedError`. It imports no concrete client/builder or filesystem/network library and extends no base class. Async `execute()` is a destination/local choice where specified, not a universal rewrite of every use case.

For C9/B2, the lookup branch uses `if order is None: return OrderNotFoundError(order_id)`. Bind `replacement = order.close()`, narrow the union with `isinstance(replacement, OrderClosedError)`, and pass the success value to `repository.save(replacement)`. An injected transaction `Protocol` can expose `__enter__`/`__exit__` for a `with transaction:` block or explicit `commit()`/`rollback()` methods. Its implementation accepts a concrete session in infrastructure. An application handoff can read `replacement.pending_events`; the selected publication implementation and its failure handling map C9, not a Python-wide bus choice.

## Adapters and delivery

For C1/P2, the concrete Python IO surface is `open`, `Path.read_text`, `glob`, network-client calls and `subprocess` calls, in infrastructure helper modules or entry code; domain/application imports of those libraries remain prohibited. For C4, `main.py` can wire `repository = OrderRepositoryAdapter(connection)` followed by `operation = CloseOrder(repository)` and then call `operation.execute()`. For C5/C6, a CLI/service handler can narrow `result` with `isinstance(result, OrderClosedError)`, build a response dictionary, then call `json.dumps(response)` if JSON delivery is selected. `json` here is a standard-library illustration, not a serializer/dependency requirement; no React Query or NestJS binding is selected.

For C4/C8–C10, an infrastructure mapping function in `infrastructure/adapters/` can have signature `def order_from_row(row: OrderRow) -> Order` and return `Order.reconstitute(...)`; the repository adapter that uses the `OrderModel` lives in `infrastructure/repositories/` and calls that mapping function. At delivery, `def request_to_parameters(request: CreateOrderRequest) -> CreateOrderParameters` and `def order_to_response(order: Order) -> OrderResponse` illustrate the typed conversions. A query adapter constructs `OrderSummary(...)` or the corresponding `TypedDict` value. These examples select no ORM or serializer framework.

## Imports and language conventions

### Deployment zones

- Each backend tooling deployment package is self-contained with its own `__init__.py`. No imports across these packages, including shared-code imports. Within an allowed deployment zone, same-package sibling imports may use `from .sibling import ...`; imports from any other package use absolute package paths. Parent-relative `..` traversal is prohibited. Absolute spelling does not permit otherwise forbidden cross-zone or cross-deployment-package imports (P3, C1).
- Standalone ticket scripts have no `__init__.py`; `sys.path.insert(0, str(ROOT))` plus sibling-name import is the established accepted convention. Ticket and backend tooling zones must not import one another.
- Feature-scoped skill scripts do not import ticket/backend tooling zones. No `from mcp_servers import ...` cross-zone imports. Feature scope and after-edit reviewer obligations remain runtime-owned.
- A feature-scoped skill-script package carries `__init__.py` at its package root and in each layer directory. A test-only directory directly under the skill's `scripts/` directory (for example each skill's `scripts/e2e/`) carries none, because the same top-level directory name repeated across skills would shadow another skill's package; a test-only directory nested inside a uniquely named package keeps its initializer, since the parent-qualified name is unique. This is a structural convention, not a packaging or distribution claim.
- Entry-point exemption (OQ5): `sys.path.insert(0, ...)` in entry scripts and server `main.py` is accepted startup convention, not a module-boundary/parent-traversal violation (P3).

### Typing and modules

Every function has parameter and return annotations; no untyped parameters or bare `-> None` where a meaningful type exists. `Optional[X]` and `X | None` are both accepted: choose one style per file and do not mix in one signature. Require `from __future__ import annotations` where forward references are used. No wildcard imports. Each file has a module docstring of at least one sentence. No inline credential strings or hardcoded paths; use `Path(__file__).parent`, environment variables, or constants modules.

### Concept-role filenames

Python spells C10's shared role vocabulary as snake_case `<concept>_<role>.py`; role folders use snake_case too (B4/P4).

| C10 role | Python filename |
|---|---|
| entity | `order_entity.py` |
| value object | `shipping_address_value_object.py` |
| event | `order_placed_event.py` |
| repository | `order_repository.py` |
| port | `clock_port.py` |
| domain service | `pricing_domain_service.py` |
| policy | `pricing_policy.py` |
| error | `order_closed_error.py` |
| row | `order_row.py` |
| model | `order_model.py` |
| request | `create_order_request.py` |
| response | `order_response.py` |
| projection | `order_summary_projection.py` |
| record | `order_snapshot_record.py` |
| query | `order_summary_query.py` |

Pure predicates/calculations map to names such as `is_order_eligible.py` or `calculate_price.py` (C7, C10).

## Testing and runtime boundaries

Read `architecture/testing/architecture.md` and `architecture/testing/stacks/python.md`; they own unit/integration/entry-point boundaries, factories, isolation, discovery, and doubles. Python test files retain both language-owner and test-owner gates in runtimes; guides do not grant execution or select destination commands. Test-runner dependencies remain separate from runtime dependencies under the applicable runtime/dependency procedure.

## Obligation mapping

| Obligation | Concrete mapping | Applicability or uncovered decision |
|---|---|---|
| C1 Layers/dependencies | Structure; Adapters and delivery | Layer packages, main.py constructor wiring and Python IO-library import exclusions. |
| C2 Domain/ports | Domain and ports | Ordinary classes, underscore storage, read-only `@property`, `@classmethod create`, Protocol/ABC and typed code/message attributes. |
| C3 Operation | Application operations | One class per operation with `execute()` and constructor-injected ports; no base class, interface or invented framework class. |
| C4 Mapping/composition | Domain and ports; Adapters and delivery | Rule ownership: a business rule lives in a domain module or entity and a use case applies it (C3), while an adapter maps outside data to domain data without business rules. Adapter and mapping modules under `infrastructure/adapters/`, repository adapters under `infrastructure/repositories/`, loaders/builders/clients, and entry wiring. |
| C5 Failures | Application operations; Adapters and delivery; Domain and ports | Union annotations, isinstance narrowing and illustrative ValueError corrupt-state path. |
| C6 Serialization | Adapters and delivery | Handler dictionary conversion and optional standard-library json.dumps. |
| C7 Helpers | Domain and ports; Concept-role filenames | Annotated def functions and predicate/calculation module names. |
| C8 Domain model | Domain and ports | Same-identity replacement, protected nested values, create/reconstitute, tuple events and record/function alternatives. |
| C9 Repositories/transactions | Domain and ports; Application operations; Adapters and delivery | Protocol/ABC aggregate or projection ports, None lookup, explicit replacement save and injected transaction capability. |
| C10 Naming | Concept-role filenames; Adapters and delivery | Snake_case spelling of the shared vocabulary, domain versus boundary records. |
| P1 Responsibilities | Structure; Domain; Application | Data-only constants and typed transformations. |
| P2 IO/delivery | Adapters and delivery | Explicit IO helpers and assembled entry. |
| P3 Deployment | Deployment zones | Three independent zones and startup exceptions. |
| B1 Backend domain/layout | Structure; Domain and ports | Per-field properties; aggregate, projection and other capability results with optional lookup. |
| B2 Backend operation | Application operations | is None branch returns OrderNotFoundError. |
| B3 Backend infrastructure | Adapters and delivery | order_from_row signature, reconstitute call and main.py constructors. |
| B4 Backend organization | Structure and dependency mapping | Aggregate-local role folders and one entity per module. |
| P4 Script organization | Structure and dependency mapping; Concept-role filenames | Business folders inside each deployment zone; functional modules retained. |
| F1–F4 Frontend shape | Not selected | This guide covers CLI/backend, not a Python UI runtime; no Hook/toast equivalent invented. |

## Open decisions

1. No Python HTTP framework, repository library, error registry layout, or serializer framework was selected in the source. A future selected adapter needs its documented mapping; CLI delivery is not an unexplained substitute for a web framework.
