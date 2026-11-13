/**
 * End to end: destination validation.
 *
 * One behavioral concern — a destination that cannot be synchronized is refused
 * before anything is written.
 *
 * Deliberately absent: a case that names the real AICore checkout as `--target`
 * to watch the inside-checkout guard reject it. That guard is authoritative and
 * is proven against the real adapter at the integration level and against the
 * use case at the unit level; pointing an end-to-end run at the operator's own
 * repository would make a failing guard the destructive path rather than the
 * tested one. Cleanup here can only ever name a directory this fixture created.
 */

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

describe("destination validation", () => {
  test("a destination that does not exist is refused", async () => {
    const created = await createFixture();
    fixture = created;

    const result = await invokeWithRevision(
      ["sync", "--target", join(created.destination, "absent"), "--editor", "opencode"],
      created,
    );

    expect(result.status).toBe(2);
    expect(result.stderr).toMatch(/not a directory/);
  });

  test("a file is refused as a destination", async () => {
    const created = await createFixture();
    fixture = created;

    const result = await invokeWithRevision(
      ["sync", "--target", join(created.destination, "AGENTS.md"), "--editor", "opencode"],
      created,
    );

    expect(result.status).toBe(2);
    expect(result.stderr).toMatch(/not a directory/);
  });
});
