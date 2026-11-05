# Evidence file — domain architecture definitions

> **Record:** [odd/tasks/2026-11-05-domain-architecture-definitions.md](../tasks/2026-11-05-domain-architecture-definitions.md) — the sole authoritative intent, task and status record for this feature.
> **Owner:** Scribe ✍️ (Docs & Problems Manager) — author of this extraction
> **Created:** 2026-11-05

## What this file is for

Hold the attestational evidence behind one feature record's `## Log`: obligation accounting, reviewer verdicts and identities, original/candidate identities, literal commands with observed results, and the preservation mapping for anything moved out of the record. Each `E#` section is referenced from a record entry as `E#`.

## What this file is not

Disposable working evidence. It is not a feature record, task tracker, status register, intent authority, approval, adoption proof or delivery evidence. A verdict, hash or observed result recorded here establishes only what its own entry states; anatomy validation, a green check or a copied reviewer verdict never certifies the feature.

## Three evidence classes

- **Decisive** — requests, corrections, approvals and their labels, decisions, obligations, acceptance limits and commits: permanent, always in the record, never here.
- **Attestational** — who verified what, with which input identity, literal command and observed result: lives here while the feature is active so the record stays readable.
- **Reproducible** — content a reader can regenerate or re-read from Git, a committed artifact, or a gitignored `output/` artifact: referenced by pointer, never copied.

Retention and close-time reconciliation are owned by `.opencode/skills/odd-workflow/SKILL.md` → `### Evidence retention`; the boundary against a durable surface citing a specific evidence file is owned by `knowledge/agent-workflow.md` → `### Feature document`. This template illustrates the layout, not another rule definition.

## E1 — obligation accounting

### Method and disposition keys

Scribe ✍️ (Docs & Problems Manager), T3–T5 author-2, read every original listed in E2 and its current counterpart in full through the `read` tool. This is semantic author accounting, not independent acceptance or byte comparison. Source line references below are to the baseline copies; candidate references use sections so the mapping survives prose edits. All implementation paths below are relative to `architecture/implementation/`.

- **Retained** means the original valid duty remains in the indicated candidate owner or its cited common rule; consolidating duplicate wording does not retire the duty.
- **Translated** means its operative expression changes under the cited feature requirement/design resolution while preserving the specified responsibility.
- **Retired** applies only to the explicit transition-neutral restriction superseded by S5/L5. No other valid obligation is intentionally retired.
- Unchanged duties require no new design decision: S9/L16 limits this work to documentation, and S10 requires preservation/mapping rather than implementation remediation. Translations below name their more specific authority.
- C8 groups taxonomy, invariant ownership and model lifecycle (S2–S5, L23); C9 groups persistence/query capabilities and transaction/publication boundaries (S1, S4–S5, L23); C10 groups semantic naming and boundary roles (S7–S8). Shapes specialize layout (S6); guides spell mechanisms and filenames (S7/S10), not competing common law.

### Common contract — `architecture.md`

| Original section / lines and valid duties | Disposition and precise candidate mapping | Rationale / authority |
|---|---|---|
| Purpose and authority, 3–5: navigation owns statement layers; intended architecture is not conformance; documentation approval differs from implementation verification. | Retained: Purpose and authority. | S9/S10; no authority expansion. |
| C1, 7–9: domain/application/infrastructure in every language; inward imports; language/library not a layer; shape folders preserve layer names. | Retained: C1. | Existing dependency law unchanged. |
| C1, 9: application imports only domain types/ports, not frameworks/adapters; injected runtime effects are allowed and runtime calls differ from imports. | Retained: C1. | Concrete guide wording cites C1; removing duplication does not remove import restrictions. |
| C2, 11–13: no framework/infrastructure domain imports; entities/ports use domain types, not external records; errors have stable codes/messages; shape/guide owns representation/syntax. | Retained: C2; C8 taxonomy and C9 projection/port detail supplement it. | S1/S2/L23 clarify domain projections without leaking boundary records. |
| C2, 15: entity differs from records/functions; class with invariant-enforcing behavior, immutable identity, valid factory, no setters/writable identity. | Translated: C2 pointer; C8 Entity row, transition/construction paragraphs and review questions. | S2/S3/S5/L23 make root-owned child enforcement explicit without moving invariants to application. |
| C2, 15: no selected state-transition convention. | Retired: replaced by C8 named behavior returning same-identity replacement or typed error. | S5 and L5 explicitly select immutable transitions; no-setter duty remains in C8. |
| C3, 17–19: named business operation, single execute, injected domain ports, one operation per file, outcome naming with excluded generic role names. | Retained: C3. | S10 guide mappings preserve operation conventions. |
| C3, 19: one operation shape per stack; mixed vocabulary finding; composition/router may wire many but not redeclare use cases. | Retained: C3. | No operation-model redesign authorized. |
| C3, 19: policy in domain/application, not adapter/presentation; records/functions valid; enduring invariants/transitions domain-owned, orchestration application-owned; false model claims can be anemic. | Retained: C3; clarified classification/review in C8. | S2/S3/L23 preserve functional/record alternatives and reject caller-owned entity rules. |
| C4, 21–23: single mapping/parsing step, no adapter business rules, concrete composition only at edge. | Retained: C4; C9 adds reconstitution mapping and C10 names boundary roles. | S1/S8/L23 specialize existing boundary duties. |
| C5, 25–27: expected business failures returned as typed values; boundary/programming/IO exceptions remain exceptions; no arbitrary exception conversion or imposed result wrapper. | Retained: C5; C8 corrupt-state and C9 conflict clauses cite it. | L23 permits only contracted conflicts, not generic exception coercion. |
| C5, 27: documented business-failure response may map to domain error; presentation binds error/exception channels without reclassification. | Retained: C5 and existing frontend F2/F3 mappings. | Failure-channel ownership unchanged. |
| C6, 29–31: operations consume/return domain types; serialization delivery-owned, not execute. | Retained: C6; C9 framework-free projections and C10 boundary placement. | S8/L23 do not turn projections into HTTP/ORM records. |
| C7, 33–35: pure helper has no artificial wrapper; policy plus infrastructure needs operation boundary. | Retained: C7; C8 pure-rule row and C10 function naming refer to it. | S2/S7 preserve functional domains. |
| Testing and execution, 37–39: testing contract/guide exclusively owns levels, organization, doubles, evidence, parity; runtimes own permissions/review/execution/scope/uncertainty; no authority grant. | Retained: Testing and execution. | L20/L23 prohibit an inferred fake-repository mandate. |

