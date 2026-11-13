/**
 * The shared spec registration for the parity corpus.
 *
 * Each integration spec file registers exactly one behavioural concern, so a
 * concern owns one spec file (T11). The cases themselves live in the corpus
 * data module; this helper only registers them and reports the differences a
 * case produced.
 */

import { describe, expect, test } from "vitest";

import { casesFor } from "./corpus.ts";
import { canCreateSymlinks } from "./fixtures.ts";
import { runParityCase } from "./runner.ts";
import type { Concern } from "./types.ts";

const symlinksAvailable = await canCreateSymlinks();

/** Register the cases of one concern as the tests of the calling spec file. */
export function describeConcern(concern: Concern, label: string): void {
  describe(label, () => {
    for (const testCase of casesFor(concern)) {
      const needsSymlinks = testCase.fixture.destinationLinks !== undefined;
      const title = needsSymlinks && !symlinksAvailable
        ? `${testCase.title} (skipped: this platform refuses to create symbolic links)`
        : testCase.title;
      const run = async (): Promise<void> => {
        const differences = await runParityCase(testCase);
        expect(differences, differences.join("\n")).toEqual([]);
      };
      if (needsSymlinks && !symlinksAvailable) {
        test.skip(title, run);
        continue;
      }
      test(title, run);
    }
  });
}
