# <Stack> implementation guide

> **Status:** proposed
> **Reviewed:** pending

## Applicability and ownership

Identify language, runtime, application shapes, and exclusions. Concrete libraries are reference-architecture mappings, not destination tool bindings. The common contract and selected shapes remain authoritative; this guide owns syntax and concrete implementation only. Documentation review does not establish code conformance.

## Structure and dependency mapping

Map each applicable shape's folders, domain, application, adapters, and composition. Explain static imports separately from runtime calls.

Map the selected B4/P4/F4 business-owned layout with concrete language paths: a compact root-only aggregate, an aggregate with children and internal role-folder growth, and a functional/record domain where applicable. Show where its repository port and boundary records live. Keep this mapping under this heading.

## Domain and ports

Preserve concrete entity, port, error, naming, and validation decisions. Map C8 using the language's construction/access controls, same-identity return unions, nested-state protection, value equality, reconstitution and immutable pending-event representation. Explain record/function alternatives. Map C9 repository, projection and other port signatures, including empty lookup syntax. Identify unsupported choices explicitly rather than inventing equivalents.

## Application operations

Map single-operation `execute()`, injection, typed results, and policy ownership.

Show C9's explicit persistence of transition replacements and application coordination through the selected infrastructure transaction capability; explain conditional applicability rather than mandating a custom UoW.

## Adapters and delivery

Map external-data conversion, IO, composition, presentation, serialization, and error binding. State conditional rules and their trigger.

Map C8/C9 reconstitution and transaction/publication flow, distinguishing reliability from ordering, and C10 row/model/request/response/projection conversions with C5-compatible failure handling.

## Imports and language conventions

Preserve concrete import, typing, module, and library conventions. Record contradictory source wording without silently resolving it.

Map C10's shared semantic role vocabulary to native filenames, citing the common table rather than introducing another vocabulary. Distinguish filename syntax examples from reviewed framework-stack coverage.

## Testing and runtime boundaries

Point to the current testing contract and applicable testing guide, without duplicating their rules. Execution authority, edit scope, gates, and uncertainty procedure stay in agent runtimes.

## Obligation mapping

| Obligation | Concrete mapping | Applicability or uncovered decision |
|---|---|---|
| C1 Layers/dependencies | <section> | <semantics> |
| C2 Domain/ports | <section> | <semantics> |
| C3 Operation | <section> | <semantics> |
| C4 Mapping/composition | <section> | <semantics> |
| C5 Failures | <section> | <semantics> |
| C6 Serialization | <section> | <semantics> |
| C7 Helpers | <section> | <semantics> |
| C8 Domain model | <section> | <construction, transitions, nested protection, reconstruction, events and record/function syntax> |
| C9 Repositories/transactions | <section> | <aggregate/projection/other ports, absence, replacement save, atomicity and event flow> |
| C10 Naming | <section> | <native spelling of all shared roles and boundary mapping> |
| Selected shape | <all shape obligations> | <differences> |

Follow `architecture/README.md` → `## Content model`. Every common obligation and applicable shape obligation needs a mapping, and every row must cite its identifier. The mapping cell names the guide section that carries the achievement; the last cell states only the language-specific achievement or a language/runtime reason for N/A. Equal rigor does not mean identical libraries. Keep this heading order in all implementation guides. This is the non-testing template; testing guides retain their own template.

## Open decisions

Name unresolved choices, source evidence, and resolution authority. Never hide a missing mapping or promote a proposal to an approved decision.
