/**
 * Integration: the reconciliation blocker across the enrolled editors.
 *
 * One behavioral concern — the block a real destination root receives keeps
 * every shared paragraph for every enrolled editor, and leaves out only the
 * project-configuration section, which describes a file an editor's own
 * delivery does not reach. The parity corpus has no editor vocabulary and this
 * suite does not enter it.
 */

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import { RECONCILE_BEGIN, RECONCILE_END } from "#domain/synchronization/constants.ts";
import type { EditorProfile } from "#domain/synchronization/editor-profile.ts";
import { LocalFilesystemLayout } from "#infrastructure/synchronization/local-filesystem-layout.ts";
import {
  createTemporaryRoot,
  disposeTemporaryRoot,
} from "#support/disposable-root.ts";
import { makeBindingsDocument } from "#support/synchronization.factory.ts";

/** Prefix that identifies a root this suite owns. */
const ROOT_PREFIX = "aicore-cli-reconciliation-blocker-";

/** The root runtime file the blocker is written into. */
const ROOT_FILE = "AGENTS.md";

/** Text that must survive the blocker write outside the block. */
const ROOT_TEXT = "# Destination\n";

/** The section only an editor whose delivery includes the config file receives. */
const CONFIG_SECTION = /opencode\.jsonc|QMD index/u;

/** Paragraph openings the block shares with every enrolled editor. */
const SHARED_ANCHORS = [
  "**Permanent rule — adopt it now",
  "**What happened.**",
  "**Do this for every file listed",
  "**To finish.**",
];

let root: string;
let rootPrefix: string;
const layout = new LocalFilesystemLayout();

beforeEach(async () => {
  const created = await createTemporaryRoot(ROOT_PREFIX);
  root = created.root;
  rootPrefix = created.prefix;
});

afterEach(async () => {
  await disposeTemporaryRoot(root, rootPrefix);
});

/** Write the blocker for one editor into its own destination and read it back. */
async function syncInto(editor: EditorProfile): Promise<string> {
  const destination = join(root, editor);
  await mkdir(destination);
  const rootFile = join(destination, ROOT_FILE);
  await writeFile(rootFile, ROOT_TEXT, "utf8");

  await layout.syncBlocker(
    destination,
    makeBindingsDocument({ editor }),
    ["AGENTS.md"],
  );

  return readFile(rootFile, "utf8");
}

/** The block's own lines, markers excluded, unwrapped from the quote prefix. */
function blockLines(text: string): readonly string[] {
  const lines = text.split("\n");
  const begin = lines.findIndex((line) => line === RECONCILE_BEGIN);
  const end = lines.findIndex((line) => line === RECONCILE_END);
  expect(begin).toBeGreaterThanOrEqual(0);
  expect(end).toBeGreaterThan(begin);
  return lines
    .slice(begin + 1, end)
    .map((line) => line.replace(/^> ?/u, "").trim())
    .filter((line) => line !== "");
}

describe("the blocker's project-configuration section", () => {
  test("Cursor omits it and keeps every shared paragraph", async () => {
    const opencode = await syncInto("opencode");
    const cursor = await syncInto("cursor");

    const opencodeLines = blockLines(opencode);
    const cursorLines = blockLines(cursor);
    const configLines = opencodeLines.filter((line) => CONFIG_SECTION.test(line));

    // The OpenCode body is the reference: it holds the section, and it holds the
    // shared paragraphs the equality below would otherwise not prove present.
    expect(configLines.length).toBeGreaterThan(0);
    for (const anchor of SHARED_ANCHORS) {
      expect(opencodeLines.some((line) => line.includes(anchor))).toBe(true);
    }

    // The section is the only difference: a reintroduced section for Cursor, or a
    // dropped shared paragraph, both break this equality.
    expect(cursorLines).toEqual(
      opencodeLines.filter((line) => !configLines.includes(line)),
    );
    expect(cursor).not.toMatch(CONFIG_SECTION);

    // The write is confined to the block, for both editors.
    expect(opencode.startsWith(`${ROOT_TEXT}\n${RECONCILE_BEGIN}`)).toBe(true);
    expect(cursor.startsWith(`${ROOT_TEXT}\n${RECONCILE_BEGIN}`)).toBe(true);
    expect(cursor.endsWith(`${RECONCILE_END}\n`)).toBe(true);
  });
});
