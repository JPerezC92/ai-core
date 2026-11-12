/**
 * Integration: the disposable-root helper the suites use to own and delete.
 *
 * One behavioral concern — a fixture may delete only a directory it created,
 * and the ownership predicate rejects every other shape. Exercised against a
 * real temporary filesystem (T4) with per-test isolation (T18).
 *
 * The two refusal cases name paths that do not exist, so even a broken guard
 * could only issue a force-delete no-op; no real directory is ever a target.
 */

import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import {
  UnsafeCleanupTargetError,
  createTemporaryRoot,
  disposeTemporaryRoot,
  isOwnedTemporaryRoot,
} from "#support/disposable-root.ts";

/** Prefix that identifies a root this suite owns. */
const ROOT_PREFIX = "aicore-cli-root-";

let root: string;
let rootPrefix: string;

beforeEach(async () => {
  const created = await createTemporaryRoot(ROOT_PREFIX);
  root = created.root;
  rootPrefix = created.prefix;
});

afterEach(async () => {
  await disposeTemporaryRoot(root, rootPrefix);
});

describe("ownership predicate", () => {
  test("a root this fixture created is owned", () => {
    expect(isOwnedTemporaryRoot(root, rootPrefix)).toBe(true);
  });

  test("the operating system temporary directory itself is never owned", () => {
    expect(isOwnedTemporaryRoot(tmpdir(), ROOT_PREFIX)).toBe(false);
  });

  test("a path outside the temporary directory is not owned", () => {
    expect(isOwnedTemporaryRoot(join(tmpdir(), "..", "aicore-decoy"), ROOT_PREFIX)).toBe(false);
  });

  test("a temporary path without the owning prefix is not owned", () => {
    expect(isOwnedTemporaryRoot(join(tmpdir(), "someone-elses-root"), ROOT_PREFIX)).toBe(false);
  });

  test("a traversal segment cannot escape the temporary directory", () => {
    expect(
      isOwnedTemporaryRoot(join(root, "..", "..", "aicore-outside"), ROOT_PREFIX),
    ).toBe(false);
  });
});

describe("cleanup refusal", () => {
  test("cleanup refuses a path outside the temporary directory", async () => {
    await expect(
      disposeTemporaryRoot(join(tmpdir(), "..", "aicore-not-owned-decoy"), ROOT_PREFIX),
    ).rejects.toThrow(UnsafeCleanupTargetError);
  });

  test("cleanup refuses a temporary path without the owning prefix", async () => {
    await expect(
      disposeTemporaryRoot(join(tmpdir(), "aicore-other-prefix-decoy"), ROOT_PREFIX),
    ).rejects.toThrow(UnsafeCleanupTargetError);
  });
});
