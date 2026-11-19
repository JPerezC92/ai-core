import { describe, expect, it } from "vitest";
import { ValidateFeatures } from "#scripts/feature_validation/application/validate_features.ts";
import { InvalidFeatureError, ValidFeature } from "#scripts/feature_validation/domain/records.ts";
import type { FeatureValidationResult } from "#scripts/feature_validation/domain/records.ts";
import {
	CLOSURE_CONSISTENCY_EFFECTIVE_FROM,
	CLOSURE_EVIDENCE_EFFECTIVE_FROM,
} from "#scripts/feature_validation/domain/rules.ts";
import type { PathComparisonPolicy } from "#scripts/feature_validation/domain/rules.ts";
import {
	FeatureSourceFake,
	makeClosedFeatureWithUnfinishedTask,
	makeCompletedFeature,
	makeFeature,
} from "#tests/support/feature-fixtures.ts";
import { COMPLETED_BUT_ACTIVE_FINDING } from "#tests/support/retirement-fixtures.ts";

const EFFECTIVE_FROM = CLOSURE_CONSISTENCY_EFFECTIVE_FROM;
const REFERENCE = "features/a.md";
const caseSensitivePolicy: PathComparisonPolicy = { caseSensitive: true };

function dayBefore(isoDate: string): string {
	const time = Date.UTC(Number(isoDate.slice(0, 4)), Number(isoDate.slice(5, 7)) - 1, Number(isoDate.slice(8, 10)));
	return new Date(time - 86_400_000).toISOString().slice(0, 10);
}

/** Runs the feature validation over one document and returns the typed results it reports. */
function resultsFor(text: string): FeatureValidationResult[] {
	const source = new FeatureSourceFake([REFERENCE], new Map([[REFERENCE, text]]));
	return [...new ValidateFeatures(source, caseSensitivePolicy).execute("features")];
}

/** The findings the feature validation reports for one document. */
function findingsFor(text: string): readonly string[] {
	const [result] = resultsFor(text);
	if (result instanceof InvalidFeatureError) return result.findings;
	if (result instanceof ValidFeature) return [];
	throw new Error(`unexpected feature validation result: ${result?.constructor.name ?? "no result"}`);
}

describe("ValidateFeatures.execute closure consistency", () => {
	it("reports an active record created on the effective date whose every task row is done", () => {
		expect(resultsFor(makeCompletedFeature({ created: EFFECTIVE_FROM }))).toStrictEqual([
			new InvalidFeatureError(REFERENCE, [COMPLETED_BUT_ACTIVE_FINDING]),
		]);
	});

	it("reports an active record created after the effective date", () => {
		expect(resultsFor(makeCompletedFeature({ created: "2027-01-31" }))).toStrictEqual([
			new InvalidFeatureError(REFERENCE, [COMPLETED_BUT_ACTIVE_FINDING]),
		]);
	});

	it("leaves a historical record alone so its status and Log are never rewritten", () => {
		expect(resultsFor(makeCompletedFeature({ created: dayBefore(EFFECTIVE_FROM) }))).toStrictEqual([
			new ValidFeature(REFERENCE),
		]);
	});

	it("accepts the same record when a Log entry names the open closure prerequisite", () => {
		expect(resultsFor(makeCompletedFeature({ created: EFFECTIVE_FROM, blocked: true }))).toStrictEqual([
			new ValidFeature(REFERENCE),
		]);
	});

	it("reports the finding again when a later Log entry stops naming the prerequisite", () => {
		expect(
			resultsFor(makeCompletedFeature({ created: EFFECTIVE_FROM, blocked: true, laterEntry: true })),
		).toStrictEqual([new InvalidFeatureError(REFERENCE, [COMPLETED_BUT_ACTIVE_FINDING])]);
	});

	it("does not report a closed record whose every task row is done", () => {
		expect(resultsFor(makeCompletedFeature({ created: EFFECTIVE_FROM, status: "closed" }))).toStrictEqual([
			new ValidFeature(REFERENCE),
		]);
	});

	it("still sees Close: when the verbatim L1 contains ATX headings", () => {
		const findings = findingsFor(
			makeCompletedFeature({
				created: EFFECTIVE_FROM,
				status: "closed",
				verbatimLogHeadings: true,
			}),
		);

		expect(findings).toStrictEqual([]);
		expect(findings).not.toContain("closed feature needs a Log 'Close:' entry");
	});

	it("does not report an active record that still carries an unfinished task", () => {
		expect(resultsFor(makeFeature())).toStrictEqual([new ValidFeature(REFERENCE)]);
	});

	it("keeps reporting a closed record with an unfinished task", () => {
		const findings = findingsFor(makeClosedFeatureWithUnfinishedTask());

		expect(findings).toContain("closed feature has a open task: - T1 | S1 | route | open | commit: pending");
		expect(findings).not.toContain(COMPLETED_BUT_ACTIVE_FINDING);
	});
});

