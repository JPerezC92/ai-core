import { describe, expect, it } from "vitest";

import { FindModels } from "#scripts/op_model_lookup/application/find_models.ts";
import type {
	LookupOutcome,
	Model,
	ModelSource,
	NoMatchingModels,
	NoModelsAvailable,
} from "#scripts/op_model_lookup/domain/catalog.ts";
import { create } from "#tests/support/model.factory.ts";

/** Narrow a lookup outcome to its business-failure branch. */
function asOutcome(value: LookupOutcome): NoModelsAvailable | NoMatchingModels {
	if (Array.isArray(value)) throw new Error("expected a business outcome, received a selection");
	return value as NoModelsAvailable | NoMatchingModels;
}

function source(models: readonly Model[], failure?: Error): ModelSource {
	return {
		fetch: () => {
			if (failure !== undefined) throw failure;
			return models;
		},
	};
}

/** Look up `query` against a source holding `models`. */
function lookup(query: string, models: readonly Model[], failure?: Error): LookupOutcome {
	return new FindModels(source(models, failure)).execute(query);
}

/** The configs a selection carries, or an empty list for a business outcome. */
function configs(outcome: LookupOutcome): readonly string[] {
	return Array.isArray(outcome) ? outcome.map((model) => model.config) : [];
}

describe("query matching", () => {
	it("returns every model in encounter order for an empty query", () => {
		const models = [create(), create({ config: "openai/gpt", id: "gpt", provider: "openai", name: "gpt" })];
		expect(lookup("", models)).toEqual(models);
	});

	it("selects the models a query fragment matches, in encounter order", () => {
		const models = [
			create({ config: "openai/gpt", id: "gpt", provider: "openai", name: "gpt" }),
			create(),
			create({ config: "openai/o3", id: "o3", provider: "openai", name: "o3" }),
		];
		expect(configs(lookup("openai", models))).toEqual(["openai/gpt", "openai/o3"]);
	});

	it("matches the human name even when the config does not carry the query", () => {
		const model = create({ config: "x/y", id: "y", provider: "x", name: "DeepSeek V4" });
		expect(configs(lookup("v4", [model]))).toEqual(["x/y"]);
	});

	it("normalizes case and separators on both sides of the comparison", () => {
		const model = create({ config: "deepseek/deepseek-v4-flash", id: "deepseek-v4-flash" });
		expect(configs(lookup("DeepSeek V4-Flash", [model]))).toEqual(["deepseek/deepseek-v4-flash"]);
	});

	it("treats a punctuation-only query as matching every model", () => {
		const models = [create(), create({ config: "openai/gpt", id: "gpt", provider: "openai", name: "gpt" })];
		expect(lookup("...", models)).toEqual(models);
	});
});

describe("business outcomes", () => {
	it("reports the empty catalog as the no-models outcome", () => {
		const outcome = asOutcome(lookup("", []));
		expect([outcome.kind, outcome.code]).toEqual(["no-models", "no_models_available"]);
	});

	it("reports an unmatched query as the no-match outcome naming the query", () => {
		const outcome = asOutcome(lookup("claude", [create()]));
		expect([outcome.kind, outcome.code]).toEqual(["no-match", "no_matching_models"]);
		expect(outcome.kind === "no-match" ? outcome.query : "").toBe("claude");
	});
});

describe("boundary propagation", () => {
	it("propagates a source failure instead of converting it to a business outcome", () => {
		expect(() => lookup("", [], new Error("boom"))).toThrow("boom");
	});
});
