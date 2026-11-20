import { describe, expect, it } from "vitest";

import { makeCreationPublication, refusePublication } from "#tests/support/publication-fixtures.ts";

describe("authored content rules", () => {
	it("refuses a title that is not a conventional one", () => {
		expect(
			refusePublication({ ...makeCreationPublication(), title: "Adds the review preparation commands." }),
		).toBe("INPUT_INVALID");
	});

	it("refuses more than three summary bullets", () => {
		const base = makeCreationPublication();
		expect(refusePublication({ ...base, summary: ["one", "two", "three", "four"] })).toBe("INPUT_INVALID");
	});

	it("refuses a duplicated test-plan item", () => {
		const base = makeCreationPublication();
		expect(
			refusePublication({
				...base,
				testPlan: [
					{ text: "same", status: "PENDING" },
					{ text: "same", status: "PENDING" },
				],
			}),
		).toBe("INPUT_INVALID");
	});

	it("refuses fewer than two test-plan items", () => {
		const base = makeCreationPublication();
		expect(refusePublication({ ...base, testPlan: [{ text: "only", status: "PENDING" }] })).toBe("INPUT_INVALID");
	});
});
