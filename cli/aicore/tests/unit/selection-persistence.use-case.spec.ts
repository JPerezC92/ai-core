/**
 * Unit: persisting an explicit selection.
 *
 * One behavioral concern — an explicitly stated destination or editor is
 * recorded for later runs, and the recorded value is the resolved destination.
 */

import { beforeEach, describe, expect, test, vi } from "vitest";
import type { MockProxy } from "vitest-mock-extended";

import { SynchronizeDestination } from "#application/synchronize-destination.ts";
import type { EngineRunner } from "#domain/ports/engine-runner.ts";
import type { SelectionStore } from "#domain/ports/selection-store.ts";
import {
  BINDINGS_PATH,
  CHECKOUT_ROOT,
  DESTINATION_PATH,
  makeEngine,
  makeFilesystem,
  makeSavedSelection,
  makeSelections,
  makeSettings,
} from "#support/aicore-cli.factory.ts";

function operation(options: {
  engine: MockProxy<EngineRunner>;
  selections: MockProxy<SelectionStore>;
}) {
  return new SynchronizeDestination({
    checkoutRoot: CHECKOUT_ROOT,
    settings: makeSettings(),
    engine: options.engine,
    files: makeFilesystem({
      directories: [DESTINATION_PATH],
      files: [BINDINGS_PATH],
    }),
    selections: options.selections,
  });
}

describe("selection persistence", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("an explicit target is recorded against the resolved destination", async () => {
    const selections = makeSelections(makeSavedSelection({ target: "G:/projects/old" }));
    await operation({ engine: makeEngine([0, 0]), selections }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: undefined,
    });

    expect(selections.write).toHaveBeenCalledWith({
      target: DESTINATION_PATH,
      editor: "opencode",
    });
  });

  test("an explicit editor alone is recorded for the current destination", async () => {
    const selections = makeSelections(makeSavedSelection());
    await operation({ engine: makeEngine([0, 0]), selections }).execute({
      target: undefined,
      editor: "opencode",
      revision: undefined,
    });

    expect(selections.write).toHaveBeenCalledWith({
      target: DESTINATION_PATH,
      editor: "opencode",
    });
  });

  test("a failed write records no selection", async () => {
    const selections = makeSelections();
    await operation({ engine: makeEngine([2]), selections }).execute({
      target: DESTINATION_PATH,
      editor: "opencode",
      revision: undefined,
    });

    expect(selections.write).not.toHaveBeenCalled();
  });
});
