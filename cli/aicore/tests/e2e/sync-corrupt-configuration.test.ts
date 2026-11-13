/**
 * End to end: corrupt operator configuration.
 *
 * One behavioral concern — a corrupt operator selection file is reported as a
 * configuration failure at the assembled entry point, not as a crash and not
 * silently ignored.
 */

import { stat, writeFile } from "node:fs/promises";
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

describe("corrupt operator configuration", () => {
  test("a corrupt selection file is reported and writes nothing", async () => {
    const created = await createFixture();
    fixture = created;
    await writeFile(created.configPath, "{ not json", "utf8");

    const result = await invokeWithRevision(["sync"], created);

    expect(result.status).toBe(2);
    expect(result.stderr).toMatch(/not valid JSON/);
    // A reported failure, not an unhandled crash.
    expect(result.stderr).not.toMatch(/at file:|Error \[|node:internal/);
    await expect(stat(join(created.destination, ".aicore"))).rejects.toThrow();
  });
});
