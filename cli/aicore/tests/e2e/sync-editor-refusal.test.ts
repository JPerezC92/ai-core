/**
 * End to end: editor refusal.
 *
 * One behavioral concern — a destination enrolled for one editor refuses a run
 * for another, by name, and writes nothing.
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

describe("editor refusal", () => {
  test("a destination enrolled for one editor refuses a run for another and writes nothing", async () => {
    const created = await createFixture({ editor: "opencode" });
    fixture = created;

    const result = await invokeWithRevision(
      ["sync", "--target", created.destination, "--editor", "cursor"],
      created,
    );

    expect(result.status).toBe(2);
    expect(result.stderr).toMatch(/enrolled for editor 'opencode'/);
    expect(result.stderr).toMatch(/requested 'cursor'/);
    expect(result.stderr).toMatch(/Nothing was written/);

    // The destination kept the bindings it had; no payload was written.
    const bindings = await readFile(join(created.destination, ".aicore", "core.yaml"), "utf8");
    expect(bindings).toMatch(/^editor: opencode$/m);
    await expect(stat(join(created.destination, ".cursor", "agents"))).rejects.toThrow();
    await expect(stat(join(created.destination, ".agents", "skills"))).rejects.toThrow();
  });
});
