import { describe, expect, it } from "vitest";
import { PolicyValidationError, SnapshotValidationError } from "#scripts/attribution_scan/domain/records.ts";
import {
	makeCompleteSnapshot,
	makeMalformedPolicy,
	makeMalformedSnapshot,
	makeSyntheticPolicy,
	scanAttribution,
	scanDecision,
} from "#tests/support/attribution-fixtures.ts";

describe("ScanAttribution.execute", () => {
	it("returns a typed snapshot error with the original message", () => {
		const result = scanDecision(makeMalformedSnapshot(), makeSyntheticPolicy());

		expect(result).toBeInstanceOf(SnapshotValidationError);
		expect(result).toMatchObject({
			code: "SNAPSHOT_INVALID",
			message: "snapshot pr_number must be a positive integer",
		});
	});

	it("returns a typed policy error with the original message", () => {
		const result = scanDecision(makeCompleteSnapshot(), makeMalformedPolicy(makeSyntheticPolicy()));

		expect(result).toBeInstanceOf(PolicyValidationError);
		expect(result).toMatchObject({
			code: "POLICY_INVALID",
			message: "policy markers must be a non-empty string list",
		});
	});

	it("validates the snapshot before the policy", () => {
		const result = scanDecision(makeMalformedSnapshot(), makeMalformedPolicy(makeSyntheticPolicy()));

		expect(result).toBeInstanceOf(SnapshotValidationError);
		expect(result).toMatchObject({ message: "snapshot pr_number must be a positive integer" });
	});

	it("returns the scan metadata without matches for complete clean inputs", () => {
		const result = scanAttribution(makeCompleteSnapshot(), makeSyntheticPolicy());

		expect(result).toEqual({
			pr_number: 80,
			head_sha: "a".repeat(40),
			base: "origin/main",
			matches: [],
			exclusions: [],
		});
	});
});
