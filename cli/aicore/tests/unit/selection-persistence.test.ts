/**
 * Unit: persisting an explicit selection.
 *
 * One behavioral concern — an explicitly stated destination or editor is
 * recorded for later runs, and the recorded value is the resolved destination.
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
  selections: MemorySelections;
}) {
  return new SynchronizeDestination({
    checkoutRoot: CHECKOUT_ROOT,
    settings: makeSettings(),
    engine: options.engine,
    files: new StubFiles({
      directories: [DESTINATION_PATH],
      files: [BINDINGS_PATH],
    }),
    selections: options.selections,
  });
}

describe("selection persistence", () => {
  test("an explicit target is recorded against the resolved destination", async () => {
    const selections = new MemorySelections(makeSavedSelection({ target: "G:/projects/old" }));
    await operation({ engine: new RecordingEngine([0, 0]), selections }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: undefined,
    });

    assert.deepEqual(selections.written, {
      target: DESTINATION_PATH,
      editor: "opencode",
    });
  });

  test("an explicit editor alone is recorded for the current destination", async () => {
    const selections = new MemorySelections(makeSavedSelection());
    await operation({ engine: new RecordingEngine([0, 0]), selections }).execute({
      target: undefined,
      editor: "opencode",
      revision: undefined,
    });

    assert.deepEqual(selections.written, {
      target: DESTINATION_PATH,
      editor: "opencode",
    });
  });

  test("a failed write records no selection", async () => {
    const selections = new MemorySelections();
    await operation({ engine: new RecordingEngine([2]), selections }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: undefined,
    });

    assert.equal(selections.written, undefined);
  });
});
