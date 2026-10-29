# Anemic domain models in Clean Architecture — and use-case naming

## Record metadata

- Primary domain: `architecture`
- Topic: `anemic-domain-model-and-use-case-naming`
- Aliases / tags: anemic domain model, rich domain model, clean architecture, use case naming, interactor, transaction script, CRUD, DDD, functional domain model.
- Researched: 2026-10-28 — two Augur 🔮 (Research Analyst) units (anemic model; use-case naming) plus Cipher 🔓 (Lead Orchestrator) synthesis.
- Reviewed: not independently reviewed — documentary synthesis only (2026-10-28).
- Source versions / revisions: articles and vendor docs are mutable and were read on 2026-10-28; Microsoft validation page at revision `1811c6d1c9ec56ba2132295802c17b5dc7ef659b` (updated 2026-04-28). Books were not read — see Limitations.
- Applicability: conceptual design guidance for layered/clean architectures, especially this repo's TypeScript reference guide and Python tooling. Not implementation-conformance evidence.
- Freshness / recheck triggers: changed vendor docs, new source editions, or a decision to make any naming rule normative.
- Related features / decisions: none found.
- Supersedes / superseded by: none evidenced.

## Question and boundaries

- What "anemic domain model" means and why it is criticized.
- Whether Clean Architecture forbids or requires it.
- Where behavior should live in a clean architecture.
- Whether functional/procedural domain code is a legitimate alternative.
- How use cases should be named, and how naming relates to anemia.
- Local comparison against `architecture/clean-architecture.md`, the backend/frontend guides, and the Python tooling in this repo.

Excluded: implementation audit, rename plan, code changes, framework selection, and empirical claims about defect rates or performance.

Intended reuse: design guidance and local-contract comparison. This record is evidence, not runtime policy, implementation approval, or delivery proof; it is not implementation-conformance evidence.

## Method and provenance

- Unit 1 (anemic model): Augur read Fowler's *Anemic Domain Model*, *Domain Model*, and *Transaction Script*; Martin's *The Clean Architecture*; Microsoft's DDD validation guidance; and the local architecture contract.
- Unit 2 (use-case naming): Augur read Cockburn's *Writing Effective Use Cases* extract; Martin's 2011 and 2012 posts; Fowler's *Service Layer*; Evans's DDD Reference; Microsoft CQRS/DDD guidance; MediatR's handler interface; Bogard's vertical-slice article; and the local stack/test guides.
- Cipher read the local files cited as `L*` and synthesized both units. No code was executed; no git, tests, installs, browser sessions, or memory writes.
- Saved-research lookup: `docs/research/README.md` has no matching topic; Basic Memory search for `anemic domain model` returned no results. No prior evidence was reused.
- Structural/source scanners were not used: this is conceptual prose research, not syntax-dependent code exploration or a source-risk audit.

## Sources