### Backend shape — `shapes/backend.md`

| Original section / lines and valid duties | Disposition and precise candidate mapping | Rationale / authority |
|---|---|---|
| Applicability, 3–5: backend scope, common contract first, navigation statement ownership. | Retained: Applicability. | Existing selection unchanged. |
| B1, 7–9: domain/application/infrastructure folders; operation file ownership; stack selects concrete location; per-field entity read accessor. | Retained: B1; accessor protection references C8. | S3/S6/L23 add protection/layout, not remove read access. |
| B1, 9: ports return entities rather than storage records. | Translated: B1 → C9 aggregate results, domain projections and other capability return types. | S1/S2/L23; entity-only wording cannot describe clocks or read projections. Storage exclusion remains. |
| B1, 9: missing lookup is empty, not thrown. | Retained by consolidation: C9 lookup rule, B1 C9 reference; B2 policy. | S1; define once in common contract. |
| B2, 11–13: use case interprets absence as an error; single execute, domain imports, injection, returned failures. | Retained: B2 and its common-rule references. | No failure-policy relocation. |
| B3, 15–17: repository implements domain port; one outside-record-to-entity mapping. | Translated: B3 refers to C9 and outside-record-to-domain mapping with entity reconstitution under C8. | S1/S8/L23 include projections without bypassing entity validity. |
| Testing selection, 19–21: select testing contract/guide for operation, adapter and assembled tests. | Retained: Testing selection. | Testing remains separate authority. |

### Scripts shape — `shapes/scripts.md`

| Original section / lines and valid duties | Disposition and precise candidate mapping | Rationale / authority |
|---|---|---|
| Applicability, 3–5: scripts/CLI/tooling including independent packages; common first; size not exemption. | Retained: Applicability. | S9 no runtime/package redesign. |
| P1, 7–9: constants and pure typed transformations, no filesystem/network IO; entities allowed for identity/invariants; records/TypedDict/functions valid and classes not universal. | Retained: P1; P4/C8 add organization/classification. | S2/S6 preserve functional tooling. |
| P1, 9: type claiming identity/invariants with rules in callers is nonconforming; typed injected execute result/error operation; helper exemption. | Retained: P1 and C3/C5/C7/C8 references. | S3/S5/L23 root-owned rules do not become caller-owned rules. |
| P2, 11–13: loaders/builders/clients implement ports and map without policy; entry composes and delivery serializes; file/subprocess/network effects entry or named infrastructure helper. | Retained: P2. | S9 no IO authority change. |
| P3, 15–17: backend tooling, ticket scripts, skill scripts remain separate zones; guide owns concrete imports/startup; runtime owns exact-script authorization and gates. | Retained: P3; P4 layout stays within zones. | S6 does not authorize cross-zone consolidation. |
| Testing selection, 19–21: testing contract/guide; importable CLI not automatic unit boundary. | Retained: Testing selection. | No testing redefinition. |

### Frontend shape — `shapes/frontend.md`

| Original section / lines and valid duties | Disposition and precise candidate mapping | Rationale / authority |
|---|---|---|
| Applicability, 3–5: feature frontend, common first, navigation statement ownership. | Retained: Applicability. | Existing scope unchanged. |
| F1, 7–9: feature domain/services/hooks/components; data-only domain structures, service ports, one typed stable-code error per feature. | Translated: F1 keeps folders/ports/error, names intentional records honestly and permits actual C8 models conditionally. | S2/S3/S7/L23; data-only records remain valid, not falsely named entities; service ports not blanket N/A. |
| F2, 11–13: operation bound in hooks and imports domain/injected port only; service adapter parses once, no policy. | Retained: F2. | Concrete React composition unchanged. |
| F2, 13: domain or documented returned business errors, never throws those; unrelated transport/parsing/boundary/programming exceptions propagate without domain conversion. | Retained: F2 and C5. | L23 preserves failure distinctions. |
| F3, 15–17: hooks/components compose and own presentation state, no business policy; views cannot bypass binding; guide owns binding errors/notifications. | Retained: F3. | No presentation redesign. |
| Testing selection, 19–21: contract/guide owns component/service/assembled boundaries. | Retained: Testing selection. | No test-scope change. |

