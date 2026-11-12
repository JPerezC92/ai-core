/**
 * End to end: revision availability.
 *
 * One behavioral concern — the source revision must be supplied by configuration,
 * and the tool never reaches for Git.
 */

import { stat } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, describe, expect, test } from "vitest";

import { createFixture, invoke, type Fixture } from "#support/aicore-cli.e2e-harness.ts";

let fixture: Fixture | undefined;

afterEach(async () => {
  await fixture?.dispose();
  fixture = undefined;
});

describe("revision availability", () => {
  test("a missing revision stops the run without writing", async () => {
    const created = await createFixture();
    fixture = created;

    const result = await invoke(
      ["sync", "--target", created.destination, "--editor", "opencode"],
      { fixture: created, revision: undefined },
    );

    expect(result.status).toBe(2);
    expect(result.stderr).toMatch(/no source revision available/);
    expect(result.stderr).toMatch(/never runs Git/);
    expect(result.stderr).toMatch(/Herald/);
    await expect(stat(join(created.destination, ".aicore"))).rejects.toThrow();
  });

  test("a malformed revision is rejected", async () => {
    const created = await createFixture();
    fixture = created;

    const result = await invoke(
      ["sync", "--target", created.destination, "--editor", "opencode"],
      { fixture: created, revision: "not-a-revision" },
    );

    expect(result.status).toBe(2);
    expect(result.stderr).toMatch(/40-character lowercase hex/);
    await expect(stat(join(created.destination, ".aicore"))).rejects.toThrow();
  });
});
