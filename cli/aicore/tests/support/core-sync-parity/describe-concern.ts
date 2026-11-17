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
import { canCreateDirectoryLinks, canCreateSymlinks } from "./fixtures.ts";
import { runParityCase } from "./runner.ts";
import type { Concern, ParityCase } from "./types.ts";

const symlinksAvailable = await canCreateSymlinks();
const directoryLinksAvailable = await canCreateDirectoryLinks();

/**
 * The kind of link a case needs, or `null` when it needs none.
 *
 * A platform that refuses to create that link cannot exercise the case, so the
 * case is reported as skipped rather than as covered. The support probes create
 * a real link first, so the skip is never unconditional.
 */
function requiredLink(testCase: ParityCase): { readonly kind: string; readonly available: boolean } | null {
	if (testCase.fixture.destinationLinks !== undefined) {
		return { kind: "symbolic links", available: symlinksAvailable };
	}
	if (testCase.fixture.sourceDirectoryLinks !== undefined) {
		return { kind: "directory links", available: directoryLinksAvailable };
	}
	return null;
}

/** Register the cases of one concern as the tests of the calling spec file. */
export function describeConcern(concern: Concern, label: string): void {
	describe(label, () => {
		for (const testCase of casesFor(concern)) {
			const linkCase = requiredLink(testCase);
			const skipped = linkCase !== null && !linkCase.available;
			const title = skipped
				? `${testCase.title} (skipped: this platform refuses to create ${linkCase.kind})`
				: testCase.title;
			const run = async (): Promise<void> => {
				const differences = await runParityCase(testCase);
				expect(differences, differences.join("\n")).toEqual([]);
			};
			if (skipped) {
				test.skip(title, run);
				continue;
			}
			test(title, run);
		}
	});
}