### Python guide — `stacks/python.md`

| Original section / lines and valid duties | Disposition and precise candidate mapping | Rationale / authority |
|---|---|---|
| Header and Applicability and ownership, 3–8: reference/documentation-only status; tooling/ticket/exact skill scope, not inferred UI/web; select common/scripts/backend; library examples not bindings; runtime exact-path authority. | Retained: same sections. | S9/S10 preserve reference status and authority boundaries. |
| Structure and dependency mapping, 10–12: constants/functions, ordinary entity classes, Protocol/ABC, errors; dataclasses/Pydantic valid for other roles; operation module; infrastructure IO/mapping; main composition/serialization. | Retained: same section and Domain/Application/Adapters mappings. | S6 adds paths, not a new framework or layer model. |
| Domain and ports, 16: typed data not self-opened paths; constants contain data only, no functions/classes/IO. | Retained: Domain and ports first bullet. | P1's Python module achievement preserved. |
| Domain and ports, 17: ordinary framework-free classes, underscore storage, readonly property per field, immutable identity; underscore not privacy proof; no universal freezing. | Translated: Domain and ports entity bullet with replacement unions, copying, immutable tuples and property alias protection. | S3/S5/L23 strengthen nested protection while retaining representation and unrelated-record freedom. |
| Domain and ports, 18: classmethod create maps valid factory; no new business validity/error semantics; no mandated constructor mechanism; backend entities not framework/Pydantic; unrelated dataclasses/Pydantic allowed. | Translated: Domain and ports create/reconstitute bullet, C8 construction protections. | S5/L23 now require lifecycle distinction and protected supported constructors; existing domain validity and C5 semantics remain, no universal new library mechanism. |
| Domain and ports, 19: Protocol/ABC domain signatures and stable-code/message business errors, not arbitrary exceptions. | Retained by consolidation: C2/C5; Domain and ports maps annotated Protocol/ABC signatures and code/message attributes. | F1 remediation removes repeated common law, retaining Python syntax. |
| Domain and ports, 20–21: structured intermediates TypedDict/equivalent not bare dict; entity behavior/class/create distinct from TypedDict records; no behaviorless entities bucket. | Translated: Domain and ports TypedDict/value/event bullets; Structure and dependency mapping; C8/C10/P4. | S2/S6/S7 classify and place records without artificial classes. |
| Pydantic models, 23–27: conditional non-backend-entity usage; ConfigDict not Config; Field constraints not custom init; field_validator/classmethod not validator; model_validate not parse_obj. | Retained: Pydantic models. | No API/library migration selected. |
| Pydantic models, 27: nested multi-field submodels not Any dict; closed forbid/open allow with reason; one-line model docstring; no framework-dependent business operations. | Retained: Pydantic models and C2. | Naming/lifecycle work does not waive schema conventions. |
| Application operations, 29–31: typed injected execute returning domain result/errors, no business raises. | Retained by consolidation: C3/C5/B2; Application operations maps typed callable/collaborators and union syntax. | F1 remediation cites owner instead of duplicating duty. |
| Application operations, 31: application verb_object module; class only for state/collaborators, VerbObject name without UseCase; no concrete client/builder or filesystem/network imports; async local choice, not universal rewrite. | Retained: Application operations. | Python-specific operation shape unchanged. |
| Adapters and delivery, 33–35: open/Path/glob/network/subprocess only infrastructure/entry; no adapter policy; entry composes, handler serializes; CLI/service edge not invented React/NestJS binding. | Retained: Adapters and delivery; common C4/C6/P2 remain operative. | S8 adds concrete boundary mapping, not framework selection. |
| Deployment zones, 39–41: self-contained backend packages with init, no cross-package/shared imports; sibling relative only within zone, others absolute; no parent traversal; absolute not bypass. | Retained: Deployment zones first bullet. | S6 growth does not change import authority. |
| Deployment zones, 42–43: standalone ticket no init, ROOT path insertion/sibling imports; ticket/backend exclusion; skill no ticket/backend or mcp_servers imports; runtime feature/gate authority. | Retained: Deployment zones second/third bullets. | Existing deployment compatibility preserved. |
| Deployment zones, 44–45: skill root/layer init; top-level repeated test-only dirs no init, unique nested package init retained; no distribution claim; accepted entry path insertion exemption. | Retained: Deployment zones fourth/fifth bullets. | No packaging redesign authorized. |
| Typing and modules, 47–49: parameter/return annotations; meaningful type instead of bare None; Optional/union per-file style; future annotations for forwards; no wildcards; sentence module docstring; no credentials/hardcoded paths, allowed derivation/env/constants. | Retained: Typing and modules. | S7 filename work preserves all typing/security conventions. |
| Testing and runtime boundaries, 51–53: select Python testing authorities, levels/factories/isolation/discovery/doubles; language and test runtime gates; no execution/command grant; runner/runtime dependency separation. | Retained: Testing and runtime boundaries. | L23 preserves testing ownership. |
| Obligation mapping, 55–72: all C1–C7/P1–P3/B1–B3 mapped; frontend unselected with no invented UI equivalent. | Translated: Obligation mapping preserves rows, updates B1 result scope, adds C8–C10/B4/P4 and extends frontend exclusion through F4. | S1/S10/L23; mapping follows refined owners, not a dropped obligation. |
| Open decisions, 74–76: no selected Python HTTP/repository/error-registry/serializer framework; future adapter needs mapping; CLI not unexplained web substitute. | Retained: Open decisions. | No new framework inferred from examples. |

