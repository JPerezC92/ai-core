import { describe, expect, it } from "vitest";
import { AssembleReviewSnapshot } from "../../scripts/pr_review/application/assemble_review_snapshot.ts";
import { ReviewPreparationError } from "../../scripts/pr_review/domain/records.ts";
import {
  createInvalidInventory,
  createNonStringPathList,
  createPaths,
  createSnapshot,
  createSnapshotWithoutCommits,
} from "../support/review-fixtures.ts";

describe("AssembleReviewSnapshot.execute", () => {
  it("preserves the deleted path of a complete snapshot", () => {
    const collected = createSnapshot();

    const result = new AssembleReviewSnapshot().execute(collected, createPaths());

    expect(result).toEqual(collected);
  });

  it("rejects a file inventory that is not the exact diff inventory", () => {
    for (const defect of ["missing", "extra", "duplicate"] as const) {
      const result = new AssembleReviewSnapshot().execute(
        createInvalidInventory(defect),
        createPaths(),
      );

      expect(result).toBeInstanceOf(ReviewPreparationError);
      expect(result).toMatchObject({ code: "SNAPSHOT_PATHS_MISMATCH" });
    }
  });

  it("rejects a snapshot without commit messages", () => {
    const result = new AssembleReviewSnapshot().execute(
      createSnapshotWithoutCommits(),
      createPaths(),
    );

    expect(result).toBeInstanceOf(ReviewPreparationError);
    expect(result).toMatchObject({ code: "SNAPSHOT_INVALID" });
  });

  it("rejects a path inventory that is not a string list", () => {
    const result = new AssembleReviewSnapshot().execute(
      createSnapshot(),
      createNonStringPathList(),
    );

    expect(result).toBeInstanceOf(ReviewPreparationError);
    expect(result).toMatchObject({
      code: "SNAPSHOT_PATHS_MISMATCH",
      message: "path inventory must be a string list",
    });
  });
});
