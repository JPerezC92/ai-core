<!-- core:begin -->
# <Stack> implementation guide

> **Status:** proposed
> **Reviewed:** pending

## Applicability and ownership

Identify language, runtime, application shapes, and exclusions. Concrete libraries are reference-architecture mappings, not destination tool bindings. The common contract and selected shapes remain authoritative; this guide owns syntax and concrete implementation only. Documentation review does not establish code conformance.

## Structure and dependency mapping

Map each applicable shape's folders, domain, application, adapters, and composition. Explain static imports separately from runtime calls.

## Domain and ports

Preserve concrete entity, port, error, naming, and validation decisions. Map the entity behavior, immutable identity, and factory/validity obligation, and do not invent a state-transition convention. Identify unsupported choices explicitly rather than inventing equivalents.

## Application operations

Map single-operation `execute()`, injection, typed results, and policy ownership.

## Adapters and delivery

Map external-data conversion, IO, composition, presentation, serialization, and error binding. State conditional rules and their trigger.

## Imports and language conventions

Preserve concrete import, typing, module, and library conventions. Record contradictory source wording without silently resolving it.

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
| Selected shape | <all shape obligations> | <differences> |

Every common obligation and applicable shape obligation needs a mapping. Equal rigor does not mean identical libraries; N/A requires a language/runtime reason, not absence of documentation. Keep this heading order in all implementation guides. This is the non-testing template; testing guides retain their own template.

## Open decisions

Name unresolved choices, source evidence, and resolution authority. Never hide a missing mapping or promote a proposal to an approved decision.
<!-- core:end -->

<!-- project:begin -->
## Project extensions
<!-- project:end -->
