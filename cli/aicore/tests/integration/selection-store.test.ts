/**
 * Integration: the operator-local selection store against a real temporary file.
 *
 * Exercises the real adapter across its filesystem boundary (contract T4), with
 * per-test isolation (T18), and separates genuine absence from corrupt persisted
 * state (C8, C9).
 */

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import {
  CorruptSelectionError,
  LocalJsonSelectionStore,
} from "#infrastructure/selection-store.ts";
import { makeSavedSelection } from "#support/aicore-cli.factory.ts";
import {
  createTemporaryRoot,
  disposeTemporaryRoot,
} from "#support/disposable-root.ts";

/** Prefix that identifies a root this suite owns. */
const ROOT_PREFIX = "aicore-cli-store-";

let root: string;
let rootPrefix: string;

beforeEach(async () => {
  const created = await createTemporaryRoot(ROOT_PREFIX);
  root = created.root;
  rootPrefix = created.prefix;
});

afterEach(async () => {
  // Ownership is re-validated here, immediately before deletion.
  await disposeTemporaryRoot(root, rootPrefix);
});

async function writeConfig(body: string): Promise<void> {
  await mkdir(join(root, ".aicore"), { recursive: true });
  await writeFile(join(root, ".aicore", "local.json"), body, "utf8");
}

describe("LocalJsonSelectionStore", () => {
  test("an absent file is an empty lookup result, not an error", async () => {
    expect(await new LocalJsonSelectionStore(root).read()).toBe(undefined);
  });

  test("a written selection reads back identically", async () => {
    const store = new LocalJsonSelectionStore(root);
    const selection = makeSavedSelection();
    await store.write(selection);
    expect(await store.read()).toEqual(selection);
  });

  test("a later write replaces the earlier selection", async () => {
    const store = new LocalJsonSelectionStore(root);
    await store.write(makeSavedSelection({ target: "G:/first" }));
    await store.write(makeSavedSelection({ target: "G:/second" }));
    expect((await store.read())?.target).toBe("G:/second");
  });

  test("the persisted document carries a version and the selection only", async () => {
    const store = new LocalJsonSelectionStore(root);
    const selection = makeSavedSelection();
    await store.write(selection);
    expect(JSON.parse(await readFile(join(root, ".aicore", "local.json"), "utf8"))).toEqual({
      version: 1,
      target: selection.target,
      editor: selection.editor,
    });
  });

  test("an explicit path override is honoured", async () => {
    const override = join(root, "nested", "selection.json");
    const store = new LocalJsonSelectionStore(root, override);
    const selection = makeSavedSelection();
    await store.write(selection);
    expect(JSON.parse(await readFile(override, "utf8"))).toEqual({
      version: 1,
      target: selection.target,
      editor: selection.editor,
    });
  });
});

describe("corrupt persisted state", () => {
  test("malformed JSON is reported, not coerced into absence", async () => {
    await writeConfig("{ not json");
    await expect(new LocalJsonSelectionStore(root).read()).rejects.toThrow(
      CorruptSelectionError,
    );
  });

  test("a non-object document is reported", async () => {
    await writeConfig("[]");
    await expect(new LocalJsonSelectionStore(root).read()).rejects.toThrow(
      CorruptSelectionError,
    );
  });

  test("an unknown document version is reported", async () => {
    await writeConfig(JSON.stringify({ version: 99, target: "G:/x", editor: "opencode" }));
    await expect(new LocalJsonSelectionStore(root).read()).rejects.toThrow(
      CorruptSelectionError,
    );
  });

  test("an unsupported editor is reported rather than ignored", async () => {
    await writeConfig(JSON.stringify({ version: 1, target: "G:/x", editor: "cursor" }));
    await expect(new LocalJsonSelectionStore(root).read()).rejects.toThrow(
      CorruptSelectionError,
    );
  });

  test("a missing destination is reported", async () => {
    await writeConfig(JSON.stringify({ version: 1, target: "", editor: "opencode" }));
    await expect(new LocalJsonSelectionStore(root).read()).rejects.toThrow(
      CorruptSelectionError,
    );
  });
});
