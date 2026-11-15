/**
 * Integration: OpenCode secret-directory writes after payload delivery.
 *
 * Four OpenCode outcomes — create the directory, empty placeholder and ignore
 * rule; preserve existing secret bytes; leave an existing ignore rule alone;
 * append the rule when other rules exist — and Cursor creates none of them.
 */

import { mkdir, readFile, stat, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, beforeEach, describe, expect, test } from "vitest";

import { ensureOpenCodeSecrets } from "#application/synchronization/open-code-secrets.ts";
import { LocalDestinationFiles } from "#infrastructure/synchronization/local-destination-files.ts";
import { LocalFilesystemLayout } from "#infrastructure/synchronization/local-filesystem-layout.ts";
import {
  createTemporaryRoot,
  disposeTemporaryRoot,
} from "#support/disposable-root.ts";

const ROOT_PREFIX = "aicore-cli-open-code-secrets-";

let root: string;
let prefix: string;

beforeEach(async () => {
  const created = await createTemporaryRoot(ROOT_PREFIX);
  root = created.root;
  prefix = created.prefix;
});

afterEach(async () => {
  await disposeTemporaryRoot(root, prefix);
});

async function run(editor: "opencode" | "cursor"): Promise<void> {
  if (editor === "opencode") {
    await mkdir(join(root, ".opencode"), { recursive: true });
    await writeFile(join(root, ".opencode", "opencode.jsonc"), "{}\n", "utf8");
  }
  await ensureOpenCodeSecrets(editor, root, {
    destinations: new LocalDestinationFiles(),
    layout: new LocalFilesystemLayout(),
  });
}

describe("ensureOpenCodeSecrets", () => {
  test("OpenCode creates the directory, an empty credential file, and the ignore rule", async () => {
    await run("opencode");

    expect((await stat(join(root, ".secrets"))).isDirectory()).toBe(true);
    const secret = await readFile(join(root, ".secrets", "context7-api-key"));
    expect(secret.byteLength).toBe(0);
    expect(await readFile(join(root, ".gitignore"), "utf8")).toBe(".secrets/\n");
  });

  test("OpenCode preserves existing secret bytes", async () => {
    await mkdir(join(root, ".secrets"), { recursive: true });
    const existing = new Uint8Array([1, 2, 3]);
    await writeFile(join(root, ".secrets", "context7-api-key"), existing);
    await run("opencode");
    expect(await readFile(join(root, ".secrets", "context7-api-key"))).toEqual(
      Buffer.from(existing),
    );
  });

  test("OpenCode leaves an existing ignore rule alone", async () => {
    const existing = "node_modules/\n.secrets/\n*.log\n";
    await writeFile(join(root, ".gitignore"), existing, "utf8");
    await run("opencode");
    expect(await readFile(join(root, ".gitignore"), "utf8")).toBe(existing);
  });

  test("OpenCode appends the rule when other rules exist", async () => {
    await writeFile(join(root, ".gitignore"), "dist", "utf8");
    await run("opencode");
    expect(await readFile(join(root, ".gitignore"), "utf8")).toBe("dist\n.secrets/\n");
  });

  test("Cursor creates neither the secret directory nor an ignore rule", async () => {
    await run("cursor");
    await expect(stat(join(root, ".secrets"))).rejects.toThrow();
    await expect(stat(join(root, ".gitignore"))).rejects.toThrow();
  });
});
