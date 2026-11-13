import { describe, expect, it } from "vitest";
import { PrepareLocalSnapshot } from "../../scripts/pr_review/application/prepare_local_snapshot.ts";
import { ReviewPreparationError } from "../../scripts/pr_review/domain/records.ts";
import {
  createBody,
  createLocalDraft,
  createLocalInventory,
  createLocalSnapshot,
  createPaths,
} from "../support/review-fixtures.ts";

describe("PrepareLocalSnapshot.execute", () => {
  it("assembles the local title and working body over the supplied immutable content", () => {
    const result = new PrepareLocalSnapshot().execute(
      createLocalDraft(),
      createBody(),
      createLocalInventory(),
      createPaths(),
    );

    expect(result).toEqual(createLocalSnapshot());
  });

  it("rejects a creation draft that carries no Title line", () => {
    const result = new PrepareLocalSnapshot().execute(
      "no title here\n",
      "## Summary\n",
      createLocalInventory(),
      createPaths(),
    );

    expect(result).toBeInstanceOf(ReviewPreparationError);
    expect(result).toMatchObject({
      code: "DRAFT_INVALID",
      message: "creation draft must begin with a Title: line",
    });
  });

  it("rejects an inventory that carries a field outside the documented set", () => {
    const inventory = { ...createLocalInventory(), extra: true };

    const result = new PrepareLocalSnapshot().execute(
      createLocalDraft(),
      "## Summary\n",
      inventory,
      createPaths(),
    );

    expect(result).toBeInstanceOf(ReviewPreparationError);
    expect(result).toMatchObject({
      code: "SNAPSHOT_INVALID",
      message: "local immutable inventory required",
    });
  });
});
