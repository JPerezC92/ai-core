/**
 * Integration: the operator-local selection store against a real temporary file.
 *
 * Exercises the real adapter across its filesystem boundary (contract T4), with
 * per-test isolation (T18), and separates genuine absence from corrupt persisted
 * state (C8, C9).
 */

import assert from "node:assert/strict";
import { mkdtemp, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { afterEach, beforeEach, describe, test } from "node:test";

import {
  CorruptSelectionError,
  LocalJsonSelectionStore,
} from "#infrastructure/selection-store.ts";
import { makeSavedSelection } from "#support/aicore-cli.factory.ts";

let root: string;

beforeEach(async () => {
  root = await mkdtemp(join(tmpdir(), "aicore-cli-store-"));
});

afterEach(async () => {
  await rm(root, { recursive: true, force: true });
});

async function writeConfig(body: string): Promise<void> {
  await mkdir(join(root, ".aicore"), { recursive: true });
  await writeFile(join(root, ".aicore", "local.json"), body, "utf8");
}

describe("LocalJsonSelectionStore", () => {
  test("an absent file is an empty lookup result, not an error", async () => {
    assert.equal(await new LocalJsonSelectionStore(root).read(), undefined);
  });

  test("a written selection reads back identically", async () => {
    const store = new LocalJsonSelectionStore(root);
    const selection = makeSavedSelection();
    await store.write(selection);
    assert.deepEqual(await store.read(), selection);
  });

  test("a later write replaces the earlier selection", async () => {
    const store = new LocalJsonSelectionStore(root);
    await store.write(makeSavedSelection({ target: "G:/first" }));
    await store.write(makeSavedSelection({ target: "G:/second" }));
    assert.equal((await store.read())?.target, "G:/second");
  });

  test("the persisted document carries a version and the selection only", async () => {
    const store = new LocalJsonSelectionStore(root);
    const selection = makeSavedSelection();
    await store.write(selection);
    assert.deepEqual(JSON.parse(await readFile(join(root, ".aicore", "local.json"), "utf8")), {
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
    assert.deepEqual(JSON.parse(await readFile(override, "utf8")), {
      version: 1,
      target: selection.target,
      editor: selection.editor,
    });
  });
});

describe("corrupt persisted state", () => {
  test("malformed JSON is reported, not coerced into absence", async () => {
    await writeConfig("{ not json");
    await assert.rejects(
      new LocalJsonSelectionStore(root).read(),
      CorruptSelectionError,
    );
  });

  test("a non-object document is reported", async () => {
    await writeConfig("[]");
    await assert.rejects(
      new LocalJsonSelectionStore(root).read(),
      CorruptSelectionError,
    );
  });

  test("an unknown document version is reported", async () => {
    await writeConfig(JSON.stringify({ version: 99, target: "G:/x", editor: "opencode" }));
    await assert.rejects(
      new LocalJsonSelectionStore(root).read(),
      CorruptSelectionError,
    );
  });

  test("an unsupported editor is reported rather than ignored", async () => {
    await writeConfig(JSON.stringify({ version: 1, target: "G:/x", editor: "cursor" }));
    await assert.rejects(
      new LocalJsonSelectionStore(root).read(),
      CorruptSelectionError,
    );
  });

  test("a missing destination is reported", async () => {
    await writeConfig(JSON.stringify({ version: 1, target: "", editor: "opencode" }));
    await assert.rejects(
      new LocalJsonSelectionStore(root).read(),
      CorruptSelectionError,
    );
  });
});
