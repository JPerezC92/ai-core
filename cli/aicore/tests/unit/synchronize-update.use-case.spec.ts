/**
 * Unit: updating a destination that is already bound.
 *
 * One behavioral concern — the update path never re-enrolls and never carries the
 * enrollment flag (contract T2, application use case with doubled ports).
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
  selections?: MockProxy<SelectionStore>;
}) {
  return new SynchronizeDestination({
    checkoutRoot: CHECKOUT_ROOT,
    settings: makeSettings(),
    engine: options.engine,
    files: makeFilesystem({
      directories: [DESTINATION_PATH],
      files: [BINDINGS_PATH],
    }),
    selections: options.selections ?? makeSelections(makeSavedSelection()),
  });
}

describe("update decision", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test("a bound destination is updated with apply and never re-enrolled", async () => {
    const engine = makeEngine([0, 0]);

    const result = await operation({ engine }).execute({
      target: undefined,
      editor: undefined,
      revision: undefined,
    });

    expect(result.ok).toBeTruthy();
    expect(engine.run).toHaveBeenNthCalledWith(1, "apply", expect.anything());
    expect(engine.run).toHaveBeenNthCalledWith(2, "check", expect.anything());
    expect(engine.run).toHaveBeenCalledTimes(2);
    // apply must not carry the enrollment flag.
    expect(engine.run.mock.calls[0]?.[1] ?? []).not.toContain("--bind-cleared");
    expect(result.ok && result.value.enrolled).toBe(false);
  });

  test("a run that reused the saved selection writes no new selection", async () => {
    const engine = makeEngine([0, 0]);
    const selections = makeSelections(makeSavedSelection());

    await operation({ engine, selections }).execute({
      target: undefined,
      editor: undefined,
      revision: undefined,
    });

    expect(selections.write).not.toHaveBeenCalled();
  });
});
