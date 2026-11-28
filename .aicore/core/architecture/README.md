# Architecture documentation

## Purpose and selection

These documents describe intended architecture, not verified implementation conformance. Documentation approval does not certify existing application code. Future code adoption/remediation requires separate authorization and evidence.

Read in order. For routine implementation and architecture-dependent explanation, the section-based route below permits bounded reads, not bounded obligations. Read the applicable owner text before acting; if a responsibility, dependency, cross-reference or material uncertainty emerges, expand the read before continuing. No omitted section ceases to bind. If bounded retrieval is unavailable, read the whole file. Content already current may be reused unless an owner requires a full or fresh read.

0. Read `C11` in `.aicore/core/architecture/implementation/architecture.md` before applying a layer, operation or folder obligation. Use an existing project's approved architecture; a new selection follows its evidence, not ODD task classification. Nothing here authorizes a migration.
1. Read the common contract's applicable `C` sections for the responsibilities and dependencies involved. At every level consider decisions and helpers, boundaries and mapping, failures, serialization, naming and external output. Domain models, records, pure rules, ports, projections, persistence and transactions trigger their applicable `C8` or `C9` text at any level; do not exclude either by level. For `C14`, read its introduction, compatibility/ownership/verification and every affected channel, not unrelated channels. For structure selection or interface movement consult the applicable diagrams.
2. Read the applicable responsibilities in shapes: `.aicore/core/architecture/implementation/shapes/frontend.md`, `.aicore/core/architecture/implementation/shapes/backend.md`, `.aicore/core/architecture/implementation/shapes/scripts.md`. Python backend tooling may select both backend and scripts; a language name is not a shape.
3. Read the applicable sections of the concrete implementation guide below, including its applicability, language/import and deployment conventions and the mappings for the responsibilities involved. Layer/operation, domain, persistence, interface, serialization and channel sections apply when their responsibilities exist; the guide maps rather than replaces the common/shape contract.
4. For test design, edits and verification, read `.aicore/core/architecture/testing/architecture.md`, then applicable documented specifics of the selected testing guide under `.aicore/core/architecture/testing/stacks/`. Testing design has its own authority and template; do not infer test rules from implementation examples. Missing coverage follows that contract's fallback, not another stack's conventions.

Architecture and conformance reviews read the complete owner text required for their declared scope, including applicable diagrams and testing; guide authoring and parity assessments retain their full-contract, template, guide and fresh-read gates. This route never relaxes another owner's full or fresh read, approval, execution or review requirement.

| Implementation guide                                                    | Shape                             | Documentation status                              |
| ----------------------------------------------------------------------- | --------------------------------- | ------------------------------------------------- |
| `.aicore/core/architecture/implementation/stacks/typescript/react.md`   | Frontend                          | reference                                         |
| `.aicore/core/architecture/implementation/stacks/typescript/nestjs.md`  | Backend                           | reference                                         |
| `.aicore/core/architecture/implementation/stacks/typescript/scripts.md` | Scripts                           | proposed                                          |
| `.aicore/core/architecture/implementation/stacks/python.md`             | Scripts; backend where applicable | reference; framework selections remain unselected |

Concrete libraries and aliases preserve reference-architecture choices, not destination tool bindings. The destination selects its tooling in project-owned configuration without weakening the common contract. Follow applicable documented specifics for the concerns they cover; for uncovered concerns, including partial guide coverage or a stack with no applicable guide, apply the agnostic contract and applicable shapes directly. Missing guide coverage alone never blocks implementation or review and never requires creating a guide. Do not import unrelated language/framework rules or infer approval from current code patterns. Execution choices require evidenced project-owned bindings, not an invented runner or convention. A real contradiction, missing authority, or missing evidence needed for a decision still uses the agent runtime's uncertainty route.

## Architecture decision procedure

Apply this sequence to implementation and review work. Steps 1–3 establish the setting, step 4 the level, steps 5–7 the placement, and steps 8–10 the checks.

1. Identify whether the task belongs to an existing project or a new project.
2. Read the project's approved architecture and the applicable AICore contracts.
3. Identify the responsibilities, external boundaries and consumers the task involves.
4. Evaluate the architecture's complexity and select `L1`, `L2` or `L3` under `C11` — only when the selection is not already fixed by the project's approved architecture.
5. Select the applicable application shape.
6. Determine whether interface responsibilities exist — any external entry edge creates one (`C12`).
7. Place the interface code according to the chosen shape and its approved structure; an independent `interfaces/` folder exists only where `C13` authorizes one.
8. Prevent business and transport responsibilities from mixing.
9. Validate the dependency boundaries with focused, proportionate checks.
10. Document any proposed deviation and request approval before changing an architectural convention.

`L1`, `L2` and `L3` are alternatives, not stages: a project does not pass through every level, and step 4 is skipped when an existing project already has an approved structure. Classifying a small artifact is a working judgment and requires no record (`C11`).

