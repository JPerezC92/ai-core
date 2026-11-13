/**
 * Delivery: turning a synchronization outcome into the operator's channels.
 *
 * A completed command writes its success word to standard output and nothing to
 * standard error; a refusal writes its diagnostic to standard error and nothing
 * to standard output. The exit contract maps drift to `1` and malformed input to
 * `2`, so a caller never has to read the message to learn the class.
 */

import type { OperationOutcome } from "#domain/synchronization/failures.ts";

/** What one command reported, as an operator observes it. */
export type SynchronizationReport = {
  readonly exitCode: number;
  readonly stdout: string;
  readonly stderr: string;
};

const EXIT_CURRENT = 0;
const EXIT_DRIFT = 1;
const EXIT_MALFORMED = 2;

/** Map a domain outcome onto the process-level result. */
export function reportOutcome(outcome: OperationOutcome): SynchronizationReport {
  if (outcome.ok) {
    return { exitCode: EXIT_CURRENT, stdout: `${outcome.message}\n`, stderr: "" };
  }
  return {
    exitCode: outcome.failure.code === "drift" ? EXIT_DRIFT : EXIT_MALFORMED,
    stdout: "",
    stderr: `${outcome.failure.message}\n`,
  };
}

/** Report a malformed command line, before any command started. */
export function reportMalformed(reason: string): SynchronizationReport {
  return { exitCode: EXIT_MALFORMED, stdout: "", stderr: `${reason}\n` };
}

/**
 * Report a write-time filesystem failure.
 *
 * The exit contract classes it as drift: the destination is not current and a
 * later `check` is required. The cause is named so the operator can act on it.
 */
export function reportFileSystemFailure(reason: string): SynchronizationReport {
  return { exitCode: EXIT_DRIFT, stdout: "", stderr: `core-sync I/O error: ${reason}\n` };
}