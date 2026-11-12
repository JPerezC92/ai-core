/**
 * Delivery: operator-facing reporting.
 *
 * The delivery edge owns all transport encodings — operator copy, exit statuses
 * and stream selection — so the application operations stay free of them
 * (contract C6, scripts-shape P2).
 */

import type { Failure } from "#domain/failures.ts";
import type { EngineRun, SynchronizeOutcome } from "#domain/outcomes.ts";

/** Process exit statuses, matching the engine's published contract. */
export const EXIT_OK = 0;
export const EXIT_DRIFT = 1;
export const EXIT_INVALID = 2;

const EXIT_BY_FAILURE = {
  "unavailable-configuration": EXIT_INVALID,
  "unsupported-editor": EXIT_INVALID,
  "unknown-editor": EXIT_INVALID,
  "invalid-destination": EXIT_INVALID,
  "invalid-revision": EXIT_INVALID,
} as const;

export function exitStatusForFailure(failure: Failure): number {
  return EXIT_BY_FAILURE[failure.code] ?? EXIT_INVALID;
}

/** Render one engine run's streams in the order the operator should read them. */
export function renderRun(run: EngineRun): { stdout: string[]; stderr: string[] } {
  const stdout = run.stdout.trim() === "" ? [] : [run.stdout.trim()];
  const stderr = run.stderr.trim() === "" ? [] : [run.stderr.trim()];
  return { stdout, stderr };
}

/**
 * Render a completed synchronization.
 *
 * The exit status reflects the last engine invocation, so a failed write or a
 * failed verification is never reported as success.
 */
export function renderSync(outcome: SynchronizeOutcome): {
  stdout: string[];
  stderr: string[];
  status: number;
} {
  const stdout: string[] = [];
  const stderr: string[] = [];
  for (const run of outcome.runs) {
    const rendered = renderRun(run);
    stdout.push(...rendered.stdout);
    stderr.push(...rendered.stderr);
  }

  const last = outcome.runs[outcome.runs.length - 1];

  if (outcome.current) {
    stdout.push(`sync: ${outcome.destination} is current (${outcome.editor}).`);
    return { stdout, stderr, status: EXIT_OK };
  }

  const wroteSuccessfully = last !== undefined && outcome.runs.length > 1 && last.status !== 0;
  stderr.push(
    wroteSuccessfully
      ? `sync: the write to ${outcome.destination} succeeded, but the engine reports the ` +
          "destination is not current. Its result above is authoritative and is not " +
          "overridden here. A freshly enrolled destination lists region files under " +
          "`pending:` until that project reconciles its own project regions; clearing " +
          "`pending:` is destination-owned and is never done by this tool."
      : `sync: synchronization of ${outcome.destination} failed with status ` +
          `${last?.status ?? EXIT_DRIFT}; nothing is claimed current.`,
  );

  return { stdout, stderr, status: last?.status ?? EXIT_DRIFT };
}

/** Render a forwarded advanced command, preserving the engine's exit status. */
export function renderAdvanced(run: EngineRun): {
  stdout: string[];
  stderr: string[];
  status: number;
} {
  const rendered = renderRun(run);
  return {
    stdout: rendered.stdout,
    stderr: rendered.stderr,
    status: run.status,
  };
}
