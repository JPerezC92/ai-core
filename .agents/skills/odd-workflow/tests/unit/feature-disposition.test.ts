import { describe, expect, it } from "vitest";
import { ValidateFeatures } from "#scripts/feature_validation/application/validate_features.ts";
import { InvalidFeatureError, ValidFeature } from "#scripts/feature_validation/domain/records.ts";
import type { FeatureValidationResult } from "#scripts/feature_validation/domain/records.ts";
import type { PathComparisonPolicy } from "#scripts/feature_validation/domain/rules.ts";
import { FeatureSourceFake } from "#tests/support/feature-fixtures.ts";

const REFERENCE = "features/a.md";
const caseSensitivePolicy: PathComparisonPolicy = { caseSensitive: true };

interface ClosedRecordOptions {
	readonly closed: string;
	readonly disposition?: string;
	readonly supersededBy?: string;
	readonly taskStatus?: "done" | "in progress";
	readonly authorization?: string;
}

/** A minimal closed record, parameterised only by the closure-disposition inputs under test. */
function closedRecord(options: ClosedRecordOptions): string {
	const header = ["> **Status:** closed", `> **Closed:** ${options.closed}`];
	if (options.disposition !== undefined) header.push(`> **Disposition:** ${options.disposition}`);
	if (options.supersededBy !== undefined) header.push(`> **Superseded-by:** ${options.supersededBy}`);
	header.push("> **Owner:** Cipher (Lead Orchestrator)", "> **Created:** 2026-10-01");
	const task =
		options.taskStatus === "done"
			? "- T1 | S1 | route | done | commit: 0123456"
			: "- T1 | S1 | route | in progress | commit: pending";
	const authorization = options.authorization ?? "No authorization recorded.";
	return [
		"# Sample feature",
		"",
		...header,
		"",
		"## Specs",
		"",
		"- S1 — A requirement.",
		"",
		"## Tasks",
		"",
		task,
		"",
		"## Log",
		"",
		"- L1 — original request",
		`- L2 — Close: ${options.closed} — ${authorization}`,
		"",
	].join("\n");
}

/** Runs the feature validation over one document and returns the findings it reports. */
function findingsFor(text: string): readonly string[] {
	const source = new FeatureSourceFake([REFERENCE], new Map([[REFERENCE, text]]));
	const [result]: FeatureValidationResult[] = [
		...new ValidateFeatures(source, caseSensitivePolicy).execute("features"),
	];
	if (result instanceof InvalidFeatureError) return result.findings;
	if (result instanceof ValidFeature) return [];
	throw new Error(`unexpected feature validation result: ${result?.constructor.name ?? "no result"}`);
}

describe("ValidateFeatures.execute closure disposition", () => {
	it("accepts a completed closure on the effective date", () => {
		expect(
			findingsFor(closedRecord({ closed: "2026-11-24", disposition: "completed", taskStatus: "done" })),
		).toStrictEqual([]);
	});

	it("requires a disposition on a record closed on the effective date", () => {
		expect(findingsFor(closedRecord({ closed: "2026-11-24", taskStatus: "done" }))).toStrictEqual([
			"closed feature needs exactly one Disposition line: completed, cancelled or superseded",
		]);
	});

	it("rejects a disposition value outside the three permitted ones", () => {
		expect(
			findingsFor(closedRecord({ closed: "2026-11-24", disposition: "done", taskStatus: "done" })),
		).toStrictEqual(["Disposition must be completed, cancelled or superseded"]);
	});

	it("accepts a cancelled closure whose tasks are only partially complete, when the user authorized it", () => {
		expect(
			findingsFor(
				closedRecord({
					closed: "2026-11-24",
					disposition: "cancelled",
					authorization: "The user authorized the cancellation of this work.",
				}),
			),
		).toStrictEqual([]);
	});

	it("requires recorded user authorization for a cancellation", () => {
		expect(findingsFor(closedRecord({ closed: "2026-11-24", disposition: "cancelled" }))).toStrictEqual([
			"cancelled feature needs a Log entry recording explicit user authorization for the cancellation",
		]);
	});

	it("requires a replacement delivery or an obsolescence explanation for a superseded closure", () => {
		expect(
			findingsFor(closedRecord({ closed: "2026-11-24", disposition: "superseded", taskStatus: "done" })),
		).toStrictEqual([
			"superseded feature needs a Superseded-by delivery reference or a Close entry explaining why its requirements are obsolete",
		]);
	});

	it("accepts a superseded closure that explains obsolescence instead of naming a replacement", () => {
		expect(
			findingsFor(
				closedRecord({
					closed: "2026-11-24",
					disposition: "superseded",
					authorization: "The requirement is obsolete: the surface it governed no longer exists.",
				}),
			),
		).toStrictEqual([]);
	});

	it("accepts a superseded closure that names its replacement and leaves a requirement incomplete", () => {
		expect(
			findingsFor(
				closedRecord({
					closed: "2026-11-24",
					disposition: "superseded",
					supersededBy: "2026-11-24 replacement delivery `af9dc60`",
				}),
			),
		).toStrictEqual([]);
	});

	it("does not require a disposition from a record closed before the effective date", () => {
		expect(findingsFor(closedRecord({ closed: "2026-11-23", taskStatus: "done" }))).toStrictEqual([]);
	});
});
