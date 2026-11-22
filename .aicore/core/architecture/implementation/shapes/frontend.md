# Frontend application shape

## Applicability

Feature-oriented frontend applications. Read `.aicore/core/architecture/implementation/architecture.md` first. Statement-layer ownership is defined in `.aicore/core/architecture/README.md` → `## Content model`. The feature layout below binds at L3 (`C11`); at L1 and L2 no feature layer folder is required, while the presentation and data-access separation of `F2` and `F3` binds wherever those responsibilities exist.

## F1 — Feature layout and domain

Use `modules/{feature}/domain/`, `services/`, `hooks/`, and `components/`. Domain defines intentional data-only domain records (not entities), any actual rule-bearing C8 model, service/query ports, and one typed, stable code-bearing business error per feature (C2). Frontend service ports remain applicable even when there is no aggregate persistence repository (C9).

## F2 — Operation and adapter

The application operation is bound in `modules/{feature}/hooks/` and depends only on domain types and an injected domain port. The service in `services/` is the outside-data adapter: single parsing step, no business logic. It returns domain data or documented business failures mapped to typed domain error values; it NEVER throws those business failures. Unrelated transport, parsing, boundary, and programming exceptions remain exceptions and may propagate unchanged to the presentation boundary, never converted into domain errors. The service consumes the API's published contract (C14).

## F3 — Composition and presentation

`hooks/` plus `components/` compose the adapter and operation and own presentation state, never business logic. Views do not bypass the presentation binding to call services or transport directly. Binding-specific error-state and notification behavior belongs in the implementation guide.

The feature Hook is this shape's designated composition point (`C12`): it constructs the operation with the concrete service adapter and supplies it to the component. That authorizes the Hook to compose for its own feature; it does not make every Hook a composition root, and it introduces no application-wide composition layer.

This presentation binding is the Interface responsibility (C12) for the frontend shape, and it is already separate from the adapter that shares the feature: it delegates to the operation, holds no business rule, and composes nothing but its own technical collaborators. A frontend therefore needs no further interface folder (`C13`).

## F4 — Feature-owned domain organization

Group domain concepts within their feature. When an aggregate is used, its named folder retains the root, children, owned values, events and repository port; a root alone requires no child scaffolding. One entity per file including children, and one rule-bearing type per module. At the second same-role module under a business owner, introduce that role subfolder inside the owner, not a global bucket that fragments an aggregate. No generic multi-concept entity/model/value-object modules.

Data-only records use concept-specific record/projection roles (C8, C10), not fake OO entity names. Delivery request/response types stay at the service/presentation edge; storage shapes stay in adapters. Read projections remain domain-owned and framework-free (C9). Guides give native syntax and preserve shared-type reuse without copying types across features.

## Testing selection

Read `.aicore/core/architecture/testing/architecture.md` and the applicable testing guide. Component/service/assembled-application boundaries are defined there, not redefined here.
