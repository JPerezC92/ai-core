import { describe, expect, it } from "vitest";
import { ValidateFeatures } from "#scripts/feature_validation/application/validate_features.ts";
import { InvalidFeatureError, ValidFeature } from "#scripts/feature_validation/domain/records.ts";
import type { FeatureValidationResult } from "#scripts/feature_validation/domain/records.ts";
import type { PathComparisonPolicy } from "#scripts/feature_validation/domain/rules.ts";
import { FeatureSourceFake } from "#tests/support/feature-fixtures.ts";

const REFERENCE = "features/a.md";
const caseSensitivePolicy: PathComparisonPolicy = { caseSensitive: true };

/** A minimal active record whose second Log entry carries the supplied identifier. */
function recordWithIdentifier(identifier: string): string {
	return [
		"# Sample feature",
		"",
		"> **Status:** active",
		"> **Owner:** Cipher (Lead Orchestrator)",
		"> **Created:** 2026-10-01",
		"",
		"## Specs",
		"",
		"- S1 — A requirement.",
		"",
		"## Tasks",
		"",
		"- T1 | S1 | route | open | commit: pending",
		"",
		"## Log",
		"",
		"- L1 — original request",
		`- L${identifier} — a later entry`,
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

describe("ValidateFeatures.execute Log identifier encoding", () => {
	it("rejects a non-ASCII decimal identifier with a named finding", () => {
		expect(findingsFor(recordWithIdentifier("٢"))).toStrictEqual([
			"Log entry identifier must use ASCII digits: - L٢ — a later entry",
		]);
	});

	it("keeps accepting an ASCII identifier", () => {
		expect(findingsFor(recordWithIdentifier("2"))).toStrictEqual([]);
	});

	it("still reports a non-ascending ASCII sequence", () => {
		const document = recordWithIdentifier("0");
		expect(findingsFor(document)).toStrictEqual(["Log entry identifiers must ascend strictly: L0 follows L1"]);
	});
});
