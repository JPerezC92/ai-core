/** Apply the snapshot assembly rules to typed local preparation records. */

import type { Snapshot } from "#scripts/attribution_scan/domain/records.ts";
import { validateSnapshot } from "#scripts/attribution_scan/domain/validation.ts";
import { ReviewPreparationError } from "#scripts/pr_review/domain/records.ts";
import type { LocalInventory } from "#scripts/pr_review/domain/records.ts";

/** Report whether two path sets carry the same paths. */
function samePathSet(left: ReadonlySet<string>, right: ReadonlySet<string>): boolean {
	if (left.size !== right.size) return false;
	for (const path of left) if (!right.has(path)) return false;
	return true;
}

/**
 * Require the typed local inventory to satisfy the scanner's completeness contract.
 *
 * The rule applies to the typed inventory, so every caller that supplies one is held to it. The
 * outside document's field set and element shapes are the mapping adapter's concern.
 */
export function requireValidLocalInventory(inventory: LocalInventory): ReviewPreparationError | undefined {
	const validated = validateSnapshot({
		schema: inventory.schema,
		pr_number: inventory.pr_number,
		head_sha: inventory.head_sha,
		base: inventory.base,
		artifacts: [
			{ surface: "pr-title", source: "local title validation boundary", content: "" },
			{ surface: "pr-body", source: "local body validation boundary", content: "" },
			...inventory.commit_messages,
		],
		changed_files: inventory.changed_files,
	});
	if (validated !== undefined) {
		return new ReviewPreparationError("SNAPSHOT_INVALID", validated.message);
	}
	return undefined;
}

/**
 * Require a complete scanner snapshot.
 *
 * The rule proves that the assembled artifacts satisfy the scanner's own completeness contract.
 */
export function requireCompleteSnapshot(candidate: Snapshot): ReviewPreparationError | undefined {
	const validated = validateSnapshot(candidate);
	if (validated !== undefined) {
		return new ReviewPreparationError("SNAPSHOT_INVALID", validated.message);
	}
	return undefined;
}

/**
 * Require the snapshot's changed paths to equal the exact diff inventory.
 *
 * Both path lists must be free of duplicates, so one repeated path cannot stand in for another.
 */
export function requireExactPaths(
	snapshotPaths: readonly string[],
	exactPaths: readonly string[],
): ReviewPreparationError | undefined {
	const snapshotSet = new Set(snapshotPaths);
	const exactSet = new Set(exactPaths);
	if (
		snapshotSet.size !== snapshotPaths.length ||
		exactSet.size !== exactPaths.length ||
		!samePathSet(snapshotSet, exactSet)
	) {
		return new ReviewPreparationError(
			"SNAPSHOT_PATHS_MISMATCH",
			"snapshot paths must equal the exact diff inventory",
		);
	}
	return undefined;
}