### NestJS guide — `stacks/typescript/nestjs.md`

| Original section / lines and valid duties | Disposition and precise candidate mapping | Rationale / authority |
|---|---|---|
| Header/Applicability and ownership, 3–8: reference only, TS/TSX backend/test imports; common/backend selection; libraries reference not binding; other stacks need mapping; no conformance. | Retained: same sections. | S9/S10 no runtime approval. |
| Structure and dependency mapping, 10–12: domain/application/use-cases/infrastructure; NestJS infrastructure-owned. | Retained: same section; B4 example added. | S6 preserves layer placement. |
| Domain and ports, 16: global entity path; private readonly, per-field getters, static valid create; behavior/identity/setter protections; forbidden framework/storage imports. | Translated: Domain and ports entity bullet and C8; aggregate-local path, private constructor/create/reconstitute with replacement and nested-state mechanisms. | S3/S5/S6/L23; read access and import ban remain. |
| Domain and ports, 17: global repository.interface path; Symbol token; domain entity return not DB records; Promise optional lookup, no missing exception; no framework/storage imports. | Translated: Domain and ports repository bullet; C9; B4/C10 local order.repository.ts. Symbol and Promise<Order or null> preserved. | S1/S6/S7/L23 remove redundant suffix and broaden distinct query/other ports without row leakage. |
| Domain and ports, 18: error path, DomainError base, readonly registry code not raw string; registry message super call. | Translated path only: Domain and ports error bullet uses business-owned order-closed.error.ts; class/registry construction retained. | S6/S7 semantic filenames; no error-system redesign. |
| Domain and ports, 19: shared code registry path, screaming snake case, suffix with HTTP mapping; message registry path and lambdas not strings. | Retained: Domain and ports registry bullet. | Concrete registry obligation unchanged. |
| Application operations, 21–23: class not function/object; VerbObjectUseCase and use-case path; public execute; repository/service interfaces via constructor; domain-only imports/no decorators; returned business errors; null handled in operation; no repository NotFoundException. | Retained by syntax/consolidation: Application operations class/path/signature/constructor/null-branch example, C1/C3/C5/B2; Imports excludes NotFoundException. | F1 remediation removes generic common restatement; concrete TypeScript mechanisms remain. |
| Adapters and repositories, 27–29: adapter path/class, static toDomain and only static methods; DB import type from @repo/database. | Retained: Adapters and repositories; calls reconstitute for entities. | S5/S8/L23 add proper lifecycle mapping. |
| Adapters and repositories, 30: infrastructure repository path, interface implementation, no Injectable; db Database constructor without Inject; use mapper not inline entity construction; no policy. | Retained: Adapters and repositories and C4/B3. | C9 adds no hidden commit; existing adapter pattern preserved. |
| Controllers, 32–35: infrastructure controller not root; direct use cases, no facade; success literal status/data; instance-of returned error thrown only at delivery. | Retained: Controllers. | C5 serialization/error channel remains edge-owned. |
| Controllers, 36–37: ZodResponse success docs; ApiResponse 4xx JSendFailDto; file-top createZodDto success DTO; controller serialization not execute. | Retained: Controllers. | C10 adds optional payload filenames, not removing transport envelope. |
| Composition, 39–41: infrastructure module not root; no facade; repository/use-case factory providers, tokens and inject arrays; no Injectable on operations/repos. | Retained: Composition. | No DI mechanism redesign. |
| Imports and language conventions, 43–45: source/tests sibling-only relative; non-sibling aliases; no parent/cross-folder relative; no NotFoundException operation/repo, root controllers/modules or facade. | Retained: Imports and language conventions. | New role folders use existing alias policy. |
| Testing and runtime boundaries, 47–49: testing contract/TS guide owns operation/repo/parser/HTTP boundaries/doubles; runtime routing/scope/gates/execution/uncertainty. | Retained: Testing and runtime boundaries. | L23 no handwritten fake mandate. |
| Obligation mapping, 51–64 and Open decisions, 66–68: C1–C7/B1–B3 coverage; no identified mapping decisions. | Retained/extended: same sections, plus C8–C10/B4 rows; B1 references refined entity lifecycle. | S10 new-rule coverage; no new framework decision claimed. |

