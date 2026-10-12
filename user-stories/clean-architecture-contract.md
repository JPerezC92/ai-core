# User story — clean-architecture-contract

> **Created:** 2026-10-11
> **Title:** Clean architecture contract
> **Status:** active
> **version:** 1.2.0
> **Epic:** core-governance
> **Affected areas:** `knowledge/agents.md`, `.opencode/agents/atrium.md`, `.opencode/agents/bastion.md`, `.opencode/agents/crucible.md`, `.opencode/agents/forge.md`, `.opencode/agents/marshal.md`, `.opencode/agents/sentinel.md`, `.opencode/skills/op-agent-creator/SKILL.md`

## Persona

- A maintainer who needs future agents to enforce clean architecture in every language, with each language's rules and libraries grouped and reusable.

## Goal

- **G:** One language-agnostic architecture contract applies in every language, every rulebook is grouped by language first with libraries nested, and no language section suspends the contract.
  - Done when: the shared contract, language interpretations, `execute()`, folder design, and test pyramid remain coherent; implementation and review roles apply them to bounded changes, and any nonconforming file included in a plan receives its necessary rework rather than a legacy exemption.

## Scenario

- An agent implements a Python skill script or a React feature. The language-agnostic contract still requires a named use case with `execute()`. The TypeScript→React section still renders the component with the real Hook and mocks only the service. The TypeScript→NestJS section still uses `application/use-cases/` and a single `execute()`. The Python section maps domain, application, infrastructure, and composition before its syntax rules.

## Acceptance criteria

- ✅ `knowledge/agents.md` states the language-agnostic contract and requires `execute()`. Evidence: `knowledge/agents.md` `### Clean architecture (language-agnostic) (HARD RULE)`.
- ✅ No language section suspends the contract. Evidence: `.opencode/agents/bastion.md` Python section; verification: `uv run --frozen python3 -B -c "from pathlib import Path; t=Path('.opencode/agents/bastion.md').read_text(); assert 'suspended for Python files' not in t; assert 'language-agnostic' in t; print('no suspension: PASS')"`.
- ✅ Sentinel 🛡️ (Quality Guardian) and Marshal 🎖️ (HR Director) enforce the structure: `SP-12` and the Runtime Spec Format require a language-agnostic Rulebook subsection before the first language section. Evidence: `.opencode/agents/sentinel.md` `SP-12`; `.opencode/agents/marshal.md` Runtime Spec Format.
- ✅ Each rulebook is grouped by language first; every language-specific obligation is generalized into the language-agnostic subsection, which also states the folder layout. Backend names its layers domain, application, infrastructure. Evidence: `.opencode/agents/bastion.md`, `.opencode/agents/atrium.md`, `.opencode/agents/crucible.md` `### Rulebook`.
- ✅ React keeps the Hook as the adapter; `execute()` is a non-Hook callable in the existing hooks file, passed to `queryFn` or `mutationFn`. Evidence: `.opencode/agents/atrium.md` Hook rule.
- ✅ The language-agnostic section carries an agnostic `Test Pyramid Overview` (three generic levels), and the TypeScript section carries the concrete two-column diagram with `**Key rule:**`, Vitest for unit/integration and Playwright for end-to-end. Evidence: `.opencode/agents/crucible.md` `##### Test Pyramid Overview` and `#### TypeScript`.
- ✅ Python maps domain, application (use case `execute()`), infrastructure, and composition; the concrete module roles are in the project region. Evidence: `.opencode/agents/bastion.md` `##### Layers (Python) — domain, application, infrastructure` and `## Project extensions` → `### Local Configuration`.
- ✅ Python tests follow the pyramid and mirror the layers. Evidence: `.opencode/agents/crucible.md` `##### Python Test Pyramid`.
- ✅ **CA5 — Semantic preservation:** Valid architectural obligations and concrete library interpretations survive or are translated without loss. Obsolete, conflicting, or noncompliant definitions are explicitly replaced or retired against the approved contract, not preserved merely because they existed before. Before-copies establish change history; they are not an architectural authority. Proving surfaces: the revised Rulebook/Workflow sections and the shared contract, assessed by semantic review.
- ✅ **CA1 — Applicable reads and gates:** Before an assigned behavior slice, the implementer reads the shared contract and applicable role/language definitions plus affected code/test/documentation dependencies. Frontend, backend/script, and test review use their actual owners; an unconditional frontend gate does not override the backend/Python gate. Proving surfaces: implementation warmup and gate routing in `.opencode/agents/forge.md`, plus the architect/test specs.
- ✅ **CA2 — Snapshot-bound architecture evidence:** Reviews state their scope and reviewed snapshot, assess responsibilities and dependency direction by reading, and do not substitute test execution for architectural judgment. Evidence is reused only when its relevant content and dependencies remain unchanged. Proving surfaces: architecture-review scope and reporting rules.
- ✅ **CA3 — Required touched-file rework:** A file included in a plan that violates the approved design must be reworked within that plan, with the necessary supporting files, tests, and documentation declared before editing. Existing noncompliance is neither grandfathered nor mislabeled compliant; unrelated repository-wide migrations are not implied. Proving surfaces: the shared architecture contract, implementer scope rules, and planning discovery/manifest gates.
- ✅ **CA4 — Effective dependency and error contracts:** Static dependency direction is distinguished from runtime calls: application may invoke effects through injected domain ports without depending on concrete infrastructure. Returned business failures are distinguished from boundary/programming exceptions; transport serialization belongs at the delivery edge. Detailed language rules, examples, and local extensions agree with these obligations rather than weakening them. Proving surfaces: the shared contract and affected language profiles.

## Change log

- 2026-10-12 — implementation-enforcement-20261012: delivered per-owner gate routing and impact-bounded reads (`forge.md`), snapshot-bound read-based review (`atrium`/`bastion`/`crucible`/`sentinel`), the dependency/runtime-port/error/serialization distinctions (`knowledge/agents.md`, `bastion.md`), and the preservation-vs-retirement + nonconforming-planned-file rules.
- 2026-10-11 — workflow-contract: approved bounded architecture review, correct gate routing, explicit dependency/error boundaries, and required rework for nonconforming planned files.
- 2026-10-11 — clean-architecture-contract-20261011: made the contract language-agnostic, grouped rulebooks by language, and kept library mappings explicit.

## Resolved decisions

- 2026-10-11 — Content is grouped by language first; libraries nest under their language. NestJS is the worked example for mapping a new library.
- 2026-10-11 — React uses a non-Hook `execute()` inside the existing hooks file. The custom Hook passes it to `queryFn` or `mutationFn`. Component-plus-Hook tests stay unchanged.
- 2026-10-11 — Python conforms to the agnostic contract; its module/IO/type rules are syntax specifics.
- 2026-10-11 — Nonconforming files included in an implementation plan are reworked in that plan; no blanket legacy exemption or unrelated repository-wide migration is authorized.
