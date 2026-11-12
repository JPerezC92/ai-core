/**
 * End to end: editor refusal.
 *
 * One behavioral concern — a requested editor the engine does not implement is
 * refused by name and writes nothing.
 */

import assert from "node:assert/strict";
import { stat } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, describe, test } from "node:test";

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

    assert.equal(result.status, 2);
    assert.match(result.stderr, /not implemented/);
    assert.match(result.stderr, /Nothing was written/);
    await assert.rejects(stat(join(created.destination, ".aicore")));
  });
});
