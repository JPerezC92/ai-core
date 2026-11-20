/** The policy input validation the scanner operation applies to decoded JSON. */

import { describe, expect, it } from "vitest";
import { PolicyValidationError } from "#scripts/attribution_scan/domain/records.ts";
import {
	loadApprovedPolicy,
	makeCompleteSnapshot,
	makeMalformedPolicy,
	scanDecision,
} from "#tests/support/attribution-fixtures.ts";

describe("policy input rejection", () => {
	it("rejects a malformed policy as a returned business error", () => {
		const policy = loadApprovedPolicy();

		const result = scanDecision(makeCompleteSnapshot(), makeMalformedPolicy(policy, "identities"));

		expect(result).toBeInstanceOf(PolicyValidationError);
		expect(result).toMatchObject({
			code: "POLICY_INVALID",
			message: "policy identities must be a non-empty string list",
		});
	});
});
