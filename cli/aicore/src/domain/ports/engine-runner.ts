/**
 * Domain port: running the existing synchronization engine.
 *
 * One capability per module (P4, C2).
 */

import type { EngineRun } from "#domain/outcomes.ts";

export interface EngineRunner {
  /**
   * Run one engine subcommand with the engine's own argument syntax.
   *
   * Returns the engine's verbatim result when it executed. A failure to execute
   * the engine at all is a boundary exception and propagates, per contract C5;
   * it is never reported as an engine outcome.
   */
  run(command: string, arguments_: readonly string[]): Promise<EngineRun>;
}
