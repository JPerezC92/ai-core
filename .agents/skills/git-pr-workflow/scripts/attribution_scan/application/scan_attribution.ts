/** Execute the attribution scan over decoded snapshot and policy inputs. */

import { scanValidatedSnapshot } from "../domain/matching.ts";
import { PolicyValidationError, SnapshotValidationError } from "../domain/records.ts";
import type { ScanInput, ScanResult } from "../domain/records.ts";
import { validatePolicy, validateSnapshot } from "../domain/validation.ts";

export class ScanAttribution {
  /** Validate the snapshot before the policy, then scan the validated snapshot. */
  execute(input: ScanInput): ScanResult | PolicyValidationError | SnapshotValidationError {
    const snapshot = validateSnapshot(input.snapshotValue);
    if (snapshot instanceof SnapshotValidationError) return snapshot;
    const policy = validatePolicy(input.policyValue);
    if (policy instanceof PolicyValidationError) return policy;
    return scanValidatedSnapshot(snapshot, policy);
  }
}
