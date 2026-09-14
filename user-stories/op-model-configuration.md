# User story — op-model-configuration

> **Created:** 2026-09-14
> **Title:** OpenCode model configuration
> **Status:** active
> **Epic:** developer-tooling
> **Affected areas:** `.opencode/skills/op-model/`, `opencode.json`, `opencode.jsonc`

## Persona

- A maintainer selecting an available subscribed model for an OpenCode agent without guessing provider or model identifiers.

## Goal

- **G:** Resolve live available models into typed records and surgically configure the selected agent only after deterministic provider selection.
  - Done when: model records have a complete typed contract, parsing and matching preserve their documented output, ambiguous providers require a user choice, and the final config edit remains surgical and validated.

## Scenario

- A maintainer names a model family, the skill resolves it from live `opencode models --verbose` output, asks when more than one provider matches, and updates only the selected agent's model field with a verified `provider/model` value.

## Acceptance criteria

- ✅ `models.py` declares and consistently uses a `TypedDict` covering `config`, `id`, `provider`, `name`, `cost_in`, and `cost_out`; `_num` has a typed parameter. Evidence: `.opencode/skills/op-model/scripts/models.py:31-39` `ModelRecord(TypedDict)`; `def _num(value: object) -> float:`; Bastion 🧱 (Backend & Scripts Architect) `[PASS]`.
- ✅ Deterministic checks preserve block parsing, malformed-block skipping, normalization, config/name matching, provider grouping, sorting, JSON-lines output, and no-match behavior. Evidence: Forge's syntax and deterministic parse/match checks exit 0; Bastion re-ran them clean on the final file.
- ✅ The skill continues to use live `opencode models` output as the only model-name authority and requires a user choice when multiple providers match. Evidence: the change is annotation-only; `op-model/SKILL.md` `1.0.1` Steps and provider-choice policy are unchanged; Vault 🔐 (Catalog Steward) `[PASS]`.
- ✅ Config editing remains surgical, parse-verified, and followed by a restart instruction; no model is invented or selected from memory. Evidence: `op-model/SKILL.md` config-edit and verification sections unchanged; Vault 🔐 (Catalog Steward) `[PASS]`.

## Change log

- 2026-09-14 — skill-debt-resolution-20260914: created the durable feature definition and planned a type-only record-contract correction; criteria remain pending during plan creation.
- 2026-09-14 — skill-debt-resolution-20260914: implemented `op-model` `1.0.1` with a `ModelRecord(TypedDict)` record contract and typed `_num` parameter; behavior preserved and Bastion 🧱 (Backend & Scripts Architect) `[PASS]`; DEBT-003 retired.

## Resolved decisions

- 2026-09-14 — The DEBT-003 correction adds no runtime-validation library or behavior-changing refactor; annotations and deterministic checks are sufficient with Bastion's architecture gate.
