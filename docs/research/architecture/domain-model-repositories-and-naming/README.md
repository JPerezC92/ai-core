# Domain models, repositories, layout and cross-language naming

## Record metadata

- Primary domain: `architecture`
- Topic: `domain-model-repositories-and-naming`
- Aliases / tags: aggregate, entity, value object, repository, domain event, immutable transition, unit of work, domain folders, role filenames.
- Researched: 2026-11-05 — prior source inspection recorded by Cipher 🔓 (Lead Orchestrator); evidence verification by Augur 🔮 (Research Analyst), T1, session `ses_e55ba41f9ffeNWGpZfLD3gMW0u`.
- Reviewed: 2026-11-05 — accepted evidence verification in feature L20 and design resolutions by Bastion 🧱 (Backend & Scripts Architect), session `ses_e55a8d854ffeMSaxrkQcGYXjnw`, L23; independent documentary semantic acceptance recorded in L28, with owner reviews in L25. No source refetch is claimed.
- Source versions / revisions: mutable web documentation; no pinned source revisions established for the November observations.
- Applicability: aggregate-oriented repository design, invariant ownership, and evidence informing the accepted shared documentation convention in ADR 0007; not implementation conformance.
- Freshness / recheck triggers: changed sources, disputed claims, new language mappings, or adoption beyond the stated aggregate-oriented scope.
- Related features / decisions: [governing feature](../../../../.aicore/core/odd/tasks/2026-11-05-domain-architecture-definitions.md); [accepted ADR 0007](../../../architecture/decisions/0007-domain-model-repositories-and-naming.md) (explicit acceptance L30).
- Supersedes / superseded by: none evidenced; extends [anemic-domain research](../anemic-domain-model-and-use-case-naming/README.md), without rewriting its historical observations.

## Question and boundaries

What distinguishes a rule-bearing domain model from records, what responsibility belongs to a repository, and what evidence supports a coherent layout and naming proposal? This record preserves already accepted evidence, not new research, operative architecture rules, implementation approval or delivery proof. Aggregate patterns are conditional, not a requirement to introduce aggregates into simple CRUD or pure tooling domains.

## Method and provenance

Scribe ✍️ (Docs & Problems Manager) synthesized the full feature record, especially L13–L16, L20 and L23, and the existing anemic-domain research. No sources were independently fetched for this publication. November source observations are attributed to the prior inspection recorded in L13; L20 identifies the independent evidence verifier. The dispatch supplies the NestJS Context7 example provenance; its exact query/library revision is not preserved in the accepted record. No new quotations, experiments, local inventory, Git commands or code scans were performed. Structural/source scanning is inapplicable to this prose-only preservation assignment.

## Sources

| ID | Locator and section | Version / revision | Access or observation date; executor | Supports / limits |
|---|---|---|---|---|
| R1 | https://martinfowler.com/eaaCatalog/repository.html | mutable | 2026-11-05; prior inspection L13, verification L20 | Repository abstraction; not a universal filename convention |
| R2 | https://www.cosmicpython.com/book/chapter_02_repository.html | mutable | 2026-11-05; L13/L20 executors above | Persistence abstraction separating domain from storage |
| R3 | https://www.cosmicpython.com/book/chapter_06_uow.html | mutable | 2026-11-05; L13/L20 | Transaction coordination outside repository; ORM session already supplies UoW behavior |
| R4 | https://www.cosmicpython.com/book/chapter_07_aggregate.html | mutable | 2026-11-05; L13/L20 | Aggregate boundaries and repository per aggregate-root type, not per instance |
| R5 | https://www.cosmicpython.com/book/appendix_validation.html | mutable | 2026-11-05; L13/L20 | Validation responsibilities; does not establish this proposal's immutable-return convention |
| R6 | https://www.cosmicpython.com/book/appendix_project_structure.html | mutable | 2026-11-05; L13/L20 | Separation of domain and adapters; no universal role-folder growth threshold |
| R7 | https://learn.microsoft.com/en-us/azure/architecture/microservices/model/tactical-domain-driven-design | mutable | 2026-11-05; L13/L20; earlier observation in companion U11 | Tactical domain distinctions and invariant ownership; aggregate root may protect child behavior |
| R8 | https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/microservice-domain-model | mutable | 2026-11-05; L13/L20 | Persistence-ignorant domain and aggregate-oriented model; not a mandate for every application |
| R9 | https://peps.python.org/pep-0008/#package-and-module-names | mutable | 2026-11-05; L13/L20 | Lowercase Python modules, underscores where useful; no domain-role suffix mandate |
| R10 | NestJS Context7 documentation examples; https://docs.nestjs.com/ | exact query/revision unknown | 2026-11-05; prior example observation attributed by dispatch and L13 | Role-suffixed filename examples inform selection, not a cross-language standard |
| R11 | [Anemic-domain research](../anemic-domain-model-and-use-case-naming/README.md), U1/U5/U8/U11/U12 and findings A1–A7 | preserved 2026-10-28 research | original Augur units and coordinator synthesis | Anemia versus data records, functional rules and application orchestration; historical local paths are not current authority |
| R12 | [Feature](../../../../.aicore/core/odd/tasks/2026-11-05-domain-architecture-definitions.md), L4–L10, L14, L20, L23 | repository record read 2026-11-05 | user selections; accepted evidence and design returns | Local proposal authority and qualifications, not external-source mandates |

