/** Collect the local Git inventory and the exact paths the commit range changed. */

import type { Artifact, ChangedFile } from "#scripts/attribution_scan/domain/records.ts";
import type { GitInventoryPort } from "#scripts/pr_review/domain/ports.ts";
import { ReviewPreparationError } from "#scripts/pr_review/domain/records.ts";
import type { CollectedInventory, LocalInventory } from "#scripts/pr_review/domain/records.ts";
import { requireValidLocalInventory } from "#scripts/pr_review/domain/snapshot_assembly.ts";

/** The revision the local snapshot reads its head commit from. */
const HEAD_REVISION = "HEAD";

export class CollectLocalInventory {
	private readonly reader: GitInventoryPort;

	constructor(reader: GitInventoryPort) {
		this.reader = reader;
	}

	/** Collect the immutable local inventory without assembling scanner artifacts. */
	execute(prNumber: number, base: string): CollectedInventory | ReviewPreparationError {
		const head = this.reader.resolveCommit(HEAD_REVISION);
		if (head === null) {
			return new ReviewPreparationError("GIT_REVISION_UNRESOLVED", "HEAD must resolve to a commit");
		}
		const resolvedBase = this.reader.resolveCommit(base);
		if (resolvedBase === null) {
			return new ReviewPreparationError("GIT_REVISION_UNRESOLVED", `base ref must resolve to a commit: ${base}`);
		}
		const ancestor = this.reader.mergeBase(resolvedBase, head);
		if (ancestor === null) {
			return new ReviewPreparationError(
				"GIT_MERGE_BASE_UNRESOLVED",
				"base ref and HEAD share no common ancestor",
			);
		}
		const commits = this.reader.listCommits(ancestor, head);
		if (commits.length === 0) {
			return new ReviewPreparationError(
				"GIT_COMMIT_RANGE_EMPTY",
				"the commit range between base and HEAD is empty",
			);
		}
		const paths = this.reader.listChangedPaths(ancestor, head);
		if (paths.length === 0) {
			return new ReviewPreparationError("GIT_PATHS_EMPTY", "the commit range changes no path");
		}
		const deleted = new Set(this.reader.listDeletedPaths(ancestor, head));
		if (![...deleted].every((path) => paths.includes(path))) {
			return new ReviewPreparationError(
				"SNAPSHOT_PATHS_MISMATCH",
				"deleted paths must belong to the changed path inventory",
			);
		}
		const binary = new Set(this.reader.listBinaryPaths(ancestor, head));
		const changedFiles: ChangedFile[] = paths.map((path) => ({
			path,
			content: deleted.has(path) || binary.has(path) ? "" : this.reader.readFile(head, path),
		}));
		const commitMessages: Artifact[] = commits.map((commit) => ({
			surface: "commit-message",
			source: commit,
			content: this.reader.readMessage(commit),
		}));
		const inventory: LocalInventory = {
			schema: 1,
			pr_number: prNumber,
			head_sha: head,
			base,
			commit_messages: commitMessages,
			changed_files: changedFiles,
		};
		const failure = requireValidLocalInventory(inventory);
		if (failure !== undefined) return failure;
		return { inventory, paths: [...paths] };
	}
}
