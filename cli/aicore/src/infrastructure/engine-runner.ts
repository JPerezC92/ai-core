/**
 * Infrastructure: runs the existing Python synchronization engine.
 *
 * The engine is the sole authority for synchronization. This adapter spawns it
 * and returns its verbatim result; it never reinterprets, retries, or repairs a
 * result. `uv run --frozen` confines execution to the checkout's locked
 * environment, so no global interpreter or undeclared dependency is picked up.
 *
 * A failure to *execute* the engine — a missing `uv` binary, an argument-vector
 * fault, a buffer overflow — is a boundary exception and propagates (contract
 * C5). It is never converted into an engine exit status, because a fabricated
 * status would be indistinguishable from real synchronization drift.
 */

import { execFile } from "node:child_process";
import { join } from "node:path";
import { promisify } from "node:util";

import { ENGINE_RELATIVE_PATH, UV_ARGUMENTS } from "#domain/constants.ts";
import type { EngineRun } from "#domain/outcomes.ts";
import type { EngineRunner } from "#domain/ports/engine-runner.ts";

const execute = promisify(execFile);

/** Raised when the engine could not be executed at all. */
export class EngineUnavailableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "EngineUnavailableError";
  }
}

export class UvEngineRunner implements EngineRunner {
  readonly #checkoutRoot: string;

  constructor(checkoutRoot: string) {
    this.#checkoutRoot = checkoutRoot;
  }

  get enginePath(): string {
    return join(this.#checkoutRoot, ENGINE_RELATIVE_PATH);
  }

  async run(command: string, arguments_: readonly string[]): Promise<EngineRun> {
    const argv = [...UV_ARGUMENTS, this.enginePath, command, ...arguments_];
    try {
      const { stdout, stderr } = await execute("uv", argv, {
        cwd: this.#checkoutRoot,
        maxBuffer: 32 * 1024 * 1024,
        windowsHide: true,
      });
      return { status: 0, stdout, stderr };
    } catch (error) {
      const failure = error as { code?: number | string; stdout?: string; stderr?: string };
      if (typeof failure.code !== "number") {
        throw new EngineUnavailableError(
          `could not execute the synchronization engine (${String(failure.code ?? error)}). ` +
            "This is an environment failure, not a synchronization result; nothing is claimed current.",
        );
      }
      return {
        status: failure.code,
        stdout: failure.stdout ?? "",
        stderr: failure.stderr ?? "",
      };
    }
  }
}
