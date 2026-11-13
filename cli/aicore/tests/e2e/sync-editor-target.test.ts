/**
 * End to end: the Cursor editor target.
 *
 * One behavioral concern — a Cursor destination receives the shared content
 * identically, its agents in Cursor's own agent directory, and no project
 * configuration.
 */

import { readFile, stat } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, describe, expect, test } from "vitest";

import {
  createFixture,
  invokeWithRevision,
  type Fixture,
} from "#support/aicore-cli.e2e-harness.ts";

let fixture: Fixture | undefined;

afterEach(async () => {
  await fixture?.dispose();
  fixture = undefined;
});

describe("cursor editor target", () => {
  test("a cursor destination receives its agents in .cursor/agents and no project configuration", async () => {
    const created = await createFixture();
    fixture = created;
    const { destination, configPath } = created;

    const result = await invokeWithRevision(
      ["sync", "--target", destination, "--editor", "cursor"],
      created,
    );

    // Enrollment succeeds; the verification that follows reports the pending
    // reconciliation the destination project itself must clear.
    expect(result.stdout, `stderr: ${result.stderr}`).toMatch(/initialized/);

    // The agents land in Cursor's own agent directory, not in OpenCode's.
    expect((await stat(join(destination, ".cursor", "agents"))).isDirectory()).toBeTruthy();
    await expect(stat(join(destination, ".opencode", "agents"))).rejects.toThrow();

    // The shared content is delivered identically, at the same paths.
    expect(
      (await stat(join(destination, ".agents", "skills", "odd-workflow"))).isDirectory(),
    ).toBeTruthy();
    expect(
      (await stat(join(destination, ".aicore", "core", "knowledge", "agents.md"))).isFile(),
    ).toBeTruthy();

    // No project configuration: Cursor has no merge target to receive one.
    await expect(stat(join(destination, "opencode.jsonc"))).rejects.toThrow();

    // The enrollment records the editor profile the destination was enrolled for.
    const bindings = await readFile(join(destination, ".aicore", "core.yaml"), "utf8");
    expect(bindings).toMatch(/^editor: cursor$/m);

    // The explicit selection was recorded in the isolated selection file.
    const saved = JSON.parse(await readFile(configPath, "utf8"));
    expect(saved.editor).toBe("cursor");
    expect(saved.target).toBe(destination);
  });
});
