/**
 * Unit: refusals that stop a run before anything is written.
 *
 * One behavioral concern — every pre-write precondition reports a typed failure
 * and runs no engine command (contract T2, T3; refusal is a returned value).
 */

import assert from "node:assert/strict";
import { describe, test } from "node:test";

import { SynchronizeDestination } from "#application/synchronize-destination.ts";
import {
  BINDINGS_PATH,
  CHECKOUT_ROOT,
  DESTINATION_PATH,
  MemorySelections,
  REVISION,
  RecordingEngine,
  StubFiles,
  makeSavedSelection,
  makeSettings,
} from "#support/aicore-cli.factory.ts";

function operation(options: {
  engine: RecordingEngine;
  files?: StubFiles;
  selections?: MemorySelections;
  /** Omitted means "use the valid default revision"; pass `null` to omit it. */
  sourceRevision?: string | null;
}) {
  const sourceRevision =
    options.sourceRevision === null ? undefined : (options.sourceRevision ?? REVISION);
  return new SynchronizeDestination({
    checkoutRoot: CHECKOUT_ROOT,
    settings: makeSettings({ sourceRevision }),
    engine: options.engine,
    files: options.files ?? new StubFiles({ directories: [DESTINATION_PATH] }),
    selections: options.selections ?? new MemorySelections(),
  });
}

describe("pre-write refusals", () => {
  test("an unimplemented editor runs no engine command", async () => {
    const engine = new RecordingEngine();
    const result = await operation({ engine }).execute({
      target: DESTINATION_PATH,
      editor: "cursor",
      revision: undefined,
    });

    assert.ok(!result.ok);
    assert.equal(result.ok ? "" : result.failure.code, "unsupported-editor");
    assert.equal(engine.calls.length, 0);
  });

  test("an unknown editor is refused by name and runs no engine command", async () => {
    const engine = new RecordingEngine();
    const result = await operation({ engine }).execute({
      target: DESTINATION_PATH,
      editor: "vim",
      revision: undefined,
    });

    assert.ok(!result.ok);
    assert.equal(result.ok ? "" : result.failure.code, "unsupported-editor");
    assert.match(result.ok ? "" : result.failure.message, /unknown editor "vim"/);
    assert.equal(engine.calls.length, 0);
  });

  test("a missing revision runs no engine command", async () => {
    const engine = new RecordingEngine();
    const result = await operation({ engine, sourceRevision: null }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: undefined,
    });

    assert.ok(!result.ok);
    assert.equal(result.ok ? "" : result.failure.code, "invalid-revision");
    assert.equal(engine.calls.length, 0);
  });

  test("a destination that is not a directory is refused", async () => {
    const engine = new RecordingEngine();
    const result = await operation({ engine, files: new StubFiles() }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: undefined,
    });

    assert.ok(!result.ok);
    assert.equal(result.ok ? "" : result.failure.code, "invalid-destination");
    assert.equal(engine.calls.length, 0);
  });

  test("a destination inside the checkout is refused", async () => {
    const engine = new RecordingEngine();
    const result = await operation({
      engine,
      files: new StubFiles({
        directories: [DESTINATION_PATH],
        insideCheckout: [DESTINATION_PATH],
      }),
    }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: undefined,
    });

    assert.ok(!result.ok);
    assert.equal(result.ok ? "" : result.failure.code, "invalid-destination");
    assert.equal(engine.calls.length, 0);
  });

  test("a bound destination without a recorded editor is never inferred", async () => {
    const engine = new RecordingEngine();
    const result = await operation({
      engine,
      files: new StubFiles({
        directories: [DESTINATION_PATH],
        files: [BINDINGS_PATH],
      }),
    }).execute({ target: DESTINATION_PATH, editor: undefined, revision: undefined });

    assert.ok(!result.ok);
    assert.equal(result.ok ? "" : result.failure.code, "unknown-editor");
    assert.equal(engine.calls.length, 0);
  });

  test("switching destination without an editor is refused", async () => {
    const engine = new RecordingEngine();
    const result = await operation({
      engine,
      selections: new MemorySelections(makeSavedSelection({ target: "G:/projects/old" })),
    }).execute({ target: DESTINATION_PATH, editor: undefined, revision: undefined });

    assert.ok(!result.ok);
    assert.equal(result.ok ? "" : result.failure.code, "unknown-editor");
    assert.equal(engine.calls.length, 0);
  });

  test("no target and no saved selection is refused", async () => {
    const engine = new RecordingEngine();
    const result = await operation({
      engine,
      selections: new MemorySelections(),
    }).execute({ target: undefined, editor: "opencode", revision: undefined });

    assert.ok(!result.ok);
    assert.equal(result.ok ? "" : result.failure.code, "unavailable-configuration");
    assert.match(result.ok ? "" : result.failure.message, /no destination selected/);
    assert.equal(engine.calls.length, 0);
  });
});
