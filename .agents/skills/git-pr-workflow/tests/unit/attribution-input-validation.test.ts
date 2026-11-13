/** The snapshot and policy input validation the scanner loader applies to decoded JSON. */

import { describe, expect, it } from "vitest";
import {
  PolicyValidationError,
  SnapshotValidationError,
} from "../../scripts/attribution_scan/domain/records.ts";
import { validatePolicy, validateSnapshot } from "../../scripts/attribution_scan/domain/validation.ts";
import {
  invalidPaths,
  loadApprovedPolicy,
  makeInvalidPathSnapshot,
  makeMalformedContentSnapshot,
  makeMalformedPolicy,
  makeMalformedSnapshot,
  makeMalformedSurfaceSnapshot,
  makeNonListCollectionSnapshot,
  makeSnapshotWithoutChangedFiles,
  makeUnbalancedSurfaceSnapshot,
  makeWrongSchemaSnapshot,
} from "../support/attribution-fixtures.ts";

describe("snapshot validation", () => {
  it("requires at least one changed-file body", () => {
    const result = validateSnapshot(makeSnapshotWithoutChangedFiles());

    expect(result).toBeInstanceOf(SnapshotValidationError);
    expect(result).toMatchObject({
      code: "SNAPSHOT_INVALID",
      message: "snapshot requires at least one changed-file body",
    });
  });

  it("rejects empty, absolute and traversing changed-file paths", () => {
    for (const path of invalidPaths()) {
      const result = validateSnapshot(makeInvalidPathSnapshot(path));

      expect(result).toBeInstanceOf(SnapshotValidationError);
      expect(result).toMatchObject({
        code: "SNAPSHOT_INVALID",
        message:
          "changed-file path must be a non-empty root-relative path without parent traversal",
      });
    }
  });

  it("rejects a schema value that is not the documented whole number", () => {
    const result = validateSnapshot(makeWrongSchemaSnapshot());

    expect(result).toBeInstanceOf(SnapshotValidationError);
    expect(result).toMatchObject({
      code: "SNAPSHOT_INVALID",
      message: "snapshot schema must be 1",
    });
  });

  it("requires exactly one title, exactly one body, and at least one commit message", () => {
    const result = validateSnapshot(makeUnbalancedSurfaceSnapshot());

    expect(result).toBeInstanceOf(SnapshotValidationError);
    expect(result).toMatchObject({
      code: "SNAPSHOT_INVALID",
      message: "snapshot requires one PR title, one PR body, and at least one commit message",
    });
  });

  it("rejects an artifact whose surface is not one of the three supported surfaces", () => {
    const result = validateSnapshot(makeMalformedSurfaceSnapshot());

    expect(result).toBeInstanceOf(SnapshotValidationError);
    expect(result).toMatchObject({
      code: "SNAPSHOT_INVALID",
      message: "artifact surface must be pr-title, pr-body, or commit-message",
    });
  });

  it("rejects artifact and changed-file collections that are not lists", () => {
    const expected = {
      artifacts: "snapshot artifacts must be a list",
      changed_files: "snapshot changed_files must be a list",
    } as const;

    for (const field of ["artifacts", "changed_files"] as const) {
      const result = validateSnapshot(makeNonListCollectionSnapshot(field));

      expect(result).toBeInstanceOf(SnapshotValidationError);
      expect(result).toMatchObject({ code: "SNAPSHOT_INVALID", message: expected[field] });
    }
  });

  it("rejects artifact content that is not a string", () => {
    const result = validateSnapshot(makeMalformedContentSnapshot());

    expect(result).toBeInstanceOf(SnapshotValidationError);
    expect(result).toMatchObject({
      code: "SNAPSHOT_INVALID",
      message: "artifact content must be a string",
    });
  });

  it("rejects a malformed snapshot as a returned business error", () => {
    const result = validateSnapshot(makeMalformedSnapshot());

    expect(result).toBeInstanceOf(SnapshotValidationError);
    expect(result).toMatchObject({
      code: "SNAPSHOT_INVALID",
      message: "snapshot pr_number must be a positive integer",
    });
  });
});

describe("policy validation", () => {
  it("rejects a malformed policy as a returned business error", () => {
    const policy = loadApprovedPolicy();
    const result = validatePolicy(makeMalformedPolicy(policy, "identities"));

    expect(result).toBeInstanceOf(PolicyValidationError);
    expect(result).toMatchObject({
      code: "POLICY_INVALID",
      message: "policy identities must be a non-empty string list",
    });
  });
});
