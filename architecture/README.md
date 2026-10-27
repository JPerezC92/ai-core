<!-- core:begin -->
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

Concrete libraries and aliases preserve reference-architecture choices, not destination tool bindings. The destination selects its tooling in project-owned configuration/extensions without weakening the common contract. If the stack has no mapping, or a contradiction prevents a decision, use the agent runtime's uncertainty route; do not infer approval from another language or current code patterns.

## Ownership and extension

The common contract owns shared semantics; shapes own application responsibilities/layout; implementation guides own syntax and library mappings. Runtime specs retain authority, scope, warmup/execution procedures, edit checkpoints, review gates, dependency ownership, reporting, and uncertainty handling. A document pointer does not grant execution permission.

Copy `architecture/stacks/_template.md` before writing another implementation guide. Keep its heading order and map every C1–C7 obligation and selected shape obligation; explain applicability and language/runtime differences. Unsupported choices remain explicit open decisions, not invented equivalents or unexplained N/A. Proposed guides are not claims of reviewed documentation or implementation conformance.

## Testing location transition

The sole testing documents are `architecture/testing/architecture.md` and `architecture/testing/stacks/{_template,typescript,python}.md`. The obsolete root compatibility files and their clearance rows are removed. Testing decisions, reviewed guide status, parity, and project-owned selections are preserved; relocation is not a new testing decision or implementation-conformance claim.

New architecture paths require destination-authorized `core-sync init --bind-cleared` enrollment at the selected revision; `apply` alone cannot enroll missing or markerless paths. Deliver the new documents with their consumers as one applicable set. Destinations reconcile displaced shared text and genuine local extensions themselves; nonempty `pending` or a reconciliation blocker prevents acceptance, and `core-sync check` must exit `0`. This source transition neither mutates a destination nor claims it migrated. Source-local ADRs are explanatory, not required shared dependencies.
<!-- core:end -->

<!-- project:begin -->
## Project extensions

### Current source selections

The previously approved import interpretations are mapped by `architecture/stacks/typescript/react.md` and `architecture/stacks/typescript/nestjs.md` → Imports and language conventions, and `architecture/stacks/python.md` → Imports and language conventions → Deployment zones. Those owners retain the sibling exceptions, non-sibling alias/absolute mappings, traversal prohibitions and deployment/startup boundaries; this navigation adds no competing portable contract.

The approved Python backend-entity representation is mapped by `architecture/stacks/python.md` → Domain and ports and Obligation mapping. Its framework-free entity choice does not select a framework for unrelated DTO/configuration roles or establish application conformance.

No Python HTTP framework, repository library, error registry layout or serializer framework mapping has been selected. These project selections remain open; current implementation patterns do not decide them. Follow `architecture/stacks/python.md` → Open decisions and the applicable runtime's uncertainty route when a missing mapping affects the task. Unselected bindings alone are not blockers for unrelated work.

### Optional source-local history

The original extraction inventory, retained-procedure accounting, approval interpretations and documentation-acceptance boundary are preserved in [architecture extraction accounting](../docs/architecture/history/architecture-extraction-accounting.md). Read it when historical evidence is relevant, not as a shared prerequisite. Reference-guide status and current definitions remain with their architecture owners; the historical review is not implementation conformance, destination migration, external publication or problem-record approval.
<!-- project:end -->
