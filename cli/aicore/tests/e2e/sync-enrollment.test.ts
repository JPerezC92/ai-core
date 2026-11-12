/**
 * End to end: enrollment and the subsequent update.
 *
 * Runs the real CLI against the real Python engine. A full synchronization takes
 * tens of seconds because the engine walks the whole cleared set, so this module
 * holds the single test that performs two writes.
 */

import { readFile, stat } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, describe, expect, test } from "vitest";

import {
  REVISION,
  createFixture,
  invokeWithRevision,
  type Fixture,
} from "#support/aicore-cli.e2e-harness.ts";

let fixture: Fixture | undefined;

afterEach(async () => {
  await fixture?.dispose();
  fixture = undefined;
});

describe("enrollment and update", () => {
  test("enrollment writes the payload, then a second run updates using the saved selection", async () => {
    const created = await createFixture();
    fixture = created;
    const { destination, configPath } = created;

    const first = await invokeWithRevision(
      ["sync", "--target", destination, "--editor", "opencode"],
      created,
    );

    // Enrollment succeeds; verification then reports the pending reconciliation
    // the destination project itself must clear. Neither state is overridden.
    expect(first.stdout).toMatch(/initialized/);
    expect(first.status).not.toBe(0);

    const bindings = await readFile(join(destination, ".aicore", "core.yaml"), "utf8");
    expect(bindings).toMatch(/^schema: 1$/m);
    expect(bindings).toMatch(new RegExp(`^core_revision: ${REVISION}$`, "m"));
    expect(bindings).toMatch(/^pending:$/m);

    // Native discovery locations and shipped documentation are present.
    expect((await stat(join(destination, ".opencode", "agents"))).isDirectory()).toBeTruthy();
    expect((await stat(join(destination, "knowledge", "agents.md"))).isFile()).toBeTruthy();
    expect((await stat(join(destination, "architecture", "README.md"))).isFile()).toBeTruthy();
    expect((await stat(join(destination, "odd", "tasks", "_template.md"))).isFile()).toBeTruthy();

    // The engine's own skill is never distributed to a destination.
    await expect(stat(join(destination, ".opencode", "skills", "core-sync"))).rejects.toThrow();

    // Region and project markers survive, and the fixture's own text is kept.
    const agents = await readFile(join(destination, "AGENTS.md"), "utf8");
    for (const marker of ["core:begin", "core:end", "project:begin", "project:end"]) {
      expect(agents).toMatch(new RegExp(`<!-- ${marker} -->`));
    }
    expect(agents).toMatch(/A disposable destination for end-to-end verification/);

    // The explicit selection was recorded in the isolated selection file.
    const saved = JSON.parse(await readFile(configPath, "utf8"));
    expect(saved.editor).toBe("opencode");
    expect(saved.target).toBe(destination);

    // A second run needs no arguments and updates instead of re-enrolling.
    const second = await invokeWithRevision(["sync"], created);
    expect(second.stdout).toMatch(/applied/);
    expect(second.stdout).not.toMatch(/initialized/);
  });
});
