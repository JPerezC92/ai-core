/** Shared model fixtures for the op-model test suites. */

import type { Model } from "#scripts/op_model_lookup/domain/catalog.ts";

/**
 * Build one model.
 *
 * Costs default to zero because the parser always produces zero-cost records
 * from selector output; a case that needs a different record states only the
 * fields that vary.
 */
export function create(overrides: Partial<Model> = {}): Model {
	return {
		config: "deepseek/deepseek-v4",
		id: "deepseek-v4",
		provider: "deepseek",
		name: "deepseek-v4",
		costIn: 0,
		costOut: 0,
		...overrides,
	};
}

/** Render one model as `opencode models` prints it. */
export function selectorOf(model: Model): string {
	return `${model.provider}/${model.id}`;
}

/** Render models as the command's standard output, one selector per line. */
export function listingOf(models: readonly Model[]): string {
	return models.map((model) => `${selectorOf(model)}\n`).join("");
}
