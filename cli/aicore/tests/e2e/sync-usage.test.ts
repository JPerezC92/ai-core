/**
 * End to end: usage surface.
 *
 * One behavioral concern — the wrapper's own argument handling and help text.
 */

import { afterEach, describe, expect, test } from "vitest";

import {
  createFixture,
  invoke,
  type Fixture,
} from "#support/aicore-cli.e2e-harness.ts";

let fixture: Fixture | undefined;

afterEach(async () => {
  await fixture?.dispose();
  fixture = undefined;
});

describe("usage surface", () => {
  test("an unknown option is reported, not silently ignored", async () => {
    const created = await createFixture();
    fixture = created;

    const result = await invoke(["sync", "--dest", created.destination], {
      fixture: created,
    });

    expect(result.status).toBe(2);
    expect(result.stderr).toMatch(/unrecognized option "--dest"/);
  });

  test("help is available without configuration", async () => {
    const created = await createFixture();
    fixture = created;

    const result = await invoke(["--help"], { fixture: created, revision: undefined });

    expect(result.status).toBe(0);
    expect(result.stdout).toMatch(/pnpm aicore sync/);
    expect(result.stdout).toMatch(/never runs Git/);
    expect(result.stdout).toMatch(/AICORE_SOURCE_REVISION/);
  });
});
