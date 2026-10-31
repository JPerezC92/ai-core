# Frontend application shape

## Applicability

Feature-oriented frontend applications. Read `architecture/clean-architecture.md` first; this shape specializes responsibilities, not the common dependency/error rules. Syntax and libraries belong to the selected implementation guide.

## F1 — Feature layout and domain

Use `modules/{feature}/domain/`, `services/`, `hooks/`, and `components/`. Domain defines entity types as data-only domain records — data structures by design, not rule-holding entities — plus service ports and one typed, stable code-bearing business error per feature; no framework or transport imports.

## F2 — Operation and adapter

The application operation is bound in `modules/{feature}/hooks/` and depends only on domain types and an injected domain port. The service in `services/` is the outside-data adapter: single parsing step, no business logic. It returns domain data or documented business failures mapped to typed domain error values; it NEVER throws those business failures. Unrelated transport, parsing, boundary, and programming exceptions remain exceptions and may propagate unchanged to the presentation boundary, never converted into domain errors.

## F3 — Composition and presentation

`hooks/` plus `components/` compose the adapter and operation and own presentation state, never business logic. Views do not bypass the presentation binding to call services or transport directly. Binding-specific error-state and notification behavior belongs in the implementation guide.

## Testing selection

Read `architecture/testing/architecture.md` and the applicable testing guide. Component/service/assembled-application boundaries are defined there, not redefined here.
