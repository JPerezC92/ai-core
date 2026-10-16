<!-- core:begin -->
# User story — op-model-configuration

> **Created:** 2026-09-14
> **Title:** OpenCode model configuration
> **Status:** active
> **version:** 1.1.0
> **Epic:** developer-tooling
> **Affected areas:** `.opencode/skills/op-model/`, `opencode.json`, `opencode.jsonc`

## Persona

- A maintainer selecting an available subscribed model for an OpenCode agent without guessing provider or model identifiers.

## Goal

- **G:** The maintainer can choose a model from what is actually available and have only that agent reconfigured, without guessing identifiers or losing unrelated configuration.
  - Done when: available models are resolved from live output and presented with enough information to compare candidates, an ambiguous provider requires an explicit user choice, and the resulting configuration edit is limited to the selected agent and verified before it takes effect.

## Scenario

- The maintainer names a model family. The skill resolves it from live `opencode models --verbose` output, presents each candidate with its identifier, provider, and cost, asks when more than one provider matches, and updates only the selected agent's model field with a verified `provider/model` value.

## Acceptance criteria

- ✅ **AC1:** Each available model is presented with its identifier, provider, and in/out cost, so the maintainer can compare candidates before choosing.
- ✅ **AC2:** Model resolution uses live `opencode models` output as the only authority for what is available; no model identifier is supplied from memory or assumption.
- ✅ **AC3:** When more than one provider offers a matching model, the maintainer is asked to choose rather than having one selected for them.
- ✅ **AC4:** The configuration change is limited to the selected agent's model field, is parse-verified after writing, and is followed by a restart instruction.
- ✅ **AC5:** A missing configuration file is created only after the maintainer confirms the exact content preview.
- ✅ **AC6:** Unrecognized or malformed model output is skipped rather than producing a fabricated record, and a no-match is reported as a no-match.

## Proof

- AC1 → `.opencode/skills/op-model/scripts/op_model_lookup/infrastructure/cli.py` `render_selection` · `.opencode/skills/op-model/scripts/op_model_lookup/e2e/test_models_cli.py` grouped-cost presentation cases
- AC2 → `.opencode/skills/op-model/SKILL.md` `### Steps` items 2–3
- AC3 → `.opencode/skills/op-model/SKILL.md` `### Steps` item 3
- AC4 → `.opencode/skills/op-model/SKILL.md` `### Steps` items 4–9
- AC5 → `.opencode/skills/op-model/SKILL.md` `### Steps` item 6 · `### Troubleshooting` missing-config confirmation rule
- AC6 → `.opencode/skills/op-model/scripts/op_model_lookup/domain/catalog.py` `parse_records`, `matches` · `.opencode/skills/op-model/scripts/op_model_lookup/domain/test_catalog.py` malformed-block recovery · `.opencode/skills/op-model/scripts/op_model_lookup/e2e/test_models_cli.py` no-match/error outcomes

## Constraints

- Live `opencode models` output is the only model-name authority — because a remembered or guessed identifier silently configures an unavailable model.
- No runtime-validation dependency is added for model records — because the skill is a small resolver and a dependency upgrade path is disproportionate risk.
- No model is selected automatically when providers are ambiguous — because the provider determines billing and availability and is a maintainer decision.

<!-- core:end -->

<!-- project:begin -->
## Local evidence

- **AC1:** Grouped rendering shows both labeled costs per 1M tokens and its end-to-end cases cover the presentation. The repaired helper (`numeric-fix-1`/`interpreter-fix-1`) passed current Python/test architecture `[PASS]` and `crucible-suite-3` `uv run --frozen --group dev pytest -q` → exit 0 (607 passed). This establishes AC1 alongside AC6; final-candidate acceptance and the matching history reference remain pending for finalization.
- **AC6:** Fresh review found an uncaught `OverflowError` on a sufficiently large valid JSON cost integer; the promised `0.0` fallback was incomplete. `numeric-fix-1` added `OverflowError` to the narrow conversion handler and a parameterized regression over both cost fields (real `10**400` input), asserting `0.0` for the affected cost, preservation of the other cost, model retention, empty issues and a surviving neighbour. `bastion-corrections-review-1` Python architecture `[PASS]`; `crucible-corrections-review-1` test architecture `[PASS]`; `crucible-suite-3` `uv run --frozen --group dev pytest -q` → exit 0 (607 passed). Current evidence establishes AC6.
- **AC5:** Prior source Proof recorded Vault 🔐 (Catalog Steward) `[PASS]` on 2026-10-09 for the missing-config confirmation preview. This retained source observation is not a fresh execution.

## Revision tracking

- 2026-10-15 — Shared-region preparation and portable proving-reference cleanup await final-candidate acceptance and a delivery-matching history reference. Existing criteria and identities are retained; no new model or config change is claimed.
- 2026-10-15 — The helper code and regression package were changed under the approved programming scope; model selection and runtime configuration were not changed. Current fallback/fixture findings were repaired through `numeric-fix-1`/`interpreter-fix-1` with fresh owner gates and `crucible-suite-3` exit 0 (607 passed), establishing AC1/AC6. Matching history remains required for finalization; final-candidate acceptance stays pending.

## Change log

- before 2026-09-14 — earlier history: see git history for this file
- 2026-09-14 — skill-debt-resolution-20260914 (PR #36): created the feature definition; added the `ModelRecord` typed record contract (`op-model` 1.0.1).
- 2026-10-09 — aicore-all-files-pr-20261008 (PR #52): made confirmation of the exact preview an explicit prerequisite for creating a missing config, alongside the existing surgical model edit.
- 2026-10-12 — story revision (PR #59): separated behavioural criteria from proof and dropped the typed-record parser contract from the feature definition.
- 2026-10-15 — story-distribution-20261015 (commit 4174328): repaired AC1/AC6 (grouped in/out costs; safe malformed-record recovery with `0.0` fallback) and regionized the story.
<!-- project:end -->
