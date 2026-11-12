/**
 * Vitest configuration for the end-to-end suite.
 *
 * The end-to-end suite spawns the CLI, which runs the Python synchronization
 * engine over the whole cleared set. A single run takes tens of seconds, so
 * the per-test and the per-hook budgets are set explicitly instead of relying
 * on the runner's default of a few seconds.
 *
 * Concurrency is kept at or below the previous runner's baseline, never above
 * it, for the same reason as in the unit and integration configuration: the
 * disposable fixtures are not established as safe under concurrent execution.
 * Node's test runner executed the package's files in parallel, so files now
 * run one at a time and tests inside a file never run concurrently.
 */

import { defineConfig } from "vitest/config";

/** The budget for one spawned CLI run and for one fixture hook. */
const E2E_TIMEOUT_MS = 300_000;

export default defineConfig({
  test: {
    include: ["tests/e2e/**"],
    fileParallelism: false,
    sequence: {
      concurrent: false,
    },
    testTimeout: E2E_TIMEOUT_MS,
    hookTimeout: E2E_TIMEOUT_MS,
  },
});