## Ownership and extension

Layer duties are defined under `## Content model` in this file. Runtime specs retain authority, scope, warmup/execution procedures, edit checkpoints, review gates, dependency ownership, reporting, and uncertainty handling. A document pointer does not grant execution permission.

Copy `.aicore/core/architecture/implementation/stacks/_template.md` before writing another implementation guide. Keep its heading order and map every C1–C14 obligation and selected shape obligation; explain applicability and language/runtime differences. Unsupported choices remain explicit open decisions, not invented equivalents or unexplained N/A. Proposed guides are not claims of reviewed documentation or implementation conformance.

Never edit a distributed architecture file. A destination may document a different stack in its own guide, copied from `.aicore/core/architecture/implementation/stacks/_template.md` or `.aicore/core/architecture/testing/stacks/_template.md`; an unbound path survives every sync. Guide authoring is an optional documentation extension, not a prerequisite for applying the agnostic fallback.

## Content model

Every architecture rule and obligation lives in exactly one of those three layers; `## Contract boundaries` states constraints on the documents themselves and the templates state authoring duties, so both are cited by section rather than by rule identifier.

1. **Agnostic contract** — `.aicore/core/architecture/implementation/architecture.md` (`C1`–`C14`) and `.aicore/core/architecture/testing/architecture.md` (`T` rules). Each normative rule in a `C`, `B`, `F`, `P`, or `T` owner carries a stable identifier. A rule is stated here once, completely, and is never restated below.
2. **Shape** — `.aicore/core/architecture/implementation/shapes/frontend.md`, `backend.md`, and `scripts.md` (`F`, `B`, and `P` obligations). A shape obligation carries an identifier and specializes the common contract for one application shape. A shape may add responsibility, layout, and boundary detail; it does not restate a `C` rule.
3. **Language guide** — `.aicore/core/architecture/implementation/stacks/` and `.aicore/core/architecture/testing/stacks/`. A guide states only how its language achieves a cited obligation, and cites that identifier in the body and in its mapping or parity table. A guide never restates a contract requirement as prose.

Two contract families are peers, each with its own contract, optional shapes, and stack guides:

    .aicore/core/architecture/
      README.md                 navigation and this model
      implementation/           implementation family
        architecture.md         common contract (C1-C14)
        shapes/                 application-shape obligations (F, B, P)
        stacks/                 implementation guides
      testing/                  testing family
        architecture.md         test contract (T rules)
        stacks/                 testing guides

A new family takes the same shape: a peer directory holding its contract, its shapes where the family needs them, and its stacks. Never add a family as a loose file at the `.aicore/core/architecture/` root.

Five duties follow:

- **Cite, do not copy.** If a guide sentence can be deleted without losing any rule the cited owner does not already state, that sentence was a restatement and does not belong in the guide.
- **One edit home.** Changing a rule edits its agnostic contract only. Guides citing the identifier stay correct unless their language-specific achievement stops satisfying it.
- **Verifiable coverage.** A mapping or parity cell that claims coverage without citing an identifier is a defect. `N/A` requires a language, runtime, or scope reason stating why the obligation cannot be achieved by guide content.
- **New rules.** Add the rule with a new identifier in its owning contract, then map it in every applicable guide. Never introduce a rule directly in a guide.
- **Canonical layout is shape-scoped.** The shapes own each application shape's canonical directory organization — which responsibilities exist and where they live — and every language applies that same layout for the shape. A language guide spells the native folder and file names of that layout and never substitutes a different organization for an equivalent responsibility. A responsibility that does not exist in a shape or project creates no directory, and no shape or project introduces a mandatory `presentation/` or `interfaces/` directory.

## Contract boundaries

- No file under `.aicore/core/architecture/` references a path outside `.aicore/core/architecture/`. These documents point to each other only; agent runtimes, knowledge documents, and source-local records point here.
- Architecture states its rules completely. A rule's content is never deferred to another document. Statements about who holds execution authority, permissions, edits, or gates are not references and remain as written.
- Every destination receives identical bytes. That guarantees distribution, not conformance: a reference library, runner, or framework named here remains a reference choice, adopted by the destination in its own configuration or its own guide.

## Testing location transition

The sole testing documents are `.aicore/core/architecture/testing/architecture.md` and `.aicore/core/architecture/testing/stacks/{_template,typescript,python}.md`. The obsolete root compatibility files and their clearance rows are removed. Testing decisions, reviewed guide status, parity, and project-owned selections are preserved; relocation is not a new testing decision or implementation-conformance claim.

New architecture paths arrive with their consumers as one applicable set and require destination-authorized `core-sync init --bind-cleared` enrollment at the selected revision. An `apply` also binds a newly cleared `raw` source and creates its absent target; a missing or markerless **region** path is enrolled by `init` alone.
