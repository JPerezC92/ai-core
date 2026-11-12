/**
 * Domain outcomes for the synchronization CLI.
 *
 * Business operations return typed values, never transport encodings
 * (architecture contract C6). An engine run's status and streams are the
 * capability's own result and travel as data; turning them into process exit
 * codes and operator copy is the delivery edge's job.
 */

import type { SupportedEditor } from "./constants.ts";

/** One engine invocation's verbatim result. */
export type EngineRun = {
  readonly status: number;
  readonly stdout: string;
  readonly stderr: string;
};

export type SynchronizeOutcome = {
  /** Absolute destination path the run acted on. */
  readonly destination: string;
  readonly editor: SupportedEditor;
  /** True when this run enrolled a destination rather than updating one. */
  readonly enrolled: boolean;
  /** The write invocation and, when it ran, the verification invocation. */
  readonly runs: readonly EngineRun[];
  /** True when the engine reported the destination is current. */
  readonly current: boolean;
};