### React guide — `stacks/typescript/react.md`

| Original section / lines and valid duties | Disposition and precise candidate mapping | Rationale / authority |
|---|---|---|
| Header/Applicability and ownership, 3–8: reference/documentation-only, TS/TSX feature source/test import scope; common/frontend selection; listed libraries not bindings; other stacks need mapping; no conformance. | Retained: same sections. | S9/S10 no runtime approval. |
| Structure and dependency mapping, 10–12: component/hook/execute/port/service/data flow; operation hooks/use-feature.ts co-location; Hook imports do not license operation framework/concrete imports. | Retained: same section. | S6 adds domain paths without moving application binding. |
| Domain and ports, 16–17: always feature service-error path; actual feature-specific class extends Error, not generic FeatureServiceError; stable code, super/name, constructor not throwing; no unrelated exception representation. | Retained: Domain and ports first two bullets. | Error mechanism unchanged under C5. |
| Domain and ports, 18: shared types first, no local duplicates; otherwise local domain, not inline services/hooks/components; data-only entity-labelled structures. | Translated: Domain and ports shared/local record/projection bullet; F4/C8/C10 correct classification and business-local paths. | S2/S3/S6/S7 preserve data-only representation, retire no record duty. |
| Domain and ports, 19: typed service port; no React domain/service imports; shared schemas/types first, otherwise local. | Retained: Domain and ports service/query bullet; additional C9 projection distinction. | L23 keeps service ports applicable independently of repositories. |
| Application operations, 21–23: plain function/object execute not Hook; injected port result/error; no Query/state/effect/Hook/fetch/client; Hook injects and calls through queryFn/mutationFn. | Retained: Application operations. | Conditional aggregate persistence paragraph supplements rather than replacing operation shape. |
| Service, 27–30: plain object service export not class; no React/inline types/policy; unknown HTTP input and one parser; no casts; Promise typed error not raw Error; documented failures returned not rejected; no blanket exception conversion. | Retained: Service and F2/C5 references. | No adapter/error-channel redesign. |
| Service, 31: no HTTP means synchronous typed result/error; no async/await/fetch/HTTP; typed domain imports/local array; no invented failure. | Retained: Service; example uses OrderSummary[] projection instead of entity-labelled record. | S2/S7/L23 translate example's type role, not sync semantics. |
| Hook, 33–36: keys.ts/as const, no inline keys; useQuery; instance-of domain error throw only presentation converts to Query error; other exceptions not reclassified. | Retained: Hook. | Existing query binding retained. |
| Hook, 37–38: mutation success invalidation, onError console only not toast; filter useMemo; no direct client/fetch, operation injection; testing boundary pointer. | Retained: Hook. | No presentation/test-policy changes. |
| Component, 40–45: reads Query data/errors, invokes Hooks not services; no try/catch Hook calls; sonner toast only components; exact delete classes, AlertDialog vs Dialog; controlled open/change and reset-on-close. | Retained: Component. | All concrete UI conventions outside naming scope retained. |
| Imports and language conventions, 47–51: source/tests sibling relative, non-sibling aliases including theme/i18n; no parent/cross-folder traversal; same-language validation library; testing authority for mocks/runner/casts. | Retained: same section; TS/JS filename syntax pointer added. | S7 adds vocabulary without importing NestJS dependencies. |
| Testing and runtime boundaries, 53–55: testing contract/TS guide owns component/Hook/service/browser boundaries; runtime execution/scope/gates/dependency/uncertainty. | Retained: same section. | No expanded execution authority. |
| Obligation mapping, 57–70 and Open decisions, 72–74: C1–C7/F1–F3 mapped, no identified decisions. | Translated/extended: same sections, record terminology/conditional models in C2, plus C8–C10/F4. | S2/S10/L23 correct entity classification without blanket frontend exemption. |

### Guide template — `stacks/_template.md`

