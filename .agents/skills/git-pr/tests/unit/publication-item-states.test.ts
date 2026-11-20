import { describe, expect, it } from "vitest";

import {
	makeCreationPublication,
	makeDecision,
	makeEvidence,
	makeReviewPublication,
	refusePublication,
} from "#tests/support/publication-fixtures.ts";

describe("test item states", () => {
	it("refuses a passed item without evidence", () => {
		const base = makeReviewPublication();
		expect(refusePublication({ ...base, testPlan: [{ text: "first", status: "PASSED" }, base.testPlan[1]!] })).toBe(
			"INPUT_INVALID",
		);
	});

	it("refuses a pending item that carries evidence", () => {
		const base = makeReviewPublication();
		expect(
			refusePublication({
				...base,
				testPlan: [{ text: "first", status: "PENDING", evidence: makeEvidence() }, base.testPlan[1]!],
			}),
		).toBe("INPUT_INVALID");
	});

	it("refuses a not-applicable item without a decision", () => {
		const base = makeReviewPublication();
		expect(
			refusePublication({
				...base,
				testPlan: [{ text: "first", status: "NOT_APPLICABLE" }, base.testPlan[1]!],
			}),
		).toBe("INPUT_INVALID");
	});

	it("refuses a decision with an impossible calendar date", () => {
		const base = makeReviewPublication();
		expect(
			refusePublication({
				...base,
				testPlan: [
					{ text: "first", status: "NOT_APPLICABLE", decision: makeDecision({ date: "2026-02-31" }) },
					base.testPlan[1]!,
				],
			}),
		).toBe("INPUT_INVALID");
	});

	it("refuses a creation record that carries a completed item", () => {
		const base = makeCreationPublication();
		expect(
			refusePublication({
				...base,
				testPlan: [{ text: "first", status: "PASSED", evidence: makeEvidence() }, base.testPlan[1]!],
			}),
		).toBe("INPUT_INVALID");
	});
});
