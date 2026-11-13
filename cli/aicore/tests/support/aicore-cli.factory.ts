/**
 * Shared test data for the synchronization CLI suite.
 *
 * Contract T15: test data comes from a factory, never from inline literals
 * scattered across modules.
 *
 * Contract T16: a doubled use-case port is a typed `MockProxy` built with
 * `vitest-mock-extended`, never a hand-written mock. Every double is
 * constructed by the test that owns it, so no mock is shared across cases and
 * no queued one-shot implementation survives into another case.
 */

import { mock, type MockProxy } from "vitest-mock-extended";

import type { EngineRun, SynchronizeOutcome } from "#domain/outcomes.ts";
import type { EngineRunner } from "#domain/ports/engine-runner.ts";
import type { FilesystemProbe } from "#domain/ports/filesystem-probe.ts";
import type { SavedSelection, SelectionStore } from "#domain/ports/selection-store.ts";
import type { OperatorSettings } from "#domain/settings.ts";

/** A valid 40-character lowercase hex revision. */
export const REVISION = "0123456789abcdef0123456789abcdef01234567";

/** A second distinct valid revision, for override comparisons. */
export const OTHER_REVISION = "fedcba9876543210fedcba9876543210fedcba98";

export const CHECKOUT_ROOT = "G:/projects/ai-core";

export const DESTINATION_PATH = "G:/projects/destination";

export const BINDINGS_PATH = `${DESTINATION_PATH}/.aicore/core.yaml`;

export function makeSettings(overrides: Partial<OperatorSettings> = {}): OperatorSettings {
  return { sourceRevision: REVISION, localConfigPath: undefined, ...overrides };
}

export function makeEngineRun(overrides: Partial<EngineRun> = {}): EngineRun {
  return { status: 0, stdout: "", stderr: "", ...overrides };
}

export function makeSynchronizeOutcome(
  overrides: Partial<SynchronizeOutcome> = {},
): SynchronizeOutcome {
  return {
    destination: DESTINATION_PATH,
    editor: "opencode",
    enrolled: true,
    runs: [makeEngineRun()],
    current: true,
    ...overrides,
  };
}

export function makeSavedSelection(overrides: Partial<SavedSelection> = {}): SavedSelection {
  return { target: DESTINATION_PATH, editor: "opencode", ...overrides };
}

/**
 * An engine double that replays a scripted status sequence.
 *
 * The sequence is consumed in call order; once it is exhausted the engine
 * reports success, exactly as a run with no further commands does.
 */
export function makeEngine(statuses: readonly number[] = []): MockProxy<EngineRunner> {
  const engine = mock<EngineRunner>();
  engine.run.mockResolvedValue(makeEngineRun());
  for (const status of statuses) {
    engine.run.mockResolvedValueOnce(makeEngineRun({ status }));
  }
  return engine;
}

/** A filesystem double describing an imaginary destination. */
export function makeFilesystem(
  options: {
    readonly directories?: readonly string[];
    readonly files?: readonly string[];
    readonly insideCheckout?: readonly string[];
  } = {},
): MockProxy<FilesystemProbe> {
  const directories = options.directories ?? [];
  const files = options.files ?? [];
  const insideCheckout = options.insideCheckout ?? [];

  const probe = mock<FilesystemProbe>();
  probe.resolve.mockImplementation((path) => path);
  probe.isDirectory.mockImplementation(async (path) => directories.includes(path));
  probe.isFile.mockImplementation(async (path) => files.includes(path));
  probe.isInside.mockImplementation((_root, path) => insideCheckout.includes(path));
  return probe;
}

/**
 * A selection store double.
 *
 * A write replaces the stored selection, so a later read observes it; the write
 * itself is asserted on the port mock.
 */
export function makeSelections(saved?: SavedSelection): MockProxy<SelectionStore> {
  let stored = saved;

  const selections = mock<SelectionStore>();
  selections.read.mockImplementation(async () => stored);
  selections.write.mockImplementation(async (selection) => {
    stored = selection;
  });
  return selections;
}