| ID | Locator and section | Version / revision | Access or observation date; executor | Supports / limits |
|---|---|---|---|---|
| U1 | https://martinfowler.com/bliki/AnemicDomainModel.html | mutable web article | 2003-11-25; read 2026-10-28 by Augur | Definition and critique of the anti-pattern |
| U2 | https://martinfowler.com/eaaCatalog/domainModel.html | mutable web article | 2003-03-05; read 2026-10-28 | Domain Model combines behavior and data |
| U3 | https://martinfowler.com/eaaCatalog/transactionScript.html | mutable web article | 2003-03-05; read 2026-10-28 | Procedural alternative; not always inferior |
| U4 | https://martinfowler.com/eaaCatalog/serviceLayer.html | mutable web article | read 2026-10-28 | Service Layer as an application boundary; no class-per-use-case rule |
| U5 | https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html | mutable web article | 2012-08-13; read 2026-10-28 | Entities may be objects or data structures plus functions; Dependency Rule |
| U6 | https://blog.cleancoder.com/uncle-bob/2011/11/22/Clean-Architecture.html | mutable web article | 2011-11-22; read 2026-10-28 | "Interactor" terminology; no suffix mandate |
| U7 | https://www.ifi.uzh.ch/dam/jcr:00000000-25a0-3d08-0000-00000ce96422/weuc_extract.pdf | pre-publication draft #3 | 2000-02-21 (pub. 2001); read 2026-10-28 | Use-case name as active verb phrase; user-goal level; CRUD discussion truncated |
| U8 | https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/domain-model-layer-validations | revision `1811c6d1c9ec56ba2132295802c17b5dc7ef659b` | updated 2026-04-28; read 2026-10-28 | Aggregates enforce invariants; DTO validation does not replace domain validation |
| U9 | https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs | mutable vendor doc | 2025-02-20; read 2026-10-28 | Commands as business tasks, not data updates; CQRS not for simple CRUD |
| U10 | https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/ddd-oriented-microservice | mutable vendor doc | 2022-04-13; read 2026-10-28 | Application layer coordinates; domain holds business rules |
| U11 | https://learn.microsoft.com/en-us/azure/architecture/microservices/model/tactical-domain-driven-design | mutable vendor doc | 2026-02-25; read 2026-10-28 | Business logic outside entities creates an anemic model |
| U12 | https://www.domainlanguage.com/wp-content/uploads/2016/05/DDD_Reference_2015-03.pdf | 2015, CC BY 4.0 | read 2026-10-28 | Thin application layer; domain services; intention-revealing interfaces |
| U13 | https://raw.githubusercontent.com/LuckyPennySoftware/MediatR/main/src/MediatR/IRequestHandler.cs | `main`, commit not resolved | read 2026-10-28 | `Handle()` is the handler method |
| U14 | https://www.jimmybogard.com/vertical-slice-architecture/ | mutable web article | 2018-04-19; read 2026-10-28 | One use case per request; vertical slices |
| L1 | `architecture/clean-architecture.md:10-18,22-34` | working tree, 2026-10-28 | read by Cipher | Local layers, C2–C7 rules |
| L2 | `architecture/shapes/backend.md:10-14` | working tree | read by Cipher | `application/` one file per use case; entity construction |
| L3 | `architecture/stacks/typescript/nestjs.md:13,17,24,42` | working tree | read by Cipher | Pure TS class, `execute()`, `XUseCase` factory example |
| L4 | `architecture/testing/stacks/typescript.md:30-60` | working tree | read by Cipher | `new XUseCase(repository)` test example |
| L5 | `architecture/stacks/python.md:13,18,31` | working tree | read by Cipher | Module-level named `execute()`; class not required |
| L6 | `.opencode/skills/op-model/scripts/op_model_lookup/application/find_models.py:1,14` | working tree | read by Cipher | Module-level `execute()` use case |
| L7 | `.opencode/skills/core-sync/scripts/core_sync_pkg/application/apply_core_revision.py:40,59` | working tree | read by Cipher | `ApplyCoreRevision` class with `execute()`, no suffix |
| L8 | `.opencode/skills/core-sync/scripts/core_sync_pkg/domain/merge.py:1-23` | working tree | read by Cipher | Pure, IO-free domain rule in a module |
| L9 | `.opencode/skills/core-sync/scripts/core_sync_pkg/domain/regions.py:1-3` | working tree | read by Cipher | Pure region parsing/rebuilding |
| L10 | `docs/research/README.md:16-42` | working tree | read by Cipher | No existing matching topic |

## Findings

### Answer in brief

1. An anemic domain model is not "a class with only data"; it is a **domain model that claims to model the domain but leaves the behavior elsewhere**, usually in services, while keeping public mutators.
2. Clean Architecture does **not** require rich object-oriented entities. It requires inward dependencies and business rules kept out of adapters and transport. Martin explicitly allows entities as "data structures and functions" [U5].
3. A codebase can be **Clean-Architecture-compliant and domain-anemic at the same time** — all rules can live in large use cases while every dependency points inward.
4. The real question is **where invariants and legal state transitions are enforced**, not whether methods live on classes.
5. Use-case naming and domain richness are the same design pressure seen from two angles: a name like `UpdateUser` describes a data mutation; `ChangeEmailAddress` describes a business outcome and forces the invariant question.
6. For this repo: C3 fixes "one named business operation" with a single `execute()` but does not mandate a suffix; `XUseCase` appears only in examples. The recommendation below is a convention, not an existing obligation.