## Findings

1. A repository separates persistence access from the domain. In the aggregate-oriented model, its collection boundary is an aggregate-root type; children do not receive independent repositories that bypass their root [R1–R4, R7–R8]. Transaction commit is coordinated outside repositories; a separate custom UoW abstraction is not universally necessary [R3].
2. Identity alone does not establish a rich model. Invariants and legal transitions must be protected by the model, including root-owned child invariants; data-only records and pure domain functions remain legitimate distinct representations [R7–R8, R11–R12].
3. Storage/transport shapes and domain objects have different responsibilities. Persistence ignorance and explicit boundary mapping support distinguishing them, but do not prescribe the exact proposed suffix vocabulary [R2, R8, R11].
4. Python module syntax and NestJS examples inform different language-native filename spellings. They establish no universal external naming mandate [R9–R10].
5. Same-identity immutable transitions returning typed errors, nested-state protection, one rule-bearing type per module, business-owned folders, and a role subfolder at the second same-role module are selected proposal rules, not claims that the sources mandate them [R12]. Growth subfolders must remain inside aggregate/business ownership.
6. L23 resolves proposal details: reconstruction validates applicable state invariants without replaying creation; query ports return domain-owned projections; only explicitly contracted persistence conflicts become typed outcomes; after-commit sequencing alone does not assure delivery [R12]. These are accepted design resolutions, not newly verified source quotations.

## Recommendations and alternatives

Use the evidence to define taxonomy, invariant ownership and repository boundaries once in the common contract, with shape-owned layout and language-specific achievement mappings. Preserve application transaction ownership without universally requiring a bespoke UoW. Keep query projection ports distinct from aggregate repositories and from raw storage/transport types.

The user-selected proposal uses common concept-role vocabulary with native Python and TS/JS separators. The selected semantic roles are entity, value object, event, repository, port, domain service, policy, error, row, model, request, response, projection, record and query. Keep pure predicates/calculations and data records visible rather than relabeling everything an entity. An actual policy uses `pricing_policy.py` / `pricing.policy.ts`; a domain service instead uses `pricing_domain_service.py` / `pricing.domain-service.ts`. An event uses `order_placed_event.py` / `order-placed.event.ts`; infrastructure `OrderModel` uses `order_model.py` / `order.model.ts`, distinct from `OrderRow`. Delivery examples are `CreateOrderRequest` and `OrderResponse`; a domain read shape is `OrderSummary` with the projection filename role. Corresponding TS filenames have `.js` equivalents, without establishing a reviewed JavaScript framework stack. These spellings align the proposal to the authored owner candidate; they are not new external-source findings. Business-owned folders with internal growth subfolders avoid both generic type buckets and fragmentation of aggregates. These are design trade-offs, not measured productivity improvements [R9–R12].

## Limitations and open questions

- No exhaustive local classification inventory, supported 34-file count, runtime adoption audit, destination conformance, or measured quality improvement exists here.
- No fresh external retrieval occurred during authoring. R10's precise Context7 invocation and source revision: TODO: requires evidence if exact retrieval reproducibility is needed.
- No automatic handwritten-fake mandate follows from repository examples; current testing guides retain doubles authority [R12 L20/L23].
- Event delivery requires an explicit reliability strategy where needed; neither an event type nor publication after commit proves reliable delivery. No delivery mechanism is selected or implemented here.
- Owner propagation and independent documentary semantic acceptance are recorded in feature L25/L28; explicit ADR acceptance is recorded in L30. Research itself does not make the naming standard normative; the architecture owners carry the operative rules.

## Reuse and supersession notes

Reuse the bounded repository and invariant evidence with its aggregate applicability and dated provenance. Recheck mutable sources for disputed or changed claims. Reuse naming/layout material as an explicitly accepted design selection, never as an externally mandated standard. The current architecture owners, not this record or its ADR, govern implementation; feature progress remains solely in the governing feature record.
