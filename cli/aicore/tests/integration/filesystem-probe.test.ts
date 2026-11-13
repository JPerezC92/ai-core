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

import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

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
    expect(probe.isInside(root, join(root, "nested"))).toBe(true);
    expect(probe.isInside(root, join(root, "nested", "deeper"))).toBe(true);
  });

  test("the root itself counts as inside", () => {
    expect(probe.isInside(root, root)).toBe(true);
  });

  test("a sibling or parent path is not inside", () => {
    expect(probe.isInside(join(root, "checkout"), join(root, "other"))).toBe(false);
    expect(probe.isInside(join(root, "checkout"), root)).toBe(false);
  });

  test("a path that merely shares a name prefix is not inside", () => {
    // Guards against a naive `startsWith` without a separator.
    expect(probe.isInside(join(root, "core"), join(root, "core-two"))).toBe(false);
  });

  test("a traversal segment cannot escape the root", () => {
    expect(probe.isInside(join(root, "core"), join(root, "core", "..", "outside"))).toBe(false);
  });
});

describe("existence probes distinguish absence from presence", () => {
  test("an absent path is neither a directory nor a file", async () => {
    const absent = join(root, "absent");
    expect(await probe.isDirectory(absent)).toBe(false);
    expect(await probe.isFile(absent)).toBe(false);
  });

  test("a real directory and a real file are reported correctly", async () => {
    const directory = join(root, "present");
    await mkdir(directory);
    const file = join(root, "present.txt");
    await writeFile(file, "content", "utf8");

    expect(await probe.isDirectory(directory)).toBe(true);
    expect(await probe.isFile(directory)).toBe(false);
    expect(await probe.isFile(file)).toBe(true);
    expect(await probe.isDirectory(file)).toBe(false);
  });
});