### Anemic domain models

#### A1. What "anemic" means

Fowler's definition: domain-named objects with properties and getters/setters but almost no behavior; services perform calculations, validation, and updates through those accessors [U1]. His target is specifically a **purported object-oriented domain model** that pays the costs of modeling and mapping without gaining behavior-rich modeling benefits [U1].

The anti-pattern is therefore not "a type with fields." It is a **domain model whose behavior has been removed while its domain-model claim remains**.

#### A2. Not every data-only type is anemic

DTOs, view models, persistence records, events, configuration, and read models are data structures by design. Martin distinguishes entities from simple data structures and explicitly permits data structures at boundaries [U5]; his 2011 post has controllers pass "simple vanilla data structures" to an interactor and return another data structure to the view [U6]. Calling a DTO anemic is a category error; calling a domain entity anemic is a design finding.

#### A3. Clean Architecture does not require rich OO entities

Martin's article states that an entity "can be an object with methods, or it can be a set of data structures and functions"; its job is to encapsulate enterprise-wide business rules independently of external mechanisms [U5]. The Dependency Rule constrains **source-code dependency direction**, not whether behavior is expressed as methods, functions, or a service [U5].

So Clean Architecture is compatible with:

- rich OO entities and aggregates;
- immutable records plus pure domain functions;
- a thin domain plus policy-heavy use cases (architecturally clean, but domain-anemic);
- transaction scripts, provided they do not invert dependencies into infrastructure.

#### A4. Clean Architecture and DDD are different disciplines

Clean Architecture owns layers, dependency direction, boundaries, and testability [U5][L1]. DDD owns modeling: aggregates, invariants, ubiquitous language, and domain services [U8][U12]. Neither implies the other. A codebase can satisfy every dependency rule and still have an anemic model; it can also have rich entities that import ORM decorators and violate Clean Architecture.

#### A5. Where behavior should live

The useful rule is not "put methods on entities." It is: **put each rule where every caller is forced to obey it.**

| Kind of logic | Preferred home | Why |
|---|---|---|
| Enduring validity rules, legal state transitions, invariants | Domain entity/aggregate or pure domain function | Must hold regardless of caller; prevents bypass |
| Rules spanning multiple entities | Domain service or domain function | Does not belong to one entity; still framework-free |
| Workflow sequencing, transaction scope, authorization, application-specific decisions | Use case | Orchestration and application policy |
| Transport shape/format validation | Delivery edge / DTO | Rejects malformed input before the domain |
| Mapping between outside records and domain types | Adapter | No business rules [L1:22] |
| Serialization | Delivery edge | Transport concern [L1:30] |
| Pure calculation | Pure helper | No artificial use-case wrapper [L1:34] |
| Read projections/reporting | Query/read model or use case returning DTO | May bypass the domain by design [U9] |

Two important nuances:

- **DTO validation does not replace domain validation.** Microsoft's DDD guidance makes aggregates responsible for invariants across state changes and explicitly warns that DTO validation alone is insufficient [U8].
- **Use cases are not necessarily rule-free.** Martin assigns application-specific business rules to use cases and general rules to entities [U5]. Evans's application layer is thinner — coordination without domain business knowledge [U12]. The local contract deliberately allows policy "here or in domain" [L1:18], which is broader than Evans. Do not flatten either formulation into "all logic belongs in entities."

#### A6. The functional alternative is legitimate

Immutable records plus cohesive domain functions can express a rich domain:

```text
use case: load order -> confirm(order) -> Result<ConfirmedOrder, DomainError> -> persist
```

