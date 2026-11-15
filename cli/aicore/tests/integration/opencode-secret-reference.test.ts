/**
 * Integration: the shipped Context7 secret reference, resolved as OpenCode
 * resolves it.
 *
 * One behavioral concern — the `{file:...}` reference the cleared OpenCode
 * configuration carries is relative to the directory holding that configuration
 * file, so it names the destination project's own `.secrets/` directory. It is
 * read from the shipped configuration rather than restated here, so moving the
 * configuration or rewriting the reference without moving the secret fails this
 * suite. With the secret file absent the resolved target stays inside the
 * project: nothing is read from the parent directory.
 */

import { mkdir, readFile, stat, writeFile } from "node:fs/promises";
import { dirname, isAbsolute, join, relative, resolve } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import { parseJsoncObject } from "#domain/synchronization/jsonc.ts";
import {
  createTemporaryRoot,
  disposeTemporaryRoot,
} from "#support/disposable-root.ts";

/** Prefix that identifies a root this suite owns. */
const ROOT_PREFIX = "aicore-cli-secret-reference-";

/** The checkout the shipped configuration is read from. */
const CHECKOUT = resolve(dirname(import.meta.dirname), "..", "..", "..");

/** The cleared OpenCode configuration, source-side and destination-side. */
const CONFIG_RELATIVE_PATH = join(".opencode", "opencode.jsonc");

/** The secret file name the header names, and its project-relative directory. */
const SECRET_RELATIVE_PATH = join(".secrets", "context7-api-key");

/** A placeholder that is not a credential. */
const PLACEHOLDER = "not-a-credential-placeholder\n";

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

/** Read one member of a parsed JSON value, or `undefined`. */
function member(value: unknown, key: string): unknown {
  return typeof value === "object" && value !== null
    ? (value as Record<string, unknown>)[key]
    : undefined;
}

/**
 * The `{file:...}` reference the shipped configuration carries.
 *
 * The header is read from the real file, so this suite measures the shipped
 * artifact; a configuration this parser cannot read fails the test instead of
 * being skipped.
 */
async function shippedReference(): Promise<string> {
  const text = await readFile(join(CHECKOUT, CONFIG_RELATIVE_PATH), "utf8");
  const object = parseJsoncObject(text);
  expect(object, `${CONFIG_RELATIVE_PATH} must be a JSONC object`).not.toBeNull();

  const servers = member(member(object?.value, "mcp"), "servers");
  const headers = member(member(servers, "context7"), "headers");
  const reference = member(headers, "CONTEXT7_API_KEY");
  expect(typeof reference).toBe("string");
  const match = /^\{file:(.+)\}$/u.exec(reference as string);
  expect(match, `the Context7 header must be a {file:...} reference: ${String(reference)}`).not.toBeNull();
  return match?.[1] ?? "";
}

/** Create a destination holding only the cleared configuration's directory. */
async function destinationDirectory(): Promise<string> {
  const destination = join(root, "destination");
  await mkdir(join(destination, ".opencode"), { recursive: true });
  return destination;
}

describe("the shipped Context7 secret reference", () => {
  test("resolves into the destination project's own .secrets/, not its parent", async () => {
    const reference = await shippedReference();
    expect(isAbsolute(reference)).toBe(false);

    const destination = await destinationDirectory();
    await mkdir(join(destination, ".secrets"), { recursive: true });
    await writeFile(join(destination, SECRET_RELATIVE_PATH), PLACEHOLDER, "utf8");

    // A decoy in the destination's parent proves the reference is not resolved
    // against the project root's parent.
    await mkdir(join(root, ".secrets"), { recursive: true });
    await writeFile(join(root, SECRET_RELATIVE_PATH), "parent decoy\n", "utf8");

    const resolved = resolve(join(destination, ".opencode"), reference);

    expect(resolved).toBe(join(destination, SECRET_RELATIVE_PATH));
    expect(resolved).not.toBe(join(root, SECRET_RELATIVE_PATH));
    const fromDestination = relative(destination, resolved);
    expect(isAbsolute(fromDestination)).toBe(false);
    expect(fromDestination.startsWith("..")).toBe(false);
    expect(await readFile(resolved, "utf8")).toBe(PLACEHOLDER);
  });

  test("stays inside the project when the secret file is absent", async () => {
    const reference = await shippedReference();

    const destination = await destinationDirectory();
    await mkdir(join(root, ".secrets"), { recursive: true });
    await writeFile(join(root, SECRET_RELATIVE_PATH), "parent decoy\n", "utf8");

    const resolved = resolve(join(destination, ".opencode"), reference);

    // Absence is absence: the target is still the project's own path, and the
    // parent directory's file is never what the reference names.
    expect(resolved).toBe(join(destination, SECRET_RELATIVE_PATH));
    expect(resolved).not.toBe(join(root, SECRET_RELATIVE_PATH));
    const fromDestination = relative(destination, resolved);
    expect(isAbsolute(fromDestination)).toBe(false);
    expect(fromDestination.startsWith("..")).toBe(false);
    await expect(stat(resolved)).rejects.toThrow();
  });
});
