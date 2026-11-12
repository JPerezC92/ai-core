/**
 * Vitest configuration for the unit and integration suites.
 *
 * The runner configuration belongs to the package: the CLI is independently
 * testable and its suites never depend on a repository-root command.
 *
 * Concurrency is kept at or below the previous runner's baseline, never above
 * it. Node's test runner executed the package's files in parallel; the
 * disposable filesystem fixtures own their own temporary roots and their safety
 * under concurrent execution is not established, so files now run one at a time
 * and tests inside a file never run concurrently.
 */

import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["tests/unit/**", "tests/integration/**"],
    fileParallelism: false,
    sequence: {
      concurrent: false,
    },
  },
});