This is not anemic if the validity rules and legal transitions live in the domain functions and construction is controlled. It becomes the same failure mode in functional clothing if every use case constructs and mutates raw records directly, duplicating rules and allowing illegal states.

The local Python guide already permits data-only constant modules and pure transformation functions in the domain [L5:13]; the TypeScript guide expects framework-free classes with immutable fields, read accessors, and a valid-instance factory [L3:17]. Both are legitimate representations of C2. The choice is a stack/style decision, not a Clean Architecture requirement.

#### A7. When a thin or CRUD model is acceptable

Fowler explicitly says Domain Model is not always the best tool and presents Transaction Script as a legitimate alternative [U3]. Microsoft's CQRS guidance also says CQRS is not appropriate for simple CRUD [U9]. A thin model is defensible when:

- the domain has few or no invariants;
- there is one entry point per mutation;
- rules do not duplicate across use cases;
- the application is short-lived or primarily data maintenance;
- the team does not need a ubiquitous language yet.

The cost is that invariants become implicit, duplicated, or enforced only by the database. The design becomes a problem when complexity arrives and the thin model is retained while the code still claims to be a domain model.

#### A8. Anemia spectrum

| Shape | Assessment |
|---|---|
| DTO, event, read model, persistence record | Not anemic; data structure by design |
| Simple CRUD with no invariants, one entry point | Thin model acceptable; transaction script is honest |
| Domain classes with public setters and no behavior; `UserService` holds all rules | Classic anemic anti-pattern |
| Rich-domain intent but all logic in use cases; entities are data bags | Clean-Architecture-compliant but domain-anemic |
| Immutable records plus centralized pure transitions | Not anemic if invariants and construction are controlled |
| Functional style with rules duplicated in every handler | Anemic in substance, regardless of syntax |

#### A9. Local reading

- C2 forbids framework/infrastructure imports in the domain; business errors are typed; ports speak domain types [L1:14].
- C3 says one named business operation with a single `execute()`, injected ports, and policy "here or in domain" [L1:18].
- C4 keeps business rules out of adapters and requires a single mapping step [L1:22].
- The backend shape requires `application/` with one file per use case, and entities with immutable identity, a read accessor per field, and a factory building valid instances [L2:10].
- The NestJS guide requires a pure TypeScript class with one `execute()`, no framework decorators, and injected interfaces [L3:24].
- The Python guide requires "the module holding the named `execute()` operation"; a class is not required [L5:13,31].

What the local contract does **not** define: a legal state-transition API for entities. The guides specify construction (`create()`), read access, and identity immutability, but not how an entity changes state. A rich model therefore needs a documented transition convention — for example, a domain method returning a new valid instance, or a pure domain function returning a typed result. Without one, teams either add setters (contradicting the entity contract) or push state changes into use cases (producing the "clean but anemic" shape).

Observed local style: the Python skill tooling uses module-level `execute()` operations [L6:14] and an unsuffixed `ApplyCoreRevision` class [L7:40,59], with pure IO-free rules in `domain/` modules such as `merge_top_level` [L8:12] and `split_regions` [L9:33]. This is a functional-domain style, not an anemic OO model. It is consistent with the local contract.

### Use-case naming

#### B1. Three different names are being conflated

| Thing being named | Example | Source of the convention |
|---|---|---|
| Business operation / use case | `PlaceOrder` (verb phrase) | Cockburn [U7], CQRS [U9] |
| Implementing component | `PlaceOrderUseCase`, `PlaceOrderHandler`, `OrderPlacer` | Framework/style conventions; Martin's "interactor" [U6] |
| Method | `execute()`, `handle()` | Local contract [L1:18]; MediatR [U13] |

Most naming arguments fail because they compare a business-operation name with a component name. `PlaceOrder` is a good operation name and an unusual class name; `PlaceOrderUseCase` is a good class name and a redundant operation label inside `application/use-cases/`.

#### B2. Cockburn: the name is the goal as an active verb phrase

