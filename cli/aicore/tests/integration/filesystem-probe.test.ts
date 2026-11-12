/**
 * Integration: the filesystem probe adapter across its real boundary.
 *
 * Exercises the real containment rule that refuses a destination inside the
 * source checkout, using synthetic temporary paths only (contract T4, T18).
 *
 * This replaces the former end-to-end case that named the operator's actual
 * checkout as a target: the behaviour is identical, but no assertion here can
 * ever resolve to a real project directory.
 */

import assert from "node:assert/strict";
import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";

import { LocalFilesystemProbe } from "#infrastructure/filesystem-probe.ts";
import {
  createTemporaryRoot,
  disposeTemporaryRoot,
} from "#support/disposable-root.ts";

/** Prefix that identifies a root this suite owns. */
const ROOT_PREFIX = "aicore-cli-probe-";

let root: string;
let rootPrefix: string;
const probe = new LocalFilesystemProbe();

beforeEach(async () => {
  const created = await createTemporaryRoot(ROOT_PREFIX);
  root = created.root;
  rootPrefix = created.prefix;
});

afterEach(async () => {
  await disposeTemporaryRoot(root, rootPrefix);
});

describe("containment rule", () => {
  test("a directory inside the given root is reported as inside", () => {
    assert.equal(probe.isInside(root, join(root, "nested")), true);
    assert.equal(probe.isInside(root, join(root, "nested", "deeper")), true);
  });

  test("the root itself counts as inside", () => {
    assert.equal(probe.isInside(root, root), true);
  });

  test("a sibling or parent path is not inside", () => {
    assert.equal(probe.isInside(join(root, "checkout"), join(root, "other")), false);
    assert.equal(probe.isInside(join(root, "checkout"), root), false);
  });

  test("a path that merely shares a name prefix is not inside", () => {
    // Guards against a naive `startsWith` without a separator.
    assert.equal(probe.isInside(join(root, "core"), join(root, "core-two")), false);
  });

  test("a traversal segment cannot escape the root", () => {
    assert.equal(probe.isInside(join(root, "core"), join(root, "core", "..", "outside")), false);
  });
});

describe("existence probes distinguish absence from presence", () => {
  test("an absent path is neither a directory nor a file", async () => {
    const absent = join(root, "absent");
    assert.equal(await probe.isDirectory(absent), false);
    assert.equal(await probe.isFile(absent), false);
  });

  test("a real directory and a real file are reported correctly", async () => {
    const directory = join(root, "present");
    await mkdir(directory);
    const file = join(root, "present.txt");
    await writeFile(file, "content", "utf8");

    assert.equal(await probe.isDirectory(directory), true);
    assert.equal(await probe.isFile(directory), false);
    assert.equal(await probe.isFile(file), true);
    assert.equal(await probe.isDirectory(file), false);
  });
});
