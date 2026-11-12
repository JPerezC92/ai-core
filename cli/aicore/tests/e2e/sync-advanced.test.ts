/**
 * End to end: advanced command forwarding.
 *
 * One behavioral concern — the wrapper forwards each advanced subcommand to the
 * engine with the engine's own argument syntax and preserves its exit status.
 * Assertions are discriminating: they require engine-originated text and forbid
 * the wrapper's own rejection wording, so dropping a command from the wrapper's
 * vocabulary fails this module instead of passing it.
 */

import assert from "node:assert/strict";
import { afterEach, describe, test } from "node:test";

import {
  CHECKOUT,
  REVISION,
  createFixture,
  invokeWithRevision,
  type Fixture,
} from "#support/aicore-cli.e2e-harness.ts";

let fixture: Fixture | undefined;

afterEach(async () => {
  await fixture?.dispose();
  fixture = undefined;
});

describe("advanced command forwarding", () => {
  for (const command of ["check", "apply", "init"]) {
    test(`${command} reaches the engine and preserves its exit status`, async () => {
      const created = await createFixture();
      fixture = created;

      // The fixture has no bindings, so the engine reports malformed input with
      // its own message. The proof is that the engine ran and its text and status
      // were relayed unchanged.
      const result = await invokeWithRevision(
        [
          command,
          "--source",
          CHECKOUT,
          "--destination",
          created.destination,
          "--bindings",
          `${created.destination}/.aicore/core.yaml`,
          "--source-revision",
          REVISION,
        ],
        created,
      );

      assert.equal(result.status, 2);
      // Engine-originated text.
      assert.match(result.stderr, /invalid bindings/i);
      // Not a wrapper-side rejection.
      assert.doesNotMatch(result.stderr, /unknown command/i);
      assert.doesNotMatch(result.stdout, /^Usage:/m);

      await created.dispose();
      fixture = undefined;
    });
  }
});
