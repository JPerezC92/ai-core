/**
 * Unit: refusals that stop a run before anything is written.
 *
 * One behavioral concern — every pre-write precondition reports a typed failure
 * and runs no engine command (contract T2, T3; refusal is a returned value).
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
  REVISION,
  makeEngine,
  makeFilesystem,
  makeSavedSelection,
  makeSelections,
  makeSettings,
} from "#support/aicore-cli.factory.ts";

function operation(options: {
  engine: MockProxy<EngineRunner>;
  files?: MockProxy<FilesystemProbe>;
  selections?: MockProxy<SelectionStore>;
  /** Omitted means "use the valid default revision"; pass `null` to omit it. */
  sourceRevision?: string | null;
}) {
  const sourceRevision =
    options.sourceRevision === null ? undefined : (options.sourceRevision ?? REVISION);
  return new SynchronizeDestination({
    checkoutRoot: CHECKOUT_ROOT,
    settings: makeSettings({ sourceRevision }),
    engine: options.engine,
    files: options.files ?? makeFilesystem({ directories: [DESTINATION_PATH] }),
    selections: options.selections ?? makeSelections(),
  });
}

describe("pre-write refusals", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("an unimplemented editor runs no engine command", async () => {
    const engine = makeEngine();
    const result = await operation({ engine }).execute({
      target: DESTINATION_PATH,
      editor: "cursor",
      revision: undefined,
    });

    expect(!result.ok).toBeTruthy();
    expect(result.ok ? "" : result.failure.code).toBe("unsupported-editor");
    expect(engine.run).not.toHaveBeenCalled();
  });

  test("an unknown editor is refused by name and runs no engine command", async () => {
    const engine = makeEngine();
    const result = await operation({ engine }).execute({
      target: DESTINATION_PATH,
      editor: "vim",
      revision: undefined,
    });

    expect(!result.ok).toBeTruthy();
    expect(result.ok ? "" : result.failure.code).toBe("unsupported-editor");
    expect(result.ok ? "" : result.failure.message).toMatch(/unknown editor "vim"/);
    expect(engine.run).not.toHaveBeenCalled();
  });

  test("a missing revision runs no engine command", async () => {
    const engine = makeEngine();
    const result = await operation({ engine, sourceRevision: null }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: undefined,
    });

    expect(!result.ok).toBeTruthy();
    expect(result.ok ? "" : result.failure.code).toBe("invalid-revision");
    expect(engine.run).not.toHaveBeenCalled();
  });

  test("a destination that is not a directory is refused", async () => {
    const engine = makeEngine();
    const result = await operation({ engine, files: makeFilesystem() }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: undefined,
    });

    expect(!result.ok).toBeTruthy();
    expect(result.ok ? "" : result.failure.code).toBe("invalid-destination");
    expect(engine.run).not.toHaveBeenCalled();
  });

  test("a destination inside the checkout is refused", async () => {
    const engine = makeEngine();
    const result = await operation({
      engine,
      files: makeFilesystem({
        directories: [DESTINATION_PATH],
        insideCheckout: [DESTINATION_PATH],
      }),
    }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: undefined,
    });

    expect(!result.ok).toBeTruthy();
    expect(result.ok ? "" : result.failure.code).toBe("invalid-destination");
    expect(engine.run).not.toHaveBeenCalled();
  });

  test("a bound destination without a recorded editor is never inferred", async () => {
    const engine = makeEngine();
    const result = await operation({
      engine,
      files: makeFilesystem({
        directories: [DESTINATION_PATH],
        files: [BINDINGS_PATH],
      }),
    }).execute({ target: DESTINATION_PATH, editor: undefined, revision: undefined });

    expect(!result.ok).toBeTruthy();
    expect(result.ok ? "" : result.failure.code).toBe("unknown-editor");
    expect(engine.run).not.toHaveBeenCalled();
  });

  test("switching destination without an editor is refused", async () => {
    const engine = makeEngine();
    const result = await operation({
      engine,
      selections: makeSelections(makeSavedSelection({ target: "G:/projects/old" })),
    }).execute({ target: DESTINATION_PATH, editor: undefined, revision: undefined });

    expect(!result.ok).toBeTruthy();
    expect(result.ok ? "" : result.failure.code).toBe("unknown-editor");
    expect(engine.run).not.toHaveBeenCalled();
  });

  test("no target and no saved selection is refused", async () => {
    const engine = makeEngine();
    const result = await operation({
      engine,
      selections: makeSelections(),
    }).execute({ target: undefined, editor: "opencode", revision: undefined });

    expect(!result.ok).toBeTruthy();
    expect(result.ok ? "" : result.failure.code).toBe("unavailable-configuration");
    expect(result.ok ? "" : result.failure.message).toMatch(/no destination selected/);
    expect(engine.run).not.toHaveBeenCalled();
  });
});