Cockburn's fully dressed template specifies the use-case name as "the goal as a short active verb phrase" [U7]. The primary unit is the **user goal**: one actor, one sitting, roughly 2–20 minutes. "Register a new customer" and "Buy a book" are user goals; "Log on" is not; "Find a Customer" is a subfunction [U7].

Cockburn records that there is **no consensus** on CRUD use cases — separate `Create/Retrieve/Update/Delete` cases versus one `Manage Frizzles` — and the available extract truncates before his resolution [U7]. So `ManageX` is an open question in the source, not an endorsed convention.

#### B3. Martin: "interactor" names the component, not the operation

Martin's 2011 post refers to the implementing object as an **interactor** [U6]; the 2012 post defines the Use Case layer and the Dependency Rule but does not prescribe a class suffix or an `execute()` method [U5]. The 2017 book was not read in this study, so no claim is made about specific class names used there.

#### B4. Fowler: Service Layer is a layer, not one operation

Fowler's Service Layer defines an application boundary with "a set of available operations" that coordinate responses [U4]. It does not prescribe a class per use case, a suffix, or a method name. `UserService` is therefore a **grouping**, not an operation — and it conflicts with the local C3 rule of one operation per component [L1:18].

#### B5. DDD: application services orchestrate; domain services hold cross-entity rules

Evans's application layer is thin, coordinates, and contains no business rules; domain services hold rules that span entities; interfaces should be intention-revealing and named in the ubiquitous language [U12]. No suffix is prescribed. Microsoft's DDD guidance aligns: application services orchestrate and contain no business logic; invariants belong in aggregates [U8][U10][U11].

This directly undermines `XManager`, `XHelper`, `XProcessor`, and `XUtil`: they name a mechanism or a vague role, not an intention [U12].

#### B6. CQRS and vertical slices: name the business task

CQRS commands should represent specific business tasks, not low-level data updates — "Book hotel room", not "Set ReservationStatus to Reserved" [U9]. Queries return DTOs and contain no domain logic [U9]. MediatR's handler interface is `Handle()` [U13], and Bogard's vertical-slice style deliberately uses one use case per request [U14].

These are valid conventions in a message-oriented architecture. They are **not** local conventions: the local contract mandates `execute()` [L1:18] and has no mediator.

#### B7. Naming-shape assessment

| Candidate | What it names | Example | Assessment |
|---|---|---|---|
| `<Verb><Object>` | Business operation | `PlaceOrder` | Best as the operation name; as a class it is a verb-phrase compromise |
| `<Verb><Object>UseCase` | Operation + role | `PlaceOrderUseCase` | Recommended for TS classes; local exemplar; redundant only at the definition site |
| `<Verb><Object>Interactor` | Martin's component role | `PlaceOrderInteractor` | Valid, but introduces a second vocabulary here |
| `XHandler` | Message handler | `PlaceOrderHandler` | Implies MediatR-style `handle()`; not local |
| `XCommand` | Message | `PlaceOrderCommand` | Names the request, not the operation class |
| `XService` | Layer/grouping | `OrderService` | Usually multiple operations; conflicts with C3's one-operation rule |
| `XManager` / `XHelper` / `XProcessor` / `XUtil` | Mechanism or vagueness | `OrderManager` | Avoid; not intention-revealing |
| `OrderPlacer` | Agent noun | — | Descriptive but indirect; uncommon here |
| `execute()` / `handle()` / `run()` | Method | `execute()` | `execute()` is mandated locally; `handle()` belongs to MediatR |

#### B8. Granularity is not fixed by any one source

- Cockburn's unit is the **user goal**, not the endpoint, screen, or table [U7].
- Martin defines use cases as application-specific business rules without fixing endpoint granularity [U5].
- CQRS uses one command/query per **business task** [U9].
- Bogard deliberately uses one use case per **request** [U14].
- The local contract says "one named business operation" without defining the boundary [L1:18].

