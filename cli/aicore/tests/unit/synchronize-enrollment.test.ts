/**
 * Unit: enrollment of a destination that is not yet bound.
 *
 * Exercises the application use case with its ports doubled (contract T2). The
 * assertion is on the operation's returned domain result and the engine
 * invocation it chose — never on operator copy or an exit status, which belong
 * to the delivery edge.
 */

import assert from "node:assert/strict";
import { describe, test } from "node:test";

import { SynchronizeDestination } from "#application/synchronize-destination.ts";
import {
  BINDINGS_PATH,
  CHECKOUT_ROOT,
  DESTINATION_PATH,
  MemorySelections,
  OTHER_REVISION,
  REVISION,
  RecordingEngine,
  StubFiles,
  makeSettings,
} from "#support/aicore-cli.factory.ts";

function operation(options: {
  engine: RecordingEngine;
  files?: StubFiles;
  selections?: MemorySelections;
  sourceRevision?: string | undefined;
}) {
  return new SynchronizeDestination({
    checkoutRoot: CHECKOUT_ROOT,
    settings: makeSettings({ sourceRevision: options.sourceRevision ?? REVISION }),
    engine: options.engine,
    files: options.files ?? new StubFiles({ directories: [DESTINATION_PATH] }),
    selections: options.selections ?? new MemorySelections(),
  });
}

describe("enrollment decision", () => {
  test("an unbound destination is enrolled with --bind-cleared, then verified", async () => {
    const engine = new RecordingEngine([0, 0]);

    const result = await operation({ engine }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: undefined,
    });

    assert.ok(result.ok);
    assert.deepEqual(
      engine.calls.map((call) => call.command),
      ["init", "check"],
    );
    assert.deepEqual(engine.calls[0]?.arguments_, [
      "--source",
      CHECKOUT_ROOT,
      "--destination",
      DESTINATION_PATH,
      "--bindings",
      BINDINGS_PATH,
      "--source-revision",
      REVISION,
      "--bind-cleared",
    ]);
    assert.equal(result.ok && result.value.enrolled, true);
    assert.equal(result.ok && result.value.current, true);
  });

  test("the explicitly supplied revision wins over the operator setting", async () => {
    const engine = new RecordingEngine([0, 0]);

    const result = await operation({ engine, sourceRevision: OTHER_REVISION }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: REVISION,
    });

    assert.ok(result.ok);
    // The engine is told the explicit revision, and never falls back to the setting.
    const arguments_ = engine.calls[0]?.arguments_ ?? [];
    const revisionPosition = arguments_.indexOf("--source-revision");
    assert.notEqual(revisionPosition, -1, "the engine must receive --source-revision");
    assert.equal(arguments_[revisionPosition + 1], REVISION);
    assert.ok(
      !arguments_.includes(OTHER_REVISION),
      "the operator setting must not reach the engine when a revision was supplied",
    );
  });

  test("the engine's verification result decides currency, not the write", async () => {
    const engine = new RecordingEngine([0, 1]);

    const result = await operation({ engine }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: undefined,
    });

    assert.ok(result.ok);
    assert.equal(result.ok && result.value.current, false);
    assert.equal(result.ok && result.value.runs.length, 2);
  });

  test("a failed write stops before verification", async () => {
    const engine = new RecordingEngine([2]);

    const result = await operation({ engine }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: undefined,
    });

    assert.ok(result.ok);
    assert.deepEqual(
      engine.calls.map((call) => call.command),
      ["init"],
    );
    assert.equal(result.ok && result.value.current, false);
  });
});
