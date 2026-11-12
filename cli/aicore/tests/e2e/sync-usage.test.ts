/**
 * End to end: usage surface.
 *
 * One behavioral concern — the wrapper's own argument handling and help text.
 */

import assert from "node:assert/strict";
import { afterEach, describe, test } from "node:test";

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

    assert.equal(result.status, 2);
    assert.match(result.stderr, /unrecognized option "--dest"/);
  });

  test("help is available without configuration", async () => {
    const created = await createFixture();
    fixture = created;

    const result = await invoke(["--help"], { fixture: created, revision: undefined });

    assert.equal(result.status, 0);
    assert.match(result.stdout, /pnpm aicore sync/);
    assert.match(result.stdout, /never runs Git/);
    assert.match(result.stdout, /AICORE_SOURCE_REVISION/);
  });
});
