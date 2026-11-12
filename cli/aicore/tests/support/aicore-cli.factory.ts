/**
 * Shared test data for the synchronization CLI suite.
 *
 * Contract T15: test data comes from a factory, never from inline literals
 * scattered across modules.
 */

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

/** An engine double that records calls and replays a scripted status sequence. */
export class RecordingEngine implements EngineRunner {
  readonly calls: { command: string; arguments_: readonly string[] }[] = [];
  #statuses: number[];

  constructor(statuses: readonly number[] = []) {
    this.#statuses = [...statuses];
  }

  async run(command: string, arguments_: readonly string[]): Promise<EngineRun> {
    this.calls.push({ command, arguments_ });
    return makeEngineRun({ status: this.#statuses.shift() ?? 0 });
  }
}

/** A filesystem double describing an imaginary destination. */
export class StubFiles implements FilesystemProbe {
  readonly directories: readonly string[];
  readonly files: readonly string[];
  readonly insideCheckout: readonly string[];

  constructor(
    options: {
      directories?: readonly string[];
      files?: readonly string[];
      insideCheckout?: readonly string[];
    } = {},
  ) {
    this.directories = options.directories ?? [];
    this.files = options.files ?? [];
    this.insideCheckout = options.insideCheckout ?? [];
  }

  resolve(path: string): string {
    return path;
  }

  async isDirectory(path: string): Promise<boolean> {
    return this.directories.includes(path);
  }

  async isFile(path: string): Promise<boolean> {
    return this.files.includes(path);
  }

  isInside(_root: string, path: string): boolean {
    return this.insideCheckout.includes(path);
  }
}

/** A selection store double. */
export class MemorySelections implements SelectionStore {
  saved: SavedSelection | undefined;
  written: SavedSelection | undefined;

  constructor(saved?: SavedSelection) {
    this.saved = saved;
  }

  async read(): Promise<SavedSelection | undefined> {
    return this.saved;
  }

  async write(selection: SavedSelection): Promise<void> {
    this.written = selection;
    this.saved = selection;
  }
}
