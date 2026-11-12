# Architecture documentation

## Purpose and selection

These documents describe intended architecture, not verified implementation conformance. Documentation approval does not certify existing application code. Future code adoption/remediation requires separate authorization and evidence.

Read in order:

1. `architecture/implementation/architecture.md` — common layers, dependencies, ports, operations, mapping/composition, failures, serialization, and helper semantics.
2. Applicable shapes: `architecture/implementation/shapes/frontend.md`, `architecture/implementation/shapes/backend.md`, `architecture/implementation/shapes/scripts.md`. Python backend tooling may select both backend and scripts; a language name is not a shape.
3. Applicable concrete implementation guide below; it maps rather than replaces the common/shape contract.
4. `architecture/testing/architecture.md`, then its selected testing guide under `architecture/testing/stacks/`. Testing design has its own authority and template; do not infer test rules from implementation examples.

| Implementation guide | Shape | Documentation status |
|---|---|---|
| `architecture/implementation/stacks/typescript/react.md` | Frontend | reference |
| `architecture/implementation/stacks/typescript/nestjs.md` | Backend | reference |
| `architecture/implementation/stacks/python.md` | Scripts; backend where applicable | reference; framework selections remain unselected |

Concrete libraries and aliases preserve reference-architecture choices, not destination tool bindings. The destination selects its tooling in project-owned configuration without weakening the common contract. Follow applicable documented specifics for the concerns they cover; for uncovered concerns, including partial guide coverage or a stack with no applicable guide, apply the agnostic contract and applicable shapes directly. Missing guide coverage alone never blocks implementation or review and never requires creating a guide. Do not import unrelated language/framework rules or infer approval from current code patterns. Execution choices require evidenced project-owned bindings, not an invented runner or convention. A real contradiction, missing authority, or missing evidence needed for a decision still uses the agent runtime's uncertainty route.

## Ownership and extension

Layer duties are defined under `## Content model` in this file. Runtime specs retain authority, scope, warmup/execution procedures, edit checkpoints, review gates, dependency ownership, reporting, and uncertainty handling. A document pointer does not grant execution permission.

Copy `architecture/implementation/stacks/_template.md` before writing another implementation guide. Keep its heading order and map every C1–C10 obligation and selected shape obligation; explain applicability and language/runtime differences. Unsupported choices remain explicit open decisions, not invented equivalents or unexplained N/A. Proposed guides are not claims of reviewed documentation or implementation conformance.

Never edit a distributed architecture file. A destination may document a different stack in its own guide, copied from `architecture/implementation/stacks/_template.md` or `architecture/testing/stacks/_template.md`; an unbound path survives every sync. Guide authoring is an optional documentation extension, not a prerequisite for applying the agnostic fallback.

## Content model

Every architecture rule and obligation lives in exactly one of those three layers; `## Contract boundaries` states constraints on the documents themselves and the templates state authoring duties, so both are cited by section rather than by rule identifier.

1. **Agnostic contract** — `architecture/implementation/architecture.md` (`C1`–`C10`) and `architecture/testing/architecture.md` (`T` rules). Each normative rule in a `C`, `B`, `F`, `P`, or `T` owner carries a stable identifier. A rule is stated here once, completely, and is never restated below.
2. **Shape** — `architecture/implementation/shapes/frontend.md`, `backend.md`, and `scripts.md` (`F`, `B`, and `P` obligations). A shape obligation carries an identifier and specializes the common contract for one application shape. A shape may add responsibility, layout, and boundary detail; it does not restate a `C` rule.
3. **Language guide** — `architecture/implementation/stacks/` and `architecture/testing/stacks/`. A guide states only how its language achieves a cited obligation, and cites that identifier in the body and in its mapping or parity table. A guide never restates a contract requirement as prose.

Two contract families are peers, each with its own contract, optional shapes, and stack guides:

    architecture/
      README.md                 navigation and this model
      implementation/           implementation family
        architecture.md         common contract (C1-C10)
        shapes/                 application-shape obligations (F, B, P)
        stacks/                 implementation guides
      testing/                  testing family
        architecture.md         test contract (T rules)
        stacks/                 testing guides

A new family takes the same shape: a peer directory holding its contract, its shapes where the family needs them, and its stacks. Never add a family as a loose file at the `architecture/` root.

Four duties follow:

- **Cite, do not copy.** If a guide sentence can be deleted without losing any rule the cited owner does not already state, that sentence was a restatement and does not belong in the guide.
- **One edit home.** Changing a rule edits its agnostic contract only. Guides citing the identifier stay correct unless their language-specific achievement stops satisfying it.
- **Verifiable coverage.** A mapping or parity cell that claims coverage without citing an identifier is a defect. `N/A` requires a language, runtime, or scope reason stating why the obligation cannot be achieved by guide content.
- **New rules.** Add the rule with a new identifier in its owning contract, then map it in every applicable guide. Never introduce a rule directly in a guide.
- **Canonical layout is shape-scoped.** The shapes own each application shape's canonical directory organization — which responsibilities exist and where they live — and every language applies that same layout for the shape. A language guide spells the native folder and file names of that layout and never substitutes a different organization for an equivalent responsibility. A responsibility that does not exist in a shape or project creates no directory, and no shape introduces a mandatory `presentation/` directory.

## Contract boundaries

- No file under `architecture/` references a path outside `architecture/`. These documents point to each other only; agent runtimes, knowledge documents, and source-local records point here.
- Architecture states its rules completely. A rule's content is never deferred to another document. Statements about who holds execution authority, permissions, edits, or gates are not references and remain as written.
- Every destination receives identical bytes. That guarantees distribution, not conformance: a reference library, runner, or framework named here remains a reference choice, adopted by the destination in its own configuration or its own guide.

## Testing location transition

The sole testing documents are `architecture/testing/architecture.md` and `architecture/testing/stacks/{_template,typescript,python}.md`. The obsolete root compatibility files and their clearance rows are removed. Testing decisions, reviewed guide status, parity, and project-owned selections are preserved; relocation is not a new testing decision or implementation-conformance claim.

New architecture paths arrive with their consumers as one applicable set and require destination-authorized `core-sync init --bind-cleared` enrollment at the selected revision; `apply` alone does not enroll missing or markerless paths.