A defensible local rule: **one business goal or transaction boundary per operation** — not one per endpoint, screen, or table. Reads are allowed to be simpler: `GetUser` is a lookup/subfunction; `ListOrders` and `SearchProducts` state read intent. `GetUser` is acceptable as a read operation but is weak as the main business vocabulary [U7].

#### B9. Naming as an anemia diagnostic

`UpdateUser(dto)` is a data-mutation label. It invites setters, bypassed invariants, and a service that knows the entity's fields. `ChangeEmailAddress` and `DeactivateAccount` name outcomes; they force the questions "what makes this valid?", "who may do it?", and "what transition is legal?" — which is exactly where domain behavior belongs [U1][U8][U12].

`PlaceOrder` is business-oriented; `CreateOrder` is persistence-oriented. Both may create a row, but only one names the business event.

Naming is a **signal, not proof**:

- A well-named method can still be anemic.
- A CRUD name can be legitimate in a genuinely simple domain [U3][U9].
- Mixed vocabulary — half business goals, half CRUD — usually indicates an unresolved modeling decision.

#### B10. Local contract and exemplars

| Local rule | What it fixes | What it leaves open |
|---|---|---|
| C3 [L1:18] | One named business operation; single `execute()`; injected ports; policy in application or domain | Class suffix, imperative vs noun class name, file name |
| Backend shape [L2:10] | `application/` with one file per use case | File naming pattern |
| NestJS [L3:24,42] | Pure class, one `execute()`, `application/use-cases/`; factory example `XUseCase` | Whether `XUseCase` is mandatory |
| Python [L5:13,31] | Module holding a named `execute()`; class not required | Module/class naming pattern |

The only explicit `XUseCase` spellings are the factory example [L3:42] and the test example [L4:60]. Both are **exemplars, not normative rules**. The Python examples use an unsuffixed operation class [L7:40] and a module-level `execute()` [L6:14].

The `UseCase` suffix is redundant at the definition site inside `application/use-cases/`, but not at TypeScript import sites (controller, module, test), where the folder is invisible. In Python the module path carries the operation, so the suffix adds less.

There is **no TypeScript application in this repository** (`**/*.ts` returned zero files); the NestJS guide is reference architecture, not evidence of local TS practice.

## Recommendations and alternatives

### R1. Judge three axes separately

1. **Dependency direction** — Clean Architecture: do inner layers depend on nothing outward? [U5][L1]
2. **Invariant ownership** — Domain modeling: is every rule enforced where every caller must obey it? [U1][U8]
3. **Operation naming** — Communication: does the name state a business outcome rather than a data mutation? [U7][U9]

None of the three implies the others. A codebase can pass axis 1 and fail axes 2 and 3.

### R2. Behavior placement heuristic

Place a rule in the domain when at least one of these holds:

- more than one use case must remember it;
- it must hold regardless of entry point;
- it defines a legal state transition;
- it is part of the domain's vocabulary;
- duplicating it would create inconsistent behavior.

Keep it in the use case when it is application-specific: orchestration, transaction scope, authorization, idempotency, or a policy choice that is not intrinsic to the domain.

Keep it at the edge when it is parsing, transport validation, serialization, or mapping.

### R3. Naming convention for this repo (recommendation, not a requirement)

**TypeScript**

- Class: `<Verb><Object>UseCase` — e.g. `PlaceOrderUseCase`, `ChangeShippingAddressUseCase`.
- File: `application/use-cases/<verb>-<object>.use-case.ts` — consistent with the existing `{entity}.entity.ts` / `{entity}.repository.ts` pattern.
- Method: `execute()` — already mandated [L1:18].
- Why: the class remains a noun phrase, the role is visible at import sites, the suffix matches the local exemplars, and the operation is still stated in business terms.

**Python**

- Module: `<verb>_<object>.py` — e.g. `place_order.py`, `change_shipping_address.py`.
- Callable: `execute()`.
- Class only when state or injected collaborators justify it; if used, `<Verb><Object>` with no suffix — e.g. `ApplyCoreRevision` [L7:40].
- Why: the module path carries the operation, matching existing practice [L6][L7]; a class is not required by the local guide [L5:13].

