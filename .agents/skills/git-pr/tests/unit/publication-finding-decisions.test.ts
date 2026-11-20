import { describe, expect, it } from "vitest";

import {
	makeAdvisoryFinding,
	makeDecision,
	makeReviewPublication,
	refusePublication,
} from "#tests/support/publication-fixtures.ts";

describe("finding identities and decisions", () => {
	it("refuses findings whose identifiers are not sequential", () => {
		const base = makeReviewPublication();
		const finding = makeAdvisoryFinding({ id: "F2" });
		expect(
			refusePublication({
				...base,
				review: { ...base.review!, findings: [finding] },
			}),
		).toBe("INPUT_INVALID");
	});

	it("refuses a deferred finding without a deferral decision", () => {
		const base = makeReviewPublication();
		expect(
			refusePublication({
				...base,
				review: { ...base.review!, findings: [makeAdvisoryFinding({ status: "DEFERRED" })] },
			}),
		).toBe("INPUT_INVALID");
	});

	it("refuses a deferral without a destination", () => {
		const base = makeReviewPublication();
		const deferral = makeDecision({ statement: "deferred", evidence: "instruction" });
		expect(
			refusePublication({
				...base,
				review: { ...base.review!, findings: [makeAdvisoryFinding({ status: "DEFERRED", deferral })] },
			}),
		).toBe("INPUT_INVALID");
	});

	it("refuses an acceptance on a blocking finding", () => {
		const base = makeReviewPublication();
		expect(
			refusePublication({
				...base,
				review: {
					...base.review!,
					findings: [makeAdvisoryFinding({ severity: "BLOCK", acceptance: makeDecision() })],
				},
			}),
		).toBe("INPUT_INVALID");
	});

	it("accepts a deferred finding whose deferral names its destination", () => {
		const base = makeReviewPublication();
		const deferral = makeDecision({ actor: "user", destination: "debt.md DEBT-070" });
		expect(
			refusePublication({
				...base,
				review: {
					...base.review!,
					findings: [makeAdvisoryFinding({ status: "DEFERRED", deferral, acceptance: deferral })],
					verdict: { kind: "ADVISORY", basis: "user 2026-11-20" },
				},
			}),
		).toBe("");
	});
});
