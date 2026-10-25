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

### Source-local extraction inventory — reviewed

This accounting is source-local history, not portable approval/history or proof of code conformance. Original identities are the full pre-extraction reads: `.opencode/agents/atrium.md` v1.4.4 (A), `.opencode/agents/bastion.md` v1.7.4 (B), `.opencode/agents/forge.md` v1.6.4 (F), `.opencode/agents/crucible.md` v1.9.0 (C); line ranges below refer to those originals. Shared contract identity: `knowledge/agents.md`, original lines 53–63 (K). Testing identities: full original contract (121 lines), template (125), TypeScript guide (203), Python guide (119), with reviewed metadata dated 2026-10-25. Candidate identities are the named paths/sections in the combined candidate accepted by the coordinator following T6 independent review. No obligation is proposed retired.

Legend: translated = same obligation extracted to the named owner; retained = procedure stays at its original owner. Separators, examples, and repeated prohibitions follow their enclosing rule, not independent mandates. The no-retirement accounting above excludes the blanket TypeScript relative-import shorthand and Python parent-relative examples superseded by the user-approved policies below.

| Original section/range | Disposition and candidate destination |
|---|---|
| A40–44 Language-agnostic: dependency direction/layout | Translated: clean-architecture C1; shapes/frontend F1. |
| A46–48 Domain | Translated: common C2; frontend F1; React Domain and ports. |
| A50–53 Application | Translated: common C3/C5/C6; frontend F2; React Application operations. |
| A55–58 Adapter | Translated: common C4/C5; frontend F2 owns the explicit never-throw-business-failures adapter obligation and unchanged exception propagation; React Service maps it to returned typed error values. |
| A60–61 Composition | Translated: common C4; frontend F3; React Hook/Component. |
| A63 Test levels | Translated reference, no competing rules: existing testing contract/TypeScript guide; frontend Testing selection. |
| A65–77 React Architecture Overview | Translated: React Structure, Application, Service, Hook, Component; synchronous branch preserved. Hook/component testing points to architecture/testing/stacks/typescript.md → Unit tests → Frontend component and hook, without a competing testing mandate. |
| A81–90 DOMAIN/error naming/constructor/code | Translated: React Domain and ports, including always-required error file and matching name. |
| A92–98 Entity types/shared package detection | Translated: React Domain and ports; no inline/duplicate types. |
| A102–109 APPLICATION/non-Hook execute | Translated: React Application operations, injected port, Hook binding. |
| A113–124 SERVICE checks | Translated: React Service; plain object, unknown HTTP, single parse, schemas, union, exceptions, no inline types. |
| A126–133 Service success example | Translated: React Service's unknown-request then parse pipeline; documented-failure mapping stays conditional. |
| A137–148 HOOK | Translated: React Hook; keys/as const, useQuery, binding throw, invalidation, console-only errors, memoized filters, no direct IO. Testing boundary is an exact pointer to architecture/testing/stacks/typescript.md → Unit tests → Frontend component and hook. |
| A152–162 COMPONENT | Translated: React Component; sonner, error state, delete colors/dialogs, controlled/reset modals, no direct IO. |
| A166–172 SHARED TOOLS CONSISTENCY | Translated: React Imports and language conventions retains validation-library consistency; mocking, runner consistency, and test-cast obligations remain solely architecture/testing/stacks/typescript.md → Test data and doubles, with an exact pointer from React. |
| A176–182 IMPORT PATH RULES | Translated: React Imports and language conventions; same-directory sibling imports allowed, aliases required for non-siblings, parent traversal forbidden. |
| A186–195 WHAT MUST NOT EXIST | Translated: React Service/Hook/Component/Domain/Imports; A195 blanket relative-import shorthand superseded by the user-approved sibling policy. |
| B40–44 Language-agnostic layers/layout | Translated: common C1; backend B1. |
| B46–51 Domain | Translated: common C2; backend B1; NestJS Domain and ports; Python Domain and ports (immutable identity, per-field read-only properties, valid-instance class factory). |
| B53–57 Application | Translated: common C3/C5; backend B2; both backend implementation guides. |
| B59–62 Infrastructure | Translated: common C4; backend B3; NestJS/Python Adapters and delivery. |
| B64 Test levels | Translated reference to existing testing authority; backend Testing selection. |
| B66–70 Dependency and error contract | Translated: common C1/C5/C6; guides map runtime effects, exceptions, delivery. |
| B72–75 File-Type Branch Trigger | Retained in backend reviewer runtime: exact scope/routing and uncertainty are not architecture definitions. |
| B77–87 NestJS DOMAIN/entities | Translated: NestJS Structure; Domain and ports (readonly/getters/create/import bans). |
| B89–93 Repository interfaces | Translated: NestJS Domain and ports (Symbol, domain entities, nullable lookup, import bans). |
| B95–100 Domain errors | Translated: NestJS Domain and ports (base/code/message registries, naming, lambda messages, HTTP suffix mapping). |
| B104–118 APPLICATION | Translated: NestJS Application operations (class, no decorators, interfaces, domain imports, returned failure/null policy). |
| B122–130 INFRASTRUCTURE/adapters | Translated: NestJS Adapters and repositories (static mapper/class/type-only DB import). |
| B132–136 Repositories | Translated: NestJS Adapters and repositories (interface, Database injection, no decorators, mapper use). |
| B138–145 Controller | Translated: NestJS Controllers (infrastructure location, direct use cases, success/fail docs, JSend DTO, edge throw). |
| B147–157 Module/factory examples | Translated: NestJS Composition, preserving DATABASE_CONNECTION and repository/use-case factories. |
| B161–167 IMPORT PATH RULES | Translated: NestJS Imports and language conventions; source/tests, aliases and detailed sibling exception. |
| B171–177 WHAT MUST NOT EXIST | Translated: NestJS relevant sections; B177 blanket relative-import shorthand superseded by the user-approved sibling policy. |
| B181–191 Python/Layers | Translated: Python Structure, Domain, Application, Adapters; common contract never suspended. |
| B192 Project-local mapping pointer | Retained: backend reviewer project extensions; local modules are not universal bindings. |
| B194–196 PYTHON BACKEND applicability | Retained routing authority in runtime; descriptive scope in Python Applicability does not grant edits. |
| B198–206 MODULE BOUNDARIES/backend packages | Translated: Python Deployment zones, including __init__, same-package sibling relative imports, absolute imports from other packages, prohibited parent traversal, and unchanged deployment isolation; B204–205 parent-relative examples superseded by the user-approved policy. No wildcards remains in Typing and modules. |
| B208–212 Ticket scripts | Translated: Python Deployment zones (standalone, sys.path convention, independent zones both directions). |
| B214–217 Feature-scoped exact paths/audit | Retained runtime authorization and after-edit gate; no doc permission replacement. |
| B218–221 Feature scripts IO/zones/OQ5 | Translated: scripts P2/P3; Python Deployment zones and Adapters; startup exemption retained. |
| B223–231 PYDANTIC MODEL CONVENTIONS | Translated: Python Pydantic models, all v2 methods, constraints, nesting, schema openness/docstrings. |
| B233–237 Zone Import Prohibitions | Translated: Python Deployment zones, including mcp_servers cross-zone example. |
| B239–248 Python Language Rules/LAYER BOUNDARIES | Translated: common C1/C3/C5/C6; scripts P1/P2; Python Domain/Application/Adapters. |
| B250–255 TYPE HINTS | Translated: Python Typing and modules; typed intermediate data, optional style, forward annotations. |
| B257–261 EXPLICIT IMPORTS AND MODULE DOCUMENTATION | Translated: Python Typing and modules; Domain constants-only constraint. |
| B263–268 WHAT MUST NOT EXIST | Translated: Python Domain/Typing/Adapters; no IO/untyped/wildcards/credentials/hardcoded paths. |
| F58–67 Static Data Service Pattern/example | Translated: React Service, typed synchronous plain-object branch. |
| F69–72 Static data constraints | Translated: React Service/Application; union, no invented failures, exceptions, no async/HTTP/React, port injection/edge serialization. |
| F74 Re-read active service spec before writing | Retained implementer procedure, not a shared architecture rule. |
| F76–80 Import Path Rules | Translated: React Imports and language conventions; aliases including theme/i18n, same-folder exception, no traversal/cross-folder relatives. |
| K53–57 Shared clean architecture | Translated: common C1–C4 and shapes; original shared heading becomes compatibility pointer under separate runtime-wiring task. |
| K58 Test ownership | Retained testing authority; common Testing and execution points to it. |
| K59–63 Static/runtime, failures, serialization, language mapping, helper exemption | Translated: common C1/C5/C6/Purpose/C7; guides map without new layers. |

