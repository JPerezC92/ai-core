/** Prepare scanner input from the generated title, the working body and the immutable inventory. */

import type { Snapshot } from "#scripts/attribution_scan/domain/records.ts";
import { ReviewPreparationError } from "#scripts/pr_review/domain/records.ts";
import type { LocalInventory } from "#scripts/pr_review/domain/records.ts";
import { requireCompleteSnapshot, requireExactPaths } from "#scripts/pr_review/domain/snapshot_assembly.ts";

export class PrepareLocalSnapshot {
	/** Assemble local artifacts without fetching remote prose or collecting Git state. */
	execute(
		title: string,
		body: string,
		inventory: LocalInventory,
		exactPaths: readonly string[],
	): Snapshot | ReviewPreparationError {
		const candidate: Snapshot = {
			schema: inventory.schema,
			pr_number: inventory.pr_number,
			head_sha: inventory.head_sha,
			base: inventory.base,
			artifacts: [
				{ surface: "pr-title", source: `PR #${inventory.pr_number} title`, content: title },
				{ surface: "pr-body", source: `PR #${inventory.pr_number} body`, content: body },
				...inventory.commit_messages,
			],
			changed_files: inventory.changed_files,
		};
		const invalid = requireCompleteSnapshot(candidate);
		if (invalid !== undefined) return invalid;
		const mismatch = requireExactPaths(
			candidate.changed_files.map((entry) => entry.path),
			exactPaths,
		);
		if (mismatch !== undefined) return mismatch;
		return candidate;
	}
}