**Rejected alternatives**

- `PlaceOrder` as the TS class: cleaner operation name, but a verb-phrase class and inconsistent with the local exemplars/tests.
- `PlaceOrderHandler`: imports MediatR vocabulary and `handle()` semantics that the local contract does not use.
- `OrderPlacer`: agent noun; descriptive but less direct and inconsistent here.
- `OrderService`: groups multiple operations; conflicts with C3's one-operation rule.
- `ManageOrders` / `ProcessOrder`: hides the missing behavior and names no outcome.

**Consistency rule:** whichever shape is chosen, apply it to every use case. A mixed vocabulary is worse than either consistent choice.

### R4. Naming review heuristic

Ask of every use-case name:

1. Does it state a business outcome a domain expert would recognize?
2. Is it one operation, not a group (`Service`, `Manager`)?
3. Is it verb + object, not a table, endpoint, or screen?
4. Is `Create/Update/Delete` used only where the domain is genuinely CRUD?
5. If it changes state, is there a legal domain transition rather than a setter?
6. Would the name survive replacing the framework or transport?

A "no" on 1, 2, 3, or 6 is a naming finding. A "no" on 4 or 5 is a signal to inspect behavior placement.

### R5. For this repository specifically

- The local contract already prevents the classic anemic OO shape: entities have immutable identity, read-only accessors, valid-instance factories, and no setters [L3:17][L5:18]. The remaining risk is the **"clean but anemic"** shape: rich use cases, trivial entities, and no documented state-transition API.
- That risk is acceptable for simple tooling domains and should be a conscious choice, not an accident.
- If a domain grows real invariants, add a transition convention to the applicable guide (domain method returning a new instance, or pure domain function returning a typed result) before adding rich behavior. Do not add setters; they contradict the entity contract.
- The naming recommendation above is a convention proposal. Making it normative would require a feature-scoped change to the architecture guides, not a research brief.
- The repo's own Python tooling is a functional-domain example, not an anemic OO model: pure rules in `domain/` [L8][L9], orchestration in `execute()` operations [L6][L7].

## Limitations and open questions

- **Books not read:** Martin's *Clean Architecture* (2017), Fowler's *PoEAA* (2002), and Evans's *Domain-Driven Design* (2003). Claims rely on free articles, the DDD Reference, and vendor docs. No claim is made about specific class names used in those books.
- **Cockburn extract:** a 2000 pre-publication draft; the CRUD discussion is truncated. The "no consensus" finding is from that extract, not the published book.
- **No empirical evidence:** no controlled study shows that a naming scheme or rich model reduces defects or cost. The recommendations are clarity, consistency, and invariant-safety arguments, not measured outcomes.
- **No implementation audit:** only the cited files were read. No TypeScript application exists in this repo; no conformance claim is made for any destination.
- **Policy breadth:** the local C3 allows policy in application or domain [L1:18], broader than Evans's thin application layer [U12]. That is a local choice, not a universal Clean Architecture rule.
- **Mutable sources:** vendor docs and articles may change; recheck before treating any claim as current.
- **Open question:** should the local guides specify an entity state-transition convention? Currently they specify construction and read access only. TODO: requires a separate design decision and authorization.

## Reuse and supersession notes

- Reusable unchanged: the anemic/CA distinction; the behavior-placement table; the naming-shape assessment; the local contract comparison.
- Recheck before reuse: vendor docs and mutable articles; any change to `architecture/clean-architecture.md` or the stack guides; any new TypeScript application.
- Not reusable as policy: the naming recommendation is a proposal, not an existing rule. The local contract fixes only "one named business operation" and `execute()`.
- Durable publication: this combined record is the selected shape from the brief's proposal; the two-record alternative (`docs/research/architecture/anemic-domain-model/` and `docs/research/architecture/use-case-naming/`) was not created. Catalog entry added in `docs/research/README.md`. Status: durable record created and cataloged in the working tree; no Git commit was performed.
