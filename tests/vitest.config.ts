import { defineConfig } from "vitest/config";

/**
 * The repository-contract suite.
 *
 * `fileParallelism` is off because every module reads the same checkout; the
 * assertions compare files against their pinned values, so running them serially
 * keeps a failure attributable to one module.
 */
export default defineConfig({
  test: {
    include: ["integration/**/*.test.ts"],
    fileParallelism: false,
  },
});