| Original section / lines and valid duties | Disposition and precise candidate mapping | Rationale / authority |
|---|---|---|
| Header/Applicability and ownership, 3–8: proposed/pending, identify language/runtime/shapes/exclusions; reference libraries not bindings; common/shapes authority; syntax-only guide, no conformance. | Retained: same sections. | S10 no automatic approval. |
| Structure and dependency mapping, 10–12: folders/layers/adapters/composition and static imports versus runtime calls. | Retained/extended: same section, B4/P4/F4 layout examples added here. | S6/S10 preserve heading order and responsibility. |
| Domain and ports, 14–16: preserve representation/ports/errors/naming/validation, map behavior/identity/valid factory; unsupported choices explicit. | Translated: same section maps C8 lifecycle/nested representation and C9 port signatures. | S2/S5/S10/L23 concretize expanded model. |
| Domain and ports, 16: do not invent state-transition convention. | Retired only as prohibition on selecting the now-defined convention: same section maps C8. | S5/L5 expressly select immutable-return convention; guides still cannot invent a competing one. |
| Application operations, 18–20: execute/injection/results/policy mapping. | Retained: same section; C9 replacement persistence/transaction mapping added. | S1/S5/S10/L23 extend mechanisms. |
| Adapters and delivery, 22–24: conversion/IO/composition/presentation/serialization/error mapping and conditional triggers. | Retained: same section; reconstitution/publication and named boundary conversions added. | S8/S10/L23 preserve failure and serialization duties. |
| Imports and language conventions, 26–28: preserve imports/typing/module/library conventions; contradictory wording recorded, not silently resolved. | Retained: same section; C10 syntax mapping added. | S7/S10 no duplicate semantic vocabulary. |
| Testing and runtime boundaries, 30–32: point to testing owners without duplicate law; runtime authority unchanged. | Retained: same section. | No testing/execution grant. |
| Obligation mapping, 34–47: every C1–C7 and applicable shape identifier; section names in mapping cells; achievement/runtime N/A rationale in final cell; equal rigor not identical libraries; fixed headings, separate testing template. | Retained/extended: Obligation mapping C1–C10 and selected-shape row; all heading order retained. | S10 new identifiers extend, not replace original coverage. |
| Open decisions, 49–51: name choices/evidence/authority; no hidden missing map or proposal-to-approved promotion. | Retained: Open decisions. | ADR remains Proposed. |

### Continuation-only companion edits

The final Python-only correction is additionally accounted below; its translations refine the earlier Python rows without retiring their duties.

These originals are the live pre-remediation files read in this continuation, not claimed baseline copies from E2's commit.

| Original section and content | Disposition and candidate mapping | Authority / limits |
|---|---|---|
| `architecture/README.md`: Ownership and extension C1–C7 range; Content model range and tree comment. | Translated: only those ranges become C1–C10; all selection, ownership, mapping, internal-reference and distribution duties remain. | S10 and parent F3; no common rules copied into navigation. |
| ADR 0007 Decision items 7–8: domain-event suffix, OrderPersistenceModel/persistence-model and PlaceOrder payload examples. | Translated: event suffix, OrderModel/model, CreateOrderRequest/OrderResponse and OrderSummary projection; other roles enumerated consistently; policy/domain-service distinction retained. | Parent F2 resolves selected vocabulary to C10 owner candidate; not an external-source mandate. |
| ADR 0007 Propagation C8–C10 rows: proposed group labels and common filename-table placement. | Translated: exact candidate C8–C10 section names; semantic table common, syntax tables guides. All propagation duties retained. | S7/S10; statement-layer ownership remains navigation-owned. |
| ADR 0007 Status, context, alternatives, consequences, provenance, acceptance/authorization and remaining propagation rows. | Retained: corresponding sections; Proposed status unchanged. | No approval or implementation authority granted. |
| Research Recommendations and alternatives: common concept-role selection, actual policy vs domain service, business-owned growth, selected trade-offs. | Translated/expanded with matching event/model examples and native filenames; preserved selection-versus-source distinction. | Parent F2; no fresh source observation claimed. |
| Research metadata, method, sources, findings, limits and reuse notes. | Retained: corresponding sections. | Original provenance and unknown Context7 revision remain explicit. |

### Final Python-only correction — complete translation delta

Input: the full Python candidate read at the final bounded correction, before the third owner round; compared with full common contract and navigation Content model, especially its cite-not-copy rule. Only `stacks/python.md` and this evidence file are writable. S9/S10 and the parent's final correction authorize representation changes, not new common policy. All unlisted Python obligations in the earlier accounting remain unchanged.