### Retained runtime and testing procedures

| Original area | Retained authority / treatment |
|---|---|
| A1–38 identity, role/roster, Rulebook review snapshot and Nonconforming feature files | Frontend reviewer runtime; no authority, stable-input or design-rework gate extracted away. |
| A197–268 Workflow/Dependency Ownership/When Uncertain/Tools/Output/Stop/Hard Rules/Naming/Local Permissions | Frontend reviewer runtime, including approval order, owned dependencies, no-code-fix boundary, output and local grants. |
| B1–38 identity/role/roster, review snapshot, Nonconforming feature files | Backend reviewer runtime; full procedures retained. |
| B270–337 Python Test Files/Workflow/Tools/runner groups/Output/Stop/Hard Rules/Naming/Local Configuration | Backend reviewer runtime; dual Python/test-owner gate and no runtime test dependency retained. Source-local concrete roles stay project-owned. |
| F1–56 identity/roles, Feature Scope, Nonconforming files, exact Python scope/workflow | Implementer runtime; assignments, no scope expansion, checkpoints and gates retained. |
| F82–168 Workflow/warmup/read bounds/per-step/blockers/dependency proposals/landmarks/learnings/Tools/bindings/denied installs/Output/Naming/Stop/Hard Rules | Implementer runtime; execution/install/Git/config restrictions, resource ownership, import completeness, and completion gates retained. |
| C1–158 full reviewer runtime | Test reviewer runtime retains procedure, scope/routing, execution/install/permissions, snapshot/evidence separation, output and local grant. Rule-free compatibility headings retained; definitions remain testing-owned. |
| testing-architecture/architecture.md (removed source path): Purpose; Test levels; Boundaries and failures; Test organization; Test data and doubles; Execution and evidence; Stack-guide selection; Stack guides; Cross-stack parity; Adding a stack guide; References; Project extensions | Relocated unchanged in meaning to architecture/testing/architecture.md; only owner/path references retargeted. Obsolete pointer removed. Statuses/parity and project-owned selections preserved. |
| testing-architecture/stacks/_template.md (removed source path): metadata/template use; Applicability and ownership; Test pyramid mapping; File organization; Unit tests; Integration tests; End-to-end tests; Test data and doubles; Execution and evidence; Cross-stack parity; Open decisions; Project extensions | Relocated to architecture/testing/stacks/_template.md, separate from the implementation template; only contract/copy paths changed. Obsolete pointer removed. |
| testing-architecture/stacks/typescript.md (removed source path): same ten sections plus metadata/project extension | Relocated to architecture/testing/stacks/typescript.md; only contract path changed. Backend use-case/parser/repository/HTTP; component+Hook/service/browser phases; exact paths, factories/faker/MockProxy, runner consistency and parity preserved. Obsolete pointer removed. |
| testing-architecture/stacks/python.md (removed source path): same ten sections plus metadata/project extension | Relocated to architecture/testing/stacks/python.md; only contract path changed. Operation/domain/parser/loader/adapter/CLI, project-wide discovery, helpers/doubles, tmp_path/hermeticity, assertion conventions, parity, no inferred framework preserved. Obsolete pointer removed. |
| knowledge/agents.md outside K53–63; knowledge/agent-workflow.md | Shared policy/workflow retained, including evidence accounting, coordination, template copying, authorization/conflict routing; not duplicated as architecture mandates. |
| ADR 0001 and ADR 0002 | Existing source-local decisions unchanged; accepted ADR 0003 records ownership evolution, not fabricated historical rationale. |

