/**
 * Infrastructure: runs the TypeScript synchronization engine in process.
 *
 * The engine is the sole authority for synchronization. This adapter hands it
 * one command and returns its result unchanged; it never reinterprets, retries
 * or repairs a result. The engine now runs inside this process, so a command
 * costs no interpreter start-up and the synchronization path carries no
 * interpreter environment, no package manager and no subprocess.
 *
 * A command line the engine's own syntax rejects never reaches the engine: the
 * adapter reports it as the engine reported it before — exit `2` with the
 * diagnostic on standard error — so the operator sees the same result.
 *
 * A failure to *execute* the engine — the engine throwing before it produced a
 * result — is a boundary exception and propagates (contract C5). It is never
 * converted into an engine exit status, because a fabricated status would be
 * indistinguishable from real synchronization drift.
 */

import type { EngineRun } from "#domain/outcomes.ts";
import type { EngineRunner } from "#domain/ports/engine-runner.ts";

import type { CoreSyncEngine } from "./core-sync-engine.ts";
import { toEngineRequest } from "./engine-arguments.ts";

/** The exit status the engine's own argument syntax reports. */
const EXIT_MALFORMED = 2;

/** Raised when the engine could not produce a result. */
export class EngineUnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "EngineUnavailableError";
  }
}

export class CoreSyncEngineRunner implements EngineRunner {
  readonly #engine: CoreSyncEngine;

  constructor(engine: CoreSyncEngine) {
    this.#engine = engine;
  }

  async run(command: string, arguments_: readonly string[]): Promise<EngineRun> {
    const mapping = toEngineRequest(command, arguments_);
    if (!mapping.ok) {
      return { status: EXIT_MALFORMED, stdout: "", stderr: `${mapping.message}\n` };
    }

    try {
      const outcome = await this.#engine.run(mapping.request);
      return {
        status: outcome.exitCode,
        stdout: outcome.stdout,
        stderr: outcome.stderr,
      };
    } catch (error) {
      throw new EngineUnavailableError(
        `the synchronization engine produced no result (${
          error instanceof Error ? error.message : String(error)
        }). This is not a synchronization result; nothing is claimed current.`,
      );
    }
  }
}
