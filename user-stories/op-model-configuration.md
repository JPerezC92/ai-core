# User story — op-model-configuration

> **Created:** 2026-09-14
> **Title:** OpenCode model configuration
> **Status:** active
> **version:** 1.0.0
> **Epic:** developer-tooling
> **Affected areas:** `.opencode/skills/op-model/`, `opencode.json`, `opencode.jsonc`

## Persona

- A maintainer selecting an available subscribed model for an OpenCode agent without guessing provider or model identifiers.

## Goal

- **G:** Resolve live available models into typed records and surgically configure the selected agent only after deterministic provider selection.
  - Done when: model records have a complete typed contract, parsing and matching preserve their documented output, ambiguous providers require a user choice, and the final config edit remains surgical and validated. Evidence: `.opencode/skills/op-model/SKILL.md` `### Steps` items 2–9; `.opencode/skills/op-model/scripts/models.py` `ModelRecord`, `parse_records`, `matches`, and `main`.

## Scenario

- A maintainer names a model family, the skill resolves it from live `opencode models --verbose` output, asks when more than one provider matches, and updates only the selected agent's model field with a verified `provider/model` value.

## Acceptance criteria

- ✅ `models.py` declares and consistently uses a `TypedDict` covering `config`, `id`, `provider`, `name`, `cost_in`, and `cost_out`; `_num` has a typed parameter. Evidence: `.opencode/skills/op-model/scripts/models.py` `ModelRecord(TypedDict)` and `def _num(value: object) -> float:`; Bastion 🧱 (Backend & Scripts Architect) `[PASS]`.
- ✅ Deterministic checks preserve block parsing, malformed-block skipping, normalization, config/name matching, provider grouping, sorting, JSON-lines output, and no-match behavior. Evidence: durable checkpoint `64fae1bf4aa5978e5a8a14ce63a30fca11905660` records the deterministic behavior checks and Bastion 🧱 (Backend & Scripts Architect) `[PASS]`; `.opencode/skills/op-model/scripts/models.py` symbols `ModelRecord(TypedDict)`, `parse_records`, `matches`, and `main`.
- ✅ The skill uses live `opencode models` output as the only model-name authority and requires a user choice when multiple providers match. Evidence: `.opencode/skills/op-model/SKILL.md` `### Steps` items 2–3.
- ✅ Config editing remains surgical, parse-verified, and followed by a restart instruction; a missing config is created only after the user confirms the exact preview; no model is invented or selected from memory. Evidence: `.opencode/skills/op-model/SKILL.md` `### Steps` items 4–9; Vault 🔐 (Catalog Steward) current catalog audit `[PASS]`, 2026-10-09.

## Change log

- 2026-10-09 — aicore-all-files-pr-20261008: made confirmation of the exact preview an explicit prerequisite for creating a missing config, alongside the existing surgical model edit.
- 2026-09-14 — skill-debt-resolution-20260914: created the feature definition; added the `ModelRecord` typed record contract (`op-model` 1.0.1).

## Resolved decisions

- 2026-09-14 — the skill uses typed records and deterministic checks; it adds no runtime-validation dependency or behavior-changing refactor.
