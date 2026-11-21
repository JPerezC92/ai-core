# ADR 0010 — Architecture selection and the Interface boundary

- **Status:** Proposed — propagation is delivered in the same work unit; promotion to `Accepted` awaits explicit user acceptance
- **Date:** 2026-11-21

## Context

The shared contract stated one architecture: domain, application and infrastructure, applied to every project in every language, with a class-form application operation required "however small the operation is". That mandate was strengthened deliberately on 2026-11-12 by user decision D1 of `odd/tasks/2026-11-12-architecture-standardization.md`, and ADR 0005 carries the corresponding `Superseded` line.

The contract had no concept of project size or complexity. A one-file utility, a small modular tool and a service with real business boundaries were all governed by the same layer and operation rules, so a simple script could only be judged conforming or non-conforming — never simply appropriate. The same gap left the delivery edge undefined: `C4` and `C6` named it, but no rule said what a delivery edge owns, and physical placement differed between the backend, scripts and frontend owners without any stated principle.

Two observations from this repository informed the boundary rules, and neither is a conformance claim:

- `cli/aicore/src/` and `mcp-servers/system-one/src/` each carry a fourth top-level directory — `delivery/` and `mcp/` respectively — whose modules import only `application` and `domain`, while the composition entry points import the concrete adapters. Neither directory imports the other's adapters, and no shared contract authorized the arrangement.
- The testing contract's `T2` closed the list of approved unit targets around the use case, the parser/loader and the UI unit, so a pure rule or transformation had no approved unit boundary at all. `DEBT-055` records that class of finding being raised against real helper units.

## Decision

1. **Complexity levels.** A project selects L1 simple, L2 modular or L3 clean architecture. The level decides whether a layout is mandated; it never removes a responsibility that exists. L1 and L2 impose no layer folder and no operation form. The level is selected for the project and governs its principal boundaries; it is never applied recursively to helpers, local functions or auxiliary scripts.
2. **Evidence-based selection.** No count of lines, files, business operations, external effects, dependencies, transports or tests selects a level, and no project type automatically selects L3. One material architectural boundary is sufficient to justify L3 at any project size, and none justifies L1 or L2 at any project size.
3. **Prospective scope for the operation form.** The class, single `execute()` and constructor injection apply to L3 application operations; L1 and L2 are not compelled to any operation form. Every other obligation in that rule — no gratuitous base class, hierarchy, forwarding layer or wrapper, helpers stay functions, presentation is not an operation, policy lives in the operation or the domain and never in an adapter or a handler — remains at every level.
4. **Interface responsibility.** Every project with an external entry edge has an Interface responsibility that parses channel input, maps it in one step, delegates the work, and binds the outcome to the channel's response or error mechanism. It holds no business rule and may delegate to one or several operations. Its existence never implies a folder.
5. **Architectural versus technical dependencies.** The contract governs dependencies between components of the architecture. Transport frameworks, SDKs, schema validators, serializers, clients, drivers and storage libraries remain permitted at the component that owns that technology. At L3 an interface module reaches the project's own capabilities only through an application operation and imports no persistence adapter, repository implementation or infrastructure IO helper; an infrastructure adapter is symmetric and never imports an interface module. Neither may use a library to implement business behavior.
6. **Optional extraction.** An independent interface folder is named `interfaces/`, is optional, is separately authorized, and changes no application operation, domain type or port. Independence holds before extraction: while interface modules and adapters share the infrastructure layout they are still separate boundaries. A change that redesigns domain or application in order to extract is a separate redesign, and the extraction may not be its pretext. An approved differently-named folder is retained rather than renamed.
7. **Testing.** A pure rule module or transformation with no external representation and no effect is an approved unit target at every level, with no per-file obligation, no mandated directory and no fixture, factory, harness or runner configuration of its own.
8. **Recording.** Architecture classification is a working judgment, not a documentation obligation. A project-level architecture record is required only for a genuine project-level architectural decision or a change to an approved architecture.

This record explains the decision. The operative rules live in the owners listed under `## Propagation`, not here.

## Alternatives

- **Keep the universal class-first rule and add an exception for small work.** Rejected: an exception inside a universal mandate is exactly the implicit exemption the design was asked to avoid, and it would leave reviewers deciding case by case whether a project qualifies.
- **Express the levels as new application shapes.** Rejected: complexity is orthogonal to application shape, so "simple" and "modular" shapes would multiply the guide-mapping surface and confuse a shape with a size.
- **Put the whole policy in a new document at the architecture root.** Rejected: the navigation forbids a loose file at that root, and a separate document would compete with the contract that must own the rules.
- **Put the policy only in the navigation README.** Rejected: the Interface prohibitions are architectural rules; without an identifier the guides cannot map them and reviewers cannot cite them, which is the defect logged as F2/F3 in the 2026-11-12 feature.
- **Introduce a third contract family for interfaces.** Rejected: Interfaces is a responsibility of the same contract, not a third peer family, and a family would require new clearance, enrollment and navigation.
- **Make `interfaces/` part of the canonical layout.** Rejected: it contradicts the standing rule that no shape imposes a mandatory presentation directory, and the design explicitly makes the folder optional.
- **Adopt `inbound/` and `outbound/` folder names.** Rejected: they contradict the canonical `infrastructure/adapters/` and `infrastructure/repositories/` homes and would force a migration of existing code.
- **Restore ADR 0005's per-stack function-form freedom.** Rejected: that freedom let every stack choose per level; this decision is level-scoped and language-independent, so L3 keeps the class form in every language.
- **Enforce the level with a validator.** Rejected: the level is a judgment about boundaries, not a mechanically checkable property, and no tooling was authorized.

