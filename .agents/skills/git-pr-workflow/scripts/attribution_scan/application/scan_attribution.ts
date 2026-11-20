/** Execute the attribution scan over typed snapshot and policy inputs. */

import { scanValidatedSnapshot } from "#scripts/attribution_scan/domain/matching.ts";
import { PolicyValidationError, SnapshotValidationError } from "#scripts/attribution_scan/domain/records.ts";
import type { ScanInput, ScanResult } from "#scripts/attribution_scan/domain/records.ts";
import { validatePolicy, validateSnapshot } from "#scripts/attribution_scan/domain/validation.ts";

export class ScanAttribution {
	/** Validate the snapshot before the policy, then scan the validated snapshot. */
	execute(input: ScanInput): ScanResult | PolicyValidationError | SnapshotValidationError {
		const snapshotFailure = validateSnapshot(input.snapshot);
		if (snapshotFailure !== undefined) return snapshotFailure;
		const policyFailure = validatePolicy(input.policy);
		if (policyFailure !== undefined) return policyFailure;
		return scanValidatedSnapshot(input.snapshot, input.policy);
	}
}
