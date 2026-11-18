/** The local inventory contract the snapshot preparation operation applies. */

import { describe, expect, it } from "vitest";
import { PrepareLocalSnapshot } from "#scripts/pr_review/application/prepare_local_snapshot.ts";
import { ReviewPreparationError } from "#scripts/pr_review/domain/records.ts";
import {
	createAlternateLocalInventory,
	createAlternateLocalPaths,
	createBody,
	createLocalDraft,
	createLocalInventoryWithForeignCommitSurface,
	createPaths,
} from "#tests/support/review-fixtures.ts";

describe("PrepareLocalSnapshot.execute over the local inventory input", () => {
	it("accepts the exact immutable inventory field set", () => {
		const inventory = createAlternateLocalInventory();

		const result = new PrepareLocalSnapshot().execute(
			createLocalDraft(),
			createBody(),
			inventory,
			createAlternateLocalPaths(),
		);

		expect(result).not.toBeInstanceOf(ReviewPreparationError);
		expect(result).toMatchObject({
			schema: inventory.schema,
			pr_number: inventory.pr_number,
			head_sha: inventory.head_sha,
			base: inventory.base,
			changed_files: inventory.changed_files,
		});
	});

	it("rejects a commit artifact that is not a commit message", () => {
		const result = new PrepareLocalSnapshot().execute(
			createLocalDraft(),
			createBody(),
			createLocalInventoryWithForeignCommitSurface(),
			createPaths(),
		);

		expect(result).toBeInstanceOf(ReviewPreparationError);
		expect(result).toMatchObject({
			code: "SNAPSHOT_INVALID",
			message: "local immutable inventory required",
		});
	});
});
