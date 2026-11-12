/**
 * End to end: revision availability.
 *
 * One behavioral concern — the source revision must be supplied by configuration,
 * and the tool never reaches for Git.
 */

import assert from "node:assert/strict";
import { stat } from "node:fs/promises";
import { join } from "node:path";
import { afterEach, describe, test } from "node:test";

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

    assert.equal(result.status, 2);
    assert.match(result.stderr, /no source revision available/);
    assert.match(result.stderr, /never runs Git/);
    assert.match(result.stderr, /Herald/);
    await assert.rejects(stat(join(created.destination, ".aicore")));
  });

  test("a malformed revision is rejected", async () => {
    const created = await createFixture();
    fixture = created;

    const result = await invoke(
      ["sync", "--target", created.destination, "--editor", "opencode"],
      { fixture: created, revision: "not-a-revision" },
    );

    assert.equal(result.status, 2);
    assert.match(result.stderr, /40-character lowercase hex/);
    await assert.rejects(stat(join(created.destination, ".aicore")));
  });
});
