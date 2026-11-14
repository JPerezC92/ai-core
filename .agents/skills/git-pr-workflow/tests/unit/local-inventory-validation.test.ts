import { describe, expect, it } from "vitest";
import { ReviewPreparationError } from "#scripts/pr_review/domain/records.ts";
import { validateLocalInventory } from "#scripts/pr_review/domain/snapshot_assembly.ts";
import {
  createLocalInventory,
  createLocalInventoryWithForeignCommitSurface,
} from "#tests/support/review-fixtures.ts";

describe("validateLocalInventory", () => {
  it("accepts the exact immutable inventory field set", () => {
    const validated = validateLocalInventory(createLocalInventory());

    expect(validated).toEqual(createLocalInventory());
  });

  it("rejects a commit artifact that is not a commit message", () => {
    const validated = validateLocalInventory(createLocalInventoryWithForeignCommitSurface());

    expect(validated).toBeInstanceOf(ReviewPreparationError);
    expect(validated).toMatchObject({
      code: "SNAPSHOT_INVALID",
      message: "local immutable inventory required",
    });
  });
});
