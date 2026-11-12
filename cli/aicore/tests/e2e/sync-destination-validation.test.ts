/**
 * End to end: destination validation.
 *
 * One behavioral concern — a destination that cannot be synchronized is refused
 * before anything is written.
 */

import assert from "node:assert/strict";
import { join } from "node:path";
import { afterEach, describe, test } from "node:test";

import {
  CHECKOUT,
  createFixture,
  invokeWithRevision,
  type Fixture,
} from "#support/aicore-cli.e2e-harness.ts";

let fixture: Fixture | undefined;

afterEach(async () => {
  await fixture?.dispose();
  fixture = undefined;
});

describe("destination validation", () => {
  test("a destination that does not exist is refused", async () => {
    const created = await createFixture();
    fixture = created;

    const result = await invokeWithRevision(
      ["sync", "--target", join(created.destination, "absent"), "--editor", "opencode"],
      created,
    );

    assert.equal(result.status, 2);
    assert.match(result.stderr, /not a directory/);
  });

  test("the checkout itself is refused as a destination", async () => {
    const created = await createFixture();
    fixture = created;

    const result = await invokeWithRevision(
      ["sync", "--target", CHECKOUT, "--editor", "opencode"],
      created,
    );

    assert.equal(result.status, 2);
    assert.match(result.stderr, /inside the AICore checkout/);
  });
});
