import { describe, expect, it } from "vitest";

import type { PublicationDebt } from "#scripts/pr_content/domain/records.ts";
import {
	makeAdvisoryFinding,
	makeDebt,
	makeReviewPublication,
	refusePublication,
} from "#tests/support/publication-fixtures.ts";

describe("independent debt", () => {
	it("refuses a debt target that repeats a finding identifier", () => {
		const base = makeReviewPublication();
		expect(
			refusePublication({
				...base,
				review: {
					...base.review!,
					findings: [makeAdvisoryFinding()],
					debt: [makeDebt({ target: "F1" })],
				},
			}),
		).toBe("INPUT_INVALID");
	});

	it("refuses a debt entry without a destination", () => {
		const base = makeReviewPublication();
		const { destination: _destination, ...withoutDestination } = makeDebt();
		expect(
			refusePublication({
				...base,
				review: {
					...base.review!,
					debt: [withoutDestination as PublicationDebt],
				},
			}),
		).toBe("INPUT_INVALID");
	});

	it("refuses duplicated debt targets", () => {
		const base = makeReviewPublication();
		const entry = makeDebt({ target: "follow-up" });
		expect(refusePublication({ ...base, review: { ...base.review!, debt: [entry, entry] } })).toBe("INPUT_INVALID");
	});
});