## Consequences

Small projects become lawful without layers, without operation classes and without documentation overhead, while L3 keeps every existing guarantee. The cost is that a reviewer must now ask which level applies before judging conformance, and must read the level statement a project records rather than assuming one.

Three consequences are recorded rather than resolved. The testing contract gained one approved target, so `T2` is longer and a future stack guide must map it. Existing projects are not migrated: `cli/aicore` keeps `delivery/` and `system-one` keeps `mcp/`, and nothing here claims they conform — the boundary rules were drafted from what those modules already do, which is not evidence that they satisfy every obligation. `DEBT-049`'s deferred question about lost normative text in the agnostic extraction remains open and is neither answered nor narrowed here.

No production code, test, dependency, permission or tooling change is authorized by this record.

## Historical accuracy

The requirement this decision replaces was **universal for the period 2026-11-12 to 2026-11-20** and was approved as universal on 2026-11-12 by user decision D1. This record amends it **prospectively**: it does not reinterpret that decision, does not claim it was originally scoped to L3, and does not rewrite ADR 0005's decision body or its `Superseded` line. Code and reviews from that period conformed to the rule as it then stood; this decision neither retroactively validates nor invalidates them. `odd/tasks/2026-11-12-architecture-standardization.md` remains accurate for its period and is not retro-edited.

## Propagation

| Owner                                                                                         | Rule carried                                                                                                                                                            |
| --------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.aicore/core/architecture/implementation/architecture.md` — `C1`                             | The level clause: obligations bind where the selected level requires the layers.                                                                                        |
| Same file — `C3`                                                                              | The complete operation rule, scoped in four blocks: L3, L1/L2, every level, and domain-model classification. No obligation retired; five re-scoped, ten left universal. |
| Same file — `C11`                                                                             | Levels, universal obligations, evidence-based selection, granularity, recording and boundaries.                                                                         |
| Same file — `C12`                                                                             | Interface existence, what it owns, delegation, architectural versus technical dependencies, L3 and L1/L2 dependency rules, composition.                                 |
| Same file — `C13`                                                                             | Placement, the `interfaces/` name, independence before extraction, the post-extraction rule, the extraction invariant, required evidence and authorization.             |
| Same file — `## Diagrams`                                                                     | The L3-only circular figure and the two deployment figures.                                                                                                             |
| `.aicore/core/architecture/implementation/architecture-boundaries.svg`                        | The circular L3 figure, embedded from the section above by relative path.                                                                                               |
| `.aicore/core/architecture/README.md`                                                         | Reading order step 0, the `C1`–`C13` range, and the never-mandatory `interfaces/` folder in the shape-scoped layout duty.                                               |
| `.aicore/core/architecture/implementation/shapes/backend.md`                                  | `## Applicability` level scope; `B1` interface placement and separation.                                                                                                |
| `.aicore/core/architecture/implementation/shapes/scripts.md`                                  | `## Applicability` level scope; `P1` conditional operation form; `P2` interface placement and separation.                                                               |
| `.aicore/core/architecture/implementation/shapes/frontend.md`                                 | `## Applicability` level scope; `F3` the presentation binding as this shape's Interface responsibility.                                                                 |
| `.aicore/core/architecture/implementation/stacks/_template.md`                                | `C11`–`C13` mapping rows and the interface-placement mapping duty.                                                                                                      |
| `.aicore/core/architecture/implementation/stacks/typescript/nestjs.md`                        | `C11`–`C13` rows; controller scope and isolation.                                                                                                                       |
| `.aicore/core/architecture/implementation/stacks/typescript/react.md`                         | `C11`–`C13` rows; operation scope.                                                                                                                                      |
| `.aicore/core/architecture/implementation/stacks/python.md`                                   | `C11`–`C13` rows; handler versus composition-root separation.                                                                                                           |
| `.aicore/core/architecture/testing/architecture.md` — `T2`                                    | The pure rule or transformation unit target and its no-per-file, no-infrastructure limits.                                                                              |
| `.aicore/core/architecture/testing/stacks/_template.md`, `typescript.md`, `python.md`         | Continuation of the target in each guide's mapping or parity table.                                                                                                     |
| `.aicore/core/knowledge/agents.md` — `### Clean architecture (language-agnostic) (HARD RULE)` | Level selection as the first step of the mandatory reading chain.                                                                                                       |
| `.opencode/agents/bastion.md`, `atrium.md`, `crucible.md`                                     | Obligation-ID range extended to `C1`–`C13`.                                                                                                                             |
| `docs/architecture/decisions/0005-use-case-organization-and-naming.md`                        | `Amended` line recording the prospective narrowing.                                                                                                                     |
| `docs/architecture/README.md`                                                                 | Navigation to this record and the corrected supersession sentence.                                                                                                      |
| `odd/features/architecture-contract.md`                                                       | Requirements `R1` and `R18`–`R26`.                                                                                                                                      |