### Unresolved source wording and review boundary

The user explicitly approved the TypeScript import policy: same-directory `./sibling` imports are allowed; all non-sibling imports use aliases; `../` traversal is forbidden. This supersedes the blanket relative-import shorthand at A195 and B177 and resolves the TypeScript contradiction in both implementation drafts; F76–80 supports the sibling form. The user also explicitly approved the Python import policy: same-package `from .sibling import ...` imports are allowed; imports from all other packages use absolute package paths; parent-relative `..` traversal is prohibited. This resolves B204–205's sibling wording/parent-relative example contradiction and supersedes those parent-relative examples. Standalone ticket scripts' sibling-name imports and `sys.path` startup conventions, entry-point exemption (OQ5), and all import-zone/deployment isolation prohibitions retain their existing scope; absolute spelling grants no cross-zone permission. These approvals do not change runtime specs or establish code conformance.

The user approved Python backend entities as ordinary framework-free domain classes, close to the existing TypeScript entity rules (B46–51, B83–87): internal underscore storage, immutable identity, a read-only `@property` per field without setters, and `@classmethod create(...)` enforcing existing domain validity. This resolves the entity representation gap without claiming underscore privacy enforces immutability, introducing constructor tokens or universal frozen fields, changing error semantics, or banning dataclasses/Pydantic for unrelated roles. Python Domain and ports and its C2/B1 mappings now record that choice. No Python HTTP framework, repository library, error registry layout, or serializer framework mapping has been selected; those decisions remain open, and current implementation patterns do not resolve them.

The coordinator accepted T6 combined Sentinel 🛡️ (Quality Guardian) PASS on the complete candidate and authorized documentation status promotion. The concrete implementation guides are reference documents and ADR 0003 is Accepted. This is documentation acceptance only, not implementation conformance or destination migration. Unselected Python framework bindings remain open, not blockers. Templates remain proposed skeletons; future proposed guides cannot support review verdicts. No external publication or problem-record mutation is performed.
<!-- project:end -->
