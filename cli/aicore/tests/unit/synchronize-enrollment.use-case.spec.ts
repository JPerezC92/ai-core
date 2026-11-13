/**
 * Unit: enrollment of a destination that is not yet bound.
 *
 * Exercises the application use case with its ports doubled (contract T2). The
 * assertion is on the operation's returned domain result and the engine
 * invocation it chose — never on operator copy or an exit status, which belong
 * to the delivery edge.
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import type { MockProxy } from "vitest-mock-extended";

import { SynchronizeDestination } from "#application/synchronize-destination.ts";
import type { EngineRunner } from "#domain/ports/engine-runner.ts";
import type { FilesystemProbe } from "#domain/ports/filesystem-probe.ts";
import type { SelectionStore } from "#domain/ports/selection-store.ts";
import {
  BINDINGS_PATH,
  CHECKOUT_ROOT,
  DESTINATION_PATH,
  OTHER_REVISION,
  REVISION,
  makeEngine,
  makeFilesystem,
  makeSelections,
  makeSettings,
} from "#support/aicore-cli.factory.ts";

function operation(options: {
  engine: MockProxy<EngineRunner>;
  files?: MockProxy<FilesystemProbe>;
  selections?: MockProxy<SelectionStore>;
  sourceRevision?: string | undefined;
}) {
  return new SynchronizeDestination({
    checkoutRoot: CHECKOUT_ROOT,
    settings: makeSettings({ sourceRevision: options.sourceRevision ?? REVISION }),
    engine: options.engine,
    files: options.files ?? makeFilesystem({ directories: [DESTINATION_PATH] }),
    selections: options.selections ?? makeSelections(),
  });
}

describe("enrollment decision", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("an unbound destination is enrolled with --bind-cleared, then verified", async () => {
    const engine = makeEngine([0, 0]);

    const result = await operation({ engine }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: undefined,
    });

    expect(result.ok).toBeTruthy();
    expect(engine.run).toHaveBeenNthCalledWith(1, "init", [
      "--source",
      CHECKOUT_ROOT,
      "--destination",
      DESTINATION_PATH,
      "--bindings",
      BINDINGS_PATH,
      "--source-revision",
      REVISION,
      "--editor",
      "opencode",
      "--bind-cleared",
    ]);
    expect(engine.run).toHaveBeenNthCalledWith(2, "check", expect.anything());
    expect(engine.run).toHaveBeenCalledTimes(2);
    expect(result.ok && result.value.enrolled).toBe(true);
    expect(result.ok && result.value.current).toBe(true);
  });

  test("the requested editor reaches the engine as the profile to deliver", async () => {
    const engine = makeEngine([0, 0]);

    const result = await operation({ engine }).execute({
      target: DESTINATION_PATH,
      editor: "cursor",
      revision: undefined,
    });

    expect(result.ok).toBeTruthy();
    const arguments_ = engine.run.mock.calls[0]?.[1] ?? [];
    const editorPosition = arguments_.indexOf("--editor");
    expect(editorPosition).not.toBe(-1);
    expect(arguments_[editorPosition + 1]).toBe("cursor");
    expect(result.ok && result.value.editor).toBe("cursor");
  });

  test("the explicitly supplied revision wins over the operator setting", async () => {
    const engine = makeEngine([0, 0]);

    const result = await operation({ engine, sourceRevision: OTHER_REVISION }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: REVISION,
    });

    expect(result.ok).toBeTruthy();
    // The engine is told the explicit revision, and never falls back to the setting.
    const arguments_ = engine.run.mock.calls[0]?.[1] ?? [];
    const revisionPosition = arguments_.indexOf("--source-revision");
    expect(revisionPosition).not.toBe(-1);
    expect(arguments_[revisionPosition + 1]).toBe(REVISION);
    expect(arguments_).not.toContain(OTHER_REVISION);
  });

  test("the engine's verification result decides currency, not the write", async () => {
    const engine = makeEngine([0, 1]);

    const result = await operation({ engine }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: undefined,
    });

    expect(result.ok).toBeTruthy();
    expect(result.ok && result.value.current).toBe(false);
    expect(result.ok && result.value.runs.length).toBe(2);
  });

  test("a failed write stops before verification", async () => {
    const engine = makeEngine([2]);

    const result = await operation({ engine }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: undefined,
    });

    expect(result.ok).toBeTruthy();
    expect(engine.run).toHaveBeenNthCalledWith(1, "init", expect.anything());
    expect(engine.run).toHaveBeenCalledTimes(1);
    expect(result.ok && result.value.current).toBe(false);
  });
});