| Pre-correction section and duty | Final candidate mapping / disposition | Authority and preservation |
|---|---|---|
| Structure and dependency mapping: generic layer duties, ports/errors and composition/serialization. | Translated into layer package names, Python module/class/Protocol forms and main.py location, citing C1/C2/P1/C4/C6. | Common responsibilities remain C1–C6; dataclasses/Pydantic availability for non-entity roles retained. |
| Domain and ports first bullet: typed pure transformation rather than self-opened input. | Translated to annotated calculate_price signature; constants-only assignments/no functions/classes/IO retained as the concrete module convention. | P1/C7 own purity; no input-file IO permission added. |
| Entity bullet: same-identity replacement, nested protection and read accessor duties. | Translated into close union signature, Order(self._id, ...) construction, tuple(items), immutable-element condition and defensive-copy access. | C8 owns invariant/alias law; ordinary non-Pydantic backend classes, underscore caveat, property-per-field and unrelated-record freedom preserved. |
| Factory bullet: protected creation/reconstruction, root child enforcement, corrupt-state failure semantics. | Translated into classmethods, shared state validator invoked by __init__, creation eligibility in create, internally constructed replacement children and illustrative raise ValueError path outside business union. | C5/C8 retain all duties; no universal exception class or new framework selected. This maps bypass protection without treating Python underscores as privacy. |
| Value/event bullet: value equality, immutable nested state, pending facts, record/function alternatives. | Translated into __eq__, optional standard-library frozen dataclass with immutable nested fields, tuple annotation and reconstitute initialization to (). TypedDict/def alternatives retained. | C8 owns law; Python frozen outer-object limitation expressed in concrete field types, no frozen entity mandate. |
| Repository/query/clock bullet: domain result types and async capability. | Translated into find_by_id, summary and now method signatures with Order/OrderSummary optional results and Instant; async def alternative. | C9 duties unchanged; no port made N/A and no raw row/transport result introduced. |
| Pydantic models last sentence: generic framework-free-business reminder. | Consolidated at C2 citation; all conditional Pydantic APIs, schema constraints, docstrings and non-backend-entity limitation retained. | C2 remains operative; no Pydantic adoption or library migration. |
| Application C9 paragraph: lookup policy, replacement persistence, transaction/session boundary, event handoff. | Translated into is None return, replacement variable, isinstance narrowing, repository.save(replacement), context-manager/explicit transaction methods and pending_events access. | C9/B2 remain operative; session implementation infrastructure-owned, existing import bans retained, publication/failure strategy referred to C9 rather than restated. |
| Adapters and delivery opening: IO-library ban plus generic no-policy mapping/composition/serialization prose. | Python IO functions/libraries and domain/application import exclusions retained; generic clauses replaced by adapter/operation constructor wiring and handler narrowing/dictionary/optional json.dumps example with C1/P2/C4–C6 citations. | Baseline responsibilities still at C1/C3–C6/P2; no serializer dependency, global JSON mandate, React or NestJS binding. |
| Adapters and delivery second paragraph: boundary conversion and projection ownership. | Translated into order_from_row, request_to_parameters and order_to_response signatures, reconstitute call, and OrderSummary/TypedDict construction. | C4/C8–C10 remain complete owners; no request/row moved to domain and no new ORM selected. |
| Concept-role filenames intro/tail: generic business class naming/no artificial wrapper clauses. | Consolidated into C10/C7 references; native snake_case syntax, full role table and concrete predicate/calculation filenames retained. | Class names still governed by C10; no valid naming/helper duty retired. |
| Obligation mapping C1/C2/C5/C6/C7/B2/B3: generic semantic summaries. | Translated into actual package/wiring/property/annotation/narrowing/JSON/function/null-branch/mapper mechanisms. Other rows retain concrete Python achievements. | S10/navigation mapping semantics require mechanisms, not copies of common law; every identifier remains mapped. |

Preserved without final edits: applicability/header limits; aggregate-local B4/P4 concrete folder examples; annotated Protocol/error attributes and TypedDict rule; all Pydantic API/schema conventions except the consolidated generic sentence; operation naming/class-vs-function/import/async conventions; all Deployment zones bans and exceptions; all Typing and modules conventions; testing/runtime ownership pointers; open framework decisions. Authority/execution/distribution disclaimers remain owner declarations, not rewritten C rules. No valid duty is retired in this correction.

## E2 — original and candidate identities

- Parent-supplied baseline attribution: `aa4d4f965f2cb561a8b48f940fdac44263a33070`. Originals were read from `output/domain-architecture-baseline/architecture/implementation/architecture.md`, `shapes/{backend,scripts,frontend}.md`, `stacks/{python,_template}.md`, and `stacks/typescript/{nestjs,react}.md`.
- Baseline copies are transcribed temporary inputs. Their byte identity to the attributed commit was not verified by this author. No Git read, hash, diff or byte-equality command was executed; these copies are evidence inputs, not normative authority.
- Candidate identity: working-tree documentation after T3–T5 author-2's initial checkpoint and this F1–F3 continuation, before any subsequent writer. Targets are the eight corresponding live implementation files plus `architecture/README.md`, ADR 0007 and the research README named in E1. No immutable candidate commit or measured hash is available in this assignment.
- All eight live implementation files, navigation, ADR, research and the full governing feature through Log were read before continuation edits. This continuation writes only Python/NestJS guides, navigation, ADR, research and this evidence file. Common contract, shapes, React and template are unchanged from the read candidate.
- Reviewer must bind acceptance to the combined candidate's final immutable identity through the coordinator; this path-and-checkpoint identity is not a substitute for that gate.
- Final correction identity: the same working-tree candidate plus author-2's subsequent Python-only full-guide duplication correction and this accounting delta. No common/shape/frontend/NestJS/navigation/ADR/research edits in that correction; no hash or commit was measured.

## E3 — reviewer verdicts and identities

- Accepted predecessor per parent dispatch: T2 research/ADR candidate independently PASS by Sentinel 🛡️ (Quality Guardian), session `ses_e55a4136dffeZrHM2zwF1ejV5t`; it did not accept ADR 0007.
- Remediation inputs per parent continuation: Bastion 🧱 (Backend & Scripts Architect), session `ses_e559db146ffe8qr3bLfet7tAYa`, findings F1 (guide duplication), F2 (proposal vocabulary mismatch), F3 (navigation range). This artifact attributes those findings; it does not invent that review's overall verdict or a fresh clearance.
- Design input remains governing feature L23, session `ses_e55a8d854ffeMSaxrkQcGYXjnw`. Design approval is not authoring acceptance.
- Fresh owner reviews, independent semantic acceptance and coordinator acceptance remain pending for this changed candidate. No task completion or ADR acceptance is asserted.
- Final parent dispatch reports F2/F3 fixed and frontend PASS unaffected; no new independent Python verdict is claimed. This correction returns before the third owner round.

