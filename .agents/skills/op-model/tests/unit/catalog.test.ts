import { describe, expect, it } from "vitest";

import { parseRecords } from "#scripts/op_model_lookup/domain/catalog.ts";
import { create, listingOf } from "#tests/support/model.factory.ts";

describe("catalog parsing", () => {
	it("parses selector lines into models with zero costs", () => {
		const expected = [
			create(),
			create({ config: "openai/gpt-5.1", id: "gpt-5.1", provider: "openai", name: "gpt-5.1" }),
		];

		const parsed = parseRecords(listingOf(expected));

		expect(parsed.models).toEqual(expected);
		expect(parsed.issues).toEqual([]);
	});

	it("skips blank lines without recording issues", () => {
		expect(parseRecords("\n  \n\n").issues).toEqual([]);
	});

	it("records a non-selector line as an issue and keeps parsing", () => {
		const parsed = parseRecords(`not a selector\n${listingOf([create()])}`);

		expect(parsed.models).toHaveLength(1);
		expect(parsed.issues).toEqual([
			{ code: "unrecognized_line", message: "not a selector: not a provider/model selector" },
		]);
	});

	it("trims surrounding whitespace before matching", () => {
		const model = create({ config: "openai/gpt-5.1", id: "gpt-5.1", provider: "openai", name: "gpt-5.1" });

		expect(parseRecords(`  ${listingOf([model])}`).models[0]?.config).toBe("openai/gpt-5.1");
	});

	it("rejects a selector whose provider starts with punctuation", () => {
		expect(parseRecords("-bad/model\n").models).toEqual([]);
	});
});
