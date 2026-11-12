/**
 * Unit: updating a destination that is already bound.
 *
 * One behavioral concern — the update path never re-enrolls and never carries the
 * enrollment flag (contract T2, application use case with doubled ports).
 */

import assert from "node:assert/strict";
import { describe, test } from "node:test";

import { SynchronizeDestination } from "#application/synchronize-destination.ts";
import {
  BINDINGS_PATH,
  CHECKOUT_ROOT,
  DESTINATION_PATH,
  MemorySelections,
  RecordingEngine,
  StubFiles,
  makeSavedSelection,
  makeSettings,
} from "#support/aicore-cli.factory.ts";

function operation(options: {
  engine: RecordingEngine;
  selections?: MemorySelections;
}) {
  return new SynchronizeDestination({
    checkoutRoot: CHECKOUT_ROOT,
    settings: makeSettings(),
    engine: options.engine,
    files: new StubFiles({
      directories: [DESTINATION_PATH],
      files: [BINDINGS_PATH],
    }),
    selections: options.selections ?? new MemorySelections(makeSavedSelection()),
  });
}

describe("update decision", () => {
  test("a bound destination is updated with apply and never re-enrolled", async () => {
    const engine = new RecordingEngine([0, 0]);

    const result = await operation({ engine }).execute({
      target: undefined,
      editor: undefined,
      revision: undefined,
    });

    assert.ok(result.ok);
    assert.deepEqual(
      engine.calls.map((call) => call.command),
      ["apply", "check"],
    );
    assert.ok(
      !engine.calls[0]?.arguments_.includes("--bind-cleared"),
      "apply must not carry the enrollment flag",
    );
    assert.equal(result.ok && result.value.enrolled, false);
  });

  test("a run that reused the saved selection writes no new selection", async () => {
    const engine = new RecordingEngine([0, 0]);
    const selections = new MemorySelections(makeSavedSelection());

    await operation({ engine, selections }).execute({
      target: undefined,
      editor: undefined,
      revision: undefined,
    });

    assert.equal(selections.written, undefined);
  });
});
