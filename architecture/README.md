# Architecture documentation

## Purpose and selection

These documents describe intended architecture, not verified implementation conformance. Documentation approval does not certify existing application code. Future code adoption/remediation requires separate authorization and evidence.

Read in order:

1. `architecture/clean-architecture.md` — common layers, dependencies, ports, operations, mapping/composition, failures, serialization, and helper semantics.
2. Applicable shapes: `architecture/shapes/frontend.md`, `architecture/shapes/backend.md`, `architecture/shapes/scripts.md`. Python backend tooling may select both backend and scripts; a language name is not a shape.
3. Applicable concrete implementation guide below; it maps rather than replaces the common/shape contract.
4. `architecture/testing/architecture.md`, then its selected testing guide under `architecture/testing/stacks/`. Testing design has its own authority and template; do not infer test rules from implementation examples.

| Implementation guide | Shape | Documentation status |
|---|---|---|
| `architecture/stacks/typescript/react.md` | Frontend | reference |
| `architecture/stacks/typescript/nestjs.md` | Backend | reference |
| `architecture/stacks/python.md` | Scripts; backend where applicable | reference; framework selections remain unselected |

Concrete libraries and aliases preserve reference-architecture choices, not destination tool bindings. The destination selects its tooling in project-owned configuration without weakening the common contract. If the stack has no mapping, or a contradiction prevents a decision, use the agent runtime's uncertainty route; do not infer approval from another language or current code patterns.

## Ownership and extension

The common contract owns shared semantics; shapes own application responsibilities/layout; implementation guides own syntax and library mappings. Runtime specs retain authority, scope, warmup/execution procedures, edit checkpoints, review gates, dependency ownership, reporting, and uncertainty handling. A document pointer does not grant execution permission.

Copy `architecture/stacks/_template.md` before writing another implementation guide. Keep its heading order and map every C1–C7 obligation and selected shape obligation; explain applicability and language/runtime differences. Unsupported choices remain explicit open decisions, not invented equivalents or unexplained N/A. Proposed guides are not claims of reviewed documentation or implementation conformance.

Never edit a distributed architecture file. A destination that needs a different stack adds its own guide, copied from `architecture/stacks/_template.md` or `architecture/testing/stacks/_template.md`; an unbound path survives every sync.

## Contract boundaries

- No file under `architecture/` references a path outside `architecture/`. These documents point to each other only; agent runtimes, knowledge documents, and source-local records point here.
- Architecture states its rules completely. A rule's content is never deferred to another document. Statements about who holds execution authority, permissions, edits, or gates are not references and remain as written.
- Every destination receives identical bytes. That guarantees distribution, not conformance: a reference library, runner, or framework named here remains a reference choice, adopted by the destination in its own configuration or its own guide.

## Testing location transition

The sole testing documents are `architecture/testing/architecture.md` and `architecture/testing/stacks/{_template,typescript,python}.md`. The obsolete root compatibility files and their clearance rows are removed. Testing decisions, reviewed guide status, parity, and project-owned selections are preserved; relocation is not a new testing decision or implementation-conformance claim.

New architecture paths arrive with their consumers as one applicable set and require destination-authorized `core-sync init --bind-cleared` enrollment at the selected revision; `apply` alone does not enroll missing or markerless paths.
