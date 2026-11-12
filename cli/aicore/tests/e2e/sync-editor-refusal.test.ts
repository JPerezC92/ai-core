/**
 * End to end: editor refusal.
 *
 * One behavioral concern — a requested editor the engine does not implement is
 * refused by name and writes nothing.
 */

import { stat } from "node:fs/promises";
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
  test("Cursor is refused and writes nothing", async () => {
    const created = await createFixture();
    fixture = created;

    const result = await invokeWithRevision(
      ["sync", "--target", created.destination, "--editor", "cursor"],
      created,
    );

    expect(result.status).toBe(2);
    expect(result.stderr).toMatch(/not implemented/);
    expect(result.stderr).toMatch(/Nothing was written/);
    await expect(stat(join(created.destination, ".aicore"))).rejects.toThrow();
  });
});
