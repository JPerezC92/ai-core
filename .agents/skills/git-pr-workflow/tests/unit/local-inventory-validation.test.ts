/** The local inventory contract the preparation mapping applies. */

import { describe, expect, it } from "vitest";
import { ReviewPreparationError } from "#scripts/pr_review/domain/records.ts";
import { decodeLocalInventory } from "#scripts/pr_review/infrastructure/adapters/snapshot_assembly.ts";
import {
	createAlternateLocalInventory,
	createLocalInventory,
	createLocalInventoryWithForeignCommitSurface,
} from "#tests/support/review-fixtures.ts";

describe("validating the local immutable inventory", () => {
	it("accepts the exact immutable inventory field set", () => {
		const inventory = createAlternateLocalInventory();

		const result = decodeLocalInventory(inventory);

		expect(result).not.toBeInstanceOf(ReviewPreparationError);
		expect(result).toEqual(inventory);
	});

	it("rejects a commit artifact that is not a commit message", () => {
		const result = decodeLocalInventory(createLocalInventoryWithForeignCommitSurface());

		expect(result).toBeInstanceOf(ReviewPreparationError);
		expect(result).toMatchObject({
			code: "SNAPSHOT_INVALID",
			message: "local immutable inventory required",
		});
	});

	it("rejects an inventory that carries a field outside the documented set", () => {
		const result = decodeLocalInventory({ ...createLocalInventory(), extra: true });

		expect(result).toBeInstanceOf(ReviewPreparationError);
		expect(result).toMatchObject({
			code: "SNAPSHOT_INVALID",
			message: "local immutable inventory required",
		});
	});
});
