# Frontend application shape

## Applicability

Feature-oriented frontend applications. Read `architecture/implementation/architecture.md` first. Statement-layer ownership is defined in `architecture/README.md` → `## Content model`.

## F1 — Feature layout and domain

Use `modules/{feature}/domain/`, `services/`, `hooks/`, and `components/`. Domain defines intentional data-only domain records (not entities), any actual rule-bearing C8 model, service/query ports, and one typed, stable code-bearing business error per feature (C2). Frontend service ports remain applicable even when there is no aggregate persistence repository (C9).

## F2 — Operation and adapter

The application operation is bound in `modules/{feature}/hooks/` and depends only on domain types and an injected domain port. The service in `services/` is the outside-data adapter: single parsing step, no business logic. It returns domain data or documented business failures mapped to typed domain error values; it NEVER throws those business failures. Unrelated transport, parsing, boundary, and programming exceptions remain exceptions and may propagate unchanged to the presentation boundary, never converted into domain errors.

## F3 — Composition and presentation

`hooks/` plus `components/` compose the adapter and operation and own presentation state, never business logic. Views do not bypass the presentation binding to call services or transport directly. Binding-specific error-state and notification behavior belongs in the implementation guide.

## F4 — Feature-owned domain organization

Group domain concepts within their feature. When an aggregate is used, its named folder retains the root, children, owned values, events and repository port; a root alone requires no child scaffolding. One entity per file including children, and one rule-bearing type per module. At the second same-role module under a business owner, introduce that role subfolder inside the owner, not a global bucket that fragments an aggregate. No generic multi-concept entity/model/value-object modules.

Data-only records use concept-specific record/projection roles (C8, C10), not fake OO entity names. Delivery request/response types stay at the service/presentation edge; storage shapes stay in adapters. Read projections remain domain-owned and framework-free (C9). Guides give native syntax and preserve shared-type reuse without copying types across features.

## Testing selection

Read `architecture/testing/architecture.md` and the applicable testing guide. Component/service/assembled-application boundaries are defined there, not redefined here.
