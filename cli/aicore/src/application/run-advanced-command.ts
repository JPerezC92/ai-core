/**
 * Application operation: forward an advanced engine command.
 *
 * The advanced subcommands keep the engine's own argument syntax, so an existing
 * workflow that calls them today behaves exactly as before through the wrapper.
 * Returns the engine's typed result; the delivery edge owns all reporting
 * (C6, P2).
 */

import type { EngineRun } from "#domain/outcomes.ts";
import type { EngineRunner } from "#domain/ports/engine-runner.ts";

export type AdvancedRequest = {
  readonly command: string;
  readonly passthrough: readonly string[];
};

export class RunAdvancedCommand {
  readonly #engine: EngineRunner;

  constructor(engine: EngineRunner) {
    this.#engine = engine;
  }

  async execute(request: AdvancedRequest): Promise<EngineRun> {
    return this.#engine.run(request.command, request.passthrough);
  }
}