describe("ValidateFeatures.execute closure evidence", () => {
	it("requires a per-spec verdict entry in the Log", () => {
		const findings = findingsFor(
			makeCompletedFeature({ created: CLOSURE_EVIDENCE_EFFECTIVE_FROM, status: "closed", verdict: "absent" }),
		);

		expect(findings).toContain("closed feature needs a per-spec verdict for S1 in its Log");
	});

	it("requires every verdict entry to name the commit it ran against", () => {
		const findings = findingsFor(
			makeCompletedFeature({
				created: CLOSURE_EVIDENCE_EFFECTIVE_FROM,
				status: "closed",
				verdict: "without-commit",
			}),
		);

		expect(findings.some((finding) => finding.includes("name the commit it ran against"))).toBe(true);
	});

	it("requires the first failure or a stated reason it cannot apply", () => {
		const findings = findingsFor(
			makeCompletedFeature({
				created: CLOSURE_EVIDENCE_EFFECTIVE_FROM,
				status: "closed",
				firstFailure: "absent",
			}),
		);

		expect(findings).toContain(
			"closed feature needs the first failure recorded or the reason an executable failure cannot apply",
		);
	});

	it("accepts a stated reason when no executable failure applies", () => {
		expect(
			findingsFor(
				makeCompletedFeature({
					created: CLOSURE_EVIDENCE_EFFECTIVE_FROM,
					status: "closed",
					firstFailure: "not-applicable",
				}),
			),
		).toStrictEqual([]);
	});

	it("accepts a compliant closed record", () => {
		expect(
			resultsFor(makeCompletedFeature({ created: CLOSURE_EVIDENCE_EFFECTIVE_FROM, status: "closed" })),
		).toStrictEqual([new ValidFeature(REFERENCE)]);
	});

	it("never re-validates a record created before the closure-evidence date", () => {
		const findings = findingsFor(
			makeCompletedFeature({
				created: dayBefore(CLOSURE_EVIDENCE_EFFECTIVE_FROM),
				status: "closed",
				verdict: "absent",
				firstFailure: "absent",
			}),
		);

		expect(findings).toStrictEqual([]);
	});

	it("does not treat an open-closure-prerequisite entry as a verdict needing a commit", () => {
		expect(
			resultsFor(
				makeCompletedFeature({
					created: CLOSURE_EVIDENCE_EFFECTIVE_FROM,
					status: "active",
					blocked: true,
				}),
			),
		).toStrictEqual([new ValidFeature(REFERENCE)]);
	});

	it("does not let a prerequisite entry satisfy the per-spec verdict requirement", () => {
		const findings = findingsFor(
			makeCompletedFeature({
				created: CLOSURE_EVIDENCE_EFFECTIVE_FROM,
				status: "closed",
				blocked: true,
				verdict: "absent",
			}),
		);

		expect(findings).toContain("closed feature needs a per-spec verdict for S1 in its Log");
	});
});
