# User story — clean-architecture-contract

> **Created:** 2026-10-11
> **Title:** Clean architecture contract
> **Status:** active
> **version:** 1.1.0
> **Epic:** core-governance
> **Affected areas:** `knowledge/agents.md`, `.opencode/agents/atrium.md`, `.opencode/agents/bastion.md`, `.opencode/agents/crucible.md`, `.opencode/agents/forge.md`, `.opencode/agents/marshal.md`, `.opencode/agents/sentinel.md`, `.opencode/skills/op-agent-creator/SKILL.md`

## Persona

- A maintainer who needs future agents to enforce clean architecture in every language, with each language's rules and libraries grouped and reusable.

## Goal

- **G:** One language-agnostic architecture contract applies in every language, every rulebook is grouped by language first with libraries nested, and no language section suspends the contract.
  - Done when: `knowledge/agents.md` holds the language-agnostic contract, each rulebook opens with a language-agnostic subsection followed by `TypeScript` (and `Python` where the language applies), and the test pyramid diagram is intact.

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
- ✅ Every obligation from the pre-change rulebooks survives in the reorganized specs; the only removals are the recorded replacements. Evidence: the `### Rulebook` sections of `.opencode/agents/atrium.md`, `.opencode/agents/bastion.md`, `.opencode/agents/crucible.md`, and `.opencode/agents/forge.md`.

## Change log

- 2026-10-11 — clean-architecture-contract-20261011: made the contract language-agnostic, grouped rulebooks by language, and kept library mappings explicit.

## Resolved decisions

- 2026-10-11 — Content is grouped by language first; libraries nest under their language. NestJS is the worked example for mapping a new library.
- 2026-10-11 — React uses a non-Hook `execute()` inside the existing hooks file. The custom Hook passes it to `queryFn` or `mutationFn`. Component-plus-Hook tests stay unchanged.
- 2026-10-11 — Python conforms to the agnostic contract; its module/IO/type rules are syntax specifics.
