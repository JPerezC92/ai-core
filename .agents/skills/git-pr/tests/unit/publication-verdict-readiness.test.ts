import { describe, expect, it } from "vitest";

import {
	makeAdvisoryFinding,
	makeDecision,
	makeReviewPublication,
	refusePublication,
} from "#tests/support/publication-fixtures.ts";

describe("verdict readiness", () => {
	it("refuses a passing verdict with an unresolved finding", () => {
		const base = makeReviewPublication();
		expect(refusePublication({ ...base, review: { ...base.review!, findings: [makeAdvisoryFinding()] } })).toBe(
			"INPUT_INVALID",
		);
	});

	it("refuses a passing verdict with an unresolved test item", () => {
		const base = makeReviewPublication();
		expect(
			refusePublication({
				...base,
				testPlan: [{ text: "first", status: "PENDING" }, base.testPlan[1]!],
			}),
		).toBe("INPUT_INVALID");
	});

	it("refuses an advisory verdict without the user's acceptance", () => {
		const base = makeReviewPublication();
		expect(
			refusePublication({
				...base,
				review: {
					...base.review!,
					findings: [makeAdvisoryFinding()],
					verdict: { kind: "ADVISORY", basis: "user 2026-11-20" },
				},
			}),
		).toBe("INPUT_INVALID");
	});

	it("refuses an advisory verdict whose basis does not name the accepting actor", () => {
		const base = makeReviewPublication();
		expect(
			refusePublication({
				...base,
				review: {
					...base.review!,
					findings: [makeAdvisoryFinding({ acceptance: makeDecision({ actor: "reviewer" }) })],
					verdict: { kind: "ADVISORY", basis: "the reviewer accepted the remaining advisory finding" },
				},
			}),
		).toBe("INPUT_INVALID");
	});

	it("refuses a blocked review", () => {
		const base = makeReviewPublication();
		expect(
			refusePublication({
				...base,
				review: { ...base.review!, verdict: { kind: "BLOCK", basis: "an open blocking finding" } },
			}),
		).toBe("INPUT_INVALID");
	});
});
