/** Assemble a scanner snapshot from a decoded snapshot and the exact diff paths. */

import type { Snapshot } from "#scripts/attribution_scan/domain/records.ts";
import { ReviewPreparationError } from "#scripts/pr_review/domain/records.ts";
import { requireCompleteSnapshot, requireExactPaths } from "#scripts/pr_review/domain/snapshot_assembly.ts";

export class AssembleReviewSnapshot {
	/** Apply the completeness and exact-path rules to typed preparation inputs. */
	execute(snapshot: Snapshot, exactPaths: readonly string[]): Snapshot | ReviewPreparationError {
		const incomplete = requireCompleteSnapshot(snapshot);
		if (incomplete !== undefined) return incomplete;
		const mismatch = requireExactPaths(
			snapshot.changed_files.map((entry) => entry.path),
			exactPaths,
		);
		if (mismatch !== undefined) return mismatch;
		return snapshot;
	}
}
