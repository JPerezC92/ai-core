import { describe, expect, it } from "vitest";
import { PrepareLocalSnapshot } from "#scripts/pr_review/application/prepare_local_snapshot.ts";
import { ReviewPreparationError } from "#scripts/pr_review/domain/records.ts";
import {
	createBody,
	createLocalInventory,
	createLocalSnapshot,
	createLocalTitle,
	createPaths,
} from "#tests/support/review-fixtures.ts";

describe("PrepareLocalSnapshot.execute", () => {
	it("assembles the generated title and body over the supplied immutable content", () => {
		const result = new PrepareLocalSnapshot().execute(
			createLocalTitle(),
			createBody(),
			createLocalInventory(),
			createPaths(),
		);

		expect(result).toEqual(createLocalSnapshot());
	});

	it("rejects a path inventory that is not the exact diff inventory", () => {
		const result = new PrepareLocalSnapshot().execute(createLocalTitle(), createBody(), createLocalInventory(), [
			"src/unlisted-path",
		]);

		expect(result).toBeInstanceOf(ReviewPreparationError);
		expect(result).toMatchObject({
			code: "SNAPSHOT_PATHS_MISMATCH",
			message: "snapshot paths must equal the exact diff inventory",
		});
	});
});
