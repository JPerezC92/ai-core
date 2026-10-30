# ADR 0002 — Testing architecture layering

- **Status:** Accepted
- **Date:** 2026-10-25
- **Amended:** 2026-10-30 — path references relocated to `architecture/testing/` by ADR 0003; the `testing-architecture/` tree no longer exists. Decision text below is unchanged.

## Context

Crucible's runtime spec carried three different concerns at once: the language-agnostic test pyramid, the TypeScript reference rules, and the Python reference rules. TypeScript was documented first and is the depth reference; Python was added later and was materially thinner. A single file made a new language look like a variation to improvise rather than a stack to document deliberately.

The test pyramid itself is a user decision and is not being reopened. The problem is placement, parity, and the distinction between shared rules and stack-specific implementation.

## Decision

- `testing-architecture/architecture.md` owns the language-agnostic test contract: levels, boundaries, organization, data and doubles, execution/verdict separation, and stack-guide selection.
- `testing-architecture/stacks/_template.md` is the single template for a stack guide. Every copied guide keeps the same ten sections.
- `testing-architecture/stacks/typescript.md` is the reference-depth implementation. It preserves the existing TypeScript decisions.
- `testing-architecture/stacks/python.md` is a peer implementation. It preserves the existing Python decisions and must match the TypeScript guide section by section; only language or runtime differences may be declared.
- `knowledge/agents.md` retains the clean-architecture contract and points to the testing contract instead of duplicating the full test-level block.
- `.opencode/agents/crucible.md` reads the contract and the applicable stack guide, routes by file type, and emits `[UNCERTAIN]` when no guide applies. It carries no duplicate stack rulebook.
- A new stack guide requires an authorized ODD feature, official-documentation research, repository evidence, and a parity review. It remains `proposed` until reviewed.
- `testing-architecture/` is a dedicated shared area, separate from `knowledge/` registers and policies. Its location is provisional and may be revisited without changing the contract or the existing stack decisions.

## Alternatives

- Keep everything in Crucible's spec — rejected; it preserves the Python/TypeScript imbalance and gives no extension point.
- Put all documents in `knowledge/` — rejected; it mixes an architecture rulebook with registers and policies.
- Put the shared guides in `docs/architecture/` — rejected for shared content; that area is source-local and is not distributed.
- Copy TypeScript mechanically into Python — rejected; UI, browser, and framework rules have no Python equivalent. Parity means equal rigor and declared differences, not identical mechanics.
- Add a new agent per stack — rejected; the test architecture role is shared, and the stack guide is the variable unit.

## Consequences

- Existing pyramid, boundary, and tooling decisions remain in force; this ADR changes their home, not their meaning.
- The shared surface grows by an architecture contract, a template, and two stack guides. Clearance, the README structure map, and the Crucible 🔥 (Test Architect) runtime spec must point to them.
- Every future stack guide has a repeatable shape and a review gate. A thinner guide is a defect rather than an implicit shortcut.
- The repository may later move `testing-architecture/`; doing so must preserve the contract, the stack-guide parity rule, and the existing decisions.