## E4 — literal commands and observed results

- No shell, Git, test, interpreter or network commands executed by this continuation; executable RED/GREEN is not applicable to these prose-only edits. No test or runtime outcome is claimed.
- Manual action: full `read` returns of the eight baseline implementation copies and eight current counterparts, then navigation, ADR, research, governing feature and evidence template. Expected: identify every original duty and its owner; observed: the E1 mappings above cover each supplied original section and mark the transition-neutral wording expressly superseded rather than importing it as precedent.
- Manual normal/adverse walkthrough for F1: compared the guide operation paragraphs to C1/C3/C5/B2 and Python port bullet to C2/C5. Expected: common duties stay at their owners, guide carries syntax/mechanisms. Candidate now uses typed Python callable/union/attributes and TypeScript class/signature/interface/null-branch syntax; shared import/failure/injection duties remain enforceable at cited owners. Fresh reviewer confirmation is pending.
- Manual normal/adverse walkthrough for F2: compared ADR Decision 7–8 and research recommendations to common C10 and Python/NestJS filename tables. Expected: event/model suffixes and OrderModel align; a policy cannot be relabelled domain service; raw row/request/response stay outside domain. Candidate spells these consistently, keeps distinct roles and preserves Proposed/provenance limits. This is textual comparison, not source retrieval or runtime verification.
- Manual normal/adverse walkthrough for F3: compared navigation coverage ranges with candidate C8–C10 and guide mapping rows. Expected: new identifiers discoverable without repeating their law; candidate changes the range references only. It does not certify guide completeness or implementation adoption.
- Final Python-only manual pass: read the complete Python candidate, common C1–C10 and navigation statement-ownership text, not only the reported adapter paragraph. Replaced generic layer/lifecycle/transaction/boundary/helper summaries with the concrete mechanisms listed in E1's final delta. Normal walkthrough: replacement is narrowed then saved; handler builds a dictionary and can serialize it. Adverse walkthrough: None branches to a typed value; corrupt-state example raises outside the business union; tuple/frozen examples explicitly require immutable nested elements. Expected owners remain common C1–C10/P1/P2/B2. Author textual comparison supports the mapping; examples were not executed and independent acceptance remains pending.

## E5 — preservation mapping

- No feature Log entry was moved, edited or deleted; no source excerpt was transplanted into this file. Reproducible source text remains at the E2 pointers.
- Initial chat-only grouped accounting is expanded here into section-specific mappings; this does not replace the feature's decisions or user wording.
- Coordinator next action: record the accounting decision/outcome, supplied-baseline identity limitation and E1/E2 pointer in the existing feature Log before acceptance. This author lacks permission to edit that record.
- Before disposal, the coordinator must retain decisive conclusions/acceptance limitations in the feature record under the skill's close-time reconciliation. This artifact is not durable authority by itself.

## E6 — optional finding-triggered impact and escape trace

- Findings: parent-supplied F1–F3 in E3. Baseline attribution and unverified copies, pre-remediation candidate, and remediation candidate are distinguished in E2; no exact introducing edit is claimed.
- Inspected footprint: all supplied original/current implementation targets and the navigation, proposed ADR, research and governing feature. Excluded: implementation/test sources, destinations, external source retrieval, Git history and additional architecture families; outside this assignment. No repository-wide coverage claim.
- Origin: baseline guide text already contains common-rule repetition in Python Domain/Application and NestJS Application; that repetition is retained in the pre-remediation candidate. The ADR vocabulary mismatch appears in the pre-remediation proposal versus owner tables; exact introducing interval is unknown. Navigation's C1–C7 text is established in the live pre-remediation read, but no navigation baseline copy was supplied here.
- Escape point: unknown; parent review identified the gaps, but this author has not inspected prior audit commands or coverage sufficient to establish why they escaped earlier checks.
- Remediation: F1 maps common duties to their owners while preserving concrete guide mechanisms; F2 aligns source-local proposal wording; F3 updates coverage ranges. These are author observations awaiting independent verification, not coordinator-validated causal findings.
- Assigned evidence writer: Scribe ✍️ (Docs & Problems Manager), author-2. Coordinator owns the permanent feature Log conclusion and subsequent acceptance; no Log entry identity has yet been assigned in this artifact.
- Final F1 scope reassessment: parent identifies the remaining Adapters and delivery repetition as baseline-origin; the baseline Python section is already read and accounted at E1 (original lines 33–35). Earlier author correction targeted only the cited Domain/Application paragraphs, leaving that adapter wording in place; earlier accounting called it retained rather than reconciling statement ownership. Exact escape point/causal attribution beyond this observed corrective footprint remains unknown, not inferred from the later finding. Final author corrective scope covers every Python section and mapping cell against common-law duplication while preserving Python-specific import and language conventions. Other guides/owners remain outside this write boundary. Permanent conclusion and refreshed owner verdict remain the coordinator's responsibility.
