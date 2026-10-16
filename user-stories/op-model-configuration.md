<!-- core:begin -->
# User story — op-model-configuration

> **Created:** 2026-09-14
> **Title:** OpenCode model configuration
> **Status:** active
> **version:** 1.2.0
> **Epic:** developer-tooling
> **Affected areas:** `.opencode/skills/op-model/`, `opencode.json`, `opencode.jsonc`

## Persona

- A maintainer selecting an available subscribed model for an OpenCode agent without guessing provider or model identifiers.

## Goal

- **G:** The maintainer can choose a model from what is actually available and have only that agent reconfigured, without guessing identifiers or losing unrelated configuration.
  - Done when: available models are resolved from live output and presented with enough information to compare candidates, an ambiguous provider requires an explicit user choice, and the resulting configuration edit is limited to the selected agent and verified before it takes effect.

## Scenario

- The maintainer names a model family. The skill resolves it from live `opencode models` output and presents each candidate with its `provider/model` selector — plus its in/out cost when the live source provides one — asks when more than one provider matches, and updates only the selected agent's model field with a verified `provider/model` value.

## Acceptance criteria

- ✅ **AC1:** Each available model is presented with its `provider/model` selector (identifier and provider), plus its in/out cost when the live source provides one, so the maintainer can compare candidates before choosing.
- ✅ **AC2:** Model resolution uses live `opencode models` output as the only authority for what is available; no model identifier is supplied from memory or assumption.
- ✅ **AC3:** When more than one provider offers a matching model, the maintainer is asked to choose rather than having one selected for them.
- ✅ **AC4:** The configuration change is limited to the selected agent's model field, is parse-verified after writing, and is followed by a restart instruction.
- ✅ **AC5:** A missing configuration file is created only after the maintainer confirms the exact content preview.
- ✅ **AC6:** Unrecognized or malformed model output is skipped rather than producing a fabricated record, and a no-match is reported as a no-match.

## Proof

- AC1 → `.opencode/skills/op-model/scripts/op_model_lookup/infrastructure/cli.py` `render_selection` · `.opencode/skills/op-model/scripts/op_model_lookup/infrastructure/test_cli.py` grouped cost-segment cases (cost shown only when the source provides it) · `.opencode/skills/op-model/scripts/op_model_lookup/e2e/test_models_cli.py` selector-listing cases
- AC2 → `.opencode/skills/op-model/SKILL.md` `### Steps` items 2–3
- AC3 → `.opencode/skills/op-model/SKILL.md` `### Steps` item 3
- AC4 → `.opencode/skills/op-model/SKILL.md` `### Steps` items 4–9
- AC5 → `.opencode/skills/op-model/SKILL.md` `### Steps` item 6 · `### Troubleshooting` missing-config confirmation rule
- AC6 → `.opencode/skills/op-model/scripts/op_model_lookup/domain/catalog.py` `parse_records`, `matches` · `.opencode/skills/op-model/scripts/op_model_lookup/domain/test_catalog.py` malformed-line recovery · `.opencode/skills/op-model/scripts/op_model_lookup/e2e/test_models_cli.py` no-match/error outcomes

## Constraints

- Live `opencode models` output is the only model-name authority — because a remembered or guessed identifier silently configures an unavailable model.
- No runtime-validation dependency is added for model records — because the skill is a small resolver and a dependency upgrade path is disproportionate risk.
- No model is selected automatically when providers are ambiguous — because the provider determines billing and availability and is a maintainer decision.

<!-- core:end -->

<!-- project:begin -->
## Local evidence

- **AC1 (pre-V2 snapshot):** Grouped rendering then showed both labeled costs per 1M tokens and its end-to-end cases covered that presentation; `crucible-suite-3` `uv run --frozen --group dev pytest -q` → exit 0 (607 passed). This predates the V2 migration: the current V2 candidate is the 599-passed run in Revision tracking, where the selector and cost-when-provided clauses are proven by `infrastructure/test_cli.py`. Final-candidate acceptance and the matching history reference remain pending.
- **AC6 (pre-V2 snapshot):** The malformed-record repairs (`numeric-fix-1`/`interpreter-fix-1`, including the `OverflowError` `0.0` fallback) passed Python/test architecture `[PASS]`; `crucible-suite-3` `uv run --frozen --group dev pytest -q` → exit 0 (607 passed). Under V2 the parser skips non-selector lines and reports no-match/no-models; the current candidate is the 599-passed run in Revision tracking. Final-candidate acceptance remains pending.
- **AC5:** Prior source Proof recorded Vault 🔐 (Catalog Steward) `[PASS]` on 2026-10-09 for the missing-config confirmation preview. This retained source observation is not a fresh execution.

## Revision tracking

- 2026-10-15 — Shared-region preparation and portable proving-reference cleanup await final-candidate acceptance and a delivery-matching history reference. Existing criteria and identities are retained; no new model or config change is claimed.
- 2026-10-15 — The helper code and regression package were changed under the approved programming scope; model selection and runtime configuration were not changed. Current fallback/fixture findings were repaired through `numeric-fix-1`/`interpreter-fix-1` with fresh owner gates and `crucible-suite-3` exit 0 (607 passed), establishing AC1/AC6. Matching history remains required for finalization; final-candidate acceptance stays pending.
- 2026-10-16 — Approved V2-compatibility revision (v1.2.0): the skill resolves from live `opencode models` output and presents each candidate as a `provider/model` selector, with in/out cost only when the live source provides it (OpenCode V2 `opencode models` emits plain selectors with no cost). AC2–AC6 and Constraints are unchanged. The Proof pointers for the V2 parser refresh and the matching delivery reference remain pending final-candidate acceptance; no Change log entry until then.
- 2026-10-16 — Current frozen V2 candidate evidence: `uv run --frozen --group dev pytest -q` → 599 passed, exit 0; `infrastructure/test_cli.py` proves the AC1 cost-when-provided clause. The earlier 607-passed entries above are the pre-V2 snapshot; final-candidate acceptance and the matching delivery reference remain pending.

## Change log

- before 2026-09-14 — earlier history: see git history for this file
- 2026-09-14 — skill-debt-resolution-20260914 (PR #36): created the feature definition; added the `ModelRecord` typed record contract (`op-model` 1.0.1).
- 2026-10-09 — aicore-all-files-pr-20261008 (PR #52): made confirmation of the exact preview an explicit prerequisite for creating a missing config, alongside the existing surgical model edit.
- 2026-10-12 — story revision (PR #59): separated behavioural criteria from proof and dropped the typed-record parser contract from the feature definition.
- 2026-10-15 — story-distribution-20261015 (PR #64): repaired AC1/AC6 (grouped in/out costs; safe malformed-record recovery with `0.0` fallback) and regionized the story.
<!-- project:end -->
